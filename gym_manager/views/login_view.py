import flet as ft
from gym_manager.controllers.auth_controller import AuthController
from gym_manager.views.home_view import HomeView

class LoginView:
    def __init__(self, page: ft.Page, auth_controller: AuthController):
        self.page = page
        self.auth_controller = auth_controller
        self.setup_page()
        
    def setup_page(self):
        self.page.title = "Login - Gym Manager"
        self.page.window_width = 400
        self.page.window_height = 700
        self.page.window_resizable = False
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.colors.WHITE
        
        # Snackbar para mensajes
        self.snack = ft.SnackBar(content=ft.Text(""))
        
        # Crear los campos de entrada
        self.nombre = ft.TextField(
            label="Nombre",
            icon=ft.icons.PERSON_OUTLINE,
            width=300,
            text_align=ft.TextAlign.LEFT,
            border_radius=8,
            focused_border_color=ft.colors.BLUE,
            cursor_color=ft.colors.BLUE
        )
        
        self.contraseña = ft.TextField(
            label="Contraseña",
            icon=ft.icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            width=300,
            text_align=ft.TextAlign.LEFT,
            border_radius=8,
            focused_border_color=ft.colors.BLUE,
            cursor_color=ft.colors.BLUE
        )
        
        # Botón de login con efecto hover
        self.login_button = ft.ElevatedButton(
            text="INGRESAR",
            width=300,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor={"": ft.colors.BLUE, "hovered": ft.colors.BLUE_700},
                color=ft.colors.WHITE,
                elevation={"": 2, "hovered": 5}
            ),
            on_click=self.login
        )

        # Logo y título
        logo_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        name=ft.icons.FITNESS_CENTER_ROUNDED,
                        size=80,
                        color=ft.colors.BLUE
                    ),
                    ft.Text(
                        "Gym Manager",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Text(
                        "Iniciar sesión",
                        size=20,
                        color=ft.colors.GREY_700,
                        weight=ft.FontWeight.W_500
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=ft.padding.all(20),
        )

        # Footer
        footer_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Potencia tu gimnasio ",
                                size=14,
                                color=ft.colors.GREY_700,
                                italic=True,
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Text(
                                "💪",
                                size=16
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Text(
                        "Versión 1.0.0",
                        size=12,
                        color=ft.colors.GREY_500
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=ft.padding.all(20),
        )

        # Construir la interfaz
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        logo_container,
                        ft.Container(height=30),
                        self.nombre,
                        ft.Container(height=15),
                        self.contraseña,
                        ft.Container(height=30),
                        self.login_button,
                        footer_container
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0
                ),
                padding=ft.padding.symmetric(horizontal=30),
                width=400
            )
        )
        
        # Agregar el snackbar a la página
        self.page.overlay.append(self.snack)
        self.page.update()

    def show_message(self, message: str, color: str = ft.colors.RED_400):
        self.snack.bgcolor = color
        self.snack.content.value = message
        self.snack.open = True
        self.page.update()

    def login(self, e):
        nombre = self.nombre.value
        contraseña = self.contraseña.value
        
        if not nombre or not contraseña:
            self.show_message("Por favor complete todos los campos")
            return
            
        success, rol = self.auth_controller.authenticate_user(nombre, contraseña)
        if success:
            self.show_message(f"¡Bienvenido! Iniciando sesión como {rol}", ft.colors.GREEN_400)
            # Limpiar la página actual
            self.page.clean()
            # Iniciar la vista de home
            HomeView(self.page, rol)
        else:
            self.show_message("Nombre o contraseña incorrectos") 