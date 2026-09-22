#ifndef Edition
  #define Edition "ko"
#endif
#define AppVersion "0.4.0"
#define AppExe "CodexModelMonitor-" + Edition + ".exe"

[Setup]
AppId=CodexModelProbe-{#Edition}
AppName=Codex Model Probe ({#Edition})
AppVersion={#AppVersion}
AppPublisher=jinyounghub
AppPublisherURL=https://github.com/jinyounghub/codex-model-probe
DefaultDirName={localappdata}\Programs\CodexModelProbe-{#Edition}
DefaultGroupName=Codex Model Probe ({#Edition})
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayIcon={app}\{#AppExe}
OutputDir=dist\{#AppVersion}
OutputBaseFilename=CodexModelProbe-Setup-{#Edition}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
DisableDirPage=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Languages]
#if Edition == "ko"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
#else
Name: "english"; MessagesFile: "compiler:Default.isl"
#endif

[Files]
Source: "dist\{#AppVersion}\bundles\CodexModelMonitor-{#Edition}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Codex Model Probe ({#Edition})"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\Codex Model Probe ({#Edition})"; Filename: "{app}\{#AppExe}"

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,Codex Model Probe}"; Flags: nowait postinstall skipifsilent
