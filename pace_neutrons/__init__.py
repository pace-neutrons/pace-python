from __future__ import annotations

import os
import sys
import contextlib
from pathlib import Path
from typing import Optional
import libpymcr


from . import _version
__version__ = _version.get_versions()['version']

from . import FunctionWrapper

# Generate a list of all the MATLAB versions available
_VERSION_DIR = Path(__file__).parent / "ctfs"

#check if the directory exists and adjust as needed
#accounts for different dir when calling regularly and during release stages of CI
if not _VERSION_DIR.is_dir():
    _VERSION_DIR = next(Path("./build").glob("lib.*")) / "pace_neutrons" / "ctfs"

def _getFiles(folder, test):
    return [{'file': file.resolve(), 'version': file.stem.split('_')[1]}
            for file in folder.iterdir() if test(file)]
_VERSIONS = _getFiles(_VERSION_DIR, lambda f: f.is_file() and f.suffix == ".ctf")
_NOMEXS = _getFiles(_VERSION_DIR, lambda f: f.is_file() and f.stem.startswith("nomex"))
_MATLABNOTFOUND_STR = f"No supported MATLAB versions [{', '.join(version['version'] for version in _NOMEXS)}] found.\n " \
    "If installed, please specify the root directory (`matlab_path` and `matlab_version`) of the MATLAB installation.\n " \
    "If not installed you can download the MCR from: https://uk.mathworks.com/products/compiler/matlab-runtime.html\n"
VERSION = ''
INITIALIZED = False


class _DummyFile(object):
    def write(self,x):
        pass
    def flush(self):
        pass


@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = _DummyFile()
    yield
    sys.stdout = save_stdout


def _initialize_compiled_worker(interface):
    import platform, shutil
    worker_path = os.path.join(os.path.dirname(sys.argv[0]), 'worker_v4')
    if platform.system() == 'Windows':
        worker_path += '.exe'
    if not os.path.exists(worker_path):
        worker_path = shutil.which('worker_v4')
    if worker_path:
        so0 = sys.stdout
        with nostdout():
            pc = interface.call('parallel_config', nargout=1)
            access = interface.call('substruct', '.', 'worker')
            interface.call('subsasgn', pc, access, worker_path)


def _checkML(versions):
    from libpymcr.utils import checkPath
    return [v for v in versions
            if checkPath(f'R{v["version"]}', error_if_not_found=False, suppress_output=True) is not None]


class Matlab(libpymcr.Matlab):

    def __init__(self, matlab_path: Optional[str] = None, matlab_version: Optional[str] = None):
        """
        Create a MATLAB instance with the correct compiled library for the MATLAB version specified.
        If no version is specified, the first version found will be used. If no MATLAB versions are 
        found, a RuntimeError will be raised. If a version is specified, but not found, a RuntimeError
        will be raised.

        :param matlab_path: Path to the root directory of the MATLAB installation or MCR installation.
        :param matlab_version: Used to specify the version of MATLAB if the matlab_path is given or if
        there is more than 1 MATLAB installation.
        """
        from libpymcr.utils import recombinemex
        global INITIALIZED
        global VERSION

        if INITIALIZED:
            super().__init__(VERSION, mlPath=matlab_path)
        elif matlab_version is None:
            avail_ML = _checkML(_VERSIONS)
            if avail_ML:
                super().__init__(avail_ML[0]['file'], mlPath=matlab_path)
            else:
                avail_ML = _checkML(_NOMEXS)
                if not avail_ML:
                    raise RuntimeError(_MATLABNOTFOUND_STR)
                for ver in avail_ML:
                    print(f'Please wait... creating pace CTF for Matlab R{ver["version"]}')
                    recombinemex(f'R{ver["version"]}', _VERSION_DIR)
                ctffile = _VERSION_DIR / f'pace_{avail_ML[0]["version"]}.ctf'
                super().__init__(ctffile.resolve(), mlPath=matlab_path)
        else:
            ctf = [v['file'] for v in _VERSIONS if v['version'].lower() == matlab_version.lower()]
            nmx = [v for v in _NOMEXS if v['version'].lower() == matlab_version.lower()]
            if not ctf and nmx:
                recombinemex(f'R{nmx[0]["version"]}', _VERSION_DIR)
                ctf = [(_VERSION_DIR / f'pace_{nmx[0]["version"]}.ctf').resolve()]
            if len(ctf) == 0:
                raise RuntimeError(
                    f"Compiled library for MATLAB version {matlab_version} not found. "
                    f"Please use: [{', '.join([version['version'] for version in _NOMEXS])}]\n ")
            else:
                ctf = ctf[0]
            super().__init__(ctf, mlPath=matlab_path)
        INITIALIZED = True
        self._interface.call('pyhorace_init', nargout=0)
        if 'worker' not in sys.argv[0]:
            _initialize_compiled_worker(self._interface)
