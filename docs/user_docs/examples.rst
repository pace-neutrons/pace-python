Examples
========


.. contents:: Contents
   :local:


Demonstration repository
------------------------

There is a `demonstration repository <https://github.com/pace-neutrons/pace-python-demo>`__
which contains a `Jupyter notebook <https://github.com/pace-neutrons/pace-python-demo/blob/main/demo.ipynb>`__,
a `plain .py script <https://github.com/pace-neutrons/pace-python-demo/blob/main/demo.py>`__
and the required datafiles to run the demonstration.

You can obtain a zip of this repository
`here <https://github.com/pace-neutrons/pace-python-demo/archive/refs/heads/main.zip>`__.

The follow examples will use the data contained in this repository.


Starting ``pace_neutrons``
--------------------------

There are three options to start ``pace_neutrons``:

* ``pace_neutrons`` - starts with an IPython console

* ``pace_neutrons -s`` or ``pace_neutrons --spyder`` - starts with the `Spyder IDE <https://www.spyder-ide.org/>`__

* ``pace_neutrons -j`` or ``pace_neutrons --jupyter`` - starts a Jupyter Notebook server.

(The option to start with ``spyder`` or ``jupyter`` only work if you have already installed Spyder or Jupyter).

The following examples will work with all modes.

Note that for the Jupyter notebooks, by default figures are rendered in the notebook as images (``inline`` mode).
If you are running the Jupyter server on a local machine, and want to have the actual plot windows,
please run the following in a Notebook cell before making any plots:

.. code-block:: python

   %pace windowed


Initialisation
--------------

After starting ``pace_neutrons`` but defore running any of the Matlab derived programs (``horace`` and ``spinw``),
we must initialise the Matlab interpreter using:

.. code-block:: python

   from pace_neutrons import Matlab
   m = Matlab()


Thereafter, all calls to the Matlab-derived code must be prefixed with ``m.``
because they are invoked as methods of the ``Matlab`` class.

In general, the syntax for Horace and SpinW in Python mirrors the syntax in Matlab,
but there are a few differences you should bear in mind:

* Constructors (like in ``fe = m.spinw()``) require explicit brackets (so ``fe = m.spinw`` will not work).
* Matlab functions like ``diag`` must be preceded by ``m.`` and array elements needs ``,`` comma separators.
* Array indexing uses square brackets ``[]`` instead of round brackets ``()`` and are indexed from zero.
* ``.T`` is used for transposed in ``numpy`` instead of the ``'`` operator.
* Keyword arguments for *Matlab functions* must be speficied as pairs ``'arg_name', arg_val``
  in the old-style Matlab fashion rather than in Python style ``arg_name=arg_val``.

For vectors and arrays, ``pace_neutrons`` will try to convert
lists of numeric values into Matlab arrays automatically.
It will convert non-numeric or mixed lists into Matlab cell arrays,
so you should not use the braces ``{}`` constructor for this
(this is used for a Python dictionary which is converted to a Matlab structure).


Using Horace to look at INS data
--------------------------------

In the first example, we will look at a 2D slice of an inelastic neutron scattering single crystal measurement
on the compound :math:`\mathrm{Pr(Ca,Sr)_2Mn_2O_7}`.
The original experiment is described in `this work <https://doi.org/10.1103/PhysRevLett.109.237202>`__
and the datafile is available
`here <https://github.com/pace-neutrons/pace-python-demo/blob/main/datafiles/pcsmo_cut1.sqw>`__.

.. code-block:: python

   proj = m.projaxes([1, 0, 0], [0, 1, 0], 'type', 'rrr')
   w1 = m.cut_sqw('pcsmo_cut1.sqw', proj, \
                  [-1, 0.05, 1], [-1, 0.05, 1], [-10, 10], [10, 20], '-nopix')
   w1.plot()
   m.lz(0, 10)

.. image:: images/example_pcsmo1.png
   :width: 500px


Ensure that you are in the same folder as the data file ``pcsmo_cut1.sqw``
or give the full or relative path to that file in the argument of ``m.cut_sqw``.
The ``cut_sqw`` function rebins (histograms) the data and is described in the Horace documentation
`here <https://pace-neutrons.github.io/Horace/3.6.0/Getting_started.html#data-visualisation>`__ and in more detail
`here <https://pace-neutrons.github.io/Horace/3.6.0/Manipulating_and_extracting_data_from_SQW_files_and_objects.html#cut-sqw>`__.
In this case, we rebin the data into ``0.05`` reciprocal lattice unit (r.l.u.) steps in the
:math:`Q=[100]` and :math:`Q=[010]` directions, summing between -10 and +10 r.l.u in the
:math:`Q=[001]` direction and between 10 and 20 meV in energy transfer.

