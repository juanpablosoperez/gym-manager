import flet as ft

class ModuleView:
    def __init__(self, page: ft.Page, title: str):
        self.page = page
        self.title = title
        self.setup_view()

    def setup_view(self):
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.title,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Text(
                        "Contenido del módulo en desarrollo",
                        size=16,
                        color=ft.colors.GREY_700
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            ),
            expand=True,
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            margin=ft.margin.all(20),
        )

    def get_content(self):
        return self.content

class MembersView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Miembros")

class PaymentsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Pagos")

class ReportsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Informes y Estadísticas")

class PaymentMethodsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Métodos de Pago")

class UsersView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Usuarios")

class BackupsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Backups") 