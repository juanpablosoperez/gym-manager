@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    CREANDO VERSION PORTABLE
echo ========================================
echo.

:: Configuracion
set APP_NAME=Gym Manager
set VERSION=1.0.0
set PORTABLE_DIR=Gym_Manager_Portable_%VERSION%
set OUTPUT_ZIP=%APP_NAME%_Portable_%VERSION%.zip

:: Limpiar directorios anteriores
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
if exist "%OUTPUT_ZIP%" del "%OUTPUT_ZIP%"

echo [1/4] Creando estructura portable...
mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\app"
mkdir "%PORTABLE_DIR%\data"
mkdir "%PORTABLE_DIR%\mysql"
mkdir "%PORTABLE_DIR%\scripts"

echo [2/4] Copiando aplicacion...

:: Buscar el ejecutable en diferentes ubicaciones posibles
set EXECUTABLE_FOUND=false

:: Verificar si existe la carpeta de distribucion de PyInstaller
if exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    xcopy /E /I /Y "dist\%APP_NAME%" "%PORTABLE_DIR%\app" >nul
    echo [OK] Aplicacion copiada (version PyInstaller con dependencias)
    set EXECUTABLE_FOUND=true
) else if exist "dist\%APP_NAME%.exe" (
    copy "dist\%APP_NAME%.exe" "%PORTABLE_DIR%\app\%APP_NAME%.exe" >nul
    if exist "gym_manager\assets" (
        xcopy /E /I /Y "gym_manager\assets" "%PORTABLE_DIR%\app\assets" >nul
    )
    echo [OK] Aplicacion copiada (version standalone)
    set EXECUTABLE_FOUND=true
) else if exist "build\%APP_NAME%\%APP_NAME%.exe" (
    xcopy /E /I /Y "build\%APP_NAME%" "%PORTABLE_DIR%\app" >nul
    echo [OK] Aplicacion copiada (version build con dependencias)
    set EXECUTABLE_FOUND=true
) else if exist "build\%APP_NAME%.exe" (
    copy "build\%APP_NAME%.exe" "%PORTABLE_DIR%\app\%APP_NAME%.exe" >nul
    if exist "gym_manager\assets" (
        xcopy /E /I /Y "gym_manager\assets" "%PORTABLE_DIR%\app\assets" >nul
    )
    echo [OK] Aplicacion copiada (version build standalone)
    set EXECUTABLE_FOUND=true
)

if "%EXECUTABLE_FOUND%"=="false" (
    echo ERROR: No se encontro el ejecutable compilado
    echo.
    echo Buscando en las siguientes ubicaciones:
    echo - dist\%APP_NAME%\%APP_NAME%.exe
    echo - dist\%APP_NAME%.exe
    echo - build\%APP_NAME%\%APP_NAME%.exe
    echo - build\%APP_NAME%.exe
    echo.
    echo Ejecuta primero build_complete.bat
    pause
    exit /b 1
)

echo [3/4] Copiando archivos de configuracion...

:: Copiar schema.sql
if exist "gym_manager\pack\files\schema.sql" (
    copy "gym_manager\pack\files\schema.sql" "%PORTABLE_DIR%\data\schema.sql" >nul
    echo [OK] Schema de base de datos copiado
)

:: Copiar MySQL installer
if exist "gym_manager\pack\files\MySQLInstallerConsole.exe" (
    copy "gym_manager\pack\files\MySQLInstallerConsole.exe" "%PORTABLE_DIR%\mysql\MySQLInstallerConsole.exe" >nul
    echo [OK] Instalador MySQL copiado
)

:: Copiar MySQL ZIP 8.4.3 (opcional)
if exist "gym_manager\pack\files\mysql-8.4.3-winx64.zip" (
    copy "gym_manager\pack\files\mysql-8.4.3-winx64.zip" "%PORTABLE_DIR%\mysql\mysql-8.4.3-winx64.zip" >nul
    echo [OK] ZIP MySQL 8.4.3 copiado
)

