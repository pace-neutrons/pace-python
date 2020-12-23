function out = check_wrapped_function(in_obj)
    out = in_obj;
    if strcmp(class(in_obj), 'pythonFunctionWrapper')
        out = @(varargin) call_python_m(in_obj.func_uuid, varargin{:});
    elseif iscell(in_obj)
        for ii = 1:numel(in_obj)
            if strcmp(class(in_obj{ii}), 'pythonFunctionWrapper')
                out{ii} = @(varargin) call_python_m(in_obj{ii}.func_uuid, varargin{:});
            end
        end
    end
end
