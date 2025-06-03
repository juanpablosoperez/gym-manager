import os
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from gym_manager.models.backup import Backup
import traceback
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupService:
    """
    Servicio para gestionar los backups de la base de datos.
    
    Este servicio maneja la creación y gestión de backups
    de la base de datos MySQL.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        # Obtener la ruta absoluta del directorio del proyecto
        project_root = Path(__file__).parent.parent.parent
        self.backup_dir = project_root / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar el logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Crear manejador de archivo
        handler = logging.FileHandler('logs/backup.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Cargar variables de entorno del archivo .env.dev
        env_path = project_root / '.env.dev'
        load_dotenv(env_path, override=True)  # Forzar la sobrescritura de variables
        
        # Configuración de la base de datos
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        if not self.DATABASE_URL:
            raise Exception("No se encontró la variable de entorno DATABASE_URL")
            
        self.logger.info(f"[Backup] Usando base de datos: {self.DATABASE_URL}")
        
        # Crear engine con la misma configuración que el sistema principal
        self.engine = create_engine(
            self.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600
        )
        
        # Limpiar backups antiguos
        self._clean_old_backups()

    def _get_database_url(self) -> str:
        """Construye la URL de la base de datos a partir de las variables de entorno."""
        # No necesitamos cargar el .env.dev aquí porque ya se cargó en el constructor
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        DB_NAME = os.getenv('DB_NAME')
        
        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
            raise Exception("Faltan variables de entorno necesarias para la conexión a la base de datos")
        
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    def _clean_old_backups(self, max_backups: int = 10):
        """
        Elimina los backups antiguos manteniendo solo los últimos max_backups.
        
        Args:
            max_backups (int): Número máximo de backups a mantener
        """
        try:
            backups = self.get_backups()
            if len(backups) > max_backups:
                self.logger.info(f"[Cleanup] Limpiando backups antiguos (máximo: {max_backups})")
                for backup in backups[max_backups:]:
                    self.delete_backup(backup.id)
                self.logger.info(f"[Cleanup] Se eliminaron {len(backups) - max_backups} backups antiguos")
        except Exception as e:
            self.logger.error(f"[Cleanup] Error limpiando backups antiguos: {str(e)}")

    def create_backup(self, description: str = None, created_by: str = None) -> Backup:
        """
        Crea un nuevo backup de la base de datos.
        
        Args:
            description (str, optional): Descripción del backup
            created_by (str, optional): Usuario que crea el backup
            
        Returns:
            Backup: Objeto Backup creado
            
        Raises:
            Exception: Si hay un error al crear el backup
        """
        self.logger.info("[Backup] Iniciando creación de backup...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_name

        try:
            backup = Backup(
                name=backup_name,
                file_path=str(backup_path),
                size_mb=0,
                status='in_progress',
                description=description,
                created_by=created_by
            )
            self.db_session.add(backup)
            self.db_session.commit()

            self._write_backup_file(backup_path)

            # Validación final del archivo
            if not backup_path.exists() or backup_path.stat().st_size == 0:
                error_msg = "[Backup] El archivo está vacío o no se creó correctamente"
                self.logger.error(error_msg)
                backup.status = 'failed'
                backup.error_message = error_msg
                self.db_session.commit()
                raise Exception(error_msg)

            # Guardar tamaño final y estado
            backup.size_mb = backup_path.stat().st_size / (1024 * 1024)
            backup.status = 'completed'
            self.db_session.commit()

            self.logger.info(f"[Backup] Backup {backup_name} creado correctamente ({backup.size_mb:.2f} MB)")
            return backup

        except Exception as e:
            self.logger.error(f"[Backup] Error al crear backup: {str(e)}")
            if 'backup' in locals():
                backup.status = 'failed'
                backup.error_message = str(e)
                self.db_session.commit()
            raise

    def _write_backup_file(self, backup_path: Path):
        """Escribe el archivo de backup con la estructura y datos de la base de datos."""
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write("-- Backup generado por Gym Manager\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

            with self.engine.connect() as conn:
                # Obtener todas las tablas excepto 'backups'
                tables = [row[0] for row in conn.execute(text("SHOW TABLES")) if row[0] != 'backups']

                for table in tables:
                    self.logger.info(f"[Backup] Procesando tabla: {table}")

                    # Estructura de la tabla
                    create_stmt = conn.execute(text(f"SHOW CREATE TABLE {table}")).fetchone()[1]
                    # Modificar el CREATE TABLE para usar IF NOT EXISTS
                    create_stmt = create_stmt.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
                    f.write(f"-- Estructura de la tabla {table}\n")
                    f.write(f"{create_stmt};\n\n")

                    # Datos
                    # Obtener la clave primaria de la tabla
                    primary_key = None
                    try:
                        result = conn.execute(text(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'"))
                        primary_key = result.fetchone()
                        if primary_key:
                            primary_key = primary_key[4]  # El nombre de la columna está en el índice 4
                    except Exception as e:
                        self.logger.warning(f"[Backup] No se pudo obtener la clave primaria de {table}: {str(e)}")

                    # Construir la consulta con ORDER BY si hay clave primaria
                    query = f"SELECT * FROM {table}"
                    if primary_key:
                        query += f" ORDER BY {primary_key}"
                    
                    result = conn.execute(text(query))
                    rows = result.fetchall()
                    columns = result.keys()

                    if rows:
                        self.logger.info(f"[Backup] {len(rows)} filas encontradas en {table}")
                        f.write(f"-- Datos de la tabla {table}\n")

                        for row in rows:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    escaped = str(val).replace("'", "''")
                                    values.append(f"'{escaped}'")
                            
                            values_str = ', '.join(values)
                            columns_str = ', '.join(columns)
                            f.write(f"INSERT INTO {table} ({columns_str}) VALUES ({values_str});\n")
                        f.write("\n")
                    else:
                        self.logger.info(f"[Backup] Tabla {table} vacía")

    def get_backups(self) -> list[Backup]:
        """
        Obtiene la lista de todos los backups.
        
        Returns:
            list[Backup]: Lista de objetos Backup
        """
        return self.db_session.query(Backup).order_by(Backup.created_at.desc()).all()

    def delete_backup(self, backup_id: int) -> Tuple[bool, str]:
        """
        Elimina un backup específico.
        
        Args:
            backup_id (int): ID del backup a eliminar
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
            - éxito: True si la eliminación fue exitosa
            - mensaje: Mensaje descriptivo del resultado
            
        Raises:
            Exception: Si hay un error al eliminar el backup
        """
        self.logger.info(f"[Delete] Iniciando eliminación de backup ID: {backup_id}")
        
        backup = self.db_session.query(Backup).get(backup_id)
        if not backup:
            return False, "Backup no encontrado"
                
        try:
            # Eliminar archivo físico
            backup_path = Path(backup.file_path)
            if not backup_path.is_absolute():
                backup_path = self.backup_dir / backup_path.name
                
            if backup_path.exists():
                try:
                    backup_path.unlink()
                    self.logger.info(f"[Delete] Archivo físico eliminado: {backup_path}")
                except Exception as e:
                    self.logger.error(f"[Delete] Error eliminando archivo físico {backup_path}: {str(e)}")
                    return False, f"No se pudo eliminar el archivo físico: {str(e)}"
            else:
                self.logger.warning(f"[Delete] El archivo físico no existe: {backup_path}")
            
            # Eliminar registro de la base de datos
            self.db_session.delete(backup)
            self.db_session.commit()
            
            self.logger.info(f"[Delete] Backup eliminado exitosamente: {backup.name}")
            return True, "Backup eliminado exitosamente"
            
        except Exception as e:
            self.logger.error(f"[Delete] Error al eliminar backup: {str(e)}")
            self.db_session.rollback()
            return False, f"Error al eliminar backup: {str(e)}"

    def get_backup(self, backup_id: int) -> Backup:
        """
        Obtiene un backup específico.
        
        Args:
            backup_id (int): ID del backup a obtener
            
        Returns:
            Backup: Objeto Backup solicitado
            
        Raises:
            Exception: Si el backup no existe
        """
        backup = self.db_session.query(Backup).get(backup_id)
        if not backup:
            raise Exception("Backup no encontrado")
        return backup 