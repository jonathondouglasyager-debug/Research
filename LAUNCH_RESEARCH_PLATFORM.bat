@echo off
REM Research Intelligence Platform Launcher
REM Opens agent monitor dashboard in default browser

cd /d "%~dp0"

echo.
echo ========================================
echo  RESEARCH INTELLIGENCE PLATFORM
echo ========================================
echo.
echo Opening Agent Monitor Dashboard...
echo.

REM Open dashboard in default browser
start "" "Tools_and_Systems\Master_Research_Hub\agent_monitor_dashboard.html"

echo.
echo Dashboard opened in your browser!
echo.
echo Quick Commands:
echo   - Process document:
echo     python _System\agent_manager.py process --document "path\to\file.md" --investigation "Investigation_Name"
echo.
echo   - Run integration:
echo     python _System\integration_controller.py run
echo.
echo   - Auto-monitor (continuous):
echo     python _System\integration_controller.py monitor
echo.
echo Press any key to close this window...
pause > nul
