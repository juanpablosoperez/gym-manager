import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from gym_manager.services.backup_service import BackupService

# Cargar variables de entorno
load_dotenv()

DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'gym_manager')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db_session = Session()

def main():
    try:
        backup_service = BackupService(db_session)
        backup = backup_service.create_backup(
            description="Backup limpio sin tabla de backups",
            created_by="sistema"
        )
        print(f"✅ Backup creado exitosamente: {backup.name}")
        print(f"ID del backup: {backup.id}")
    except Exception as e:
        print(f"❌ Error al crear el backup: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    main() 