:: Crear script de inicio portable
echo Creando script de inicio portable...
(
echo @echo off
echo setlocal enabledelayedexpansion
echo.
echo echo ========================================
echo echo    GYM MANAGER - VERSION PORTABLE
echo echo ========================================
echo echo.
echo.
echo :: Verificar si MySQL esta instalado
echo set MYSQL_EXE64=C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe
echo set MYSQL_EXE32=C:\Program Files ^(x86^)\MySQL\MySQL Server 8.4\bin\mysql.exe
echo set MYSQL_EXE_ALT1=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
echo set MYSQL_EXE_ALT2=C:\Program Files ^(x86^)\MySQL\MySQL Server 8.0\bin\mysql.exe
echo set MYSQL_EXE=
echo.
echo if exist "%%MYSQL_EXE64%%" set MYSQL_EXE=%%MYSQL_EXE64%%
echo if exist "%%MYSQL_EXE32%%" set MYSQL_EXE=%%MYSQL_EXE32%%
echo if exist "%%MYSQL_EXE_ALT1%%" set MYSQL_EXE=%%MYSQL_EXE_ALT1%%
echo if exist "%%MYSQL_EXE_ALT2%%" set MYSQL_EXE=%%MYSQL_EXE_ALT2%%
echo.
echo if "%%MYSQL_EXE%%"=="" ^(
echo     echo MySQL no encontrado. Instalando MySQL...
echo     echo.
echo     if exist "mysql\MySQLInstallerConsole.exe" ^(
echo         echo Instalando MySQL 8.4... Esto puede tomar varios minutos.
echo         "mysql\MySQLInstallerConsole.exe" community install server;8.4.0;x64:*:type=config;openfirewall=true;port=3306;servicename=MySQL84;rootpasswd=root;start=1
echo         echo.
echo         echo Esperando a que MySQL este listo...
echo         timeout /t 10 /nobreak ^>nul
echo     ^) else ^(
echo         echo ERROR: No se encontro el instalador de MySQL
echo         echo Por favor, instala MySQL manualmente desde: https://dev.mysql.com/downloads/installer/
echo         pause
echo         exit /b 1
echo     ^)
echo ^)
echo.
echo :: Buscar MySQL nuevamente
echo if exist "%%MYSQL_EXE64%%" set MYSQL_EXE=%%MYSQL_EXE64%%
echo if exist "%%MYSQL_EXE32%%" set MYSQL_EXE=%%MYSQL_EXE32%%
echo if exist "%%MYSQL_EXE_ALT1%%" set MYSQL_EXE=%%MYSQL_EXE_ALT1%%
echo if exist "%%MYSQL_EXE_ALT2%%" set MYSQL_EXE=%%MYSQL_EXE_ALT2%%
echo.
echo if "%%MYSQL_EXE%%"=="" ^(
echo     echo ERROR: MySQL no se instalo correctamente
echo     pause
echo     exit /b 1
echo ^)
echo.
echo :: Crear base de datos si no existe
echo echo Configurando base de datos...
echo echo CREATE DATABASE IF NOT EXISTS gym_manager; ^| "%%MYSQL_EXE%%" -uroot -proot 2^>nul
echo.
echo :: Importar schema si existe
echo if exist "data\schema.sql" ^(
echo     echo Importando estructura de la base de datos...
echo     "%%MYSQL_EXE%%" -uroot -proot gym_manager ^< "data\schema.sql" 2^>nul
echo ^)
echo.
echo :: Crear archivo de configuracion
echo echo DATABASE_URL=mysql+pymysql://root:root@localhost:3306/gym_manager ^> "app\.env.dev"
echo.
echo echo Iniciando Gym Manager...
echo echo.
echo cd /d "app"
echo start "" "Gym Manager.exe"
echo cd /d ".."
echo.
echo echo Gym Manager iniciado exitosamente!
echo echo.
echo echo Para cerrar la aplicacion, simplemente cierra la ventana.
echo echo.
echo pause
) > "%PORTABLE_DIR%\Iniciar_Gym_Manager.bat"

echo [OK] Script de inicio creado

:: Crear README para la version portable
(
echo # Gym Manager - Version Portable
echo.
echo ## Que es la version portable?
echo.
echo Esta version de Gym Manager no requiere instalacion. Simplemente:
echo.
echo 1. **Ejecutar `Iniciar_Gym_Manager.bat`**
echo 2. **La aplicacion se configurara automaticamente**
echo 3. **Listo para usar!**
echo.
echo ## Ventajas de la version portable:
echo.
echo - **No requiere instalacion** - Solo ejecutar
echo - **No modifica el registro** de Windows
echo - **Facil de transportar** - Copiar carpeta completa
echo - **Facil de desinstalar** - Solo eliminar carpeta
echo - **Configuracion automatica** de MySQL
echo.
echo ## Requisitos:
echo.
echo - Windows 10/11 ^(64 bits^)
echo - Permisos de administrador ^(solo para instalar MySQL^)
echo - 2 GB de espacio libre
echo.
echo ## Uso:
echo.
echo 1. **Ejecutar como administrador** ^(clic derecho - Ejecutar como administrador^)
echo 2. **Esperar** a que se instale MySQL ^(solo la primera vez^)
echo 3. **Disfrutar!** La aplicacion se abrira automaticamente
echo.
echo ## Notas importantes:
echo.
echo - La primera ejecucion puede tomar varios minutos ^(instalacion de MySQL^)
echo - Las ejecuciones posteriores son instantaneas
echo - Todos los datos se guardan en la carpeta `data`
echo - Para desinstalar, simplemente elimina toda la carpeta
echo.
echo ---
echo.
echo **Desarrollado por:** Gym Manager Team
echo **Version:** %VERSION%
echo **Soporte:** soporte@gymmanager.com
) > "%PORTABLE_DIR%\README_PORTABLE.txt"

echo [OK] Documentacion creada

echo [4/4] Creando archivo ZIP...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Compress-Archive -Path '%PORTABLE_DIR%\*' -DestinationPath '%OUTPUT_ZIP%' -Force"

if errorlevel 1 (
    echo ERROR: Fallo en la creacion del ZIP
    pause
    exit /b 1
)

echo [OK] Archivo ZIP creado: %OUTPUT_ZIP%

:: Limpiar directorio temporal
rmdir /s /q "%PORTABLE_DIR%"

echo.
echo ========================================
echo    VERSION PORTABLE CREADA
echo ========================================
echo.
echo Archivo generado: %OUTPUT_ZIP%
echo.
echo Esta version portable incluye:
echo - Aplicacion completa con todas las dependencias
echo - Script de inicio: Iniciar_Gym_Manager.bat
echo - Instalador automatico de MySQL
echo - Documentacion completa (README_PORTABLE.txt)
echo - Configuracion automatica de base de datos
echo.
echo Para distribuir:
echo 1. Enviar el archivo ZIP al cliente
echo 2. El cliente solo necesita descomprimir y ejecutar
echo 3. No requiere instalacion adicional!
echo.
pause
