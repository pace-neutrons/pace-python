import six
import numpy as np
from numbers import Number
from .MatlabProxyObject import MatlabProxyObject
from .MatlabFunction import MatlabFunction
from .TypeWrappers import as_matlab, as_numpy
from .FunctionWrapper import pymatpy

NPY_INT = [np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64, np.int64, np.bool_]

class DataTypes:

    def __init__(self, interface, pyMatlab):
        """
        Data Converter to/from python and MATLAB
        :param matlab:
        """
        self.matlab = pyMatlab
        self.interface = interface
        # self.outNumpy = True
        # self.transpose = True

    def _unwrap(self, datalist):
        for ii in range(len(datalist)):
            datalist[ii] = self.encode(datalist[ii])
        return datalist

    def encode(self, data):

        # What is data?
        # 1) If it's a numpy array or a list, we convert. to matlab.double
        # 2) If it is a dict, then we enumerate values and encode them.
        # 3) If it's a tuple, it's a cell, which we enumerate. BUT, then we convert it into a list.
        # 4) If it is a double it's a double, if a integer, we encode to a double as well. MATLAB is tricky :-/

        if isinstance(data, bool):
            data = self.matlab.logical([data])
        elif isinstance(data, list) or isinstance(data, range):
            # Case 1)
            try:
                data = self.matlab.double(data)
            except ValueError:
                data = self._unwrap(data)
            # If the list is not one of numbers leave it for Matlab to convert to a cell array
        elif isinstance(data, np.ndarray):
            if data.size < 1000 and data.dtype in NPY_INT:
                data = self.matlab.double(data.tolist())
            else:
                data = as_matlab(data)
        elif isinstance(data, Number):
            # Case 4)
            data = float(data)
        elif isinstance(data, MatlabFunction):
            if isinstance(data._fun, six.string_types):
                if data._parent:
                    data = self.interface.get_method_refs(data._fun, data._parent, nargout=1)
                else:
                    data = self.interface.get_method_refs(data._fun, nargout=1)
            else:
                data = data._fun
        elif isinstance(data, MatlabProxyObject):
            data = data.handle
        elif hasattr(data, '__call__'):
            # A python callable - wrap it so that a Matlab mex using the C API can call it
            data = pymatpy(data, self.interface)
        else:
            # Case 2, 3
            if isinstance(data, dict):
                # Case 2)
                for key, item in data.items():
                    data[key] = self.encode(item)
            elif isinstance(data, tuple):
                # Case 3)
                newdata = []
                for item in data:
                    newdata.append(self.encode(item))
                data = newdata

        # Unknown data i.e. text should pass through
        # TODO Make sure this works for more data cases...
        return data

    def decode(self, data):
        # Decode the numeric data types. NOTE that we let the functions/methods slip through.
        if isinstance(data, list):
            # This is a cell return
            for key, item in enumerate(data):
                data[key] = self.decode(data[key])
            data = tuple(data)
        elif isinstance(data, tuple):
            return (self.decode(d) for d in data)
        elif isinstance(data, self.matlab.double):
            data = as_numpy(data)
        elif isinstance(data, self.matlab.int8):
            # TODO for all available data types
            data = np.ndarray(data)
        elif isinstance(data, str):
            if len(data) == 34:
                if data[0:2] == '!$':
                    try:
                        data = self.decode(self.interface.get_global(data[2:]))
                    except Exception as e:
                        print(e)
        elif isinstance(data, dict):
            for key, item in data.items():
                data[key] = self.decode(item)
        elif self.interface.call('isobject', [data]):
            data = MatlabProxyObject(self.interface, data, self)
        elif self.interface.call('isa', [data, 'function_handle']):
            data = MatlabFunction(self.interface, data, converter=self, parent=[])

        return data
