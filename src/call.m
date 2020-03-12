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

if resultsize > 0
    % call the function with the given number of
    % output arguments:
    results = cell(resultsize, 1);
    [results{:}] = feval(name, args{:});
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
    feval(name, args{:})
    try
        results = {ans};
    catch err
        results = {[]};
    end
    out = results{1};
end
end
