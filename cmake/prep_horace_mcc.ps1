robocopy "$($args[0])\Horace\horace_core" "$($args[1])\Horace" /s
Get-ChildItem "$($args[1])\Horace" -recurse | where-object {$_.length -eq 0} | ?{Remove-Item $_.fullname}
Get-ChildItem "$($args[1])\Horace" -recurse | where-object {$_.Name -match "_docify"} | ?{Remove-Item $_.fullname -recurse}

robocopy "$($args[0])\Herbert\herbert_core" "$($args[1])\Herbert" /s
Get-ChildItem "$($args[1])\Herbert" -recurse | where-object {$_.length -eq 0} | ?{Remove-Item $_.fullname}
Get-ChildItem "$($args[1])\Herbert" -recurse | where-object {$_.Name -match "_docify"} | ?{Remove-Item $_.fullname -recurse}

Remove-Item "$($args[1])\Herbert\applications\docify" -recurse
