import os
from dotenv import load_dotenv

# Determinar entorno
ENV = os.getenv("ENV", "development")
env_file = ".env.prod" if ENV == "production" else ".env.dev"

# Cargar variables de entorno
load_dotenv(env_file)

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
