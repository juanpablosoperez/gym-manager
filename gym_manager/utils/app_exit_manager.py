import os
import logging
import time
from typing import Optional
import flet as ft

logger = logging.getLogger(__name__)

class AppExitManager:
    def __init__(self, page: ft.Page, db_session=None):
        self.page = page
        self.db_session = db_session
        self._exit_dialog: Optional[ft.AlertDialog] = None

    def _close_resources(self):
        """Cierra todos los recursos de la aplicación"""
        try:
            # Cerrar conexión a la base de datos
            if self.db_session:
                self.db_session.close()
                logger.info("Conexión a la base de datos cerrada")

            # Cerrar todos los diálogos abiertos
            for overlay in self.page.overlay:
                if isinstance(overlay, ft.AlertDialog):
                    overlay.open = False

            logger.info("Recursos cerrados correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar recursos: {str(e)}")

    def _exit_application(self):
        """Cierra la aplicación de manera segura"""
        try:
            self._close_resources()
            def _salir():
                print("Cerrando aplicación...")
                os._exit(0)
            import threading
            threading.Thread(target=_salir).start()
        except Exception as e:
            logger.error(f"Error al cerrar la aplicación: {str(e)}")
            os._exit(1)

    def show_exit_dialog(self, title: str, message: str, show_cancel: bool = True):
        """Muestra un diálogo de confirmación antes de cerrar la aplicación"""
        self._exit_dialog = ft.AlertDialog(
            title=ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(message, size=16)
            ], spacing=10),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._close_dialog()
                ) if show_cancel else None,
                ft.TextButton(
                    "Cerrar aplicación",
                    on_click=lambda e: self._exit_application()
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # Filtrar acciones None
        self._exit_dialog.actions = [action for action in self._exit_dialog.actions if action is not None]
        
        # Agregar diálogo a la página y mostrarlo
        self.page.overlay.append(self._exit_dialog)
        self._exit_dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Cierra el diálogo de salida"""
        if self._exit_dialog:
            self._exit_dialog.open = False
            self.page.update() 