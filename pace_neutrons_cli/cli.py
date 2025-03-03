import sys, os
import platform
from .utils import set_env, get_mantid
import argparse

IS_WINDOWS = platform.system() == 'Windows'

def _prepend_QT_libs():
    import os
    # We only need to care about PyQt5 since Matlab only bundles Qt5,
    # and Spyder removed support for PySide2
    # Addendum: Spyder reinstated PySide2 support in Aug 2021,
    # https://github.com/spyder-ide/spyder/pull/16322
    # But current the pypi version still just use PyQt5
    try:
        import PyQt5
    except ImportError:
        pass
    else:
        libdir = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt', 'lib')
        if 'LD_LIBRARY_PATH' in os.environ:
            if libdir not in os.environ['LD_LIBRARY_PATH']:
                os.environ['LD_LIBRARY_PATH'] = libdir + ':' + os.environ['LD_LIBRARY_PATH']
                return True
        else:
            os.environ['LD_LIBRARY_PATH'] = libdir
            return True
    return False
    

def _get_args():
    parser = argparse.ArgumentParser(description='A wrapper script to run the PACE module')
    parser.add_argument('-d', '--matlab-dir', help='Directory where Matlab MCR is installed')
    parser.add_argument('-s', '--spyder', action='store_true', help='Runs under Spyder IDE')
    parser.add_argument('-j', '--jupyter', action='store_true', help='Runs in Jupyter notebook server')
    parser.add_argument('-m', '--mantid', action='store_true', help='Runs under Mantid Workbench')
    parser.add_argument('--mantid-nosad', action='store_true', help='Runs Mantid without error reporter')
    parser.add_argument('--install-mcr', action='store_true', help='Installs the Matlab MCR')
    return parser


def main(args=None):
    args = _get_args().parse_args(args if args else sys.argv[1:])
    if sum([args.spyder, args.jupyter, args.mantid]) > 1:
        raise RuntimeError('You can only specify one of --spyder, --jupyter or --mantid')
    if args.install_mcr:
        from .utils import install_MCR
        install_MCR(interactive=False)
    # Need to set the Qt library folder first if we're using Spyder,
    # or get conflict with bundled Matlab libraries on Linux
    if (args.spyder or args.mantid) and not IS_WINDOWS:
        _prepend_QT_libs()
    set_env()
    # Launches other environments if asked for
    if args.spyder:
        sys.argv = ['']
        try:
            import spyder.app.start
        except ImportError:
            raise RuntimeError('Spyder is not installed')
        else:
            print('Running Spyder')
            spyder.app.start.main()
    elif args.jupyter:
        sys.argv = ['']
        try:
            import notebook.notebookapp
        except ImportError:
            raise RuntimeError('Jupyter notebook is not installed')
        else:
            print('Running Jupyter-Notebook')
            notebook.notebookapp.main()
    elif args.mantid or args.mantid_nosad:
        mantid_dir = get_mantid()
        if not mantid_dir:
            raise RuntimeError('Cannot find Mantid or Mantid is not installed')
        for dirs in ['plugins', 'lib', 'bin']:
            sys.path.insert(0, os.path.join(mantid_dir, dirs))
        if args.mantid:
            import mantidqt.dialogs.errorreports.main
            sys.argv[1:] = ['--exitcode=0', '--application=workbench']
            mantidqt.dialogs.errorreports.main.main()
        else:
            import workbench.app.main
            sys.argv = ['']
            workbench.app.main.main()
    else:
        import IPython
        IPython.embed()
