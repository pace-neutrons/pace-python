classdef pythonFunctionWrapper < handle
    properties
        func_uuid
    end
    methods
        % Constructor
        function obj = pythonFunctionWrapper(uuid)
            obj.func_uuid = char(uuid);
        end
        function delete(obj)
            pythonRemoveFuncKey(obj.func_uuid);
        end
        function varargout = subsref(obj, s)
            switch s(1).type
                case '()'
                    varargout = call_python_m(obj.func_uuid, s(1).subs{:});
                case '.'
                    varargout = obj.(s(1).subs);
                otherwise
                    error('Function wrapper does not cell indexing');
            end
            if ~iscell(varargout)
                varargout = {varargout};
            end
        end
    end
end
