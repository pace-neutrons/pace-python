classdef pythonFunctionWrapper < handle
    properties
        func_uuid
    end
    methods
        % Constructor
        function obj = pythonFunctionWrapper(uuid)
            obj.func_uuid = char(uuid)
        end
        function delete(obj)
            pythonRemoveFuncKey(obj.func_uuid)
        end
    end
end
