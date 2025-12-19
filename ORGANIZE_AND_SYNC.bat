@echo off
REM Quick launcher for Organize and Sync workflow
REM Double-click this file to organize Inbox and sync to GitHub

cd /d "%~dp0"
cd _Automation

echo.
echo ========================================
echo  RESEARCH ORGANIZE AND SYNC
echo ========================================
echo.

python organize_and_sync.py

echo.
echo Press any key to close...
pause > nul
