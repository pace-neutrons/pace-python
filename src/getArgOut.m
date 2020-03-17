function n = getArgOut(name, parent)

if isstring(name)
    fun = str2func(name);
    try
        n = nargout(fun);
    catch % nargout fails if fun is a method:
        try
            n = nargout(name);
        catch
            n = 1;
        end
    end
else
    n = 1;
end

end
