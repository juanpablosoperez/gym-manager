import flet as ft
from datetime import datetime
import os
from pathlib import Path
from gym_manager.services.backup_service import BackupService
from gym_manager.services.restore_service import RestoreService
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
        self.restore_service = RestoreService(db_session, page=page)
        self.current_backup_thread: Optional[threading.Thread] = None
        
        # Definir diálogo de restauración
        self.restore_dialog = ft.AlertDialog(
            title=ft.Text("Restaurar Backup"),
            content=ft.Column([
                ft.Text("", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Detalles del backup:", size=14, weight=ft.FontWeight.W_500),
                ft.Text("Nombre: ", size=14),
                ft.Text("Fecha: ", size=14),
                ft.Text("Tamaño: ", size=14),
                ft.Text("Creado por: ", size=14),
                ft.Text("\n¿Estás seguro de que deseas restaurar este backup?\nEsta acción no se puede deshacer.", size=14, color=ft.colors.RED),
            ], spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._close_dialog(self.restore_dialog)),
                ft.TextButton("Restaurar", on_click=self._restore_backup),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Definir diálogo de éxito en restauración
        self.restore_success_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("¡RESTAURACIÓN COMPLETADA!", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(
                    "La restauración del backup se completó correctamente.",
                    size=16
                ),
                ft.Text(
                    "Por favor, cierre la aplicación manualmente para finalizar el proceso.",
                    size=16,
                    color=ft.colors.BLUE
                )
            ], spacing=10),
            actions=[],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # Definir diálogo de error en restauración
        self.restore_error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error en la restauración", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text("", size=16),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda e: self._close_dialog(self.restore_error_dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Agregar diálogos a la página
        self.page.overlay.extend([
            self.restore_dialog,
            self.restore_success_dialog,
            self.restore_error_dialog
        ])
        
        self.setup_backup_view()
        self.load_backups()

    def get_content(self):
        """Implementación del método requerido por BaseView"""
        return self.content

    def _close_dialog(self, dialog: ft.AlertDialog):
        """Cierra un diálogo y actualiza la página"""
        dialog.open = False
        self.page.update()

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
                        ft.DataCell(ft.Text(
                            backup.status,
                            color=ft.colors.GREEN if backup.is_completed else 
                                  ft.colors.RED if backup.is_failed else 
                                  ft.colors.ORANGE
                        )),
                        ft.DataCell(ft.Text(backup.created_by or "Sistema")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.RESTORE,
                                        tooltip="Restaurar",
                                        on_click=lambda e, id=backup.id: self.show_restore_dialog(id),
                                        disabled=not backup.is_completed
                                    ),
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

    def show_restore_dialog(self, backup_id: int):
        """Muestra el diálogo de confirmación para restaurar un backup"""
        try:
            # Buscar el backup en la base de datos
            backup = self.backup_service.get_backup(backup_id)
            if not backup:
                self.show_message("Backup no encontrado", ft.colors.RED)
                return

            # Actualizar el contenido del diálogo con los detalles del backup
            self.restore_dialog.content.controls[0].value = backup.name  # Título
            self.restore_dialog.content.controls[2].value = f"Nombre: {backup.name}"
            self.restore_dialog.content.controls[3].value = f"Fecha: {backup.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            self.restore_dialog.content.controls[4].value = f"Tamaño: {backup.size_mb:.2f} MB"
            self.restore_dialog.content.controls[5].value = f"Creado por: {backup.created_by or 'Sistema'}"

            # Guardar el ID del backup para la restauración
            self.restore_dialog.content.value = str(backup_id)

            # Mostrar el diálogo
            self.restore_dialog.open = True
            self.page.update()

        except Exception as e:
            self._handle_error("Error al mostrar diálogo de restauración", e)

    def _restore_backup(self, e):
        """Restaura el backup seleccionado"""
        try:
            backup_id = int(self.restore_dialog.content.value)
            self._close_dialog(self.restore_dialog)
            
            # Deshabilitar botones durante la restauración
            self._set_buttons_state(False)
            
            def restore_thread():
                try:
                    success, message = self.restore_service.restore_backup(backup_id)
                    
                    if success:
                        # Mostrar diálogo de éxito
                        self.page.dialog = self.restore_success_dialog
                        self.restore_success_dialog.open = True
                    else:
                        # Actualizar y mostrar diálogo de error
                        self.restore_error_dialog.content.value = message
                        self.page.dialog = self.restore_error_dialog
                        self.restore_error_dialog.open = True
                    
                    self.page.update()
                    
                except Exception as e:
                    self.show_message(f"Error al restaurar el backup: {str(e)}", ft.colors.RED)
                finally:
                    self._set_buttons_state(True)
                    self.page.update()
            
            # Iniciar restauración en un hilo separado
            self.current_backup_thread = threading.Thread(target=restore_thread)
            self.current_backup_thread.start()
            
        except Exception as e:
            self._handle_error("Error al restaurar backup", e)
            self._set_buttons_state(True)

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
        for row in self.backup_table.rows:
            for cell in row.cells:
                if isinstance(cell.content, ft.Row):
                    for button in cell.content.controls:
                        if isinstance(button, ft.IconButton):
                            button.disabled = not enabled
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