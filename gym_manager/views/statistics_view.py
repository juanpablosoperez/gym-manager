import flet as ft
# from flet.user_control import UserControl # Ya no es necesario
from datetime import datetime

class StatisticsView: # Eliminar la herencia de UserControl
    def __init__(self, page: ft.Page, controller):
        # super().__init__() # Eliminar llamada al super de UserControl
        self.page = page
        self.controller = controller

        # --- Componentes de la UI --- 
        # (Se definen aquí para mejor organización)

        # --- Sección de Generación de Informes ---
        self.report_type_dropdown = ft.Dropdown(
            label="Tipo de Informe",
            hint_text="Seleccione un tipo de informe",
            options=[
                ft.dropdown.Option("Informe de Miembros"),
                ft.dropdown.Option("Informe de Pagos"),
                ft.dropdown.Option("Informe de Ingresos Mensuales"),
                ft.dropdown.Option("Informe por Método de Pago"),
            ],
            expand=True, border_radius=8, content_padding=12
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
            on_click=lambda _: self.start_date_picker.pick_date(),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12)
        )
        self.start_date_text = ft.Text("No seleccionada", weight=ft.FontWeight.BOLD)
        
        self.end_date_button = ft.ElevatedButton(
            "Fecha de Fin", icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.end_date_picker.pick_date(),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=12)
        )
        self.end_date_text = ft.Text("No seleccionada", weight=ft.FontWeight.BOLD)

        self.membership_status_dropdown = ft.Dropdown(
            label="Estado de Membresía",
            hint_text="Seleccione un estado",
            options=[
                ft.dropdown.Option("Todos"), ft.dropdown.Option("Activa"),
                ft.dropdown.Option("Vencida"), ft.dropdown.Option("Suspendida"),
                ft.dropdown.Option("Baja"),
            ],
            expand=True, border_radius=8, content_padding=12
        )

        self.generate_report_button = ft.ElevatedButton(
            text="Generar Informe",
            icon=ft.icons.RECEIPT_LONG, # Icono 🧾
            bgcolor=ft.colors.BLUE_GREY_800,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(vertical=12, horizontal=16)),
            height=48
        )

        # --- Panel de Estadísticas Dinámicas ---
        self.total_members_card = self._create_summary_card(
            icon_name=ft.icons.PEOPLE_ALT_OUTLINED, # Icono 👥
            value="0", description="Miembros Totales",
            color=ft.colors.BLUE_600
        )
        self.monthly_payments_card = self._create_summary_card(
            icon_name=ft.icons.PAYMENT_OUTLINED, # Icono 💳
            value="$0.00", description="Pagos del Mes",
            color=ft.colors.GREEN_600
        )
        self.most_used_method_card = self._create_summary_card(
            icon_name=ft.icons.INSIGHTS, # Icono 🟡 (placeholder)
            value_text="N/A", description_value_format="Método más usado: {}",
            text_value="0 pagos",
            color=ft.colors.ORANGE_600
        )
        self.active_members_today_card = self._create_summary_card(
            icon_name=ft.icons.DIRECTIONS_RUN_OUTLINED, # Icono 🏃‍♂️
            value="0", description="Miembros hoy", # Descripción más corta
            color=ft.colors.PURPLE_600
        )

        # Marcadores de posición para gráficos
        self.income_bar_chart = self._create_chart_placeholder("Ingresos por Mes (últimos 6 meses)")
        self.payment_method_pie_chart = self._create_chart_placeholder("Distribución de Métodos de Pago")
        self.new_members_line_chart = self._create_chart_placeholder("Nuevos Miembros por Mes")

    def _create_summary_card(self, icon_name, value=None, description=None, color=ft.colors.PRIMARY, value_text=None, text_value=None, description_value_format="{}"):
        icon_widget = ft.Icon(name=icon_name, size=40, color=color) # Ícono grande
        
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
                spacing=20 # Espacio entre ícono y texto
            ),
            padding=ft.padding.all(20),
            border_radius=ft.border_radius.all(12),
            bgcolor=ft.colors.WHITE, # Fondo blanco para las cards
            shadow=ft.BoxShadow(
                spread_radius=1, blur_radius=10, color=ft.colors.BLACK12,
                offset=ft.Offset(1, 1)
            ),
            margin=ft.margin.all(5),
            # expand=True # Se manejará con ResponsiveRow
        )

    def _create_chart_placeholder(self, title_text):
        return ft.Container(
            content=ft.Column([
                ft.Text(title_text, size=18, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                # Aquí iría el control del gráfico real más adelante
                ft.Container(ft.ProgressRing(), alignment=ft.alignment.center, expand=True) # Placeholder visual para el gráfico
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, spacing=10),
            padding=20,
            border_radius=12,
            border=ft.border.all(1, ft.colors.GREY_300),
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(1,1)),
            margin=ft.margin.symmetric(vertical=10),
            height=350 # Altura fija para los placeholders de gráficos
        )

    def build(self):
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
                        # Alinear el botón al final de la columna (verticalmente) y al final (derecha) horizontalmente
                        # O podrías usar ft.MainAxisAlignment.CENTER y ft.CrossAxisAlignment.CENTER si se prefiere centrado
                        alignment=ft.MainAxisAlignment.CENTER, # Centra el botón verticalmente en el espacio de la columna
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH # Hace que el botón ocupe el ancho de la columna
                    )
                ], spacing=15, run_spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER) # Alinear items verticalmente al centro en la fila
            ], spacing=15),
            padding=20, margin=ft.margin.only(bottom=25, left=5, right=5),
            border_radius=12, bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.colors.BLACK12, offset=ft.Offset(1,1))
        )

        # --- Sección Panel de Estadísticas ---
        metrics_cards_section = ft.ResponsiveRow([
                ft.Column([self.total_members_card], col={"xs": 12, "sm": 6, "md": 3}),
                ft.Column([self.monthly_payments_card], col={"xs": 12, "sm": 6, "md": 3}),
                ft.Column([self.most_used_method_card], col={"xs": 12, "sm": 6, "md": 3}),
                ft.Column([self.active_members_today_card], col={"xs": 12, "sm": 6, "md": 3}),
            ], spacing=10, run_spacing=10
        )

        charts_section = ft.ResponsiveRow([
                ft.Column([self.income_bar_chart], col={"xs": 12, "md": 6}),
                ft.Column([self.payment_method_pie_chart], col={"xs": 12, "md": 6}),
                ft.Column([self.new_members_line_chart], col={"xs": 12}), # Este ocupa todo el ancho en todas las vistas
            ], spacing=10, run_spacing=10
        )

        statistics_panel = ft.Container(
            content=ft.Column([
                ft.Text("Métricas Clave", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK87),
                metrics_cards_section,
                ft.Divider(height=20, thickness=1),
                ft.Text("Análisis Gráfico", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK87),
                charts_section
            ], spacing=20),
            padding=ft.padding.all(15),
            # No necesita fondo propio si la página es blanca y las cards tienen su fondo
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
            bgcolor=ft.colors.GREY_100, # Fondo general gris claro para contraste con cards blancas
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


# Example usage (for testing this view standalone)
# if __name__ == "__main__":
#     def main(page: ft.Page):
#         page.title = "Statistics View"
#         page.vertical_alignment = ft.MainAxisAlignment.START
#         page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#         page.theme_mode = ft.ThemeMode.LIGHT
#         page.bgcolor = ft.colors.WHITE
#
#         # Dummy controller for testing
#         class DummyController:
#             def handle_report_type_change(self, e): print(f"Report type changed: {e.control.value}")
#             def handle_start_date_change(self, e): print(f"Start date changed: {e.control.value}")
#             def handle_end_date_change(self, e): print(f"End date changed: {e.control.value}")
#             def handle_membership_status_change(self, e): print(f"Membership status changed: {e.control.value}")
#             async def handle_generate_report(self, e): 
#                 print("Generate report clicked")
#                 self.page.show_snack_bar(ft.SnackBar(ft.Text("Informe generado!"), open=True))
#             def handle_card_click(self, e): print("Card clicked")
#             async def initialize_statistics(self):
#                 print("Dummy init stats")
#                 # Simulate data loading for cards
#                 if hasattr(stats_view, 'total_members_card'):
#                     stats_view.total_members_card.content.controls[1].value = "175"
#                     stats_view.monthly_payments_card.content.controls[1].value = "$130,000"
#                     stats_view.most_used_method_card.content.controls[1].value = "Método: Débito"
#                     stats_view.most_used_method_card.content.controls[3].value = "70 pagos"
#                     stats_view.active_members_today_card.content.controls[1].value = "30"
#                     stats_view.update() # Actualizar la vista después de cambiar los valores
#
#         controller = DummyController()
#         # Asignar page al dummy controller si lo necesita, como para show_snack_bar
#         controller.page = page 
#         stats_view = StatisticsView(page, controller)
#         page.add(stats_view.build()) # Llamar a build() para obtener el control
#         page.run_task(controller.initialize_statistics) # Ejecutar la inicialización
#         page.update()
#
#     ft.app(target=main) 