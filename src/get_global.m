function value = get_global(name)
existance = evalin('base', ['exist(''' name ''')']);
% exist doesn't find methods, though.
existance = existance | any(which(name));
% value does not exist:
if ~existance
    error('pyMATLAB:novariable' , ['Undefined variable ''' name '''.']);
else
    value = evalin('base', name);
end
end