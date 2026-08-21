@echo off
setlocal
cd /d "%~dp0"

set PORT=8787
set URL=http://127.0.0.1:%PORT%

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Install Python 3 and add to PATH first.
    pause
    exit /b 1
)

netstat -ano | findstr ":%PORT%" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo Server already running at %URL%. Opening browser...
    start "" "%URL%"
    exit /b 0
)

echo Starting Agent OS Web UI at %URL% ...
echo Server console will stay open. Close it to stop the server.
start "Agent OS Web UI" cmd /k python serve_ui.py

timeout /t 2 /nobreak >nul
start "" "%URL%"
endlocal