from IPython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.display import Image, display
import ipykernel
from matlab import double as md

import threading
import ctypes
import time
import sys
import io
import os
try:
    from tempfile import TemporaryDirectory, TemporaryFile, NamedTemporaryFile
except ImportError:
    from backports.tempfile import TemporaryDirectory, TemporaryFile, NamedTemporaryFile

_magic_class_ref = None

# We will overload the `post_run_cell` event with this function
# That callback is a method of `EventManager` hence the `self` argument
def showPlot(self=None, result=None):
    # We use a global reference to the magics class to get the reference to Matlab interpreter
    # If it doesn't exist, we can't do anything, and assume the user is just using Python
    ip = get_ipython()
    if ip is None or _magic_class_ref is None or _magic_class_ref.plot_type != 'inline':
        return
    interface = _magic_class_ref.m
    nfig = len(interface.call('get',(0., "children")))
    if nfig == 0:
        return
    if _magic_class_ref.next_pars:
        width, height, resolution = (_magic_class_ref.next_pars[idx] for idx in ['width', 'height', 'resolution'])
    else:
        width, height, resolution = (_magic_class_ref.width, _magic_class_ref.height, _magic_class_ref.resolution)
    interface.call('set', (0., 'defaultfigurepaperposition', md([0, 0, width / resolution, height / resolution])), nargout=0)
    interface.call('set', (0., 'defaultfigurepaperunits', 'inches'), nargout=0)
    format = 'png'
    with TemporaryDirectory() as tmpdir:
        try:
            interface.call('eval',
                ["arrayfun(@(h, i) print(h, sprintf('{}/%i', i), '-d{}', '-r{}'),get(0, 'children'), (1:{})')"
                                   .format('/'.join(tmpdir.split(os.sep)), format, resolution, nfig)],
                nargout=0)
            interface.call('eval', ["arrayfun(@(h) close(h), get(0, 'children'))"], nargout=0)
            for fname in sorted(os.listdir(tmpdir)):
                display(Image(filename=os.path.join(tmpdir, fname)))
        except Exception as exc:
            ip.showtraceback()
            return
        finally:
            interface.call('set', (0., 'defaultfigurevisible', 'off'), nargout=0)
            if _magic_class_ref.next_pars:
                _magic_class_ref.next_pars = None

# Matlab writes to the C-level stdout / stderr file descriptors
# whereas IPython overloads the Python-level sys.stdout / sys.stderr streams
# To force Matlab output into the IPython cells we need to 
#   1. Duplicate the stdout/err file descriptors into a pipe (with os.dup2)
#   2. Create a thread which watches the pipe and re-prints to IPython
# See: https://stackoverflow.com/questions/41216215/
#      https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/

class Redirection(object):
    # Class which redirects a C-level file descriptor to the equiv. IPython stream
    def __init__(self, target='stdout'):
        self.libc = ctypes.CDLL(None)
        self.c_stdstream = ctypes.c_void_p.in_dll(self.libc, target)
        self.target = {'stdout':sys.__stdout__, 'stderr':sys.__stderr__}[target].fileno()
        self.output = {'stdout':sys.stdout, 'stderr':sys.stderr}[target]
        self.thread = None
        self.stop_flag = None
        self.saved_fd = None
        self.read_pipe = None
        self.exc_info = None
        self.ip = get_ipython()

    def not_redirecting(self):
        return (
                self.ip is None or _magic_class_ref is None or
                (_magic_class_ref.output != 'inline' and self.saved_fd == None)
               )

    def pre(self):
        if self.not_redirecting():
            return
        self.libc.fflush(self.c_stdstream)
        if self.saved_fd == None:
            self.saved_fd = os.dup(self.target)
        self.read_pipe, write_pipe = os.pipe()
        os.dup2(write_pipe, self.target)
        os.close(write_pipe)

        def redirect_thread():
            try:
                while not self.stop_flag:
                    raw = os.read(self.read_pipe, 1000)
                    if raw:
                        self.output.write(raw.decode())
            except Exception:
                self.exc_info = sys.exc_info()

        self.stop_flag = False
        self.thread = threading.Thread(target=redirect_thread)
        self.thread.daemon = True  # Makes the thread non-blocking
        self.thread.start()

    def post(self):
        if self.not_redirecting() or self.saved_fd == None:
            return
        sys.stdout.flush()
        self.libc.fflush(self.c_stdstream)
        os.dup2(self.saved_fd, self.target)
        self.stop_flag = True
        os.close(self.read_pipe)
        os.close(self.saved_fd)
        if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            self.thread.join()
        self.thread = None
        self.saved_fd = None
        if self.exc_info:
            ip.showtraceback()


