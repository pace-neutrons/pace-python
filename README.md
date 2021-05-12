# PACE-python

PACE is a suite of programs for data analysis of inelastic neutron scattering spectra, written in both Python and Matlab.

The packages included in PACE are:

* [Horace](https://github.com/pace-neutrons/Horace/) - 
  A Matlab program for the visualisation and analysis of large datasets from time-of-flight neutron inelastic scattering spectrometers.
* [Euphonic](https://github.com/pace-neutrons/euphonic) - 
  A Python program for simulating phonon spectra from DFT output (CASTEP or Phonopy).
* [Brille](https://github.com/brille/brille) - A C++/Python program for Brillouin zone interpolation.
* [SpinW](https://github.com/spinw/spinw) - A Matlab program for simulating spin wave (magnon) spectra.

The Python programs have separate PyPI packages 
([Euphonic](https://pypi.org/project/euphonic/) and [Brille](https://pypi.org/project/brille/)),
whilst this package provides a Python module for the Matlab codes using a compiled Matlab library, which does not require a Matlab license.


## Install

`pace_python` is still alpha-software so you need to build it yourself:

```
git clone https://github.com/pace-neutrons/pace-python
cd pace-python
python setup.py install --user
```

The build will download the necessary Matlab packages (i.e. Horace and SpinW) and compile them.
So, you will need a Matlab installation with the Matlab Compiler SDK toolbox installed.
In addition, you will need `cmake`, and a Matlab supported C compiler for your OS
(generally `gcc-6`, `Visual Studio 2017` or `xcode-10.13` or newer).

Note that Matlab only supports [certain Python versions](https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/support/sysreq/files/python-compatibility.pdf). 
In particular, no Matlab versions supports Python 3.9, and only Matlab R2020b and newer supports Python 3.8.

The build will install `pace_python` as a module which can be imported.


### Windows specific build notes.

For `cmake` to work, you need to have Visual Studio on the path.
You can either start `cmd` or PowerShell from the `Tools->Command Line` menu.
Or, if you're just running `cmd` straight you need to execute the `vcvarsall.bat` script first.
If you're using PowerShell straight or `git bash` you need to somehow import this environment first.
For Powershell, the [`Invoke-Environment`](https://raw.githubusercontent.com/majkinetor/posh/master/MM_Admin/Invoke-Environment.ps1) script could be used.
For `git bash` a similar [script](https://gist.github.com/kalj/1c85df4a9ba2f6de78f3bcce658f329c) is available.
Finally, you can also start a `cmd` shell, run `vcvarsall.bat` and then start a PowerShell or `git bash`.

If you have [chocolatey](https://chocolatey.org/) installed, you can install all the dependencies to build `pace_python` with:

```
choco install -y cmake --installargs 'ADD_CMAKE_TO_PATH=System'
choco install -y visualstudio2019community --package-parameters "--includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop
choco install -y miniconda git
Invoke-WebRequest -Uri https://raw.githubusercontent.com/majkinetor/posh/master/MM_Admin/Invoke-Environment.ps1 -OutFile C:\windows\system32\Invoke-Environment.psm1
```

when run in an Adminstrator PowerShell.
Then you can clone and build `pace_python` (in a separate user PowerShell) with:

```
Invoke-Environment "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
git clone https://github.com/pace-neutrons/pace-python
cd pace-python
& "C:\tools\miniconda3\shell\condabin\conda-hook.ps1"
conda create -n pace python=3.7
conda activate pace
python setup.py install --user
```

## Usage

In order to run the compiled module you either need a full Matlab installation with the Compiler SDK toolbox,
or, if you have compiled it and distributed it to others, a
[Matlab Compiler Runtime](https://uk.mathworks.com/products/compiler/matlab-runtime.html) of the same version as was used to compile it.

Examples scripts are in the `examples` folder.
A simple usage is:

```python
from pace_python import Matlab
m = Matlab()

proj = m.projaxes([-0.5, 1, 0], [0, 0, 1], 'type', 'rrr')
w1 = m.cut_sqw('ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.4, 0.5], [3, 0.5, 20])
hf = m.plot(w1)
```

The commands should follow the Matlab syntax for Horace/SpinW.

Before running Python, you may need to set up the paths, as described in this 
[document](https://uk.mathworks.com/help/compiler/mcr-path-settings-for-run-time-deployment.html).


## Pull requests are welcome!  
