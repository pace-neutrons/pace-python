function Write-and-Invoke([string]$command) {
    Write-Output "+ $command"
    Invoke-Expression "$command"
}

# Invokes a Cmd.exe shell script and updates the environment.
function Invoke-CmdScript {
  param(
    [String] $scriptName
  )
  $cmdLine = """$scriptName"" $args & set"
  & $Env:SystemRoot\system32\cmd.exe /c $cmdLine |
  select-string '^([^=]*)=(.*)$' | foreach-object {
    $varName = $_.Matches[0].Groups[1].Value
    $varValue = $_.Matches[0].Groups[2].Value
    set-item Env:$varName $varValue
  }
}

Try {
    python -m pip uninstall scipy numpy spglib pillow kiwisolver matplotlib seekpath pint -y
} Catch {
    Write-Error("Could not uninstall base python packages")
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

Write-and-Invoke "conda env remove -n pace_neutrons -y"

Try {
    Write-and-Invoke "Remove-Item -Force -Recurse -Path $conda_env_dir"
} Catch {
    Write-Output "Could not remove '$conda_env_dir'`n$($_.Exception)"
}

Write-and-Invoke "conda create -n pace_neutrons -c conda-forge python=3.7 -y"
Write-and-Invoke "Enter-CondaEnvironment pace_neutrons"
Write-and-Invoke "python -m pip install --upgrade pip"
Write-and-Invoke "python -m pip install numpy scipy matplotlib"
Invoke-CmdScript "$Env:VS2019_VCVARSALL" x86_amd64
Write-and-Invoke "python -m pip install --force-reinstall euphonic brille"

# Hard code to use R2020a as it is the mininum version needed for pace_neutrons
Try {
    $MATLAB_REG = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Mathworks\MATLAB\9.8" -ErrorAction Stop
    $Env:MATLAB_DIR = $MATLAB_REG.MATLABROOT
} Catch {
    Write-Output "Could not find Matlab R2020a folder. Using default Matlab"
}

Write-and-Invoke "python setup.py bdist_wheel"
