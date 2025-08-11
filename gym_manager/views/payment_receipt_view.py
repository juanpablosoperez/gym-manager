import flet as ft
from gym_manager.views.module_views import ModuleView
from gym_manager.controllers.payment_receipt_controller import PaymentReceiptController
from gym_manager.utils.database import get_db_session
from datetime import datetime
import os
import tempfile

class PaymentReceiptView(ModuleView):
    def __init__(self, page: ft.Page):
        # Inicializar variables básicas
        self.page = page
        self.title = "Comprobantes de Pago"
        self.content = None
        
        # Inicializar controlador
        self.payment_receipt_controller = PaymentReceiptController(get_db_session())
        
        # Inicializar paginación ANTES de setup_view
        from gym_manager.utils.pagination import PaginationController, PaginationWidget
        self.pagination_controller = PaginationController(items_per_page=10)
        self.pagination_widget = PaginationWidget(
            self.pagination_controller, 
            on_page_change=self._on_page_change
        )
        
        # Ahora llamar setup_view después de inicializar todo
        self.setup_view()
        # NO llamar load_data aquí, se llamará cuando la vista se muestre

    def setup_view(self):
        # Título principal
        self.title = ft.Text(
            "Visualiza los Comprobantes de Pago!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
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

        # Botón limpiar filtros
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

        # Filtros
        self.filters_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            # Fecha desde
                            ft.Column(
                                controls=[
                                    ft.Text("Fecha desde", size=16),
                                    self.date_from_field,
                                ],
                            ),
                            # Fecha hasta
                            ft.Column(
                                controls=[
                                    ft.Text("Fecha hasta", size=16),
                                    self.date_to_field,
                                ],
                            ),
                            # Botón limpiar
                            ft.Column(
                                controls=[
                                    ft.Text("", size=16),  # Espaciador
                                    self.clear_btn,
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
                                    alignment=ft.alignment.top_left,
                                    padding=ft.padding.symmetric(horizontal=20),
                                    height=600,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            expand=True,
                        ),
                        alignment=ft.alignment.top_left,
                        width=1200,
                        padding=ft.padding.only(top=10),
                    ),
                    # Widget de paginación
                    ft.Container(
                        content=self.pagination_widget.get_widget(),
                        padding=ft.padding.only(top=20, bottom=20),
                        alignment=ft.alignment.center,
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
        # Llamar load_data después de que la vista esté completamente inicializada
        self.page.loop.create_task(self._load_data_async())
        return self.content
    
    async def _load_data_async(self):
        """Carga los datos de forma asíncrona después de que la vista esté lista"""
        try:
            # Pequeño delay para asegurar que la vista esté completamente renderizada
            import asyncio
            await asyncio.sleep(0.1)
            
            print("[DEBUG - Comprobantes] Iniciando load_data asíncrono")
            
            filters = {}
            if self.date_from_value:
                filters['fecha_desde'] = self.date_from_value
            if self.date_to_value:
                filters['fecha_hasta'] = self.date_to_value

            receipts = self.payment_receipt_controller.get_receipts(filters)
            print(f"[DEBUG - Comprobantes] Obtenidos {len(receipts)} comprobantes")
            
            # Actualizar paginación
            self.pagination_controller.set_items(receipts)
            self.pagination_widget.update_items(receipts)
            print("[DEBUG - Comprobantes] Paginación actualizada")
            
            # Actualizar tabla
            self.update_receipts_table(receipts)
            print("[DEBUG - Comprobantes] Tabla actualizada")
            
        except Exception as e:
            print(f"[DEBUG - Comprobantes] Error en load_data asíncrono: {str(e)}")
            self.show_message(f"Error al cargar los comprobantes: {str(e)}", ft.colors.RED)
    
    def _on_page_change(self):
        """Callback cuando cambia la página"""
        self.update_receipts_table()

    def open_date_picker(self, picker):
        picker.open = True
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

    def update_receipts_table(self, receipts=None):
        """
        Actualiza la tabla de comprobantes
        """
        print(f"[DEBUG - Comprobantes] Actualizando tabla con {len(receipts) if receipts else 'None'} comprobantes")
        self.receipts_table.rows.clear()
        
        # Obtener comprobantes de la página actual
        if receipts is None:
            receipts = self.pagination_controller.get_current_page_items()
            print(f"[DEBUG - Comprobantes] Comprobantes de página actual: {len(receipts)}")
        
        if not receipts:
            # Estado vacío consistente
            self.receipts_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Icon(name=ft.icons.RECEIPT_LONG, size=48, color=ft.colors.GREY_400),
                                        ft.Text(
                                            "No se encontraron comprobantes",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.GREY_700
                                        ),
                                        ft.Text(
                                            "Genera o registra comprobantes desde la sección de Pagos",
                                            size=16,
                                            color=ft.colors.GREY_600
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                ),
                                padding=40,
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
                    ]
                )
            )
            self.page.update()
            return

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

    def apply_filters(self):
        """
        Aplica los filtros seleccionados
        """
        # Recargar datos con filtros usando el método asíncrono
        self.page.loop.create_task(self._load_data_async())

    def clear_filters(self, e):
        """
        Limpia los filtros
        """
        self.date_from_value = None
        self.date_to_value = None
        self.date_from.value = None
        self.date_to.value = None
        self.date_from_field.content.controls[0].value = ""
        self.date_to_field.content.controls[0].value = ""
        self.page.update()
        # Recargar datos sin filtros usando el método asíncrono
        self.page.loop.create_task(self._load_data_async())

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