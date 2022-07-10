#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
`pace_neutrons` is a Python module which packages together "compiled" versions of the Matlab programs
which comprises the PACE suite of inelastic neutron scattering data analysis programs.
It includes [Horace](https://github.com/pace-neutrons/Horace) and [SpinW](https://github.com/SpinW/SpinW)
and interfaces between these programs and other PACE components such as
[Euphonic](https://github.com/pace-neutrons/euphonic) and [Brille](https://github.com/brille/brille).

This notebook is an example of how to use `pace_neutrons`.

If you are using the STFC Data Analysis as a Service (DAaaS) platform, then you can run
`pace_neutrons` by starting a command line terminal and typing:
    
/mnt/nomachine/isis_direct_soft/pace_neutrons --spyder

or

/mnt/nomachine/isis_direct_soft/pace_neutrons --jupyter

If you are running this on your own system you will need to install the module with:

pip install pace_neutrons

In addition you also need the Matlab Compiler Runtime (MCR) version R2020a 
for you OS, which can be downloaded here:
https://www.mathworks.com/products/compiler/matlab-runtime.html
Alternatively, if you have a Matlab R2020a *with the Compiler SDK toolbox installed*
then you do not need the MCR.
"""

# First we import the module and start up the Matlab interpreter

import numpy as np
from pace_neutrons import Matlab
m = Matlab()

# Note that every Matlab command (including all Horace and SpinW commands)
# must be called as a method of the Matlab `m` object.
# For example, to calculate the eigenvalues of a 3x3 "magic" square matrix in Matlab:
em = m.eig(m.magic(3))
print(em)

# If you are not running this on the DAaaS platform, you will need some files
# from the Excitations Data Analysis Training Course (EDATC).
# Please download a zip of the repository here:
# https://github.com/pace-neutrons/edatc/archive/refs/heads/main.zip
# And put the location you unzipped it in the `edatc_folder` variable.
# Note that you should also download the Zenodo archive here:
# https://zenodo.org/record/5020485
# And unzip the contents of that file into the edatc/crystal_datafiles folder

# If you are running this on DAaaS, the following path is correct
edatc_folder = '/home/mdl27/src/edatc'

# Put the folder where you want generated files from this script to go:
output_data_folder = '/tmp/aaa_my_work'

# Create the output folder if it doesn't exist
import os
if not os.path.exists(output_data_folder):
    os.mkdir(output_data_folder)

#%%
# =========================================================================
#              Make a fake data set to explore more thoroughly 
# =========================================================================

# Name and folder for output "fake" generated file
sqw_file = os.path.join(output_data_folder, 'my_fake_file.sqw')

# Instrument parameter file (may be in another location to this)
par_file = os.path.join(edatc_folder, 'crystal_datafiles/4to1_102.par')

# u and v vectors to define the crystal orientation 
# (u||ki, uv plane is horizontal but v does not need to be perp to u.
u = [1, 0, 0]
v = [0, 1, 0]

# Range of rotation (psi) angles to cover in simulated dataset.
# (psi=0 when u||ki)
psi = range(0, 91, 5)

# Incident energy in meV
efix = 401
emode = 1    # This is for direct geometry (set to 2 for indirect)

# Range of energy transfer (in meV) for the dataset to cover
en = range(0, 361, 4)

# Sample lattice parameters (in Angstrom) and angles (in degrees)
alatt = [2.87, 2.87, 2.87]
angdeg = [90, 90, 90]

# Sample misalignment angles ("gonios"). [More details in session 4].
omega=0; dpsi=0; gl=0; gs=0;

# This runs the command to generate the "fake" dataset.
m.fake_sqw (en, par_file, sqw_file, efix, emode, alatt, angdeg,
            u, v, psi, omega, dpsi, gl, gs)

#%%
# =========================================================================
# Once generated, you can use standard Horace plotting tools to explore 
# this fake dataset, where the colour scale corresponds to the value of psi
# that contributed data to a given region of reciprocal space					 

sqw_file = os.path.join(output_data_folder, 'my_fake_file.sqw')

# First define a view projection (these u and v do not need to be the same
# as the sample u and v above. They just define the first, second and third
# axes for making a cut (third axis w is implicit being perpendicular to the 
# plane defined by u and v).
proj = {'u':[-1,-1,1], 'v':[0,1,1]}

# The 4th offset coordinate is energy transfer 
proj['uoffset'] = [0, 0, 0, 0]

# Type is Q units for each axis and can be either 'r' for r.l.u. or 'a' 
# for absolute (A^-1). E.g. 'rar' means u and w are normalissed to in r.l.u, v in A^-1.
proj['type'] = 'rrr'

# Actually, it is better to make a projection object with this information
# rather than a structure. Type: >> doc projaxes   for more details.
# Note that the default for uoffset is [0,0,0,0] so it doesn't need to be set
proj = m.projaxes([-1,-1,1], [0,1,1], 'uoffset', [0,0,0,0], 'type', 'rrr')

# Now make a cut of the fake dataset.
# The four vectors indicate either the range and step (three-vector) or
# the integration range (2-vector), with units defined by the proj.type
# The following makes a 3D volume cut with axes u, v and energy 
# (first, second and fourth vectors are 3-vectors), 
# integrating over w between -0.1 and 0.1.
# '-nopix' indicates to discard the pixel information and create
# a dnd (d3d) object.
my_vol = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-3,0.05,3],
                   [-0.1,0.1], [0,4,360], '-nopix')

# Plot the 3D cut - click on the graph to plot 2D projections of the volume
my_vol.plot()

# The following makes a 2D cut with axes u and energy (first and fourth
# vectors are 3-vectors), integrating over v and w between -0.1 and 0.1
my_cut = m.cut_sqw(sqw_file, proj, [-1,0.05,1], [-0.1,0.1], [-0.1,0.1], [0,10,400], '-nopix')

# Now plot the 2D cut.
m.plot(my_cut)

# We set the offset to be centred on (200), (020) and (002) in turn
# Plotting the dispersion along the [h00] direction (note different u and v)
# Using keep_figure to keep the figures on screen.
# Afterwards, you can check which figure gives the largest coverage.
proj = m.projaxes([1,0,0], [0,1,0], 'uoffset', [2,0,0,0], 'type', 'rrr')
m.plot(m.cut_sqw(sqw_file, proj, [-1,0.05,1], [-0.1,0.1], [-0.1,0.1], [0,4,360], '-nopix'))
m.keep_figure();

proj = m.projaxes([1,0,0], [0,1,0], 'uoffset', [0,2,0,0], 'type', 'rrr')
m.plot(m.cut_sqw(sqw_file, proj, [-1,0.05,1], [-0.1,0.1], [-0.1,0.1], [0,4,360], '-nopix'))
m.keep_figure();

proj = m.projaxes([1,0,0], [0,1,0], 'uoffset', [0,0,2,0], 'type', 'rrr')
m.plot(m.cut_sqw(sqw_file, proj, [-1,0.05,1], [-0.1,0.1], [-0.1,0.1], [0,4,360], '-nopix'));
m.keep_figure();

# As an alternative, we could manually change the integration range in the relevant
# axes instead, but using uoffset is easier:
# proj = m.projaxes([1,0,0], [0,1,0], 'type', 'rrr');
# w200 = m.cut_sqw(sqw_file, proj, [-1+2,0.05+2,1+2], [-0.1,0.1], [-0.1,0.1], [0,4,360], '-nopix')
# w020 = m.cut_sqw(sqw_file, proj, [-1,0.05,1], [-0.1+2,0.1+2], [-0.1,0.1], [0,4,360], '-nopix')
# w002 = m.cut_sqw(sqw_file, proj, [-1,0.05,1], [-0.1,0.1], [-0.1+2,0.1+2], [0,4,360], '-nopix')

# Use a different projection to make a 2D slice along [hhh] centred at (200)
proj = m.projaxes([1,1,1], [0,1,0], 'uoffset', [2,0,0,0], 'type', 'rrr')
m.plot(m.cut_sqw(sqw_file, proj, [-1,0.05,1], [-0.1,0.1], [-0.1,0.1], [0,4,360], '-nopix'))

#%%
# =========================================================================
#                        Generating an sqw file
# =========================================================================
data_path = os.path.join(edatc_folder, 'crystal_datafiles')

# Name of output sqw file (for the 4D combined dataset)
sqw_file = os.path.join(output_data_folder, 'iron.sqw')

# Instrument parameter file name (only needed for spe files - nxspe files
# have the par file embedded in them).
#par_file = [data_path, '4to1_102.par'];
par_file = ''

# u and v vectors to define the crystal orientation 
# (u||ki when psi=0; uv plane is horizontal but v does not need to be perp to u).
u = [1, 0, 0] 
v = [0, 1, 0]

# Range of rotation (psi) angles of the data files.
# (psi=0 when u||ki)
psi = range(0, 90, 2)

# Data file run number corresponding to the psi angles declared above
# (must be the same size and order as psi)
runno = range(15052, 15098)

# Ensure that we have the parallised SQW generation switched on
m.hpc('on')
m.hpc_config().parallel_cluster = 'herbert'

# Incident energy in meV
efix = 401
emode = 1   # This is for direct geometry (set to 2 for indirect)

# Sample lattice parameters (in Angstrom) and angles (in degrees)
alatt = [2.87, 2.87, 2.87];
angdeg = [90, 90, 90];

# Sample misalignment angles ("gonios"). [More details in session 4].
omega=0; dpsi=0; gl=0; gs=0;

# Construct the data file names from the run numbers (the data file names
# are actually what is required by the gen_sqw function below, but we
# use the numbers as a convenience. This assumes that the data file names
# follow the standard convention of IIInnnnnn_eiEEE.nxspe, where III is
# the instrument abbreviation (MAP, MER or LET), nnnnnn is the run number
# and EEE is the incident energy.
efix_for_name = 400;
spefile = [f'{data_path}/map{runno[ii]}_ei{efix_for_name}.nxspe' for ii in range(len(psi))]

# Now run the function to generate the sqw file.
m.gen_sqw(spefile, par_file, sqw_file, efix, emode, alatt, angdeg, u, v, psi, omega, dpsi, gl, gs)

# Now make a cut and plot it
proj = {'u':[1,1,0], 'v':[-1,1,0], 'type':'rrr'}
w1 = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.05,-0.95], [-0.05,0.05], [70, 90]);
hf = w1.plot()
#m.uiwait(hf)

#%%
# =========================================================================
#                Accumulating data to an existing sqw file
# =========================================================================
#
# The above gen_sqw file generates an sqw file from the list of input
# spe or nxspe files in one go, and deletes all temporary files after it
# finishes. If you are in the middle of a rotation scan, you can use
# accumulate_sqw which does not delete the temporary files and so can
# append newly processed spe/nxspe files to an existing sqw file.
# This may save some time in processing, but is not now generally
# recommended since the implementation of parallelisation in gen_sqw has
# made gen_sqw much faster.
#
# This is because accumulate_sqw needs to know _all_ the psi values
# (including those not yet measured) in order to construct  coarse data
# grid that enables Horace to make fast cuts. If you then include
# measurements at psi values not in the original list, then it is possible
# that some data will lie outside this grid and it will be 'lost' to the
# sqw file. If the additional runs are ones that interleave between the
# original files, this will not be a problem, but if the additional runs
# extend the original angular range, then you must use the 'clean' option
# which is equivalent to gen_sqw.
#
# The syntax for accumulate_sqw is very similar to gen_sqw:
#
# m.accumulate_sqw(spefile, par_file, sqw_file, efix, emode, alatt, angdeg,
#                  u, v, psi, omega, dpsi, gl, gs)
#
# Or:
# m.accumulate_sqw(spefile, par_file, sqw_file, efix, emode, alatt, angdeg,
#                  u, v, psi, omega, dpsi, gl, gs, 'clean')
#
# This is a way of appending newly processed spe files to an existing
# dataset. The key point is that the psi and spe_file arrays contain a list
# of PLANNED files and run-numbers - only those that actually exist will be
# included in the file.
#
# You can run this periodically, for example overnight.

#%%
# =========================================================================
#                         Making cuts and slices
# =========================================================================

# Close previous plots
m.close('all')

# Before making a cut, we have to define viewing (projection) axes, and
# these u and v do not need to be the same as the sample orientation which
# is defined by u and v above (where u||ki at psi=0).
# These u and v just define the Q axes for cut_sqw. Generally you only need
# to define the first two axes, u and v. The third axis w is implicitly
# constructed as being perpendicular to the plane defined by u and v.
# The units of the Q axes are specified by the 'type', which can be 'r'
# for r.l.u. or 'a' for absolute units (A^-1).
# E.g. 'rar' means u and w are in r.l.u, v in A^-1.
# The offset gives a offset for the zero of that axis, with the fourth
# coordinate being the energy transfer in meV.
proj = {}
proj['u']  = [1,1,0]
proj['v']  = [-1,1,0]
proj['uoffset']  = [0,0,0,0]
proj['type']  = 'rrr'

# Alternatively, you can make a projection object with this information
# rather than a structure. Type: >> doc projaxes   for more details.
# Note that the default for uoffset is [0,0,0,0] so it doesn't need to be set
proj = m.projaxes([-1,-1,1], [0,1,1], 'uoffset', [0,0,0,0], 'type', 'rrr')

# The syntax for cut_sqw is:
#
# cut = cut_sqw(sqw_file, proj, u_axis_limits, v_axis_limits, w_axis_limits, ...
#               en_axis_limits, keywords)
#
# The *_axis_limits are either:
#   1. a single number, [0.05], which means that this axis will be plotted
#      with the number being the bin size and limits being the limits of
#      the data.
#   2. two numbers, [-1, 1], which means that this axis will be integrated
#      over between the specified limits.
#   3. three numbers, [-1, 0.05, 1], which means that this axis will be
#      plotted between the first value to the last value with the bin size
#      specified by the middle value.

# In the following we make 3d volume plots along u, v and energy and
# integrating over the w direction. The '-nopix' at the end means that
# cut_sqw will discard all pixel information - that is it will only retain
# the counts and errors for each bin rather than keep the counts of each
# neutron event which is enclosed by each bin. This saves a lot of memory
# and is good enough for plotting but would not be good enough for fitting,
# or for re-cutting as shown below.
my_vol = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-3,0.05,3], [-0.1,0.1], [0,4,360], '-nopix')
m.plot(my_vol)

# Note you can also do:
my_vol.plot()

# Now we make 2D slices integrating over both v and w in Q.
my_slice = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [0,4,280])
m.plot(my_slice)

# Now we make a 1D cut along u, timing how long it takes.
m.tic()
my_cut = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [130,150])
print(m.toc())
m.plot(my_cut)

# In addition to cutting from an sqw file, you can also cut from a previous
# cut. Note that if the previous cut had used '-nopix', the cut bins must
# be aligned with the old cut. Thus if you want to re-cut a cut, do not
# use '-nopix'.
m.tic()
my_cut2 = m.cut(my_slice, [], [130,150])
# The [] above is to keep 1st axes as it is, [130,150] is integration range
# for 2nd axis note because the object we are cutting from is 2d, we only
# need 2 binning arguments, rather than the 4 that are needed when taking a
# cut form the 4-dimensional dataset in the file
print(m.toc())

m.plot(my_cut2)
# This plot is identical to my_cut, but was much faster to create.
# Imagine if you were running a script to take many cuts from the data - it
# is probably quicker to take them from existing data objects, where
# possible!

# For use with later example scripts, save a cut and slice
m.save(my_slice, os.path.join(output_data_folder, 'iron_slice.sqw'))
m.save(my_cut, os.path.join(output_data_folder, 'iron_cut.sqw'))

#%%
# =========================================================================
#                     Basic customisation of plots
# =========================================================================

# Make axes tight:
m.plot(m.compact(my_slice));

# Smoothing:
#m.plot(m.smooth(my_slice))   # this gives an error - think about why!

m.plot(m.smooth(m.d2d(my_slice)));
# d2d command (for 2d objects) converts from sqw type data, with detector pixel retained
# to d2d / dnd object that is smaller in memory and without detector pixel info

# Smoothing options:
m.plot(m.smooth(m.d2d(my_slice),[2,2],'gaussian'));

# Set colour scale and other axes scales in script:
m.lz(0, 0.5)
m.ly(50, 250)
m.lx(-1.5, 1.5)

# Reset a limit
m.lx()

# Retain a figure, so it is not replaced next time you make a plot (of the
# same dimensionality)
m.keep_figure()
m.plot(my_slice)

# Cursor to find a particular data point value
m.plot(my_cut2)
try:
    m.xycursor()
except:
    pass

#%%
# =========================================================================
#                Plotting data with non-orthogonal axes
# =========================================================================

# To demonstrate plotting a non-orthogonal axes system we will use data
# from a crystal with hexagonal symmetry

sqw_nonorth = os.path.join(data_path, 'upd3_elastic.sqw')
proj_nonorth = {}
proj_nonorth['u'] = [1, 0, 0]
proj_nonorth['v'] = [0, 1, 0]
proj_nonorth['type'] = 'rrr'
proj_nonorth['nonorthogonal'] = False   # <--- Default sets to False

# If proj.nonorthogonal is false, u, v and w will be reconstructed to be
# orthogonal. The plots will have correct aspect ratio but it will be
# harder to tell the right reciprocal lattice coordinates by eye.
ws_orth = m.cut_sqw(sqw_nonorth, proj_nonorth, [-7,0.02,3], [-2,0.02,2], [-0.1,0.1], [-1,1])
m.plot(ws_orth)
m.keep_figure()

# Now set the projection axes to non-orthogonal
proj_nonorth['nonorthogonal'] = True;
ws_nonorth = m.cut_sqw(sqw_nonorth, proj_nonorth, [-7,0.02,3], [-2,0.02,2], [-0.1,0.1], [-1,1])
m.plot(ws_nonorth)
m.keep_figure()

#%%
# =========================================================================
#                    Correcting for sample misalignment
# =========================================================================

# Name of output sqw file (for the 4D combined dataset)
sqw_file = os.path.join(output_data_folder, 'iron.sqw')

# Make a series of hk-slices at different l, in order to work out what Bragg
# positions we have. Step sizes and energy integration should be customised for your data
# Step sizes should be as small as possible, and energy integration tight.

proj = m.projaxes([1,0,0], [0,1,0], 'type', 'rrr')

alignment_slice1 = m.cut_sqw(sqw_file, proj, [-5,0.03,8], [-5,0.03,8],  [-0.05,0.05], [-10,10], '-nopix')
alignment_slice2 = m.cut_sqw(sqw_file, proj, [0.95,1.05], [-5,0.03,8],  [-3,0.03,3],  [-10,10], '-nopix')
alignment_slice3 = m.cut_sqw(sqw_file, proj, [-5,0.03,8], [-0.05,0.05], [-3,0.03,3],  [-10,10], '-nopix')

# Look at the 3 orthogonal slices to figure out what bragg peaks are visible
m.plot(m.compact(alignment_slice1)); m.keep_figure()
m.plot(m.compact(alignment_slice2)); m.keep_figure()
m.plot(m.compact(alignment_slice3)); m.keep_figure()

# Our notional Bragg peaks - a list of accessible Bragg peaks (in data they
# may be off from these notional positions)
bragg_peaks = [[4,0,0], [2,0,0], [1,1,0], [4,4,0], [1,0,1]]

# Get the actual Bragg peak positions with the current crystal alignment
# This routine takes radial and transverse cuts around the Bragg peaks listed
# above. See the help for further information about how the routine works -
# you will in general have to adjust some of the inputs here, especially the
# energy window
rlu0, width, wcut, wpeak = m.bragg_positions(sqw_file, bragg_peaks, 1.5, 0.06, 0.4,
                                             1.5, 0.06, 0.4, 20, 'gauss', 'bin_ab')

# Check how well the function did (note the command line prompts to allow you
# to scan through the cuts made above)
m.bragg_positions_view(wcut, wpeak)

# Determine corrections to lattice and orientation (in this example we choose
# to keep the lattice angles fixed, but allow the lattice parameters to be
# refined, keeping a cubic structure by keeping ratios of lattice pars to be same):
alatt = [2.87, 2.87, 2.87]    # original lattice parameters
angdeg = [90, 90, 90]
rlu_corr, alatt, angdeg, _, _, rotangle = m.refine_crystal(rlu0, alatt, angdeg,
    bragg_peaks, 'fix_angdeg', 'fix_alatt_ratio')

# Apply changes to sqw file. For the purposes of this examples sheet you might
# want to copy the file in case you have made a mistake. In practice, you shouldn't
# make a copy as the sqw file could many hundreds of gigabytes and could take
# along time to copy.
print('Copying SQW file to new file to change alignment info in file')
sqw_file_new = os.path.join(output_data_folder, 'iron_aligned.sqw')
m.copyfile(sqw_file, sqw_file_new)
m.change_crystal_horace(sqw_file_new, rlu_corr)

# Check the outcome: Get Bragg peak positions and look at output: should be much better
rlu0, width, wcut, wpeak = m.bragg_positions(sqw_file_new, bragg_peaks, 1.5, 0.06, 0.4,
                                             1.5, 0.06, 0.4, 20, 'gauss','bin_ab')
m.bragg_positions_view(wcut, wpeak)

#=========
# Generally you only want to figure out the misorientation once, then apply
# some correction to subsequent data. You can do this by finding the values
# of the notional goniometers gl, gs, dpsi that are used in gen_sqw:

u = [1, 0, 0]
v = [0, 1, 0]
alatt = [2.87, 2.87, 2.87]   # original lattice parameters
angdeg = [90, 90, 90];
omega=0; dpsi=0; gl=0; gs=0;

alatt, angdeg, dpsi, gl, gs = m.crystal_pars_correct(u, v, alatt, angdeg, omega,
                                                     dpsi, gl, gs, rlu_corr)
print('Corrected lattice parameters: a={}, b={}, c={},'.format(*alatt[0]) +
      'alpha={}, beta={}, gamma={}'.format(*angdeg[0]))
# u and v are the notional scattering plane, alatt0, angdeg0, etc are the
# original values for those parameters you used in gen_sqw, rlu_corr is the
# misalignment correction matrix determined above. The routine outputs the
# corrected lattic parameters (if these were refined) and the values of
# dpsi, gl and gs to use in future regenerations of the sqw file.

#%%
# ========================================================================
#             Advanced plotting and publication quality figures
# =========================================================================

m.close('all')

# ========================================================================
#                            "Spaghetti" plot
# =========================================================================
sqw_file = os.path.join(output_data_folder, 'iron.sqw')

rlp = [[1,-1,0], [2,0,0], [1,1,0], [1,-1,0]]
wspag = m.spaghetti_plot(rlp, sqw_file, 'qbin', 0.1, 'qwidth', 0.3, 'ebin', [0,4,250])
m.lz(0, 3)

# =========================================================================
#                          Two dimensional plot
# =========================================================================

# Recreate the Q-E slice from earlier, this time without saving the pixel
# information
proj = m.projaxes([1,1,0], [-1,1,0], 'type', 'rrr')

my_slice = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [0,4,280], '-nopix')

# Plot the 2d slice first:
m.plot(m.smooth(m.compact(my_slice)))

# Set limits
m.lx(-2, 2)
m.ly(40, 250)
m.lz(0, 0.5)

# Make a nicer title
m.title('My QE slice')

# Label the axes with something nicer
m.xlabel('(1+h,-1+h,0) (r.l.u.)')
m.ylabel('Energy (meV)')

# Get rid of the colour slider
m.colorslider('delete')
m.colorbar()

# If we want to set the font sizes to be bigger, then we have to re-do the
# above:
m.title('My QE slice', 'FontSize', 16)
m.xlabel('(1+h,-1+h,0) (r.l.u.)', 'FontSize', 16)
m.ylabel('Energy (meV)', 'FontSize', 16)

# To set the font size of the ticks, we need to access the figure's axes.
my_handles = m.gca()
# there are many things you can adjust! To set the font size, or any of the
# other properties, do the following:
m.set(my_handles, 'FontSize', 16)

# Suppose we want to change what tick marks are used on the x-axis
num2str = m.eval('@num2str')
m.set(my_handles, 'XTick', np.arange(-2, 2.1, 0.5))
m.set(my_handles, 'XTickLabel', m.arrayfun(num2str, np.arange(-2, 2.1, 0.5), 'UniformOutput', False))

# Put some text on the figure:
m.text(-0.5, 220, 'Ei = 400 meV', 'FontSize', 16)

# Some fancier text to label the colour bar:
tt = m.text(3.2, 240, 'Intensity (mb sr^{-1} meV^{-1} f.u.^{-1})', 'FontSize', 16)
m.set(tt, 'Rotation', -90)

# Save as jpg and eps
m.print('-djpeg', os.path.join(output_data_folder, 'figure.jpg'))
m.print('-depsc', os.path.join(output_data_folder, 'figure.eps'))


#%%
# =========================================================================
#                          One dimensional plots
# =========================================================================

# Make an array of 1d cuts:
energy_range = range(80, 161, 20)
# We first have to create an empty container of the correct size
# In Matlab we can do: `my_cuts(1) = cut_sqw(...` to assign an array of objects
# but Python needs to define the variable `my_cuts` first.
my_cuts = m.sqw.empty()
# Note that in the following, although we are using a Matlab container,
# because we are in Python we use Python (0-based) indexing, not Matlab (1-based).
for i, en in enumerate(energy_range):
    my_cuts[i] = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [-10+en, 10+en])

# plot them individually, to see what they look like first
for i in range(len(energy_range)):
    m.plot(my_cuts[i])
    m.keep_figure()

# We want to plot them all on the same axes, with different colours and
# markers.
my_col = ['black', 'red', 'blue', 'green', 'yellow']
my_mark = ['+', 'o', '*', '.', 'x', 's', 'd', '^', 'v', '>', '<', 'p', 'h']
# note the above are all the possible choices!

for i in range(len(my_cuts)):
    m.acolor(my_col[i])
    m.amark(my_mark[i])
    if i == 1:
        m.plot(my_cuts[i])
    else:
        # The pp command overplots (markers and errorbars) on existing 1d axes
        m.pp(my_cuts[i])

# This is a bit messy. Let's add a constant offset between each cut, and make
# the markers bigger
my_offset = np.arange(0, 1.3, 0.3)
for i in range(len(my_cuts)):
    m.acolor(my_col[i])
    m.amark(my_mark[i], 6)
    if i == 1:
        m.plot(my_cuts[i] + my_offset[i])
    else:
        m.pp(my_cuts[i] + my_offset[i])

# But we could have done this much more cleanly using the vectorised capabilities
# of Horace functions
m.acolor(['black', 'red', 'blue', 'green', 'yellow'])
m.amark(['+', 'o', '*', '.', 'x', 's'], 6)
my_cut_offset = my_cuts + np.arange(0, 1.3, 0.3)
m.dp(my_cut_offset)
# Note that the above only works because we created a Matlab container.
# If we had used a Python list all the code up to here would work but the
# last two lines above would not, because the Matlab `plus` operator
# and the `dp` function does not understand Python lists.

# Now need to extend axes to see everything:
m.lx(-2, 2)
m.ly(0, 1.8)

# Use the same settings as before to get nice font sizes
m.title('Q cuts', 'FontSize', 16)
m.xlabel('(1+h,-1+h,0) (r.l.u.)', 'FontSize', 16)
m.ylabel('Intensity (mb sr^{-1} meV ^{-1} f.u.^{-1})', 'FontSize', 16)
m.set(m.gca(), 'FontSize', 16)
m.set(m.gca(), 'XTick', np.arange(-2, 2.1, 0.5))
m.set(m.gca(), 'XTickLabel', m.arrayfun(num2str, np.arange(-2, 2.1, 0.5), 'UniformOutput', False))

# Insert a figure legend
m.legend('80 meV', '100 meV', '120 meV', '140 meV', '160 meV')

# Reset the plot color to black
m.acolor('k')

#%%
# =========================================================================
#                         Background Subtraction
# =========================================================================
# Recreate the Q-E slice from earlier
sqw_file = os.path.join(output_data_folder, 'iron.sqw')
proj = m.projaxes([1,1,0], [-1,1,0], 'type', 'rrr')
my_slice = m.cut_sqw(sqw_file, proj,
                     [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [0,4,360])
m.plot(my_slice)
m.keep_figure();
m.lz(0, 2)

# Make a 1D cut from the slice at high Q
my_bg = m.cut(my_slice, [1.9,2.1], [])
m.plot(my_bg);

# Now tile it (note the conversion to dnd)
my_bg_rep = m.replicate(m.d1d(my_bg), m.d2d(my_slice))
m.plot(my_bg_rep)
m.ly(0, 2)

my_slice_subtracted = m.d2d(my_slice) - my_bg_rep
m.plot(my_slice_subtracted)
m.lz(0, 2)

#%%
# =========================================================================
#                            Symmetrisation
# =========================================================================
my_slice2 = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-3,0.05,3], [-0.1,0.1], [100,120])
m.plot(my_slice2)

# Fold along vertical:
my_sym = m.symmetrise_sqw(my_slice2, [-1,1,0], [0,0,1], [0,0,0])
m.plot(my_sym);

# Two folds along diagonals
my_sym2 = m.symmetrise_sqw(my_slice2, [1,0,0], [0,0,1], [0,0,0]);
my_sym2 = m.symmetrise_sqw(my_sym2, [0,1,0], [0,0,1], [0,0,0]);
m.plot(my_sym2);

# Some origami!
my_slice3 = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-3,0.05,3], [-2,0.05,2], [100,120]);
m.plot(my_slice3)

sym1 = m.symmetrise_sqw(my_slice3, [0,1,0], [1,0,0], [0,0,0]);
m.plot(sym1);

sym2 = m.symmetrise_sqw(sym1, [1,0,0], [0,0,1], [0,0,0]);
sym2 = m.symmetrise_sqw(sym2, [0,1,0], [0,0,1], [0,0,0]);
m.plot(sym2)

# Squeeze out all the dead volume
m.plot(m.compact(sym2))

# You can also perform whole-dataset symmetrisation with gen_sqw()
# when the sqw file is created. (Whole dataset symmetrisation is not
# supported after the sqw if create at the moment).
# First you need to define a symmetrisation function such as:
#
# def wout = my_sym(win):
#    wout = m.symmetrise_sqw(win, [1,0,0], [0,1,0], [0,0,0])
#
# Then you can call gen_sqw with the "transform_sqw" argument, e.g.:
#
# m.gen_sqw(spefile, par_file, sym_sqw_file, efix, emode, alatt, angdeg,
#           u, v, psi, omega, dpsi, gl, gs, 'transform_sqw', my_sym)

#%%
# =========================================================================
#                            Spurious data
# =========================================================================
w_sp1 = m.sqw(os.path.join(edatc_folder, 'crystal_datafiles', 'spurious1.sqw'))
par_file = os.path.join(edatc_folder, 'crystal_datafiles', '4to1_102.par')

cut1_sp1 = m.cut(w_sp1, [], [-0.1, 0.1], []);
m.plot(cut1_sp1)
# You should see an intense streak at the Bragg position.
# Lets look at a reciprocal space map of it
m.plot(m.cut(w_sp1, [], [], [-2, 2])); m.lz(0, 2000); m.keep_figure();
m.plot(m.cut(w_sp1, [], [], [8, 12])); m.lz(0, 2000); m.keep_figure();
# You should see that there are 3 streaks all in the same direction,
# all coming out of a Bragg peak.
m.run_inspector(cut1_sp1)
# Move through the runs – you should see around run 22 that there is a very
# intense diagonal streak which is present in several runs.

# The excitations are too intense and are not symmetric about the Bragg peak
# so they are not real dispersion, but because they are associated with the
# sample Bragg peak, it suggests they _are_ scattering from the sample.
# In fact they are a detector artefact. This happens because the crystal
# is aligned such that equivalent off-plane Bragg peaks hit a single detector
# tube at the same time causing the electronics to misrecord neutron events,
# because the peaks are so intense.

#%%
# The second dataset
w_sp2 = m.read_sqw(os.path.join(edatc_folder, 'crystal_datafiles', 'spurious2.sqw'))
m.plot(w_sp2)
# You should see that there are Bragg peaks but they don’t seem to have the
# 6-fold symmetry you would expect from the (111) plane of a cubic crystal.
m.run_inspector(w_sp2, 'col', [0, 10000])
# Move through the run_inspector. You should see that the sqw file was formed
# of a set of 46 scans from 0 to 90 deg in 2 deg steps, and then another
# 45 scans from 1 to 89 deg in 2 deg steps.
# Comparing runs 22-27 and 69-74 (you can use run_inspector twice to get 2 plots)
# you should see the scattering is similar but doesn't match up
# (e.g. run 22 looks like run 70 but are 5 degrees apart).
# This is because during the rotation from 90 deg to 1 deg for the second set
# of scans, the sample assembly became stuck and the motor lost its position
# So the second set was not actually measuring from 1 to 89 deg.

#%%
# =========================================================================
#                            Masking data
# =========================================================================
# Mask parts of a dataset out, e.g. if there is a region with a spurion that
# you wish to remove before proceeding to fitting the data
sqw_file = os.path.join(output_data_folder, 'iron.sqw')
proj = m.projaxes([1,1,0], [-1,1,0], 'type', 'rrr')
my_slice = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [0,4,280])
mask_arr = m.ones(m.size(my_slice.data.npix))  # keeps everything
mask_arr2 = mask_arr
mask_arr2[60:120,:] = 0;   # Remember to use Python 0-based indexing here

my_slice_masked1 = m.mask(my_slice,mask_arr);  # should do nothing
my_slice_masked2 = m.mask(my_slice,mask_arr2);

m.plot(my_slice_masked1); m.keep_figure();
m.plot(my_slice_masked2); m.keep_figure();

# Mask out specific points, if the mask you need for the above is more
# complex:
sel1 = m.mask_points(my_slice,   'keep', [-1,1,100,120])  # specify limits to keep
sel2 = m.mask_points(my_slice, 'remove', [-1,1,100,120])  # specify limits to remove

my_slice_masked3 = m.mask(my_slice, sel1)
my_slice_masked4 = m.mask(my_slice, sel2)

m.plot(my_slice_masked3); m.keep_figure();
m.plot(my_slice_masked4); m.keep_figure();

# Masking spurious data
w_sp1 = m.sqw(os.path.join(edatc_folder, 'crystal_datafiles', 'spurious1.sqw'))
cut_sp1 = m.cut(w_sp1, [-0.6, -0.5], [], [])
m.plot(cut_sp1); m.keep_figure(); m.lz(0, 1000)
# Determine the mask – best way is to plot the actual picture with pcolor
#m.figure(); m.pcolor(cut_sp1.data.s); m.caxis([0,1000])
# Then determine the coordinates from this (remember that pcolor transposes the matrix)
mask_arr_sp = m.ones(m.size(cut_sp1.data.npix))
mask_arr_sp[39:41, 56:58] = 0
wmasked = m.mask(cut_sp1, mask_arr_sp)
m.plot(wmasked)
m.lz(0, 1000)

#%%
# =========================================================================
#                            Rescaling data
# =========================================================================

# Bose correction function.
# NB it does not do much at high energies, or course!

my_slice = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [0,4,280])
m.plot(my_slice)
m.lz(0, 2)
m.keep_figure()

my_slice_bose = m.bose(my_slice, 300)  # pretend the data was taken at 300K...
m.plot(my_slice_bose)  # you can still see what this does
m.lz(0, 2)


#%%
# =========================================================================
#                            Miscellaneous
# =========================================================================

# Note the following doesn't work on IDAaaS at the moment as the signal() function was wrongly removed!)
"""
# If you want to see how a certain parameter varies across a dataset:
w_sig = my_slice.signal('Q'); % mod Q in this case
w_sig.plot()

# You can use this now to apply a scale factor to the data. Suppose you wish
# to multiply signal by energy:
my_slice2 = my_slice * my_slice.signal('E');
m.plot(my_slice2)
m.lz(0, 100)
"""

# Take a section out of a dataset:
w_sec = m.section(my_slice, [0, 2.5], [100, 250])  # just 0 to 2.5 in Q, 100 to 250 in energy
m.plot(w_sec)


# Split a dataset up into its contributing runs
w_split = m.split(my_slice)
# w_split is an array of objects (recall indexing of arrays in Matlab)
# each element of the array corresponds to the data from a single
# contributing spe file
m.plot(w_split[0]); m.keep_figure();
m.plot(w_split[9]); # etc.
# Allows you to determine if a spurious or strange signal is coming from a
# single run, or if it is from a collection of runs.

#%%
# =========================================================================
#                         Simulation and Fitting
# =========================================================================

# Defines some functions to be used in the following.
# In Matlab these are given as separate m-files in the `matlab_scripts`
# folder of the EDATC repository.

def sr122_disp(qh, qk, ql, p, twomodes=False):
    """
    SrFe2As2 cross-section, from Tobyfit
    Spin waves for FeAs, from Ewings et al., PRB 78 
    Lattice parameters as for orthorhombic lattice i.e. a ~= b ~5.6Ang
    """
    s_eff, _, _, sj_1a, sj_1b, sj_2, sj_c, _ = tuple(p)
    sjplus = sj_1a + (2.*sj_2)
    #sjminus = (2.*sj_2) - sj_1b
    sk_ab = 0.5 * (np.sqrt((sjplus+sj_c)**2 + 10.5625) - (sjplus + sj_c))
    sk_c  = sk_ab

    # First twin:
    a_q = 2*( sj_1b * (np.cos(np.pi * qk) - 1) + sj_1a + 2*sj_2 + sj_c ) + (3*sk_ab + sk_c)
    d_q = 2*( sj_1a * np.cos(np.pi * qh) + 2*sj_2*np.cos(np.pi*qh)*np.cos(np.pi*qk) + sj_c*np.cos(np.pi * ql) )
    c_anis = sk_ab-sk_c

    wdisp1 = np.sqrt(np.abs(a_q**2 - (d_q + c_anis)**2))
    s_yy = s_eff * ((a_q - d_q - c_anis) / wdisp1)
    if not twomodes:
        return wdisp1, s_yy
    wdisp2 = np.sqrt(np.abs(a_q**2 - (d_q - c_anis)**2))
    s_zz = s_eff * ((a_q - d_q + c_anis) / wdisp2)
    return wdisp1, s_yy, wdisp2, s_zz

def sr122_xsec(qh, qk, ql, en, p):
    """
    SrFe2As2 cross-section, from Tobyfit
    Spin waves for FeAs, from Ewings et al., PRB 78 
    Lattice parameters as for orthorhombic lattice i.e. a ~= b ~5.6Ang
    """
    gam = p[7]
    alatt = np.array([5.57,5.51,12.298])
    arlu = 2*np.pi / alatt
    qsqr = (qh*arlu[0])**2 + (qk*arlu[1])**2 + (ql*arlu[2])**2

    # First Twin
    wdisp1, s_yy, wdisp2, s_zz = sr122_disp(qh, qk, ql, p, twomodes=True)
    wt1 = (4*gam*wdisp1) / (np.pi*((en**2 - wdisp1**2)**2 + 4*(gam*en)**2))  # (n(w)+1).*delta_fnc(w-wd)
    wt2 = (4*gam*wdisp2) / (np.pi*((en**2 - wdisp2**2)**2 + 4*(gam*en)**2))
    s_yy = s_yy * wt1
    s_zz = s_zz * wt2

    weight = 291.2 * ((1-(qk*arlu[1])**2/qsqr) * s_yy + (1-(ql*arlu[2])**2/qsqr) * s_zz)
     
    # Second Twin
    th = -qk * arlu[1] / arlu[0]
    tk = qh *arlu[0] / arlu[1]
    wdisp1, s_yy, wdisp2, s_zz = sr122_disp(th, tk, ql, p, twomodes=True)
    wt1 = (4*gam*wdisp1) / (np.pi*((en**2 - wdisp1**2)**2 + 4*(gam*en)**2))  # (n(w)+1).*delta_fnc(w-wd)
    wt2 = (4*gam*wdisp2) / (np.pi*((en**2 - wdisp2**2)**2 + 4*(gam*en)**2))
    s_yy = s_yy * wt1
    s_zz = s_zz * wt2
    
    weight = weight + 291.2 * ((1-(qk*arlu[1])**2/qsqr) * s_yy + (1-(ql*arlu[2])**2/qsqr) * s_zz)
    return weight

# =========================================================================
#                Simulating a pre-prepared S(Q,w) function
# =========================================================================

# Create cuts and slices for use later
sqw_file = os.path.join(output_data_folder, 'iron.sqw')
proj = m.projaxes([1,1,0], [-1,1,0], 'type', 'rrr')

# Make our usual 2d slice
my_slice = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [0,4,280])

# Make the array of 1d cuts previous made in the advance plotting session
energy_range = range(80, 161, 20)
my_cuts = m.sqw.empty()
for i, en in enumerate(energy_range):
    my_cuts[i] = m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.1,-0.9], [-0.1,0.1], [-10+en, 10+en])

# Simulate on sqw objects (xsec function defined in Python above - no need for @ operator)
parameter_vector = [1,0,0,35,-5,15,10,0.1]
sim_slice = m.sqw_eval(my_slice, sr122_xsec, parameter_vector)
sim_cut = m.sqw_eval(my_cuts, sr122_xsec, parameter_vector)

# Repeat on dnd objects
sim_slice_dnd = m.sqw_eval(m.d2d(my_slice), sr122_xsec, parameter_vector)
sim_cut_dnd = m.sqw_eval(m.d1d(my_cuts), sr122_xsec, parameter_vector)

m.plot(sim_slice); m.keep_figure();
m.plot(sim_slice_dnd); m.keep_figure();

m.acolor('blue')
m.dl(sim_cut[1])
m.acolor('red')
m.pl(sim_cut_dnd[1])
m.keep_figure()

# Note the differences between simulations of notionally the same data.
# This is because dnd just takes the centre point of the integration range,
# whereas sqw takes all of the contributing detector pixels. This is
# imperative if the dispersion varies significantly in a direction
# perpendicular to your cut/slice, as it introduces broadening that the dnd
# simulation fails to capture.


#%%
# =========================================================================
#                  Simulate a peak function with a cut
# =========================================================================
mgauss = m.eval('@mgauss')
pars_in = [0.4,-0.7,0.1, 0.5,-0.2,0.1, 0.5,0.2,0.1, 0.4,0.6,0.1, 0.4,1.3,0.1];
peak_cut = m.func_eval(my_cuts[1], mgauss, pars_in)

m.acolor('black')
m.plot(my_cuts[1])
m.acolor('b')
m.pl(peak_cut);

#%%
# =========================================================================
#                         Make dispersion plots
# =========================================================================

alatt = [2.87, 2.87, 2.87]
angdeg = [90, 90, 90]

lattice = alatt + angdeg
# Reciprocal lattice points to draw dispersion between:
rlp = [[0,0,0], [0,0,1], [0,0,0], [1,0,0], [0,0,0], [1,1,0], [0,0,0], [1,1,1]]
# Input parameters
pars = [1, 0.05, 0.05, 35, -5, 15, 10, 0.1];
# Energy grid
ecent = [0, 0.1, 200];
# Energy broadening term
fwhh = 5
# sr122_disp function defined above - no need for @ operator like in Matlab
m.disp2sqw_plot(lattice, rlp, sr122_disp, pars, ecent, fwhh)



