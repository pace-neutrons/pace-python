function [n, undetermined] = getArgOut(name, parent)

undertermined = false;
if isstring(name)
    fun = str2func(name);
    try
        n = nargout(fun);
    catch % nargout fails if fun is a method:
        try
            n = nargout(name);
        catch
            n = 1;
            undetermined = true;
        end
    end
else
    n = 1;
    undetermined = true;
end

end
