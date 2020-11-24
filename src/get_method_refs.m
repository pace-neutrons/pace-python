function out = get_method_refs(name, parent)
% Gets a reference ("function handle") to a method of a class
% Note that if the class method shadows a Matlab function name 
% (e.g. swpref.getpref) the built-in will take precedent unfortunately
    if ~isstring(name) && ~ischar(name)
        error('Method name must be string')
    end
    if nargin < 2
        out = str2func(name);
    else
        evalstr = ['@(par, varargin) ' name '(par, varargin{:})'];
        fn0 = eval(evalstr);
        out = @(varargin) fn0(parent, varargin{:});
    end
end
