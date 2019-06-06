from pySpinW import Matlab

m = Matlab(mlPath='/MATLAB/MATLAB_Runtime/v96')

# Test calling a function
hkl = m.sw_qscan(([0, 0, 0], [1, 1, 0], 500))

# Test call class
s = m.spinw()

# Print a method call with out arguments
print(s.abc())
# Function call with 2 types of argument
s.genlattice('lat_const', [3, 8, 8], 'angled', [90, 90, 90])
s.addatom('r', [0, 0, 0], label='MCu2')

# Generate a model
af = m.sw_model('squareAF', 1.)
# Do a calculation
spec = af.spinwave(([0, 0, 0], [1, 1, 0], 500))
print(spec)


# NOTE You can not set subfields manually :-(