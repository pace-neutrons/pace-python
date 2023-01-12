from io import StringIO
from .funcinspect import lhs_info
import re

def wrap(inputs, interface):
    # Matlab return types must be: np.array, opaque container, str, tuple, list, dict
    if 'matlab_wrapper' in str(type(inputs)):
        return MatlabProxyObject(interface, inputs)
    elif isinstance(inputs, tuple):
        return tuple(wrap(v, interface) for v in inputs)
    elif isinstance(inputs, list):
        return [wrap(v, interface) for v in inputs]
    elif isinstance(inputs, dict):
        return {k:wrap(v, interface) for k, v in inputs.items()}
    else:
        return inputs

def unwrap(inputs, interface):
    # Matlab return types must be: np.array, opaque container, str, tuple, list, dict
    if isinstance(inputs, MatlabProxyObject):
        return inputs.handle
    elif isinstance(inputs, matlab_method):
        nested_func_str = f'@(obj) @(varargin) {inputs.method}(obj, varargin{{:}})'
        meth_wrapper = interface.call('str2func', nested_func_str, nargout=1)
        return interface.call('feval', meth_wrapper, inputs.proxy.handle)
    elif isinstance(inputs, tuple):
        return tuple(unwrap(v, interface) for v in inputs)
    elif isinstance(inputs, list):
        return [unwrap(v, interface) for v in inputs]
    elif isinstance(inputs, dict):
        return {k:unwrap(v, interface) for k, v in inputs.items()}
    else:
        return inputs

class matlab_method:
    def __init__(self, proxy, method):
        self.proxy = proxy
        self.method = method

    def __call__(self, *args, **kwargs):
        nreturn = lhs_info(output_type='nreturns')
        nargout = int(kwargs.pop('nargout') if 'nargout' in kwargs.keys() else nreturn)
        nargout = max(min(nargout, nreturn), 1)
        ifc = self.proxy.interface
        # serialize keyword arguments:
        args += sum(kwargs.items(), ())
        args = unwrap(args, ifc)
        rv = ifc.call(self.method, self.proxy.handle, *args, nargout=nargout)
        return wrap(rv, ifc)

    # only fetch documentation when it is actually needed:
    @property
    def __doc__(self):
        classname = self.proxy.interface.call('class', self.proxy)
        return self.proxy.interface.call('help', '{0}.{1}'.format(classname, self.method), nargout=1)


