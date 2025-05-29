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
            # Configurar timeout para la transacción
            with self.engine.begin() as conn:
                # Establecer timeout de 5 minutos
                conn.execute(text("SET SESSION wait_timeout=300"))
                
                # Deshabilitar verificación de claves foráneas
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                
                # Obtener todas las tablas y sus relaciones
                self.logger.info("[Restore] Obteniendo estructura de la base de datos...")
                tables_query = """
                    SELECT 
                        TABLE_NAME,
                        COLUMN_NAME,
                        REFERENCED_TABLE_NAME,
                        REFERENCED_COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE REFERENCED_TABLE_NAME IS NOT NULL
                    AND TABLE_SCHEMA = DATABASE()
                """
                foreign_keys = {}
                for row in conn.execute(text(tables_query)):
                    table = row[0]
                    if table not in foreign_keys:
                        foreign_keys[table] = []
                    foreign_keys[table].append({
                        'column': row[1],
                        'referenced_table': row[2],
                        'referenced_column': row[3]
                    })
                
                # Ordenar tablas por dependencias
                self.logger.info("[Restore] Ordenando tablas por dependencias...")
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
                    
                    # Diccionario para almacenar el máximo ID de cada tabla
                    max_ids = {}
                    failed_commands = []
                    
                    # Procesar y ejecutar comandos
                    for cmd in commands:
                        cmd = cmd.strip()
                        if not cmd:
                            continue
                            
                        try:
                            # Remover punto y coma final si existe
                            if cmd.endswith(';'):
                                cmd = cmd[:-1]
                            
                            # Procesar comandos INSERT
                            if cmd.strip().upper().startswith('INSERT'):
                                # Extraer partes del comando
                                parts = cmd.split('VALUES')
                                if len(parts) != 2:
                                    raise ValueError("Formato de INSERT inválido")
                                    
                                insert_part = parts[0].strip()
                                values_part = parts[1].strip()
                                
                                # Extraer nombre de tabla y columnas
                                table_name = insert_part.split('INTO')[1].split('(')[0].strip()
                                
                                # Ignorar comandos INSERT para la tabla backups
                                if table_name == 'backups':
                                    self.logger.info("[Restore] Ignorando comando INSERT para tabla backups")
                                    continue
                                
                                columns_part = insert_part[insert_part.find('('):insert_part.find(')')+1]
                                
                                # Construir parte UPDATE
                                update_parts = []
                                columns = columns_part.strip('()').split(',')
                                for col in columns:
                                    col = col.strip()
                                    update_parts.append(f"{col}=VALUES({col})")
                                
                                # Procesar cada grupo de valores
                                current_pos = 0
                                while current_pos < len(values_part):
                                    if values_part[current_pos] == '(':
                                        end_pos = current_pos + 1
                                        paren_count = 1
                                        while end_pos < len(values_part) and paren_count > 0:
                                            if values_part[end_pos] == '(':
                                                paren_count += 1
                                            elif values_part[end_pos] == ')':
                                                paren_count -= 1
                                            end_pos += 1
                                        
                                        value_group = values_part[current_pos:end_pos]
                                        
                                        # Procesar ID
                                        value_group_clean = value_group.strip('()')
                                        values = [v.strip() for v in value_group_clean.split(',')]
                                        if len(values) > 0:
                                            try:
                                                id_value = int(values[0])
                                                if table_name not in max_ids or id_value > max_ids[table_name]:
                                                    max_ids[table_name] = id_value
                                                    self.logger.info(f"[Restore] Nuevo máximo ID encontrado para {table_name}: {id_value}")
                                            except ValueError:
                                                self.logger.warning(f"[Restore] No se pudo convertir el ID a entero: {values[0]}")
                                        
                                        # Ejecutar INSERT individual
                                        single_cmd = f"{insert_part} VALUES {value_group} ON DUPLICATE KEY UPDATE {', '.join(update_parts)}"
                                        self.logger.info(f"[Restore] Ejecutando comando INSERT individual: {single_cmd}")
                                        result = conn.execute(text(single_cmd))
                                        self.logger.info(f"[Restore] Filas afectadas: {result.rowcount}")
                                        
                                        current_pos = end_pos
                                    else:
                                        current_pos += 1
                            
                            # Ejecutar otros comandos
                            else:
                                # Ignorar comandos que afecten a la tabla backups
                                if 'backups' in cmd.lower():
                                    self.logger.info("[Restore] Ignorando comando que afecta a la tabla backups")
                                    continue
                                    
                                result = conn.execute(text(cmd))
                                self.logger.info(f"[Restore] Comando ejecutado: {cmd}")
                                
                        except Exception as e:
                            self.logger.error(f"[Restore] Error ejecutando comando SQL: {str(e)}")
                            self.logger.error(f"[Restore] Comando que falló: {cmd}")
                            failed_commands.append((cmd, str(e)))
                            continue
                    
                    # Actualizar AUTO_INCREMENT para cada tabla
                    self.logger.info("[Restore] Actualizando AUTO_INCREMENT...")
                    for table, max_id in max_ids.items():
                        if max_id:
                            try:
                                next_id = max_id + 1
                                conn.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = {next_id}"))
                                self.logger.info(f"[Restore] AUTO_INCREMENT de {table} establecido en {next_id}")
                            except Exception as e:
                                self.logger.warning(f"[Restore] Error actualizando AUTO_INCREMENT de {table}: {str(e)}")
                
                # Rehabilitar verificación de claves foráneas
                conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
                
                # Verificar integridad de los datos restaurados
                self.logger.info("[Restore] Verificando integridad de datos...")
                for table, fks in foreign_keys.items():
                    try:
                        # Verificar conteo de registros
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        self.logger.info(f"[Restore] Tabla {table}: {count} registros")
                        
                        # Verificar claves foráneas
                        for fk in fks:
                            query = f"""
                                SELECT COUNT(*) FROM {table} t
                                LEFT JOIN {fk['referenced_table']} r 
                                ON t.{fk['column']} = r.{fk['referenced_column']}
                                WHERE r.{fk['referenced_column']} IS NULL
                                AND t.{fk['column']} IS NOT NULL
                            """
                            result = conn.execute(text(query))
                            orphaned = result.scalar()
                            if orphaned > 0:
                                self.logger.warning(
                                    f"[Restore] Se encontraron {orphaned} registros huérfanos en {table} "
                                    f"referenciando {fk['referenced_table']}"
                                )
                        
                    except Exception as e:
                        self.logger.warning(f"[Restore] Error verificando tabla {table}: {str(e)}")
                
                # Reportar comandos fallidos
                if failed_commands:
                    self.logger.warning("[Restore] Los siguientes comandos fallaron:")
                    for cmd, error in failed_commands:
                        self.logger.warning(f"[Restore] Comando: {cmd}")
                        self.logger.warning(f"[Restore] Error: {error}")
                
                # Registrar el backup restaurado en la tabla backups
                try:
                    # Verificar si el backup ya está registrado
                    backup_name = backup_path.name
                    existing_backup = self.db_session.query(Backup).filter_by(name=backup_name).first()
                    
                    if not existing_backup:
                        self.logger.info(f"[Restore] Registrando backup restaurado: {backup_name}")
                        backup = Backup(
                            name=backup_name,
                            file_path=str(backup_path),
                            size_mb=backup_path.stat().st_size / (1024 * 1024),
                            status='completed',
                            description="Backup restaurado",
                            created_by="system",
                            created_at=datetime.now()
                        )
                        self.db_session.add(backup)
                        self.db_session.commit()
                        self.logger.info(f"[Restore] Backup registrado exitosamente: {backup_name}")
                    else:
                        self.logger.info(f"[Restore] El backup {backup_name} ya está registrado")
                        
                except Exception as e:
                    self.logger.error(f"[Restore] Error registrando backup restaurado: {str(e)}")
                    # No lanzamos la excepción para no interrumpir el proceso de restauración
                
                self.logger.info("[Restore] Restauración completada exitosamente")
                
        except Exception as e:
            self.logger.error(f"[Restore] Error durante la ejecución: {str(e)}")
            raise 