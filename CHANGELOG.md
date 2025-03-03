# [v0.4.0](https://github.com/pace-neutrons/pace-python/compare/v0.3.0a0...v0.4.0)

Updated to Horace 4.0.0

* New features
  - Updated to use libpymcr [v0.2.1](https://github.com/pace-neutrons/libpymcr/releases/tag/v0.2.1)
  - Features from that include: specifying function handle using the `@` operator, 
    use of `Ctrl+C` to interrrupt Matlab execution, better formatting of Matlab output

* Bugfixes
  - Now have `ctf` for Matlab R2021b to R2024b included in distribution.
  - Support for Python 3.13 added, support for Python 3.7 dropped.


# [v0.3.0a1](https://github.com/pace-neutrons/pace-python/compare/v0.2.0...v0.3.0a0)

* New features
  - Add ability to use existing Horace/SpinW rather than downloading
  - Check included to test provided Horace/SpinW path
  - Add option to exclude Horace/SpinW from build
  - Add option to set version/release to download
  - Version checking for both Horace and SpinW included
  - Inclusion of libpymcr enabling use of previously incompatible Matlab and Python versions
  - IPythonMagics module moved to [libpymcr](https://pypi.org/project/libpymcr/).

* For developers (CI changes)
  - Update to use PACE-shared-lib
  - Add parametrised pipeline
  - Update for use with rocky8 and icdpacewin
  - Use conda environments throughout
  - Remove podman usage
  - Introduce seperate build installer stage
  - Remove reliance on external powershell and bash scripts

* Notes
  - Brille test currently disabled (see #28)

# [v0.2.0](https://github.com/pace-neutrons/pace-python/compare/v0.1.4...v0.2.0)

Updated to Horace 3.6.2

* New features
  - Add support for Horace parallel framework. Use `m.hpc('on')` to activate and then set the cluster type `m.hpc_config().parallel_cluster = <x>` where `<x> = 'parpool'`, `'herbert'` or `'mpiexec_mpi'`.

* Bugfixes
  - Fix bug where Matlab `+namespaces` were not accessible in Python
  - Several small bugs when using with Spyder.

# [v0.1.4](https://github.com/pace-neutrons/pace-python/compare/v0.1.3...v0.1.4)

* New features
  - New `pace_neutrons` wrapper script to launch PACE, setting all needed paths
  - Can also launch jupyter or spyder with `pace_neutrons --spyder` or `pace_neutrons --jupyter`
  - Facility to download and install MCR automatically or on first use

* Bugfixes
  - If neither spyder or jupyter installed will use IPython (now a dependency)
  - Fix logic error in searching for MCR runtime DLL. Will use registry on Windows.

# [v0.1.3](https://github.com/pace-neutrons/pace-python/compare/v0.1.1...v0.1.3)

Updated to Horace 3.6.1.

* Bugfixes
  - Fix MatlabProxyObject `__setattr__` - can now do e.g. `h = m.herbert_config(); h.use_mex = True`
  - Fix `worker_v2 not found in initialisation` error
  - Fix DataTypes.py encoding list recursion.

# [v0.1.1](https://github.com/pace-neutrons/pace-python/compare/v0.1.0...v0.1.1)

## Initial public beta version of pace_python.

Please download the `pace_python_matlab_installer` file for your OS and run it. This will install the Matlab Runtime and a GUI installer app. Run the installer app (`pace_python_installer`) which will install miniconda and the `pace_python` module (if you have an existing Python installation you wish to use, select `Custom Installation` in the app).

If you select `Jupyter` and/or `Spyder` (both recommended) in the `Default Installation` option, then after the installation finishes, you will see links to Jupyter and Spyder in your start menu (on Windows) which you can use to start Jupyter/Spyder with pace-python. Then run:

```
import pace_python
m = pace_python.Matlab()
m.horace()
```

To start the Horace GUI.

If you have any problems, please create an issue on this repository.
