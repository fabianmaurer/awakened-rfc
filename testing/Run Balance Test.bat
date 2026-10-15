@echo off
setlocal
pushd "%~dp0.."
if errorlevel 1 exit /b 1

echo Awakened RFC - single balance recording
echo Scenario: 3000 BC. AI-only. 250 turns. Seed: 1.
echo State snapshots and checkpoint saves every 25 turns.
echo Recordings: %~dp0runs\balance-single
echo.
echo Close any existing Civ4 game before continuing.
echo Scenario setup with America is confirmed automatically. Keep the desktop unlocked.
echo The launcher closes its own game after recording finishes.
echo.

if exist "%~dp0..\.venv-art\Scripts\python.exe" (
    "%~dp0..\.venv-art\Scripts\python.exe" "%~dp0run_observer.py" --mode balance --games 1 --turns 250 --seed 1 --record-interval 25 --checkpoint-interval 25 --startup-timeout 600 --stall-timeout 900 --output-dir "%~dp0runs\balance-single"
) else (
    py -3 "%~dp0run_observer.py" --mode balance --games 1 --turns 250 --seed 1 --record-interval 25 --checkpoint-interval 25 --startup-timeout 600 --stall-timeout 900 --output-dir "%~dp0runs\balance-single"
)
set "RUN_RESULT=%ERRORLEVEL%"
echo.
if "%RUN_RESULT%"=="0" (
    echo Recording finished. Share the printed batch folder path for analysis.
) else (
    echo Run stopped with exit code %RUN_RESULT%. See the message above.
)
popd
pause
exit /b %RUN_RESULT%
