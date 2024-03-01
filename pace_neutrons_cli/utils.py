import os
import sys
import glob
import platform
from pathlib import Path
from http import HTTPStatus


def get_runtime_version():
    try:
        from ._matlab_version import RUNTIME_VERSION_W_DOTS
        return RUNTIME_VERSION_W_DOTS
    except ImportError:
        pass
    # Looks in the Matlab generated __init__ file to determine the required Matlab version
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'pace', '__init__.py'), 'r') as pace_init:
        for line in pace_init:
            if 'RUNTIME_VERSION_W_DOTS' in line:
                return line.split('=')[1].strip().replace("'",'')


def get_matlab_from_registry(version=None):
    # Searches for the Mathworks registry key and finds the Matlab path from that
    retval = []
    try:
        import winreg
    except ImportError:
        return retval
    for installation in ['MATLAB', 'MATLAB Runtime', 'MATLAB Compiler Runtime']:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'SOFTWARE\\MathWorks\\{installation}') as key:
                versions = [winreg.EnumKey(key, k) for k in range(winreg.QueryInfoKey(key)[0])]
        except (FileNotFoundError, OSError):
            pass
        else:
            if version is not None:
                versions = [v for v in versions if v == version]
            for v in versions:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'SOFTWARE\\MathWorks\\{installation}\\{v}') as key:
                    retval.append(winreg.QueryValueEx(key, 'MATLABROOT')[0])
    return retval


def get_mantid():
    mantid_dir = None
    # If Mantid is installed on the path, can just import it
    try:
        import mantid
    except ImportError:
        pass
    else:
        return os.path.abspath(os.path.join(os.path.dirname(mantid.__file__), '..', '..'))
    # On Windows can look at the registry
    try:
        import winreg
    except ImportError:
        pass
    else:
        key_string = (r'SOFTWARE\ISIS Rutherford Appleton Laboratory UKRI, '
                      r'NScD Oak Ridge National Laboratory, '
                      r'European Spallation Source and Institut Laue - Langevin')
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_string) as key:
                mantids = {}
                for k in range(winreg.QueryInfoKey(key)[0]):
                    distro = winreg.EnumKey(key, k)
                    mantids[distro] = winreg.QueryValue(key, distro)
        except (FileNotFoundError, OSError):
            pass
        else:
            return mantids['mantid'] if 'mantid' in mantids else mantids.values()[0]
    # Else search standard paths
    GUESSES = {'Windows': [r'C:\MantidInstall', r'D:\MantidInstall', r'C:\MantidNightlyInstall',
                           r'C:\Program Files\Mantid', r'C:\Program Files (x86)\Mantid'], 
               'Linux': ['/opt/Mantid', '/opt/mantidnightly', '/usr/local/Mantid'],
               'Darwin': ['/Applications/Mantid']}
    for possible_dir in GUESSES[platform.system()]:
        if os.path.isdir(possible_dir):
            if os.path.exists(os.path.join(possible_dir, 'lib', 'mantid', '__init__.py')):
                return possible_dir
    return None


class PaceConfiguration(object):
    def __init__(self):
        import configparser
        import appdirs
        self.config_dir = appdirs.user_config_dir('pace_neutrons')
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.config_file = os.path.join(self.config_dir, 'pace.ini')
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        if 'pace' not in self.config:
            self.config['pace'] = {}
            self.IsFirstRun = True

    @property
    def CachedMatlabDirs(self):
        try:
            retval = self.config['pace']['CachedMatlabDirs'].split(';')
        except KeyError:
            retval = []
        return [r for r in retval if r != '']

    @CachedMatlabDirs.setter
    def CachedMatlabDirs(self, val):
        if not isinstance(val, str):
            raise RuntimeError('Cached Matlab folder must be a string')
        cached = self.CachedMatlabDirs
        if not any([d for d in cached if val in d]):
            cached += [val]
            self.config['pace']['CachedMatlabDirs'] = ';'.join(cached)

    @property
    def IsFirstRun(self):
        try:
            return self.config['pace']['IsFirstRun'] == 'True'
        except KeyError:
            self.config['pace']['IsFirstRun'] = 'True'
            return True

    @IsFirstRun.setter
    def IsFirstRun(self, val):
        self.config['pace']['IsFirstRun'] = str(val)

    @property
    def CachedCTFs(self):
        try:
            retval = self.config['pace']['CachedCTFs'].split(';')
        except KeyError:
            retval = []
        return [val for val in retval if val]

    @CachedCTFs.setter
    def CachedCTFs(self, val):
        try:
            val = str(val)
        except:
            raise RuntimeError('Cached CTF must be convertible to a string')
        cached = self.CachedCTFs
        if not any([d for d in cached if val in d]):
            cached += [val]
            self.config['pace']['CachedCTFs'] = ';'.join(cached)

    def save(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_val, trace):
        if exception_type is None:
            self.save()
            return True
        else:
            raise


