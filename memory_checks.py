import struct
import ctypes

from pyHorace import Matlab
m = Matlab()

# We cannot directly create a variable in the Matlab base namespace
# So we first create it in Python using the default matlab.double ctor and get its memory address
import matlab
mm = matlab.double([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
addr_py = mm._data.buffer_info()[0]
print('Original Matlab array in Python memory address is {}'.format(addr_py))

# Check that it contains the correct data (in column-major, so: [1, 4, 7, 2, 5, 8, 3, 6, 9])
data_orig = [struct.unpack('<d', ctypes.string_at(addr_py+i*8, 8))[0] for i in range(9)]
print(data_orig)

# Now we use the get_address mex file to find the address of the matrix in Matlab
addr_mat = int(m.interface.call('get_address', [mm]))
print('Matlab array memory address is {}'.format(addr_mat))

# Luckily if we assign this variable to the Matlab base workspace, it _doesn't_ make another copy
m.interface.call('assignin', ['base', 'mm_mat', mm])
m.interface.call('evalin', ['base', 'whos'], nargout=0)
addr_base = int(m.interface.call('evalin', ['base', 'get_address(mm_mat)']))
print('Matlab base workspace array memory address is {}'.format(addr_base))

# Unfortunately, if we re-export this back to Python it creates another data copy.
# We use evalin (because we cannot use assignin to export to Python) 
mm_py = m.interface.call('evalin', ['base', 'mm_mat'])
print(type(mm_py))
print(mm_py)

# The data is stored in the _data attribute as a buffer object
print(type(mm_py._data))
print(mm_py._data)
# The address of the buffer can be obtained from the buffer_info property
# The first element is the address, the second is the length
buf_info = mm_py._data.buffer_info()
print(buf_info)
print('Exported Python array memory address is {}'.format(buf_info[0]))

# Check that the memory pointed to by the buffer info stores the right data
# Assumming the data is stored as IEEE double, 64-bit (8 byte) floating point number
data_py = [struct.unpack('<d', ctypes.string_at(buf_info[0]+i*8, 8))[0] for i in range(buf_info[1])]
print(data_py)

# And the corresponding Matlab data
data_mat = [struct.unpack('<d', ctypes.string_at(addr_mat+i*8, 8))[0] for i in range(buf_info[1])]
print(data_mat)

# Recap
print('Original Matlab array in Python memory address is {}'.format(addr_py))
print('Matlab array memory address is                    {}'.format(addr_mat))
print('Matlab base workspace array memory address is     {}'.format(addr_base))
print('Exported Python array memory address is           {}'.format(buf_info[0]))

# We can do some additional exploration:
#   1. We can change an element in Python and see if it propagates to Matlab (partly)
#   2. We can change an element in Matlab and see if it propagates to Python (no)

# First Python-to-Matlab
print('\nChange first element in Python matrix')
mm[0][0] = 10
print(mm._data.buffer_info()[0])
print([struct.unpack('<d', ctypes.string_at(addr_py+i*8, 8))[0] for i in range(9)])
print('Matlab Matrix in Python')
print(int(m.interface.call('get_address', [mm])))
m.interface.call('disp', [mm])
print('Matlab Matrix in Matlab') 
print(int(m.interface.call('evalin', ['base', 'get_address(mm_mat)'])))
m.interface.call('evalin', ['base', 'disp(mm_mat)'], nargout=0)

# Now Matlab-to-Python
print('Change second element in Matlab base workspace')
m.interface.call('evalin', ['base', 'mm_mat(2) = 12'], nargout=0)
print('Matlab Matrix in Python')
print(int(m.interface.call('get_address', [mm])))
m.interface.call('disp', [mm])
print('Python Matrix')
print(mm_py._data.buffer_info()[0])
print(mm_py)

# So element change in Python causes another copy of the whole matrix when exported to Matlab
