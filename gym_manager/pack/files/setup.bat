@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    INSTALADOR GYM MANAGER
echo ========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Este script requiere permisos de administrador.
    echo Por favor, ejecuta como administrador (clic derecho - Ejecutar como administrador)
    echo.
    pause
    exit /b 1
)

:: Configuración
set INSTALL_DIR=%ProgramFiles%\Gym Manager
set MYSQL_ROOT_PASSWORD=root
set MYSQL_PORT=3306
set MYSQL_SERVICE_NAME=MySQL84

echo [1/6] Preparando instalación...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Verificar que el ejecutable existe
if not exist "Gym Manager.exe" (
    echo ERROR: No se encontró el archivo Gym Manager.exe
    echo Asegúrate de ejecutar este script desde la carpeta correcta.
    pause
    exit /b 1
)

echo [2/6] Copiando archivos de la aplicación...
copy /Y "Gym Manager.exe" "%INSTALL_DIR%\Gym Manager.exe" >nul
if errorlevel 1 (
    echo ERROR: No se pudo copiar el ejecutable principal
    pause
    exit /b 1
)

if exist "assets" (
    xcopy /E /I /Y "assets" "%INSTALL_DIR%\assets" >nul
    echo ✓ Assets copiados
)

echo [3/6] Verificando MySQL...

:: Buscar MySQL en ubicaciones comunes
set MYSQL_EXE64=C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe
set MYSQL_EXE32=C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe
set MYSQL_EXE_ALT1=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
set MYSQL_EXE_ALT2=C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe
set MYSQL_EXE=

if exist "%MYSQL_EXE64%" set MYSQL_EXE=%MYSQL_EXE64%
if exist "%MYSQL_EXE32%" set MYSQL_EXE=%MYSQL_EXE32%
if exist "%MYSQL_EXE_ALT1%" set MYSQL_EXE=%MYSQL_EXE_ALT1%
if exist "%MYSQL_EXE_ALT2%" set MYSQL_EXE=%MYSQL_EXE_ALT2%

if "%MYSQL_EXE%"=="" (
    echo MySQL no encontrado. Instalando MySQL 8.4...
    
    :: Verificar que el instalador existe
    if not exist "MySQLInstallerConsole.exe" (
        echo ERROR: No se encontró MySQLInstallerConsole.exe
        echo Por favor, asegúrate de que este archivo esté en la misma carpeta.
        pause
        exit /b 1
    )
    
    echo Instalando MySQL 8.4 (esto puede tomar varios minutos)...
    echo Por favor, espera mientras se instala MySQL...
    
    :: Instalar MySQL con configuración automática
    "MySQLInstallerConsole.exe" community install server;8.4.0;x64:*:type=config;openfirewall=true;port=%MYSQL_PORT%;servicename=%MYSQL_SERVICE_NAME%;rootpasswd=%MYSQL_ROOT_PASSWORD%;start=1
    
    if errorlevel 1 (
        echo ADVERTENCIA: La instalación de MySQL falló o fue cancelada
        echo Intentando continuar con la configuración manual...
    )
    
    :: Buscar MySQL nuevamente después de la instalación
    if exist "%MYSQL_EXE64%" set MYSQL_EXE=%MYSQL_EXE64%
    if exist "%MYSQL_EXE32%" set MYSQL_EXE=%MYSQL_EXE32%
    if exist "%MYSQL_EXE_ALT1%" set MYSQL_EXE=%MYSQL_EXE_ALT1%
    if exist "%MYSQL_EXE_ALT2%" set MYSQL_EXE=%MYSQL_EXE_ALT2%
    
    if "%MYSQL_EXE%"=="" (
        echo ERROR: MySQL no se instaló correctamente
        echo Por favor, instala MySQL manualmente desde: https://dev.mysql.com/downloads/installer/
        echo Luego ejecuta este script nuevamente.
        pause
        exit /b 1
    )
    
    echo ✓ MySQL instalado correctamente
) else (
    echo ✓ MySQL encontrado: %MYSQL_EXE%
)

