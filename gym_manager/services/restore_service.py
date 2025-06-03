import os
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from gym_manager.models.backup import Backup
from gym_manager.services.backup_service import BackupService
import traceback
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import flet as ft
import sqlparse

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestoreService:
    """
    Servicio para restaurar backups de la base de datos.
    
    Este servicio maneja la restauración de backups
    de la base de datos MySQL.
    """
    
    def __init__(self, db_session: Session, page: ft.Page = None):
        self.db_session = db_session
        self.page = page
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Crear manejador de archivo
        handler = logging.FileHandler('logs/restore.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Cargar variables de entorno del archivo .env.dev
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / '.env.dev'
        load_dotenv(env_path, override=True)  # Forzar la sobrescritura de variables
        
        # Configuración de la base de datos
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        if not self.DATABASE_URL:
            raise Exception("No se encontró la variable de entorno DATABASE_URL")
            
        self.logger.info(f"[Restore] Usando base de datos: {self.DATABASE_URL}")
        
        # Crear engine con la misma configuración que el sistema principal
        self.engine = create_engine(
            self.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600
        )
        
        # Inicializar servicio de backup para crear backups de seguridad
        self.backup_service = BackupService(db_session)

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

    def restore_backup(self, backup_id: int) -> Tuple[bool, str]:
        """
        Restaura un backup específico.
        
        Args:
            backup_id (int): ID del backup a restaurar
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
            - éxito: True si la restauración fue exitosa
            - mensaje: Mensaje descriptivo del resultado
        """
        self.logger.info(f"[Restore] Iniciando restauración del backup ID: {backup_id}")
        
        try:
            # Obtener el backup
            backup = self.db_session.query(Backup).get(backup_id)
            if not backup:
                return False, "Backup no encontrado"
                
            # Crear backup de seguridad del estado actual
            self.logger.info("[Restore] Creando backup de seguridad del estado actual...")
            security_backup = self.backup_service.create_backup(
                description="Backup de seguridad antes de restauración",
                created_by="system"
            )
            self.logger.info(f"[Restore] Backup de seguridad creado: {security_backup.name}")
            
            # Preparar el backup
            backup_path = Path(backup.file_path)
            if not backup_path.is_absolute():
                backup_path = Path(__file__).parent.parent.parent / backup_path
            
            if not backup_path.exists():
                return False, f"Archivo de backup no encontrado: {backup_path}"
            
            # Ejecutar la restauración
            self._execute_restore(backup_path)
            
            self.logger.info(f"[Restore] Backup {backup.name} restaurado exitosamente")
            return True, "La restauración se ha completado correctamente."
            
        except Exception as e:
            self.logger.error(f"[Restore] Error durante la restauración: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Ocurrió un error durante la restauración: {str(e)}"

    def _execute_restore(self, backup_path: Path):
        """
        Ejecuta la restauración del backup.
        
        Args:
            backup_path (Path): Ruta al archivo de backup
        """
        try:
            with self.engine.connect() as conn:
                # Obtener todas las tablas y sus claves foráneas
                self.logger.info("[Restore] Obteniendo información de tablas...")
                foreign_keys = {}
                for row in conn.execute(text("""
                    SELECT 
                        TABLE_NAME,
                        REFERENCED_TABLE_NAME
                    FROM
                        INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE
                        REFERENCED_TABLE_NAME IS NOT NULL
                        AND TABLE_SCHEMA = DATABASE()
                """)):
                    if row[0] not in foreign_keys:
                        foreign_keys[row[0]] = []
                    foreign_keys[row[0]].append({
                        'referenced_table': row[1]
                    })

                # Ordenar tablas para evitar problemas con claves foráneas
                ordered_tables = []
                processed = set()
                
                def process_table(table):
                    if table in processed:
                        return
                    if table in foreign_keys:
                        for fk in foreign_keys[table]:
                            process_table(fk['referenced_table'])
                    ordered_tables.append(table)
                    processed.add(table)
                
                # Obtener todas las tablas excepto 'backups'
                all_tables = [row[0] for row in conn.execute(text("SHOW TABLES")) if row[0] != 'backups']
                for table in all_tables:
                    process_table(table)
                
                # Eliminar datos en orden inverso
                self.logger.info("[Restore] Limpiando datos existentes...")
                for table in reversed(ordered_tables):
                    try:
                        conn.execute(text(f"DELETE FROM {table}"))
                        self.logger.info(f"[Restore] Datos eliminados de tabla {table}")
                    except Exception as e:
                        self.logger.warning(f"[Restore] Error al limpiar tabla {table}: {str(e)}")
                
                # Leer y ejecutar el archivo de backup
                self.logger.info("[Restore] Ejecutando comandos del backup...")
                with open(backup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Limpiar el contenido del archivo
                    self.logger.info("[Restore] Limpiando contenido del archivo...")
                    content = '\n'.join(line for line in content.split('\n') 
                                      if line.strip() and not line.strip().startswith('--'))
                    
                    # Usar sqlparse para dividir los comandos SQL
                    commands = sqlparse.split(content)
                    
                    # Procesar y ejecutar comandos
                    for cmd in commands:
                        if cmd.strip():
                            try:
                                conn.execute(text(cmd))
                                conn.commit()
                            except Exception as e:
                                self.logger.error(f"[Restore] Error ejecutando comando: {str(e)}")
                                self.logger.error(f"Comando: {cmd}")
                                raise
                
                self.logger.info("[Restore] Restauración completada exitosamente")
                
        except Exception as e:
            self.logger.error(f"[Restore] Error durante la ejecución: {str(e)}")
            raise 