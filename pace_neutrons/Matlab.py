import os, sys
import platform
from .funcinspect import lhs_info
# On Windows/Conda we need to load numpy DLLs before Matlab starts
import numpy
# On some systems we need to load the BLAS/LAPACK libraries with the DEEPBIND
# flag so it doesn't conflict with Matlab's BLAS/LAPACK.
# This only works if users `import pace_neutrons` before they import scipy...
if platform.system() == 'Linux':
    old_flags = sys.getdlopenflags()
    sys.setdlopenflags(os.RTLD_NOW | os.RTLD_DEEPBIND)
    import scipy.linalg
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
            _global_matlab_ref = _MatlabInstance(self.get_runtime_version(), mlPath)
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

    def get_runtime_version(self):
        # Looks in the Matlab generated __init__ file to determine the required Matlab version
        with open(os.path.join(os.path.dirname(__file__), 'pace', '__init__.py'), 'r') as pace_init:
            for line in pace_init:
                if 'RUNTIME_VERSION_W_DOTS' in line:
                    return line.split('=')[1].strip().replace("'",'')

    def type(self, obj):
        if obj._is_thin_wrapper:
            return self.interface.call('evalin', ['base', 'class({})'.format(obj._objstr)], nargout=1)
        else:
            return self.interface.call('class', [obj.handle], nargout=1)

def checkPath(runtime_version, mlPath):
    """
    Sets the environmental variables for Win, Mac, Linux

    :param mlPath: Path to the SDK i.e. '/MATLAB/MATLAB_Runtime/v96' or to the location where matlab is installed
    (MATLAB root directory)
    :return: None
    """

    class osObj(object):
        def __init__(self, version):
            self.ver = version
            self.PLATFORM_DICT = {'Windows': ['PATH', 'dll', ''], 'Linux': ['LD_LIBRARY_PATH', 'so', 'libmw'],
                     'Darwin': ['DYLD_LIBRARY_PATH', 'dylib', 'libmw']}
            # Note that newer Matlabs are 64-bit only
            self.ARCH_DICT = {'Windows': {'64bit': 'pcwin64', '32bit': 'pcwin32'},
                              'Linux': {'64bit': 'glnxa64', '32bit': 'glnx86'},
                              'Darwin': {'64bit': 'maci64', '32bit': 'maci'}}
            self.system = platform.system()
            if self.system not in self.PLATFORM_DICT:
                raise RuntimeError('{0} is not a supported platform.'.format(self.system))
            (self.path_var, self.ext, self.lib_prefix) = self.PLATFORM_DICT[self.system]
            self.arch = self.ARCH_DICT[self.system][platform.architecture()[0]]
            if self.system == 'Windows':
                self.file_to_find = ''.join((self.lib_prefix, 'mclmcrrt', self.ver.replace('.','_'), '.', self.ext))
                self.sep = ';'
            elif self.system == 'Linux':
                self.file_to_find = ''.join((self.lib_prefix, 'mclmcrrt', '.', self.ext, '.', self.ver))
                self.sep = ':'
            elif self.system == 'Darwin':
                self.file_to_find = ''.join((self.lib_prefix, 'mclmcrrt', '.', self.ver, '.', self.ext))
                self.sep = ':'
            else:
                raise RuntimeError(f'Operating system {self.system} is not supported.')

        def find_version(self, root_dir, raise_if_not_found=True):
            def check_lib_file(obj, ver, runtime_dir):
                arch = next(os.walk(runtime_dir))[1]
                if len(arch) == 1 and os.path.exists(os.path.join(runtime_dir, arch[0], self.file_to_find)):
                    self.ver, self.arch = (ver, arch[0])
                    rv = os.path.dirname(runtime_dir)
                    print(f'Found Matlab {ver} {self.arch} at {rv}')
                    return rv
                return None
            sub_dirs = next(os.walk(root_dir))[1]
            for sub_dir in sub_dirs:
                # We use the highest version
                runtime_dir = os.path.join(root_dir, sub_dir, 'runtime')
                if os.path.isdir(runtime_dir):
                    rv = check_lib_file(self, sub_dir, runtime_dir)
                    if rv: return rv
                else:
                    # Search one more level ('MATLAB_Runtime' is often below 'MATLAB' for MCRs)
                    full_subdir = os.path.join(root_dir, sub_dir)
                    subsubs = next(os.walk(full_subdir))[1]
                    subsubs.sort()
                    for subsub in subsubs[::-1]:
                        sub_runtime = os.path.join(full_subdir, subsub)
                        if os.path.isdir(sub_runtime):
                            rv = check_lib_file(self, subsub, sub_runtime)
                            if rv: return rv
            if raise_if_not_found:
                raise FileNotFoundError(f'Required Matlab version {self.ver} not found in folder {root_dir}')
            else:
                return None

        def guess_path(self):
            GUESSES = {'Windows': [r'C:\Program Files\MATLAB', r'C:\Program Files (x86)\MATLAB', 
                                   r'C:\Program Files\MATLAB\MATLAB Runtime', r'C:\Program Files (x86)\MATLAB\MATLAB Runtime'],
                       'Linux': ['/usr/local/MATLAB', '/opt/MATLAB', '/opt', '/usr/local/MATLAB/MATLAB_Runtime'],
                       'Darwin': ['/Applications/MATLAB']}
            for possible_dir in GUESSES[self.system]:
                if os.path.isdir(possible_dir):
                    rv = self.find_version(possible_dir, raise_if_not_found=False)
                    if rv is not None:
                       return rv
            return None

        def guess_from_env(self):
            ld_path = os.getenv(obj.path_var)
            if ld_path is None: return None
            for possible_dir in ld_path.split(self.sep):
                if os.path.exists(os.path.join(possible_dir, self.file_to_find)):
                    return os.path.abspath(os.path.join(possible_dir, '..', '..'))
            return None
            
    # We use a class to try to get the necessary variables.
    obj = osObj(runtime_version)

    if mlPath:
        if not os.path.exists(os.path.join(mlPath)):
            if not os.path.exists(mlPath):
                raise FileNotFoundError(f'Input Matlab folder {mlPath} not found')
    else:
        mlPath = obj.guess_from_env()
        if mlPath is None:
            mlPath = obj.guess_path()
            if mlPath is None:
                raise RuntimeError('Cannot find Matlab')
            else:
                needed_dirs = ['runtime', os.path.join('sys', 'os'), 'bin', os.path.join('extern', 'bin')]
                ld_path = obj.sep.join([os.path.join(mlPath, sub, obj.arch) for sub in needed_dirs])
                os.environ[obj.path_var] = ld_path
                print('Set ' + os.environ.get(obj.path_var))
        else:
            print('Found: ' + os.environ.get(obj.path_var))


def register_ipython_magics():
    try:
        import IPython 
    except ImportError:
        return None
    global _has_registered_magic
    _has_registered_magic = True
    running_kernel = IPython.get_ipython()
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
