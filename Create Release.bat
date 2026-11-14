@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\create_release.ps1"
if errorlevel 1 (
    echo.
    echo Release creation failed. See the error above.
    pause
    exit /b 1
)
echo.
pause
