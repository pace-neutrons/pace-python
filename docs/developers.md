# Developer Notes

Note that although the package has been renamed `pace_neutrons`, the repo is still `pace-python`(!)


## Pushing a release

Releases can be made by first editing/updating the `CHANGELOG.md` and `CITATION.cff` files,
and then tagging and pushing to github:

```
git tag vX.Y.Z
git push origin vX.Y.Z
```

This will trigger a Jenkins job which will build and test the code,
create a draft release on github and upload the binary wheels.

Once all the wheels for the different OS are uploaded, 
you can manually trigger a github actions job to push the wheels to PyPI.


## Building from Source

```
git clone https://github.com/pace-neutrons/pace-python
cd pace-python
python setup.py install --user
```

The build will download the necessary Matlab packages (i.e. Horace and SpinW) and compile them.
You will need a Matlab installation with the Matlab Compiler SDK toolbox installed.
The Parallel Computation toolbox is also needed if you want build with Horace with `parpool` parallelisation.
If you don't need this, also comment ou the relevant number in
[make_package.m](https://github.com/pace-neutrons/pace-python/blob/main/installer/make_package.m#L13).
In addition, you will need `cmake`, and a Matlab supported C compiler for your OS
(generally `gcc-6`, `Visual Studio 2017` or `xcode-10.13` or newer).

Note that Matlab only supports [certain Python versions](https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/support/sysreq/files/python-compatibility.pdf). 
In particular, no Matlab versions supports Python 3.10 or higher, and only Matlab R2020b and newer supports Python 3.8.

The build will install `pace_neutrons` as a module which can be imported.


### Windows specific build notes.

For `cmake` to work, you need to have Visual Studio on the path.
You can either start `cmd` or PowerShell from the `Tools->Command Line` menu.
Or, if you're just running `cmd` straight you need to execute the `vcvarsall.bat` script first.
If you're using PowerShell straight or `git bash` you need to somehow import this environment first.
For PowerShell, the [`Invoke-Environment`](https://raw.githubusercontent.com/majkinetor/posh/master/MM_Admin/Invoke-Environment.ps1) script could be used.
For `git bash` a similar [script](https://gist.github.com/kalj/1c85df4a9ba2f6de78f3bcce658f329c) is available.
Finally, you can also start a `cmd` shell, run `vcvarsall.bat` and then start a PowerShell or `git bash`.

If you have [chocolatey](https://chocolatey.org/) installed, you can install all the dependencies to build `pace_neutrons` with:

```
choco install -y cmake --installargs 'ADD_CMAKE_TO_PATH=System'
choco install -y visualstudio2019community --package-parameters "--includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop"
choco install -y miniconda git
Invoke-WebRequest -Uri https://raw.githubusercontent.com/majkinetor/posh/master/MM_Admin/Invoke-Environment.ps1 -OutFile C:\windows\system32\Invoke-Environment.psm1
```

when run in an Adminstrator PowerShell.
Then you can clone and build `pace_neutrons` (in a separate user PowerShell) with:

```
Invoke-Environment "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
git clone https://github.com/pace-neutrons/pace-python
cd pace-python
& "C:\tools\miniconda3\shell\condabin\conda-hook.ps1"
conda create -n pace python=3.7
conda activate pace
python setup.py install --user
```
