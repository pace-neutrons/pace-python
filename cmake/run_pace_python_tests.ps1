function Write-and-Invoke([string]$command) {
    Write-Output "+ $command"
    Invoke-Expression "$command"
}

$conda_root_dir = "C:\programming\miniconda3"
#Try {
#    $reg = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Python\ContinuumAnalytics\Anaconda39-64\InstallPath"
#    $conda_root_dir = "$($reg.'(default)')"
#} Catch [System.Management.Automation.ItemNotFoundException] {
#    Write-Error("Could not find Anaconda key in registry")
#}
$conda_env_dir = "$conda_root_dir\envs\pace_neutrons"

$Env:CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
$Env:_CE_M = ""
$Env:_CE_CONDA = ""
$Env:_CONDA_ROOT = "$conda_root_dir"
$Env:_CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
Import-Module "$Env:_CONDA_ROOT\shell\condabin\Conda.psm1"

Write-and-Invoke "conda activate pace_neutrons"

$wheels = Get-ChildItem dist -Filter *cp37*.whl
Write-and-Invoke "python -m pip install .\dist\$($wheels[-1].Name)"

# Hard code to use R2020b as it is the mininum version needed for python 3.8
Try {
    $MATLAB_REG = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Mathworks\MATLAB\9.9" -ErrorAction Stop
    $MATLAB_EXE = $MATLAB_REG.MATLABROOT + "\bin\matlab.exe"
} Catch {
    Write-Output "Could not find Matlab R2020b folder. Using default Matlab"
    $MATLAB_EXE = "matlab.exe"
}

Try {
    Write-and-Invoke "python test/run_test.py"
} Catch {
    Write-and-Invoke "python test/run_test.py"
}
