classdef pythonFunctionWrapper < handle
    properties
        func_ptr
        converter
    end
    methods
        % Constructor
        function obj = pythonFunctionWrapper(func_ptr, converter)
            obj.func_ptr = func_ptr;
            obj.converter = converter;
        end
    end
end
