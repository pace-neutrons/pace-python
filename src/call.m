function results = call(name, args)

resultsize = nargout;
if nargin == 1
    args = {};
end

if resultsize > 0
    % call the function with the given number of
    % output arguments:
    results = cell(resultsize, 1);
    [results{:}] = feval(name, args{:});
    if length(results) == 1
        results = results{1};
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
end
end