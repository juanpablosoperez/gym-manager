import flet as ft
from gym_manager.views.module_views import ModuleView
from datetime import datetime

class StatisticsView(ModuleView):
    def __init__(self, page: ft.Page, controller):
        super().__init__(page, "Informes y Estadísticas")
        self.controller = controller
        current_year = datetime.now().year

        # --- Componentes de la UI --- 
        # (Se definen aquí para mejor organización)

        # --- Sección de Generación de Informes ---
        self.report_type_dropdown = ft.Dropdown(
            label="Tipo de Informe",
            hint_text="Seleccione un tipo de informe",
            options=[
                ft.dropdown.Option("Informe de Miembros"),
                ft.dropdown.Option("Informe de Pagos"),
            ],
            expand=True, border_radius=8, content_padding=12,
            on_change=self._validate_report_generation
        )

        self.start_date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        self.end_date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        self.page.overlay.extend([self.start_date_picker, self.end_date_picker])

        self.start_date_button = ft.ElevatedButton(
            "Fecha de Inicio", icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self._open_date_picker(self.start_date_picker),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12)
        )
        self.start_date_text = ft.Text("No seleccionada", weight=ft.FontWeight.BOLD)
        
        self.end_date_button = ft.ElevatedButton(
            "Fecha de Fin", icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self._open_date_picker(self.end_date_picker),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12)
        )
        self.end_date_text = ft.Text("No seleccionada", weight=ft.FontWeight.BOLD)

        self.membership_status_dropdown = ft.Dropdown(
            label="Estado de Membresía",
            hint_text="Seleccione un estado",
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Activo"),
                ft.dropdown.Option("Inactivo"),
            ],
            expand=True, 
            border_radius=8, 
            content_padding=ft.padding.symmetric(horizontal=24, vertical=20),
            label_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_500),
            text_style=ft.TextStyle(size=15),
            width=200
        )

        self.generate_report_button = ft.ElevatedButton(
            text="Generar Informe",
            icon=ft.icons.RECEIPT_LONG,
            bgcolor=ft.colors.BLUE_GREY_800,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(vertical=12, horizontal=16)),
            height=48,
            disabled=True  # Inicialmente deshabilitado
        )

        # --- Panel de Estadísticas Dinámicas ---
        # Tarjetas de Métricas (Conservadas)
        self.monthly_payments_card = self._create_summary_card(
            icon_name=ft.icons.PAYMENT_OUTLINED, value="$0.00", 
            description="Pagos del Mes", color=ft.colors.GREEN_600
        )
        self.active_members_today_card = self._create_summary_card(
            icon_name=ft.icons.DIRECTIONS_RUN_OUTLINED, value="0", 
            description="Miembros totales", color=ft.colors.PURPLE_600
        )
        self.expired_memberships_card = self._create_summary_card(
            icon_name=ft.icons.EVENT_BUSY_OUTLINED, value="0", 
            description="Membresías Vencidas", color=ft.colors.RED_ACCENT_200
        )
        self.total_annual_income_card = self._create_summary_card(
            icon_name=ft.icons.SHOW_CHART_OUTLINED, value="$0.00", 
            description=f"Ingresos {current_year}", color=ft.colors.TEAL_500
        )
        
        # Marcadores de posición para gráficos (Conservados)
        self.income_bar_chart = self._create_chart_placeholder("Ingresos por Mes")
        self.payment_method_pie_chart = self._create_chart_placeholder("Distribución de Métodos de Pago")
        self.new_members_line_chart = self._create_chart_placeholder("Nuevos Miembros por Mes")
        self.active_memberships_by_type_chart = self._create_chart_placeholder("Membresías Activas")

        # Indicador de carga (overlay modal)
        self.loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Row(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("  Cargando estadísticas...", size=16),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            actions=[],
        )
        # Asegurar que el overlay contenga el diálogo
        if self.loading_dialog not in self.page.overlay:
            self.page.overlay.append(self.loading_dialog)

    def _create_summary_card(self, icon_name, value=None, description=None, color=ft.colors.PRIMARY, value_text=None, text_value=None, description_value_format="{}"):
        icon_widget = ft.Icon(name=icon_name, size=40, color=color)
        
        text_column_controls = []
        if value is not None:
            text_column_controls.append(ft.Text(value, size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT))
        if value_text is not None:
             text_column_controls.append(ft.Text(description_value_format.format(value_text), size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT))
        if description is not None:
            text_column_controls.append(ft.Text(description, size=14, color=ft.colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.RIGHT))
        if text_value is not None:
            text_column_controls.append(ft.Text(text_value, size=14, weight=ft.FontWeight.NORMAL, text_align=ft.TextAlign.RIGHT))

        text_column = ft.Column(text_column_controls, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, expand=True)

        return ft.Container(
            content=ft.Row(
                [icon_widget, text_column],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
                spacing=20 
            ),
            padding=ft.padding.all(20),
            border_radius=ft.border_radius.all(12),
            bgcolor=ft.colors.WHITE, 
            shadow=ft.BoxShadow(
                spread_radius=1, blur_radius=10, color=ft.colors.BLACK12,
                offset=ft.Offset(1, 1)
            ),
            margin=ft.margin.all(5),
        )

    def _create_chart_placeholder(self, title_text):
        return ft.Container(
            content=ft.Column([
                ft.Text(title_text, size=18, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                ft.Container(ft.ProgressRing(width=40, height=40), alignment=ft.alignment.center, expand=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, spacing=10),
            padding=15, border_radius=12, border=ft.border.all(1, ft.colors.GREY_300),
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=3, color=ft.colors.BLACK12),
            margin=ft.margin.symmetric(vertical=5),
            height=450
        )

    # API pública para mostrar/ocultar el loader desde el controlador o el contenedor
    def show_loading(self):
        try:
            self.loading_dialog.open = True
            self.page.update()
        except Exception:
            pass

    def hide_loading(self):
        try:
            self.loading_dialog.open = False
            self.page.update()
        except Exception:
            pass

    def _open_date_picker(self, picker):
        picker.open = True
        self.page.update()

    def _validate_report_generation(self, e):
        """Valida si se puede generar el informe basado en la selección del dropdown"""
        if self.report_type_dropdown.value:
            self.generate_report_button.disabled = False
            self.generate_report_button.bgcolor = ft.colors.BLUE_GREY_800
        else:
            self.generate_report_button.disabled = True
            self.generate_report_button.bgcolor = ft.colors.GREY_400
        self.page.update()

    def build(self):
        try:
            self.report_type_dropdown.on_change = self._validate_report_generation
            self.start_date_picker.on_change = lambda e: self._update_date_text(self.start_date_text, self.start_date_picker.value)
            self.end_date_picker.on_change = lambda e: self._update_date_text(self.end_date_text, self.end_date_picker.value)

            # --- Encabezado ---
            header_section = ft.Container(
                ft.Column([
                    ft.Text("Informes y Estadísticas", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK87),
                    ft.Text("Visualizá la actividad del gimnasio y generá reportes exportables", size=16, color=ft.colors.GREY_700)
                ], spacing=5),
                padding=ft.padding.only(top=10, bottom=20, left=10, right=10)
            )

            # --- Sección de Generación de Informes (Card) ---
            report_filters_card = ft.Container(
                content=ft.Column([
                    ft.Text("Generación de Informes", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK87),
                    ft.ResponsiveRow([
                        ft.Column([self.report_type_dropdown], col={"xs": 12, "sm": 6, "md": 3}),
                        ft.Column([self.membership_status_dropdown], col={"xs": 12, "sm": 6, "md": 3}),
                        ft.Column([
                            self.start_date_button, self.start_date_text
                            ], col={"xs": 12, "sm": 6, "md": 2}, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                        ft.Column([
                            self.end_date_button, self.end_date_text
                            ], col={"xs": 12, "sm": 6, "md": 2}, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                        # Nueva columna para el botón Generar Informe
                        ft.Column(
                            [self.generate_report_button],
                            col={"xs": 12, "sm": 12, "md": 2},
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
                        )
                    ], spacing=15, run_spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], spacing=15),
                padding=20, margin=ft.margin.only(bottom=25, left=5, right=5),
                border_radius=12, bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_300),
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.colors.BLACK12, offset=ft.Offset(1,1))
            )

            # --- Sección Panel de Estadísticas ---
            metrics_cards_section = ft.ResponsiveRow([
                    ft.Column([self.monthly_payments_card], col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Column([self.active_members_today_card], col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Column([self.expired_memberships_card], col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Column([self.total_annual_income_card], col={"xs": 12, "sm": 6, "md": 3}),
                ], spacing=10, run_spacing=10
            )

            # --- Gráficos (usar placeholders al construir; el controlador los cargará) ---
            charts_section = ft.Column([
                    ft.ResponsiveRow([
                        ft.Column([self.income_bar_chart], col={"xs": 12, "md": 12}),
                    ], spacing=10, run_spacing=10),
                    ft.ResponsiveRow([
                        ft.Column([self.payment_method_pie_chart], col={"xs": 12, "md": 12}),
                    ], spacing=10, run_spacing=10),
                    ft.ResponsiveRow([
                        ft.Column([self.new_members_line_chart], col={"xs": 12, "md": 12}),
                    ], spacing=10, run_spacing=10),
                    ft.ResponsiveRow([
                        ft.Column([self.active_memberships_by_type_chart], col={"xs": 12, "md": 12}),
                    ], spacing=10, run_spacing=10),
                ], spacing=10
            )

            statistics_panel = ft.Container(
                content=ft.Column([
                    ft.Text("Métricas Clave", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK87),
                    metrics_cards_section, # Solo una sección de tarjetas ahora
                    ft.Divider(height=30, thickness=1, color=ft.colors.GREY_300),
                    ft.Text("Análisis Gráfico", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK87),
                    charts_section
                ], spacing=20),
                padding=ft.padding.all(15),
            )
            
            return ft.Container(
                content=ft.Column(
                    controls=[
                        header_section,
                        report_filters_card,
                        statistics_panel
                    ],
                    scroll=ft.ScrollMode.ADAPTIVE,
                    spacing=0, # Controlar espaciado con márgenes de los hijos
                ),
                expand=True,
                bgcolor=ft.colors.WHITE, # Fondo blanco
                padding=ft.padding.symmetric(horizontal=15, vertical=10)
            )
        except Exception:
            return ft.Container(
                content=ft.Column([
                    ft.Text('Error al cargar Estadísticas', color=ft.colors.RED, size=20),
                ], spacing=10),
                padding=20,
            )

    def _update_date_text(self, text_control, date_value):
        if date_value:
            text_control.value = date_value.strftime("%Y-%m-%d")
        else:
            text_control.value = "No seleccionada"
        self.page.update()

    def get_content(self):
        return self.build()

