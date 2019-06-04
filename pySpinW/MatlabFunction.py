
class MatlabFunction(object):

    def __init__(self, interface, converter, parent, fun):
        '''

        Create a proxt function to handle matlab calls

        :param interface:
        :param parent:
        :param fun:
        '''
        self._interface = interface
        self.converter = converter
        self._parent = parent
        self._fun = fun

    def __call__(self, *args, nargout=-1, **kwargs):
        """Call the Matlab function.

        Calling this function will transfer all function arguments
        from Python to Matlab, and translate them to the appropriate
        Matlab data structures.

        Return values are translated the same way, and transferred
        back to Python.

        Parameters
        ----------
        nargout : int
            Call the function in Matlab with this many output
            arguments. If the argument not given, we will try and work
            out the corrent value.
        **kwargs : dict
            Keyword arguments are transparently translated to Matlab's
            key-value pairs. For example, ``matlab.struct(foo="bar")``
            will be translated to ``struct('foo', 'bar')``.

        """
        # serialize keyword arguments:
        args += sum(kwargs.items(), ())
        args = self.converter.encode(args)

        # Determination of the number of output arguments is a pain.
        # Push it here instead of the main matlab call function.

        nargout = int(self._interface.getArgOut(self._fun, nargout=1))

        if args:
            if nargout > 0:
                d = self._interface.call2(self._fun, self._parent, args, nargout=nargout)
            else:
                self._interface.call2(self._fun, self._parent, args, nargout=nargout)
                return
        else:
            if nargout > 0:
                d = self._interface.feval(self._fun, self._parent, nargout=nargout)
            else:
                self._interface.feval(self._fun, self._parent, nargout=nargout)
                return

        ## TODO write a value decoder/encoder.
        return d
