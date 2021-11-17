import os, sys
import platform
import six


def get_runtime_version():
    # Looks in the Matlab generated __init__ file to determine the required Matlab version
    with open(os.path.join(os.path.dirname(__file__), 'pace', '__init__.py'), 'r') as pace_init:
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
        if not isinstance(val, six.string_types):
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
        def check_lib_file(obj, ver, runtime_dir):
            arch = next(os.walk(runtime_dir))[1]
            if len(arch) == 1 and os.path.exists(os.path.join(runtime_dir, arch[0], self.file_to_find)):
                self.ver, self.arch = (ver, arch[0])
                rv = os.path.dirname(runtime_dir)
                print(f'Found Matlab {ver} {self.arch} at {rv}')
                return rv
            return None
        root_dir = os.path.abspath(root_dir)
        if os.path.basename(root_dir) == 'runtime':
            rv = check_lib_file(self, self.ver, root_dir)
            if rv: return rv
        sub_dirs = next(os.walk(root_dir))[1]
        for sub_dir in sub_dirs:
            # We use the highest version
            if sub_dir == 'runtime':
                rv = check_lib_file(self, self.ver, os.path.join(root_dir, sub_dir))
                if rv: return rv
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


def release_exists(tag_name, retval='upload_url'):
    import requests
    response = requests.get(
        'https://api.github.com/repos/pace-neutrons/pace-python/releases',
        headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"]})
    if response.status_code != 200:
        raise RuntimeError('Could not query Github if release exists')
    response = json.loads(response.text)
    desired_release = [v for v in response if v['tag_name'] == tag_name]
    if desired_release:
        upload_url = re.search('^(.*)\{\?', desired_release['upload_url']).groups()[0]
        return desired_release[retval]
    else:
        return False


def download_github(url, local_filename=None):
    import requests
    if not local_filename:
        local_filename = url.split('/')[-1]
    with requests.get(url, stream=True,
                      headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"],
                               "Accept":"application/octet-stream"}) as r:
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def install_MCR():
    """
    Downloads an installer from github which would install the required MCR components only
    This relies on there being the correct version of the installer available
    """
    import requests, tempfile, subprocess
    from pace_neutrons import __version__
    assets_url = release_exists('v' + __version__, retval='assets_url')
    if not assets_url:
        raise RuntimeError(f'No Github release exists for pace_neutrons version {__version__}')
    response = requests.get(assets_url, headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"]})
    if response.status_code != 200:
        raise RuntimeError('Could not query Github for list of assets')
    response = json.loads(response.text)
    INSTALLERS = {'Windows':'pace_neutrons_installer_win32.exe', 'Linux':'pace_neutron_installer_linux.install'}
    system = platform.system()
    try:
        installer_name = INSTALLERS[system]
    except KeyError:
        raise RuntimeError(f'No installer exists for OS: {system}')
    installer_url = [a['url'] for a in response if a == installer_name][0]
    with tempfile.TemporaryDirectory() as dd:
        installer_file = os.path.join(dd, installer_name)
        download_github(url, local_filename=installer_file)
        pr = subprocess.Popen([installer_file, '-mode', 'silent', '-agreeToLicense', 'yes'],
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(pr)
