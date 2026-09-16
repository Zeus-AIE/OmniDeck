@echo off
title Legion FPS Monitor (Admin Debug Console)
cd /d "%~dp0"

:: 1. Check if running with Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo =======================================================
    echo  Legion Performance Monitor PRO (Debug Console)
    echo  Yeu cau quyen Administrator...
    echo =======================================================
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k \"\"%~dp0.venv\Scripts\python.exe\" \"%~dp0src\app_modern.py\"\"' -WorkingDirectory '%~dp0' -Verb RunAs"
    exit /b
)

:: 2. Already elevated - run directly with pause on exit
cd /d "%~dp0"
echo =======================================================
echo  Legion Performance Monitor PRO - Admin Debug Console
echo  Dang chay duoi quyen Administrator...
echo =======================================================
set LEGION_DEBUG=1
"%~dp0.venv\Scripts\python.exe" "%~dp0src\app_modern.py"
pause
