Installation
============


.. contents:: Contents
   :local:


``pace_neutrons`` is available on the Python Package Index `(PyPI) <https://pypi.org/project/pace-neutrons>`__,
and can in principle be installed with any (CPython) distributions.
We highly recommend to use an isolated Python virtual environment rather than to install ``pace_neutrons``
into a common Python environment with your other software - in particular, ``pace_neutrons`` is currently
not compatible with Mantid due to clashing library dependencies.

If you use the conda/mamba system, one way to install is:

.. code-block:: sh

   conda create -n pace python=3.11
   conda activate pace
   python -m pip install pace_neutrons jupyter

Where you can replace ``conda`` with ``mamba`` if you use the later.
Alternatively, you can use the ``venv`` package:

.. code-block:: sh

    python -m venv /path/to/where/you/want/pace
    /path/to/where/you/want/pace/env/Scripts/activate
    python -m pip install pace_neutrons jupyter

We currently support Python 3.8 to 3.13.


Matlab Compiler Runtime
-----------------------

``pace_neutrons`` relies on the Matlab Compiler Runtime (MCR), which needs to be installed separately.
You can find versions at `the Mathworks page <https://www.mathworks.com/products/compiler/matlab-runtime.html>`__.
We currently support Matlab versions from R2021b to R2024b (R2025a and R2025b are currently not supported).

Alternatively you can download an older installer for `Linux <https://github.com/pace-neutrons/pace-python/releases/download/v0.3.0a1/pace_neutrons_installer_linux.install>`__ or `Windows <https://github.com/pace-neutrons/pace-python/releases/download/v0.3.0a1/pace_neutrons_installer_win32.exe>`__
which will install a stripped down version of the R2021b MCR and a small GUI application to create
a conda environment and install ``pace_neutrons``.
This approach is no longer supported, but the MCR installed by the installer will still work and require
a smaller download than the full MCR from the `official Mathworks webpage <https://www.mathworks.com/products/compiler/matlab-runtime.html>`__.

Finally, ``pace_neutrons`` will also work if you have a full (licensed) version of Matlab, as long as
the Compiler SDK toolbox is installed.


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

An installation of ``pace_neutrons`` is available on the `Ada <https://ada.stfc.ac.uk>`__ system.
To run it, open a terminal and type:

.. code-block:: sh

   /mnt/ceph/auxiliary/excitations/pace_neutrons

Note that because the distribution is stored on a CEPH shared network drive,
there may be a delay of ~10s the first time it is run whilst the data is retrieved and cached.
Subsequent start-up time should be faster.
