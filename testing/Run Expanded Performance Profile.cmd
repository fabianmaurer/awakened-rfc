@echo off
setlocal
rem One serial 3000 BC game, seed 1, 400 turns. Performance mode disables saves.
call "%~dp0run-test.cmd" --mode performance --start 0 --runs 1 --turns 400 --seed 1 --startup-timeout 600 --stall-timeout 1800
set "PROFILE_EXIT=%ERRORLEVEL%"
echo.
echo Profiling finished with exit code %PROFILE_EXIT%. Recordings and reports are under testing\runs.
pause
exit /b %PROFILE_EXIT%
