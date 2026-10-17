@echo off
setlocal
set "TESTING_DIR=%~dp0"
if exist "%TESTING_DIR%..\.venv-art\Scripts\python.exe" (
    "%TESTING_DIR%..\.venv-art\Scripts\python.exe" "%TESTING_DIR%run_observer.py" %*
) else (
    py -3 "%TESTING_DIR%run_observer.py" %*
)
exit /b %ERRORLEVEL%
