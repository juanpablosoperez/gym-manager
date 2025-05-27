import flet as ft
from datetime import datetime
import os
from pathlib import Path
from gym_manager.services.backup_service import BackupService
import threading
from gym_manager.views.base_view import BaseView
import traceback
import logging
from gym_manager.models.backup import Backup
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BackupView(BaseView):
    def __init__(self, page: ft.Page, db_path: str, db_session):
        super().__init__(page)
        self.db_path = db_path
        self.db_session = db_session
        self.backup_service = BackupService(db_session)
        self.setup_backup_view()
        self.load_backups()

    def get_content(self):
        """Implementación del método requerido por BaseView"""
        return self.content

    def setup_backup_view(self):
        """Configura la vista de backup"""
        self.page.title = "Gestión de Backups"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_resizable = True
        self.page.window_maximizable = True
        self.page.window_minimizable = True

        # Crear botón para nuevo backup
        self.new_backup_button = ft.ElevatedButton(
            "Nuevo Backup",
            icon=ft.icons.BACKUP,
            on_click=self.create_backup
        )

        # Crear tabla de backups
        self.backup_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Tamaño")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Creado por")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]  # Las filas se actualizarán en load_backups
        )

        # Crear el contenido principal
        self.content = ft.Column(
            [
                ft.Row(
                    [self.new_backup_button],
                    alignment=ft.MainAxisAlignment.END
                ),
                self.backup_table
            ],
            spacing=20
        )

    def load_backups(self):
        """Carga la lista de backups"""
        try:
            backups = self.backup_service.get_backups()
            self.backup_table.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(backup.name)),
                        ft.DataCell(ft.Text(backup.created_at.strftime("%Y-%m-%d %H:%M:%S"))),
                        ft.DataCell(ft.Text(f"{backup.size_mb:.2f} MB")),
                        ft.DataCell(ft.Text(backup.status)),
                        ft.DataCell(ft.Text(backup.created_by or "Sistema")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Eliminar",
                                        on_click=lambda e, id=backup.id: self.delete_backup(id)
                                    )
                                ]
                            )
                        )
                    ]
                )
                for backup in backups
            ]
            
            # Actualizar la página
            self.page.update()
            logger.info("Tabla de backups actualizada exitosamente")
            
        except Exception as e:
            self._handle_error("Error cargando backups", e)

    def create_backup(self, e):
        """Crea un nuevo backup en un hilo separado"""
        try:
            # Deshabilitar botones durante la creación
            self._set_buttons_state(False)
            
            def backup_thread():
                try:
                    # Crear backup con descripción y usuario
                    backup = self.backup_service.create_backup(
                        description="Backup manual",
                        created_by="admin"  # TODO: Obtener usuario actual
                    )
                    
                    if backup.is_completed:
                        self.show_message("Backup creado exitosamente", ft.colors.GREEN)
                        # Actualizar la lista de backups inmediatamente después de crear uno nuevo
                        self.load_backups()
                        self.page.update()
                    else:
                        self.show_message(f"Error al crear backup: {backup.error_message}", ft.colors.RED)
                except Exception as e:
                    self.show_message(f"Error al crear backup: {str(e)}", ft.colors.RED)
                finally:
                    # Habilitar botones después de la creación
                    self._set_buttons_state(True)
                    self.page.update()
            
            # Iniciar backup en un hilo separado
            self.current_backup_thread = threading.Thread(target=backup_thread)
            self.current_backup_thread.start()
        except Exception as e:
            self.show_message(f"Error al iniciar el proceso de backup: {str(e)}", ft.colors.RED)
            self._set_buttons_state(True)

    def delete_backup(self, backup_id: int):
        """Elimina un backup específico"""
        try:
            if self.backup_service.delete_backup(backup_id):
                self.show_message("Backup eliminado exitosamente", ft.colors.GREEN)
                self.load_backups()
            else:
                self.show_message("Error al eliminar el backup", ft.colors.RED)
        except Exception as e:
            self.show_message(f"Error al eliminar el backup: {str(e)}", ft.colors.RED)

    def _set_buttons_state(self, enabled: bool):
        """Habilita o deshabilita los botones de la interfaz"""
        self.new_backup_button.disabled = not enabled
        self.page.update()

    def _handle_error(self, message: str, error: Exception):
        """Maneja los errores de la interfaz"""
        logger.error(f"{message}: {str(error)}")
        self.show_message(f"{message}: {str(error)}", ft.colors.RED)

    def show_message(self, content, bgcolor: str):
        """Muestra un mensaje en la interfaz"""
        try:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(content),
                bgcolor=bgcolor
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            print(f"Error mostrando mensaje: {str(e)}")
            print(traceback.format_exc()) 