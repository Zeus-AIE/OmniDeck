@echo off
title Legion FPS Monitor (Administrator Mode)
cd /d "%~dp0"

:: 1. Check if running with Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo =======================================================
    echo  Legion Performance Monitor PRO
    echo  Yeu cau quyen Administrator de doc WMI ACPI Fan Sensor...
    echo =======================================================
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~dp0.venv\Scripts\pythonw.exe' -ArgumentList '\"%~dp0src\app_modern.py\"' -WorkingDirectory '%~dp0' -Verb RunAs"
    exit /b
)

:: 2. Already elevated - launch app directly
cd /d "%~dp0"
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0src\app_modern.py"
exit
