function [out, varargout] = call2(name ,obj, args)

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

for ir = 1:numel(args) 
    if strcmp(class(args{ir}), 'pythonFunctionWrapper')
        args{ir} = @(varargin) call_python_m(args{ir}.func_uuid, varargin{:});
    end
end

if resultsize > 0
    % call the function with the given number of
    % output arguments:
    results = cell(resultsize, 1);
    if isempty(obj) && (numel(args) > 0 && strcmp(class(args{1}), 'thinwrapper'))
        obj = args{1};
        if numel(args) == 1
            args = {}; 
        else 
            args = args(2:end);
        end
    end
    if isempty(obj)
        [results{:}] = feval(name, args{:});
    else
        % If one the input is a thinwrapper it means its an old-style class
        % The wrapper is to basically put into the global Matlab namespace
        % and to export only the variable name (as a string) to Python.
        % So we have to push all input variables into the global namespace
        % and evaluate the function there rather than in this local namespace.
        if strcmp(class(obj), 'thinwrapper')
            evalstr = sprintf('%s(%s', name, obj.ObjectString);
            for iar = 1:numel(args)
                assignin('base', sprintf('arg%d', iar), args{iar});
                evalstr = sprintf('%s, arg%d', evalstr, iar);
            end
            evalstr = [evalstr ')'];
            [results{:}] = evalin('base', evalstr);
        else
            [results{:}] = feval(name, obj, args{:});
        end
    end
    % Checks if any output is an old-style class, if so wrap it a new
    % style class so it doesn't get converted to Python dict on return.
    for ir = 1:numel(results)
        if isempty(metaclass(results{ir})) && ~isjava(results{ir})
            results{ir} = thinwrapper(results{ir});
        end
    end
    out = results{1};
    if length(results) > 1
        varargout = results(2:end);
    end
else
    % try to get output from ans:
    clear('ans');
    if isempty(obj)
        feval(name, args{:})
    else
        if strcmp(class(obj), 'thinwrapper')
            evalstr = sprintf('%s(%s', name, obj.ObjectString);
            for iar = 1:numel(args)
                assignin('base', sprintf('arg%d', iar), args{iar});
                evalstr = sprintf('%s, arg%d', evalstr, iar);
            end
            evalstr = [evalstr ')'];
            evalin('base', evalstr);
        else
            feval(name, obj, args{:});
        end
    end
    try
        results = {ans};
    catch err
        results = {[]};
    end
    out = results{1};
end

% Remove all non mapable reults
results = recfind(results);

end
