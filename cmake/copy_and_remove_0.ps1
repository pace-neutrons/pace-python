robocopy "$($args[0])" "$($args[1])" /s
Get-ChildItem "$($args[1])" -recurse | where-object {$_.length -eq 0} | ?{Remove-Item $_.fullname}
Get-ChildItem "$($args[1])" -recurse | where-object {$_.Name -match "_docify"} | ?{Remove-Item $_.fullname -recurse}
Get-ChildItem "$($args[1])" -recurse | where-object {($_.Name -match "@*_old") -and ($_.GetType().Name -eq "DirectoryInfo")} | ?{Remove-Item $_.fullname -recurse}
