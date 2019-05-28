class MatlabProxyObject(object):
    def __init__(self, parent, pxObject):
        self._parent = parent
        self._pxObject = pxObject

        for method in self.__getMethods__():
            print('Method {} set'.format(method))

        for param in self.__getParams__self():
            print('Method {} set'.format(param))

    def __call__(self, *args, **kwargs):
        print('The method has been called')

    def __getattr__(self, key):
        # Only called when not found. Else __getAttribute__ called.
        if key in self.__getParams__self():
            r = self._parent.interface.feval('get', self._pxObject, key)
            return self.decode(r)

    def __setattr__(self, key, value):
        if key in self.__getParams__self():
            value = self.encode(value)
            self._parent.interface.feval('set', self._pxObject, key, value)

    def __getParams__self(self):
        return []

    def __getMethods__(self):
        return []

    def encode(self, value):
        raise NotImplementedError

    def decode(self, value):
        raise NotImplementedError
