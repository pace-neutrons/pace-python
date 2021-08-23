function Write-and-Invoke([string]$command) {
    Write-Output "+ $command"
    Invoke-Expression "$command"
}

Try {
    $reg = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Python\ContinuumAnalytics\Anaconda39-64\InstallPath"
} Catch [System.Management.Automation.ItemNotFoundException] {
    Write-Error("Could not find Anaconda key in registry")
}
$conda_root_dir = "$($reg.'(default)')"
$conda_env_dir = "$conda_root_dir\envs\pace_python"

$Env:CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
$Env:_CE_M = ""
$Env:_CE_CONDA = ""
$Env:_CONDA_ROOT = "$conda_root_dir"
$Env:_CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
Import-Module "$Env:_CONDA_ROOT\shell\condabin\Conda.psm1"

Write-and-Invoke "Enter-CondaEnvironment pace_python"

$wheels = Get-ChildItem dist -Filter *.whl
Write-and-Invoke "python -m pip install .\dist\$($wheels[-1].Name)"

# Hard code to use R2020a as it is the mininum version needed for pace_python
Try {
    $MATLAB_REG = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Mathworks\MATLAB\9.8" -ErrorAction Stop
    $Env:Path += ";$($MATLAB_REG.MATLABROOT)\runtime\win64"
} Catch {
    Write-Output "Could not find Matlab R2020a folder. Will guess Matlab."
}

Write-and-Invoke "python test/run_test.py"
