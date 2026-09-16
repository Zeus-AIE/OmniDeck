$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath('Desktop')
$ProjDir = "C:\Users\ADMIN\.gemini\antigravity\scratch\legion_fps_monitor"
$TargetExe = "$ProjDir\.venv\Scripts\pythonw.exe"
$ScriptArg = "$ProjDir\src\app_modern.py"
$AdminBat = "$ProjDir\run_admin.bat"
$Icon = "$ProjDir\assets\icon.ico"

# 1. Standard Desktop Shortcut
$DesktopLinkPath = Join-Path $Desktop "Legion FPS Monitor.lnk"
$Shortcut = $WshShell.CreateShortcut($DesktopLinkPath)
$Shortcut.TargetPath = $TargetExe
$Shortcut.Arguments = "`"$ScriptArg`""
$Shortcut.WorkingDirectory = $ProjDir
$Shortcut.IconLocation = "$Icon,0"
$Shortcut.Description = "Legion Game FPS & Performance Monitor"
$Shortcut.Save()
Write-Host "Created Desktop Shortcut at: $DesktopLinkPath"

# 2. Administrator Desktop Shortcut
$DesktopAdminLinkPath = Join-Path $Desktop "Legion FPS Monitor (Admin).lnk"
$ShortcutAdmin = $WshShell.CreateShortcut($DesktopAdminLinkPath)
$ShortcutAdmin.TargetPath = $AdminBat
$ShortcutAdmin.WorkingDirectory = $ProjDir
$ShortcutAdmin.IconLocation = "$Icon,0"
$ShortcutAdmin.Description = "Legion Game FPS & Performance Monitor (Run as Administrator)"
$ShortcutAdmin.Save()
try {
    $bytes = [System.IO.File]::ReadAllBytes($DesktopAdminLinkPath)
    $bytes[0x15] = $bytes[0x15] -bor 0x20
    [System.IO.File]::WriteAllBytes($DesktopAdminLinkPath, $bytes)
} catch {}
Write-Host "Created Admin Desktop Shortcut at: $DesktopAdminLinkPath"

# 3. Shortcut in Project Directory
$ProjLinkPath = Join-Path $ProjDir "Legion FPS Monitor.lnk"
$Shortcut2 = $WshShell.CreateShortcut($ProjLinkPath)
$Shortcut2.TargetPath = $TargetExe
$Shortcut2.Arguments = "`"$ScriptArg`""
$Shortcut2.WorkingDirectory = $ProjDir
$Shortcut2.IconLocation = "$Icon,0"
$Shortcut2.Description = "Legion Game FPS & Performance Monitor"
$Shortcut2.Save()
Write-Host "Created Project Shortcut at: $ProjLinkPath"

# 4. Shortcut in Start Menu (Programs) for Windows Search index
$StartMenu = [Environment]::GetFolderPath('Programs')
$StartMenuLinkPath = Join-Path $StartMenu "Legion FPS Monitor.lnk"
$Shortcut3 = $WshShell.CreateShortcut($StartMenuLinkPath)
$Shortcut3.TargetPath = $TargetExe
$Shortcut3.Arguments = "`"$ScriptArg`""
$Shortcut3.WorkingDirectory = $ProjDir
$Shortcut3.IconLocation = "$Icon,0"
$Shortcut3.Description = "Legion Game FPS & Performance Monitor"
$Shortcut3.Save()
Write-Host "Created Start Menu Shortcut at: $StartMenuLinkPath"
