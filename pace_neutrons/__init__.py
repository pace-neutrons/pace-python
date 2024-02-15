from __future__ import annotations

import os
import sys
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
    _VERSION_DIR = next(Path("../build").glob("lib.*")) / "pace_neutrons" / "ctfs"

_VERSIONS = []

for file in _VERSION_DIR.iterdir():
    if file.is_file() and file.suffix == ".ctf":
        _VERSIONS.append({'file': file.resolve(),
                          'version': file.name.split('.')[0].split('_')[1]})

_CALLPYTHON = None

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

        initialized = False
        if matlab_version is None:
            for version in _VERSIONS:
                if initialized:
                    break
                try:
                    print(f"Trying MATLAB version: {version['version']} ({version['file']}))")
                    super().__init__(version['file'], mlPath=matlab_path)
                    initialized = True
                except RuntimeError:
                    continue
        else:
            ctf = [version['file'] for version in _VERSIONS
                    if version['version'].lower() == matlab_version.lower()]
            if len(ctf) == 0:
                raise RuntimeError(
                    f"Compiled library for MATLAB version {matlab_version} not found. Please use: [{', '.join([version['version'] for version in _VERSIONS])}]\n ")
            else:
                ctf = ctf[0]
            try:
                super().__init__(ctf, mlPath=matlab_path)
                initialized = True
            except RuntimeError:
                pass
        if not initialized:
            raise RuntimeError(
                f"No MATLAB versions found. Please use: [{', '.join([version['version'] for version in _VERSIONS])}]\n "
                f"If installed, please specify the root directory (`matlab_path` and `matlab_version`) of the MATLAB "
                f"installation.")
        else:
            self._interface.call('pyhorace_init', nargout=0)
