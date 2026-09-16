
try {
    $inst = Get-CimInstance -Namespace root\wmi -ClassName LENOVO_FAN_METHOD -ErrorAction Stop
    $fan0 = $inst | Invoke-CimMethod -MethodName Fan_GetCurrentFanSpeed -Arguments @{ FanID = [byte]0 }
    $fan1 = $inst | Invoke-CimMethod -MethodName Fan_GetCurrentFanSpeed -Arguments @{ FanID = [byte]1 }
    $out = "CPU_FAN=" + $fan0.CurrentFanSpeed + "`nGPU_FAN=" + $fan1.CurrentFanSpeed
    Set-Content -Path "C:\Users\ADMIN\.gemini\antigravity\scratch\legion_fps_monitor\fan_output.txt" -Value $out
} catch {
    Set-Content -Path "C:\Users\ADMIN\.gemini\antigravity\scratch\legion_fps_monitor\fan_output.txt" -Value ("ERROR: " + $_.Exception.Message)
}
