import os, sys
import platform
from .funcinspect import lhs_info
from pace_neutrons_cli.utils import get_runtime_version, checkPath

# On Windows/Conda we need to load numpy DLLs before Matlab starts
import numpy
# On some systems we need to load the BLAS/LAPACK libraries with the DEEPBIND
# flag so it doesn't conflict with Matlab's BLAS/LAPACK.
# This only works if users `import pace_neutrons` before they import scipy...
if platform.system() == 'Linux':
    old_flags = sys.getdlopenflags()
    sys.setdlopenflags(os.RTLD_NOW | os.RTLD_DEEPBIND)
    try:
        import scipy.linalg
    except ImportError:
        pass
    sys.setdlopenflags(old_flags)

# Import brille here to load its C module before Matlab gets loaded
try:
    import brille
except ImportError:
    pass

# Store the Matlab engine as a module global wrapped inside a class
# When the global ref is deleted (e.g. when Python exits) the __del__ method is called
# Which then gracefully shutsdown Matlab, else we get a segfault.
_global_matlab_ref = None
_has_registered_magic = None

class _MatlabInstance(object):
    def __init__(self, runtime_version, mlPath):
        checkPath(runtime_version, mlPath)
        # We do the import here as we have to set the ENV before we can import
        from pace_neutrons import pace
        self._interface = pace.initialize()
        print('Interface opened')
        self._interface.call('pyhorace_init', [], nargout=0)

    def __del__(self):
        if self._interface:
            self._interface.exit()
            print('Interface closed')
            self._interface = None

    def __getattr__(self, name):
        if self._interface:
            return getattr(self._interface, name)
        else:
            raise RuntimeError('Matlab interface is not open')


class Matlab(object):
    def __init__(self, mlPath=None):
        """
        Create an interface to a matlab compiled python library and treat the objects in a python/matlab way instead of
        the ugly way it is done by default.

        :param mlPath: Path to the SDK i.e. '/MATLAB/MATLAB_Runtime/v96' or to the location where matlab is installed
        (MATLAB root directory)
        """
 
        self.interface = None
        self.pyMatlab = None
        self.converter = None
        self.initialize(mlPath)

    def initialize(self, mlPath=None):
        """
        Initialize the matlab environment. This can only be done after the module has been imported.

        :return: None. obj has been filled with initialization pars.
        """
        global _global_matlab_ref
        if _global_matlab_ref is None: 
            _global_matlab_ref = _MatlabInstance(get_runtime_version(), mlPath)
        self.interface = _global_matlab_ref
        import matlab as pyMatlab
        from .DataTypes import DataTypes
        self.pyMatlab = pyMatlab
        self.converter = DataTypes(self.interface, pyMatlab)

    def __getattr__(self, name):
        """
        Override for the get attribute. We don't want to call the process but the interface, so redirect calls there and
        return a MatlabProxyObject

        :param name: The function/class to be called.
        :return: MatlabProxyObject of class/function given by name
        """

        def method(*args, **kwargs):
            nargout = kwargs.pop('nargout') if 'nargout' in kwargs.keys() else None
            nreturn = lhs_info(output_type='nreturns')
            try:
                if nargout is None:
                    mnargout, undetermined = self.interface.getArgOut(name, nargout=2)
                    if not undetermined:
                        nargout = max(min(int(mnargout), nreturn), 1)
                    else:
                        nargout = max(nreturn, 1)
                m_args = [self.converter.encode(ar) for ar in args] 
                results = self.interface.call_method(name, [], m_args, nargout=nargout)
                return self.converter.decode(results)
            except Exception as e:
                print(e)
                return []
        return method

    def __del__(self):
        """
        Auto close the python/MATLAB interface.
        :return: None
        """
        if self.interface:
            self.interface = None
            self.pyMatlab = None

    def type(self, obj):
        if obj._is_thin_wrapper:
            return self.interface.call('evalin', ['base', 'class({})'.format(obj._objstr)], nargout=1)
        else:
            return self.interface.call('class', [obj.handle], nargout=1)


def register_ipython_magics():
    try:
        import IPython 
    except ImportError:
        return None
    else:
        running_kernel = IPython.get_ipython()
        # Only register these magics when running in a notebook / lab
        # Other values seen are: 'TerminalInteractiveShell' and 'InteractiveShellEmbed'
        if running_kernel.__class__.__name__ != 'ZMQInteractiveShell':
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
    redirect_stdout = IPythonMagics.Redirection(target='stdout')
    running_kernel.events.register('pre_run_cell', redirect_stdout.pre)
    running_kernel.events.register('post_run_cell', redirect_stdout.post)

if not _has_registered_magic:
    register_ipython_magics()
