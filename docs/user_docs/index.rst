.. PACE documentation master file, created by
   sphinx-quickstart on Wed Nov 17 16:31:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PACE: Proper Analysis of Coherent Excitations in Python
=======================================================

``PACE`` is a suite of programs for data analysis of inelastic neutron scattering spectra,
written in both Python and Matlab.

The packages included in PACE are:

* `Horace <https://github.com/pace-neutrons/Horace/>`__ -
  A Matlab program for the visualisation and analysis of large datasets
  from time-of-flight neutron inelastic scattering spectrometers.

* `Euphonic <https://github.com/pace-neutrons/euphonic>`__ -
  A Python program for simulating phonon spectra from DFT output (CASTEP or Phonopy).

* `Brille <https://github.com/brille/brille>`__ -
  A C++/Python program for Brillouin zone interpolation.

* `SpinW <https://github.com/spinw/spinw>`__ -
  A Matlab program for simulating spin wave (magnon) spectra.

The Python programs have separate PyPI packages
(`Euphonic <https://pypi.org/project/euphonic/>`__ and `Brille <https://pypi.org/project/brille/>`__),
whilst this package provides a Python module for the Matlab codes using a compiled Matlab library,
which does not require a Matlab license.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   examples


.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
