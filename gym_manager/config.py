import os
from pathlib import Path

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de la base de datos MySQL local
# Configuración por defecto para desarrollo local
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "gym_manager"
DB_USER = "root"
DB_PASSWORD = "root"  # Cambiar por tu contraseña de MySQL

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 