class DetectMatlab(object):
    def __init__(self, version):
        self.ver = version
        self.PLATFORM_DICT = {'Windows': ['PATH', 'dll', ''], 'Linux': ['LD_LIBRARY_PATH', 'so', 'libmw'],
                 'Darwin': ['DYLD_LIBRARY_PATH', 'dylib', 'libmw']}
        # Note that newer Matlabs are 64-bit only
        self.ARCH_DICT = {'Windows': {'64bit': 'win64', '32bit': 'pcwin32'},
                          'Linux': {'64bit': 'glnxa64', '32bit': 'glnx86'},
                          'Darwin': {'64bit': 'maci64', '32bit': 'maci'}}
        # https://uk.mathworks.com/help/compiler/mcr-path-settings-for-run-time-deployment.html
        DIRS = ['runtime', os.path.join('sys', 'os'), 'bin', os.path.join('extern', 'bin')]
        self.REQ_DIRS = {'Windows':[DIRS[0]], 'Darwin':DIRS[:3], 'Linux':DIRS}
        self.system = platform.system()
        if self.system not in self.PLATFORM_DICT:
            raise RuntimeError('{0} is not a supported platform.'.format(self.system))
        (self.path_var, self.ext, self.lib_prefix) = self.PLATFORM_DICT[self.system]
        self.arch = self.ARCH_DICT[self.system][platform.architecture()[0]]
        self.required_dirs = self.REQ_DIRS[self.system]
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

    def find_version(self, root_dir):
        def find_file(path, filename, max_depth=3):
            """ Finds a file, will return first match"""
            for depth in range(max_depth + 1):
                dirglobs = f'*{os.sep}'*depth
                files = glob.glob(f'{path}{os.sep}{dirglobs}{filename}')
                files = list(filter(os.path.isfile, files))
                if len(files) > 0:
                    return files[0]
            return None
        lib_file = find_file(root_dir, self.file_to_find)
        if lib_file is not None:
            lib_path = Path(lib_file)
            arch_dir = lib_path.parts[-2]
            self.arch = arch_dir
            ml_subdir = lib_path.parts[-3]
            if ml_subdir != 'runtime':
                self.ver = ml_subdir
            ml_path = os.path.abspath(lib_path.parents[2])
            print(f'Found Matlab {self.ver} {self.arch} at {ml_path}')
            return ml_path
        else:
            return None

    def guess_path(self, mlPath=[]):
        GUESSES = {'Windows': [r'C:\Program Files\MATLAB', r'C:\Program Files (x86)\MATLAB', 
                               r'C:\Program Files\MATLAB\MATLAB Runtime', r'C:\Program Files (x86)\MATLAB\MATLAB Runtime'],
                   'Linux': ['/usr/local/MATLAB', '/opt/MATLAB', '/opt', '/usr/local/MATLAB/MATLAB_Runtime'],
                   'Darwin': ['/Applications/MATLAB']}
        if self.system == 'Windows':
            mlPath += get_matlab_from_registry(self.ver) + GUESSES['Windows']
        for possible_dir in mlPath + GUESSES[self.system]:
            if os.path.isdir(possible_dir):
                rv = self.find_version(possible_dir)
                if rv is not None:
                   return rv
        return None

    def guess_from_env(self):
        ld_path = os.getenv(self.path_var)
        if ld_path is None: return None
        for possible_dir in ld_path.split(self.sep):
            if os.path.exists(os.path.join(possible_dir, self.file_to_find)):
                return os.path.abspath(os.path.join(possible_dir, '..', '..'))
        return None

    def env_not_set(self):
        # Determines if the environment variables required by the MCR are set
        if self.path_var not in os.environ:
            return True
        rt = os.path.join('runtime', self.arch)
        pv = os.getenv(self.path_var).split(self.sep)
        for path in [dd for dd in pv if rt in dd]:
            if self.find_version(os.path.join(path,'..','..')) is not None:
                return False
        return True

    def set_environment(self, mlPath=None):
        if mlPath is None:
            mlPath = self.guess_path()
        if mlPath is None:
            raise RuntimeError('Could not find Matlab')
        req_matlab_dirs = self.sep.join([os.path.join(mlPath, sub, self.arch) for sub in self.required_dirs])
        if self.path_var not in os.environ:
            os.environ[self.path_var] = req_matlab_dirs
        else:
            os.environ[self.path_var] += self.sep + req_matlab_dirs
        return None


