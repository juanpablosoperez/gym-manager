import os
from pathlib import Path
from dotenv import load_dotenv

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno del archivo .env.dev
env_path = BASE_DIR / '.env.dev'
load_dotenv(env_path)

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise Exception("No se encontró la variable de entorno DATABASE_URL") 