The ``'-nopix'`` option means that "pixel" (as-measured detector-energy elements) information
is discarded in the returned object, producing a ``d2d`` object
(as opposed to an ``sqw`` object which does retain the pixel information).
``dnd`` objects take up less memory but are unsuitable for resolution convolution calculations
or other complex modelling.
The two types are described in more details in the
`Horace documentation <https://pace-neutrons.github.io/Horace/3.6.0/FAQ.html#the-difference-between-sqw-and-dnd-objects>`__.


Using SpinW to model spin waves
-------------------------------

`SpinW <https://spinw.org/>`__ is a program for calculating magnetic inelastic neutron spectra using linear spin wave theory.

..
   Simple example: bcc-Iron
   ........................

In this example we will model the spin waves in bcc-Iron.
First we define a ``spinw`` object and use its methods to define the crystal lattice, atomic basis,
and spin Hamiltonian parameters (the exchange interactions and single-ion anisotropy).
These parameters are in principle tensor quantities, and are defined in SpinW as :math:`3 \times 3` named matrices.
Finally we define the ferromagnetic structure and plot it.

.. code-block::

   a = 2.87;  # Angstrom, lattice parameter of bcc-Iron

   # Define a SpinW object and the lattice of bcc-Iron
   fe = m.spinw();
   fe.genlattice('lat_const', [a, a, a], 'angled', [90, 90, 90], 'spgr', 'I m -3 m')
   fe.addatom('label', 'MFe3', 'r', [0, 0, 0], 'S', 5/2, 'color', 'gold')
   # Generates the near-neighbour bonds (up to 8 Angstrom by default)
   fe.gencoupling()
   # Define the first neighbour interaction J1 and single-ion anisotropy D
   fe.addmatrix('label', 'J1', 'value', 1, 'color', 'gray')
   fe.addmatrix('label', 'D', 'value', m.diag([0, 0, -1]), 'color', 'green')
   fe.addcoupling('mat', 'J1', 'bond', 1)
   fe.addaniso('D')
   # Define the ferromagnetic structure
   fe.genmagstr('mode', 'direct', 'S', np.array([[0., 0., 1.], [0., 0., 1.]]).T);

   # Plots the structure
   m.plot(fe)

.. image:: images/example_spinw_fe_struct.png
   :width: 500px

We can now plot a dispersion and INS spectrum along high symmetry directions:

.. code-block::

   Qlist = [[3/4, 1/4, 1], [1/2, 1/2, 1], [1/2, 0, 1], [3/4, 1/4, 1], \
            [1, 0, 1], [1/2, 0, 1], 100]
   Qlab  = ['P', 'M', 'X', 'P', '\Gamma', 'X'];

   feSpec = fe.spinwave(Qlist,'hermit',False)
   feSpec = m.sw_egrid(m.sw_neutron(feSpec), 'component', 'Sperp');
   m.figure()
   m.sw_plotspec(feSpec, 'dE', 30, 'qlabel', Qlab)
   m.legend('off')

.. image:: images/example_spinw_fe_disp.png
   :width: 500px


..
   More complex example: Yttrium Iron Garnet
   .........................................

   We will now turn to a more complex example: YIG, which will closely follow
   `tutorial 21 <https://spinw.org/tutorials/21tutorial>`__ of the SpinW webpage.
   This will highlight the slight differences in syntax between the Python version used here
   and the original Matlab code.

   First we define the crystal structure and spin Hamiltonian, following
   `tutorial 21 <https://spinw.org/tutorials/21tutorial>`__ and the
   `original paper (PRL 117, 217201 (2016)) <https://doi.org/10.1103/PhysRevLett.117.217201>`__.

   TODO: Doesn't work with pace-neutrons 0.1.4
         Need to update pace-neutrons and SpinW code (to use less structs and more classes)...


Using Euphonic to model lattice vibrations
------------------------------------------

`Euphonic <https://euphonic.readthedocs.io>`__ is a program to calculate phonon bandstructures
and INS intensities from force constants data.
Euphonic is a Python program and is included automatically in ``pace_neutrons``
so you can simply ``import euphonic`` and follow the examples in the
`documentation <https://euphonic.readthedocs.io/en/stable/qpoint-phonon-modes.html#example>`__.
The input file may be found
`here <https://github.com/pace-neutrons/pace-python-demo/blob/main/datafiles/quartz.castep_bin>`__.

