@echo off
title Legion FPS Monitor (Debug Console)
cd /d "%~dp0"
echo Starting Legion Performance & FPS Monitor in debug mode...
".venv\Scripts\python.exe" "src\app_modern.py"
pause
