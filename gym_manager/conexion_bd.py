from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from gym_manager.config import DATABASE_URL

db_url = DATABASE_URL
print("Intentando conectar a:", db_url)

try:
    engine = create_engine(db_url, pool_recycle=3600, pool_pre_ping=True)
    with engine.connect() as conn:
        print("¡Conexión exitosa!")
except SQLAlchemyError as e:
    print(f"Error al conectar a la base de datos: {str(e)}")
    raise Exception("No se pudo conectar a la base de datos. Por favor, verifique la configuración.")
