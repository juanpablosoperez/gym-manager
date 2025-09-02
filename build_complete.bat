@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    BUILD COMPLETO - GYM MANAGER
echo ========================================
echo.

:: Configuración
set APP_NAME=Gym Manager
set VERSION=1.0.0
set BUILD_DIR=build
set DIST_DIR=dist
set PACK_DIR=gym_manager\pack
set OUTPUT_ZIP=%APP_NAME%_%VERSION%_Complete.zip

:: Limpiar directorios anteriores
echo Limpiando directorios anteriores...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%OUTPUT_ZIP%" del "%OUTPUT_ZIP%"

:: Crear directorios
mkdir "%BUILD_DIR%"
mkdir "%DIST_DIR%"

echo.
echo [1/4] Verificando herramientas de build...

:: Verificar si flet está disponible
set FLET_AVAILABLE=false
flet --version >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: Flet no encontrado en el PATH
    echo Intentando instalar flet...
    
    :: Intentar instalar flet
    pip install flet --user >nul 2>&1
    if errorlevel 1 (
        echo ERROR: No se pudo instalar flet
        echo Intentando con PyInstaller como alternativa...
        goto :use_pyinstaller
    )
    
    :: Verificar si se instaló correctamente
    flet --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Flet no se instaló correctamente
        echo Usando PyInstaller como alternativa...
        goto :use_pyinstaller
    )
    
    echo ✓ Flet instalado correctamente
    set FLET_AVAILABLE=true
) else (
    echo ✓ Flet encontrado
    set FLET_AVAILABLE=true
)

:use_flet
if "%FLET_AVAILABLE%"=="true" (
    echo.
    echo [2/4] Generando ejecutable con Flet...
    poetry run flet pack gym_manager\main.py ^
    --name "%APP_NAME%" ^
    --icon gym_manager\assets\app.ico ^
    --add-data "gym_manager\assets;assets" ^
    --hidden-import gym_manager.views.member_view ^
    --hidden-import gym_manager.views.backup_view ^
    --hidden-import gym_manager.views.statistics_view ^
    --hidden-import gym_manager.views.login_view ^
    --hidden-import gym_manager.views.home_view ^
    --hidden-import gym_manager.views.payment_view ^
    --hidden-import gym_manager.views.routine_view ^
    --hidden-import gym_manager.views.user_view ^
    --hidden-import gym_manager.views.payment_method_view ^
    --hidden-import gym_manager.views.payment_receipt_view ^
    --hidden-import gym_manager.controllers.statistics_controller ^
    --hidden-import gym_manager.controllers.auth_controller ^
    --hidden-import gym_manager.controllers.member_controller ^
    --hidden-import gym_manager.controllers.payment_controller ^
    --hidden-import gym_manager.services.backup_service ^
    --hidden-import gym_manager.services.restore_service ^
    --hidden-import gym_manager.services.auth ^
    --hidden-import gym_manager.services.database ^
    --hidden-import gym_manager.utils.database ^
    --hidden-import gym_manager.utils.navigation ^
    --hidden-import gym_manager.config ^
    --hidden-import plotly ^
    --hidden-import plotly.graph_objs ^
    --hidden-import flet.plotly_chart ^
    --hidden-import kaleido ^
    --hidden-import pymysql ^
    --hidden-import pymysql.cursors ^
    --hidden-import pymysql.connections ^
    --hidden-import reportlab ^
    --hidden-import reportlab.lib ^
    --hidden-import reportlab.platypus ^
    --hidden-import openpyxl

    if errorlevel 1 (
        echo ERROR: Fallo en la generación del ejecutable con Flet
        echo Intentando con PyInstaller como alternativa...
        goto :use_pyinstaller
    )

    echo ✓ Ejecutable generado exitosamente con Flet
    
    :: Verificar que el ejecutable existe
    if not exist "%DIST_DIR%\%APP_NAME%.exe" (
        echo ERROR: No se encontró el ejecutable generado
        echo Intentando con PyInstaller como alternativa...
        goto :use_pyinstaller
    )
    
    goto :continue_build
)

:use_pyinstaller
echo.
echo [2/4] Generando ejecutable con PyInstaller...
echo Verificando archivo .spec...

set SPEC_FILE=Gym_Manager_Optimized.spec
if not exist "%SPEC_FILE%" (
    echo ERROR: No se encontró el archivo .spec: %SPEC_FILE%
    pause
    exit /b 1
)

echo ✓ Archivo .spec encontrado: %SPEC_FILE%

:: Verificar si PyInstaller está disponible
py -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller no encontrado
    echo Instalando PyInstaller...
    pip install pyinstaller --user >nul 2>&1
    if errorlevel 1 (
        echo ERROR: No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
)

echo Compilando con PyInstaller...
py -m PyInstaller "%SPEC_FILE%" --noconfirm --log-level=INFO

if errorlevel 1 (
    echo ERROR: Fallo en la generación del ejecutable con PyInstaller
    pause
    exit /b 1
)

echo ✓ Ejecutable generado exitosamente con PyInstaller

:: Verificar que el ejecutable existe
if not exist "%DIST_DIR%\%APP_NAME%\%APP_NAME%.exe" (
    echo ERROR: No se encontró el ejecutable generado en la carpeta de distribución
    pause
    exit /b 1
)

:continue_build
echo.
echo [3/4] Verificando archivos de instalación...
if not exist "%PACK_DIR%\installer.iss" (
    echo ERROR: No se encontró installer.iss
    pause
    exit /b 1
)