.. code-block:: python

   import seekpath
   import numpy as np
   from euphonic import ureg, QpointPhononModes, ForceConstants
   from euphonic.util import mp_grid

   # Read the force constants
   fc = ForceConstants.from_castep('datafiles/quartz.castep_bin')

   # Generate a recommended q-point path to calculate the structure factor on
   # using seekpath
   cell = fc.crystal.to_spglib_cell()
   qpts = seekpath.get_explicit_k_path(cell)["explicit_kpoints_rel"]
   # Calculate frequencies/eigenvectors for the q-point path
   phonons = fc.calculate_qpoint_phonon_modes(qpts, asr='reciprocal')

   # For the Debye-Waller calculation, generate and calculate
   # frequencies/eigenvectors on a grid (generate a Monkhorst-Pack grid of
   # q-points using the mp-grid helper function)
   q_grid = mp_grid([5,5,5])
   phonons_grid = fc.calculate_qpoint_phonon_modes(q_grid, asr='reciprocal')
   # Now calculate the Debye-Waller exponent
   temperature = 5*ureg('K')
   dw = phonons_grid.calculate_debye_waller(temperature)

   # Calculate the structure factor for each q-point in phonons. A
   # StructureFactor object is returned
   fm = ureg('fm')
   scattering_lengths = {'Si': 4.1491*fm, 'O': 5.803*fm}
   sf = phonons.calculate_structure_factor(scattering_lengths, dw=dw)

   # Plots the spectrum as a colormesh
   from euphonic import ureg
   from euphonic.plot import plot_2d
   energy_bins = np.arange(0, 160, 1)*ureg('meV')
   fig = plot_2d(sf.calculate_sqw_map(energy_bins), vmax=0.1)

.. image:: images/example_quartz_disp.png
   :width: 500px


Defining a Python model function for Horace
-------------------------------------------

In order to use Horace to model or fit an inelastic neutron spectrum,
we have to pass it a model function.
This function should either:

* Accept 4 vectors defining the momentum and energy transfer coordinates
  :math:`(Q_h, Q_k, Q_l, E)` and return the scattering function
  :math:`S(\mathbf{Q}, E)` at those coordinates, *or*
* Accept 3 vectors defining the momentum transfer :math:`(Q_h, Q_k, Q_l)`
  and return two cell arrays :math:`E_n(\mathbf{Q}), S_n(\mathbf{Q})`
  whose :math:`\mathrm{n^{th}}` elements are vectors of the energies and
  intensities of the :math:`\mathrm{n^{th}}` mode.

..
   In the following example we define a Python function of the second form
   which returns two cell arrays :math:`E_n(\mathbf{Q}), S_n(\mathbf{Q})`
   for the case of spin waves in bcc-Iron, that we used SpinW earlier to model.
   We then use the `disp2sqw_plot` to plot the dispersion relation.

   TODO: Doesn't work at the momemnt - need to change ``call_python``

In the following example, we first take a cut from a measurement of bcc-Iron.
Then we define a Python function of the first format which returns :math:`S(\mathbf{Q}, E)`.
This is used to construct a ``multifit_sqw`` object which can be used for fitting or modelling.
The calculated spectrum is this simulated and plot over the data.

.. code-block:: python

   # Make a cut of the data
   proj = {'u':[1,1,0], 'v':[-1,1,0], 'type':'rrr'}
   energy_range = range(80, 160, 20)
   w_fe = m.cut_sqw('datafiles/fe_cut.sqw', proj, \
                    [-3,0.05,3], [-1.05,-0.95], [-0.05,0.05], [70, 90])

   # Parameters for the form factor of Fe2+
   A=0.0706; a=35.008;  B=0.3589; b=15.358;  C=0.5819; c=5.561;  D=-0.0114;

   # Define the Python function
   import numpy as np
   def py_fe_sqw(h, k, l, e, p):
       js = p[0]
       d = p[1]
       om = d + (8*js) * (1 - np.cos(np.pi * h) * np.cos(np.pi * k) * np.cos(np.pi * l))
       q2 = ((1/(2*2.87))**2) * (h**2 + k**2 + l**2)
       ff = A * np.exp(-a*q2) + B * np.exp(-b*q2) + C * np.exp(-c*q2) + D
       return (ff**2) * (p[4]/np.pi) * (e / (1-np.exp(-11.602*e/p[3]))) \
           * (4 * p[2] * om) / ((e**2 - om**2)**2 + 4*(p[2] * e)**2)

   # Starting parameters for fit
   J = 35;     # Exchange interaction in meV
   D = 0;      # Single-ion anisotropy in meV
   gam = 30;   # Intrinsic linewidth in meV (inversely proportional to excitation lifetime)
   temp = 10;  # Sample measurement temperature in Kelvin
   amp = 300;  # Magnitude of the intensity of the excitation (arbitrary units)

   # Define linear background function
   linear_bg = m.eval('@linear_bg')

   # Set up multifit_sqw object
   kk = m.multifit_sqw(w_fe)
   kk = kk.set_fun (py_fe_sqw, [J, D, gam, temp, amp])
   kk = kk.set_free ([1, 0, 1, 0, 1])
   kk = kk.set_bfun (linear_bg, [0.3,0])
   kk = kk.set_bfree ([1,0])

   # Calculate the model spectrum
   w_cal = kk.simulate()

   # Plots the data and model together
   m.plot(w_fe)
   m.pl(w_cal)


