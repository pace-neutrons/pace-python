import uuid

_globalFunctionDict = {}

class pymatpy(object):
    def __init__(self, func):
        self.func_uuid = str(uuid.uuid4())
        _globalFunctionDict[self.func_uuid] = func

    def __call__(self, *args, **kwargs):
        _globalFunctionDict[self.func_uuid](*args, **kwargs)

    def __del__(self):
        _globalFunction.pop(self.func_uuid)
