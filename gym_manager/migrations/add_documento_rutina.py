from sqlalchemy import create_engine, Column, LargeBinary, String
from sqlalchemy.sql import text
from gym_manager.utils.database import DATABASE_URL

def migrate():
    """
    Agrega los campos documento_rutina y nombre_documento a la tabla rutinas
    """
    engine = create_engine(DATABASE_URL)
    
    # Agregar las nuevas columnas
    with engine.connect() as conn:
        # Verificar si las columnas ya existen
        result = conn.execute(text("SHOW COLUMNS FROM rutinas LIKE 'documento_rutina'"))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE rutinas ADD COLUMN documento_rutina LONGBLOB"))
        
        result = conn.execute(text("SHOW COLUMNS FROM rutinas LIKE 'nombre_documento'"))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE rutinas ADD COLUMN nombre_documento VARCHAR(255)"))
        
        conn.commit()

if __name__ == "__main__":
    migrate() 