import os, sys
import platform
import shutil
from .funcinspect import lhs_info
sys.path.append(os.path.join(os.path.abspath(__file__), '..', 'Debug'))
import libpymcr
from .MatlabProxyObject import wrap, unwrap
#from pace_neutrons_cli.utils import get_runtime_version, checkPath

# Store the Matlab engine as a module global wrapped inside a class
# When the global ref is deleted (e.g. when Python exits) the __del__ method is called
# Which then gracefully shutsdown Matlab, else we get a segfault.
_global_matlab_ref = None
_has_registered_magic = None

class _MatlabInstance(object):
    def __init__(self):#, runtime_version, mlPath):
        # checkPath(runtime_version, mlPath)
        # # We do the import here as we have to set the ENV before we can import
        # from pace_neutrons import pace
        self.interface = libpymcr.matlab(u'libpace.ctf', r'c:\Program Files\MATLAB\R2020a')
        print('Interface opened')

        #self.interface.call('pyhorace_init', [], nargout=0)
        ## Sets the parallel worker to the compiled worker if it exists
        #if 'worker' not in sys.argv[0]:
        #    is_windows = platform.system() == 'Windows'
        #    worker_path = os.path.join(os.path.dirname(sys.argv[0]), 'worker_v2')
        #    if is_windows:
        #        worker_path = worker_path + '.exe'
        #    if not os.path.exists(worker_path):
        #        # Tries to search for it on the path
        #        worker_path = shutil.which('worker_v2')
        #    if worker_path:
        #        pc = self.interface.call('parallel_config', nargout=1)
        #        access = self.interface.call('substruct', '.', 'worker')
        #        self.interface.call('subsasgn', pc, access, worker_path)

    def __getattr__(self, name):
        if self.interface:
            return getattr(self.interface, name)
        else:
            raise RuntimeError('Matlab interface is not open')


class NamespaceWrapper(object):
    def __init__(self, interface, name):
        self._interface = interface
        self._name = name

    def __getattr__(self, name):
        return NamespaceWrapper(self._matlab, f'{self._name}.{name}')

    def __call__(self, *args, **kwargs):
        nargout = kwargs.pop('nargout') if 'nargout' in kwargs.keys() else None
        nreturn = lhs_info(output_type='nreturns')
        if nargout is None:
            mnargout, undetermined = self._interface.call('getArgOut', self._name, nargout=2)
            if not undetermined:
                nargout = max(min(int(mnargout), nreturn), 1)
            else:
                nargout = max(nreturn, 1)
        args += sum(kwargs.items(), ())
        args = unwrap(args, self._interface)
        return wrap(self._interface.call(self._name, *args, nargout=nargout), self._interface)

    def getdoc(self):
        # To avoid error message printing in Spyder
        raise NotImplementedError


class Matlab(object):
    def __init__(self, mlPath=None):
        """
        Create an interface to a matlab compiled python library and treat the objects in a python/matlab way instead of
        the ugly way it is done by default.

        :param mlPath: Path to the SDK i.e. '/MATLAB/MATLAB_Runtime/v96' or to the location where matlab is installed
        (MATLAB root directory)
        """

        global _global_matlab_ref
        if _global_matlab_ref is None:
            _global_matlab_ref = _MatlabInstance()#get_runtime_version(), mlPath)
        self._interface = _global_matlab_ref.interface

    def __getattr__(self, name):
        """
        Override for the get attribute. We don't want to call the process but the interface, so redirect calls there and
        return a MatlabProxyObject

        :param name: The function/class to be called.
        :return: MatlabProxyObject of class/function given by name
        """
        return NamespaceWrapper(self._interface, name)

    def type(self, obj):
        return self._interface.call('class', obj.handle, nargout=1)


def register_ipython_magics():
    try:
        import IPython
    except ImportError:
        return None
    else:
        running_kernel = IPython.get_ipython()
        # Only register these magics when running in a notebook / lab
        # Other values seen are: 'TerminalInteractiveShell' and 'InteractiveShellEmbed'
        if (running_kernel.__class__.__name__ != 'ZMQInteractiveShell'
            and running_kernel.__class__.__name__ != 'SpyderShell'):
            return None
    global _has_registered_magic
    _has_registered_magic = True
    if running_kernel is None or sys.__stdout__ is None or sys.__stderr__ is None:
        return None
    from . import IPythonMagics
    from traitlets import Instance
    shell = Instance('IPython.core.interactiveshell.InteractiveShellABC', allow_none=True)
    magics = IPythonMagics.MatlabMagics(shell, None)
    running_kernel.register_magics(magics)
    running_kernel.events.register('post_run_cell', IPythonMagics.showPlot)
    # Only do redirection for Jupyter notebooks - causes errors on Spyder
    if running_kernel == 'ZMQInteractiveShell':
        redirect_stdout = IPythonMagics.Redirection(target='stdout')
        running_kernel.events.register('pre_run_cell', redirect_stdout.pre)
        running_kernel.events.register('post_run_cell', redirect_stdout.post)


if not _has_registered_magic:
    register_ipython_magics()
