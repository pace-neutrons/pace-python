# from pyHorace import Matlab
# 
# m = Matlab()
# 
# #ho = m.hor_config(nargout=1)
# #he = m.herbert_config(nargout=1)
# #hp = m.parallel_config(nargout=1)
# #print(ho)
# #print(he)
# #print(hp)
# proj = m.projaxes([-0.5, 1, 0], [0, 0, 1], 'type', 'rrr', nargout=1)
# #w1 = m.cut_sqw('/home/vqq25957/sqw_files/spinw/ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [1.5, 2.5], [0.48, 0.52], [10, 0.5, 20], nargout=1)
# w1 = m.cut_sqw('/home/vqq25957/sqw_files/spinw/ei30_10K.sqw', proj, [0.1, 0.02, 0.5], [-8, 8], [0.4, 0.5], [3, 0.5, 20], nargout=1)
# 
# #print(w1)
# #m.plot(w1, nargout=0)
# #m.waitforgui(nargout=0)

from pyHorace import horace
from matlab import double as md
import matlab

m = horace.initialize()
 
proj = m.projaxes(md([-0.5, 1, 0]), md([0, 0, 1]), 'type', 'rrr', nargout=1)
# The following fails in the compiled code with Matlab R2017b
w1 = m.cut_sqw('/home/vqq25957/sqw_files/spinw/ei30_10K.sqw', proj, md([0.1, 0.02, 0.5]), md([1.5, 2.5]), md([0.4, 0.5]), md([3, 0.5, 20]), nargout=1) 
# Will probably fail in all version (value classes are converted to python dict, lose class info).
w2 = m.cut_sqw(w1, proj, md([0.1, 0.5]), md([3, 0.5, 20]), nargout=1)

# import matlab.engine
# from matlab import double as md
# 
# m = matlab.engine.start_matlab();
# m.addpath('/home/vqq25957/src/herbert_git')
# m.herbert_init(nargout=0)
# m.addpath('/home/vqq25957/src/horace_git')
# m.horace_init(nargout=0)
# 
# #proj = m.projaxes(md([-0.5, 1, 0]), md([0, 0, 1]), 'type', 'rrr', nargout=1)
# proj = {'u':md([-0.5, 1, 0]), 'v':md([0, 0, 1]), 'type':'rrr'}
# # The following line runs in Matlab 2019a, fails in older Matlab python engine versions
# w1 = m.cut_sqw('/home/vqq25957/sqw_files/spinw/ei30_10K.sqw', proj, md([0.1, 0.02, 0.5]), md([-8, 8]), md([0.4, 0.5]), md([3, 0.5, 20]), nargout=1) 
# #print(w1)
# # The following fails in all versions
# w2 = m.cut_sqw(w1, proj, md([0.1, 0.5]), md([3, 0.5, 20]), nargout=1)
