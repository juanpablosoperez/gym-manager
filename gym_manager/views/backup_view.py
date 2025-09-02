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

class BackupProgressModal:
    def __init__(self, page: ft.Page):
        self.page = page
        self.progress_bar = ft.ProgressBar(width=400)
        self.status_text = ft.Text("", size=16)
        self.detail_text = ft.Text("", size=14, color=ft.colors.GREY_600)
        self.time_estimate = ft.Text("", size=12, color=ft.colors.GREY_500)
        self.cancel_button = ft.TextButton(
            "Cancelar Operación", 
            on_click=self.cancel_operation,
            style=ft.ButtonStyle(color=ft.colors.RED_600)
        )
        self.cancelled = False
        
        self.modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Procesando...", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                self.progress_bar,
                self.status_text,
                self.detail_text,
                self.time_estimate,
                self.cancel_button
            ], spacing=15),
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def show(self, title: str = "Procesando..."):
        """Muestra el modal de progreso"""
        self.modal.title.value = title
        self.progress_bar.value = 0
        self.status_text.value = "Iniciando..."
        self.detail_text.value = ""
        self.time_estimate.value = ""
        self.cancelled = False
        self.modal.open = True
        self.page.update()
    
    def hide(self):
        """Oculta el modal de progreso"""
        self.modal.open = False
        self.page.update()
    
    def update_progress(self, progress: float, status: str, detail: str = "", time_estimate: str = ""):
        """Actualiza el progreso del modal"""
        if self.cancelled:
            return
        
        self.progress_bar.value = progress / 100
        self.status_text.value = status
        self.detail_text.value = detail
        self.time_estimate.value = time_estimate
        self.page.update()
    
    def cancel_operation(self, e):
        """Cancela la operación en curso"""
        self.cancelled = True
        self.status_text.value = "Cancelando..."
        self.detail_text.value = "Esperando que termine la operación actual..."
        self.cancel_button.disabled = True
        self.page.update()
    
    def is_cancelled(self) -> bool:
        """Verifica si la operación fue cancelada"""
        return self.cancelled

