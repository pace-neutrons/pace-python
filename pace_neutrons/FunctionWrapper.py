import uuid
import numpy as np
import libpymcr

_globalObjectsDict = {}

def remove_object(object_string):
    _globalObjectsDict.pop(object_string, None)

def get_obj_prop(object_string, prop_name):
    return getattr(_globalObjectsDict[object_string], prop_name)

def call_obj_method(object_string, method_name, *args, **kwargs):
    return getattr(_globalObjectsDict[object_string], method_name)(*args, **kwargs)

libpymcr._globalFunctionDict['remove_object'] = remove_object
libpymcr._globalFunctionDict['get_obj_prop'] = get_obj_prop
libpymcr._globalFunctionDict['call_obj_method'] = call_obj_method


class WrappedPythonClass(object):
    def __init__(self, input_class, typename='pyobj'):
        self.target_class = input_class
        self.typename = typename

    def __call__(self, *args, **kwargs):
        args = [_globalObjectsDict[arg] if (isinstance(arg, str) and arg.startswith('pyobj')) else arg for arg in args]
        kwargs = {ky:(_globalObjectsDict[val] if (isinstance(val, str) and val.startswith('pyobj')) else val) for ky, val in kwargs.items()}
        input_object = self.target_class(*args, **kwargs)
        obj_uuid = str(uuid.uuid4())
        key_string = self.typename + obj_uuid
        _globalObjectsDict[key_string] = input_object
        return key_string

try:
    from brille.utils import create_bz, create_grid
except ImportError:
    pass
else:
    wrapped_create_bz = WrappedPythonClass(create_bz, 'pyobj_bz')
    wrapped_create_grid = WrappedPythonClass(create_grid, 'pyobj_grid')
    libpymcr._globalFunctionDict['create_bz'] = wrapped_create_bz
    libpymcr._globalFunctionDict['create_grid'] = wrapped_create_grid
    def brille_grid_fill(objstr, *args):
        # We have to do the reshape here because Matlab swallows singleton dims
        args = list(args)
        for idx in ([0, 2, 3, 5] if len(args) > 5 else [0, 2]):
            shp = np.shape(args[idx])
            if len(shp) < 3:
                args[idx] = np.reshape(args[idx], (shp[0], shp[1], 1))
        for idx in ([1, 4] if len(args) > 5 else [1, 3]):
            args[idx] = np.reshape(args[idx], (np.prod(np.shape(args[idx])),)).astype('int32')
        if len(args) % 2 == 1:
            args[-1] = args[-1][0]
        return getattr(_globalObjectsDict[objstr], 'fill')(*args)
    libpymcr._globalFunctionDict['brille_grid_fill'] = brille_grid_fill
    def brille_ir_interpolate_at(objstr, *args):
        # Again we can't transpose in Matlab because brille needs a C-style array
        hkl = args[0] if np.shape(args[0])[1] == 3 else np.transpose(args[0])
        kwargs = {args[idx]:args[idx+1] for idx in range(1, len(args), 2)} if len(args) > 1 else {}
        return getattr(_globalObjectsDict[objstr], 'ir_interpolate_at')(hkl, **kwargs)
    libpymcr._globalFunctionDict['brille_ir_interpolate_at'] = brille_ir_interpolate_at
