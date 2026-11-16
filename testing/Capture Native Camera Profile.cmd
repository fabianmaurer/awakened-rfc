@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Capture Native Camera Profile.ps1"
set "CAPTURE_EXIT=%ERRORLEVEL%"
pause
exit /b %CAPTURE_EXIT%
