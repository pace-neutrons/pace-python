# Pace-Neutrons: getting started
version: 0.3.0
## Introduction

Pace-Neutrons, previously known as pace-python, is a python package which brings Horace 3.6.3 and SpinW to python removing the need for Matlab whilst keeping the commands you have become familiar with.

## Requirements

- Windows
- Python 3.8, 3.9 or 3.10 (You can check this by running `python --version` in your terminal)
- Matlab R2021b runtime

## Installation

The easiest way to install `pace-neutrons` and its installer is by downloading the `pace_neutrons_installer` from the [release](https://github.com/pace-neutrons/pace-python/releases) on github.
When this is run, it will install the pace-neutrons pypi package as well as the Matlab runtime required to use the package.

Alternatively, Pace-Neutrons can be installed by running:

`pip install pace-neutrons`

This will require you to download and install the corresponding Matlab runtime (by default R2021b) which can be found along with installation instructions 
[here](https://uk.mathworks.com/products/compiler/matlab-runtime.html). The correct runtime can also be obtained by running the `pace_neutrons --install-mcr`
command in your terminal. 

## Usage

### Differences to regular Horace

All of the familiar [Horace commands](https://pace-neutrons.github.io/Horace/v3.6.3/) can be used with pace-neutrons simply by prefixing them 
with `m.` and dropping the semi-colon at the end of the line. For example,  

```matlab
plot(cut_sqw('file.sqw', proj, [-2 0.05 2], [-2 0.05 2], [-0.1 0.1], [9 11], '-nopix'));
```

would become 

```python
m.plot(m.cut_sqw('file.sqw', proj, [-2, 0.05, 2], [-2, 0.05, 2], [-0.1, 0.1], [9, 11], '-nopix'))
```

(Note that Python requires a comma between vector elements, unlike Matlab).

Beyond this, the key difference is that the syntax used beyond Horace, e.g. for loops
and conditional statements, or to define structures will be Python. 
So, in the above example, whilst the projection `struct` would be defined as

```matlab
proj = struct('u', [1 1 0], 'v', [-1 1 0], 'type', 'rrr');
```

or

```matlab
proj = struct();
proj.u = [1 1 0]; proj.v = [-1 1 0]; proj.type = 'rrr';
```

in Matlab, in Python it must be defined as a `dict` as follows

```python
proj = {'u':[1, 1, 0], 'v':[-1, 1, 0], 'type':'rrr'}
```

or

```python
proj = {}
proj['u'] = [1, 1, 0]; proj['v'] = [-1, 1, 0]; proj['type'] = 'rrr';
```

Likewise, loops would use Python syntax so something in Matlab like:

```matlab
proj = struct('u', [1 1 0], 'v', [-1 1 0], 'type', 'rrr');
for en = [10:2:20]
    plot(cut_sqw('file.sqw', proj, [-2 0.05 2], [-2 0.05 2], [-0.1 0.1], en+[-1 1], '-nopix'));
    lz 0 0.01;
    keep_figure;
end
```

would become in Python:

```python
proj = {'u':[1, 1, 0], 'v':[-1, 1, 0], 'type':'rrr'}
for en in range(10, 21, 2):
    m.plot(m.cut_sqw('file.sqw', proj, [-2, 0.05, 2], [-2, 0.05, 2], [-0.1, 0.1], [en-1, en+1], '-nopix'))
    m.lz(0, 0.01)
    m.keep_figure()
```

Note that the Matlab "command syntax" (e.g. `lz 0 0.01`) will not work in Python so you must use the "Function syntax" instead.
Also, whilst Matlab allows functions to be called without the brackets if no arguments are needed,
Python does not, hence the need for brackets in `m.keep_figure()`.
Finally, the `plus` (`+`) operator functions differently for Matlab `vector`s and Python `list`s,
so the syntax `en+[-1 1]` in Matlab will not work in Python.
In Matlab is works as an addition, whilst in Python it is a concatenation operator.
The Matlab `vector` is more like a *numpy* `array`, than a Python `list` but the similarity of square bracket operators for
the construction of Matlab `vector`s and Python `list`s caused us to choose to allow `list`s of numbers to be substituted
for Matlab `vector`s.
If you want to use the `plus` operator like in Matlab, you can convert the list into a numpy array, e.g.

```python
import numpy as np
for en in range(10, 21, 2):
    m.plot(m.cut_sqw('file.sqw', proj, [-2, 0.05, 2], [-2, 0.05, 2], [-0.1, 0.1], en+np.array([-1, 1]), '-nopix'))
```

A Matlab `cell array` is more similar to a Python `list` but in Python the curly brackets are used to construct a `dict`.
So, instead we have chosen to use a Python `tuple` as equivalent to a Matlab `cell array`
(a Python `list` which contains non-numeric elements will also be interpreted as a Matlab `cell array`).

Thus the following code in Matlab:

```matlab
proj = struct('u', [1 1 0], 'v', [-1 1 0], 'type', 'rrr');
ws = cut_sqw('file.sqw', proj, [-2, 0.05, 2], [-0.1, 0.1], [-0.1, 0.1], [4, 6]);
tri = sw_model('triAF', 1);
fwhm = 0.75;
scalefactor = 1;
kk = multifit_sqw(ws);
kk = kk.set_fun(@tri.horace_sqw);
kk = kk.set_pin({[J fwhm scalefactor], 'mat', {'J_1'}, 'hermit', false, 'formfact', true, 'resfun', 'gauss'});
tic
ws_sim = kk.simulate()
toc
```

would be in Python:

```python
proj = {'u':[1, 1, 0], 'v':[-1, 1, 0], 'type':'rrr'}
ws = m.cut_sqw('file.sqw', proj, [-2, 0.05, 2], [-0.1, 0.1], [-0.1, 0.1], [4, 6])
tri = m.sw_model('triAF', 1)
fwhm = 0.75
scalefactor = 1
kk = m.multifit_sqw(ws)
kk = kk.set_fun(tri.horace_sqw)
kk = kk.set_pin(([J, fwhm, scalefactor], 'mat', ('J_1'), 'hermit', false, 'formfact', true, 'resfun', 'gauss'))
m.tic()
ws_sim = kk.simulate()
m.toc()
```

### Setup

In order to get started with pace-neutrons, first begin a python session either in your terminal
by running either the `python` or `python3` command or by creating a `.py` file. Once this is done, 
the following commands must be run in order for Horace commands to be useable:

```python
from pace_neutrons import Matlab
m = Matlab()
```

**Note:** if you assign `Matlab()` to a different variable name this would be the new prefix to 
the Horace matlab commands.

### Example commands

#### Example

Using Horace:
```matlab
proj = projaxes([-0.5, 1, 0], [0, 0, 1], 'type', 'rrr');
w1 = cut_sqw('ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.4, 0.5], [3, 0.5, 20]);
hf = plot(w1);
```

Using pace-neutrons:
```python
from pace_neutrons import Matlab
m = Matlab()
proj = m.projaxes([-0.5, 1, 0], [0, 0, 1], 'type', 'rrr')
w1 = m.cut_sqw('ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.4, 0.5], [3, 0.5, 20])
hf = m.plot(w1)
```

**Note:** The above example will not work for you due the absence of the `'ei30_10K.sqw'` file.

Additional examples can be found in the demo scripts detailed in the next section.
The examples found in the demo are complete with the required data files ready for use.

#### Demo

A demo for pace-neutrons is found [here](https://github.com/pace-neutrons/pace-python-demo). This can be 
downloaded by first navigating to the provided github repository and clicking on the green code button and
selecting the `Download ZIP` option. This demo is complete with a demo `.py` script as well as a `.ipynb` 
file for use in a Jupyter notebook.


#### Horace GUI

The Horace GUI can be opened, following the setup procedure outlined above, by 
running `m.horace()`

## Jupyter notebook specifics

By default, when creating the Matlab plots in a Jupyter notebook, a screenshot of the plot is taken 
and displayed in the document. To bypass this behaviour and obtain the usual pop out plots expected 
from plots created using Horace, `%matlab_plot_mode windowed` can be run in a code cell.

## Advanced usage (for developers): Creating a custom build

An installable wheel file can be built by running `python setup.py bdist_wheel <options>` in the top level
directory of pace-python. The command line <options> allow a build to be customised. The available options are 
detailed below and can be used by prefixing them with `-D`. 

**Note:** Through the dependence on the `libpymcr` python package, custom builds are not required to conform to
standard Matlab-python version compatability and instead can use any combination of Python3 and Matlab.

#### Command line options

- **WITH_HORACE** - Set Horace use ON/OFF
- **WITH_SPINW** - Set SpinW use ON/OFF
- **HORACE_PATH** - Provide a path to your version of Horace
- **SPINW_PATH**  - Provide a path to your version of SpinW
- **HORACE_VERSION** - Set the Horace release version to download e.g. 3.6.3
- **SPINW_VERSION** - Set the SpinW version (git tag/branch/hash)
- **SPINW_REPO** - Set the repo to get SpinW from e.g. "mducle/spinw"
- **Matlab_ROOT_DIR** - Provide a path to desired Matlab version

#### Example

`python setup.py bdist_wheel -DWITH_SPINW=OFF -DHORACE_PATH="/path/to/your/systems/Horace"`

This example builds pace-neutrons without SpinW and uses a local copy of Horace located at
the provided path.

## Running on Linux

Currently, whilst using linux, `pace_neutrons` struggles to locate Matlab. It may be possible
to resolve this by setting the following two environment variables:

```
LD_LIBRARY_PATH = "<matlab_runtime_root>/runtime/glnxa64:<matlab_runtime_root>/bin/glnxa64"
LD_PRELOAD = "<matlab_runtime_root>/sys/os/glnxa64/libiomp5.so"
```

Alternatively, try running the `pace_neutrons` with the `--matlab-dir` option as shown below:

`pace_neutrons --matlab-dir /path/to/matlab/runtime`