def checkPath(runtime_version, mlPath):
    """
    Sets the environmental variables for Win, Mac, Linux

    :param mlPath: Path to the SDK i.e. '/MATLAB/MATLAB_Runtime/v96' or to the location where matlab is installed
    (MATLAB root directory)
    :return: None
    """

    # We use a class to try to get the necessary variables.
    obj = DetectMatlab(runtime_version)

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
                ld_path = obj.sep.join([os.path.join(mlPath, sub, obj.arch) for sub in obj.required_dirs])
                os.environ[obj.path_var] = ld_path
                print('Set ' + os.environ.get(obj.path_var))
        else:
            print('Found: ' + os.environ.get(obj.path_var))


def release_exists(tag_name, retval='upload_url', use_auth=True):
    import requests, json, re
    headers = {}
    if use_auth:
        headers = {"Authorization": "token " + os.environ["GITHUB_TOKEN"]}
    response = requests.get(
        'https://api.github.com/repos/pace-neutrons/pace-python/releases',
        headers=headers)
    print(response.text)
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError('Could not query Github if release exists')
    response = json.loads(response.text)
    desired_release = [v for v in response if v['tag_name'] == tag_name]
    if desired_release:
        return desired_release[0][retval]
    else:
        return False


def download_github(url, local_filename=None, use_auth=True):
    import requests
    headers = {"Accept":"application/octet-stream"}
    if use_auth:
        headers["Authorization"] = "token " + os.environ["GITHUB_TOKEN"]
    if not local_filename:
        local_filename = url.split('/')[-1]
    with requests.get(url, stream=True, headers=headers) as r:
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def install_MCR(interactive=False):
    """
    Downloads an installer from github which would install the required MCR components only
    This relies on there being the correct version of the installer available
    """
    if interactive:
        p = input('Do you want to automatically install the MCR? ("y" or "n")')
        if not p.lower().startswith('y'):
            return
    import tempfile, subprocess
    try:
        import requests, json
    except ImportError:
        # Try to pip install it internally
        proc = subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'requests', 'json'],
                              capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError('Could not import or install the requests module to communicate with github')
        print(proc.stdout.decode())
    from pace_neutrons import __version__
    assets_url = release_exists('v' + __version__, retval='assets_url', use_auth=False)
    if not assets_url:
        raise RuntimeError(f'No Github release exists for pace_neutrons version {__version__}')
    response = requests.get(assets_url)
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError('Could not query Github for list of assets')
    response = json.loads(response.text)
    INSTALLERS = {'Windows':'pace_neutrons_installer_win32.exe', 'Linux':'pace_neutrons_installer_linux.install'}
    system = platform.system()
    try:
        installer_name = INSTALLERS[system]
    except KeyError:
        raise RuntimeError(f'No installer exists for OS: {system}')
    try:
        installer_url = [a['url'] for a in response if installer_name in a['name']][0]
    except IndexError:
        raise RuntimeError(f'Could not find the installer in the Github release')
    if interactive:
        lic_file = os.path.join(os.path.dirname(__file__), '..', 'pace_neutrons', 'MCR_license.txt')
        with open(lic_file, 'r') as lic:
            print(lic.read())
        p = input('Do agree with the above license? ("y" or "n")')
        if not p.lower().startswith('y'):
            return
    else:
        print(('By running this you agree to the Matlab MCR license.\n'
               'A copy can be found at:\n'
               'https://github.com/pace-neutrons/pace-python/tree/main/pace_neutrons/MCR_license.txt'))
    with tempfile.TemporaryDirectory() as dd:
        installer_file = os.path.join(dd, installer_name)
        download_github(installer_url, local_filename=installer_file, use_auth=False)
        prefix = []
        if system != 'Windows':
            os.chmod(installer_file, 0o755)
            prefix = ['sudo']
        print('------------------------------------')
        print('Running the Matlab installer now.')
        print('This could take some time (15-30min)')
        print('------------------------------------')
        proc = subprocess.run(prefix + [installer_file, '-mode', 'silent', '-agreeToLicense', 'yes'],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stderr)
            raise RuntimeError('Could not install the Matlab MCR')
        print(proc.stdout.decode())
