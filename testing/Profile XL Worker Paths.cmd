@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Profile XL Worker Paths.ps1"
set "PROFILE_EXIT=%ERRORLEVEL%"
pause
exit /b %PROFILE_EXIT%
