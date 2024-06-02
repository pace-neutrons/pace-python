import sys, os, re
import argparse
from .utils import set_env

def _get_args():
    parser = argparse.ArgumentParser(description='A wrapper script to run a PACE parallel worker')
    parser.add_argument('-logfile', help='Logfile output')
    parser.add_argument('-r', metavar='CMD', help='Runs a command interactively')
    parser.add_argument('-batch', metavar='CMD', help='Runs a command non-interactively')
    parser.add_argument('-nosplash', action='store_true', help='Do not show splash screen')
    parser.add_argument('-nojvm', action='store_true', help='Do not start JVM')
    parser.add_argument('-nodesktop', action='store_true', help='Do not start desktop')
    parser.add_argument('-softwareopengl', action='store_true', help='Use software OpenGL')
    parser.add_argument('ctrl_str', metavar='C', nargs='*', default='', help='Worker control string')
    return parser

def _parse_control_string(cs):
    if isinstance(cs, list):
        cs = ' '.join(cs)
    if "('" in cs and "')" in cs:
        match = re.match("[\w\d\.\\\/:]*\('([\w\d\-]*)'\).*", cs)
        if match:
            return match.group(1)
    if '/' in cs or '\\' in cs:
        cs = ''
    return cs

def main(args=None):
    args = _get_args().parse_args(args if args else sys.argv[1:])
    # Run set env first before any more imports because we might need to restart the process
    set_env()
    cs = _parse_control_string(args.ctrl_str)
    if args.ctrl_str == '':
        if args.batch is not None:
            cs = _parse_control_string(args.batch)
        elif args.r is not None:
            cs = _parse_control_string(args.r)
    import pace_neutrons
    if args.logfile is not None:
        logs = open(args.logfile, 'w')
    else:
        # Python stdout not compatible with Matlab C descriptor
        # So if we're not logging, then just redirect to /dev/null
        logs = pace_neutrons._DummyFile()
    sys.stdout = logs
    if 'PACE_MCR_VERSION' in os.environ:
        m = pace_neutrons.Matlab(matlab_version=os.environ['PACE_MCR_VERSION'])
    else:
        m = pace_neutrons.Matlab()
    m.worker_v4(cs)
    logs.close()
