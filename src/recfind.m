function in = recfind(in)

blacklist = {'spinw'};

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
            for j = 1:length(blacklist)
                if isa(in{i}.(f{k}),blacklist{j})
                    in{i}.(f{k}) = -1;
                end
            end
        end
    end
end

if uncell
    in = in{1};
end