@echo off
title Legion FPS Monitor
cd /d "%~dp0"
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0src\app_modern.py"
exit
