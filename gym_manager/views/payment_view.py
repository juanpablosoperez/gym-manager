import flet as ft
from gym_manager.controllers.payment_controller import PaymentController
from datetime import datetime, timedelta
from gym_manager.utils.navigation import db_session
from gym_manager.models.member import Miembro
from gym_manager.models.payment_method import MetodoPago

class PaymentsView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.payment_controller = PaymentController(db_session)
        self.db_session = db_session
        self.setup_payment_view()
        self.load_data()

    def setup_payment_view(self):
        # Título amigable arriba de los filtros, en negro y bien arriba
        self.welcome_title = ft.Text(
            "¡Administra y consulta los pagos de tus miembros!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        # Botón Nuevo Pago
        self.new_payment_btn = ft.ElevatedButton(
            text="Nuevo Pago",
            icon=ft.icons.ADD,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
            width=150,
            on_click=self.show_new_payment_modal
        )

        # Botón Exportar a Excel (solo icono y tooltip)
        self.export_excel_btn = ft.IconButton(
            icon=ft.icons.TABLE_VIEW,
            icon_color=ft.colors.GREEN_700,
            tooltip="Exportar a Excel",
            on_click=self.export_to_excel,
            width=48,
            height=48,
        )
        # Botón Exportar a PDF (solo icono y tooltip)
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
            label="Buscar por nombre",
            prefix_icon=ft.icons.SEARCH,
            border_radius=10,
            width=260,
            height=48,
            text_size=16,
            on_change=self.apply_filters
        )

        # DatePicker Desde
        self.date_from = ft.DatePicker(
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2025, 12, 31),
            on_change=self.on_date_from_change
        )
        self.page.overlay.append(self.date_from)
        self.date_from_value = None
        self.date_from_field = ft.Container(
            content=ft.Row([
                ft.Text(self.date_from_value.strftime("%d/%m/%Y") if self.date_from_value else "",
                        size=16,
                        color=ft.colors.BLACK54),
                ft.Icon(ft.icons.CALENDAR_TODAY, size=20, color=ft.colors.GREY_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            width=120,
            on_click=lambda e: self.open_date_picker(self.date_from),
            bgcolor=ft.colors.WHITE,
            tooltip="Seleccionar fecha desde",
        )

        # DatePicker Hasta
        self.date_to = ft.DatePicker(
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2025, 12, 31),
            on_change=self.on_date_to_change
        )
        self.page.overlay.append(self.date_to)
        self.date_to_value = None
        self.date_to_field = ft.Container(
            content=ft.Row([
                ft.Text(self.date_to_value.strftime("%d/%m/%Y") if self.date_to_value else "", 
                        size=16, 
                        color=ft.colors.BLACK54),
                ft.Icon(ft.icons.CALENDAR_TODAY, size=20, color=ft.colors.GREY_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            width=120,
            on_click=lambda e: self.open_date_picker(self.date_to),
            bgcolor=ft.colors.WHITE,
            tooltip="Seleccionar fecha hasta",
        )

        self.payment_method = ft.Dropdown(
            label="Método de pago",
            width=180,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Transferencia bancaria"),
                ft.dropdown.Option("Tarjeta de crédito")
            ],
            border_radius=10,
            text_size=16,
            on_change=self.apply_filters
        )

        # Filtro de estado
        self.status_filter = ft.Dropdown(
            label="Estado",
            width=120,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Pagado"),
                ft.dropdown.Option("Cancelado")
            ],
            border_radius=10,
            text_size=16,
            value="Pagado",
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
            )
        )

        self.clear_btn.on_click = self.clear_filters

        # Tabla de pagos
        self.payments_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Miembro", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Monto", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Método", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Observaciones", size=18, weight=ft.FontWeight.BOLD)),
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

        # Modal de nuevo pago
        self.new_payment_client_field = ft.TextField(
            label="Miembro",
            prefix_icon=ft.icons.SEARCH,
            border_radius=8,
            hint_text="Buscar miembro por nombre o documento...",
            width=500,
            height= 40,
            on_change=self.search_member
        )
        
        # Primero define el ListView
        self.member_search_results = ft.ListView(
            spacing=10,
            padding=10,
            height=40,
            visible=False,
            auto_scroll=False,
            expand=False
        )
        # Luego el Container que lo envuelve
        self.member_search_results_container = ft.Container(
            content=self.member_search_results,
            height=0 if not self.member_search_results.visible else 60,  # altura dinámica
            padding=0,
            margin=0
        )
        
        self.selected_member = None
        self.new_payment_date_picker = ft.DatePicker(
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2025, 12, 31),
            on_change=self.on_new_payment_date_change
        )
        self.page.overlay.append(self.new_payment_date_picker)
        self.new_payment_date_value = None
        self.new_payment_date_field = ft.Container(
            content=ft.Row([
                ft.Text(self.new_payment_date_value.strftime("%d/%m/%Y") if self.new_payment_date_value else "Seleccionar fecha",
                        size=16,
                        color=ft.colors.BLACK54),
                ft.Icon(ft.icons.CALENDAR_TODAY, size=20, color=ft.colors.GREY_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            width=500,
            on_click=lambda e: self.open_date_picker(self.new_payment_date_picker),
            bgcolor=ft.colors.GREY_100,
            tooltip="Seleccionar fecha",
        )
        self.new_payment_amount_field = ft.TextField(
            label="Monto",
            prefix_icon=ft.icons.ATTACH_MONEY,
            border_radius=8,
            width=500,
            value="0.00",
        )
        self.new_payment_method_field = ft.Dropdown(
            label="Método de pago",
            options=[
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Transferencia bancaria"),
                ft.dropdown.Option("Tarjeta de crédito")
            ],
            border_radius=8,
            width=500,
            hint_text="Seleccionar método",
        )
        self.new_payment_observations_field = ft.TextField(
            label="Observaciones",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=8,
            width=500,
            height=60,
            hint_text="Agregar observaciones...",
        )
        self.new_payment_modal = ft.AlertDialog(
            title=ft.Text("Registrar Nuevo Pago", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Miembro", size=16, weight=ft.FontWeight.BOLD),
                    self.new_payment_client_field,
                    self.member_search_results_container,
                    ft.Text("Fecha", size=16, weight=ft.FontWeight.BOLD),
                    self.new_payment_date_field,
                    ft.Text("Monto", size=16, weight=ft.FontWeight.BOLD),
                    self.new_payment_amount_field,
                    ft.Text("Método de pago", size=16, weight=ft.FontWeight.BOLD),
                    self.new_payment_method_field,
                    ft.Text("Observaciones", size=16, weight=ft.FontWeight.BOLD),
                    self.new_payment_observations_field,
                ],
                spacing=18,
                width=540,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_modal, style=ft.ButtonStyle(bgcolor=ft.colors.WHITE, color=ft.colors.BLACK87, shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=28, vertical=12), text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD))),
                ft.ElevatedButton(
                    "Guardar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                    ),
                    on_click=self.save_payment
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )

        # Modal de edición de pago
        self.edit_payment_client_field = ft.TextField(
            label="Miembro",
            prefix_icon=ft.icons.PERSON,
            border_radius=8,
            width=500,
            read_only=True
        )
        self.edit_payment_date_picker = ft.DatePicker(
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2025, 12, 31),
            on_change=self.on_edit_payment_date_change
        )
        self.page.overlay.append(self.edit_payment_date_picker)
        self.edit_payment_date_value = None
        self.edit_payment_date_field = ft.Container(
            content=ft.Row([
                ft.Text(self.edit_payment_date_value.strftime("%d/%m/%Y") if self.edit_payment_date_value else "Seleccionar fecha",
                        size=16,
                        color=ft.colors.BLACK54),
                ft.Icon(ft.icons.CALENDAR_TODAY, size=20, color=ft.colors.GREY_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            width=500,
            on_click=lambda e: self.open_date_picker(self.edit_payment_date_picker),
            bgcolor=ft.colors.GREY_100,
            tooltip="Seleccionar fecha",
        )
        self.edit_payment_amount_field = ft.TextField(
            label="Monto",
            prefix_icon=ft.icons.ATTACH_MONEY,
            border_radius=8,
            width=500,
            value="0.00",
        )
        self.edit_payment_method_field = ft.Dropdown(
            label="Método de pago",
            options=[
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Transferencia bancaria"),
                ft.dropdown.Option("Tarjeta de crédito")
            ],
            border_radius=8,
            width=500,
            hint_text="Seleccionar método",
        )
        self.edit_payment_observations_field = ft.TextField(
            label="Observaciones",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=8,
            width=500,
            height=60,
            hint_text="Agregar observaciones...",
        )
        self.edit_payment_modal = ft.AlertDialog(
            title=ft.Text("Editar Pago", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Miembro", size=16, weight=ft.FontWeight.BOLD),
                    self.edit_payment_client_field,
                    ft.Text("Fecha", size=16, weight=ft.FontWeight.BOLD),
                    self.edit_payment_date_field,
                    ft.Text("Monto", size=16, weight=ft.FontWeight.BOLD),
                    self.edit_payment_amount_field,
                    ft.Text("Método de pago", size=16, weight=ft.FontWeight.BOLD),
                    self.edit_payment_method_field,
                    ft.Text("Observaciones", size=16, weight=ft.FontWeight.BOLD),
                    self.edit_payment_observations_field,
                ],
                spacing=18,
                width=540,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_edit_modal, style=ft.ButtonStyle(bgcolor=ft.colors.WHITE, color=ft.colors.BLACK87, shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=28, vertical=12), text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD))),
                ft.ElevatedButton(
                    "Actualizar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                    ),
                    on_click=self.update_payment
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        self.page.overlay.append(self.edit_payment_modal)

        # Modal de confirmación de borrado
        self.delete_confirm_modal = ft.AlertDialog(
            title=ft.Text("Confirmar Cancelación", size=22, weight=ft.FontWeight.BOLD),
            content=ft.Text("¿Estás seguro que deseas cancelar este pago? El pago cancelado no se mostrará más en la lista, pero puedes recuperarlo desde la base de datos si es necesario.", size=16),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_delete_modal, style=ft.ButtonStyle(bgcolor=ft.colors.WHITE, color=ft.colors.BLACK87, shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=28, vertical=12), text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD))),
                ft.ElevatedButton(
                    "Confirmar Cancelación",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.RED_700,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                    on_click=self.confirm_delete_payment
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        self.page.overlay.append(self.delete_confirm_modal)
        self.selected_payment_to_delete = None

        # Layout principal
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=self.welcome_title,
                        padding=ft.padding.only(bottom=30, top=0, left=10, right=10),
                        alignment=ft.alignment.top_left,
                        width=900,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.search_field,
                                self.date_from_field,
                                self.date_to_field,
                                self.payment_method,
                                self.status_filter,
                                self.clear_btn,
                                self.new_payment_btn,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                            expand=True,
                        ),
                        padding=ft.padding.only(bottom=10, left=10),
                        alignment=ft.alignment.top_left,
                        width=1300,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.export_excel_btn,
                                self.export_pdf_btn,
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=8,
                        ),
                        padding=ft.padding.only(bottom=10, left=10, right=30),
                        alignment=ft.alignment.top_right,
                        width=1300,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=self.payments_table,
                                    expand=True,
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.symmetric(horizontal=40),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            expand=True,
                        ),
                        alignment=ft.alignment.center,
                        width=1300,
                        padding=ft.padding.only(top=30),
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.ALWAYS,
                horizontal_alignment=ft.CrossAxisAlignment.START,
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

    def create_summary_card(self, title: str, value: str, icon: str, color: str):
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

    def show_new_payment_modal(self, e):
        if self.new_payment_modal not in self.page.overlay:
            self.page.overlay.append(self.new_payment_modal)
        self.new_payment_modal.open = True
        self.page.update()

    def close_modal(self, e):
        self.new_payment_client_field.value = ""
        self.selected_member = None
        self.member_search_results.visible = False
        self.new_payment_date_value = None
        self.new_payment_date_picker.value = None
        self.new_payment_date_field.content.controls[0].value = "Seleccionar fecha"
        self.new_payment_amount_field.value = "0.00"
        self.new_payment_method_field.value = None
        self.new_payment_observations_field.value = ""
        self.new_payment_observations_field.height = 100
        self.new_payment_modal.open = False
        self.page.update()

    def load_data(self):
        """
        Carga los datos iniciales de la vista
        """
        payments = [p for p in self.payment_controller.get_payments() if p.estado == 1]
        self.update_payments_table(payments)

    def update_payments_table(self, payments):
        """
        Actualiza la tabla de pagos con datos reales
        """
        self.payments_table.rows.clear()
        
        if not payments:
            # Mostrar mensaje cuando no hay pagos
            self.payments_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Icon(name=ft.icons.PAYMENTS_OUTLINED, size=48, color=ft.colors.GREY_400),
                                        ft.Text(
                                            "No se encontraron pagos",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.GREY_700
                                        ),
                                        ft.Text(
                                            "Registra tu primer pago usando el botón 'Nuevo Pago'",
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
                        )
                    ]
                )
            )
        else:
            for payment in payments:
                estado_texto = "Pagado" if payment.estado == 1 else "Cancelado"
                color_estado = ft.colors.GREEN if payment.estado == 1 else ft.colors.RED
                self.payments_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(f"{payment.miembro.nombre} {payment.miembro.apellido}")),
                            ft.DataCell(ft.Text(payment.fecha_pago.strftime("%d/%m/%Y"))),
                            ft.DataCell(ft.Text(f"${payment.monto}")),
                            ft.DataCell(ft.Text(payment.metodo_pago.descripcion)),
                            ft.DataCell(ft.Text(payment.referencia if payment.referencia else "")),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        estado_texto,
                                        color=color_estado
                                    ),
                                    bgcolor=ft.colors.GREY_100 if payment.estado == 1 else ft.colors.RED_100,
                                    border_radius=8,
                                    padding=5,
                                )
                            ),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_color=ft.colors.BLUE,
                                            tooltip="Editar",
                                            on_click=lambda e, p=payment: self.edit_payment(p)
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_color=ft.colors.RED,
                                            tooltip="Eliminar",
                                            on_click=lambda e, p=payment: self.delete_payment(p)
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.RECEIPT,
                                            icon_color=ft.colors.GREEN,
                                            tooltip="Generar Comprobante",
                                            on_click=lambda e, p=payment: self.generate_receipt(p)
                                        ),
                                    ],
                                    spacing=0,
                                )
                            ),
                        ]
                    )
                )
        self.page.update()

    def apply_filters(self, e=None):
        """
        Aplica los filtros seleccionados
        """
        filters = {}
        
        if self.search_field.value:
            filters['member_name'] = self.search_field.value
        
        # Filtro de fecha desde
        if self.date_from.value:
            filters['date_from'] = self.date_from.value
        
        # Filtro de fecha hasta
        if self.date_to.value:
            filters['date_to'] = self.date_to.value
        
        if self.payment_method.value and self.payment_method.value != "Todos":
            filters['payment_method'] = self.payment_method.value
        
        # Filtro de estado
        if self.status_filter.value == "Pagado":
            filters['estado'] = 1
        elif self.status_filter.value == "Cancelado":
            filters['estado'] = 0
        # Si es "Todos", no se agrega filtro
        
        payments = self.payment_controller.get_payments(filters)
        # Si el filtro es por estado, filtrar aquí también por si acaso
        if 'estado' in filters:
            payments = [p for p in payments if p.estado == filters['estado']]
        self.update_payments_table(payments)

    def clear_filters(self, e):
        """
        Limpia todos los filtros
        """
        self.search_field.value = ""
        self.date_from.value = None
        self.date_to.value = None
        self.date_from_field.content.controls[0].value = ""
        self.date_to_field.content.controls[0].value = ""
        self.payment_method.value = "Todos"
        self.status_filter.value = "Pagado"
        self.page.update()
        # Recargar datos sin filtros
        self.load_data()

    def edit_payment(self, payment):
        """
        Abre el modal para editar un pago, cargando los datos del pago seleccionado
        """
        self.selected_payment = payment
        self.edit_payment_client_field.value = f"{payment.miembro.nombre} {payment.miembro.apellido}"
        self.edit_payment_date_value = payment.fecha_pago
        self.edit_payment_date_picker.value = payment.fecha_pago
        self.edit_payment_date_field.content.controls[0].value = payment.fecha_pago.strftime("%d/%m/%Y")
        self.edit_payment_amount_field.value = str(payment.monto)
        self.edit_payment_method_field.value = payment.metodo_pago.descripcion
        self.edit_payment_observations_field.value = payment.referencia if payment.referencia else ""
        self.edit_payment_modal.open = True
        self.page.update()

    def close_edit_modal(self, e):
        self.edit_payment_client_field.value = ""
        self.edit_payment_date_value = None
        self.edit_payment_date_picker.value = None
        self.edit_payment_date_field.content.controls[0].value = "Seleccionar fecha"
        self.edit_payment_amount_field.value = "0.00"
        self.edit_payment_method_field.value = None
        self.edit_payment_observations_field.value = ""
        self.edit_payment_modal.open = False
        self.selected_payment = None
        self.page.update()

    def on_edit_payment_date_change(self, e):
        self.edit_payment_date_value = self.edit_payment_date_picker.value
        value = self.edit_payment_date_picker.value.strftime("%d/%m/%Y") if self.edit_payment_date_picker.value else "Seleccionar fecha"
        self.edit_payment_date_field.content.controls[0].value = value
        self.page.update()

    def update_payment(self, e):
        if not self.selected_payment:
            self.show_message("No hay pago seleccionado para editar", ft.colors.RED)
            return
        if not self.edit_payment_date_value:
            self.show_message("Debe seleccionar una fecha", ft.colors.RED)
            return
        if not self.edit_payment_amount_field.value or float(self.edit_payment_amount_field.value) <= 0:
            self.show_message("Debe ingresar un monto válido", ft.colors.RED)
            return
        if not self.edit_payment_method_field.value:
            self.show_message("Debe seleccionar un método de pago", ft.colors.RED)
            return
        payment_data = {
            'fecha_pago': self.edit_payment_date_value,
            'monto': float(self.edit_payment_amount_field.value),
            'id_miembro': self.selected_payment.miembro.id_miembro,
            'id_metodo_pago': self.get_payment_method_id(self.edit_payment_method_field.value),
            'referencia': self.edit_payment_observations_field.value
        }
        success, message = self.payment_controller.update_payment(self.selected_payment.id_pago, payment_data)
        if success:
            self.show_message(message, ft.colors.GREEN)
            self.close_edit_modal(e)
            self.load_data()
        else:
            self.show_message(message, ft.colors.RED)

    def delete_payment(self, payment):
        """
        Abre el modal de confirmación para eliminar un pago
        """
        self.selected_payment_to_delete = payment
        self.delete_confirm_modal.open = True
        self.page.update()

    def close_delete_modal(self, e):
        self.delete_confirm_modal.open = False
        self.selected_payment_to_delete = None
        self.page.update()

    def confirm_delete_payment(self, e):
        if not self.selected_payment_to_delete:
            self.show_message("No hay pago seleccionado para cancelar", ft.colors.RED)
            self.delete_confirm_modal.open = False
            self.page.update()
            return
        # Cancelar pago: poner estado en 0
        payment_data = {'estado': 0}
        success, message = self.payment_controller.update_payment(self.selected_payment_to_delete.id_pago, payment_data)
        if success:
            self.show_message("Pago cancelado correctamente", ft.colors.GREEN)
            self.delete_confirm_modal.open = False
            self.selected_payment_to_delete = None
            self.load_data()
        else:
            self.show_message("Error al cancelar el pago", ft.colors.RED)
            self.delete_confirm_modal.open = False
            self.selected_payment_to_delete = None
        self.page.update()

    def generate_receipt(self, payment):
        """
        Genera un comprobante de pago
        """
        # TODO: Implementar generación de comprobante
        self.show_message("Función en desarrollo", ft.colors.ORANGE)

    def search_member(self, e):
        """
        Busca miembros según el texto ingresado
        """
        search_text = self.new_payment_client_field.value.lower()
        if not search_text:
            self.member_search_results.visible = False
            self.member_search_results_container.height = 0
            self.page.update()
            return

        # Buscar miembros que coincidan con el texto de búsqueda
        members = self.db_session.query(Miembro).filter(
            (Miembro.nombre.ilike(f"%{search_text}%")) |
            (Miembro.apellido.ilike(f"%{search_text}%")) |
            (Miembro.documento.ilike(f"%{search_text}%"))
        ).limit(5).all()

        self.member_search_results.controls.clear()
        
        if members:
            for member in members:
                self.member_search_results.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.PERSON),
                            title=ft.Text(f"{member.nombre} {member.apellido}"),
                            subtitle=ft.Text(f"Documento: {member.documento}"),
                            on_click=lambda e, m=member: self.select_member(m)
                        ),
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=8,
                        bgcolor=ft.colors.WHITE,
                    )
                )
            self.member_search_results.visible = True
            self.member_search_results_container.height = 60
        else:
            self.member_search_results.controls.append(
                ft.Container(
                    content=ft.Text("No se encontraron miembros", color=ft.colors.GREY_700),
                    padding=10,
                    alignment=ft.alignment.center,
                )
            )
            self.member_search_results.visible = True
            self.member_search_results_container.height = 60
        
        self.page.update()

    def select_member(self, member):
        """
        Selecciona un miembro de la lista de resultados
        """
        self.selected_member = member
        self.new_payment_client_field.value = f"{member.nombre} {member.apellido}"
        self.member_search_results.visible = False
        self.member_search_results_container.height = 0
        self.page.update()

    def save_payment(self, e):
        """
        Guarda un nuevo pago
        """
        if not self.selected_member:
            self.show_message("Debe seleccionar un miembro", ft.colors.RED)
            return

        if not self.new_payment_date_value:
            self.show_message("Debe seleccionar una fecha", ft.colors.RED)
            return

        if not self.new_payment_amount_field.value or float(self.new_payment_amount_field.value) <= 0:
            self.show_message("Debe ingresar un monto válido", ft.colors.RED)
            return

        if not self.new_payment_method_field.value:
            self.show_message("Debe seleccionar un método de pago", ft.colors.RED)
            return

        payment_data = {
            'fecha_pago': self.new_payment_date_value,
            'monto': float(self.new_payment_amount_field.value),
            'id_miembro': self.selected_member.id_miembro,
            'id_metodo_pago': self.get_payment_method_id(self.new_payment_method_field.value),
            'referencia': self.new_payment_observations_field.value
        }
        
        success, message = self.payment_controller.create_payment(payment_data)
        if success:
            self.show_message(message, ft.colors.GREEN)
            self.close_modal(e)
            self.load_data()
        else:
            self.show_message(message, ft.colors.RED)

    def get_payment_method_id(self, method_name):
        """
        Obtiene el ID del método de pago según su nombre
        """
        method = self.db_session.query(MetodoPago).filter_by(descripcion=method_name).first()
        return method.id_metodo_pago if method else None

    def show_message(self, message: str, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_date_from_change(self, e):
        self.date_from_value = self.date_from.value
        value = self.date_from.value.strftime("%d/%m/%Y") if self.date_from.value else ""
        self.date_from_field.content.controls[0].value = value
        self.page.update()

    def on_date_to_change(self, e):
        self.date_to_value = self.date_to.value
        value = self.date_to.value.strftime("%d/%m/%Y") if self.date_to.value else ""
        self.date_to_field.content.controls[0].value = value
        self.page.update()
        self.apply_filters()  # Aplicar filtros automáticamente al cambiar la fecha hasta

    def open_date_picker(self, picker):
        picker.open = True
        self.page.update()

    def on_new_payment_date_change(self, e):
        self.new_payment_date_value = self.new_payment_date_picker.value
        value = self.new_payment_date_picker.value.strftime("%d/%m/%Y") if self.new_payment_date_picker.value else "Seleccionar fecha"
        self.new_payment_date_field.content.controls[0].value = value
        self.page.update()

    def export_to_excel(self, e):
        self.show_message("Función de exportar a Excel en desarrollo", ft.colors.BLUE)

    def export_to_pdf(self, e):
        self.show_message("Función de exportar a PDF en desarrollo", ft.colors.BLUE)
