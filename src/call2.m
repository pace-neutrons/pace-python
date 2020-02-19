function results = call2(name ,obj, args)

resultsize = nargout;
if nargin == 2
    args = {};
end

if resultsize > 0
    % call the function with the given number of
    % output arguments:
    results = cell(resultsize, 1);
    if isempty(obj)
        [results{:}] = feval(name, args{:});
    else
        % If one the input is a thinwrapper it means its an old-style class
        % The wrapper is to basically put into the global Matlab namespace
        % and to export only the variable name (as a string) to Python.
        % So we have to push all input variables into the global namespace
        % and evaluate the function there rather than in this local namespace.
        if class(obj) == 'thinwrapper'
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
    if length(results) == 1
        results = results{1};
    end
else
    % try to get output from ans:
    clear('ans');
    if isempty(obj)
        feval(name, args{:})
    else
        feval(name, obj, args{:})
    end
    try
        results = {ans};
    catch err
        results = {[]};
    end
end

% Remove all non mapable reults
results = recfind(results);

end
