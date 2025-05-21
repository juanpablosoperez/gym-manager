import flet as ft
from gym_manager.views.module_views import ModuleView
from gym_manager.utils.database import get_db_session

class BackupView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Respaldo y Restauración")
        self.setup_view()

    def setup_view(self):
        self.welcome_title = ft.Text(
            "Respaldo y Restauración",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self.welcome_title,
                    ft.Text("Funcionalidad en desarrollo...", size=16),
                ],
                spacing=20,
            ),
            padding=20,
        )

    def get_content(self):
        return self.content 