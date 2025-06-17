import flet as ft
from gym_manager.views.module_views import ModuleView
from gym_manager.controllers.payment_receipt_controller import PaymentReceiptController
from gym_manager.utils.database import get_db_session
from datetime import datetime
import os
import tempfile

class PaymentReceiptView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Comprobantes de Pago")
        self.payment_receipt_controller = PaymentReceiptController(get_db_session())
        self.setup_view()
        self.load_data()

    def setup_view(self):
        # Título principal
        self.title = ft.Text(
            "Visualiza los Comprobantes de Pago!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        # Campos de fecha
        self.date_from_field = ft.TextField(
            read_only=True,
            border_radius=8,
            width=200,
            height=40,
            hint_text="Seleccionar fecha",
            on_focus=lambda e: self.open_date_picker(self.date_from),
        )

        self.date_to_field = ft.TextField(
            read_only=True,
            border_radius=8,
            width=200,
            height=40,
            hint_text="Seleccionar fecha",
            on_focus=lambda e: self.open_date_picker(self.date_to),
        )

        # Filtros
        self.filters_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Filtros", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            # Fecha desde
                            ft.Column(
                                controls=[
                                    ft.Text("Fecha desde", size=16),
                                    ft.Container(
                                        content=self.date_from_field,
                                        border=ft.border.all(1, ft.colors.GREY_400),
                                        border_radius=8,
                                    ),
                                ],
                            ),
                            # Fecha hasta
                            ft.Column(
                                controls=[
                                    ft.Text("Fecha hasta", size=16),
                                    ft.Container(
                                        content=self.date_to_field,
                                        border=ft.border.all(1, ft.colors.GREY_400),
                                        border_radius=8,
                                    ),
                                ],
                            ),
                            # Botones de filtro
                            ft.Column(
                                controls=[
                                    ft.Text("", size=16),  # Espaciador
                                    ft.Row(
                                        controls=[
                                            ft.ElevatedButton(
                                                "Filtrar",
                                                icon=ft.icons.FILTER_LIST,
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.colors.BLUE_900,
                                                    color=ft.colors.WHITE,
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                                ),
                                                on_click=self.apply_filters
                                            ),
                                            ft.ElevatedButton(
                                                "Limpiar",
                                                icon=ft.icons.CLEAR,
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.colors.GREY_400,
                                                    color=ft.colors.WHITE,
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                                ),
                                                on_click=self.clear_filters
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=20,
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.GREY_300,
            ),
        )

        # Tabla de comprobantes
        self.receipts_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Miembro", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Monto", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Método de Pago", size=18, weight=ft.FontWeight.BOLD)),
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

        # Layout principal
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=self.title,
                        padding=ft.padding.only(bottom=20, top=0, left=10, right=10),
                        alignment=ft.alignment.top_left,
                        width=1200,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            self.filters_container,
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=18,
                                        expand=True,
                                    ),
                                    padding=ft.padding.only(bottom=10, left=10, right=10),
                                    alignment=ft.alignment.top_left,
                                    expand=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=20,
                        ),
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=self.receipts_table,
                                    expand=True,
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.symmetric(horizontal=20),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            expand=True,
                        ),
                        alignment=ft.alignment.center,
                        width=1200,
                        padding=ft.padding.only(top=20),
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

        # Date pickers
        self.date_from = ft.DatePicker(
            on_change=self.on_date_from_change,
        )
        self.date_to = ft.DatePicker(
            on_change=self.on_date_to_change,
        )
        self.page.overlay.extend([self.date_from, self.date_to])

        # Valores de fecha
        self.date_from_value = None
        self.date_to_value = None

    def open_date_picker(self, picker):
        picker.pick_date()

    def on_date_from_change(self, e):
        if e.date:
            self.date_from_value = e.date
            self.date_from_field.value = e.date.strftime("%d/%m/%Y")
            self.page.update()

    def on_date_to_change(self, e):
        if e.date:
            self.date_to_value = e.date
            self.date_to_field.value = e.date.strftime("%d/%m/%Y")
            self.page.update()

    def load_data(self):
        """
        Carga los datos de los comprobantes
        """
        try:
            filters = {}
            if self.date_from_value:
                filters['fecha_desde'] = self.date_from_value
            if self.date_to_value:
                filters['fecha_hasta'] = self.date_to_value

            receipts = self.payment_receipt_controller.get_receipts(filters)
            self.update_receipts_table(receipts)
        except Exception as e:
            self.show_message(f"Error al cargar los comprobantes: {str(e)}", ft.colors.RED)

    def update_receipts_table(self, receipts):
        """
        Actualiza la tabla de comprobantes
        """
        self.receipts_table.rows.clear()
        for receipt in receipts:
            self.receipts_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(receipt['fecha_emision'].strftime("%d/%m/%Y"))),
                        ft.DataCell(ft.Text(receipt['miembro'])),
                        ft.DataCell(ft.Text(f"${receipt['monto']:,.2f}")),
                        ft.DataCell(ft.Text(receipt['metodo_pago'])),
                        ft.DataCell(
                            ft.ElevatedButton(
                                "Ver comprobante",
                                icon=ft.icons.VISIBILITY,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.BLUE_900,
                                    color=ft.colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                ),
                                on_click=lambda e, r=receipt: self.view_receipt(r)
                            )
                        ),
                    ]
                )
            )
        self.page.update()

    def view_receipt(self, receipt):
        """
        Muestra el comprobante seleccionado
        """
        try:
            # Obtener el contenido del comprobante
            pdf_content = self.payment_receipt_controller.get_receipt_content(receipt['id_comprobante'])
            if not pdf_content:
                self.show_message("No se pudo obtener el contenido del comprobante", ft.colors.RED)
                return

            # Crear un archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name

            # Abrir el PDF
            if os.name == 'nt':  # Windows
                os.startfile(temp_file_path)
            elif os.name == 'posix':  # macOS y Linux
                import subprocess
                subprocess.run(['xdg-open', temp_file_path])

        except Exception as e:
            self.show_message(f"Error al mostrar el comprobante: {str(e)}", ft.colors.RED)

    def apply_filters(self, e):
        """
        Aplica los filtros seleccionados
        """
        self.load_data()

    def clear_filters(self, e):
        """
        Limpia los filtros
        """
        self.date_from_value = None
        self.date_to_value = None
        self.date_from_field.value = "Seleccionar fecha"
        self.date_to_field.value = "Seleccionar fecha"
        self.page.update()
        self.load_data()

    def show_message(self, message: str, color: str):
        """
        Muestra un mensaje al usuario
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=3000,
            action="OK",
            action_color=ft.colors.WHITE
        )
        self.page.snack_bar.open = True
        self.page.update() 