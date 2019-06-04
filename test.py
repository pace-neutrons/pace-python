from pySpinW import Matlab

m = Matlab(mlPath='/MATLAB/MATLAB_Runtime/v96')

# This won't be needed eventually....
matlab = m.pyMatlab

s = m.spinw()

hkl = m.sw_qscan(([0, 0, 0], [1, 1, 0], 500))


print(s.abc())
s.genlattice('lat_const', [3, 8, 8], 'angled', [90, 90, 90])
s.addatom('r', [0, 0, 0], label='MCu2')

af = m.sw_model('squareAF', 1.)
spec = af.spinwave(([0, 0, 0], [1, 1, 0], 500))
print(s)