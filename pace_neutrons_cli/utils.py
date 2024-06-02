import os
import sys
import glob
import platform
from http import HTTPStatus


OS = platform.system()
OSTYPE = {'Windows': 'win64', 'Linux': 'glnxa64', 'Darwin': 'maci64'}
PATHVAR = {'Windows': 'PATH', 'Linux': 'LD_LIBRARY_PATH', 'Darwin': 'DYLD_LIBRARY_PATH'}


def get_mlpath():
    if 'PACE_MCR_DIR' in os.environ:
        return os.environ['PACE_MCR_DIR']
    import pace_neutrons, libpymcr
    if pace_neutrons.INITIALIZED:
        with pace_neutrons.nostdout():
            ver = pace_neutrons.VERSION
            mlPath = libpymcr.utils.checkPath(ver)
    else:
        mcr_found = False
        for version in pace_neutrons._VERSIONS:
            ver = version['version']
            with pace_neutrons.nostdout():
                mlPath = libpymcr.utils.checkPath(ver, error_if_not_found=False)
            if mlPath is not None:
                break
    if mlPath is None:
        raise RuntimeError('Could not find Matlab MCR in known locations.\n' \
                           'Please rerun with the environment variable ' \
                           'PACE_MCR_DIR set to the MCR location.\n')
    return mlPath, ver


def set_env():
    # If the environment variables are not set, we need to restart with execv
    if PATHVAR[OS] in os.environ and OSTYPE[OS] in os.environ[PATHVAR[OS]]:
        return
    mlPath, mlver = get_mlpath()
    os.environ['PACE_MCR_VERSION'] = mlver
    ldpath = os.path.join(mlPath, 'bin', OSTYPE[OS])
    if PATHVAR[OS] not in os.environ:
        os.environ[PATHVAR[OS]] = ldpath
    elif mlPath not in os.environ[PATHVAR[OS]]:
        os.environ[PATHVAR[OS]] = os.environ[PATHVAR[OS]] + os.pathsep + ldpath
    if OS != 'Windows':
        os.execv(sys.executable, [sys.executable]+sys.argv)


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
        if not any(dir for dir in cached if val in dir):
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


def release_exists(tag_name, retval='upload_url', use_auth=True):
    import requests, json, re
    headers = {}
    if use_auth:
        headers = {"Authorization": "token " + os.environ["GITHUB_TOKEN"]}
    response = requests.get(
        'https://api.github.com/repos/pace-neutrons/pace-python/releases',
        headers=headers)
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f'Could not query Github if release exists: \n {response.text}')
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
        raise RuntimeError('Could not query Github for list of assets: \n {response.text}')
    response = json.loads(response.text)
    INSTALLERS = {'Windows': 'pace_neutrons_installer_win32.exe', 'Linux': 'pace_neutrons_installer_linux.install'}
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
