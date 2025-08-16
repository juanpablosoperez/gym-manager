import os
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from gym_manager.models.backup import Backup
from gym_manager.services.backup_service import BackupService
import traceback
from typing import List, Optional, Tuple, Dict, Set
# from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import flet as ft
import sqlparse
import re
import base64
import sys

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
        
        # Directorio de datos/logs escribible del usuario
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent
        data_root = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'GymManager'
        data_root.mkdir(parents=True, exist_ok=True)
        log_dir = data_root / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear manejador de archivo
        handler = logging.FileHandler(str(log_dir / 'restore.log'))
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Cargar variables de entorno desde posibles ubicaciones
        # Usar configuración SQLite local
        from gym_manager.config import DATABASE_URL
        self.DATABASE_URL = DATABASE_URL
            
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
                # Intentar resolver en carpeta de datos de usuario primero
                data_root = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'GymManager' / 'backups'
                candidate = data_root / backup_path.name
                backup_path = candidate if candidate.exists() else (Path(__file__).parent.parent.parent / backup_path)
            
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

    def restore_backup_with_progress(self, backup_id: int, progress_callback=None) -> Tuple[bool, str]:
        """
        Restaura un backup específico con progreso.
        
        Args:
            backup_id (int): ID del backup a restaurar
            progress_callback: Función callback para actualizar el progreso
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
            - éxito: True si la restauración fue exitosa
            - mensaje: Mensaje descriptivo del resultado
        """
        self.logger.info(f"[Restore] Iniciando restauración del backup ID: {backup_id}")
        
        try:
            # Paso 1: Preparación (0%)
            if progress_callback:
                progress_callback(0, "Preparando restauración...", "Verificando backup y permisos", "~3 minutos")
            
            # Obtener el backup
            backup = self.db_session.query(Backup).get(backup_id)
            if not backup:
                return False, "Backup no encontrado"
                
            # Paso 2: Crear backup de seguridad (20%)
            if progress_callback:
                progress_callback(20, "Creando backup de seguridad...", "Respaldo del estado actual", "~2.5 minutos")
                
            security_backup = self.backup_service.create_backup(
                description="Backup de seguridad antes de restauración",
                created_by="system"
            )
            self.logger.info(f"[Restore] Backup de seguridad creado: {security_backup.name}")
            
            # Paso 3: Preparar archivo de backup (40%)
            if progress_callback:
                progress_callback(40, "Preparando archivo de backup...", "Validando integridad del archivo", "~2 minutos")
                
            backup_path = Path(backup.file_path)
            if not backup_path.is_absolute():
                data_root = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'GymManager' / 'backups'
                candidate = data_root / backup_path.name
                backup_path = candidate if candidate.exists() else (Path(__file__).parent.parent.parent / backup_path)
            
            if not backup_path.exists():
                return False, f"Archivo de backup no encontrado: {backup_path}"
            
            # Paso 4: Ejecutar restauración (40% - 90%)
            if progress_callback:
                progress_callback(40, "Iniciando restauración...", "Limpiando datos existentes", "~1.5 minutos")
                
            self._execute_restore_with_progress(backup_path, progress_callback)
            
            # Paso 5: Finalización (90% - 100%)
            if progress_callback:
                progress_callback(100, "Restauración completada", f"Backup {backup.name} restaurado exitosamente", "")
            
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
        conn = None
        cursor = None
        try:
            # Obtener una conexión directa a MySQL
            conn = self.engine.raw_connection()
            cursor = conn.cursor()
            
            self.logger.info(f"[Restore] Iniciando restauración desde: {backup_path}")
            
            # Obtener lista de tablas excluyendo backups
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name != 'backups'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Obtener dependencias de claves foráneas
            cursor.execute("""
                SELECT 
                    table_name,
                    referenced_table_name
                FROM information_schema.key_column_usage
                WHERE referenced_table_name IS NOT NULL
                AND table_schema = DATABASE()
            """)
            dependencies = cursor.fetchall()
            
            # Construir grafo de dependencias
            dependency_graph = {table: set() for table in tables}
            for table, referenced_table in dependencies:
                if referenced_table in dependency_graph:
                    dependency_graph[table].add(referenced_table)
            
            # Ordenar tablas por dependencias (topological sort)
            ordered_tables = []
            visited = set()
            
            def visit(table):
                if table in visited:
                    return
                visited.add(table)
                for dep in dependency_graph[table]:
                    visit(dep)
                ordered_tables.append(table)
            
            for table in tables:
                visit(table)
            
            # Eliminar datos en orden inverso
            self.logger.info("[Restore] Eliminando datos existentes...")
            for table in reversed(ordered_tables):
                try:
                    cursor.execute(f"DELETE FROM `{table}`")
                    self.logger.info(f"[Restore] Datos eliminados de la tabla: {table}")
                except Exception as e:
                    self.logger.error(f"[Restore] Error al eliminar datos de {table}: {str(e)}")
                    raise

            # Leer y parsear el archivo de backup línea por línea
            statements = []
            current_stmt = ""

            with open(backup_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith('--') or stripped.startswith('/*') or stripped.startswith('/*!'):
                        continue

                    current_stmt += line
                    if stripped.endswith(';'):
                        statements.append(current_stmt.strip())
                        current_stmt = ""

            # En caso de que haya una última sentencia sin punto y coma (raro, pero seguro)
            if current_stmt.strip():
                statements.append(current_stmt.strip())


            self.logger.info(f"[Restore] Se encontraron {len(statements)} sentencias SQL para ejecutar")
            if statements:
                self.logger.debug(f"[Restore] Primera sentencia: {statements[0]}")

            # Ejecutar cada sentencia
            for i, stmt in enumerate(statements, 1):
                try:
                    if not stmt:
                        continue
                    
                    self.logger.debug(f"[Restore] Ejecutando sentencia {i}/{len(statements)}")
                    cursor.execute(stmt)
                    
                except Exception as e:
                    self.logger.error(f"[Restore] Error en sentencia {i}: {str(e)}")
                    self.logger.error(f"[Restore] Sentencia problemática: {stmt}")
                    raise
            
            # Hacer commit de todos los cambios
            conn.commit()
            self.logger.info("[Restore] Restauración completada exitosamente")
            
        except Exception as e:
            self.logger.error(f"[Restore] Error durante la restauración: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _execute_restore_with_progress(self, backup_path: Path, progress_callback=None):
        """
        Ejecuta la restauración del backup con progreso.
        
        Args:
            backup_path (Path): Ruta al archivo de backup
            progress_callback: Función callback para actualizar el progreso
        """
        conn = None
        cursor = None
        try:
            # Obtener una conexión directa a MySQL
            conn = self.engine.raw_connection()
            cursor = conn.cursor()
            
            self.logger.info(f"[Restore] Iniciando restauración desde: {backup_path}")
            
            # Paso 1: Obtener lista de tablas (40% - 50%)
            if progress_callback:
                progress_callback(40, "Analizando estructura...", "Obteniendo lista de tablas", "~1.5 minutos")
                
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name != 'backups'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Obtener dependencias de claves foráneas
            cursor.execute("""
                SELECT 
                    table_name,
                    referenced_table_name
                FROM information_schema.key_column_usage
                WHERE referenced_table_name IS NOT NULL
                AND table_schema = DATABASE()
            """)
            dependencies = cursor.fetchall()
            
            # Construir grafo de dependencias
            dependency_graph = {table: set() for table in tables}
            for table, referenced_table in dependencies:
                if referenced_table in dependency_graph:
                    dependency_graph[table].add(referenced_table)
            
            # Ordenar tablas por dependencias (topological sort)
            ordered_tables = []
            visited = set()
            
            def visit(table):
                if table in visited:
                    return
                visited.add(table)
                for dep in dependency_graph[table]:
                    visit(dep)
                ordered_tables.append(table)
            
            for table in tables:
                visit(table)
            
            # Paso 2: Eliminar datos existentes (50% - 60%)
            if progress_callback:
                progress_callback(50, "Limpiando datos existentes...", "Eliminando registros actuales", "~1 minuto")
                
            self.logger.info("[Restore] Eliminando datos existentes...")
            for i, table in enumerate(reversed(ordered_tables)):
                try:
                    cursor.execute(f"DELETE FROM `{table}`")
                    self.logger.info(f"[Restore] Datos eliminados de la tabla: {table}")
                    
                    if progress_callback:
                        progress = 50 + (i / len(ordered_tables)) * 10  # 50% a 60%
                        progress_callback(progress, f"Limpiando tabla: {table}", f"Tabla {i+1} de {len(ordered_tables)}", "~45 segundos")
                        
                except Exception as e:
                    self.logger.error(f"[Restore] Error al eliminar datos de {table}: {str(e)}")
                    raise

            # Paso 3: Leer y parsear archivo de backup (60% - 70%)
            if progress_callback:
                progress_callback(60, "Procesando archivo de backup...", "Leyendo sentencias SQL", "~30 segundos")
                
            statements = []
            current_stmt = ""

            with open(backup_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith('--') or stripped.startswith('/*') or stripped.startswith('/*!'):
                        continue

                    current_stmt += line
                    if stripped.endswith(';'):
                        statements.append(current_stmt.strip())
                        current_stmt = ""

            if current_stmt.strip():
                statements.append(current_stmt.strip())

            self.logger.info(f"[Restore] Se encontraron {len(statements)} sentencias SQL para ejecutar")
            
            # Paso 4: Ejecutar sentencias (70% - 95%)
            if progress_callback:
                progress_callback(70, "Ejecutando sentencias SQL...", f"Procesando {len(statements)} sentencias", "~20 segundos")
                
            for i, stmt in enumerate(statements, 1):
                try:
                    if not stmt:
                        continue
                    
                    if progress_callback:
                        progress = 70 + (i / len(statements)) * 25  # 70% a 95%
                        progress_callback(progress, f"Ejecutando sentencia {i}/{len(statements)}", f"Procesando sentencia SQL", "~15 segundos")
                        
                    self.logger.debug(f"[Restore] Ejecutando sentencia {i}/{len(statements)}")
                    cursor.execute(stmt)
                    
                except Exception as e:
                    self.logger.error(f"[Restore] Error en sentencia {i}: {str(e)}")
                    self.logger.error(f"[Restore] Sentencia problemática: {stmt}")
                    raise
            
            # Paso 5: Finalizar (95% - 100%)
            if progress_callback:
                progress_callback(95, "Finalizando restauración...", "Haciendo commit de cambios", "~5 segundos")
                
            # Hacer commit de todos los cambios
            conn.commit()
            self.logger.info("[Restore] Restauración completada exitosamente")
            
        except Exception as e:
            self.logger.error(f"[Restore] Error durante la restauración: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
