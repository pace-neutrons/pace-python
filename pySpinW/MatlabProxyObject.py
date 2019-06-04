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
        :param interface:
        :param handle:
        """
        self.__dict__['handle'] = handle
        self.__dict__['interface'] = interface
        self.__dict__['converter'] = converter

        for attribute in self._getAttributeNames():
            self.__dict__[attribute] = self.__getattr__(attribute)
        for method in self._getMethodNames():
            super(MatlabProxyObject, self).__setattr__(method, MatlabFunction(self.interface, self.converter, self.handle, method))

    def _getAttributeNames(self):
        return self.interface.fieldnames(self.interface.feval('handle', self.handle))

    def _getMethodNames(self):
        return self.interface.methods(self.interface.feval('handle', self.handle))

    def __getattr__(self, name):
        """Retrieve a value or function from the object.

        Properties are returned as native Python objects or
        :class:`MatlabProxyObject` objects.

        Functions are returned as :class:`MatlabFunction` objects.

        """
        m = self.interface
        # if it's a property, just retrieve it
        if name in m.properties(self.handle, nargout=1):
            return m.subsref(self.handle, m.substruct('.', name))
        # if it's a method, wrap it in a functor
        if name in m.methods(self.handle, nargout=1):
            class matlab_method:
                def __call__(_self, *args, nargout=-1, **kwargs):
                    # serialize keyword arguments:
                    args += sum(kwargs.items(), ())
                    return getattr(m, name)(self, *args, nargout=nargout)

                # only fetch documentation when it is actually needed:
                @property
                def __doc__(_self):
                    classname = getattr(m, 'class')(self)
                    return m.help('{0}.{1}'.format(classname, name), nargout=1)

            return matlab_method()

    def __setattr__(self, name, value):
        self.__class__[name] = value
        access = self.interface.substruct('.', name)
        self.interface.subsasgn(self, access, value)

    def __repr__(self):
        # getclass = self.interface.str2func('class')
        return "<proxy for Matlab {} object>".format(self.interface.feval('class', self.handle))

    def __str__(self):
        # remove pseudo-html tags from Matlab output
        html_str = self.interface.eval("@(x) evalc('disp(x)')")
        html_str = self.interface.feval(html_str, self.handle)
        return re.sub('</?a[^>]*>', '', html_str)

    @property
    def __doc__(self):
        return self.interface.help(self.handle, nargout=1)
