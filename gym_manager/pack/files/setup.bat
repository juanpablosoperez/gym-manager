@echo off
setlocal enabledelayedexpansion

set INSTALL_DIR=%ProgramFiles%\Gym Manager

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y "Gym Manager.exe" "%INSTALL_DIR%\Gym Manager.exe" >nul
if exist "assets" xcopy /E /I /Y "assets" "%INSTALL_DIR%\assets" >nul

set MYSQL_EXE64=C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe
set MYSQL_EXE32=C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe
set MYSQL_EXE=
if exist "%MYSQL_EXE64%" set MYSQL_EXE=%MYSQL_EXE64%
if exist "%MYSQL_EXE32%" set MYSQL_EXE=%MYSQL_EXE32%

if "%MYSQL_EXE%"=="" (
  echo Instalando MySQL 8.4...
  start /wait "" ".\MySQLInstallerConsole.exe" community install server;8.4.0;x64:*:type=config;openfirewall=true;port=3306;servicename=MySQL84;rootpasswd=root;start=1
  if exist "%MYSQL_EXE64%" set MYSQL_EXE=%MYSQL_EXE64%
  if exist "%MYSQL_EXE32%" set MYSQL_EXE=%MYSQL_EXE32%
)

if "%MYSQL_EXE%"=="" (
  echo No se encontro mysql.exe tras la instalacion. Abortando.
  exit /b 1
)

mkdir "%INSTALL_DIR%\install" 2>nul
copy /Y "schema.sql" "%INSTALL_DIR%\install\schema.sql" >nul

echo Creando base de datos y tablas...
cmd /c ""%MYSQL_EXE%" -uroot -proot < "%INSTALL_DIR%\install\schema.sql""

> "%INSTALL_DIR%\.env.dev" echo DATABASE_URL=mysql+pymysql://root:root@localhost:3306/gym_manager

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([IO.Path]::Combine($env:Public,'Desktop','Gym Manager.lnk')); "^
  "$s.TargetPath='%INSTALL_DIR%\Gym Manager.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.IconLocation='%INSTALL_DIR%\Gym Manager.exe,0'; $s.Save()"

start "" "%INSTALL_DIR%\Gym Manager.exe"
exit /b 0