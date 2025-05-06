import flet as ft
from gym_manager.utils.navigation import db_session

class UsersView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.form_visible = False
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.apellido = ft.TextField(label="Apellido", width=300)
        self.rol = ft.Dropdown(
            label="Rol",
            width=300,
            options=[
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("user"),
            ],
        )
        self.contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)

        self.form_container = ft.Container(
            visible=self.form_visible,
            content=ft.Column(
                controls=[
                    ft.Text("Formulario de Usuario", size=20, weight=ft.FontWeight.BOLD),
                    self.nombre,
                    self.apellido,
                    self.rol,
                    self.contrasena,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("Guardar", icon=ft.icons.SAVE, on_click=self.guardar_usuario),
                            ft.OutlinedButton("Cancelar", icon=ft.icons.CANCEL, on_click=self.cancelar_formulario),
                        ],
                        spacing=10
                    )
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=ft.colors.GREY_100,
            border_radius=10,
        )

    def get_content(self):
        return ft.Column(
            controls=[
                ft.Text("Gestión de Usuarios", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Desde aquí podés agregar, editar o desactivar usuarios.", size=16, color=ft.colors.GREY_700),
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="Agregar Usuario",
                            icon=ft.icons.ADD,
                            on_click=self.mostrar_formulario
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Container(height=10),
                self.form_container,
                ft.Container(height=20),
                self.build_user_table_placeholder(),
            ],
            spacing=20,
        )

    def mostrar_formulario(self, e):
        self.form_container.visible = True
        self.page.update()

    def cancelar_formulario(self, e):
        self.form_container.visible = False
        self.resetear_campos()
        self.page.update()

    def guardar_usuario(self, e):
        # Validaciones básicas
        if not all([self.nombre.value, self.apellido.value, self.rol.value, self.contrasena.value]):
            self.page.snack_bar = ft.SnackBar(ft.Text("Todos los campos son obligatorios"), bgcolor=ft.colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return

        # (Aquí más adelante se agregará la lógica de guardado en la DB)
        self.page.snack_bar = ft.SnackBar(ft.Text("Usuario guardado exitosamente"), bgcolor=ft.colors.GREEN)
        self.page.snack_bar.open = True

        # Ocultar y limpiar formulario
        self.cancelar_formulario(e)

    def resetear_campos(self):
        self.nombre.value = ""
        self.apellido.value = ""
        self.rol.value = None
        self.contrasena.value = ""

    def build_user_table_placeholder(self):
        return ft.Container(
            content=ft.Text("Tabla de usuarios irá aquí...", italic=True, color=ft.colors.GREY),
            padding=20,
            bgcolor=ft.colors.GREY_100,
            border_radius=10,
        )
