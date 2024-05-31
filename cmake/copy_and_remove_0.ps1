Get-ChildItem "$($args[0])" -recurse | where-object {$_.length -eq 0} | ?{Remove-Item $_.fullname}
Get-ChildItem "$($args[0])" -recurse | where-object {$_.Name -match "_docify"} | ?{Remove-Item $_.fullname -recurse}
Get-ChildItem "$($args[0])" -recurse | where-object {($_.Name -match "@*_old") -and ($_.GetType().Name -eq "DirectoryInfo")} | ?{Remove-Item $_.fullname -recurse}
Get-ChildItem "$($args[0])" -recurse | where-object {($_.Name -match "@testsigvar") -and ($_.GetType().Name -eq "DirectoryInfo")} | ?{Remove-Item $_.fullname -recurse}
Get-ChildItem "$($args[0])" -recurse | where-object {$_.Name -match "compute_bin_data_mex_.m"} | ?{Remove-Item $_.fullname -recurse}
