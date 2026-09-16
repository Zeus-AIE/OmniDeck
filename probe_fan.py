import os
import subprocess
import time

ps_code = """
try {
    $inst = Get-CimInstance -Namespace root\\wmi -ClassName LENOVO_FAN_METHOD -ErrorAction Stop
    $fan0 = $inst | Invoke-CimMethod -MethodName Fan_GetCurrentFanSpeed -Arguments @{ FanID = [byte]0 }
    $fan1 = $inst | Invoke-CimMethod -MethodName Fan_GetCurrentFanSpeed -Arguments @{ FanID = [byte]1 }
    $out = "CPU_FAN=" + $fan0.CurrentFanSpeed + "`nGPU_FAN=" + $fan1.CurrentFanSpeed
    Set-Content -Path "C:\\Users\\ADMIN\\.gemini\\antigravity\\scratch\\legion_fps_monitor\\fan_output.txt" -Value $out
} catch {
    Set-Content -Path "C:\\Users\\ADMIN\\.gemini\\antigravity\\scratch\\legion_fps_monitor\\fan_output.txt" -Value ("ERROR: " + $_.Exception.Message)
}
"""
with open("fan_query.ps1", "w", encoding="utf-8") as f:
    f.write(ps_code)

print("Running fan_query.ps1 as current user...")
res = subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "fan_query.ps1"], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)

if os.path.exists("fan_output.txt"):
    with open("fan_output.txt", "r", encoding="utf-8") as f:
        print("OUTPUT FILE:", f.read())
