from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv('.env.dev')

db_url = os.getenv("DATABASE_URL")
print("Intentando conectar a:", db_url)
engine = create_engine(db_url)
with engine.connect() as conn:
    print("¡Conexión exitosa!")
