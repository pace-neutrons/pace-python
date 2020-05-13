function out = call_function_m(varargin)

% Convert row vectors to column vectors for better conversion to numpy
for ii = 1:numel(varargin)
    if size(varargin{ii}, 1) == 1
        varargin{ii} = varargin{ii}';
    end
end
out = call_python(varargin{:});
