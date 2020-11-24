function out = wrap_obj(obj)
% Wraps a given (old style) object in a thin wrapper so it does not get converted
% to a dict when transfered to Python.
%
% For a true struct (not old style class), it will keep it a struct but wrap any
% fields which are old-style classes (e.g. struct returned by multifit)
    if isstruct(obj)
        fn = fieldnames(obj);
        for ifn = 1:numel(fn)
            memb = obj.(fn{ifn});
            if (isempty(metaclass(memb)) && ~isjava(memb)) || has_thin_members(memb)
                out.(fn{ifn}) = thinwrapper(memb);
            else
                out.(fn{ifn}) = memb;
            end
        end
    else
        out = thinwrapper(obj);
    end
end
