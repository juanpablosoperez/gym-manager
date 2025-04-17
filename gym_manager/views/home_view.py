import flet as ft
from gym_manager.components.header import create_header
from gym_manager.components.sidebar import create_sidebar
from gym_manager.utils.navigation import navigate_to_login
from gym_manager.views.module_views import (
    MembersView, PaymentsView, ReportsView,
    PaymentMethodsView, UsersView, BackupsView
)

class HomeView:
    def __init__(self, page: ft.Page, user_rol: str, user_name: str = "Usuario"):
        self.page = page
        self.user_rol = user_rol
        self.user_name = user_name
        # Inicializar el snackbar
        self.snack = ft.SnackBar(content=ft.Text(""))
        self.page.overlay.append(self.snack)
        self.setup_page()

    def setup_page(self):
        self.page.title = "Gym Manager - Home"
        self.page.padding = 0
        self.page.bgcolor = ft.colors.GREY_50
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_resizable = True

        # Crear header
        self.header = create_header(
            page=self.page,
            user_name=self.user_name,
            user_role=self.user_rol,
            on_logout=self.logout
        )

        # Crear sidebar
        self.sidebar = create_sidebar(
            page=self.page,
            on_item_selected=self.handle_route_change
        )

        # Contenedor principal para el contenido
        self.main_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("¡Bienvenido al Sistema!", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Selecciona una opción del menú para comenzar.", size=16, color=ft.colors.GREY_700),
                    ft.Container(height=20),
                    self.create_stats_row(),
                ],
            ),
            expand=True,
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            margin=ft.margin.all(20),
        )

        # Construir la interfaz
        self.page.add(
            ft.Column(
                controls=[
                    self.header,
                    ft.Row(
                        controls=[
                            self.sidebar,
                            ft.VerticalDivider(width=1),
                            self.main_content,
                        ],
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            )
        )
        self.page.update()

    def create_stats_row(self):
        return ft.Row(
            controls=[
                self.create_stat_card("Total Miembros", "150", ft.icons.PEOPLE, ft.colors.BLUE),
                self.create_stat_card("Activos Hoy", "45", ft.icons.FITNESS_CENTER, ft.colors.GREEN),
                self.create_stat_card("Pagos Pendientes", "12", ft.icons.PAYMENT, ft.colors.ORANGE),
                self.create_stat_card("Rutinas Activas", "34", ft.icons.SCHEDULE, ft.colors.PURPLE),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def create_stat_card(self, title: str, value: str, icon: str, color: str):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(name=icon, color=color, size=32),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD),
                    ft.Text(title, size=14, color=ft.colors.GREY_700),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            width=250,
            height=150,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.GREY_300,
            ),
            padding=20,
        )

    def handle_route_change(self, index: int):
        # Limpiar el contenido actual
        self.main_content.content = None
        
        # Crear la vista correspondiente según el índice
        if index == 0:  # Dashboard
            self.main_content.content = ft.Column(
                controls=[
                    ft.Text("¡Bienvenido al Sistema!", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Selecciona una opción del menú para comenzar.", size=16, color=ft.colors.GREY_700),
                    ft.Container(height=20),
                    self.create_stats_row(),
                ],
            )
        elif index == 1:  # Gestión de Miembros
            view = MembersView(self.page)
            self.main_content.content = view.get_content()
        elif index == 2:  # Gestión de Pagos
            view = PaymentsView(self.page)
            self.main_content.content = view.get_content()
        elif index == 3:  # Informes y Estadísticas
            view = ReportsView(self.page)
            self.main_content.content = view.get_content()
        elif index == 4:  # Métodos de Pago
            view = PaymentMethodsView(self.page)
            self.main_content.content = view.get_content()
        elif index == 5:  # Gestión de Usuarios
            view = UsersView(self.page)
            self.main_content.content = view.get_content()
        elif index == 6:  # Gestión de Backups
            view = BackupsView(self.page)
            self.main_content.content = view.get_content()
        
        self.page.update()

    def show_message(self, message: str, color: str):
        self.snack.bgcolor = color
        self.snack.content.value = message
        self.snack.open = True
        self.page.update()

    def logout(self, e):
        self.show_message("¡Hasta pronto! Cerrando sesión...", ft.colors.BLUE)
        # Esperar un momento para que se vea el mensaje
        self.page.update()
        # Navegar al login
        navigate_to_login(self.page) 