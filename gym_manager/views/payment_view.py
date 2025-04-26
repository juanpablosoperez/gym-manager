import flet as ft
from gym_manager.controllers.payment_controller import PaymentController
from datetime import datetime, timedelta
from gym_manager.utils.navigation import db_session

class PaymentsView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.payment_controller = PaymentController(db_session)
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
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
            ),
            on_click=self.show_new_payment_modal
        )

        # Filtros de búsqueda
        self.search_field = ft.TextField(
            label="Buscar por nombre",
            prefix_icon=ft.icons.SEARCH,
            border_radius=10,
            width=320,
            height=48,
            text_size=16
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
            width=220,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Tarjeta"),
                ft.dropdown.Option("Transferencia")
            ],
            border_radius=10,
            text_size=16
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
            label="Cliente",
            prefix_icon=ft.icons.SEARCH,
            border_radius=8,
            hint_text="Buscar cliente...",
            width=500,
        )
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
                ft.dropdown.Option("Tarjeta"),
                ft.dropdown.Option("Transferencia")
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
            hint_text="Agregar observaciones...",
        )
        self.new_payment_modal = ft.AlertDialog(
            title=ft.Text("Registrar Nuevo Pago", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Cliente", size=16, weight=ft.FontWeight.BOLD),
                    self.new_payment_client_field,
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
                                self.clear_btn,
                                ft.Container(self.new_payment_btn, alignment=ft.alignment.center_right, padding=ft.padding.only(left=30)),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                            expand=True,
                        ),
                        padding=ft.padding.only(bottom=50, left=10),
                        alignment=ft.alignment.top_left,
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
        self.new_payment_modal.open = False
        self.page.update()

    def load_data(self):
        """
        Carga los datos iniciales de la vista
        """
        # Ya no se carga el resumen
        # summary = self.payment_controller.get_payment_summary()
        # self.update_summary_cards(summary)
        
        # Cargar pagos
        payments = self.payment_controller.get_payments()
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
                            col_span=6
                        )
                    ]
                )
            )
        else:
            for payment in payments:
                self.payments_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(f"{payment.miembro.nombre} {payment.miembro.apellido}")),
                            ft.DataCell(ft.Text(payment.fecha_pago.strftime("%d/%m/%Y"))),
                            ft.DataCell(ft.Text(f"${payment.monto}")),
                            ft.DataCell(ft.Text(payment.metodo_pago.descripcion)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        "Pagado" if payment.estado else "Pendiente",
                                        color=ft.colors.GREEN if payment.estado else ft.colors.ORANGE
                                    ),
                                    bgcolor=ft.colors.GREY_100 if payment.estado else ft.colors.ORANGE_100,
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

    def apply_filters(self, e):
        """
        Aplica los filtros seleccionados
        """
        filters = {}
        
        if self.search_field.value:
            filters['member_name'] = self.search_field.value
        
        if self.date_from.value:
            filters['date_from'] = self.date_from.value
        
        if self.date_to.value:
            filters['date_to'] = self.date_to.value
        
        if self.payment_method.value and self.payment_method.value != "Todos":
            filters['payment_method'] = self.payment_method.value
        
        payments = self.payment_controller.get_payments(filters)
        self.update_payments_table(payments)

    def clear_filters(self, e):
        """
        Limpia todos los filtros
        """
        self.search_field.value = ""
        self.date_from.value = None
        self.date_to.value = None
        self.payment_method.value = "Todos"
        self.page.update()
        
        # Recargar datos sin filtros
        self.load_data()

    def edit_payment(self, payment):
        """
        Abre el modal para editar un pago
        """
        # TODO: Implementar edición de pago
        self.show_message("Función en desarrollo", ft.colors.ORANGE)

    def delete_payment(self, payment):
        """
        Elimina un pago
        """
        success, message = self.payment_controller.delete_payment(payment.id_pago)
        if success:
            self.show_message(message, ft.colors.GREEN)
            self.load_data()
        else:
            self.show_message(message, ft.colors.RED)

    def generate_receipt(self, payment):
        """
        Genera un comprobante de pago
        """
        # TODO: Implementar generación de comprobante
        self.show_message("Función en desarrollo", ft.colors.ORANGE)

    def save_payment(self, e):
        """
        Guarda un nuevo pago
        """
        # TODO: Implementar validación de campos
        payment_data = {
            'fecha_pago': datetime.now(),
            'monto': float(self.new_payment_amount_field.value),
            'id_miembro': 1,  # TODO: Obtener ID del miembro seleccionado
            'id_metodo_pago': 1,  # TODO: Obtener ID del método de pago seleccionado
        }
        
        success, message = self.payment_controller.create_payment(payment_data)
        if success:
            self.show_message(message, ft.colors.GREEN)
            self.close_modal(e)
            self.load_data()
        else:
            self.show_message(message, ft.colors.RED)

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

    def open_date_picker(self, picker):
        picker.open = True
        self.page.update()

    def on_new_payment_date_change(self, e):
        self.new_payment_date_value = self.new_payment_date_picker.value
        value = self.new_payment_date_picker.value.strftime("%d/%m/%Y") if self.new_payment_date_picker.value else "Seleccionar fecha"
        self.new_payment_date_field.content.controls[0].value = value
        self.page.update()
