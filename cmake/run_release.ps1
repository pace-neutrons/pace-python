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
$conda_env_dir = "$conda_root_dir\envs\pace_neutrons"

$Env:CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
$Env:_CE_M = ""
$Env:_CE_CONDA = ""
$Env:_CONDA_ROOT = "$conda_root_dir"
$Env:_CONDA_EXE = "$conda_root_dir\Scripts\conda.exe"
Import-Module "$Env:_CONDA_ROOT\shell\condabin\Conda.psm1"

Write-and-Invoke "matlab -nodesktop -r \"try, cd('installer'), run('make_package.m'), catch ME, fprintf('%s: %s\n', ME.identifier, ME.message), end, exit\""
Write-and-Invoke "Enter-CondaEnvironment pace_neutrons"
Write-and-Invoke "python -m pip install requests pyyaml"
Write-and-Invoke "python release.py --github --notest"