@magics_class
class MatlabMagics(Magics):
    """
    Class for IPython magics for interacting with Matlab

    It defines several magic functions:

    %pace_python - sets up the plotting environment (default 'inline')
    %matlab_fig - defines the inline figure size and resolution for the next plot only
    """

    def __init__(self, shell, interface):
        super(MatlabMagics, self).__init__(shell)
        self.m = interface
        self.output = 'inline'
        self.plot_type = 'inline'
        self.width = 400
        self.height = 300
        self.resolution = 300
        self.next_pars = None
        global _magic_class_ref
        _magic_class_ref = self

    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('plot_type', type=str, help="Matlab plot type, either: 'inline' or 'windowed'")
    @magic_arguments.argument('output', nargs='?', type=str, help="Matlab output, either: 'inline' or 'console'")
    @magic_arguments.argument('-w', '--width', type=int, help="Default figure width in pixels [def: 400]")
    @magic_arguments.argument('-h', '--height', type=int, help="Default figure height in pixels [def: 300]")
    @magic_arguments.argument('-r', '--resolution', type=int, help="Default figure resolution in dpi [def: 150]")
    def pace_python(self, line):
        """Set up pace_python to work with IPython notebooks
        
        Use this magic function to set the behaviour of Matlab programs Horace and SpinW in Python.
        You can specify how plots should appear: either 'inline' [default] or 'windowed'.
        You can also specify how Matlab text output from functions appear: 'inline' [default] or 'console'

        Examples
        --------
        By default the inline backend is used for both figures and outputs. 
        To switch behaviour use, use:

            In [1]: %pace_python windowed             # windowed figures, output unchanged ('inline' default)
            In [2]: %pace_python console              # figure unchanged ('inline' default), console output
            In [3]: %pace_python windowed console     # windowed figures, console output
            In [4]: %pace_python inline inline        # inline figures, inline output
            In [5]: %pace_python inline               # inline figures, inline output
            In [6]: %pace_python inline console       # inline figures, console output
            In [7]: %pace_python windowed inline      # windowed figures, console output

        Note that if you specify `%pace_python inline` this sets `'inline'` for _both_ figures and outputs.
        If you want inline figures and console outputs or windowed figures and inline output you must specify
        that specifically.

        Note that using (default) inline text output imposes a slight performance penalty.

        For inlined figures, you can also set the default figure size and resolution with

            In [8]: %pace_python inline --width 400 --height 300 --resolution 150

        The values are in pixels for the width and height and dpi for resolution. A short cut:

            In [9]: %pace_python inline -w 400 -h 300 -r 150

        Also works. The width, height and resolution only applies to inline figures.
        You should use the usual Matlab commands to resize windowed figures.
        """
        args = magic_arguments.parse_argstring(self.pace_python, line)
        plot_type = args.plot_type if args.plot_type else self.plot_type
        output = args.output if args.output else self.output
        if args.plot_type and args.plot_type == 'inline' and args.output == None:
            output = 'inline'
        self.output = output
        if plot_type == 'inline':
            self.plot_type = plot_type
            if args.width: self.width = args.width
            if args.height: self.height = args.height
            if args.resolution: self.resolution = args.resolution
            self.m.call('set', (0., 'defaultfigurevisible', 'off'), nargout=0)
            self.m.call('set', (0., 'defaultfigurepaperpositionmode', 'manual'), nargout=0)
        elif plot_type == 'windowed':
            self.plot_type = plot_type
            self.m.call('set', (0., 'defaultfigurevisible', 'on'), nargout=0)
            self.m.call('set', (0., 'defaultfigurepaperpositionmode', 'auto'), nargout=0)
        else:
            raise RuntimeError(f'Unknown plot type {plot_type}')

    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-w', '--width', type=int, help="Default figure width in pixels [def: 400]")
    @magic_arguments.argument('-h', '--height', type=int, help="Default figure height in pixels [def: 300]")
    @magic_arguments.argument('-r', '--resolution', type=int, help="Default figure resolution in dpi [def: 150]")
    def matlab_fig(self, line):
        """Defines size and resolution of the next inline Matlab figure to be plotted

        Use this magic function to define the figure size and resolution of the next figure
        (and only that figure) without changing the default size and resolution.

        Examples
        --------
        Size and resolution is specified as options, any which is not defined here will use the default values
        These values are reset after the figure is plotted (default: width=400, height=300, resolution=150)

            In [1]: %matlab_fig -w 800 -h 200 -r 300
                    m.plot(-pi:0.01:pi, sin(-pi:0.01:pi), '-')

            In [2]: m.plot(-pi:0.01:pi, cos(-pi:0.01:pi), '-')

        The sine graph in the first cell will be 800x200 at 300 dpi, whilst the cosine graph is 400x300 150 dpi.
        """
        args = magic_arguments.parse_argstring(self.matlab_fig, line)
        width = args.width if args.width else self.width
        height = args.height if args.height else self.height
        resolution = args.resolution if args.resolution else self.resolution
        self.next_pars = {'width':width, 'height':height, 'resolution':resolution}
