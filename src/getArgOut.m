function n = getArgOut(name, parent)

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
end

