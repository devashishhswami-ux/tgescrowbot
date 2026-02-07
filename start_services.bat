@echo off
echo ===============================================
echo Starting Middle Crypto Bot Services
echo ===============================================
echo.

echo Starting Telethon Microservice...
start "Telethon Service" cmd /k "cd /d %~dp0 && python telethon_service.py"

echo Waiting 5 seconds for Telethon service to initialize...
timeout /t 5 /nobreak >nul

echo Starting Main Bot...
start "Main Bot" cmd /k "cd /d %~dp0 && python bot.py"

echo.
echo ===============================================
echo Both services are starting...
echo - Telethon Service: http://localhost:5001
echo - Main Bot: Running
echo ===============================================
echo.
echo Press any key to exit this window (services will keep running)
pause >nul
