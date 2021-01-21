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
cmake .
cmake --build .
```

The build will download the necessary Matlab packages and compile them.
So, you will need a Matlab installation with the Matlab Compiler SDK toolbox installed.
In addition, you will need `cmake`, and a Matlab supported C compiler for your OS
(generally `gcc-6`, `Visual Studio 2017` or `xcode-10.13` or newer).

The build will create a `bin` folder with the `pace_python` module inside.
(You can also build it in a separate folder, with `mkdir pp_build && cd pp_build && cmake ../pace-python && cmake --build .`).
You should then add this bin folder to your python path:

```python
import sys
sys.path.append('/path/to/bin')
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
