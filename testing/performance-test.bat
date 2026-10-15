@echo off
setlocal
pushd "%~dp0.."
if errorlevel 1 exit /b 1

echo Awakened RFC - performance analysis
echo Scenario: 600 AD. AI-only as China. 150 turns. Seed: 1.
echo Timings only: no gameplay snapshots or checkpoint saves.
echo Close Civ4 first. Keep the desktop unlocked for automatic setup.
echo Reports: %~dp0runs\performance-600ad-150turns
echo.
if exist "%~dp0..\.venv-art\Scripts\python.exe" (
    "%~dp0..\.venv-art\Scripts\python.exe" "%~dp0run_observer.py" --mode performance --scenario 600ad --games 1 --turns 150 --seed 1 --checkpoint-interval 0 --startup-timeout 600 --stall-timeout 1800 --output-dir "%~dp0runs\performance-600ad-150turns"
) else (
    py -3 "%~dp0run_observer.py" --mode performance --scenario 600ad --games 1 --turns 150 --seed 1 --checkpoint-interval 0 --startup-timeout 600 --stall-timeout 1800 --output-dir "%~dp0runs\performance-600ad-150turns"
)
set "RUN_RESULT=%ERRORLEVEL%"
echo.
if "%RUN_RESULT%"=="0" (
    echo Performance recording finished. See the printed performance report path.
) else (
    echo Run stopped with exit code %RUN_RESULT%. See the message above.
)
popd
pause
exit /b %RUN_RESULT%
