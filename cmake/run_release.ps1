function Write-and-Invoke([string]$command) {
    Write-Output "+ $command"
    Invoke-Expression "$command"
}

$conda_root_dir = "$($reg.'(default)')"
#Try {
#    $reg = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Python\ContinuumAnalytics\Anaconda39-64\InstallPath"
#} Catch [System.Management.Automation.ItemNotFoundException] {
#    Write-Error("Could not find Anaconda key in registry")
#}
$conda_root_dir = "$($reg.'(default)')"
$conda_env_dir = "$conda_root_dir\envs\pace_neutrons"

$Env:CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
$Env:_CE_M = ""
$Env:_CE_CONDA = ""
$Env:_CONDA_ROOT = "$conda_root_dir"
$Env:_CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
Import-Module "$Env:_CONDA_ROOT\shell\condabin\Conda.psm1"

# Hard code to use R2020b as it is the mininum version needed for python 3.8
Try {
    $MATLAB_REG = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Mathworks\MATLAB\9.9" -ErrorAction Stop
    $MATLAB_EXE = $MATLAB_REG.MATLABROOT + "\bin\matlab.exe"
} Catch {
    Write-Output "Could not find Matlab R2020b folder. Using default Matlab"
    $MATLAB_EXE = "matlab.exe"
}

$mstr = "try, cd('installer'), run('make_package.m'), catch ME, fprintf('%s: %s\n', ME.identifier, ME.message), end, exit"
Write-and-Invoke "& `'$MATLAB_EXE`' -nosplash -nodesktop -wait -r `"$mstr`""

Write-and-Invoke "Enter-CondaEnvironment pace_neutrons"
Write-and-Invoke "python -m pip install requests pyyaml"
Write-and-Invoke "python release.py --github --notest"
