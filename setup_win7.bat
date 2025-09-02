@echo off
echo Configurando entorno para Windows 7...

echo Instalando Python 3.9 (compatible con Windows 7)...
echo Por favor, descarga Python 3.9 desde: https://www.python.org/downloads/release/python-3918/
echo e instálalo antes de continuar.

echo.
echo Instalando dependencias compatibles con Windows 7...
pip install flet==0.21.0
pip install sqlalchemy==1.4.53
pip install alembic==1.12.1
pip install pymysql==1.0.3
pip install pandas==1.5.3
pip install openpyxl==3.1.2
pip install matplotlib==3.7.2
pip install seaborn==0.12.2
pip install numpy==1.24.3
pip install plotly==5.17.0
pip install kaleido==0.2.1
pip install reportlab==4.0.4
pip install cryptography==41.0.7
pip install bcrypt==4.0.1
pip install fpdf==1.7.2
pip install psutil==5.9.5

echo.
echo Entorno configurado para Windows 7!
echo Ahora puedes ejecutar: build_exe_win7.bat
pause

