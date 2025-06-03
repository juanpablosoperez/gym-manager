import flet as ft
from gym_manager.views.module_views import ModuleView
from gym_manager.models.payment import Pago
from gym_manager.controllers.payment_controller import PaymentController
from gym_manager.utils.database import get_db_session
from gym_manager.controllers.monthly_fee_controller import MonthlyFeeController
from datetime import datetime, timedelta
from gym_manager.utils.navigation import navigate_to_login
from gym_manager.models.member import Miembro
from gym_manager.models.payment_method import MetodoPago
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import os
from pathlib import Path
from gym_manager.models.monthly_fee import CuotaMensual
from gym_manager.utils.database import session_scope

class PaymentsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Pagos")
        self.payment_controller = PaymentController(get_db_session())
        self.monthly_fee_controller = MonthlyFeeController(get_db_session())
        self.db_session = get_db_session()
        self.current_monthly_fee = None  # Variable para almacenar la cuota mensual actual
        self.setup_payment_view()
        self.load_data()
        self.export_type = None  # Agregar variable para el tipo de exportación
        self.check_overdue_payments()  # Verificar pagos vencidos al iniciar

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
            on_change=self.validate_payment_amount
        )
        
        # Mensaje de advertencia para el monto
        self.amount_warning_text = ft.Text(
            "",
            color=ft.colors.RED,
            size=12,
            visible=False
        )

        # Actualizar el dropdown de métodos de pago para que cargue los métodos activos
        self.new_payment_method_field = ft.Dropdown(
            label="Método de pago",
            options=[],  # Se llenará dinámicamente
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
                    self.amount_warning_text,  # Agregar el mensaje de advertencia aquí
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
            options=[],  # Se llenará dinámicamente
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
            content=ft.Text("¿Estás seguro que deseas cancelar este pago? El pago cancelado no se mostrará más en la lista.", size=16),
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

        # Modal de exportación
        self.export_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exportación", size=22, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "¿Deseas exportar los pagos?\n"
                "El archivo se guardará en tu carpeta de Descargas.",
                size=16
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.close_export_dialog,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.ElevatedButton(
                    "Exportar",
                    on_click=self.confirm_export,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        self.page.overlay.append(self.export_dialog)

        # Modal de confirmación de comprobante
        self.receipt_confirm_modal = ft.AlertDialog(
            title=ft.Text("Generar Comprobante", size=22, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "¿Deseas generar el comprobante de pago?\n"
                "El archivo se guardará en tu carpeta de Descargas.",
                size=16
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.close_receipt_modal,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.ElevatedButton(
                    "Generar",
                    on_click=self.confirm_generate_receipt,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        self.page.overlay.append(self.receipt_confirm_modal)
        self.selected_payment_for_receipt = None

        # Agregar el indicador de cuota mensual
        self.monthly_fee_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.icons.ATTACH_MONEY,
                                color=ft.colors.BLUE_900,
                                size=32
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Cuota Mensual",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLUE_900
                                    ),
                                    ft.Text(
                                        f"${self.monthly_fee_controller.get_current_fee().monto:,.2f}" if self.monthly_fee_controller.get_current_fee() else "No configurada",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLUE_900
                                    )
                                ],
                                spacing=2
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_color=ft.colors.BLUE_900,
                                tooltip="Editar cuota mensual",
                                on_click=self.show_edit_fee_modal
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10
                    )
                ],
                spacing=5
            ),
            padding=20,
            border_radius=12,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.GREY_300,
            )
        )

        # Modal para editar la cuota mensual
        self.edit_fee_field = ft.TextField(
            label="Nueva cuota mensual",
            prefix_icon=ft.icons.ATTACH_MONEY,
            border_radius=8,
            width=300,
            value=str(self.monthly_fee_controller.get_current_fee().monto) if self.monthly_fee_controller.get_current_fee() else "0.00"
        )

        # DatePicker para la fecha de actualización
        self.edit_fee_date_picker = ft.DatePicker(
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2025, 12, 31),
            on_change=self.on_edit_fee_date_change
        )
        self.page.overlay.append(self.edit_fee_date_picker)
        self.edit_fee_date_value = None
        self.edit_fee_date_field = ft.Container(
            content=ft.Row([
                ft.Text(self.edit_fee_date_value.strftime("%d/%m/%Y") if self.edit_fee_date_value else "Seleccionar fecha",
                        size=16,
                        color=ft.colors.BLACK54),
                ft.Icon(ft.icons.CALENDAR_TODAY, size=20, color=ft.colors.GREY_700),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            width=300,
            on_click=lambda e: self.open_date_picker(self.edit_fee_date_picker),
            bgcolor=ft.colors.GREY_100,
            tooltip="Seleccionar fecha",
        )

        self.edit_fee_modal = ft.AlertDialog(
            title=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.ATTACH_MONEY,
                            color=ft.colors.BLUE_900,
                            size=32
                        ),
                        ft.Text(
                            "Editar Cuota Mensual",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE_900
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                padding=ft.padding.only(bottom=20)
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Monto Actual",
                                        size=14,
                                        color=ft.colors.GREY_700
                                    ),
                                    ft.Text(
                                        f"${self.monthly_fee_controller.get_current_fee().monto:,.2f}" if self.monthly_fee_controller.get_current_fee() else "$0.00",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLUE_900
                                    ),
                                    ft.Text(
                                        f"Última actualización: {self.monthly_fee_controller.get_current_fee().fecha_actualizacion.strftime('%d/%m/%Y')}" if self.monthly_fee_controller.get_current_fee() else "No hay fecha de actualización",
                                        size=12,
                                        color=ft.colors.GREY_600
                                    )
                                ],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.only(bottom=20)
                        ),
                        ft.Container(
                            content=ft.Divider(height=1, color=ft.colors.GREY_300),
                            margin=ft.margin.only(bottom=20)
                        ),
                        ft.Text(
                            "Nuevo Monto",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE_900
                        ),
                        self.edit_fee_field,
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20,
                bgcolor=ft.colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.colors.GREY_300,
                )
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.close_edit_fee_modal,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.ElevatedButton(
                    "Guardar",
                    on_click=self.save_monthly_fee,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True
        )
        self.page.overlay.append(self.edit_fee_modal)

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
                                    expand=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=20,
                        ),
                        padding=ft.padding.only(bottom=10, left=10),
                        alignment=ft.alignment.top_left,
                        width=1300,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.monthly_fee_card,  # Mover la tarjeta aquí
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
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
        self.selected_member_data = None
        self.member_search_results.visible = False
        self.new_payment_date_value = None
        self.new_payment_date_picker.value = None
        self.new_payment_date_field.content.controls[0].value = "Seleccionar fecha"
        self.new_payment_amount_field.value = "0.00"
        self.amount_warning_text.visible = False  # Ocultar el mensaje al cerrar
        self.new_payment_method_field.value = None
        self.new_payment_observations_field.value = ""
        self.new_payment_observations_field.height = 100
        self.new_payment_modal.open = False
        self.page.update()

    def load_data(self):
        """
        Carga los datos iniciales de la vista
        """
        # Cargar pagos
        payments = [p for p in self.payment_controller.get_payments() if p.estado == 1]
        self.update_payments_table(payments)

        # Cargar la cuota mensual actual
        try:
            with session_scope() as session:
                current_fee = session.query(CuotaMensual).filter_by(activo=1).first()
                self.current_monthly_fee = current_fee.monto if current_fee else None
        except Exception as e:
            print(f"Error al cargar cuota mensual: {str(e)}")
            self.current_monthly_fee = None

        # Cargar métodos de pago activos
        active_payment_methods = self.db_session.query(MetodoPago).filter_by(estado=True).all()
        self.new_payment_method_field.options = [
            ft.dropdown.Option(method.descripcion) for method in active_payment_methods
        ]
        self.edit_payment_method_field.options = [
            ft.dropdown.Option(method.descripcion) for method in active_payment_methods
        ]
        self.payment_method.options = [
            ft.dropdown.Option("Todos")
        ] + [
            ft.dropdown.Option(method.descripcion) for method in active_payment_methods
        ]
        self.page.update()

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
                            )
                        ),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
                        ft.DataCell(ft.Container()),
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
        Prepara la generación del comprobante de pago
        """
        self.selected_payment_for_receipt = payment
        self.receipt_confirm_modal.open = True
        self.page.update()

    def close_receipt_modal(self, e):
        """
        Cierra el modal de confirmación del comprobante
        """
        self.receipt_confirm_modal.open = False
        self.selected_payment_for_receipt = None
        self.page.update()

    def confirm_generate_receipt(self, e):
        """
        Confirma la generación del comprobante
        """
        if not self.selected_payment_for_receipt:
            self.show_message("No hay pago seleccionado", ft.colors.RED)
            return

        try:
            print("Iniciando generación de comprobante...")  # Debug
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # Generar nombre del archivo
            downloads_path = str(Path.home() / "Downloads")
            filename = f"comprobante_pago_{self.selected_payment_for_receipt.id_pago}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(downloads_path, filename)
            print(f"Ruta del comprobante: {filepath}")  # Debug

            # Crear el documento PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                spaceAfter=30,
                alignment=1,  # Centrado
                textColor=colors.HexColor('#1F4E78')
            )
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=16,
                spaceAfter=12,
                alignment=1,
                textColor=colors.HexColor('#1F4E78')
            )
            normal_style = styles['Normal']
            bold_style = ParagraphStyle(
                'Bold',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#1F4E78')
            )
            value_style = ParagraphStyle(
                'Value',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black
            )

            # Contenido del PDF
            elements = []

            # Título con línea decorativa
            title = Paragraph("COMPROBANTE DE PAGO", title_style)
            elements.append(title)
            elements.append(Spacer(1, 10))
            
            # Línea decorativa
            line = Table([['']], colWidths=[7*inch])
            line_style = TableStyle([
                ('LINEBELOW', (0, 0), (0, 0), 2, colors.HexColor('#1F4E78')),
                ('TOPPADDING', (0, 0), (0, 0), 5),
                ('BOTTOMPADDING', (0, 0), (0, 0), 5),
            ])
            line.setStyle(line_style)
            elements.append(line)
            elements.append(Spacer(1, 20))

            # Número de comprobante
            receipt_number = Paragraph(f"N° {self.selected_payment_for_receipt.id_pago:06d}", subtitle_style)
            elements.append(receipt_number)
            elements.append(Spacer(1, 30))

            # Información del pago con diseño mejorado
            payment_info = [
                ["Fecha:", self.selected_payment_for_receipt.fecha_pago.strftime("%d/%m/%Y")],
                ["Miembro:", f"{self.selected_payment_for_receipt.miembro.nombre} {self.selected_payment_for_receipt.miembro.apellido}"],
                ["Documento:", self.selected_payment_for_receipt.miembro.documento],
                ["Método de Pago:", self.selected_payment_for_receipt.metodo_pago.descripcion],
                ["Monto:", f"${self.selected_payment_for_receipt.monto:,.2f}"],
                ["Estado:", "PAGADO" if self.selected_payment_for_receipt.estado == 1 else "CANCELADO"]
            ]

            # Crear tabla de información con estilo mejorado
            table = Table(payment_info, colWidths=[2*inch, 4*inch])
            table_style = TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F4E78')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ])
            table.setStyle(table_style)
            elements.append(table)
            elements.append(Spacer(1, 30))

            # Observaciones si existen
            if self.selected_payment_for_receipt.referencia:
                elements.append(Paragraph("Observaciones:", bold_style))
                elements.append(Spacer(1, 5))
                elements.append(Paragraph(self.selected_payment_for_receipt.referencia, value_style))
                elements.append(Spacer(1, 30))

            # Línea decorativa
            line = Table([['']], colWidths=[7*inch])
            line_style = TableStyle([
                ('LINEBELOW', (0, 0), (0, 0), 1, colors.HexColor('#E0E0E0')),
                ('TOPPADDING', (0, 0), (0, 0), 5),
                ('BOTTOMPADDING', (0, 0), (0, 0), 5),
            ])
            line.setStyle(line_style)
            elements.append(line)
            elements.append(Spacer(1, 20))

            # Pie de página con fecha y hora
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1
            )
            footer = Paragraph(
                f"Comprobante generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                footer_style
            )
            elements.append(footer)

            # Generar el PDF
            print("Construyendo comprobante...")  # Debug
            doc.build(elements)
            print("Comprobante generado exitosamente")  # Debug

            # Mostrar mensaje de éxito
            self.show_message(f"Comprobante guardado en: {filepath}", ft.colors.GREEN)
            
            # Cerrar el modal
            self.close_receipt_modal(e)

        except Exception as e:
            print(f"Error al generar comprobante: {str(e)}")  # Debug
            self.show_message(f"Error al generar el comprobante: {str(e)}", ft.colors.RED)
            self.close_receipt_modal(e)

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
        # Guardar solo los datos necesarios del miembro
        self.selected_member_data = {
            'id': member.id_miembro,
            'nombre': member.nombre,
            'apellido': member.apellido
        }
        self.new_payment_client_field.value = f"{member.nombre} {member.apellido}"
        self.member_search_results.visible = False
        self.member_search_results_container.height = 0
        self.page.update()

    def save_payment(self, e):
        """
        Guarda un nuevo pago
        """
        print("Iniciando guardado de pago...")  # Debug log
        
        # Validaciones iniciales
        if not self.selected_member_data:
            self.show_message("Debe seleccionar un miembro", ft.colors.RED)
            return

        if not self.new_payment_date_value:
            self.show_message("Debe seleccionar una fecha", ft.colors.RED)
            return

        try:
            monto = float(self.new_payment_amount_field.value)
            if monto <= 0:
                self.show_message("Debe ingresar un monto válido", ft.colors.RED)
                return
        except ValueError:
            self.show_message("El monto ingresado no es válido", ft.colors.RED)
            return

        if not self.new_payment_method_field.value:
            self.show_message("Debe seleccionar un método de pago", ft.colors.RED)
            return

        try:
            # Limpiar cualquier transacción pendiente
            if hasattr(self, 'db_session'):
                try:
                    self.db_session.rollback()
                except:
                    pass
                self.db_session.close()
            
            print("Obteniendo ID del método de pago...")  # Debug log
            metodo_pago_id = self.get_payment_method_id(self.new_payment_method_field.value)
            if not metodo_pago_id:
                self.show_message("Error al obtener el método de pago", ft.colors.RED)
                return

            print("Preparando datos del pago...")  # Debug log
            payment_data = {
                'fecha_pago': self.new_payment_date_value,
                'monto': monto,
                'id_miembro': self.selected_member_data['id'],
                'id_metodo_pago': metodo_pago_id,
                'referencia': self.new_payment_observations_field.value
            }
            
            print("Llamando al controlador para crear el pago...")  # Debug log
            success, message = self.payment_controller.create_payment(payment_data)
            
            if success:
                print("Pago creado exitosamente")  # Debug log
                self.show_message(message, ft.colors.GREEN)
                self.close_modal(e)
                self.load_data()
            else:
                print(f"Error al crear el pago: {message}")  # Debug log
                self.show_message(message, ft.colors.RED)
        except Exception as e:
            print(f"Error inesperado al guardar el pago: {str(e)}")  # Debug log
            self.show_message(f"Error al guardar el pago: {str(e)}", ft.colors.RED)

    def get_payment_method_id(self, method_name):
        """
        Obtiene el ID del método de pago según su nombre
        """
        try:
            with session_scope() as session:
                method = session.query(MetodoPago).filter_by(descripcion=method_name).first()
                return method.id_metodo_pago if method else None
        except Exception as e:
            print(f"Error al obtener método de pago: {str(e)}")
            return None

    def show_message(self, message: str, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=5000 if color == ft.colors.ORANGE else 3000,  # 5 segundos para advertencias, 3 para otros mensajes
            action="OK",
            action_color=ft.colors.WHITE
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
        """
        Exporta los pagos actuales a un archivo Excel
        """
        try:
            self.export_type = "excel"  # Establecer tipo de exportación
            
            # Obtener los pagos filtrados actuales
            filters = {}
            
            if self.search_field.value:
                filters['member_name'] = self.search_field.value
            
            if self.date_from.value:
                filters['date_from'] = self.date_from.value
            
            if self.date_to.value:
                filters['date_to'] = self.date_to.value
            
            if self.payment_method.value and self.payment_method.value != "Todos":
                filters['payment_method'] = self.payment_method.value
            
            # Aplicar filtro de estado
            if self.status_filter.value == "Pagado":
                filters['estado'] = 1
            elif self.status_filter.value == "Cancelado":
                filters['estado'] = 0

            payments = self.payment_controller.get_payments(filters)
            # Filtrar por estado aquí también para asegurarnos
            if 'estado' in filters:
                payments = [p for p in payments if p.estado == filters['estado']]
            
            if not payments:
                self.show_message("No hay pagos para exportar", ft.colors.ORANGE)
                return

            # Actualizar el contenido del diálogo con el número de pagos
            self.export_dialog.content.value = f"¿Deseas exportar {len(payments)} pagos a Excel?\nEl archivo se guardará en tu carpeta de Descargas."
            
            # Mostrar el diálogo
            self.export_dialog.open = True
            self.page.update()

        except Exception as e:
            self.show_message(f"Error al preparar la exportación: {str(e)}", ft.colors.RED)

    def export_to_pdf(self, e):
        """
        Exporta los pagos actuales a un archivo PDF
        """
        try:
            print("Iniciando exportación a PDF...")  # Debug
            self.export_type = "pdf"  # Establecer tipo de exportación
            print(f"Tipo de exportación establecido: {self.export_type}")  # Debug
            
            # Obtener los pagos filtrados actuales
            filters = {}
            
            if self.search_field.value:
                filters['member_name'] = self.search_field.value
            
            if self.date_from.value:
                filters['date_from'] = self.date_from.value
            
            if self.date_to.value:
                filters['date_to'] = self.date_to.value
            
            if self.payment_method.value and self.payment_method.value != "Todos":
                filters['payment_method'] = self.payment_method.value
            
            # Aplicar filtro de estado
            if self.status_filter.value == "Pagado":
                filters['estado'] = 1
            elif self.status_filter.value == "Cancelado":
                filters['estado'] = 0

            payments = self.payment_controller.get_payments(filters)
            # Filtrar por estado aquí también para asegurarnos
            if 'estado' in filters:
                payments = [p for p in payments if p.estado == filters['estado']]
            
            print(f"Número de pagos a exportar: {len(payments)}")  # Debug
            
            if not payments:
                self.show_message("No hay pagos para exportar", ft.colors.ORANGE)
                return

            # Actualizar el contenido del diálogo con el número de pagos
            self.export_dialog.content.value = f"¿Deseas exportar {len(payments)} pagos a PDF?\nEl archivo se guardará en tu carpeta de Descargas."
            
            # Guardar los pagos en una variable de instancia para usarla en confirm_export
            self.payments_to_export = payments
            
            # Mostrar el diálogo
            self.export_dialog.open = True
            self.page.update()

        except Exception as e:
            print(f"Error en export_to_pdf: {str(e)}")  # Debug
            self.show_message(f"Error al preparar la exportación: {str(e)}", ft.colors.RED)

    def confirm_export(self, e):
        """
        Confirma la exportación y genera el archivo
        """
        try:
            print("Iniciando confirmación de exportación...")  # Debug
            print(f"Tipo de exportación actual: {self.export_type}")  # Debug
            
            # Obtener la ruta de la carpeta de descargas
            downloads_path = str(Path.home() / "Downloads")
            print(f"Ruta de descargas: {downloads_path}")  # Debug

            # Usar los pagos guardados en export_to_pdf
            payments = getattr(self, 'payments_to_export', [])
            if not payments:
                self.show_message("No hay pagos para exportar", ft.colors.ORANGE)
                return

            print(f"Número de pagos a exportar: {len(payments)}")  # Debug

            # Determinar el tipo de exportación
            if self.export_type == "excel":
                print("Exportando a Excel...")  # Debug
                self._export_to_excel(payments, downloads_path)
            elif self.export_type == "pdf":
                print("Exportando a PDF...")  # Debug
                self._export_to_pdf(payments, downloads_path)
            else:
                print(f"Error: Tipo de exportación no válido: {self.export_type}")  # Debug
                self.show_message("Error: Tipo de exportación no válido", ft.colors.RED)
                return

            # Limpiar los pagos guardados
            self.payments_to_export = None

            # Cerrar el diálogo de confirmación
            self.close_export_dialog(e)

        except Exception as e:
            print(f"Error en confirm_export: {str(e)}")  # Debug
            self.show_message(f"Error al exportar: {str(e)}", ft.colors.RED)

    def close_export_dialog(self, e):
        """
        Cierra el diálogo de exportación
        """
        self.export_dialog.open = False
        self.export_type = None  # Resetear el tipo de exportación
        self.page.update()

    def _export_to_excel(self, payments, downloads_path):
        """
        Exporta los pagos a Excel
        """
        # Crear un nuevo libro de Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Pagos"

        # Estilos
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        money_format = '#,##0.00'
        date_format = 'dd/mm/yyyy'

        # Configurar ancho de columnas
        ws.column_dimensions['A'].width = 30  # Miembro
        ws.column_dimensions['B'].width = 15  # Fecha
        ws.column_dimensions['C'].width = 15  # Monto
        ws.column_dimensions['D'].width = 20  # Método
        ws.column_dimensions['E'].width = 30  # Observaciones
        ws.column_dimensions['F'].width = 15  # Estado

        # Escribir encabezados
        headers = ["Miembro", "Fecha", "Monto", "Método", "Observaciones", "Estado"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border

        # Escribir datos
        for row, payment in enumerate(payments, 2):
            # Miembro
            cell = ws.cell(row=row, column=1)
            cell.value = f"{payment.miembro.nombre} {payment.miembro.apellido}"
            cell.border = border
            cell.alignment = Alignment(horizontal='left', vertical='center')

            # Fecha
            cell = ws.cell(row=row, column=2)
            cell.value = payment.fecha_pago
            cell.number_format = date_format
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')

            # Monto
            cell = ws.cell(row=row, column=3)
            cell.value = payment.monto
            cell.number_format = money_format
            cell.border = border
            cell.alignment = Alignment(horizontal='right', vertical='center')

            # Método
            cell = ws.cell(row=row, column=4)
            cell.value = payment.metodo_pago.descripcion
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')

            # Observaciones
            cell = ws.cell(row=row, column=5)
            cell.value = payment.referencia if payment.referencia else ""
            cell.border = border
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

            # Estado
            cell = ws.cell(row=row, column=6)
            cell.value = "Pagado" if payment.estado == 1 else "Cancelado"
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Color de fondo según estado
            if payment.estado == 1:
                cell.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
            else:
                cell.fill = PatternFill(start_color="FFD9D9", end_color="FFD9D9", fill_type="solid")

        # Congelar la primera fila
        ws.freeze_panes = 'A2'

        # Generar nombre del archivo
        filename = f"pagos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(downloads_path, filename)

        # Guardar archivo
        wb.save(filepath)

        # Mostrar mensaje de éxito
        self.show_message(f"Archivo Excel guardado en: {filepath}", ft.colors.GREEN)

    def _export_to_pdf(self, payments, downloads_path):
        """
        Exporta los pagos a PDF
        """
        try:
            print("Iniciando generación de PDF...")  # Debug
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter, landscape
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
            except ImportError as e:
                print(f"Error al importar reportlab: {str(e)}")  # Debug
                self.show_message("Error: No se pudo importar la biblioteca reportlab. Por favor, asegúrese de que está instalada correctamente.", ft.colors.RED)
                return

            # Generar nombre del archivo
            filename = f"pagos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(downloads_path, filename)
            print(f"Ruta del archivo PDF: {filepath}")  # Debug

            # Crear el documento PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(letter),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Centrado
            )

            # Contenido del PDF
            elements = []

            # Título
            title = Paragraph("Reporte de Pagos", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))

            # Información de filtros aplicados
            filter_info = []
            if self.search_field.value:
                filter_info.append(f"Miembro: {self.search_field.value}")
            if self.date_from.value:
                filter_info.append(f"Desde: {self.date_from.value.strftime('%d/%m/%Y')}")
            if self.date_to.value:
                filter_info.append(f"Hasta: {self.date_to.value.strftime('%d/%m/%Y')}")
            if self.payment_method.value and self.payment_method.value != "Todos":
                filter_info.append(f"Método: {self.payment_method.value}")
            if self.status_filter.value != "Todos":
                filter_info.append(f"Estado: {self.status_filter.value}")

            if filter_info:
                filter_text = " | ".join(filter_info)
                filter_paragraph = Paragraph(f"Filtros aplicados: {filter_text}", styles["Normal"])
                elements.append(filter_paragraph)
                elements.append(Spacer(1, 20))

            # Datos de la tabla
            data = [["Miembro", "Fecha", "Monto", "Método", "Observaciones", "Estado"]]
            
            for payment in payments:
                data.append([
                    f"{payment.miembro.nombre} {payment.miembro.apellido}",
                    payment.fecha_pago.strftime("%d/%m/%Y"),
                    f"${payment.monto:,.2f}",
                    payment.metodo_pago.descripcion,
                    payment.referencia if payment.referencia else "",
                    "Pagado" if payment.estado == 1 else "Cancelado"
                ])

            # Crear la tabla
            table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.5*inch, 2.5*inch, 1.2*inch])
            
            # Estilo de la tabla
            table_style = TableStyle([
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                
                # Alineación específica
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Miembro
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Monto
                ('ALIGN', (4, 1), (4, -1), 'LEFT'),  # Observaciones
            ])

            # Agregar colores de fondo según estado
            for i, payment in enumerate(payments, 1):
                if payment.estado == 1:
                    table_style.add('BACKGROUND', (5, i), (5, i), colors.HexColor('#E2EFDA'))
                else:
                    table_style.add('BACKGROUND', (5, i), (5, i), colors.HexColor('#FFD9D9'))

            table.setStyle(table_style)
            elements.append(table)

            # Pie de página con fecha y hora
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1
            )
            footer = Paragraph(
                f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                footer_style
            )
            elements.append(Spacer(1, 20))
            elements.append(footer)

            # Generar el PDF
            print("Construyendo PDF...")  # Debug
            doc.build(elements)
            print("PDF generado exitosamente")  # Debug

            # Mostrar mensaje de éxito
            self.show_message(f"Archivo PDF guardado en: {filepath}", ft.colors.GREEN)

        except Exception as e:
            print(f"Error en _export_to_pdf: {str(e)}")  # Debug
            self.show_message(f"Error al generar PDF: {str(e)}", ft.colors.RED)
            raise  # Re-lanzar la excepción para ver el error completo

    def check_overdue_payments(self):
        """
        Verifica los pagos vencidos y muestra una alerta
        """
        try:
            # Obtener todos los miembros
            members = self.db_session.query(Miembro).all()
            overdue_members = []

            for member in members:
                # Obtener el último pago del miembro
                last_payment = self.db_session.query(Pago).filter(
                    Pago.id_miembro == member.id_miembro,
                    Pago.estado == 1  # Solo pagos activos
                ).order_by(Pago.fecha_pago.desc()).first()

                if last_payment:
                    # Calcular días desde el último pago
                    days_since_payment = (datetime.now() - last_payment.fecha_pago).days
                    
                    # Si han pasado más de 30 días, agregar a la lista de vencidos
                    if days_since_payment > 30:
                        overdue_members.append({
                            'member': member,
                            'days_overdue': days_since_payment,
                            'last_payment_date': last_payment.fecha_pago,
                            'last_payment_amount': last_payment.monto,
                            'payment_method': last_payment.metodo_pago.descripcion
                        })

            if overdue_members:
                # Crear el contenido de la alerta
                alert_content = ft.Column(
                    controls=[
                        # Encabezado con icono
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        name=ft.icons.WARNING_ROUNDED,
                                        size=40,
                                        color=ft.colors.RED_700
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                "¡Atención! Pagos Vencidos",
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.colors.RED_700
                                            ),
                                            ft.Text(
                                                "Los siguientes miembros tienen pagos pendientes:",
                                                size=16,
                                                color=ft.colors.GREY_700
                                            )
                                        ],
                                        spacing=5
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=15
                            ),
                            padding=ft.padding.only(bottom=20)
                        ),
                        
                        # Lista de miembros con pagos vencidos
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                # Encabezado de la tarjeta
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(
                                                            name=ft.icons.PERSON,
                                                            color=ft.colors.BLUE_900,
                                                            size=24
                                                        ),
                                                        ft.Text(
                                                            f"{m['member'].nombre} {m['member'].apellido}",
                                                            size=16,
                                                            weight=ft.FontWeight.BOLD,
                                                            color=ft.colors.BLUE_900
                                                        ),
                                                        ft.Container(
                                                            content=ft.Text(
                                                                f"Vencido hace {m['days_overdue']} días",
                                                                color=ft.colors.WHITE,
                                                                weight=ft.FontWeight.BOLD,
                                                                size=12
                                                            ),
                                                            bgcolor=ft.colors.RED_700,
                                                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                                            border_radius=20
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                ),
                                                
                                                # Línea separadora
                                                ft.Container(
                                                    content=ft.Divider(height=1, color=ft.colors.GREY_300),
                                                    margin=ft.margin.symmetric(vertical=10)
                                                ),
                                                
                                                # Detalles del pago
                                                ft.Row(
                                                    controls=[
                                                        ft.Column(
                                                            controls=[
                                                                ft.Text(
                                                                    "Último Pago",
                                                                    size=12,
                                                                    color=ft.colors.GREY_600
                                                                ),
                                                                ft.Text(
                                                                    m['last_payment_date'].strftime("%d/%m/%Y"),
                                                                    size=14,
                                                                    weight=ft.FontWeight.BOLD
                                                                )
                                                            ],
                                                            spacing=2
                                                        ),
                                                        ft.Column(
                                                            controls=[
                                                                ft.Text(
                                                                    "Monto",
                                                                    size=12,
                                                                    color=ft.colors.GREY_600
                                                                ),
                                                                ft.Text(
                                                                    f"${m['last_payment_amount']:,.2f}",
                                                                    size=14,
                                                                    weight=ft.FontWeight.BOLD
                                                                )
                                                            ],
                                                            spacing=2
                                                        ),
                                                        ft.Column(
                                                            controls=[
                                                                ft.Text(
                                                                    "Método",
                                                                    size=12,
                                                                    color=ft.colors.GREY_600
                                                                ),
                                                                ft.Text(
                                                                    m['payment_method'],
                                                                    size=14,
                                                                    weight=ft.FontWeight.BOLD
                                                                )
                                                            ],
                                                            spacing=2
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                )
                                            ],
                                            spacing=5
                                        ),
                                        border=ft.border.all(1, ft.colors.GREY_300),
                                        border_radius=12,
                                        padding=15,
                                        bgcolor=ft.colors.WHITE,
                                        shadow=ft.BoxShadow(
                                            spread_radius=1,
                                            blur_radius=10,
                                            color=ft.colors.GREY_300,
                                        ),
                                        margin=ft.margin.only(bottom=10)
                                    ) for m in overdue_members
                                ],
                                scroll=ft.ScrollMode.AUTO,
                                height=300
                            ),
                            margin=ft.margin.only(top=10, bottom=10)
                        ),
                        
                        # Pie de página
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Acción Requerida",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLUE_900
                                    ),
                                    ft.Text(
                                        "Por favor, contacte a estos miembros para regularizar sus pagos lo antes posible.",
                                        size=14,
                                        color=ft.colors.GREY_700
                                    )
                                ],
                                spacing=5,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.symmetric(vertical=10),
                            bgcolor=ft.colors.BLUE_50,
                            border_radius=8
                        )
                    ],
                    spacing=10,
                    width=600
                )

                # Crear el diálogo de alerta
                self.overdue_alert = ft.AlertDialog(
                    title=None,  # Quitamos el título por defecto
                    content=alert_content,
                    actions=[
                        ft.ElevatedButton(
                            "Entendido",
                            icon=ft.icons.CHECK_CIRCLE,
                            on_click=self.close_overdue_alert,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_900,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=28, vertical=12),
                                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                            )
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    modal=True
                )

                # Mostrar la alerta
                self.page.overlay.append(self.overdue_alert)
                self.overdue_alert.open = True
                self.page.update()

        except Exception as e:
            print(f"Error al verificar pagos vencidos: {str(e)}")

    def close_overdue_alert(self, e):
        """
        Cierra la alerta de pagos vencidos
        """
        if hasattr(self, 'overdue_alert'):
            self.overdue_alert.open = False
            self.page.update()

    def show_edit_fee_modal(self, e):
        """
        Muestra el modal para editar la cuota mensual
        """
        current_fee = self.monthly_fee_controller.get_current_fee()
        if current_fee:
            self.edit_fee_field.value = str(current_fee.monto)
        self.edit_fee_modal.open = True
        self.page.update()

    def close_edit_fee_modal(self, e):
        """
        Cierra el modal de edición de cuota mensual
        """
        self.edit_fee_modal.open = False
        self.page.update()

    def save_monthly_fee(self, e):
        """
        Guarda la nueva cuota mensual
        """
        try:
            new_amount = float(self.edit_fee_field.value)
            if new_amount <= 0:
                self.show_message("El monto debe ser mayor a 0", ft.colors.RED)
                return

            success, message = self.monthly_fee_controller.update_fee(new_amount)
            if success:
                self.show_message(message, ft.colors.GREEN)
                # Actualizar el valor mostrado en la tarjeta
                self.monthly_fee_card.content.controls[0].controls[1].controls[1].value = f"${new_amount:,.2f}"
                # Actualizar la cuota mensual en memoria
                self.current_monthly_fee = new_amount
                self.close_edit_fee_modal(e)
                self.page.update()
            else:
                self.show_message(message, ft.colors.RED)
        except ValueError:
            self.show_message("Por favor, ingrese un monto válido", ft.colors.RED)

    def on_edit_fee_date_change(self, e):
        """
        Maneja el cambio de fecha en el selector de fecha de la cuota mensual
        """
        self.edit_fee_date_value = self.edit_fee_date_picker.value
        value = self.edit_fee_date_picker.value.strftime("%d/%m/%Y") if self.edit_fee_date_picker.value else "Seleccionar fecha"
        self.edit_fee_date_field.content.controls[0].value = value
        self.page.update()

    def validate_payment_amount(self, e):
        """
        Valida el monto ingresado contra la cuota mensual
        """
        try:
            # Solo validar si el valor es un número válido
            amount = float(self.new_payment_amount_field.value)
            
            # Usar la cuota mensual almacenada en memoria
            if self.current_monthly_fee and amount != self.current_monthly_fee:
                self.amount_warning_text.value = f"Advertencia: El monto ingresado (${amount:,.2f}) es diferente a la cuota mensual (${self.current_monthly_fee:,.2f})"
                self.amount_warning_text.visible = True
            else:
                self.amount_warning_text.visible = False
                
            self.page.update()
        except ValueError:
            # Si el valor no es un número válido, ocultamos la advertencia
            self.amount_warning_text.visible = False
            self.page.update()
