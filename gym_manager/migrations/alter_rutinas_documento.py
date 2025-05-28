from sqlalchemy import create_engine, text
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:KQJXRWXfVxCOmRYwAkoyrVenMWkTsVaI@yamanote.proxy.rlwy.net:35638/railway')

def upgrade():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Modificar la columna para permitir más datos
        conn.execute(text("""
            ALTER TABLE rutinas 
            MODIFY COLUMN documento_rutina LONGBLOB
        """))
        conn.commit()

if __name__ == "__main__":
    upgrade() 