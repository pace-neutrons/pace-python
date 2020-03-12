from io import StringIO

from .MatlabFunction import MatlabFunction
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

        for attribute in self._getAttributeNames():
            self.__dict__[attribute] = self.__getattr__(attribute)
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
        return self.interface.call('fieldnames', [self.interface.call('handle', [self.handle])])

    def _getMethodNames(self):
        """
        Gets methods from a MATLAB object
        :return: list of method names
        """
        return self.interface.call('methods', [self.interface.call('handle', [self.handle])])

    def __getattr__(self, name):
        """Retrieve a value or function from the object.

        Properties are returned as native Python objects or
        :class:`MatlabProxyObject` objects.

        Functions are returned as :class:`MatlabFunction` objects.

        """
        m = self.interface
        # if it's a property, just retrieve it
        if name in m.call('properties', [self.handle], nargout=1):
            return m.call('subsref', [self.handle, m.call('substruct', ['.', name])])
        # if it's a method, wrap it in a functor
        if name in m.call('methods', [self.handle], nargout=1):
            class matlab_method:
                def __call__(_self, *args, **kwargs):
                    nargout = kwargs.pop('nargout') if 'nargout' in kwargs.keys() else -1
                    # serialize keyword arguments:
                    args += sum(kwargs.items(), ())
                    return getattr(m, name)(self, *args, nargout=nargout)

                # only fetch documentation when it is actually needed:
                @property
                def __doc__(_self):
                    classname = getattr(m, 'class')(self)
                    return m.call('help', ['{0}.{1}'.format(classname, name)], nargout=1)

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
        html_str = self.interface.call('eval', ["@(x) evalc('disp(x)')"])
        html_str = self.interface.call(html_str, [self.handle])
        return re.sub('</?a[^>]*>', '', html_str)

    @property
    def __doc__(self):
        out = StringIO()
        return self.interface.call('help', [self.handle], nargout=1, stdout=out)

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
