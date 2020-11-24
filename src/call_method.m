function [out, varargout] = call_method(name, obj, args)

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
if nargin == 2
    args = {};
end

if isempty(obj) && (numel(args) > 0 && strcmp(class(args{1}), 'thinwrapper'))
    obj = args{1};
    if numel(args) == 1
        args = {}; 
    else 
        args = args(2:end);
    end
end

% If the object or any arguments are a thinwrapper it means its an old-style class
% The wrapper is to basically put into the global Matlab namespace
% and to export only the variable name (as a string) to Python.
% So we have to push all input variables into the global namespace
% and evaluate the function there rather than in this local namespace.
is_thin = false;
try
    evalstr = sprintf('%s(', name);
catch
    evalstr = [];
end
if numel(evalstr) > 0
    assargs = {};
    assobj = false;
    if ~isempty(obj)
        if numel(args) > 0; comma = ','; else; comma = ''; end
        if strcmp(class(obj), 'thinwrapper')
            evalstr = sprintf('%s%s%s ', evalstr, obj.ObjectString, comma);
            is_thin = true;
        else
            evalstr = sprintf('%s arg%d%s ', evalstr, 0, comma);
            assobj = true;
        end
    end
    for ir = 1:numel(args)
        if ir > 1; comma = ','; else; comma = ''; end;
        %disp(args{ir})
        if strcmp(class(args{ir}), 'thinwrapper')
            evalstr = sprintf('%s%s %s', evalstr, comma, args{ir}.ObjectString);
            assargs{ir} = [];
            is_thin = true;
        else
            if strcmp(class(args{ir}), 'pythonFunctionWrapper')
                args{ir} = @(varargin) call_python_m(args{ir}.func_uuid, varargin{:});
            end
            evalstr = sprintf('%s%s arg%d', evalstr, comma, ir);
            assargs{ir} = sprintf('arg%d', ir);
        end
    end
end
if is_thin && (strcmp(name, 'class'))
    is_thin = false;
end
if is_thin
    for ir = 1:numel(args)
        if ~isempty(assargs{ir})
            assignin('base', assargs{ir}, args{ir});
        end
    end
    if assobj
        assignin('base', 'arg0', obj);
    end
    evalstr = [evalstr ')'];
end

if resultsize > 0
    % call the function with the given number of
    % output arguments:
    results = cell(resultsize, 1);
    has_failed = false;
    if is_thin
        try
            [results{:}] = evalin('base', evalstr);
        catch err
            %disp(err)
            has_failed = true;
        end
    end
    if ~is_thin || has_failed
        try
            if isempty(obj)
                [results{:}] = feval(name, args{:});
            else
                [results{:}] = feval(name, obj, args{:});
            end
        catch err
            if (strcmp(err.identifier,'MATLAB:unassignedOutputs'))
                results = {[]};
            else
                rethrow(err);
            end
        end
    end
    % Checks if any output is an old-style class, if so wrap it a new
    % style class so it doesn't get converted to Python dict on return.
    for ir = 1:numel(results)
        if (isempty(metaclass(results{ir})) && ~isjava(results{ir})) || has_thin_members(results{ir})
            results{ir} = wrap_obj(results{ir});
        end
    end
    out = results{1};
    if length(results) > 1
        varargout = results(2:end);
    end
else
    % try to get output from ans:
    if is_thin
        evalin('base', evalstr);
        try
            results = evalin('base', 'ans');
        catch err
            results = {[]};
        end
    else
        clear('ans');
        if isempty(obj)
            feval(name, args{:});
        else
            feval(name, obj, args{:});
        end
        try
            results = {ans};
        catch err
            results = {[]};
        end
    end
    out = results{1};
end

% Remove all non mapable reults
results = recfind(results);

end
