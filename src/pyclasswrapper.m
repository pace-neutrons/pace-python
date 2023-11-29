classdef pyclasswrapper < handle
    properties
        pyObjectString
    end
    properties(Access=protected)
        overrides = {'pyObjectString'};
    end
    methods
        function delete(obj)
            if ~isempty(obj.pyObjectString)
                try %#ok<TRYNC>
                    call('_call_python', 'remove_object', obj.pyObjectString);
                end
            end
        end
        function varargout = subsref(obj, s)
            switch s(1).type
                case '.'
                    if any(cellfun(@(c) strcmp(s(1).subs, c), obj.overrides))
                        if numel(s) > 1 && strcmp(s(2).type, '()')
                            [varargout{1:nargout}] = obj.(s(1).subs)(s(2).subs{:});
                        else
                            varargout = obj.(s(1).subs);
                        end
                    elseif numel(s) == 1
                        varargout = call('_call_python', 'get_obj_prop', obj.pyObjectString, s(1).subs);
                    elseif s(2).type == '()'
                        varargout = call('_call_python', 'call_obj_method', obj.pyObjectString, s(1).subs, s(2).subs{:});
                    else 
                        error('Python class wrapper only supports calling direct methods');
                    end
                otherwise
                    error('Python class wrapper does support calling or cell indexing');
            end
            if ~iscell(varargout)
                varargout = {varargout};
            end
        end
    end
end
