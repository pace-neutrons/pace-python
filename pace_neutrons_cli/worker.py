import sys, os, re
import platform
import argparse
from .utils import DetectMatlab, get_runtime_version
from pace_neutrons.IPythonMagics import Redirection


class LogfileRedirection(Redirection):
    def __init__(self, logfile):
        self.target = sys.__stdout__.fileno()
        self.output = open(logfile, 'w')
        self.ip = None
        self.flush = lambda: self.output.flush()
        self.pre()

    def not_redirecting(self):
        return False

    def showtraceback(self):
        pass

    def close(self):
        self.post()
        self.output.close()
        self.output = None

    def __del__(self):
        if self.output is not None:
            self.close()


def _set_env(input_path=''):
    # If the environment variables are not set, we need to restart with execv
    DET = DetectMatlab(get_runtime_version())
    if DET.env_not_set():
        mlPath = DET.guess_path([input_path])
        if not mlPath:
            raise RuntimeError('Could not find Matlab MCR in known locations.\n' \
                               'Please rerun with the environment variable ' \
                               'PACE_MCR_DIR set to the MCR location.\n')
        DET.set_environment(mlPath)
        if DET.system != 'Windows':
            os.execv(sys.executable, [sys.executable]+sys.argv)

def _get_args():
    parser = argparse.ArgumentParser(description='A wrapper script to run a PACE parallel worker')
    parser.add_argument('-logfile', help='Logfile output')
    parser.add_argument('-r', metavar='CMD', help='Runs a command interactively')
    parser.add_argument('-batch', metavar='CMD', help='Runs a command non-interactively')
    parser.add_argument('-nosplash', action='store_true', help='Do not show splash screen')
    parser.add_argument('-nojvm', action='store_true', help='Do not start JVM')
    parser.add_argument('-nodesktop', action='store_true', help='Do not start desktop')
    parser.add_argument('ctrl_str', metavar='C', nargs='*', default='', help='Worker control string')
    return parser

def _parse_control_string(cs):
    if isinstance(cs, list):
        cs = ' '.join(cs)
    if "('" in cs and "')" in cs:
        match = re.match("[\w\d]*\('([\w\d\-]*)'\).*", cs)
        if match:
            return match.group(1)
    return cs

def main(args=None):
    is_windows = platform.system() == 'Windows'
    args = _get_args().parse_args(args if args else sys.argv[1:])
    # Run set env first before any more imports because we might need to restart the process
    mlPath = os.environ['PACE_MCR_DIR'] if 'PACE_MCR_DIR' in os.environ else ''
    _set_env(mlPath)
    cs = _parse_control_string(args.ctrl_str)
    if args.ctrl_str == '':
        if args.batch is not None:
            cs = _parse_control_string(args.batch)
        elif args.r is not None:
            cs = _parse_control_string(args.r)
    if args.logfile is not None:
        logs = LogfileRedirection(args.logfile)
        sys.stdout = logs.output
    else:
        # Python stdout not compatible with Matlab C descriptor
        # So if we're not logging, then just redirect to /dev/null
        logs = LogfileRedirection(os.devnull)
        sys.stdout = logs.output
    import pace_neutrons.Matlab
    m = pace_neutrons.Matlab()
    m.worker_v2(cs)
    if args.logfile is not None:
        logs.close()
