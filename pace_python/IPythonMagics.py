from IPython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.display import Image, display
from matlab import double as md

import os
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

_magic_class_ref = None

# We will overload the `post_run_cell` event with this function
# That callback is a method of `EventManager` hence the `self` argument
def showPlot(self=None, result=None):
    # We use a global reference to the magics class to get the reference to Matlab interpreter
    # If it doesn't exist, we can't do anything, and assume the user is just using Python
    ip = get_ipython()
    if ip is None or _magic_class_ref == None or _magic_class_ref.plot_type != 'inline':
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
    @magic_arguments.argument('-w', '--width', type=int, help="Default figure width in pixels [def: 400]")
    @magic_arguments.argument('-h', '--height', type=int, help="Default figure height in pixels [def: 300]")
    @magic_arguments.argument('-r', '--resolution', type=int, help="Default figure resolution in dpi [def: 150]")
    def pace_python(self, line):
        """Set up pace_python to work with IPython notebooks
        
        Use this magic function to set the default plot type, figure size and resolution.

        Examples
        --------
        By default the inline backend is used. To switch to windows figures, use:

            In [1]: %pace_python windowed

        You for inlined figures, you can also set the default figure size and resolution with

            In [2]: %pace_python inline --width 400 --height 300 --resolution 150

        The values are in pixels for the width and height and dpi for resolution. A short cut:

            In [3]: %pace_python inline -w 400 -h 300 -r 150

        Also works. The width, height and resolution only applies to inline figures.
        You should use the usual Matlab commands to resize windowed figures.
        """
        args = magic_arguments.parse_argstring(self.pace_python, line)
        if args.plot_type == 'inline':
            self.plot_type = args.plot_type
            if args.width: self.width = args.width
            if args.height: self.height = args.height
            if args.resolution: self.resolution = args.resolution
            self.m.call('set', (0., 'defaultfigurevisible', 'off'), nargout=0)
            self.m.call('set', (0., 'defaultfigurepaperpositionmode', 'manual'), nargout=0)
        elif args.plot_type == 'windowed':
            self.plot_type = args.plot_type
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
