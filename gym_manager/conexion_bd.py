from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.exc import SQLAlchemyError

load_dotenv('.env.dev')

db_url = os.getenv("DATABASE_URL")
print("Intentando conectar a:", db_url)

try:
    engine = create_engine(db_url, pool_recycle=3600, pool_pre_ping=True)
    with engine.connect() as conn:
        print("¡Conexión exitosa!")
except SQLAlchemyError as e:
    print(f"Error al conectar a la base de datos: {str(e)}")
    raise Exception("No se pudo conectar a la base de datos. Por favor, verifique la configuración.")
