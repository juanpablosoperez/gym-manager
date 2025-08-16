import os
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from gym_manager.models.backup import Backup
import traceback
from typing import List, Optional, Tuple
# from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import base64
import sys

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
        # Resolver base del proyecto compatible con exe empaquetado
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent
        project_root = base_dir
        # Ubicación de datos escribible por el usuario
        data_root = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'GymManager'
        data_root.mkdir(parents=True, exist_ok=True)
        self.backup_dir = data_root / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar el logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Crear directorio de logs en ubicación escribible
        log_dir = data_root / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear manejador de archivo
        handler = logging.FileHandler(str(log_dir / 'backup.log'))
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Usar configuración SQLite local
        from gym_manager.config import DATABASE_URL
        self.DATABASE_URL = DATABASE_URL
            
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
            self.logger.error(traceback.format_exc())

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
                raise ValueError(error_msg)

            # Guardar tamaño final y estado
            backup.size_mb = backup_path.stat().st_size / (1024 * 1024)
            backup.status = 'completed'
            self.db_session.commit()

            self.logger.info(f"[Backup] Backup {backup_name} creado correctamente ({backup.size_mb:.2f} MB)")
            return backup

        except Exception as e:
            self.logger.error(f"[Backup] Error al crear backup: {str(e)}")
            self.logger.error(traceback.format_exc())
            if 'backup' in locals():
                backup.status = 'failed'
                backup.error_message = str(e)
                self.db_session.commit()
            raise

    def create_backup_with_progress(self, progress_callback=None, description: str = None, created_by: str = None) -> Backup:
        """
        Crea un nuevo backup de la base de datos con progreso.
        
        Args:
            progress_callback: Función callback para actualizar el progreso
            description (str, optional): Descripción del backup
            created_by (str, optional): Usuario que crea el backup
            
        Returns:
            Backup: Objeto Backup creado
            
        Raises:
            Exception: Si hay un error al crear el backup
        """
        self.logger.info("[Backup] Iniciando creación de backup con progreso...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_name

        try:
            # Paso 1: Inicialización (0%)
            if progress_callback:
                progress_callback(0, "Inicializando backup...", "Preparando archivo y estructura", "~2 minutos")
            
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

            # Inicializar archivo de backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write("-- Backup generado por Gym Manager\n")
                f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

            # Paso 2: Obtener estructura de tablas (20%)
            if progress_callback:
                progress_callback(20, "Obteniendo estructura de tablas...", "Analizando esquema de la base de datos", "~1.5 minutos")
            
            with self.engine.connect() as conn:
                tables = [row[0] for row in conn.execute(text("SHOW TABLES")) if row[0] != 'backups']
                total_tables = len(tables)
                
                # Paso 3: Procesar cada tabla (20% - 90%)
                for i, table in enumerate(tables):
                    if progress_callback:
                        progress = 20 + (i / total_tables) * 70  # 20% a 90%
                        progress_callback(
                            progress, 
                            f"Procesando tabla: {table}", 
                            f"Tabla {i+1} de {total_tables} ({table})", 
                            f"~{int((total_tables - i) * 0.5)} minutos"
                        )
                    
                    self._write_table_to_backup(conn, table, backup_path)
                    
                    # Verificar si fue cancelado
                    if progress_callback and hasattr(progress_callback, 'is_cancelled') and progress_callback.is_cancelled():
                        raise Exception("Operación cancelada por el usuario")

            # Paso 4: Finalización (90% - 100%)
            if progress_callback:
                progress_callback(90, "Finalizando backup...", "Validando archivo y calculando tamaño", "~30 segundos")

            # Cerrar formalmente el archivo de backup
            with open(backup_path, 'a', encoding='utf-8') as f:
                f.write("-- Fin del backup\n")
                f.write("\n")

            # Validación final del archivo
            if not backup_path.exists() or backup_path.stat().st_size == 0:
                error_msg = "[Backup] El archivo está vacío o no se creó correctamente"
                self.logger.error(error_msg)
                backup.status = 'failed'
                backup.error_message = error_msg
                self.db_session.commit()
                raise ValueError(error_msg)

            # Guardar tamaño final y estado
            backup.size_mb = backup_path.stat().st_size / (1024 * 1024)
            backup.status = 'completed'
            self.db_session.commit()

            if progress_callback:
                progress_callback(100, "Backup completado", f"Archivo: {backup_name} ({backup.size_mb:.2f} MB)", "")

            self.logger.info(f"[Backup] Backup {backup_name} creado correctamente ({backup.size_mb:.2f} MB)")
            return backup

        except Exception as e:
            self.logger.error(f"[Backup] Error al crear backup: {str(e)}")
            self.logger.error(traceback.format_exc())
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

                    # Obtener información de las columnas
                    columns_info = conn.execute(text(f"SHOW COLUMNS FROM {table}")).fetchall()
                    blob_columns = [col[0] for col in columns_info if 'BLOB' in col[1].upper()]
                    
                    if blob_columns:
                        self.logger.info(f"[Backup] Columnas BLOB detectadas en {table}: {', '.join(blob_columns)}")

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
                            for col_name, val in zip(columns, row):
                                if val is None:
                                    values.append("NULL")
                                elif col_name in blob_columns and isinstance(val, bytes):
                                    # Codificar BLOB en Base64
                                    encoded = base64.b64encode(val).decode('utf-8')
                                    values.append(f"'{encoded}'")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    escaped = str(val).replace("'", "''")
                                    values.append(f"'{escaped}'")
                            
                            values_str = ', '.join(values)
                            columns_str = ', '.join(f"`{col}`" for col in columns)
                            f.write(f"INSERT INTO `{table}` ({columns_str}) VALUES ({values_str});\n")
                        f.write("\n")
                    else:
                        self.logger.info(f"[Backup] Tabla {table} vacía")
                   
            # Cierre formal del archivo de backup
            f.write("-- Fin del backup\n")
            f.write("\n")

    def _write_table_to_backup(self, conn, table: str, backup_path: Path):
        """Escribe una tabla específica al archivo de backup"""
        with open(backup_path, 'a', encoding='utf-8') as f:
            self.logger.info(f"[Backup] Procesando tabla: {table}")

            # Estructura de la tabla
            create_stmt = conn.execute(text(f"SHOW CREATE TABLE {table}")).fetchone()[1]
            create_stmt = create_stmt.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
            f.write(f"-- Estructura de la tabla {table}\n")
            f.write(f"{create_stmt};\n\n")

            # Obtener información de las columnas
            columns_info = conn.execute(text(f"SHOW COLUMNS FROM {table}")).fetchall()
            blob_columns = [col[0] for col in columns_info if 'BLOB' in col[1].upper()]
            
            if blob_columns:
                self.logger.info(f"[Backup] Columnas BLOB detectadas en {table}: {', '.join(blob_columns)}")

            # Datos
            primary_key = None
            try:
                result = conn.execute(text(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'"))
                primary_key = result.fetchone()
                if primary_key:
                    primary_key = primary_key[4]
            except Exception as e:
                self.logger.warning(f"[Backup] No se pudo obtener la clave primaria de {table}: {str(e)}")

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
                    for col_name, val in zip(columns, row):
                        if val is None:
                            values.append("NULL")
                        elif col_name in blob_columns and isinstance(val, bytes):
                            encoded = base64.b64encode(val).decode('utf-8')
                            values.append(f"'{encoded}'")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            escaped = str(val).replace("'", "''")
                            values.append(f"'{escaped}'")
                    
                    values_str = ', '.join(values)
                    columns_str = ', '.join(f"`{col}`" for col in columns)
                    f.write(f"INSERT INTO `{table}` ({columns_str}) VALUES ({values_str});\n")
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
            self.logger.error(traceback.format_exc())
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
            raise ValueError("Backup no encontrado")
        return backup 