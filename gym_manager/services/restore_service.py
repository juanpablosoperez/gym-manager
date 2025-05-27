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
import sys
import flet as ft

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
        handler = logging.FileHandler('restore.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Cargar variables de entorno
        load_dotenv()
        
        # Configuración de la base de datos
        self.DATABASE_URL = self._get_database_url()
        self.engine = create_engine(self.DATABASE_URL)
        
        # Inicializar servicio de backup para crear backups de seguridad
        self.backup_service = BackupService(db_session)

    def _get_database_url(self) -> str:
        """Construye la URL de la base de datos a partir de las variables de entorno."""
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME', 'gym_manager')
        
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    def restore_backup(self, backup_id: int) -> bool:
        """
        Restaura un backup específico.
        
        Args:
            backup_id (int): ID del backup a restaurar
            
        Returns:
            bool: True si la restauración fue exitosa
            
        Raises:
            Exception: Si hay un error durante la restauración
        """
        self.logger.info(f"[Restore] Iniciando restauración del backup ID: {backup_id}")
        
        try:
            # Obtener el backup
            backup = self.db_session.query(Backup).get(backup_id)
            if not backup:
                raise Exception("Backup no encontrado")
                
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
                raise Exception(f"Archivo de backup no encontrado: {backup_path}")
            
            # Ejecutar la restauración
            self._execute_restore(backup_path)
            
            self.logger.info(f"[Restore] Backup {backup.name} restaurado exitosamente")
            
            # Mostrar mensaje de finalización en la interfaz gráfica
            if self.page:
                def close_app(e):
                    self.page.window_destroy()
                
                # Crear diálogo de éxito
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("¡RESTAURACIÓN COMPLETADA!"),
                    content=ft.Text(
                        "La restauración se ha completado correctamente.\n"
                        "Es necesario reiniciar la aplicación para que los cambios surtan efecto."
                    ),
                    actions=[
                        ft.TextButton("Cerrar aplicación", on_click=close_app)
                    ],
                    actions_alignment=ft.MainAxisAlignment.END
                )
                
                # Mostrar diálogo
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            
            return True
            
        except Exception as e:
            self.logger.error(f"[Restore] Error durante la restauración: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Mostrar error en la interfaz gráfica
            if self.page:
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Error en la restauración"),
                    content=ft.Text(f"Ocurrió un error durante la restauración: {str(e)}"),
                    actions=[
                        ft.TextButton("Aceptar", on_click=lambda e: setattr(dialog, 'open', False))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END
                )
                
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            
            raise

    def _execute_restore(self, backup_path: Path):
        """
        Ejecuta la restauración del backup.
        
        Args:
            backup_path (Path): Ruta al archivo de backup
            
        Raises:
            Exception: Si hay un error durante la ejecución
        """
        try:
            with self.engine.connect() as conn:
                # Deshabilitar verificación de claves foráneas
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                
                # Primero eliminar todas las tablas existentes
                self.logger.info("[Restore] Eliminando tablas existentes...")
                tables = [row[0] for row in conn.execute(text("SHOW TABLES")) if row[0] != 'backups']
                for table in tables:
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                        self.logger.info(f"[Restore] Tabla {table} eliminada")
                    except Exception as e:
                        self.logger.warning(f"[Restore] Error eliminando tabla {table}: {str(e)}")
                
                # Leer y ejecutar el archivo de backup
                self.logger.info("[Restore] Ejecutando comandos del backup...")
                with open(backup_path, 'r', encoding='utf-8') as f:
                    # Leer todo el contenido del archivo
                    content = f.read()
                    
                    # Dividir en comandos individuales
                    commands = content.split(';')
                    
                    # Ejecutar cada comando
                    for cmd in commands:
                        cmd = cmd.strip()
                        if cmd and not cmd.startswith('--'):  # Ignorar comentarios y líneas vacías
                            try:
                                # Ejecutar el comando y obtener el resultado
                                result = conn.execute(text(cmd))
                                
                                # Si es un INSERT, registrar cuántas filas se insertaron
                                if cmd.strip().upper().startswith('INSERT'):
                                    self.logger.info(f"[Restore] Filas insertadas: {result.rowcount}")
                                
                                # Hacer commit después de cada comando
                                conn.commit()
                                
                            except Exception as e:
                                self.logger.error(f"[Restore] Error ejecutando comando SQL: {str(e)}")
                                self.logger.error(f"[Restore] Comando que falló: {cmd}")
                                raise
                
                # Rehabilitar verificación de claves foráneas
                conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
                conn.commit()
                
                # Verificar que los datos se restauraron correctamente
                self.logger.info("[Restore] Verificando datos restaurados...")
                for table in ['usuarios', 'miembros', 'pagos', 'rutinas']:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        self.logger.info(f"[Restore] Tabla {table}: {count} registros")
                    except Exception as e:
                        self.logger.warning(f"[Restore] Error verificando tabla {table}: {str(e)}")
                
                self.logger.info("[Restore] Restauración completada exitosamente")
                
        except Exception as e:
            self.logger.error(f"[Restore] Error durante la ejecución: {str(e)}")
            raise 