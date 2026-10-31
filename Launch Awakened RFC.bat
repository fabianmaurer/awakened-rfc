@echo off
setlocal
set "STEAM_DIR=%ProgramFiles(x86)%\Steam"
if not exist "%STEAM_DIR%\steam.exe" (
    echo Steam was not found in "%STEAM_DIR%".
    pause
    exit /b 1
)
set "CIV4_DIR=%STEAM_DIR%\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword"
if not exist "%CIV4_DIR%\Civ4BeyondSword.exe" (
    echo Civilization IV Beyond the Sword was not found in "%CIV4_DIR%".
    pause
    exit /b 1
)
if not exist "%CIV4_DIR%\Mods\Awakened RFC\Assets\CvGameCoreDLL.dll" (
    echo Awakened RFC was not found in "%CIV4_DIR%\Mods\Awakened RFC".
    pause
    exit /b 1
)
rem Start Steam first so Civ4 does not need to restart through Steam.
start "" "%STEAM_DIR%\steam.exe" -silent
rem Keep the quotes around the mod path, as required by Civ4's argument parser.
start "" /D "%CIV4_DIR%" "%CIV4_DIR%\Civ4BeyondSword.exe" mod="Mods\Awakened RFC"
