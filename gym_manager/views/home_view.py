import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gym_manager.views.login_view import LoginView

class HomeView:
    def __init__(self, page: ft.Page, user_rol: str):
        self.page = page
        self.user_rol = user_rol
        self.setup_page()

    def setup_page(self):
        self.page.title = "Gym Manager - Home"
        self.page.padding = 0
        self.page.bgcolor = ft.colors.WHITE
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_resizable = True

        # Barra superior
        self.top_bar = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(name=ft.icons.FITNESS_CENTER_ROUNDED, color=ft.colors.WHITE, size=30),
                    ft.Text("Gym Manager", color=ft.colors.WHITE, size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),  # Espaciador
                    ft.Row(
                        controls=[
                            ft.Icon(name=ft.icons.PERSON_OUTLINE, color=ft.colors.WHITE),
                            ft.Text(f"Rol: {self.user_rol}", color=ft.colors.WHITE),
                            ft.IconButton(
                                icon=ft.icons.LOGOUT,
                                icon_color=ft.colors.WHITE,
                                tooltip="Cerrar sesión",
                                on_click=self.logout
                            )
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=ft.colors.BLUE,
            padding=ft.padding.all(20),
        )

        # Menú lateral
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            leading=ft.Container(
                content=ft.Icon(name=ft.icons.MENU),
                margin=ft.margin.only(bottom=20)
            ),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PEOPLE_OUTLINE,
                    selected_icon=ft.icons.PEOPLE,
                    label="Miembros",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FITNESS_CENTER_OUTLINED,
                    selected_icon=ft.icons.FITNESS_CENTER,
                    label="Rutinas",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PAYMENTS_OUTLINED,
                    selected_icon=ft.icons.PAYMENTS,
                    label="Pagos",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="Configuración",
                ),
            ],
            on_change=self.nav_change,
        )

        # Área principal con contenido de ejemplo
        self.main_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("¡Bienvenido al Sistema!", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Selecciona una opción del menú para comenzar.", size=16, color=ft.colors.GREY_700),
                    ft.Container(height=20),
                    ft.Row(
                        controls=[
                            self.create_stat_card("Total Miembros", "150", ft.icons.PEOPLE, ft.colors.BLUE),
                            self.create_stat_card("Activos Hoy", "45", ft.icons.FITNESS_CENTER, ft.colors.GREEN),
                            self.create_stat_card("Pagos Pendientes", "12", ft.icons.PAYMENT, ft.colors.ORANGE),
                            self.create_stat_card("Rutinas Activas", "34", ft.icons.SCHEDULE, ft.colors.PURPLE),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            expand=True,
            padding=ft.padding.all(20),
        )

        # Construir la interfaz
        self.page.add(
            self.top_bar,
            ft.Row(
                controls=[
                    self.nav_rail,
                    ft.VerticalDivider(width=1),
                    self.main_content,
                ],
                expand=True,
            ),
        )
        self.page.update()

    def create_stat_card(self, title: str, value: str, icon: str, color: str) -> ft.Container:
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
            width=200,
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

    def nav_change(self, e):
        index = e.control.selected_index
        sections = ["Dashboard", "Miembros", "Rutinas", "Pagos", "Configuración"]
        print(f"Navegando a la sección: {sections[index]}")
        # Aquí se implementará la navegación a cada sección

    def logout(self, e):
        from gym_manager.views.login_view import LoginView
        from gym_manager.controllers.auth_controller import AuthController
        
        # Mostrar mensaje de despedida
        self.show_message("¡Hasta pronto! Cerrando sesión...", ft.colors.BLUE)
        
        # Limpiar la página actual
        self.page.clean()
        
        # Restablecer el tamaño de la ventana
        self.page.window_width = 400
        self.page.window_height = 700
        self.page.window_resizable = False
        self.page.update()
        
        # Volver a la pantalla de login
        auth_controller = AuthController(None)  # No necesitamos la sesión para el login inicial
        LoginView(self.page, auth_controller)

    def show_message(self, message: str, color: str):
        # Crear y mostrar un snackbar
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        self.page.show_snack_bar(snack) 