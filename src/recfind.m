function in = recfind(in)

uncell = false;
if ~iscell(in)
    in = {in};
    uncell = true;
end

for i = 1:length(in)
    if iscell(in{i})
        in{i} = recfind(in{i});
    elseif isstruct(in{i})
        f = fieldnames(in{i});
        for k = 1:length(f)
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
end

if uncell
    in = in{1};
end