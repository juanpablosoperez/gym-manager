import flet as ft
Colors = getattr(ft, "colors", getattr(ft, "Colors", None))
from gym_manager.controllers.auth_controller import AuthController
from gym_manager.utils.navigation import navigate_to_login

class LoginView:
    def __init__(self, page: ft.Page, auth_controller: AuthController):
        self.page = page
        self.auth_controller = auth_controller
        self.setup_page()
        
    def setup_page(self):
        self.page.title = "Login - Gym Manager"
        self.page.window_width = 400
        self.page.window_height = 500
        self.page.window_resizable = False
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.colors.WHITE
        
        # Snackbar para mensajes
        self.snack = ft.SnackBar(content=ft.Text(""))
        
        # Crear los campos de entrada con mejor diseño
        self.nombre = ft.TextField(
            label="Nombre",
            icon=ft.icons.PERSON_OUTLINE,
            width=300,
            text_align=ft.TextAlign.LEFT,
            border_radius=8,
            focused_border_color=ft.colors.BLUE,
            cursor_color=ft.colors.BLUE,
            prefix_icon=ft.icons.PERSON,
            helper_text="Ingrese su nombre de usuario",
            helper_style=ft.TextStyle(size=12, color=ft.colors.GREY_600),
            border_color=ft.colors.GREY_400,
            bgcolor=ft.colors.GREY_50,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=15)
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
            cursor_color=ft.colors.BLUE,
            prefix_icon=ft.icons.LOCK,
            helper_text="Ingrese su contraseña",
            helper_style=ft.TextStyle(size=12, color=ft.colors.GREY_600),
            border_color=ft.colors.GREY_400,
            bgcolor=ft.colors.GREY_50,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=15)
        )
        
        # Botón de login con mejor diseño y efectos
        self.login_button = ft.ElevatedButton(
            text="INGRESAR",
            width=300,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor={"": ft.colors.BLUE, "hovered": ft.colors.BLUE_700},
                color=ft.colors.WHITE,
                elevation={"": 2, "hovered": 5},
                animation_duration=300,
                overlay_color=ft.colors.BLUE_100
            ),
            on_click=self.login
        )

        # Logo y título con mejor diseño y menos espacio
        logo_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            name=ft.icons.FITNESS_CENTER_ROUNDED,
                            size=60,
                            color=ft.colors.BLUE
                        ),
                        bgcolor=ft.colors.BLUE_50,
                        border_radius=50,
                        padding=15,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=10,
                            color=ft.colors.BLUE_100,
                        )
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        "Gym Manager",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Iniciar sesión",
                        size=16,
                        color=ft.colors.GREY_700,
                        weight=ft.FontWeight.W_500,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=ft.padding.all(15),
        )

        # Footer con diseño más compacto
        footer_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Divider(color=ft.colors.GREY_300, height=1),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Potenciá tu gimnasio ",
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
            padding=ft.padding.only(top=10, bottom=10),
        )

        # Contenedor principal con sombra y bordes redondeados
        main_container = ft.Container(
            content=ft.Column(
                controls=[
                    logo_container,
                    ft.Container(height=15),
                    self.nombre,
                    ft.Container(height=10),
                    self.contraseña,
                    ft.Container(height=15),
                    self.login_button,
                    footer_container
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            width=400,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.GREY_300,
            ),
        )

        # Fondo con gradiente
        background = ft.Container(
            content=main_container,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[ft.colors.BLUE_50, ft.colors.WHITE]
            ),
            expand=False,
            padding=ft.padding.all(20)
        )

        # Construir la interfaz
        self.page.add(background)
        
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
            # Importar aquí para evitar circular import
            from gym_manager.utils.navigation import navigate_to_home
            navigate_to_home(self.page, rol, nombre)
        else:
            self.show_message("Nombre o contraseña incorrectos") 