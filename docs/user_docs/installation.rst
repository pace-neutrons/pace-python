Installation
============


.. contents:: Contents
   :local:


``pace_neutrons`` is available on the Python Package Index `(PyPI) <https://pypi.org/project/pace-neutrons>`__,
and can in principle be installed with any (CPython) distributions.
However, due to :ref:`restrictions <installation:Restrictions>` detailed below we recommend that you use the
`conda <https://docs.conda.io>`__ system.
You can install a minimal conda system using `miniconda <https://docs.conda.io/en/latest/miniconda.html>`__.
Once you have installed ``conda``, run it and type:

.. code-block:: sh

   conda create -n pace python=3.7
   conda activate pace
   pip install pace_neutrons spyder jupyter

Alternatively, you can download and run one of the installers from the
`github page <https://github.com/pace-neutrons/pace-python/releases/tag/v0.1.4>`__
(either for `Windows <https://github.com/pace-neutrons/pace-python/releases/download/v0.1.4/pace_neutrons_installer_win32.exe>`__
or `Linux <https://github.com/pace-neutrons/pace-python/releases/download/v0.1.4/pace_neutrons_installer_linux.install>`__).

The installer will first install the Matlab Compiler Runtime (MCR) needed by ``pace_neutrons``,
and install a small GUI application called ``Pace Neutrons Installer``,
which you should then run to install a conda environment and the ``pace_neutrons`` package.


Matlab Compiler Runtime
-----------------------

``pace_neutrons`` relies on the Matlab Compiler Runtime (MCR).
If you did not use the installer, then the MCR also needs to be installed.
When you first run ``pace_neutrons`` after installing it using ``pip``,
and the program detects that the MCR has not been installed,
it will prompt you to ask if you want to install it (and to accept the MCR license).
Note that you do not need a full Matlab license to install the MCR or to run ``pace_neutrons``.

Alternatively, if you have the MCR or a full version of Matlab with the Compiler SDK toolbox
(but note that ``pace_neutrons`` specifically needs R2020a on Linux and R2020b on Windows)
installed but in a non-standard location, you can tell ``pace_neutrons`` this using:

.. code-block:: sh

   pace_neutrons -d <path/to/MCR>


This location will be cached for future use, so you do not need to specify it again.

You can also tell the program to install the MCR manually using:

.. code-block:: sh

   pace_neutrons --install-mcr


In this case it will assume that you consent to the MCR license and will not prompt.


Restrictions
------------

Because of the dependence on the MCR, which bundles its own version of many common libraries,
``pace_neutrons`` has a number of restrictions:

* On Linux, only Python 3.6 and 3.7 are supported, requiring Matlab 2020a.
  This is to be compatible with the IDAaaS system.
* On Windows, only Python 3.7 and 3.8 are supported, requiring Matlab 2020b.
  This is to support the most common versions of Python in the Windows app store.
* At present, Mac OS is not supported.
* ``pace_neutrons`` is not compatible with Mantid Workbench.
  This is because of incompatibilities between the versions of the Qt and HDF5 libraries
  bundled by the MCR and those which Mantid is compiled with.

We are working to remove some of these restrictions.

In addition, to avoid incompatiblities with system libraries or those of other Python modules,
we recommend that you install ``pace_neutrons`` in a Python virtual environment such as
`venv <https://docs.python.org/3/library/venv.html>`__/`virtualenv <https://virtualenv.pypa.io/>`__
or `conda <https://docs.conda.io>`__.


Parallization
-------------

You can activate the parallization framework using:

.. code-block:: python

   from pace_neutrons import Matlab
   m = Matlab()
   m.hpc('on')

or deactivate it with :code:`m.hpc('off')`. You can select different types of parallelisation using:

.. code-block:: python

   m.hpc_config().parallel_cluster = 'parpool'

(The compiled matlab code includes the parallelisation toolbox so :code:`parpool` will work.)

Other options are :code:`'herbert'` (file-based communications) or :code:`'mpiexec_mpi'`.
The last options needs an MPI installation, and a properly configured firewall.
On Windows you can use `MSMPI <https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi>`__.
Horace does bundle a version of ``mpiexec`` for Windows but it may be blocked by the firewall in some
cases where the official Microsoft version is not blocked.
(The Matlab version of Horace also has an addition option :code:`'slurm_mpi'` but this only works
on certain versions of the IDAaaS system.)


IDAaaS Installation
-------------------

An installation of ``pace_neutrons`` is available on the `IDAaaS <https://isis.analysis.stfc.ac.uk>`__ system.
To run it, open a terminal and type:

.. code-block:: sh

   /mnt/nomachine/isis_direct_soft/pace_neutrons --spyder

Note that because the distribution is stored on a CEPH shared network drive,
there may be a delay of ~15-30s the first time it is run whilst the data is retrieved and cached.
Subsequent start-up time should be faster.
