import flet as ft
from gym_manager.views.module_views import ModuleView
from gym_manager.utils.database import get_db_session
from gym_manager.models.user import Usuario
from gym_manager.controllers.user_controller import UserController


class UsersView(ModuleView):
    def __init__(self, page: ft.Page):
        # Inicializar las banderas antes de llamar a setup_view
        self.tocado = {"nombre": False, "apellido": False, "contrasena": False}
        self.intento_guardar = False
        super().__init__(page, "Gestión de Usuarios")
        self.user_controller = UserController()
        self.setup_confirm_dialog()
        self.load_data()

    def setup_view(self):
        # Título principal
        self.welcome_title = ft.Text(
            "¡Administra los usuarios del sistema!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        # Botón Nuevo Usuario
        self.new_user_btn = ft.ElevatedButton(
            text="Agregar Usuario",
            icon=ft.icons.ADD,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
            width=150,
            on_click=self.mostrar_formulario
        )

        # Filtros
        self.filtro_rol = ft.Dropdown(
            label="Filtrar por rol",
            width=200,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("user"),
            ],
            value="Todos",
            border_radius=8,
            on_change=self.aplicar_filtros
        )

        self.filtro_estado = ft.Dropdown(
            label="Filtrar por estado",
            width=200,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Activos"),
                ft.dropdown.Option("Inactivos"),
            ],
            value="Todos",
            border_radius=8,
            on_change=self.aplicar_filtros
        )

        self.limpiar_filtros_btn = ft.TextButton(
            text="Limpiar filtros",
            icon=ft.icons.CLEAR,
            on_click=self.limpiar_filtros,
            style=ft.ButtonStyle(
                color=ft.colors.BLACK87,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                text_style=ft.TextStyle(size=14),
            ),
        )

        # Campos del formulario
        def crear_campo_con_error(campo, nombre_campo):
            # Crear contenedor de error separado
            error_container = ft.Container(
                ft.Text(
                    "",
                    size=12,
                    color=ft.colors.RED
                ),
                height=20,
                padding=ft.padding.only(left=8, top=2),
                alignment=ft.alignment.top_left,
                visible=False
            )
            
            # Guardar referencia para poder actualizarlo después
            setattr(self, f"error_container_{nombre_campo}", error_container)
            
            return ft.Column([
                campo,
                error_container
            ], spacing=0)

        self.nombre = ft.TextField(
            label="Nombre",
            prefix_icon=ft.icons.PERSON,
            border_radius=8,
            width=500,
            height=40,
            max_length=50,
            on_change=lambda e: self.validar_campo_con_tocado("nombre"),
            on_blur=lambda e: self.marcar_tocado("nombre"),
            focused_border_color=ft.colors.BLUE,
            border_color=ft.colors.GREY_400
        )
        self.apellido = ft.TextField(
            label="Apellido",
            prefix_icon=ft.icons.PERSON,
            border_radius=8,
            width=500,
            height=40,
            max_length=50,
            on_change=lambda e: self.validar_campo_con_tocado("apellido"),
            on_blur=lambda e: self.marcar_tocado("apellido"),
            focused_border_color=ft.colors.BLUE,
            border_color=ft.colors.GREY_400
        )
        self.rol = ft.Dropdown(
            label="Rol",
            prefix_icon=ft.icons.ADMIN_PANEL_SETTINGS,
            width=500,
            options=[
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("user"),
            ],
            border_radius=8,
            on_change=self.validar_campos,
            focused_border_color=ft.colors.BLUE,
            border_color=ft.colors.GREY_400
        )
        self.contrasena = ft.TextField(
            label="Contraseña",
            prefix_icon=ft.icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=8,
            width=500,
            height=40,
            max_length=50,
            on_change=lambda e: self.validar_campo_con_tocado("contrasena"),
            on_blur=lambda e: self.marcar_tocado("contrasena"),
            focused_border_color=ft.colors.BLUE,
            border_color=ft.colors.GREY_400
        )

        # Modal de nuevo/editar usuario
        self.user_modal = ft.AlertDialog(
            title=ft.Container(
                content=ft.Text(
                    "Registrar Nuevo Usuario",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLACK87,
                ),
                padding=ft.padding.only(bottom=20),
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Nombre",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLACK87,
                                    ),
                                    crear_campo_con_error(self.nombre, 'nombre'),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.only(bottom=25),  # Espaciado fijo entre campos
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Apellido",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLACK87,
                                    ),
                                    crear_campo_con_error(self.apellido, 'apellido'),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.only(bottom=25),  # Espaciado fijo entre campos
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Rol",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLACK87,
                                    ),
                                    self.rol,
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.only(bottom=25),  # Espaciado fijo entre campos
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Contraseña",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLACK87,
                                    ),
                                    crear_campo_con_error(self.contrasena, 'contrasena'),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.only(bottom=25),  # Espaciado fijo entre campos
                        ),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.TextButton(
                                "Cancelar",
                                on_click=self.cancelar_formulario,
                                style=ft.ButtonStyle(
                                    color=ft.colors.BLACK87,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.padding.symmetric(horizontal=28, vertical=12),
                                    text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                                ),
                            ),
                            ft.ElevatedButton(
                                "Guardar",
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.BLUE,
                                    color=ft.colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.padding.symmetric(horizontal=28, vertical=12),
                                    text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                                ),
                                on_click=self.guardar_usuario,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
                    ),
                    padding=ft.padding.only(top=20),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor=ft.colors.WHITE,
        )

        # Tabla de usuarios
        self.users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", size=16, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Apellido", size=16, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rol", size=16, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", size=16, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", size=16, weight=ft.FontWeight.BOLD)),
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
            width=1200,
        )

        # Layout principal
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.welcome_title,
                                ft.Container(
                                    content=self.new_user_btn,
                                    alignment=ft.alignment.center_right,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=30, top=0, left=10, right=10),
                        alignment=ft.alignment.top_left,
                        width=1300,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.filtro_rol,
                                self.filtro_estado,
                                self.limpiar_filtros_btn,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=20,
                        ),
                        padding=ft.padding.only(bottom=20, left=10),
                    ),
                    ft.Container(
                        content=ft.Container(
                            content=self.users_table,
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=20),
                        ),
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=20),
                        margin=ft.margin.only(top=20),
                        alignment=ft.alignment.center,
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
            bgcolor=ft.colors.WHITE,
            border_radius=18,
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
            alignment=ft.alignment.top_left,
        )

    def get_content(self):
        return self.content

    def load_data(self):
        """
        Carga los datos iniciales de la vista
        """
        try:
            usuarios = self.user_controller.get_users()
            self.update_users_table(usuarios)
        except Exception as ex:
            self.show_message(f"Error al cargar los usuarios: {str(ex)}", ft.colors.RED)

    def update_users_table(self, usuarios):
        """
        Actualiza la tabla de usuarios con datos reales
        """
        self.users_table.rows.clear()
        
        if not usuarios:
            self.users_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Icon(name=ft.icons.PEOPLE_OUTLINE, size=48, color=ft.colors.GREY_400),
                                        ft.Text(
                                            "No se encontraron usuarios",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.GREY_700
                                        ),
                                        ft.Text(
                                            "Registra tu primer usuario usando el botón 'Agregar Usuario'",
                                            size=16,
                                            color=ft.colors.GREY_600
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                ),
                                padding=40,
                                alignment=ft.alignment.center,
                            ),
                            col_span=5
                        ),
                    ]
                )
            )
        else:
            for user in usuarios:
                self.users_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        user.nombre,
                                        size=14,
                                        color=ft.colors.BLACK87,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=10),
                                )
                            ),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        user.apellido,
                                        size=14,
                                        color=ft.colors.BLACK87,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=10),
                                )
                            ),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        user.rol,
                                        size=14,
                                        color=ft.colors.BLACK87,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=10),
                                )
                            ),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Container(
                                        content=ft.Text(
                                            "Activo" if user.estado else "Inactivo",
                                            size=14,
                                            color=ft.colors.WHITE,
                                        ),
                                        bgcolor=ft.colors.GREEN if user.estado else ft.colors.RED,
                                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                        border_radius=20,
                                    ),
                                    alignment=ft.alignment.center,
                                )
                            ),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_color=ft.colors.BLUE,
                                            tooltip="Editar",
                                            on_click=lambda e, u=user: self.editar_usuario(u)
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.TOGGLE_ON if user.estado else ft.icons.TOGGLE_OFF,
                                            icon_color=ft.colors.GREEN if user.estado else ft.colors.RED,
                                            tooltip="Activar/Desactivar",
                                            on_click=lambda e, u=user: self.toggle_estado_usuario(u)
                                        ),
                                    ],
                                    spacing=0,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                )
                            ),
                        ]
                    )
                )
        self.page.update()

    def mostrar_formulario(self, e):
        self.usuario_editando = None
        self.resetear_campos()
        if self.user_modal not in self.page.overlay:
            self.page.overlay.append(self.user_modal)
        self.user_modal.open = True
        self.page.update()

    def cancelar_formulario(self, e):
        self.usuario_editando = None
        self.resetear_campos()
        self.user_modal.open = False
        self.page.update()

    def resetear_campos(self):
        self.nombre.value = ""
        self.apellido.value = ""
        self.rol.value = None
        self.contrasena.value = ""
        self.tocado = {"nombre": False, "apellido": False, "contrasena": False}
        self.intento_guardar = False
        
        # Limpiar contenedores de error solo si existen
        for campo in ['nombre', 'apellido', 'contrasena']:
            if hasattr(self, f"error_container_{campo}"):
                self.actualizar_error_campo(campo, None)

    def guardar_usuario(self, e):
        self.intento_guardar = True
        self.tocado = {"nombre": True, "apellido": True, "contrasena": True}
        self.validar_campos()
        # Validar campos obligatorios
        campos_faltantes = []
        if not self.nombre.value:
            campos_faltantes.append("Nombre")
        if not self.apellido.value:
            campos_faltantes.append("Apellido")
        if not self.rol.value:
            campos_faltantes.append("Rol")
        if not self.usuario_editando and not self.contrasena.value:
            campos_faltantes.append("Contraseña")

        if campos_faltantes:
            self.show_message(f"Los siguientes campos son obligatorios: {', '.join(campos_faltantes)}", ft.colors.RED)
            return

        try:
            if self.usuario_editando:
                # Validar que no se intente cambiar el rol del último admin
                if self.usuario_editando.rol == "admin" and self.rol.value != "admin":
                    admins = [u for u in self.user_controller.get_users() if u.rol == "admin" and u.estado]
                    if len(admins) <= 1:
                        self.show_message("No se puede cambiar el rol del último administrador activo", ft.colors.RED)
                        return

                # Actualizar usuario existente
                success, message = self.user_controller.update_user(
                    self.usuario_editando.id_usuario,
                    nombre=self.nombre.value.strip(),
                    apellido=self.apellido.value.strip(),
                    rol=self.rol.value,
                    contraseña=self.contrasena.value if self.contrasena.value else None
                )
                if not success:
                    raise Exception(message)
                mensaje = "Usuario actualizado exitosamente"
            else:
                # Crear nuevo usuario
                success, message = self.user_controller.create_user(
                    nombre=self.nombre.value.strip(),
                    apellido=self.apellido.value.strip(),
                    rol=self.rol.value,
                    contraseña=self.contrasena.value
                )
                if not success:
                    raise Exception(message)
                mensaje = "Usuario guardado exitosamente"

            self.show_message(mensaje, ft.colors.GREEN)
            self.cancelar_formulario(e)
            self.load_data()

        except Exception as ex:
            self.show_message(f"Error al guardar: {str(ex)}", ft.colors.RED)

        self.page.update()

    def editar_usuario(self, usuario):
        self.usuario_editando = usuario
        self.nombre.value = usuario.nombre
        self.apellido.value = usuario.apellido
        self.rol.value = usuario.rol
        self.contrasena.value = ""
        # Resetear las banderas de validación para que no se muestren errores al abrir
        self.tocado = {"nombre": False, "apellido": False, "contrasena": False}
        self.intento_guardar = False
        
        # Limpiar contenedores de error solo si existen
        for campo in ['nombre', 'apellido', 'contrasena']:
            if hasattr(self, f"error_container_{campo}"):
                self.actualizar_error_campo(campo, None)

        if self.user_modal not in self.page.overlay:
            self.page.overlay.append(self.user_modal)
        self.user_modal.title = ft.Text("Editar Usuario", size=26, weight=ft.FontWeight.BOLD)
        self.user_modal.open = True
        self.page.update()

    def setup_confirm_dialog(self):
        """
        Configura el diálogo de confirmación
        """
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar acción", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text("¿Estás seguro de que deseas cambiar el estado de este usuario?"),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.close_confirm_dialog,
                    style=ft.ButtonStyle(
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                ),
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=self.confirm_toggle_estado,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15),
        )

    def toggle_estado_usuario(self, usuario):
        """
        Muestra el diálogo de confirmación antes de cambiar el estado
        """
        self.usuario_a_toggle = usuario
        if self.confirm_dialog not in self.page.overlay:
            self.page.overlay.append(self.confirm_dialog)
        self.confirm_dialog.open = True
        self.page.update()

    def close_confirm_dialog(self, e):
        """
        Cierra el diálogo de confirmación
        """
        self.confirm_dialog.open = False
        self.usuario_a_toggle = None
        self.page.update()

    def confirm_toggle_estado(self, e):
        """
        Ejecuta el cambio de estado después de la confirmación
        """
        if self.usuario_a_toggle:
            try:
                success, message = self.user_controller.update_user(
                    self.usuario_a_toggle.id_usuario,
                    estado=not self.usuario_a_toggle.estado
                )
                if not success:
                    raise Exception(message)
                mensaje = "Usuario activado" if not self.usuario_a_toggle.estado else "Usuario desactivado"
                self.show_message(mensaje, ft.colors.GREEN)
                self.load_data()
            except Exception as ex:
                self.show_message(f"Error al cambiar estado: {str(ex)}", ft.colors.RED)
            finally:
                self.close_confirm_dialog(e)

    def show_message(self, message: str, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def aplicar_filtros(self, e):
        """
        Aplica los filtros seleccionados
        """
        try:
            usuarios = self.user_controller.get_users()
            usuarios_filtrados = []

            # Filtrar por rol
            if self.filtro_rol.value != "Todos":
                usuarios_filtrados = [u for u in usuarios if u.rol == self.filtro_rol.value]
            else:
                usuarios_filtrados = usuarios

            # Filtrar por estado
            if self.filtro_estado.value == "Activos":
                usuarios_filtrados = [u for u in usuarios_filtrados if u.estado]
            elif self.filtro_estado.value == "Inactivos":
                usuarios_filtrados = [u for u in usuarios_filtrados if not u.estado]

            self.update_users_table(usuarios_filtrados)
        except Exception as ex:
            self.show_message(f"Error al aplicar filtros: {str(ex)}", ft.colors.RED)

    def limpiar_filtros(self, e):
        """
        Limpia los filtros y muestra todos los usuarios
        """
        self.filtro_rol.value = "Todos"
        self.filtro_estado.value = "Todos"
        self.load_data()
        self.page.update()

    def actualizar_error_campo(self, nombre_campo, mensaje_error):
        """
        Actualiza el mensaje de error de un campo específico
        """
        error_container = getattr(self, f"error_container_{nombre_campo}", None)
        if error_container:
            error_text = error_container.content
            mostrar = self.tocado[nombre_campo] or self.intento_guardar
            
            if mensaje_error and mostrar:
                error_text.value = mensaje_error
                error_container.visible = True
            else:
                error_text.value = ""
                error_container.visible = False
            
            # Solo actualizar si el contenedor está en la página
            try:
                if hasattr(error_container, '_page') and error_container._page:
                    error_container.update()
            except:
                pass  # Ignorar errores si el contenedor no está en la página

    def validar_campo_con_tocado(self, nombre_campo):
        """
        Valida un campo específico y lo marca como tocado
        """
        self.tocado[nombre_campo] = True
        
        if nombre_campo == 'nombre':
            if self.nombre.value and len(self.nombre.value.strip()) < 2:
                self.actualizar_error_campo('nombre', "El nombre debe tener al menos 2 caracteres")
            else:
                self.actualizar_error_campo('nombre', None)
        elif nombre_campo == 'apellido':
            if self.apellido.value and len(self.apellido.value.strip()) < 2:
                self.actualizar_error_campo('apellido', "El apellido debe tener al menos 2 caracteres")
            else:
                self.actualizar_error_campo('apellido', None)
        elif nombre_campo == 'contrasena':
            if not self.usuario_editando or self.contrasena.value:
                if self.contrasena.value and len(self.contrasena.value) < 6:
                    self.actualizar_error_campo('contrasena', "La contraseña debe tener al menos 6 caracteres")
                else:
                    self.actualizar_error_campo('contrasena', None)

        self.page.update()

    def validar_campos(self, e=None):
        """
        Valida todos los campos del formulario (usado para validación completa)
        """
        # Validar longitud de nombre y apellido
        if self.nombre.value and len(self.nombre.value.strip()) < 2:
            self.actualizar_error_campo('nombre', "El nombre debe tener al menos 2 caracteres")
        else:
            self.actualizar_error_campo('nombre', None)

        if self.apellido.value and len(self.apellido.value.strip()) < 2:
            self.actualizar_error_campo('apellido', "El apellido debe tener al menos 2 caracteres")
        else:
            self.actualizar_error_campo('apellido', None)

        # Validar contraseña solo si es nuevo usuario o se está cambiando
        if not self.usuario_editando or self.contrasena.value:
            if self.contrasena.value and len(self.contrasena.value) < 6:
                self.actualizar_error_campo('contrasena', "La contraseña debe tener al menos 6 caracteres")
            else:
                self.actualizar_error_campo('contrasena', None)

        self.page.update()

    def marcar_tocado(self, campo):
        self.tocado[campo] = True
        self.page.update()