class BackupView(BaseView):
    def __init__(self, page: ft.Page, db_path: str, db_session, current_user: str = "Sistema"):
        super().__init__(page)
        self.db_path = db_path
        self.db_session = db_session
        self.current_user = current_user  # Usuario logueado actualmente
        self.backup_service = BackupService(db_session)
        self.restore_service = RestoreService(db_session, page=page)
        self.current_backup_thread: Optional[threading.Thread] = None
        self.backup_to_delete_id: Optional[int] = None
        
        # Inicializar paginación ANTES de setup_backup_view
        from gym_manager.utils.pagination import PaginationController, PaginationWidget
        self.pagination_controller = PaginationController(items_per_page=10)
        self.pagination_widget = PaginationWidget(
            self.pagination_controller, 
            on_page_change=self._on_page_change
        )
        
        # Inicializar modal de progreso
        self.progress_modal = BackupProgressModal(page)
        
        # Definir diálogo de restauración
        self.restore_dialog = ft.AlertDialog(
            title=ft.Text("Restaurar Backup"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Detalles del backup:", size=14, weight=ft.FontWeight.W_500),
                    ft.Text("Nombre: ", size=14),
                    ft.Text("Fecha: ", size=14),
                    ft.Text("Tamaño: ", size=14),
                    ft.Text("Creado por: ", size=14),
                    ft.Text("\n¿Estás seguro de que deseas restaurar este backup?\nEsta acción no se puede deshacer.", size=14, color=ft.colors.RED),
                ], spacing=10),
                width=500,
                height=350
            ),
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

        # Definir diálogo de confirmación de eliminación
        self.delete_confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Detalles del backup:", size=14, weight=ft.FontWeight.W_500),
                    ft.Text("Nombre: ", size=14),
                    ft.Text("Fecha: ", size=14),
                    ft.Text("Tamaño: ", size=14),
                    ft.Text("Creado por: ", size=14),
                    ft.Text("\n¿Estás seguro de que deseas eliminar este backup?\nEsta acción no se puede deshacer.", size=14, color=ft.colors.RED),
                ], spacing=10),
                width=450,
                height=300
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._close_dialog(self.delete_confirm_dialog)),
                ft.TextButton("Eliminar", on_click=self._confirm_delete_backup, style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Agregar diálogos a la página
        self.page.overlay.extend([
            self.progress_modal.modal,
            self.restore_dialog,
            self.restore_success_dialog,
            self.restore_error_dialog,
            self.delete_confirm_dialog
        ])
        
        self.setup_backup_view()
        self.load_backups()

    def get_content(self):
        """Implementación del método requerido por BaseView"""
        # Llamar load_backups después de que la vista esté completamente inicializada
        self.page.loop.create_task(self._load_backups_async())
        return self.content
    
    async def _load_backups_async(self):
        """Carga los backups de forma asíncrona después de que la vista esté lista"""
        try:
            # Pequeño delay para asegurar que la vista esté completamente renderizada
            import asyncio
            await asyncio.sleep(0.1)
            
            backups = self.backup_service.get_backups()
            
            # Actualizar paginación
            self.pagination_controller.set_items(backups)
            self.pagination_controller.current_page = 1
            self.pagination_widget.update_items(backups)
            
            # Actualizar tabla
            self.update_backups_table()
            
        except Exception as e:
            self.show_error_message(f"Error al cargar los backups: {str(e)}")
    
    def _on_page_change(self):
        """Callback cuando cambia la página"""
        self.update_backups_table()

    def _close_dialog(self, dialog: ft.AlertDialog):
        """Cierra un diálogo y actualiza la página"""
        dialog.open = False
        self.page.update()

    def setup_backup_view(self):
        """Configura la vista de backup"""
        self.page.title = "Gestión de Backups"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        # No configurar la ventana aquí para evitar sobrescribir la maximización
        # La configuración de ventana se maneja en navigation.py

        # Título principal (alineado a MembersView)
        self.welcome_title = ft.Text(
            "¡Administra y consulta tus backups!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        # Crear botón para nuevo backup (alta)
        self.new_backup_button = ft.ElevatedButton(
            "Nuevo Backup",
            icon=ft.icons.BACKUP,
            on_click=self.create_backup,
            tooltip="Crear un nuevo backup de la base de datos",
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE,
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
        )

        # Contador de registros (como MembersView)
        self.records_counter = ft.Text(
            "0 backups",
            size=14,
            color=ft.colors.GREY_600,
            weight=ft.FontWeight.W_500,
        )

        # Crear tabla de backups
        self.backup_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tamaño", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Creado por", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", size=18, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=12,
            vertical_lines=ft.border.all(1, ft.colors.GREY_300),
            horizontal_lines=ft.border.all(1, ft.colors.GREY_300),
            column_spacing=100,
            heading_row_color=ft.colors.GREY_100,
            heading_row_height=60,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=56,
            expand=True,
        )

        # Layout principal
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    # Encabezado (título a la izquierda, alta a la derecha)
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.welcome_title,
                                ft.Row([self.new_backup_button], alignment=ft.MainAxisAlignment.END),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=20, top=20, left=20, right=20),
                        alignment=ft.alignment.top_left,
                    ),
                    ft.Container(
                        content=self.backup_table,
                        padding=ft.padding.symmetric(horizontal=20),
                        height=600,
                        alignment=ft.alignment.top_left,
                        expand=True,
                    ),
                    # Widget de paginación
                    ft.Container(
                        content=self.pagination_widget.get_widget(),
                        padding=ft.padding.only(top=20, bottom=20),
                        alignment=ft.alignment.center,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
            padding=0,
            bgcolor=ft.colors.WHITE,
        )

    def load_backups(self):
        """Carga la lista de backups"""
        try:
            backups = self.backup_service.get_backups()
            self.pagination_controller.set_items(backups)
            self.pagination_controller.current_page = 1
            self.pagination_widget.update_items(backups)
            self.update_backups_table()
        except Exception as e:
            self._handle_error("Error cargando backups", e)
    
    def update_backups_table(self, backups=None):
        """Actualiza la tabla de backups con paginación"""
        try:
            # Obtener backups de la página actual
            if backups is None:
                backups = self.pagination_controller.get_current_page_items()
            
            # Actualizar contador de registros
            count = len(backups)
            self.records_counter.value = f"{count} {'backup' if count == 1 else 'backups'}"

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
            
            # Actualizar la página y forzar scroll al tope
            self.page.update()
            try:
                if hasattr(self.page, "scroll_to"):
                    self.page.scroll_to(0)
            except Exception:
                pass
            logger.info("Tabla de backups actualizada exitosamente")
            
        except Exception as e:
            self._handle_error("Error al actualizar la tabla de backups", e)

    def show_restore_dialog(self, backup_id: int):
        """Muestra el diálogo de confirmación para restaurar un backup"""
        try:
            # Buscar el backup en la base de datos
            backup = self.backup_service.get_backup(backup_id)
            if not backup:
                self.show_message("Backup no encontrado", ft.colors.RED)
                return

            # Actualizar el contenido del diálogo con los detalles del backup
            # Acceder al contenido del Container que envuelve la Column
            column_content = self.restore_dialog.content.content
            column_content.controls[0].value = backup.name  # Título
            column_content.controls[2].value = f"Nombre: {backup.name}"
            column_content.controls[3].value = f"Fecha: {backup.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            column_content.controls[4].value = f"Tamaño: {backup.size_mb:.2f} MB"
            column_content.controls[5].value = f"Creado por: {backup.created_by or 'Sistema'}"

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
            
            # Mostrar modal de progreso
            self.progress_modal.show("Restaurando backup...")
            
            def progress_callback(progress, status, detail, time_estimate):
                self.progress_modal.update_progress(progress, status, detail, time_estimate)
            
            def restore_thread():
                try:
                    success, message = self.restore_service.restore_backup_with_progress(
                        backup_id, 
                        progress_callback=progress_callback
                    )
                    
                    self.progress_modal.hide()
                    
                    if success:
                        # Mostrar diálogo de éxito
                        self.page.dialog = self.restore_success_dialog
                        self.restore_success_dialog.open = True
                    else:
                        # Mostrar mensaje de error
                        self.show_error_message(f"Error en la restauración: {message}")
                    
                    self.page.update()
                    
                except Exception as e:
                    self.progress_modal.hide()
                    self.show_error_message(f"Error al restaurar el backup: {str(e)}")
            
            # Iniciar restauración en un hilo separado
            self.current_backup_thread = threading.Thread(target=restore_thread)
            self.current_backup_thread.start()
            
        except Exception as e:
            self._handle_error("Error al restaurar backup", e)

    def create_backup(self, e):
        """Crea un nuevo backup"""
        try:
            # Mostrar modal de progreso
            self.progress_modal.show("Creando backup...")
            
            def progress_callback(progress, status, detail, time_estimate):
                self.progress_modal.update_progress(progress, status, detail, time_estimate)
            
            def backup_thread():
                try:
                    backup = self.backup_service.create_backup_with_progress(
                        progress_callback=progress_callback,
                        created_by=self.current_user
                    )
                    self.progress_modal.hide()
                    self.show_success_message(f"Backup creado exitosamente: {backup.name}")
                    self.load_backups()  # Recargar la lista
                except Exception as e:
                    self.progress_modal.hide()
                    self.show_error_message(f"Error al crear backup: {str(e)}")
            
            # Iniciar backup en un hilo separado
            self.current_backup_thread = threading.Thread(target=backup_thread)
            self.current_backup_thread.start()
            
        except Exception as e:
            self._handle_error("Error al crear backup", e)

    def delete_backup(self, backup_id: int):
        """Muestra el modal de confirmación para eliminar un backup"""
        try:
            # Buscar el backup en la base de datos
            backup = self.backup_service.get_backup(backup_id)
            if not backup:
                self.show_message("Backup no encontrado", ft.colors.RED)
                return

            # Actualizar el contenido del diálogo con los detalles del backup
            column_content = self.delete_confirm_dialog.content.content
            column_content.controls[0].value = backup.name  # Título
            column_content.controls[2].value = f"Nombre: {backup.name}"
            column_content.controls[3].value = f"Fecha: {backup.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            column_content.controls[4].value = f"Tamaño: {backup.size_mb:.2f} MB"
            column_content.controls[5].value = f"Creado por: {backup.created_by or 'Sistema'}"

            # Guardar el ID del backup para la eliminación
            self.backup_to_delete_id = backup_id

            # Mostrar el diálogo
            self.delete_confirm_dialog.open = True
            self.page.update()

        except Exception as e:
            self._handle_error("Error al mostrar diálogo de eliminación", e)

    def _confirm_delete_backup(self, e):
        """Confirma y ejecuta la eliminación del backup"""
        try:
            backup_id = self.backup_to_delete_id
            if backup_id is None:
                self.show_error_message("No se ha seleccionado ningún backup para eliminar")
                return
            
            self._close_dialog(self.delete_confirm_dialog)
            
            # Ejecutar la eliminación
            success, message = self.backup_service.delete_backup(backup_id)
            if success:
                self.show_success_message("Backup eliminado exitosamente")
                self.load_backups()  # Recargar la lista
            else:
                self.show_error_message(f"Error al eliminar backup: {message}")
                
        except Exception as e:
            self._handle_error("Error al eliminar backup", e)

    def _set_buttons_state(self, enabled: bool):
        """Habilita o deshabilita los botones de la interfaz"""
        self.new_backup_button.disabled = not enabled
        for row in self.backup_table.rows:
            for cell in row.cells:
                if isinstance(cell.content, ft.Row):
                    for button in cell.content.controls:
                        button.disabled = not enabled
        self.page.update()

    def _handle_error(self, message: str, error: Exception):
        """Maneja los errores mostrando un mensaje y registrándolos"""
        error_msg = f"{message}: {str(error)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        self.show_message(error_msg, ft.colors.RED)

    def show_message(self, content, bgcolor: str):
        """Muestra un mensaje en la interfaz"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(content),
            bgcolor=bgcolor
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_success_message(self, message: str):
        """Muestra un mensaje de éxito"""
        self.show_message(message, ft.colors.GREEN)

    def show_error_message(self, message: str):
        """Muestra un mensaje de error"""
        # Mejorar mensajes específicos
        if "no se pudo eliminar" in message.lower():
            message = "No se pudo eliminar el archivo de backup. Verifique permisos."
        elif "archivo de backup no encontrado" in message.lower():
            message = "El archivo de backup no existe. Puede haber sido eliminado manualmente."
        elif "error al crear backup" in message.lower():
            message = "Error al crear el backup. Verifique el espacio en disco y permisos."
        
        self.show_message(message, ft.colors.RED)
