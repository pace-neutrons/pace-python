import os
import platform
from .MatlabProxyObject import MatlabProxyObject

class Matlab(object):
    def __init__(self, mlPath=None, knowBetter=False):

        self.checkPath(mlPath, knowBetter)

        from spinwCompilePyLib.for_testing import spinw
        print('Interface opened')
        self.Matlab = spinw
        self.interface = None

    def initialize(self):
        self.interface = self.Matlab.initialize()
        return

    def __getattr__(self, name):
        def method(*args):
            print("tried to handle unknown method " + name)
            if args:
                print("it had arguments: " + str(args))
            # print("tried to handle unknown method " + name)
            # if args:
            #     print("it had arguments: " + str(args))
            #     obj = self.interface.feval(name)
            # else:
            #     obj = self.interface.feval(name, *args)
            # return MatlabProxyObject(self, obj)
        return method

    def __del__(self):
        print('Interface closed')

    def checkPath(self, mlPath, knowBetter=False):

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



