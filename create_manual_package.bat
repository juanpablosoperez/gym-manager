@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    CREANDO PAQUETE MANUAL ^(SIN MySQL^)
echo ========================================
echo.

:: Configuracion
set APP_NAME=Gym Manager
set VERSION=1.0.0
set PACKAGE_DIR=Gym_Manager_Manual_%VERSION%
set OUTPUT_ZIP=gym_manager_manual.zip

echo [1/8] Limpiando artefactos anteriores...
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
if exist "%OUTPUT_ZIP%" del "%OUTPUT_ZIP%"

:: Verificar que ya exista un ejecutable compilado ^(no ejecutamos build para evitar otros ZIPs^)
echo [2/8] Verificando ejecutable existente...
set EXECUTABLE_FOUND=false
if exist "dist\%APP_NAME%\%APP_NAME%.exe" set EXECUTABLE_FOUND=true
if exist "dist\%APP_NAME%.exe" set EXECUTABLE_FOUND=true
if exist "build\%APP_NAME%\%APP_NAME%.exe" set EXECUTABLE_FOUND=true
if exist "build\%APP_NAME%.exe" set EXECUTABLE_FOUND=true

if "%EXECUTABLE_FOUND%"=="false" (
	echo ERROR: No se encontro el ejecutable compilado en dist\ o build\.
	echo Por favor, compila primero la aplicacion ^(ejecuta tu script de build^) y vuelve a correr este bat.
	pause
	exit /b 1
)

:: Crear estructura de carpetas del paquete manual
set APP_DIR=%PACKAGE_DIR%\app
set SCRIPTS_DIR=%PACKAGE_DIR%\scripts
set DOCS_DIR=%PACKAGE_DIR%\docs
set MYSQL_DIR=%PACKAGE_DIR%\mysql

echo [3/8] Creando estructura de directorios...
mkdir "%APP_DIR%"
mkdir "%SCRIPTS_DIR%"
mkdir "%DOCS_DIR%"
mkdir "%MYSQL_DIR%"

:: Copiar aplicacion ^(exe + dependencias^); soporta varias disposiciones de PyInstaller

echo [4/8] Copiando aplicacion...
set COPIED_APP=false
if "%COPIED_APP%"=="false" if exist "dist\%APP_NAME%\%APP_NAME%.exe" (
	xcopy /E /I /Y "dist\%APP_NAME%" "%APP_DIR%" >nul
	echo [OK] Aplicacion copiada desde dist\%APP_NAME%\
	set COPIED_APP=true
)
if "%COPIED_APP%"=="false" if exist "dist\%APP_NAME%.exe" (
	copy "dist\%APP_NAME%.exe" "%APP_DIR%\%APP_NAME%.exe" >nul
	if exist "gym_manager\assets" (
		xcopy /E /I /Y "gym_manager\assets" "%APP_DIR%\assets" >nul
	)
	echo [OK] Aplicacion copiada desde dist\ ^(standalone^)
	set COPIED_APP=true
)
if "%COPIED_APP%"=="false" if exist "build\%APP_NAME%\%APP_NAME%.exe" (
	xcopy /E /I /Y "build\%APP_NAME%" "%APP_DIR%" >nul
	echo [OK] Aplicacion copiada desde build\%APP_NAME%\
	set COPIED_APP=true
)
if "%COPIED_APP%"=="false" if exist "build\%APP_NAME%.exe" (
	copy "build\%APP_NAME%.exe" "%APP_DIR%\%APP_NAME%.exe" >nul
	if exist "gym_manager\assets" (
		xcopy /E /I /Y "gym_manager\assets" "%APP_DIR%\assets" >nul
	)
	echo [OK] Aplicacion copiada desde build\ ^(standalone^)
	set COPIED_APP=true
)

if not "%COPIED_APP%"=="true" (
	echo ERROR: No se pudo copiar la aplicacion.
	pause
	exit /b 1
)

:: Copiar scripts SQL necesarios para iniciar el sistema

echo [5/8] Copiando scripts SQL...
set COPIED_SQL=false
if exist "gym_manager\pack\files\schema.sql" (
	copy "gym_manager\pack\files\schema.sql" "%SCRIPTS_DIR%\schema.sql" >nul
	set COPIED_SQL=true
	echo [OK] Copiado: schema.sql
)
if exist "fix_routine_table.sql" (
	copy "fix_routine_table.sql" "%SCRIPTS_DIR%\fix_routine_table.sql" >nul
	set COPIED_SQL=true
	echo [OK] Copiado: fix_routine_table.sql
)
if "%COPIED_SQL%"=="false" (
	echo Aviso: No se encontraron scripts SQL para copiar.
)

:: Copiar instaladores/ZIP de MySQL incluidos en el proyecto

echo [6/8] Copiando instaladores de MySQL ^(uso manual^)...
set MYSQL_INSTALLER_SRC=gym_manager\pack\files\MySQLInstallerConsole.exe
set MYSQL_ZIP_SRC=gym_manager\pack\files\mysql-8.4.3-winx64.zip

if exist "%MYSQL_INSTALLER_SRC%" (
	copy "%MYSQL_INSTALLER_SRC%" "%MYSQL_DIR%\MySQLInstallerConsole.exe" >nul
	echo [OK] Copiado: MySQLInstallerConsole.exe
) else (
	echo Aviso: No se encontro %MYSQL_INSTALLER_SRC%
)

if exist "%MYSQL_ZIP_SRC%" (
	copy "%MYSQL_ZIP_SRC%" "%MYSQL_DIR%\mysql-8.4.3-winx64.zip" >nul
	echo [OK] Copiado: mysql-8.4.3-winx64.zip
) else (
	echo Aviso: No se encontro %MYSQL_ZIP_SRC%
)

