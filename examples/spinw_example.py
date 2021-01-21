from pyHorace import Matlab
m = Matlab()

from matlab import double as md
import numpy as np

tri = m.sw_model('triAF', 1)
tri.addmatrix('label', 'K', 'value', m.diag([0, 0, -1]))

print(tri.matrix)

af = m.sw_model('squareAF', 1.)
spec = af.spinwave(([0, 0, 0], [1, 1, 0], 500))
hf0 = m.figure()
m.sw_plotspec(spec, nargout=0)

# Now setup the SpinW model and try to run it
a = 2.87;

fe = m.spinw();
fe.genlattice('lat_const', [a, a, a], 'angled', [90, 90, 90], 'spgr', 'I m -3 m')  # bcc Fe
fe.addatom('label', 'MFe3', 'r', [0, 0, 0], 'S', 5/2, 'color', 'gold')
fe.gencoupling()
fe.addmatrix('label', 'J1', 'value', 1, 'color', 'gray')
fe.addmatrix('label', 'D', 'value', m.diag([0, 0, -1]), 'color', 'green')
fe.addcoupling('mat', 'J1', 'bond', 1)
fe.addaniso('D')
fe.genmagstr('mode', 'direct', 'S', np.array([[0., 0., 1.], [0., 0., 1.]]).T);  # Ferromagnetic

hf2 = m.plot(fe, 'range', [2, 2, 2])
#m.uiwait(hf2)

sqw_file = 'iron.sqw'
# Make a series of 1D cuts of the data
proj = {'u':[1,1,0], 'v':[-1,1,0], 'type':'rrr'}
energy_range = range(80, 160, 20)
my_cuts = []
# Evaluating sqw_eval for a list of cuts doesn't work at the moment
for i in [0]:#range(len(energy_range)):
    my_cuts.append(m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.05,-0.95], [-0.05,0.05], [-10+energy_range[i], 10+energy_range[i]]));
linear_bg = m.eval('@linear_bg');

# Constant parameters for SpinW model
# Note that we use the damped harmonic oscillator resolution model ('sho')
cpars = ['mat', ['J1', 'D(3,3)'], 'hermit', False, 'optmem', 1,
         'useFast', True, 'resfun', 'sho', 'formfact', True];
#m.swpref.setpref('usemex', True);

# Initial parameters:
J = -16;     # Exchange constant in meV - Note previous value was J*S (S=2.5)
D = -0.1;    # SIA constant in meV
gam = 66;
temp = 10;
amp = 131;

kk = m.multifit_sqw (my_cuts[0]);
kk = kk.set_fun (fe.horace_sqw, [md([J, D, gam, temp, amp])]+cpars)
kk = kk.set_free ([1, 0, 1, 0, 1]);
kk = kk.set_bfun (linear_bg, [0.1,0]);
kk = kk.set_bfree ([1,0]);
kk = kk.set_options ('list',2);

# Time a single iteration
m.tic()
wsim = kk.simulate('comp');
t_spinw_single = m.toc();

# Time the fit
m.tic()
wfit, fitdata = kk.fit('comp');
t_spinw = m.toc();

#for i=1:numel(my_cuts)
m.acolor('black');
hf3 = m.plot(my_cuts[0]);
m.acolor('red');
m.pl(wfit['sum']);
m.pl(wfit['back']);
m.keep_figure;
#end

# Display how long it takes to fit
#if exist('t_ana', 'var');
#    fprintf('Time for analytical fitting = %f s\n', t_ana);
#end
print(f'Time for SpinW single iteration = {t_spinw_single} s')
print(f'Time for SpinW fit = {t_spinw} s')

m.uiwait(hf3)