class MatlabProxyObject(object):
    """A Proxy for an object that exists in Matlab.

    All property accesses and function calls are executed on the
    Matlab object in Matlab.

    Auto populates methods and properties and can be called ala matlab/python

    """

    def __init__(self, interface, handle):
        """
        Create a non numeric object of class handle (an object from a non-numeric class).
        :param interface: The callable MATLAB interface (where we run functions)
        :param handle: The matlabObject which represents a class object
        """
        self.__dict__['handle'] = handle
        self.__dict__['interface'] = interface
        self.__dict__['_is_handle_class'] = self.interface.call('isa', self.handle, 'handle', nargout=1)

        # This cause performance slow downs for large data members and an recursion issue with
        # samples included in sqw object (each sample object is copied to all dependent header "files")
        #if not self._is_handle_class:
        #    # Matlab value class: properties will not change so copy them to the Python object
        #    for attribute in self._getAttributeNames():
        #        self.__dict__[attribute] = self.__getattr__(attribute)
        for method in self._getMethodNames():
            super(MatlabProxyObject, self).__setattr__(method, matlab_method(self, method))

    def _getAttributeNames(self):
        """
        Gets attributes from a MATLAB object
        :return: list of attribute names
        """
        return self.interface.call('fieldnames', self.handle) + self.interface.call('properties', self.handle, nargout=1)

    def _getMethodNames(self):
        """
        Gets methods from a MATLAB object
        :return: list of method names
        """
        return self.interface.call('methods', self.handle)

    def __getattr__(self, name):
        """Retrieve a value or function from the object.

        Properties are returned as native Python objects or
        :class:`MatlabProxyObject` objects.

        Functions are returned as :class:`MatlabFunction` objects.

        """
        m = self.interface
        # if it's a property, just retrieve it
        if name in self._getAttributeNames():
            try:
                return wrap(self.interface.call('subsref', self.handle, {'type':'.', 'subs':name}), self.interface)
            except TypeError:
                return None
        # if it's a method, wrap it in a functor
        elif name in self.interface.call('methods', self.handle, nargout=1):
            return matlab_method(self, name)

    def __setattr__(self, name, value):
        self.interface.call('subsasgn', self.handle, {'type':'.', 'subs':name}, value)

    def __repr__(self):
        return "<proxy for Matlab {} object>".format(self.interface.call('class', self.handle))

    def __str__(self):
        # remove pseudo-html tags from Matlab output
        html_str = self.interface.call('eval', "@(x) evalc('disp(x)')")
        html_str = self.interface.call(html_str, self.handle)
        return re.sub('</?a[^>]*>', '', html_str)

    def __dir__(self):
        return list(set(super(MatlabProxyObject, self).__dir__() + list(self.__dict__.keys()) + self._getAttributeNames()))

    def __getitem__(self, key):
        if not (isinstance(key, int) or (hasattr(key, 'is_integer') and key.is_integer())) or key < 0:
            raise RuntimeError('Matlab container indices must be positive integers')
        key = [float(key + 1)]   # Matlab uses 1-based indexing
        return self.interface.call('subsref', self.handle, {'type':'()', 'subs':key})

    def __setitem__(self, key, value):
        if not (isinstance(key, int) or (hasattr(key, 'is_integer') and key.is_integer())) or key < 0:
            raise RuntimeError('Matlab container indices must be positive integers')
        if not isinstance(value, MatlabProxyObject) or repr(value) != self.__repr__():
            raise RuntimeError('Matlab container items must be same type.')
        access = self.interface.call('substruct', '()', [float(key + 1)])   # Matlab uses 1-based indexing
        self.__dict__['handle'] = self.interface.call('subsasgn', self.handle, access, value)

    def __len__(self):
        return int(self.interface.call('numel', self.handle, nargout=1))

    # Operator overloads
    def __eq__(self, other):
        return self.interface.call('eq', self.handle, other, nargout=1)

    def __ne__(self, other):
        return self.interface.call('ne', self.handle, other, nargout=1)

    def __lt__(self, other):
        return self.interface.call('lt', self.handle, other, nargout=1)

    def __gt__(self, other):
        return self.interface.call('gt', self.handle, other, nargout=1)

    def __le__(self, other):
        return self.interface.call('le', self.handle, other, nargout=1)

    def __ge__(self, other):
        return self.interface.call('ge', self.handle, other, nargout=1)

    def __bool__(self):
        return self.interface.call('logical', self.handle, nargout=1)

    def __and__(self, other):  # bit-wise & operator (not `and` keyword)
        return self.interface.call('and', self.handle, other, nargout=1)

    def __or__(self, other):   # bit-wise | operator (not `or` keyword)
        return self.interface.call('or', self.handle, other, nargout=1)

    def __invert__(self):      # bit-wise ~ operator (not `not` keyword)
        return self.interface.call('not', self.handle, nargout=1)

    def __pos__(self):
        return self.interface.call('uplus', self.handle, nargout=1)

    def __neg__(self):
        return self.interface.call('uminus', self.handle, nargout=1)

    def __abs__(self):
        return self.interface.call('abs', self.handle, nargout=1)

    def __add__(self, other):
        return self.interface.call('plus', self.handle, other, nargout=1)

    def __radd__(self, other):
        return self.interface.call('plus', other, self.handle, nargout=1)

    def __sub__(self, other):
        return self.interface.call('minus', self.handle, other, nargout=1)

    def __rsub__(self, other):
        return self.interface.call('minus', other, self.handle, nargout=1)

    def __mul__(self, other):
        return self.interface.call('mtimes', self.handle, other, nargout=1)

    def __rmul__(self, other):
        return self.interface.call('mtimes', other, self.handle, nargout=1)

    def __truediv__(self, other):
        return self.interface.call('mrdivide', self.handle, other, nargout=1)

    def __rtruediv__(self, other):
        return self.interface.call('mrdivide', other, self.handle, nargout=1)

    def __pow__(self, other):
        return self.interface.call('mpower', self.handle, other, nargout=1)

    @property
    def __doc__(self):
        out = StringIO()
        return self.interface.call('help', self.handle, nargout=1, stdout=out)

    def __del__(self):
        pass

    def updateProxy(self):
        """
        Perform a update on an objects fields. Useful for when dealing with handle classes.
        :return: None
        """
        # We assume methods can't change
        for attribute in self._getAttributeNames():
            self.__dict__[attribute] = self.__getattr__(attribute)
