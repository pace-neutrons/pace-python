import os, sys
import platform
import shutil
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


def _disable_umr():
    # Mark Matlab libraries so Spyder does not reload (*delete*) them
    if 'spydercustomize' not in sys.modules:
        return
    ll = '_internal,_internal.mlarray_utils,_internal.mlarray_sequence,mlarray,' \
         'mlexceptions,matlab,matlab_pysdk,matlab_pysdk.runtime.errorhandler,' \
         'matlab_pysdk.runtime.futureresult,matlab_pysdk.runtime.deployablefunc,' \
         'matlab_pysdk.runtime.deployableworkspace,matlab_pysdk.runtime,' \
         'matlab_pysdk.runtime.deployablepackage,matlabruntimeforpython3_8'

    if 'matlab_pysdk' not in sys.modules['spydercustomize'].__umr__.namelist:
        sys.modules['spydercustomize'].__umr__.namelist += ll.split(',')


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
        if 'SPYDER_ARGS' in os.environ:
            _disable_umr()
        # Sets the parallel worker to the compiled worker if it exists
        if 'worker' not in sys.argv[0]:
            is_windows = platform.system() == 'Windows'
            worker_path = os.path.join(os.path.dirname(sys.argv[0]), 'worker_v2')
            if is_windows:
                worker_path = worker_path + '.exe'
            if not os.path.exists(worker_path):
                # Tries to search for it on the path
                worker_path = shutil.which('worker_v2')
            if worker_path:
                pc = self._interface.call('parallel_config', [], nargout=1)
                access = self._interface.call('substruct', ['.', 'worker'])
                self._interface.call('subsasgn', [pc, access, worker_path])

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


class NamespaceWrapper(object):
    def __init__(self, matlab, name):
        self._matlab = matlab
        self._interface = matlab.interface
        self._converter = matlab.converter
        self._name = name

    def __getattr__(self, name):
        return NamespaceWrapper(self._matlab, f'{self._name}.{name}')

    def __call__(self, *args, **kwargs):
        nargout = kwargs.pop('nargout') if 'nargout' in kwargs.keys() else None
        nreturn = lhs_info(output_type='nreturns')
        if nargout is None:
            mnargout, undetermined = self._interface.getArgOut(self._name, nargout=2)
            if not undetermined:
                nargout = max(min(int(mnargout), nreturn), 1)
            else:
                nargout = max(nreturn, 1)
        m_args = [self._converter.encode(ar) for ar in args]
        results = self._interface.call_method(self._name, [], m_args, nargout=nargout)
        return self._converter.decode(results)

    def getdoc(self):
        # To avoid error message printing in Matlab
        raise NotImplementedError


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
        return NamespaceWrapper(self, name)

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
    redirect_stdout = IPythonMagics.Redirection(target='stdout')
    running_kernel.events.register('pre_run_cell', redirect_stdout.pre)
    running_kernel.events.register('post_run_cell', redirect_stdout.post)

if not _has_registered_magic:
    register_ipython_magics()
