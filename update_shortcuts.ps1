$baseDir = "C:\Users\ADMIN\.gemini\antigravity\scratch\legion_fps_monitor"
$pythonw = "$baseDir\.venv\Scripts\pythonw.exe"
$appModern = "$baseDir\src\app_modern.py"
$iconPath = "$baseDir\assets\icon.ico"
$startMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"

$desktopDirs = @(
    "$HOME\Desktop",
    [System.Environment]::GetFolderPath("Desktop")
) | Select-Object -Unique | Where-Object { Test-Path $_ }

$WshShell = New-Object -ComObject WScript.Shell

foreach ($d in $desktopDirs) {
    # 1. Standard Desktop Shortcut
    $sc1 = $WshShell.CreateShortcut((Join-Path $d "Legion FPS Monitor.lnk"))
    $sc1.TargetPath = $pythonw
    $sc1.Arguments = "`"$appModern`""
    $sc1.WorkingDirectory = $baseDir
    $sc1.IconLocation = "$iconPath,0"
    $sc1.Description = "Legion Performance & Game FPS Monitor PRO"
    $sc1.Save()

    # 2. Administrator Desktop Shortcut
    $scAdmin = $WshShell.CreateShortcut((Join-Path $d "Legion FPS Monitor (Admin).lnk"))
    $scAdmin.TargetPath = "powershell.exe"
    $scAdmin.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command `"Start-Process -FilePath '$pythonw' -ArgumentList '`"`"$appModern`"`"' -WorkingDirectory '$baseDir' -Verb RunAs`""
    $scAdmin.WorkingDirectory = $baseDir
    $scAdmin.IconLocation = "$iconPath,0"
    $scAdmin.Description = "Legion Performance & Game FPS Monitor (Administrator Mode)"
    $scAdmin.WindowStyle = 7
    $scAdmin.Save()
    Write-Host "Updated shortcuts in: $d"
}

# 3. Start Menu Shortcut
$sc2 = $WshShell.CreateShortcut((Join-Path $startMenu "Legion FPS Monitor.lnk"))
$sc2.TargetPath = $pythonw
$sc2.Arguments = "`"$appModern`""
$sc2.WorkingDirectory = $baseDir
$sc2.IconLocation = "$iconPath,0"
$sc2.Description = "Legion Performance & Game FPS Monitor PRO"
$sc2.Save()
Write-Host "Updated Start Menu shortcut"

Write-Host "ALL_DESKTOP_LOCATIONS_UPDATED_SUCCESSFULLY"
