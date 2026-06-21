[Setup]
AppName=PDF Merger
AppVersion=1.0.0
AppPublisher=B3 Software
DefaultDirName={autopf}\PDFMerger
DefaultGroupName=PDF Merger
OutputDir=.
OutputBaseFilename=PDF_Merger_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Kopiowanie głównego pliku wykonywalnego
Source: "dist\PDFMerger\PDFMerger.exe"; DestDir: "{app}"; Flags: ignoreversion
; Kopiowanie całej zawartości środowiska
Source: "dist\PDFMerger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PDF Merger"; Filename: "{app}\PDFMerger.exe"
Name: "{autodesktop}\PDF Merger"; Filename: "{app}\PDFMerger.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PDFMerger.exe"; Description: "{cm:LaunchProgram,PDF Merger}"; Flags: nowait postinstall skipifsilent