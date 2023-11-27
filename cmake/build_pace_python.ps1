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

$conda_root_dir = "C:\programming\miniconda3"
#Try {
#    $reg = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Python\ContinuumAnalytics\Anaconda39-64\InstallPath"
#    $conda_root_dir = "$($reg.'(default)')"
#} Catch {
#    $reg = (Get-Command conda).Path
#    $conda_root_dir = Split-Path $reg | Split-Path | Split-Path
#}
Write-Host $conda_root_dir
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
Write-and-Invoke "conda activate pace_neutrons"
Write-and-Invoke "python -m pip install numpy scipy matplotlib"
Invoke-CmdScript "$Env:VS2019_VCVARSALL" x86_amd64
Write-and-Invoke "python -m pip install --force-reinstall euphonic[phonopy_reader] brille"

# Hard code to use R2020b as it is the mininum version needed for python 3.8
Try {
    $MATLAB_REG = Get-ItemProperty "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Mathworks\MATLAB\9.9" -ErrorAction Stop
    $Env:MATLAB_DIR = $MATLAB_REG.MATLABROOT
} Catch {
    Write-Output "Could not find Matlab R2020b folder. Using default Matlab"
}

Write-and-Invoke "python setup.py bdist_wheel"

# Build Python 3.8 version for Mantid
Write-and-Invoke "conda env remove -n pace_neutrons38 -y"
Try {
    Write-and-Invoke "Remove-Item -Force -Recurse -Path $conda_root_dir\envs\pace_neutrons38"
} Catch {
    Write-Output "Could not remove '$conda_root_dir\envs\pace_neutrons'`n$($_.Exception)"
}
Write-and-Invoke "conda create -n pace_neutrons38 -c conda-forge python=3.8 -y"
Write-and-Invoke "conda activate pace_neutrons38"
Write-and-Invoke "python setup.py bdist_wheel"
