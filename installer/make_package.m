% Needs R2020a or newer
if ispc
    mcc -e pace_python_installer.m
    execname = 'pace_python_installer.exe';
else
    mcc -m pace_python_installer.m
    execname = 'pace_python_installer';
end
% Make sure we install the required products:
% 35000=Core, 35010=Numerics, 35055=Python
% Installer only has 35000 and 35010
fid = fopen('requiredMCRProducts.txt', 'w');
fprintf(fid, '35000	35010	35055\n');
fclose(fid);
compiler.package.installer(execname, 'requiredMCRProducts.txt', 'ApplicationName', 'Pace_Python_Installer')
