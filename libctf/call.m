function [varargout] = call(name, varargin)
    if strcmp(name, '_call_python')
        varargout = call_python_m(varargin{:});
        return
    end
    resultsize = nargout;
    try
        maxresultsize = nargout(name);
        if maxresultsize == -1
            maxresultsize = resultsize;
        end
    catch
        maxresultsize = resultsize;
    end
    if resultsize > maxresultsize
        resultsize = maxresultsize;
    end
    if nargin == 1
        args = {};
    else
        args = varargin;
    end
    for ir = 1:numel(args)
        args{ir} = check_wrapped_function(args{ir});
    end
    if resultsize > 0
        % call the function with the given number of
        % output arguments:
        varargout = cell(resultsize, 1);
        try
            [varargout{:}] = feval(name, args{:});
        catch err
            if (strcmp(err.identifier,'MATLAB:unassignedOutputs'))
                varargout = eval_ans(name, args);
            else
                rethrow(err);
            end
        end
    else
        varargout = eval_ans(name, args);
    end
end

function out = check_wrapped_function(in_obj)
    out = in_obj;
    if isstruct(in_obj) && isfield(in_obj, 'func_ptr') && isfield(in_obj, 'converter')
        out = @(varargin) call('_call_python', [in_obj.func_ptr, in_obj.converter], varargin{:});
    elseif iscell(in_obj)
        for ii = 1:numel(in_obj)
            out{ii} = check_wrapped_function(in_obj{ii});
        end
    end
end

function results = eval_ans(name, args)
    % try to get output from ans:
    clear('ans');
    feval(name, args{:});
    try
        results = {ans};
    catch err
        results = {[]};
    end
end

function [n, undetermined] = getArgOut(name, parent)
    undertermined = false;
    if isstring(name)
        fun = str2func(name);
        try
            n = nargout(fun);
        catch % nargout fails if fun is a method:
            try
                n = nargout(name);
            catch
                n = 1;
                undetermined = true;
            end
        end
    else
        n = 1;
        undetermined = true;
    end
end

function out = call_python_m(varargin)
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
    out = call_python(fun_name, remaining_args{:});
    if ~iscell(out)
        out = {out};
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
