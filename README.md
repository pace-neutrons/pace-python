# PACE-neutrons

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


## Getting Started

You can install and run the package using:

```
pip install pace_neutrons
pace_neutrons
```

When you first run `pace_neutrons` the module will check to see if you have the
[Matlab Compiler Runtime (MCR)](https://www.mathworks.com/products/compiler/matlab-runtime.html) installed.
If you do not have the version required by PACE (currently R2020a)
then the program will prompt you to accept the Matlab license and
it will download and install the required MCR components
(approximately 500MB download, 2GB installed).
Note that the installation is silent and may take some time to download and install (~15-30min).
You can also manually install the MCR at the above link,
but note that the distributions linked there is for the full Matlab installation including all toolboxes,
which is approximately 2.5GB to download and 15GB installed.

After installing the MCR, the program will start a Python command line.
To use PACE you must first import and initialise the `Matlab` module as follows:

```python
from pace_neutrons import Matlab
m = Matlab()
```

Thereafter, you can use the Matlab-based commands of Horace or SpinW by prefixing them with `m.`, e.g.:

```python
proj = m.projaxes([-0.5, 1, 0], [0, 0, 1], 'type', 'rrr')
w1 = m.cut_sqw('ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.4, 0.5], [3, 0.5, 20])
hf = m.plot(w1)
```

You can get further help from the [Horace](https://horace.isis.rl.ac.uk/) or [SpinW](https://spinw.org/) webpages.

Finally if you have Jupyter or Spyder installed you can start a PACE session in either with:

```
pace_neutrons --jupyter
```

or 

```
pace_neutrons --spyder
```

## Developer notes

Developer documentation is [here](docs/developers.md)
