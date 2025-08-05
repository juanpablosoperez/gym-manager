import flet as ft
from gym_manager.views.module_views import ModuleView
from datetime import datetime
import plotly.graph_objs as go
from flet.plotly_chart import PlotlyChart

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
                ft.Container(ft.ProgressRing(), alignment=ft.alignment.center, expand=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, spacing=10),
            padding=20, border_radius=12, border=ft.border.all(1, ft.colors.GREY_300),
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(1,1)),
            margin=ft.margin.symmetric(vertical=10),
            height=350 
        )

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

        # --- Gráficos ---
        # Ingresos por Mes (datos reales)
        data_ingresos = self.controller.get_monthly_income_data()
        fig_ingresos = go.Figure(
            data=[go.Bar(x=data_ingresos["meses"], y=data_ingresos["ingresos"], marker_color="#1F4E78")],
            layout=go.Layout(
                title=dict(
                    text="Ingresos por Mes",
                    font=dict(size=24, family="Arial", color="black")
                ),
                xaxis=dict(
                    title=dict(
                        text="Mes",
                        font=dict(size=18, family="Arial")
                    ),
                    tickfont=dict(size=18)
                ),
                yaxis=dict(
                    title=dict(
                        text="Ingresos ($)",
                        font=dict(size=18, family="Arial")
                    ),
                    tickfont=dict(size=18)
                ),
                width=800,
                height=600,
                margin=dict(l=50, r=50, t=50, b=50)
            )
        )
        chart_ingresos = ft.Container(
            PlotlyChart(fig_ingresos, expand=True), 
            bgcolor=ft.colors.WHITE, 
            border_radius=12, 
            padding=20, 
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(1,1)), 
            margin=ft.margin.symmetric(vertical=10)
        )

        # Distribución de Métodos de Pago (datos reales)
        data_metodos = self.controller.get_payment_methods_distribution()
        metodos = list(data_metodos.keys())
        valores = list(data_metodos.values())
        fig_metodos = go.Figure(
            data=[go.Pie(
                labels=metodos, 
                values=valores, 
                hole=0.3,
                textfont=dict(size=18)
            )],
            layout=go.Layout(
                title=dict(
                    text="Distribución de Métodos de Pago",
                    font=dict(size=24, family="Arial", color="black")
                ),
                legend=dict(
                    font=dict(size=18)
                ),
                width=800,
                height=600,
                margin=dict(l=50, r=50, t=50, b=50)
            )
        )
        chart_metodos = ft.Container(
            PlotlyChart(fig_metodos, expand=True), 
            bgcolor=ft.colors.WHITE, 
            border_radius=12, 
            padding=20, 
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(1,1)), 
            margin=ft.margin.symmetric(vertical=10)
        )

        # Nuevos Miembros por Mes (datos reales)
        data_nuevos = self.controller.get_new_members_per_month()
        meses = data_nuevos["meses"]
        nuevos = data_nuevos["nuevos"]
        fig_nuevos = go.Figure(
            data=[go.Scatter(
                x=meses, 
                y=nuevos, 
                mode="lines+markers", 
                line=dict(color="#4CAF50"),
                textfont=dict(size=18)
            )],
            layout=go.Layout(
                title=dict(
                    text="Nuevos Miembros por Mes",
                    font=dict(size=24, family="Arial", color="black")
                ),
                xaxis=dict(
                    title=dict(
                        text="Mes",
                        font=dict(size=18, family="Arial")
                    ),
                    tickfont=dict(size=18)
                ),
                yaxis=dict(
                    title=dict(
                        text="Cantidad",
                        font=dict(size=18, family="Arial")
                    ),
                    tickfont=dict(size=18)
                ),
                width=800,
                height=600,
                margin=dict(l=50, r=50, t=50, b=50)
            )
        )
        chart_nuevos = ft.Container(
            PlotlyChart(fig_nuevos, expand=True), 
            bgcolor=ft.colors.WHITE, 
            border_radius=12, 
            padding=20, 
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(1,1)), 
            margin=ft.margin.symmetric(vertical=10)
        )

        # Membresías Activas por Tipo (datos reales)
        data_tipos = self.controller.get_active_memberships_by_type()
        tipos = list(data_tipos.keys())
        activos = list(data_tipos.values())
        fig_tipos = go.Figure(
            data=[go.Bar(
                x=tipos, 
                y=activos, 
                marker_color="#FF9800",
                textfont=dict(size=18)
            )],
            layout=go.Layout(
                title=dict(
                    text="Membresías Activas por Tipo",
                    font=dict(size=24, family="Arial", color="black")
                ),
                xaxis=dict(
                    title=dict(
                        text="Tipo",
                        font=dict(size=18, family="Arial")
                    ),
                    tickfont=dict(size=18)
                ),
                yaxis=dict(
                    title=dict(
                        text="Cantidad",
                        font=dict(size=18, family="Arial")
                    ),
                    tickfont=dict(size=18)
                ),
                width=800,
                height=600,
                margin=dict(l=50, r=50, t=50, b=50)
            )
        )
        chart_tipos = ft.Container(
            PlotlyChart(fig_tipos, expand=True), 
            bgcolor=ft.colors.WHITE, 
            border_radius=12, 
            padding=20, 
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(1,1)), 
            margin=ft.margin.symmetric(vertical=10)
        )

        charts_section = ft.Column([
                ft.ResponsiveRow([
                    ft.Column([chart_ingresos], col={"xs": 12, "md": 6}),
                    ft.Column([chart_metodos], col={"xs": 12, "md": 6}),
                ], spacing=10, run_spacing=10),
                ft.ResponsiveRow([
                    ft.Column([chart_nuevos], col={"xs": 12, "md": 6}),
                    ft.Column([chart_tipos], col={"xs": 12, "md": 6}),
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

    def _update_date_text(self, text_control, date_value):
        if date_value:
            text_control.value = date_value.strftime("%Y-%m-%d")
        else:
            text_control.value = "No seleccionada"
        # No llamar a self.update() aquí, el controlador llamará a page.update()
        # Si esta vista fuera un UserControl, self.update() sería apropiado.
        # Por ahora, la actualización de estos textos la maneja la interacción directa.
        # Si se vuelve más complejo, el controlador podría manejar estos cambios de texto.
        self.page.update() # Necesario para que el texto de la fecha se actualice visualmente.

    def get_content(self):
        return self.build()

