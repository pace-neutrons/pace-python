"""
This a Python translation of an example script from the Horace training course.
In the original script, a multifit() model was setup and fit but this does not
work in Python at the moment because the thinwrapper around old-style Matlab 
classes does not nest (and the multifit object has a nested sqw object inside
it). So it is changed to just use sqw_eval() instead.
"""

# Have to import Matlab first before any CPython modules or will give ABI errors
from pace_python import Matlab
m = Matlab()
data_path = '/path/to/sqw/'

import numpy as np

sqw_file = '{}/iron.sqw'.format(data_path)

# If the data file doesn't exist, create a fake version
#if ~exist(sqw_file, 'file')
#    generate_iron	
#end

# Make a series of 1D cuts of the data
proj = {'u':[1,1,0], 'v':[-1,1,0], 'type':'rrr'}
energy_range = range(80, 160, 20)
my_cuts = []
# Evaluating sqw_eval for a list of cuts doesn't work at the moment
for i in [0]:#range(len(energy_range)):
    my_cuts.append(m.cut_sqw(sqw_file, proj, [-3,0.05,3], [-1.05,-0.95], [-0.05,0.05], [-10+energy_range[i], 10+energy_range[i]]));

##
# Run the fitting with an analytical expression for the cross-section
#  - using an exact expression for the dispersion of a body-centered cubic 
#    FM combined with a damped harmonic oscillator for the intensity.
# The parameters of the function is: [JS Delta Gamma Temperature Amplitude]
p0 = [35, 0, 30, 10, 300];
# Expression for the dispersion
om = m.eval('@(h,k,l,e,js,d) d + (8*js)*(1-cos(pi*h).*cos(pi*k).*cos(pi*l))');
# The magnetic form factor of Fe2+
A=0.0706; a=35.008;  B=0.3589; b=15.358;  C=0.5819; c=5.561;  D=-0.0114;
ff = m.eval('@(h,k,l) sum(bsxfun(@times, [{} {} {}], exp(bsxfun(@times, -[{} {} {}], ((1/(2*2.87)).^2 .* (h(:).^2 + k(:).^2 + l(:).^2))))), 2) + {}'.format(A, B, C, a, b, c, D));
# Put it altogether
m.assignin('base', 'om', om)
m.assignin('base', 'ff', ff)
fe_sqw = m.evalin('base', '@(h,k,l,e,p) ff(h,k,l).^2 .* (p(5)/pi) .* (e./(1-exp(-11.602.*e./p(4)))) .* 4.*p(3).*om(h,k,l,e,p(1),p(2)) ./ ((e.^2-om(h,k,l,e,p(1),p(2)).^2).^2 + 4.*(p(3).*e).^2)');
linear_bg = m.eval('@linear_bg');

# Starting parameters for fit
J = 35;
D = 0;
gam = 30;
temp = 10;
amp = 300;

# Define the equivalent Python function
def py_fe_sqw(h, k, l, e, p):
    js = p[0]
    d = p[1]
    om = d + (8*js) * (1 - np.cos(np.pi * h) * np.cos(np.pi * k) * np.cos(np.pi * l))
    q2 = ((1/(2*2.87))**2) * (h**2 + k**2 + l**2)
    ff = A * np.exp(-a*q2) + B * np.exp(-b*q2) + C * np.exp(-c*q2) + D
    return (ff**2) * (p[4]/np.pi) * (e / (1-np.exp(-11.602*e/p[3]))) * (4 * p[2] * om) / ((e**2 - om**2)**2 + 4*(p[2] * e)**2)

# Call with Matlab function
w_cal_m = m.sqw_eval(my_cuts[0], fe_sqw, [35, 0, 30, 10, 300])

# Call with Python function
w_cal_py = m.sqw_eval(my_cuts[0], py_fe_sqw, [35, 0, 30, 10, 300])

w_sum_m = m.cut(w_cal_m, [-999., 999.])
print("Summed counts in Matlab calculated cuts = {}".format(w_sum_m.data.s))
w_sum_py = m.cut(w_cal_py, [-999., 999.])
print("Summed counts in Python calculated cuts = {}".format(w_sum_py.data.s))

hf1 = m.plot(w_cal_m)
m.pl(w_cal_py)
m.uiwait(hf1)

kk = m.multifit_sqw(my_cuts[0])
kk = kk.set_fun (fe_sqw, [J, D, gam, temp, amp])
kk = kk.set_free ([1, 0, 1, 0, 1])
kk = kk.set_bfun (linear_bg, [0.1,0])
kk = kk.set_bfree ([1,0])
kk = kk.set_options ('list',2)

# Time it to see how long it takes to do the fit
m.tic()
wfit, fitdata = kk.fit('comp')
t_ana = m.toc();
print(t_ana)
