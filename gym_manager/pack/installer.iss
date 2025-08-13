[Setup]
AppName=Gym Manager
AppVersion=1.0.0
DefaultDirName={pf}\Gym Manager
DefaultGroupName=Gym Manager
UninstallDisplayIcon={app}\Gym Manager.exe
SetupIconFile=assets\app.ico
PrivilegesRequired=admin
Compression=lzma
SolidCompression=yes

[Files]
; App (exe generado por flet pack). Este .iss está en gym_manager, el exe está en ..\dist
Source: "..\dist\Gym Manager.exe"; DestDir: "{app}"; Flags: ignoreversion
; Assets si no están ya embebidos en el exe (ajusta si no usaste --add-data)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; SQL de creación
Source: "install\schema.sql"; DestDir: "{app}\install"; Flags: ignoreversion
; MySQL Installer Console (coloca el ejecutable REAL aquí antes de compilar; un acceso directo .lnk NO sirve)
Source: "install\MySQLInstallerConsole.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Run]
; 1) Instalar MySQL 8.4 silencioso si no existe
Filename: "{tmp}\MySQLInstallerConsole.exe"; \
  Parameters: "community install server;8.4.0;x64:*:type=config;openfirewall=true;port=3306;servicename=MySQL84;rootpasswd={code:GetRootPwd};start=1"; \
  StatusMsg: "Instalando MySQL..."; Flags: runhidden; Check: not IsMysqlInstalled

; 2) Importar el schema (usa cmd para la redirección)
Filename: "cmd.exe"; \
  Parameters: "/C \"\"\"{code:GetMysqlExe}\"\" -uroot -p{code:GetRootPwd} < \"\"{app}\install\schema.sql\"\"\""; \
  StatusMsg: "Creando base de datos y tablas..."; Flags: runhidden

; 3) Lanzar la app al terminar
Filename: "{app}\Gym Manager.exe"; Description: "Iniciar Gym Manager"; Flags: nowait postinstall skipifsilent

[Icons]
Name: "{group}\Gym Manager"; Filename: "{app}\Gym Manager.exe"
Name: "{commondesktop}\Gym Manager"; Filename: "{app}\Gym Manager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones:"

[Code]
const
  DefaultRootPwd = 'root';

function IsMysqlInstalled: Boolean;
begin
  Result :=
    FileExists(ExpandConstant('{pf64}\\MySQL\\MySQL Server 8.4\\bin\\mysql.exe')) or
    FileExists(ExpandConstant('{pf}\\MySQL\\MySQL Server 8.4\\bin\\mysql.exe'));
end;

function GetRootPwd(Param: string): string;
begin
  Result := DefaultRootPwd;  // si quieres, puedes pedirla al usuario con InputQuery
end;

function GetMysqlExe(Param: string): string;
var
  pf64Path, pf32Path: string;
begin
  pf64Path := ExpandConstant('{pf64}\\MySQL\\MySQL Server 8.4\\bin\\mysql.exe');
  pf32Path := ExpandConstant('{pf}\\MySQL\\MySQL Server 8.4\\bin\\mysql.exe');
  if FileExists(pf64Path) then
    Result := pf64Path
  else
    Result := pf32Path;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvPath: string;
  DBUrl: string;
begin
  if CurStep = ssInstall then
  begin
    ; // Crear .env.dev al lado del exe
    EnvPath := ExpandConstant('{app}\.env.dev');
    DBUrl := 'DATABASE_URL=mysql+pymysql://root:' + GetRootPwd('') + '@localhost:3306/gym_manager';
    SaveStringToFile(EnvPath, DBUrl + #13#10, False);
  end;
end;