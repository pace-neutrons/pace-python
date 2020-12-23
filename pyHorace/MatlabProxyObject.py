from io import StringIO

from .MatlabFunction import MatlabFunction
from .funcinspect import lhs_info
import re


class MatlabProxyObject(object):
    """A Proxy for an object that exists in Matlab.

    All property accesses and function calls are executed on the
    Matlab object in Matlab.

    Auto populates methods and properties and can be called ala matlab/python

    """

    def __init__(self, interface, handle, converter):
        """
        Create a non numeric object of class handle (an object from a non-numeric class).
        :param interface: The callable MATLAB interface (where we run functions)
        :param handle: The matlabObject which represents a class object
        :param converter: The converter class between MATLAB/python
        """
        self.__dict__['handle'] = handle
        self.__dict__['interface'] = interface
        self.__dict__['converter'] = converter
        self.__dict__['_is_thinwrapper'] = self.interface.call('class', [self.handle], nargout=1) == 'thinwrapper'
        self.__dict__['_is_handle_class'] = self.interface.call('isa', [self.handle, 'handle'], nargout=1)
        if self._is_thinwrapper:
            self.__dict__['_objstr'] = self.interface.call('subsref', [self.handle, self.interface.call('substruct', ['.', 'ObjectString'])])

        # This cause performance slow downs for large data members and an recursion issue with
        # samples included in sqw object (each sample object is copied to all dependent header "files")
        #if not self._is_handle_class:
        #    # Matlab value class: properties will not change so copy them to the Python object
        #    for attribute in self._getAttributeNames():
        #        self.__dict__[attribute] = self.__getattr__(attribute)
        self._getAttributeNames()
        for method in self._getMethodNames():
            super(MatlabProxyObject, self).__setattr__(method,
                                                       MatlabFunction(self.interface, method,
                                                                      converter=self.converter, parent=self.handle,
                                                                      caller=self))

    def _getAttributeNames(self):
        """
        Gets attributes from a MATLAB object
        :return: list of attribute names
        """
        if self._is_thinwrapper:
            self.__dict__['_attributes'] = self.interface.call('evalin', ['base', 'fieldnames({})'.format(self._objstr)])
            return self._attributes
        else:
            return self.interface.call('fieldnames', [self.interface.call('handle', [self.handle])])

    def _getMethodNames(self):
        """
        Gets methods from a MATLAB object
        :return: list of method names
        """
        if self._is_thinwrapper:
            self.__dict__['_methods'] = self.interface.call('evalin', ['base', 'methods({})'.format(self._objstr)])
            return self._methods
        else:
            return self.interface.call('methods', [self.interface.call('handle', [self.handle])])

    def __getattr__(self, name):
        """Retrieve a value or function from the object.

        Properties are returned as native Python objects or
        :class:`MatlabProxyObject` objects.

        Functions are returned as :class:`MatlabFunction` objects.

        """
        m = self.interface
        # if it's a property, just retrieve it
        if self._is_thinwrapper:
            if name in self._attributes:
                return self.converter.decode(self.interface.call('evalin', ['base', '{}.{}'.format(self._objstr, name)]))
            class matlab_method:
                def __call__(_self, *args, **kwargs):
                    nreturn = lhs_info(output_type='nreturns')
                    nargout = max(min(int(kwargs.pop('nargout') if 'nargout' in kwargs.keys() else -1), nreturn), 1)
                    # serialize keyword arguments:
                    args += sum(kwargs.items(), ())
                    args = [self.converter.encode(ar) for ar in args]
                    return self.converter.decode(self.interface.call_method(name, self.handle, args, nargout=nargout))
            return matlab_method()
        elif name in self.interface.call('properties', [self.handle], nargout=1):
            try:
                return self.converter.decode(self.interface.call('subsref', [self.handle, self.interface.call('substruct', ['.', name])]))
            except TypeError:
                return None
        # if it's a method, wrap it in a functor
        elif name in self.interface.call('methods', [self.handle], nargout=1):
            class matlab_method:
                def __call__(_self, *args, **kwargs):
                    nreturn = lhs_info(output_type='nreturns')
                    nargout = max(min(int(kwargs.pop('nargout') if 'nargout' in kwargs.keys() else -1), nreturn), 1)
                    # serialize keyword arguments:
                    args += sum(kwargs.items(), ())
                    return getattr(m, name)(self, *args, nargout=nargout)

                # only fetch documentation when it is actually needed:
                @property
                def __doc__(_self):
                    classname = getattr(m, 'class')(self)
                    return self.interface.call('help', ['{0}.{1}'.format(classname, name)], nargout=1)

            return matlab_method()

    def __setattr__(self, name, value):
        self.__class__[name] = value
        access = self.interface.call('substruct', ['.', name])
        self.interface.call('subsasgn', [self, access, value])

    def __repr__(self):
        # getclass = self.interface.str2func('class')
        return "<proxy for Matlab {} object>".format(self.interface.call('class', [self.handle]))

    def __str__(self):
        # remove pseudo-html tags from Matlab output
        if self._is_thinwrapper:
            html_str = self.interface.call('evalin', ['base', f"evalc('display({self._objstr})')"], nargout=1)
        else:
            html_str = self.interface.call('eval', ["@(x) evalc('disp(x)')"])
            html_str = self.interface.call(html_str, [self.handle])
        return re.sub('</?a[^>]*>', '', html_str)

    def __dir__(self):
        return super(MatlabProxyObject, self).__dir__() + list(self.__dict__.keys()) + self._getAttributeNames()

    @property
    def __doc__(self):
        out = StringIO()
        if self._is_thinwrapper:
            return self.interface.call('evalin', ['base', f"evalc('help({self._objstr})')"], nargout=1, stdout=out)
        else:
            return self.interface.call('help', [self.handle], nargout=1, stdout=out)

    def __del__(self):
        if self._is_thinwrapper:
            try:
                self.interface.call('evalin', ['base', f"clear('{self._objstr}')"], nargout=0)
            except RuntimeError as err:
                if not str(err).startswith('call() cannot be called after terminate()'):
                    raise

    def updateProxy(self):
        """
        Perform a update on an objects fields. Useful for when dealing with handle classes.
        :return: None
        """
        # We assume methods can't change
        for attribute in self._getAttributeNames():
            self.__dict__[attribute] = self.__getattr__(attribute)

    def updateObj(self):
        """
        When you change an attributes value, the corresponding value should be changed in self.handle
        :return: None
        """
        raise NotImplementedError
