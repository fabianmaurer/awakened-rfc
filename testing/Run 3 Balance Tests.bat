@echo off
setlocal
pushd "%~dp0.."
if errorlevel 1 exit /b 1

echo Awakened RFC - three sequential balance recordings
echo Scenario: 3000 BC. AI-only. 500 turns per game. Seeds: 1, 2, 3.
echo State snapshots and checkpoint saves every 25 turns.
echo Recordings: %~dp0runs\balance-3games-500turns
echo.
echo Close any existing Civ4 game before continuing.
echo Scenario setup with America is confirmed automatically. Keep the desktop unlocked.
echo Each game closes automatically before the next starts. A failed run stops the batch.
echo.

if exist "%~dp0..\.venv-art\Scripts\python.exe" (
    "%~dp0..\.venv-art\Scripts\python.exe" "%~dp0run_observer.py" --mode balance --games 3 --turns 500 --seed 1 --record-interval 25 --checkpoint-interval 25 --startup-timeout 600 --stall-timeout 900 --output-dir "%~dp0runs\balance-3games-500turns"
) else (
    py -3 "%~dp0run_observer.py" --mode balance --games 3 --turns 500 --seed 1 --record-interval 25 --checkpoint-interval 25 --startup-timeout 600 --stall-timeout 900 --output-dir "%~dp0runs\balance-3games-500turns"
)
set "RUN_RESULT=%ERRORLEVEL%"
echo.
if "%RUN_RESULT%"=="0" (
    echo All three recordings finished. Share the printed batch folder path for analysis.
) else (
    echo Batch stopped with exit code %RUN_RESULT%. See the message above.
)
popd
pause
exit /b %RUN_RESULT%
