@echo off
title IP Logger Launcher
cd /d "%~dp0"
setlocal

for /f %%i in ('powershell -NoProfile -Command "[guid]::NewGuid().ToString()"') do set "FLASK_SECRET_KEY=%%i"

echo Installing Flask if needed...
py -m pip install flask

echo.
echo Starting IP Logger on http://127.0.0.1:5000 ...
echo.
start "IP Logger App" cmd /k "cd /d ""%~dp0"" && set FLASK_SECRET_KEY=%FLASK_SECRET_KEY% && py app.py"

timeout /t 3 /nobreak >nul

where cloudflared >nul 2>nul
if errorlevel 1 (
    echo cloudflared is not installed, so remote access is not enabled yet.
    echo.
    echo Fastest remote option:
    echo 1. Install cloudflared from Cloudflare.
    echo 2. Run this file again.
    echo 3. A public tunnel URL will open for port 5000.
    echo.
    echo Local access still works at:
    echo http://127.0.0.1:5000
    echo.
    pause
    exit /b 0
)

echo Opening Cloudflare tunnel for remote access...
echo The public URL will be copied to your clipboard automatically.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_tunnel.ps1"

pause
