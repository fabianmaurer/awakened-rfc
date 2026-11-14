#ifndef PayloadDir
  #error PayloadDir must point to the packaged mod folder
#endif
#ifndef OutputDir
  #error OutputDir must point to the release staging folder
#endif

[Setup]
AppId={{D91F6C78-2E40-4396-8C3D-74CC70D66F52}
AppName=Awakened Rhye's and Fall of Civilization
AppVersion=1
DefaultDirName={code:DefaultGameDir}
DisableProgramGroupPage=yes
DisableWelcomePage=no
WizardImageFile=installer-welcome.bmp
PrivilegesRequired=admin
OutputDir={#OutputDir}
OutputBaseFilename=Awakened-RFC-Setup
Compression=lzma2
SolidCompression=yes
Uninstallable=no
DirExistsWarning=no

[Tasks]
Name: graphics; Description: "Install GraphicsUpgrade by Deliverator. Improves water and shadows; disable it by removing d3d9.dll."; Flags: unchecked

[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}\Mods\Awakened RFC"; Flags: recursesubdirs createallsubdirs ignoreversion

[Code]
procedure InitializeWizard;
begin
  WizardForm.SelectDirLabel.Caption := 'Select the Beyond the Sword folder containing Civ4BeyondSword.exe.';
end;

function DefaultGameDir(Param: String): String;
var Steam: String;
begin
  if RegQueryStringValue(HKCU, 'Software\Valve\Steam', 'SteamPath', Steam) then begin
    Result := Steam + '\steamapps\common\Sid Meier''s Civilization IV Beyond the Sword\Beyond the Sword';
    if FileExists(Result + '\Civ4BeyondSword.exe') then exit;
  end;
  Result := ExpandConstant('{autopf32}\Steam\steamapps\common\Sid Meier''s Civilization IV Beyond the Sword\Beyond the Sword');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = wpSelectDir) and not FileExists(ExpandConstant('{app}\Civ4BeyondSword.exe')) then begin
    MsgBox('Select the Beyond the Sword folder containing Civ4BeyondSword.exe.', mbError, MB_OK);
    Result := False;
  end;
end;

function GraphicsInstalled: Boolean;
begin
  Result := FileExists(ExpandConstant('{app}\d3d9.dll')) and
    DirExists(ExpandConstant('{app}\GraphicsUpgrade')) and
    FileExists(ExpandConstant('{app}\GraphicsUpgrade.ini'));
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpSelectTasks then begin
    if GraphicsInstalled then begin
      WizardForm.TasksList.Checked[0] := False;
      WizardForm.TasksList.ItemEnabled[0] := False;
      WizardForm.TasksList.ItemCaption[0] := 'GraphicsUpgrade by Deliverator is already installed.';
    end else begin
      WizardForm.TasksList.ItemEnabled[0] := True;
      WizardForm.TasksList.ItemCaption[0] := 'Install GraphicsUpgrade by Deliverator. Improves water and shadows; disable it by removing d3d9.dll.';
    end;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var OldDir, Backup: String; N: Integer; Code: Integer;
begin
  Result := '';
  if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), '-NoProfile -Command "if (Get-Process Civ4BeyondSword -ErrorAction SilentlyContinue) { exit 1 }"', '', SW_HIDE, ewWaitUntilTerminated, Code) then begin
    Result := 'Could not check whether Beyond the Sword is running.';
    exit;
  end;
  if Code <> 0 then begin
    Result := 'Close Beyond the Sword before installing or updating the mod.';
    exit;
  end;
  OldDir := ExpandConstant('{app}\Mods\Awakened RFC');
  if DirExists(OldDir) then begin
    Backup := OldDir + '-backup-' + GetDateTimeString('yyyymmdd-hhnnss', '-', ':');
    N := 0;
    while DirExists(Backup) do begin
      N := N + 1;
      Backup := OldDir + '-backup-' + GetDateTimeString('yyyymmdd-hhnnss', '-', ':') + '-' + IntToStr(N);
    end;
    if not RenameFile(OldDir, Backup) then
      Result := 'Could not move the existing mod to a backup. Close the game and check folder permissions.';
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var Code: Integer; Script: String;
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('graphics') and not GraphicsInstalled then begin
    Script := ExpandConstant('{app}\Mods\Awakened RFC\Install Graphics Upgrade.ps1');
    if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), '-NoProfile -ExecutionPolicy Bypass -File "' + Script + '"', '', SW_SHOW, ewWaitUntilTerminated, Code) then
      MsgBox('Could not start the graphics installer. Run Install Graphics Upgrade.ps1 from the installed mod folder.', mbError, MB_OK)
    else if Code <> 0 then
      MsgBox('GraphicsUpgrade was not installed. Run Install Graphics Upgrade.ps1 from the installed mod folder to see the error.', mbError, MB_OK);
  end;
end;
