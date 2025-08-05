from sqlalchemy import create_engine, text
from gym_manager.utils.database import DATABASE_URL

def migrate():
    """
    Elimina la columna id_miembro de la tabla rutinas ya que la relación ahora va desde Miembro hacia Rutina
    """
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Verificar si la columna existe antes de eliminarla
        result = conn.execute(text("SHOW COLUMNS FROM rutinas LIKE 'id_miembro'"))
        if result.fetchone():
            # Obtener el nombre de la clave foránea
            result = conn.execute(text("""
                SELECT CONSTRAINT_NAME 
                FROM information_schema.TABLE_CONSTRAINTS 
                WHERE TABLE_NAME = 'rutinas' 
                AND CONSTRAINT_TYPE = 'FOREIGN KEY'
            """))
            foreign_key = result.fetchone()
            
            if foreign_key:
                # Eliminar la clave foránea
                conn.execute(text(f"""
                    ALTER TABLE rutinas 
                    DROP FOREIGN KEY {foreign_key[0]}
                """))
            
            # Luego eliminar la columna
            conn.execute(text("""
                ALTER TABLE rutinas 
                DROP COLUMN id_miembro
            """))
            
            conn.commit() 