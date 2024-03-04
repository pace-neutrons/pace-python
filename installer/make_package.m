% Needs R2020a or newer
if ispc
    mcc -e pace_neutrons_installer.m
    execname = 'pace_neutrons_installer.exe';
else
    mcc -m pace_neutrons_installer.m
    execname = 'pace_neutrons_installer';
end
% Make sure we install the required products:
% 35000=Core, 35010=Numerics, 35055=Python, 35180=Parallel Toolbox
% Installer only has 35000 and 35010
fid = fopen('requiredMCRProducts.txt', 'w');
fprintf(fid, '35000	35010	35180	35055\n');
fclose(fid);
compiler.package.installer(execname, 'requiredMCRProducts.txt', 'ApplicationName', 'pace_python_')