if not exist "%PACK_DIR%\files\MySQLInstallerConsole.exe" (
    echo ERROR: No se encontró MySQLInstallerConsole.exe
    pause
    exit /b 1
)

if not exist "%PACK_DIR%\files\schema.sql" (
    echo ERROR: No se encontró schema.sql
    pause
    exit /b 1
)

echo ✓ Archivos de instalación verificados

echo.
echo [4/4] Compilando instalador con Inno Setup...
:: Buscar Inno Setup en ubicaciones comunes
set INNO_COMPILER=
for %%p in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    "C:\Program Files\Inno Setup 5\ISCC.exe"
) do (
    if exist %%p (
        set INNO_COMPILER=%%p
        goto :found_inno
    )
)

:found_inno
if "%INNO_COMPILER%"=="" (
    echo ADVERTENCIA: Inno Setup no encontrado. Saltando compilación del instalador.
    echo Para compilar el instalador, instala Inno Setup desde: https://jrsoftware.org/isdl.php
    goto :skip_installer
)

echo Compilando con: %INNO_COMPILER%
"%INNO_COMPILER%" "%PACK_DIR%\installer.iss"

if errorlevel 1 (
    echo ADVERTENCIA: Fallo en la compilación del instalador
    goto :skip_installer
)

echo ✓ Instalador compilado exitosamente

:skip_installer
echo.
echo [5/5] Creando paquete ZIP completo...

:: Crear directorio temporal para el zip
set TEMP_PACKAGE_DIR=%BUILD_DIR%\package
mkdir "%TEMP_PACKAGE_DIR%"

:: Copiar ejecutable según el método usado
if "%FLET_AVAILABLE%"=="true" (
    if exist "%DIST_DIR%\%APP_NAME%.exe" (
        copy "%DIST_DIR%\%APP_NAME%.exe" "%TEMP_PACKAGE_DIR%\%APP_NAME%.exe" >nul
    )
) else (
    :: Copiar toda la carpeta de distribución (incluye ejecutable y dependencias)
    xcopy /E /I /Y "%DIST_DIR%\%APP_NAME%" "%TEMP_PACKAGE_DIR%\%APP_NAME%" >nul
)

:: Copiar archivos de instalación
if exist "%PACK_DIR%\files" (
    xcopy /E /I /Y "%PACK_DIR%\files" "%TEMP_PACKAGE_DIR%\install" >nul
)

:: Copiar assets si no están embebidos
if exist "gym_manager\assets" (
    xcopy /E /I /Y "gym_manager\assets" "%TEMP_PACKAGE_DIR%\assets" >nul
)

:: Copiar instalador compilado si existe
if exist "%PACK_DIR%\Output\GymManagerSetup.exe" (
    copy "%PACK_DIR%\Output\GymManagerSetup.exe" "%TEMP_PACKAGE_DIR%\" >nul
)

:: Copiar README del cliente si existe
if exist "README_CLIENTE.md" (
    copy "README_CLIENTE.md" "%TEMP_PACKAGE_DIR%\README_CLIENTE.md" >nul
    echo ✓ README del cliente incluido
)

:: Crear archivo README de instalación técnica
echo Instrucciones de Instalación > "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo ============================== >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo. >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo 1. Ejecutar GymManagerSetup.exe (si está disponible) >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo 2. O ejecutar setup.bat desde la carpeta install >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
if "%FLET_AVAILABLE%"=="true" (
    echo 3. El ejecutable principal es: %APP_NAME%.exe >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
) else (
    echo 3. El ejecutable principal está en: %APP_NAME%\%APP_NAME%.exe >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
    echo. >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
    echo IMPORTANTE: Esta versión incluye todas las dependencias necesarias. >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
    echo No es necesario instalar Python ni librerías adicionales. >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
)
echo. >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo Nota: Se requiere MySQL 8.4 para el funcionamiento completo. >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo. >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo IMPORTANTE: Para instrucciones completas de instalación, >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"
echo consultar README_CLIENTE.md >> "%TEMP_PACKAGE_DIR%\README_INSTALACION.txt"

:: Crear ZIP usando PowerShell (más confiable que herramientas externas)
echo Creando archivo ZIP...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Compress-Archive -Path '%TEMP_PACKAGE_DIR%\*' -DestinationPath '%OUTPUT_ZIP%' -Force"

if errorlevel 1 (
    echo ERROR: Fallo en la creación del ZIP
    pause
    exit /b 1
)

echo ✓ Paquete ZIP creado exitosamente: %OUTPUT_ZIP%

:: Limpiar directorio temporal
rmdir /s /q "%TEMP_PACKAGE_DIR%"

echo.
echo ========================================
echo    BUILD COMPLETADO EXITOSAMENTE
echo ========================================
echo.
echo Archivos generados:
if "%FLET_AVAILABLE%"=="true" (
    echo - Ejecutable: %DIST_DIR%\%APP_NAME%.exe
) else (
    echo - Ejecutable y dependencias: %DIST_DIR%\%APP_NAME%\
)
echo - Paquete completo: %OUTPUT_ZIP%
echo.
echo El paquete ZIP contiene:
echo - Ejecutable principal
echo - Archivos de instalación
echo - Scripts de configuración
echo - Assets de la aplicación
echo - Instrucciones de instalación
echo.
if "%FLET_AVAILABLE%"=="false" (
    echo NOTA: Esta versión incluye todas las dependencias Python
    echo embebidas, por lo que es completamente portable.
    echo.
)
pause
