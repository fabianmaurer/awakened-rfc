@echo off
setlocal
set "TESTING_DIR=%~dp0"
pushd "%TESTING_DIR%.."
if errorlevel 1 exit /b 1

if not exist "%TESTING_DIR%run_observer.py" (
    echo Cannot find observer launcher: "%TESTING_DIR%run_observer.py"
    popd
    pause
    exit /b 1
)

echo Awakened RFC - five sequential early game mechanics recordings
echo Scenario: 3000 BC. AI-only. 150 turns per game. Seeds: 1, 2, 3, 4, 5.
echo Diagnostics mode: detailed state and mechanic checks every turn.
echo Checkpoint saves every 25 turns, plus initial and final saves.
echo Recordings: %TESTING_DIR%runs\mechanics-3000bc-5games-150turns
echo.
echo Close any existing Civ4 game before continuing.
echo Scenario setup with America is confirmed automatically. Keep the desktop unlocked.
echo Each game closes automatically before the next starts. A failed run stops the batch.
echo.

if exist "%TESTING_DIR%..\.venv-art\Scripts\python.exe" (
    "%TESTING_DIR%..\.venv-art\Scripts\python.exe" "%TESTING_DIR%run_observer.py" --mode diagnostics --scenario 3000bc --games 5 --turns 150 --seed 1 --record-interval 1 --checkpoint-interval 25 --startup-timeout 600 --stall-timeout 900 --output-dir "%TESTING_DIR%runs\mechanics-3000bc-5games-150turns"
) else (
    py -3 "%TESTING_DIR%run_observer.py" --mode diagnostics --scenario 3000bc --games 5 --turns 150 --seed 1 --record-interval 1 --checkpoint-interval 25 --startup-timeout 600 --stall-timeout 900 --output-dir "%TESTING_DIR%runs\mechanics-3000bc-5games-150turns"
)
set "RUN_RESULT=%ERRORLEVEL%"
echo.
if "%RUN_RESULT%"=="0" (
    echo All five recordings finished. Share the printed batch folder path for analysis.
) else (
    echo Batch stopped with exit code %RUN_RESULT%. See the message above.
)
popd
pause
exit /b %RUN_RESULT%
