import os
import platform
from .funcinspect import lhs_info

class Matlab(object):
    def __init__(self, mlPath=None, knowBetter=False):
        """
        Create an interface to a matlab compiled python library and treat the objects in a python/matlab way instead of
        the ugly way it is done by default.

        :param mlPath: Path to the SDK i.e. '/MATLAB/MATLAB_Runtime/v96' or to the location where matlab is installed
        (MATLAB root directory)
        :param knowBetter: The program tries to auto suggest the necessary directories. If we know better than the
        program this parameter is True. Otherwise, False
        """

        self.checkPath(mlPath, knowBetter)
        # We do the import here as we have to set the ENV before we can import
        from pyHorace import horace
        print('Interface opened')
        self.process = horace
        self.interface = None
        self.pyMatlab = None
        self.converter = None
        self.initialize()

    def initialize(self):
        """
        Initialize the matlab environment. This can only be done after the module has been imported.

        :return: None. obj has been filled with initialization pars.
        """
        self.interface = self.process.initialize()
        import matlab as pyMatlab
        from .DataTypes import DataTypes
        self.pyMatlab = pyMatlab
        self.converter = DataTypes(self.interface, pyMatlab)
        self.interface.call('pyhorace_init', [], nargout=0)

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
                    nargout = max(min(int(self.interface.getArgOut(name, nargout=1)), nreturn), 1)
                results = self.interface.call_method(name, [], self.converter.encode(args), nargout=nargout)
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
            self.interface.exit()
            self.interface = None
            self.pyMatlab = None
            print('Interface closed')

    def checkPath(self, mlPath, knowBetter=False):
        """
        Sets the environmental variables for Win, Mac, Linux

        :param mlPath: Path to the SDK i.e. '/MATLAB/MATLAB_Runtime/v96' or to the location where matlab is installed
        (MATLAB root directory)
        :param knowBetter: The program tries to auto suggest the necessary directories. If we know better than the
        program this parameter is True. Otherwise, False
        :return: None
        """

        class osObj(object):
            def __init__(self):
                self.ver = 'v96'
                self.PLATFORM_DICT = {'Windows': ['PATH', 'dll', ''], 'Linux': ['LD_LIBRARY_PATH', 'so', 'libmw'],
                         'Darwin': ['DYLD_LIBRARY_PATH', 'dylib', 'libmw']}
                self.system = None
                self.arch = None
                self.path_var = None
                self.ext = None
                self.lib_prefix = None
                self.is_linux = False
                self.is_mac = False
                self.is_windows = False

        # This will return 'Windows', 'Linux', or 'Darwin' (for Mac).
        obj = osObj()
        obj.system = platform.system()
        if obj.system not in obj.PLATFORM_DICT:
            raise RuntimeError('{0} is not a supported platform.'.format(obj.system))
        else:
            # path_var is the OS-dependent name of the path variable ('PATH', 'LD_LIBRARY_PATH', "DYLD_LIBRARY_PATH')
            (obj.path_var, obj.ext, obj.lib_prefix) = obj.PLATFORM_DICT[obj.system]

        if obj.system == 'Windows':
            obj.is_windows = True
            bit_str = platform.architecture()[0]
            if bit_str == '64bit':
                obj.arch = 'win64'
            elif bit_str == '32bit':
                obj.arch = 'win32'
            else:
                raise RuntimeError('{0} is not supported.'.format(bit_str))
        elif obj.system == 'Linux':
            obj.is_linux = True
            obj.arch = 'glnxa64'
        elif obj.system == 'Darwin':
            obj.is_mac = True
            obj.arch = 'maci64'
        else:
            raise RuntimeError('Operating system {0} is not supported.'.format(obj.system))

        if mlPath:
            if not os.path.exists(os.path.join(mlPath, obj.ver)):
                if not os.path.exists(mlPath):
                    raise FileNotFoundError
                obj.ver = ''
        else:
            mlPath = ''
            obj.ver = ''

        ASSUMED_PATH = os.path.join(mlPath, obj.ver, 'runtime', obj.arch) + ':' + \
                       os.path.join(mlPath, obj.ver, 'sys', 'os', obj.arch) + ':' + \
                       os.path.join(mlPath, obj.ver, 'bin', obj.arch) + ':' + \
                       os.path.join(mlPath, obj.ver, 'extern', 'bin', obj.arch)

        if mlPath:
            f = ': '
            if ASSUMED_PATH not in mlPath:
                if not knowBetter:
                    mlPath = ASSUMED_PATH
                    f = ' forced: '
            os.environ[obj.path_var] = mlPath
            print('Set' + f + os.environ.get(obj.path_var))
        else:
            if obj.path_var in os.environ:
                mlPath = os.environ.get(obj.path_var)
                # if ASSUMED_PATH not in mlPath:
                #     if not knowBetter:
                #         raise EnvironmentError
                # else:
                print('Found: ' + os.environ.get(obj.path_var))


#         DYLD_LIBRARY_PATH:
#         /Applications/MATLAB/MATLAB_Runtime/v96/runtime/maci64:/Applications/MATLAB/MATLAB_Runtime/v96/sys/os/maci64:/Applications/MATLAB/MATLAB_Runtime/v96/bin/maci64:/Applications/MATLAB/MATLAB_Runtime/v96/extern/bin/maci64:/Users/simonward/.conda/envs/pySpinW2/lib



