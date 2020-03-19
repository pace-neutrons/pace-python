import uuid

_globalFunctionDict = {}


def pymatpy(func, interface):
    func_uuid = str(uuid.uuid4())
    _globalFunctionDict[func_uuid] = func
    return interface.call('pythonFunctionWrapper', [func_uuid])
