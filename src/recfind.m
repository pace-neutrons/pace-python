function in = recfind(in)

uncell = false;
if ~iscell(in)
    in = {in};
    uncell = true;
end

% Unsupported MATLAB types in Python (as of R2020b) 
% https://www.mathworks.com/help/matlab/matlab_external/limitations-to-python-support.html
%   Multidimensional char or cell arrays [Ok, gives error message, no crash]
%   Structure arrays
%   Complex, scalar integers or arrays  [Ok, will wrap it]
%   Sparse arrays 
%   categorical, table, containers.Map, datetime types
%   MATLAB objects
%   meta.class (py.class)

for i = 1:numel(in)
    class_i = class(in{i});
    if iscell(in{i})
        in{i} = recfind(in{i});
    elseif isstruct(in{i})
        if numel(in{i}) > 1
            % Structure array, convert to cell of structures (auto convert to list)
            outcell = {};
            for n = 1:numel(in{i})
                outcell{n} = recfind(in(i));
            end
            in{i} = outcell;
        else
            f = fieldnames(in{i});
            for k = 1:numel(f)
                if isobject(in{i}.(f{k}))
                    UUID = char(randsample([65:74 97:106], 32, true));
                    set_global(UUID, in{i}.(f{k}))
                    in{i}.(f{k}) = sprintf('!$%s',UUID);
                elseif isstruct(in{i}.(f{k}))
                    in{i}.(f{k}) = recfind(in{i}.(f{k}));
                elseif iscell(in{i}.(f{k}))
                    in{i}.(f{k}) = recfind(in{i}.(f{k}));
                end
            end
        end
    elseif strncmp(class_i, 'matlab', 6) || ...  % Matlab object
           strcmp(class_i, 'categorical') || strcmp(class_i, 'table') || ...
           strcmp(class_i, 'containers.Map') || strcmp(class_i, 'datetime') || ...
           strcmp(class_i, 'meta.class') || ...
           strncmp(class_i, 'py.', 3) || ...
           issparse(in{i})
        in{i} = thinwrapper(in{i});
    end
end

if uncell
    in = in{1};
end
