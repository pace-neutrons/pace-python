import sys, os
import platform
from .utils import DetectMatlab, get_runtime_version, PaceConfiguration, get_mantid
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
    

def _check_matlab_installed(input_path=None):
    cf = PaceConfiguration()
    from pace_neutrons import _VERSIONS
    from libpymcr.utils import DetectMatlab, get_version_from_ctf
    guess_path = [input_path] if input_path else []
    if not IS_WINDOWS:
        guess_path += ['/usr/local']
    for vers in _VERSIONS:
        dm = DetectMatlab(get_version_from_ctf(vers['file']))
        if mlPath := dm.guess_path(guess_path):
            cf.CachedCTFs = vers['file']
            cf.CachedMatlabDirs = mlPath
            cf.save()
            break
    if mlPath is None:
        if cf.IsFirstRun:
            from pace_neutrons_cli.utils import install_MCR
            print(('This is the first time PACE has been run, '
                   'and we could not find a suitable Matlab Compiler Runtime (MCR) installed.'))
            mlPath = install_MCR(interactive=True)
            cf.IsFirstRun = False
            cf.save()
        else:
            raise RuntimeError('Could not find Matlab MCR in known locations.\n'
                               'Please rerun with the option --matlab-dir to the MCR location.\n'
                               'This location will be cached for future lookup.\n'
                               'Alternatively, you can rerun with the --install-mcr option to install '
                               'the compiler runtime.\n'
                               'This takes approximately 15-30min and will be silent\n')
    if cf.IsFirstRun:
        cf.IsFirstRun = False
        cf.save()
    if input_path and input_path in mlPath:
        cf.CachedMatlabDirs = mlPath
        cf.save()


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
        from pace_neutrons_cli.utils import install_MCR
        install_MCR(interactive=False)
    # Need to set the Qt library folder first if we're using Spyder,
    # or get conflict with bundled Matlab libraries on Linux
    force_reload = False
    if (args.spyder or args.mantid) and not IS_WINDOWS:
        force_reload = _prepend_QT_libs()
    # Check that either Matlab or the MCR is installed
    _check_matlab_installed(args.matlab_dir)
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