echo [4/6] Configurando base de datos...

:: Crear directorio de instalación
mkdir "%INSTALL_DIR%\install" 2>nul

:: Copiar schema.sql
if exist "schema.sql" (
    copy /Y "schema.sql" "%INSTALL_DIR%\install\schema.sql" >nul
    echo ✓ Schema de base de datos copiado
) else (
    echo ADVERTENCIA: No se encontró schema.sql
    echo La base de datos se creará con configuración por defecto
)

:: Esperar a que MySQL esté completamente iniciado
echo Esperando a que MySQL esté listo...
timeout /t 5 /nobreak >nul

:: Intentar conectar a MySQL y crear la base de datos
echo Creando base de datos y tablas...
echo CREATE DATABASE IF NOT EXISTS gym_manager; | "%MYSQL_EXE%" -uroot -p%MYSQL_ROOT_PASSWORD% 2>nul

if errorlevel 1 (
    echo ADVERTENCIA: No se pudo conectar a MySQL con la contraseña por defecto
    echo Intentando con contraseña vacía...
    echo CREATE DATABASE IF NOT EXISTS gym_manager; | "%MYSQL_EXE%" -uroot 2>nul
    
    if errorlevel 1 (
        echo ERROR: No se pudo conectar a MySQL
        echo Por favor, verifica que MySQL esté ejecutándose y la contraseña sea correcta
        echo.
        echo Soluciones posibles:
        echo 1. Reiniciar el servicio MySQL
        echo 2. Verificar la contraseña del usuario root
        echo 3. Ejecutar este script nuevamente
        pause
        exit /b 1
    )
)

:: Importar schema si existe
if exist "%INSTALL_DIR%\install\schema.sql" (
    echo Importando estructura de la base de datos...
    "%MYSQL_EXE%" -uroot -p%MYSQL_ROOT_PASSWORD% gym_manager < "%INSTALL_DIR%\install\schema.sql" 2>nul
    if errorlevel 1 (
        echo ADVERTENCIA: No se pudo importar el schema completo
        echo La aplicación se ejecutará con configuración básica
    ) else (
        echo ✓ Base de datos configurada correctamente
    )
)

echo [5/6] Configurando archivos de configuración...

:: Crear archivo de configuración
echo DATABASE_URL=mysql+pymysql://root:%MYSQL_ROOT_PASSWORD%@localhost:%MYSQL_PORT%/gym_manager > "%INSTALL_DIR%\.env.dev"
echo ✓ Archivo de configuración creado

:: Crear acceso directo en el escritorio
echo Creando acceso directo...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { "^
  "  $s=(New-Object -ComObject WScript.Shell).CreateShortcut([IO.Path]::Combine($env:Public,'Desktop','Gym Manager.lnk')); "^
  "  $s.TargetPath='%INSTALL_DIR%\Gym Manager.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.IconLocation='%INSTALL_DIR%\Gym Manager.exe,0'; $s.Save(); "^
  "  Write-Host 'Acceso directo creado exitosamente' "^
  "} catch { "^
  "  Write-Host 'ADVERTENCIA: No se pudo crear el acceso directo' "^
  "}"

echo [6/6] Finalizando instalación...

echo.
echo ========================================
echo    INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo ✓ Gym Manager instalado en: %INSTALL_DIR%
echo ✓ MySQL configurado y ejecutándose
echo ✓ Base de datos creada
echo ✓ Acceso directo en el escritorio
echo.
echo La aplicación se iniciará automáticamente...
echo.

:: Iniciar la aplicación
start "" "%INSTALL_DIR%\Gym Manager.exe"

echo ¡Instalación completada exitosamente!
echo.
echo Si tienes problemas, verifica que:
echo - MySQL esté ejecutándose
echo - El puerto 3306 esté disponible
echo - Tengas permisos de administrador
echo.
pause
exit /b 0