function varargout = call_function_m(varargin)
    % Convert row vectors to column vectors for better conversion to numpy
    for ii = 1:numel(varargin)
        if size(varargin{ii}, 1) == 1
            varargin{ii} = varargin{ii}';
        end
    end
    fun_name = varargin{1};
    [kw_args, remaining_args] = get_kw_args(varargin(2:end));
    if ~isempty(kw_args)
        remaining_args = [remaining_args {struct('pyHorace_pyKwArgs', 1, kw_args{:})}];
    end
    varargout = call_python(fun_name, remaining_args{:});
    if ~iscell(varargout)
        varargout = {varargout};
    end
end

function [kw_args, remaining_args] = get_kw_args(args)
    % Finds the keyword arguments (string, val) pairs, assuming that they always at the end (last 2n items)
    first_kwarg_id = numel(args) + 1;
    for ii = (numel(args)-1):-2:1
        if ischar(args{ii}); args{ii} = string(args{ii}(:)'); end
        if isstring(args{ii}) && ...
            strcmp(regexp(args{ii}, '^[A-Za-z_][A-Za-z0-9_]*', 'match'), args{ii})
            % Python identifiers must start with a letter or _ and can contain charaters, numbers or _
            first_kwarg_id = ii;
        else
            break;
        end
    end
    if first_kwarg_id < numel(args)
        kw_args = args(first_kwarg_id:end);
        remaining_args = args(1:(first_kwarg_id-1));
    else
        kw_args = {};
        remaining_args = args;
    end
end
