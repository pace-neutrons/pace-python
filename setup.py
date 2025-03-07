import os
import re
import sys
import glob
import subprocess
import pkgutil
import shutil
import versioneer
from sysconfig import get_platform
from subprocess import CalledProcessError, check_output, check_call, run, PIPE
from distutils.version import LooseVersion
from setuptools import setup, Extension, find_packages

CURRDIR = os.path.dirname(__file__)

# We can use cmake provided from pip which (normally) gets installed at /bin
# Except that in the manylinux builds it's placed at /opt/python/[version]/bin/
# (as a symlink at least) which is *not* on the path.
# If cmake is a known module, import it and use it tell us its binary directory
if pkgutil.find_loader('cmake') is not None:
    import cmake
    CMAKE_BIN = cmake.CMAKE_BIN_DIR + os.path.sep + 'cmake'
else:
    CMAKE_BIN = 'cmake'

def get_cmake():
    return CMAKE_BIN


def is_vsc():
    platform = get_platform()
    return platform.startswith("win")


def is_mingw():
    platform = get_platform()
    return platform.startswith("mingw")


def update_euphonic_sqw_models():
    # Calls git to update euphonic_sqw_models submodule
    try:
        cmk_out = run([get_cmake(), '.'], cwd=os.path.join('cmake', 'print_git'),
                      stdout=PIPE, stderr=PIPE, check=True)
    except OSError:
        raise RuntimeError("CMake must be installed to build this extension")
    if "Git Not Found" in cmk_out.stderr.decode():
        raise RuntimeError("Git must be installed to build this extension")
    git_bin = cmk_out.stderr.decode().split('Git Found: ')[1].split('\n')[0]
    git_out = run([git_bin, 'submodule', 'update', '--init', 'euphonic_sqw_models_module'])
    git_out.check_returncode()


def copy_euphonic_sqw_models():
    # Copies the euphonic_sqw_models module folder to the top level folder
    #
    # In order for setuptools to pick up euphonic_sqw_models, the Python
    # module folder must be exist in the top level folder when it runs
    if not os.path.isdir(os.path.join(CURRDIR, 'euphonic_sqw_models_module', 'euphonic_sqw_models')):
        update_euphonic_sqw_models()
    shutil.copytree(os.path.join(CURRDIR, 'euphonic_sqw_models_module', 'euphonic_sqw_models'),
                    os.path.join(CURRDIR, 'euphonic_sqw_models'))


if not os.path.isfile(os.path.join(CURRDIR, 'euphonic_sqw_models', '__init__.py')):
    copy_euphonic_sqw_models()


#Removes additional args for cmake options to avoid issue with setuptools
if len(sys.argv)>2:
    sys.argv, extra_args = sys.argv[:2], sys.argv[2:]
else:
    extra_args = []


if not os.path.isdir(os.path.join(CURRDIR, 'pace_neutrons', 'ctfs')):
    try:
        import libpymcr
    except ModuleNotFoundError:
        pip_out = run([sys.executable, '-m', 'pip', 'install', 'libpymcr>=0.2.1'])
    try:
        out = check_output([get_cmake(), '--version'])
    except OSError:
        raise RuntimeError("CMake must be installed to build this module")
    rex = r'version\s*([\d.]+)'
    cmake_version = LooseVersion(re.search(rex, out.decode()).group(1))
    if cmake_version < '3.15.0':
        raise RuntimeError("CMake >= 3.15.0 is required")

    if not os.path.isfile(os.path.join('euphonic_sqw_models', '__init__.py')):
        copy_euphonic_sqw_models()

    extdir = os.path.join(CURRDIR, 'extdir')
    cmake_args = []
    if is_vsc():
        if sys.maxsize > 2**32:
            cmake_args += ['-A', 'x64']
        else:
            cmake_args += ['-A', 'Win32']

    if is_mingw():
        cmake_args += ['-G','Unix Makefiles'] # Must be two entries to work

    cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                   '-DPYTHON_EXECUTABLE=' + sys.executable]

    cfg = 'Release'
    #cfg = 'Debug' if self.debug else 'RelWithDebInfo'
    build_args = ['--config', cfg]

    # make sure all library files end up in one place
    cmake_args += ["-DCMAKE_BUILD_WITH_INSTALL_RPATH=TRUE"]
    cmake_args += ["-DCMAKE_INSTALL_RPATH={}".format("$ORIGIN")]

    if is_vsc():
        cmake_lib_out_dir = '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'
        cmake_args += [cmake_lib_out_dir.format(cfg.upper(), extdir)]
        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
        build_args += ['--', '/m:4']
    else:
        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
        build_args += ['--', '-j']

    env = os.environ.copy()
    cxxflags = f'{env.get("CXXFLAGS", "")} -DVERSION_INFO=\\"{versioneer.get_version()}\\"'
    env['CXXFLAGS'] = cxxflags

    cmake_args += extra_args
    print(cmake_args)
    # exit()

    if 'MATLAB_DIR' in env:
        cmake_args += ['-DMatlab_ROOT_DIR=' + env['MATLAB_DIR']]

    build_temp = os.path.join(CURRDIR, 'buildtmp')
    if not os.path.exists(build_temp):
        os.makedirs(build_temp)
    check_call([get_cmake(), CURRDIR] + cmake_args, cwd=build_temp, env=env)
    # Only build call_python - use mcc_all.py to build CTFs
    check_call([get_cmake(), '--build', '.', '--target', 'call_python', 'spinw', 'patch_ctf', 'copy_mex'] + build_args, cwd=build_temp)
    # Call mcc_all.py to build all CTFs
    check_call([sys.executable, 'mcc_all.py', build_temp], cwd=CURRDIR)
    # Copy the zip (separated compiled m and mex files) to the main distribution folder
    destination = os.path.join('pace_neutrons', 'ctfs')
    if not os.path.exists(destination):
        os.makedirs(destination)
    for file in glob.glob(os.path.join('ctfs', '*xz')):
        shutil.copy(file, destination)


with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()


KEYWORDARGS = dict(
    name='pace_neutrons',
    version=versioneer.get_version(),
    author='Duc Le',
    author_email='duc.le@stfc.ac.uk',
    description='A Python wrapper around Matlab programs for inelastic neutron scattering data analysis',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=['pace_neutrons', 'pace_neutrons_cli', 'euphonic_sqw_models'],
    package_data={'pace_neutrons': ['ctfs/*ctf', 'ctfs/*xz', 'MCR_license.txt']},
    install_requires = ['six>=1.12.0', 'numpy>=1.7.1', 'appdirs>=1.4.4', 'ipython>=3.2.1', 'requests', 'psutil>=0.6.0',
                        'matplotlib>=2.0.0', 'euphonic[phonopy_reader]>=1.3.1', 'libpymcr>=0.2.0'], # 'brille>=0.5.4',
    extras_require = {'interactive':['matplotlib>=2.2.0',],},
    cmdclass=versioneer.get_cmdclass(),
    entry_points={'console_scripts': [
        'pace_neutrons = pace_neutrons_cli:main',
        'worker_v4 = pace_neutrons_cli.worker:main']},
    url="https://github.com/pace-neutrons/pace-python",
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ]
)

try:
    setup(**KEYWORDARGS)
except CalledProcessError:
    print("Failed to build the extension!")