.. image:: images/example_pyfun_spectrum.png
   :width: 500px


A fit can be run be replacing ``w_cal = kk.simulate()`` with ``w_fit, fitpars = kk.fit()``.


Modelling INS data with instrument resolution convolution
---------------------------------------------------------

Including instrument resolution convolution to the calculation is simply a matter of
defining the instrument and experimental parameters on the workspace and then replacing
``kk = m.multifit_sqw(w_fe)`` with ``kk = m.tobyfit(w_fe)``, e.g.

.. code-block:: python

   # Set up instrument and experiment parameters
   xgeom = [0,0,1]; ygeom = [0,1,0]; shape = 'cuboid'; shape_pars = [0.01,0.05,0.01];
   w_fe = m.set_sample(w_fe, m.IX_sample(xgeom, ygeom, shape, shape_pars));
   ei = 70; freq = 250; chopper = 's';
   w_fe = m.set_instrument(w_fe, m.maps_instrument(ei, freq, chopper));

   # Set up resolution convolution model
   gam = 0.1 # set intrinsic width to minimum
   kk = m.multifit_sqw(w_fe)
   kk = kk.set_fun (py_fe_sqw, [J, D, gam, temp, amp])
   kk = kk.set_free ([1, 0, 1, 0, 1])
   kk = kk.set_bfun (linear_bg, [0.3,0])
   kk = kk.set_bfree ([1,0])

   # Calculate the model spectrum
   w_res = kk.simulate()

   # Plots the data and model together
   m.plot(w_fe)
   m.pl(w_res)


Modelling Horace data with SpinW or Euphonic
--------------------------------------------

Finally, to use SpinW or Euphonic with Horace, we pass a "gateway" function
defined by those programs to ``multifit_sqw`` or ``tobyfit`` instead of the Python function
we defined in the previous section.

For SpinW, this function is called ``horace_sqw`` and returns a single array :math:`S(\mathbf{Q}, E)`
so can be used directly.

.. code-block:: python

   # Constant parameters for SpinW model
   # Note that we use the damped harmonic oscillator resolution model ('sho')
   cpars = ['mat', ['J1', 'D(3,3)'], 'hermit', False, 'optmem', 1,
            'useFast', True, 'resfun', 'sho', 'formfact', True];

   kk = m.multifit_sqw(w_fe)
   # The spinw object "fe" is previous defined above
   # We need to pass the "horace_sqw" method of the "fe" object:
   kk = kk.set_fun (fe.horace_sqw, [[J, D, gam, temp, amp]]+cpars)
   kk = kk.set_free ([1, 0, 1, 0, 1]);
   kk = kk.set_bfun (linear_bg, [0.1,0]);
   kk = kk.set_bfree ([1,0]);
   kk = kk.set_options ('list',2);

   # Time a single iteration
   m.tic()
   wsim = kk.simulate('comp');
   t_spinw_single = m.toc();

   print(f'Time to evaluate a single iteration: {t_spinw_single}s')

   m.plot(w_fe)
   m.pl(wsim['fore'])


For Euphonic, the gateway function is ``horace_disp`` and returns two cell arrays
:math:`E_n(\mathbf{Q}), S_n(\mathbf{Q})`, so must be wrapped in another function ``disp2sqw`` first.
In addition, ``horace_disp`` is a method of a helper class ``CoherentCrystal``
from the ``euphonic_sqw_models`` module which should be constructed from the ``ForceConstants`` as follows:

.. code-block:: python

   from euphonic import ForceConstants
   from euphonic_sqw_models import CoherentCrystal

   fc = ForceConstants.from_castep('datafiles/quartz.castep_bin')
   euobj = CoherentCrystal(fc, debye_waller_grid=[6, 6, 6], temperature=100,
                           negative_e=True, asr=True, chunk=10000, use_c=True)

   scalefac = 200
   effective_fwhm = 1
   intrinsic_fwhm = 0.1

   wsc = m.cut_sqw('datafiles/quartz_cut.sqw', [-3.02, -2.98], [5, 0.5, 38])

   # Calculate spectra with simple energy convolution (fixed width Gaussian)
   # by wrapping with the "disp2sqw" function in Horace.
   disp2sqwfun = m.eval('@disp2sqw');
   kk = m.multifit_sqw(wsc);
   kk = kk.set_fun(disp2sqwfun, [euobj.horace_disp, [scalefac], intrinsic_fwhm]);
   wsim = kk.simulate()

   hf = m.plot(wsc); m.pl(wsim)


