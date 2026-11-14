@echo off
setlocal
set "RETREAT_VERSION=%~1"
if not defined RETREAT_VERSION (
    choice /C BA /M "Select B for before, A for after"
    if errorlevel 2 (set "RETREAT_VERSION=after") else (set "RETREAT_VERSION=before")
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Compare Retreat From Autosave.ps1" -Version "%RETREAT_VERSION%"
set "RETREAT_EXIT=%ERRORLEVEL%"
pause
exit /b %RETREAT_EXIT%
