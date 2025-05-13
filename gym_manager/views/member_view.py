import flet as ft
from datetime import datetime
from gym_manager.controllers.member_controller import MemberController
from gym_manager.utils.navigation import db_session
from gym_manager.services.excel_utils import export_members_to_excel, export_members_to_pdf
import os
import subprocess

class MembersView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.member_controller = MemberController(db_session)
        self.db_session = db_session
        
        # Inicializar referencias
        self.new_member_name = ft.Ref[ft.TextField]()
        self.new_member_lastname = ft.Ref[ft.TextField]()
        self.new_member_document = ft.Ref[ft.TextField]()
        self.new_member_email = ft.Ref[ft.TextField]()
        self.new_member_birth_date = ft.Ref[ft.ElevatedButton]()
        self.new_member_gender = ft.Ref[ft.Dropdown]()
        self.new_member_phone = ft.Ref[ft.TextField]()
        self.new_member_address = ft.Ref[ft.TextField]()
        self.new_member_membership = ft.Ref[ft.Dropdown]()
        self.new_member_start_date = ft.Ref[ft.ElevatedButton]()
        self.new_member_medical = ft.Ref[ft.TextField]()
        
        # DatePickers
        self.birth_date_picker = ft.DatePicker(
            first_date=datetime(1950, 1, 1),
            last_date=datetime.now(),
            on_change=self.on_birth_date_change
        )
        self.start_date_picker = ft.DatePicker(
            first_date=datetime.now(),
            last_date=datetime(2100, 12, 31),
            on_change=self.on_start_date_change
        )
        
        # Agregar DatePickers al overlay de la página
        self.page.overlay.append(self.birth_date_picker)
        self.page.overlay.append(self.start_date_picker)
        
        self.setup_member_view()
        self.load_data()

    def setup_member_view(self):
        # Título amigable
        self.welcome_title = ft.Text(
            "¡Administra y consulta tus miembros!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        # Botón Nuevo Miembro
        self.new_member_btn = ft.ElevatedButton(
            text="Nuevo Miembro",
            icon=ft.icons.PERSON_ADD,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
            width=150,
            on_click=self.show_new_member_modal
        )

        # Botones de exportación
        self.export_excel_btn = ft.IconButton(
            icon=ft.icons.TABLE_VIEW,
            icon_color=ft.colors.GREEN_700,
            tooltip="Exportar a Excel",
            on_click=self.export_to_excel,
            width=48,
            height=48,
        )
        self.export_pdf_btn = ft.IconButton(
            icon=ft.icons.PICTURE_AS_PDF,
            icon_color=ft.colors.RED_700,
            tooltip="Exportar a PDF",
            on_click=self.export_to_pdf,
            width=48,
            height=48,
        )

        # Filtros de búsqueda
        self.search_field = ft.TextField(
            label="Buscar por nombre, documento o email",
            prefix_icon=ft.icons.SEARCH,
            border_radius=10,
            width=320,
            height=48,
            text_size=16,
            on_change=self.apply_filters
        )

        self.status_filter = ft.Dropdown(
            label="Estado",
            width=150,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Activo"),
                ft.dropdown.Option("Inactivo")
            ],
            border_radius=10,
            text_size=16,
            on_change=self.apply_filters
        )

        self.membership_type = ft.Dropdown(
            label="Tipo de membresía",
            width=200,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Mensual"),
                ft.dropdown.Option("Trimestral"),
                ft.dropdown.Option("Semestral"),
                ft.dropdown.Option("Anual")
            ],
            border_radius=10,
            text_size=16,
            on_change=self.apply_filters
        )

        self.clear_btn = ft.OutlinedButton(
            text="Limpiar filtros",
            icon=ft.icons.CLEAR,
            style=ft.ButtonStyle(
                color=ft.colors.GREY_700,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
                text_style=ft.TextStyle(size=16),
            ),
            on_click=self.clear_filters
        )

        # Tabla de miembros
        self.members_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Documento", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Email", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Teléfono", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Membresía", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", size=18, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=12,
            vertical_lines=ft.border.all(1, ft.colors.GREY_300),
            horizontal_lines=ft.border.all(1, ft.colors.GREY_300),
            column_spacing=60,
            heading_row_color=ft.colors.GREY_100,
            heading_row_height=60,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=56,
        )

        # Modal de nuevo/editar miembro
        self.is_editing = False
        self.editing_member_id = None
        self.new_member_modal = ft.AlertDialog(
            title=ft.Text("Registrar Nuevo Miembro", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Información Personal", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.TextField(
                                label="Nombre",
                                width=240,
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_name
                            ),
                            ft.TextField(
                                label="Apellido",
                                width=240,
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_lastname
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
                        ft.Container(height=8),
                        ft.Row([
                            ft.TextField(
                                label="Documento",
                                width=240,
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_document
                            ),
                            ft.TextField(
                                label="Email",
                                width=240,
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_email
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
                        ft.Container(height=8),
                        ft.Row([
                            ft.ElevatedButton(
                                self.get_birth_date_btn_text(),
                                icon=ft.icons.CALENDAR_TODAY,
                                on_click=self.show_birth_date_picker,
                                ref=self.new_member_birth_date,
                                style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=12, vertical=10)),
                            ),
                            ft.Dropdown(
                                label="Género",
                                width=240,
                                options=[
                                    ft.dropdown.Option("Masculino"),
                                    ft.dropdown.Option("Femenino"),
                                    ft.dropdown.Option("Otro")
                                ],
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_gender
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
                        ft.Container(height=16),
                        ft.Text("Información de Contacto", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.TextField(
                                label="Teléfono",
                                width=240,
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_phone
                            ),
                            ft.TextField(
                                label="Dirección",
                                width=240,
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_address
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
                        ft.Container(height=16),
                        ft.Text("Información de Membresía", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Dropdown(
                                label="Tipo de Membresía",
                                width=240,
                                options=[
                                    ft.dropdown.Option("Mensual"),
                                    ft.dropdown.Option("Trimestral"),
                                    ft.dropdown.Option("Semestral"),
                                    ft.dropdown.Option("Anual")
                                ],
                                border_radius=8,
                                text_size=16,
                                ref=self.new_member_membership
                            ),
                            ft.ElevatedButton(
                                self.get_start_date_btn_text(),
                                icon=ft.icons.CALENDAR_TODAY,
                                on_click=self.show_start_date_picker,
                                ref=self.new_member_start_date,
                                style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=12, vertical=10)),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
                        ft.Container(height=16),
                        ft.Text("Información Médica", size=16, weight=ft.FontWeight.BOLD),
                        ft.TextField(
                            label="Información Médica",
                            width=480,
                            border_radius=8,
                            text_size=16,
                            ref=self.new_member_medical,
                            multiline=True,
                            min_lines=3,
                            max_lines=5,
                            helper_text="Ingrese cualquier información médica relevante del miembro"
                        ),
                    ],
                    spacing=0,
                ),
                width=540,
                padding=20,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_modal),
                ft.ElevatedButton(
                    lambda: "Actualizar" if self.is_editing else "Guardar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                    ),
                    on_click=self.save_member,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def get_content(self):
        content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.welcome_title,
                            ft.Row(
                                controls=[
                                    self.new_member_btn,
                                    self.export_excel_btn,
                                    self.export_pdf_btn,
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        controls=[
                            self.search_field,
                            self.status_filter,
                            self.membership_type,
                            self.clear_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=20),
                    self.members_table,
                ],
                spacing=0,
            ),
            padding=20,
            expand=True,
        )
        self.page.update()
        return content

    def load_data(self):
        """
        Carga los datos de miembros
        """
        members = self.member_controller.get_members()
        self.update_members_table(members)

    def update_members_table(self, members):
        """
        Actualiza la tabla de miembros
        """
        self.members_table.rows.clear()
        for member in members:
            self.members_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{member.nombre} {member.apellido}")),
                    ft.DataCell(ft.Text(member.documento)),
                    ft.DataCell(ft.Text(member.correo_electronico)),
                    ft.DataCell(ft.Text(member.telefono or "-")),
                    ft.DataCell(ft.Text(member.tipo_membresia)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                "Activo" if member.estado else "Inactivo",
                                color=ft.colors.WHITE
                            ),
                            bgcolor=ft.colors.GREEN if member.estado else ft.colors.RED,
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        )
                    ),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_color=ft.colors.BLUE,
                                tooltip="Editar",
                                on_click=lambda e, m=member: self.edit_member(m)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=ft.colors.RED,
                                tooltip="Eliminar",
                                on_click=lambda e, m=member: self.delete_member(m)
                            ),
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                icon_color=ft.colors.GREEN,
                                tooltip="Ver detalles",
                                on_click=lambda e, m=member: self.view_member_details(m)
                            ),
                        ])
                    ),
                ])
            )
        self.page.update()

    def show_new_member_modal(self, e):
        self.is_editing = False
        self.editing_member_id = None
        self.clear_member_fields()
        self.new_member_modal.title = ft.Text("Registrar Nuevo Miembro", size=26, weight=ft.FontWeight.BOLD)
        self.new_member_modal.actions[1].text = "Guardar"
        if self.new_member_modal not in self.page.overlay:
            self.page.overlay.append(self.new_member_modal)
        self.new_member_modal.open = True
        self.page.update()

    def close_modal(self, e):
        """
        Cierra el modal y limpia los campos
        """
        self.new_member_modal.open = False
        self.page.update()

    def show_birth_date_picker(self, e):
        """
        Muestra el selector de fecha de nacimiento
        """
        self.birth_date_picker.open = True
        self.page.update()

    def show_start_date_picker(self, e):
        """
        Muestra el selector de fecha de inicio
        """
        self.start_date_picker.open = True
        self.page.update()

    def on_birth_date_change(self, e):
        """
        Maneja el cambio de fecha de nacimiento
        """
        if e.date:
            self.new_member_birth_date.current.text = e.date.strftime("%d/%m/%Y")
            self.birth_date_picker.value = e.date
            self.page.update()

    def on_start_date_change(self, e):
        """
        Maneja el cambio de fecha de inicio de membresía
        """
        if e.date:
            self.new_member_start_date.current.text = e.date.strftime("%d/%m/%Y")
            self.start_date_picker.value = e.date
            self.page.update()

    def get_birth_date_btn_text(self):
        if self.birth_date_picker.value:
            return self.birth_date_picker.value.strftime("%d/%m/%Y")
        return "Fecha de Nacimiento"

    def get_start_date_btn_text(self):
        if self.start_date_picker.value:
            return self.start_date_picker.value.strftime("%d/%m/%Y")
        return "Fecha de Inicio"

    def save_member(self, e):
        """
        Guarda un nuevo miembro o actualiza uno existente
        """
        print("Iniciando guardado de miembro...")  # Debug log
        try:
            # Validar campos requeridos
            required_fields = {
                "nombre": self.new_member_name.current.value,
                "apellido": self.new_member_lastname.current.value,
                "documento": self.new_member_document.current.value,
                "email": self.new_member_email.current.value,
                "fecha_nacimiento": self.birth_date_picker.value,
                "genero": self.new_member_gender.current.value,
                "tipo_membresia": self.new_member_membership.current.value,
            }

            print("Valores de los campos:", required_fields)  # Debug log

            # Validar campos obligatorios
            for field, value in required_fields.items():
                if not value:
                    print(f"Campo requerido faltante: {field}")  # Debug log
                    self.show_message(f"El campo {field} es requerido", ft.colors.RED)
                    return

            # Validar formato de email
            if not "@" in required_fields["email"]:
                print("Email inválido")  # Debug log
                self.show_message("El email no tiene un formato válido", ft.colors.RED)
                return

            # Validar documento (solo números)
            if not required_fields["documento"].isdigit():
                print("Documento inválido")  # Debug log
                self.show_message("El documento debe contener solo números", ft.colors.RED)
                return

            # Preparar datos del miembro
            member_data = {
                "nombre": required_fields["nombre"].strip(),
                "apellido": required_fields["apellido"].strip(),
                "documento": required_fields["documento"].strip(),
                "correo_electronico": required_fields["email"].strip(),
                "fecha_nacimiento": required_fields["fecha_nacimiento"],
                "genero": required_fields["genero"],
                "tipo_membresia": required_fields["tipo_membresia"],
                "telefono": self.new_member_phone.current.value.strip() if self.new_member_phone.current.value else None,
                "direccion": self.new_member_address.current.value.strip() if self.new_member_address.current.value else None,
                "informacion_medica": self.new_member_medical.current.value.strip() if self.new_member_medical.current.value else None,
                "estado": True  # Por defecto, el miembro se crea activo
            }

            print("Datos del miembro a guardar:", member_data)  # Debug log

            if self.is_editing:
                # Actualizar miembro existente
                success, message = self.member_controller.update_member(self.editing_member_id, member_data)
                if success:
                    self.show_message("Miembro actualizado exitosamente", ft.colors.GREEN)
                    self.close_modal(e)
                    self.load_data()
                else:
                    self.show_message(f"Error al actualizar el miembro: {message}", ft.colors.RED)
            else:
                # Crear nuevo miembro
                success, message = self.member_controller.create_member(member_data)
                if success:
                    self.show_message("Miembro agregado exitosamente", ft.colors.GREEN)
                    self.close_modal(e)
                    self.load_data()
                else:
                    self.show_message(f"Error al crear el miembro: {message}", ft.colors.RED)

        except Exception as e:
            print(f"Error inesperado al guardar miembro: {str(e)}")  # Debug log
            self.show_message(f"Error inesperado: {str(e)}", ft.colors.RED)

    def edit_member(self, member):
        self.is_editing = True
        self.editing_member_id = member.id_miembro
        self.new_member_modal.title = ft.Text("Editar Miembro", size=26, weight=ft.FontWeight.BOLD)
        self.new_member_modal.actions[1].text = "Actualizar"
        # Autocompletar campos
        self.new_member_name.current.value = member.nombre
        self.new_member_lastname.current.value = member.apellido
        self.new_member_document.current.value = member.documento
        self.new_member_email.current.value = member.correo_electronico
        self.birth_date_picker.value = member.fecha_nacimiento
        self.new_member_birth_date.current.text = self.get_birth_date_btn_text()
        self.new_member_gender.current.value = member.genero
        self.new_member_phone.current.value = member.telefono or ""
        self.new_member_address.current.value = member.direccion or ""
        self.new_member_membership.current.value = member.tipo_membresia
        self.start_date_picker.value = member.fecha_registro if hasattr(member, 'fecha_registro') else None
        self.new_member_start_date.current.text = self.get_start_date_btn_text()
        self.new_member_medical.current.value = member.informacion_medica or ""
        if self.new_member_modal not in self.page.overlay:
            self.page.overlay.append(self.new_member_modal)
        self.new_member_modal.open = True
        self.page.update()

    def clear_member_fields(self):
        self.new_member_name.current.value = ""
        self.new_member_lastname.current.value = ""
        self.new_member_document.current.value = ""
        self.new_member_email.current.value = ""
        self.birth_date_picker.value = None
        self.new_member_birth_date.current.text = self.get_birth_date_btn_text()
        self.new_member_gender.current.value = None
        self.new_member_phone.current.value = ""
        self.new_member_address.current.value = ""
        self.new_member_membership.current.value = None
        self.start_date_picker.value = None
        self.new_member_start_date.current.text = self.get_start_date_btn_text()
        self.new_member_medical.current.value = ""
        self.page.update()

    def delete_member(self, member):
        """
        Elimina un miembro
        """
        success, message = self.member_controller.delete_member(member.id_miembro)
        if success:
            self.show_message(message, ft.colors.GREEN)
            self.load_data()
        else:
            self.show_message(message, ft.colors.RED)

    def view_member_details(self, member):
        """
        Muestra los detalles de un miembro en un modal
        """
        details_modal = ft.AlertDialog(
            title=ft.Text(f"Detalles del Miembro", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Información Personal", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Nombre:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{member.nombre} {member.apellido}", size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Documento:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.documento, size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Email:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.correo_electronico, size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Fecha de Nacimiento:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.fecha_nacimiento.strftime("%d/%m/%Y") if member.fecha_nacimiento else "-", size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Género:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.genero or "-", size=14),
                                ]),
                            ], spacing=10),
                            padding=10,
                        ),
                        ft.Divider(),
                        ft.Text("Información de Contacto", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Teléfono:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.telefono or "-", size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Dirección:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.direccion or "-", size=14),
                                ]),
                            ], spacing=10),
                            padding=10,
                        ),
                        ft.Divider(),
                        ft.Text("Información de Membresía", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Tipo de Membresía:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.tipo_membresia, size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Estado:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text(
                                            "Activo" if member.estado else "Inactivo",
                                            color=ft.colors.WHITE
                                        ),
                                        bgcolor=ft.colors.GREEN if member.estado else ft.colors.RED,
                                        border_radius=8,
                                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                    ),
                                ]),
                                ft.Row([
                                    ft.Text("Fecha de Registro:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.fecha_registro.strftime("%d/%m/%Y") if member.fecha_registro else "-", size=14),
                                ]),
                            ], spacing=10),
                            padding=10,
                        ),
                        ft.Divider(),
                        ft.Text("Información Médica", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Condiciones Médicas:", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(member.informacion_medica or "-", size=14),
                                ]),
                            ], spacing=10),
                            padding=10,
                        ),
                    ],
                    spacing=0,
                ),
                width=600,
                padding=20,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.close_details_modal(details_modal)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        if details_modal not in self.page.overlay:
            self.page.overlay.append(details_modal)
        details_modal.open = True
        self.page.update()

    def close_details_modal(self, modal):
        """
        Cierra el modal de detalles
        """
        modal.open = False
        self.page.update()

    def apply_filters(self, e):
        """
        Aplica los filtros seleccionados
        """
        filters = {}
        
        if self.search_field.value:
            filters['search'] = self.search_field.value
        
        if self.status_filter.value and self.status_filter.value != "Todos":
            filters['status'] = self.status_filter.value == "Activo"
        
        if self.membership_type.value and self.membership_type.value != "Todos":
            filters['membership_type'] = self.membership_type.value
        
        members = self.member_controller.get_members(filters)
        self.update_members_table(members)

    def clear_filters(self, e):
        """
        Limpia todos los filtros
        """
        self.search_field.value = ""
        self.status_filter.value = "Todos"
        self.membership_type.value = "Todos"
        self.page.update()
        
        # Recargar datos sin filtros
        self.load_data()

    def show_success_dialog(self, file_path: str):
        """
        Muestra un diálogo de éxito con un botón para abrir la carpeta
        """
        def open_folder(e):
            folder_path = os.path.dirname(file_path)
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS y Linux
                subprocess.run(['xdg-open', folder_path])
            success_dialog.open = False
            self.page.update()

        success_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN, size=30),
                ft.Text("¡Descargado con éxito!", size=20, weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Column([
                ft.Text(f"El archivo se ha guardado en:", size=14),
                ft.Text(file_path, size=14, color=ft.colors.GREY_700),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Abrir carpeta",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=open_folder,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                    ),
                ),
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.close_success_dialog(success_dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        if success_dialog not in self.page.overlay:
            self.page.overlay.append(success_dialog)
        success_dialog.open = True
        self.page.update()

    def close_success_dialog(self, dialog):
        """
        Cierra el diálogo de éxito
        """
        dialog.open = False
        self.page.update()

    def export_to_excel(self, e):
        """
        Exporta los datos a Excel
        """
        try:
            members = self.member_controller.get_members()
            file_path = export_members_to_excel(members)
            self.show_success_dialog(file_path)
        except Exception as ex:
            self.show_message(
                ft.Row([
                    ft.Icon(ft.icons.ERROR, color=ft.colors.RED),
                    ft.Text(f"Error al exportar a Excel: {str(ex)}", color=ft.colors.RED)
                ]),
                ft.colors.RED_50
            )

    def export_to_pdf(self, e):
        """
        Exporta los datos a PDF
        """
        try:
            members = self.member_controller.get_members()
            file_path = export_members_to_pdf(members)
            self.show_success_dialog(file_path)
        except Exception as ex:
            self.show_message(
                ft.Row([
                    ft.Icon(ft.icons.ERROR, color=ft.colors.RED),
                    ft.Text(f"Error al exportar a PDF: {str(ex)}", color=ft.colors.RED)
                ]),
                ft.colors.RED_50
            )

    def show_message(self, content, bgcolor: str):
        """
        Muestra un mensaje al usuario
        """
        self.page.snack_bar = ft.SnackBar(
            content=content,
            bgcolor=bgcolor,
            duration=5000,  # 5 segundos
            action="Cerrar",
            action_color=ft.colors.WHITE,
        )
        self.page.snack_bar.open = True
        self.page.update()

# Para probar directamente:
if __name__ == "__main__":
    ft.app(target=MembersView)
