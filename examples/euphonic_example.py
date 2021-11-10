# For some reason we _have_ to load euphonic before Matlab
from euphonic import ForceConstants
from pace_neutrons import EuphonicWrapper

# Setting (os.RTLD_NOW | os.RTLD_DEEPBIND) flags causes a crash here...
#import sys; sys.setdlopenflags(10)

from pace_neutrons import Matlab
m = Matlab()
import numpy as np
from matlab import double as md

fc = ForceConstants.from_castep('quartz/quartz.castep_bin')
euobj = EuphonicWrapper(fc, debye_waller_grid=[6, 6, 6], temperature=100, 
                        negative_e=True, asr=True, chunk=10000, use_c=True)

scalefac = 1e12
effective_fwhm = 1
intrinsic_fwhm = 0.1

wsc = m.cut_sqw('quartz/2ph_m4_0_ECut.sqw', [-3.02, -2.98], [5, 0.5, 38])

# Calculate spectra with simple energy convolution (fixed width Gaussian)
wsim = m.disp2sqw_eval(wsc, euobj.horace_disp, (scalefac), effective_fwhm)

# Calculate spectra with full instrument resolution convolution
is_crystal = True; 
xgeom = [0,0,1]; 
ygeom = [0,1,0]; 
shape = 'cuboid'; 
shape_pars = [0.01,0.05,0.01];
wsc = m.set_sample(wsc, m.IX_sample(is_crystal, xgeom, ygeom, shape, shape_pars));
ei = 40; freq = 400; chopper = 'g';
wsc = m.set_instrument(wsc, m.merlin_instrument(ei, freq, chopper));
disp2sqwfun = m.eval('@disp2sqw');
kk = m.tobyfit(wsc);
kk = kk.set_fun(disp2sqwfun, [euobj.horace_disp, [scalefac], intrinsic_fwhm]);
wtoby = kk.simulate()

hf = m.plot(wsc); m.pl(wsim); m.acolor('red'); m.pl(wtoby);
m.uiwait(hf)
