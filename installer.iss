[Setup]
AppName=Kenshi Save Editor
AppVersion=1.0.2
AppVerName=Kenshi Save Editor 1.0.2
AppPublisher=wansolanso
AppPublisherURL=https://github.com/wansolanso/Kenshi-Save-Editor
DefaultDirName={autopf}\Kenshi Save Editor
DefaultGroupName=Kenshi Save Editor
UninstallDisplayIcon={app}\KenshiSaveEditor.exe
OutputDir=dist
OutputBaseFilename=KenshiSaveEditor-Setup-v1.0.2
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
SetupIconFile=
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Files]
Source: "dist\entry.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Kenshi Save Editor"; Filename: "{app}\KenshiSaveEditor.exe"
Name: "{autodesktop}\Kenshi Save Editor"; Filename: "{app}\KenshiSaveEditor.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\KenshiSaveEditor.exe"; Description: "Launch Kenshi Save Editor"; Flags: nowait postinstall skipifsilent
