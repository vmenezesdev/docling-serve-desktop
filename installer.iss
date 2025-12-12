; Inno Setup Script for Docling Serve Desktop
; This creates a simple installation wizard for Windows

#define MyAppName "Docling Serve Desktop"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Docling Project"
#define MyAppURL "https://github.com/docling-project/docling-serve"
#define MyAppExeName "DoclingServeDesktop.exe"

[Setup]
; Application information
AppId={{B8F3E2A1-9C4D-4F3E-A5B6-7D8E9F0A1B2C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output configuration
OutputDir=installer_output
OutputBaseFilename=DoclingServeDesktop-Setup
SetupIconFile=

; Compression
Compression=lzma
SolidCompression=yes

; Windows version requirement
MinVersion=10.0

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Architecture
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Launch {#MyAppName} at Windows startup"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Include all files from the dist\DoclingServeDesktop folder
Source: "dist\DoclingServeDesktop\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Startup shortcut (optional)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
; Option to launch the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  FreeMB: Cardinal;
  TotalMB: Cardinal;
  RequiredMB: Cardinal;
begin
  Result := True;

  // Check available disk space (require at least 3GB free)
  // GetSpaceOnDisk with InMegabytes=True returns space in megabytes (MB).
  RequiredMB := 3 * 1024; // 3GB in MB
  if GetSpaceOnDisk(ExpandConstant('{autopf}'), True, FreeMB, TotalMB) then
  begin
    if FreeMB < RequiredMB then
    begin
      MsgBox('Insufficient disk space. At least 3GB of free space is required.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Any post-installation tasks can be added here
  end;
end;