:: Crear README con instrucciones manuales paso a paso
(
	echo # Gym Manager - Paquete Manual ^(sin instalacion automatica de MySQL^)
	echo.
	echo Este paquete incluye la aplicacion y sus dependencias ya compiladas, los scripts SQL
	echo necesarios, y los instaladores de MySQL para uso manual. La instalacion y configuracion
	echo de MySQL se realizan manualmente siguiendo los pasos de abajo.
	echo.
	echo ## Requisitos previos
	echo - Windows 10/11 ^(64 bits^)
	echo - Permisos para instalar software ^(MySQL^)
	echo.
	echo ## Archivos incluidos
	echo - Carpeta ^"app^": ejecutable ^"%APP_NAME%.exe^" con librerias
	echo - Carpeta ^"scripts^": scripts SQL ^(p.ej. schema.sql^)
	echo - Carpeta ^"mysql^": MySQLInstallerConsole.exe y/o mysql-8.4.3-winx64.zip ^(si estaban disponibles^)
	echo - Carpeta ^"docs^": este README
	echo.
	echo ## Paso a paso ^(instalacion y primera ejecucion^)
	echo 1. Instalar MySQL Server ^(opciones^):
	echo    - Opcion A: Ejecutar ^"mysql\\MySQLInstallerConsole.exe^" y seguir el asistente.
	echo    - Opcion B: Descomprimir ^"mysql\\mysql-8.4.3-winx64.zip^" y configurar manualmente el servicio.
	echo    - Alternativa: Descargar desde https://dev.mysql.com/downloads/installer/
	echo 2. Crear la base de datos para la app ^(usar usuario root / contrasenia root^):
	echo    - MySQL Workbench: CREATE DATABASE IF NOT EXISTS gym_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
	echo    - Consola: mysql -u root -proot -e ^"CREATE DATABASE IF NOT EXISTS gym_manager;^"
	echo 3. Importar el esquema inicial:
	echo    - MySQL Workbench: File ^> Open SQL Script ^> seleccionar ^"scripts\\schema.sql^" ^> Run
	echo    - Consola: mysql -u root -proot gym_manager ^< scripts\\schema.sql
	echo 4. ^(Opcional^) Ejecutar otros scripts de ^"scripts^" si corresponde ^(p.ej. fix_routine_table.sql^)
	echo 5. Configurar la conexion de la aplicacion ^(si se requiere archivo de entorno^):
	echo    - Crear el archivo ^"app\\.env.dev^" con:
	echo      DATABASE_URL=mysql+pymysql://root:root@localhost:3306/gym_manager
	echo 6. Abrir la aplicacion desde ^"app\\%APP_NAME%.exe^".
	echo.
	echo ## Comandos por consola ^(alternativa sin Workbench^)
	echo - Crear base de datos:
	echo   mysql -u root -proot -e ^"CREATE DATABASE IF NOT EXISTS gym_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;^"
	echo - Importar schema:
	echo   mysql -u root -proot gym_manager ^< scripts\\schema.sql
	echo - Ejecutar script opcional ^(ejemplo fix_routine_table.sql^):
	echo   mysql -u root -proot gym_manager ^< scripts\\fix_routine_table.sql
	echo - Probar conexion / listar:
	echo   mysql -u root -proot -e ^"SHOW DATABASES;^"
	echo   mysql -u root -proot -D gym_manager -e ^"SHOW TABLES;^"
	echo - Verificar usuario admin en la base ^(ajusta el nombre de tabla/campo si difiere^):
	echo   mysql -u root -proot -D gym_manager -e ^"SELECT * FROM users WHERE username='admin';^"
	echo - Si ^"mysql^" no se reconoce, usar ruta completa ^(ejemplos^):
	echo   ^"C:\\Program Files\\MySQL\\MySQL Server 8.4\\bin\\mysql.exe^" -u root -proot -e ^"SHOW DATABASES;^"
	echo   ^"C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe^" -u root -proot -D gym_manager -e ^"SELECT * FROM users WHERE username='admin';^"
	echo.
	echo ## Credenciales de la aplicacion
	echo - El esquema incluye el usuario administrador de la aplicacion: admin / admin
	echo   ^(si tu ^"schema.sql^" ya lo define; de lo contrario, crealo manualmente^)
	echo.
	echo **Version del paquete:** %VERSION%
) > "%DOCS_DIR%\README_INSTALACION.txt"

:: Copia del README a la raiz del paquete para visibilidad
copy "%DOCS_DIR%\README_INSTALACION.txt" "%PACKAGE_DIR%\README_INSTALACION.txt" >nul

if not exist "%PACKAGE_DIR%\README_INSTALACION.txt" (
	echo ERROR: No se pudo crear README_INSTALACION.txt en la raiz del paquete.
	pause
	exit /b 1
)

echo [7/8] Documentacion creada: docs\README_INSTALACION.txt y README_INSTALACION.txt ^(raiz^)

:: Empaquetar en ZIP

echo [8/8] Creando archivo ZIP...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%OUTPUT_ZIP%' -Force"

if errorlevel 1 (
	echo ERROR: Fallo en la creacion del ZIP
	pause
	exit /b 1
)

echo [OK] Archivo ZIP creado: %OUTPUT_ZIP%

echo.
echo ========================================
echo    PAQUETE MANUAL CREADO CORRECTAMENTE

echo.
echo Archivo generado: %OUTPUT_ZIP%
echo Contenido: app\, scripts\, docs\, mysql\, README_INSTALACION.txt

echo El README con instrucciones esta en: README_INSTALACION.txt ^(raiz^) y docs\README_INSTALACION.txt dentro del ZIP.

echo.
pause
