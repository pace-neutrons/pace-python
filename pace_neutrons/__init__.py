from __future__ import annotations

from . import _version
__version__ = _version.get_versions()['version']

import os
import sys
import libpymcr

from . import FunctionWrapper

# Generate a list of all the MATLAB versions available
_VERSION_DIR = os.path.join(os.path.dirname(__file__), 'ctfs')
_VERSIONS = []
for file in os.scandir(_VERSION_DIR):
    if file.is_file() and file.name.endswith('.ctf'):
        _VERSIONS.append({'file':    os.path.join(_VERSION_DIR, file.name),
                          'version': file.name.split('.')[0].split('_')[1]
                          })

_CALLPYTHON = None

class Matlab(libpymcr.Matlab):
    def __init__(self, matlab_path: Optional[str] = None, matlab_version: Optional[str] = None):
        """
        Create a MATLAB instance with the correct compiled library for the MATLAB version specified. If no version is
        specified, the first version found will be used. If no MATLAB versions are found, a RuntimeError will be
        raised. If a version is specified, but not found, a RuntimeError will be raised.

        :param matlab_path: Path to the root directory of the MATLAB installation or MCR installation.
        :param matlab_version: Used to specify the version of MATLAB if the matlab_path is given or if there is more
        than 1 MATLAB installation.
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
            ctf = [version['file'] for version in _VERSIONS if version['version'].lower() == matlab_version.lower()]
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
            if _CALLPYTHON is None:
                _CALLPTYHON = CallPython()
            self._callpython = _CALLPYTHON


import socketserver, threading

class CallPythonHandler(socketserver.BaseRequestHandler):
    def setup(self):
        from libpymcr.Matlab import _global_matlab_ref
        from libpymcr import _globalFunctionDict
        if _global_matlab_ref is None:
            raise RuntimeError('This class must be constructed after Matlab has been initialised')
        self.interface = _global_matlab_ref.interface
        self.fundict = _globalFunctionDict

    def handle(self):
        data = self.request.recv(4096).decode()
        print(data)
        fun_name, idstr, haskw = data.split(',')
        print(self.fundict)
        #self.interface.call('evalin', 'base', 'whos', nargout=0)
        print(f'|{fun_name}|')
        try:
            #args = self.interface.call('evalin', 'base', f'{idstr}_inp', nargout=1)
            #args = self.interface.getvar(f'{idstr}_inp')
            self.interface.getvar(f'{idstr}_inp')
            #print(args)
            #if haskw:
            #    #kwargs = self.interface.call('evalin', 'base', f'{idstr}_kw', nargout=1)
            #    kwargs = self.interface.getvar(f'{idstr}_kw')
            #    print(kwargs)
            #    out = self.fundict[fun_name](*args, **kwargs)
            #else:
            #    out = self.fundict[fun_name](*args)
            out = ('hello')
            print(out)
            #self.interface.call('assignin', 'base', f'{idstr}_out', out, nargout=0)
            pstat = self.interface.putvar(f'{idstr}_out', out)
            print(f'pstat = {pstat}')
        except Exception as e:
            self.request.sendall(e.message.encode())
        else:
            self.request.sendall(b'Call completed')


class CallPython:
    thread = None
    server = None

    def __init__(self):
        def serverlisten():
            if self.server is None:
                self.server = socketserver.TCPServer(('localhost', 19999), CallPythonHandler)
            self.server.serve_forever()
        self.thread = threading.Thread(target=serverlisten)
        self.thread.daemon = True
        self.thread.start()

    def __del__(self):
        if self.thread is None:
            return
        if self.server is not None:
            self.server.server_close()
            self.server = None
        if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            self.thread.join()
        self.thread = None
