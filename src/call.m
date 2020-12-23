function [out, varargout] = call(name, args)

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
end

% Checks if any arguments are thinwrappers - if they are, we have to
% to push all input variables into the global namespace and evaluate the function 
% there rather than in this local namespace, because the real object behind the
% thinwrapper is only in the global namespace.
is_thin = false;
try
    evalstr = sprintf('%s(', name);
catch
    evalstr = [];
end
if numel(evalstr) > 0
    assargs = {};
    for ir = 1:numel(args) 
        if ir > 1; comma = ','; else comma = ''; end;
        if strcmp(class(args{ir}), 'thinwrapper')
            evalstr = sprintf('%s%s %s', evalstr, comma, args{ir}.ObjectString);
            assargs{ir} = [];
            is_thin = true;
        else
            args{ir} = check_wrapped_function(args{ir});
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
    evalstr = [evalstr ')'];
end

if resultsize > 0
    % call the function with the given number of
    % output arguments:
    results = cell(resultsize, 1);
    try
        if is_thin
            try
                [results{:}] = evalin('base', evalstr);
            catch err
                %disp(err);
                [results{:}] = feval(name,  args{:});
            end
        else
            [results{:}] = feval(name,  args{:});
        end
    catch err
        if (strcmp(err.identifier,'MATLAB:unassignedOutputs'))
            results = {[]};
        else
            rethrow(err);
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
    clear('ans');
    if is_thin
        evalin('base', evalstr);
        try
            results = evalin('base', 'ans');
        catch err
            results = {[]};
        end
    else
        feval(name, args{:});
        try
            results = {ans};
        catch err
            results = {[]};
        end
    end
    out = results{1};
end
end
