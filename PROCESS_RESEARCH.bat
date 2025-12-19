@echo off
REM Quick Research Processing Launcher
REM Auto-detects latest file and runs complete workflow

cd /d "%~dp0"

echo.
echo ========================================
echo  RESEARCH INTELLIGENCE PLATFORM
echo  Auto Process - Complete Workflow
echo ========================================
echo.

python _Automation\auto_process.py

echo.
echo Press any key to close...
pause > nul
