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
        [results{:}] = feval(name, obj, args{:});
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