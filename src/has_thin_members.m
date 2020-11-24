function out = has_thin_members(obj)
% Checks whether any member of a class or struct is an old-style class
% or is already a wrapped instance of such a class
    out = false;
    if isobject(obj) || isstruct(obj)
        try
            fn = fieldnames(obj);
        catch
            return;
        end
        for ifn = 1:numel(fn)
            try
                mem = subsref(obj, struct('type', '.', 'subs', fn{ifn}));
            catch
                continue;
            end
            if strcmp(class(mem), 'thinwrapper') || ...
               (isempty(metaclass(mem)) && ~isjava(mem))
                out = true;
                break;
            end
        end
    end
end
