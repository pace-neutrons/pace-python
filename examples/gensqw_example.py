from pace_neutrons import Matlab
m = Matlab()

#% ========================================================================
#                        Generating an sqw file
# =========================================================================
data_path = 'fe_redux'

# Name of output sqw file (for the 4D combined dataset)
sqw_file = 'iron.sqw'

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
m.uiwait(hf)
