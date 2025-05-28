import flet as ft
from gym_manager.components.header import create_header
from gym_manager.components.sidebar import create_sidebar
from gym_manager.utils.navigation import navigate_to_login
from gym_manager.utils.database import get_db_session
from gym_manager.views.module_views import (
    MembersView, PaymentsView, ReportsView,
    PaymentMethodsView, UsersView, BackupsView, RoutinesView
)
from gym_manager.views.statistics_view import StatisticsView
from gym_manager.controllers.statistics_controller import StatisticsController
from gym_manager.controllers.payment_controller import PaymentController
from gym_manager.controllers.member_controller import MemberController
from datetime import datetime, timedelta

class HomeView:
    def __init__(self, page: ft.Page, user_rol: str, user_name: str = "Usuario"):
        self.page = page
        self.user_rol = user_rol
        self.user_name = user_name
        # Inicializar controladores con nuevas sesiones
        self.db_session = get_db_session()
        self.payment_controller = PaymentController(self.db_session)
        self.member_controller = MemberController(self.db_session)
        # Inicializar el snackbar
        self.snack = ft.SnackBar(content=ft.Text(""))
        self.page.overlay.append(self.snack)
        self.setup_page()

    def __del__(self):
        """Cleanup cuando se destruye la instancia"""
        if hasattr(self, 'db_session'):
            self.db_session.close()

    def setup_page(self):
        self.page.title = "Gym Manager - Home"
        self.page.padding = 0
        self.page.bgcolor = ft.colors.GREY_50
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_resizable = True

        # Título de sección por defecto
        self.section_title = "Dashboard"

        # Crear header
        self.header = create_header(
            page=self.page,
            user_name=self.user_name,
            user_role=self.user_rol,
            on_logout=self.logout,
            section_title=self.section_title
        )

        # Crear sidebar
        self.sidebar = create_sidebar(
            page=self.page,
            on_item_selected=self.handle_route_change
        )

        # Contenedor principal para el contenido
        self.main_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"¡Bienvenido, {self.user_name}! 👋", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Selecciona una opción del menú para comenzar.", size=16, color=ft.colors.GREY_700),
                    ft.Container(height=20),
                    self.create_stats_row(),
                    ft.Container(height=30),  # Espacio entre las cards y las tablas
                    ft.Row(
                        controls=[
                            self.create_recent_members_table(),
                            ft.Container(width=20),  # Espacio entre tablas
                            self.create_recent_payments_table(),
                        ],
                        expand=True,
                    ),
                ],
                scroll=ft.ScrollMode.ADAPTIVE,  # Agregar scroll adaptativo
                spacing=0,  # Controlar espaciado con márgenes de los hijos
            ),
            expand=True,
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            margin=ft.margin.all(20),
        )

        # Construir la interfaz
        self.page.add(
            ft.Column(
                controls=[
                    self.header,
                    ft.Row(
                        controls=[
                            self.sidebar,
                            ft.VerticalDivider(width=1),
                            self.main_content,
                        ],
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            )
        )
        self.page.update()

    def create_stats_row(self):
        # Obtener datos reales de pagos de hoy
        hoy = datetime.now()
        inicio_dia = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = hoy.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        pagos_hoy = self.payment_controller.get_payments({
            'date_from': inicio_dia,
            'date_to': fin_dia
        })
        # Filtrar solo pagos activos y sumar sus montos
        total_pagos_hoy = sum(
            pago.monto for pago in pagos_hoy 
            if pago.estado == True  # Solo pagos activos
        )

        # Obtener nuevos miembros del mes actual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        fin_mes = (inicio_mes.replace(month=inicio_mes.month + 1) if inicio_mes.month < 12 
                  else inicio_mes.replace(year=inicio_mes.year + 1, month=1)) - timedelta(days=1)
        nuevos_miembros = self.member_controller.get_members({
            'fecha_registro_desde': inicio_mes,
            'fecha_registro_hasta': fin_mes
        })
        total_nuevos = len(nuevos_miembros)

        # Obtener membresías que vencen esta semana
        inicio_semana = datetime.now().replace(hour=0, minute=0, second=0)
        fin_semana = inicio_semana + timedelta(days=7)
        vencimientos = self.member_controller.get_expired_memberships_count()

        # Obtener ingresos totales del mes actual
        ingresos_mes = self.payment_controller.get_current_month_payments_sum()
        nombre_mes = datetime.now().strftime("%B").capitalize()

        return ft.Row(
            controls=[
                self.create_stat_card("💳 Pagos hoy", f"${total_pagos_hoy:,.2f}", ft.icons.PAYMENT, ft.colors.BLUE),
                self.create_stat_card("🧍‍♂️ Nuevos miembros este mes", str(total_nuevos), ft.icons.PEOPLE, ft.colors.GREEN),
                self.create_stat_card("📅 Vencimientos esta semana", str(vencimientos), ft.icons.CALENDAR_TODAY, ft.colors.ORANGE),
                self.create_stat_card("📈 Ingresos en " + nombre_mes, f"${ingresos_mes:,.2f}", ft.icons.TRENDING_UP, ft.colors.PURPLE),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def create_stat_card(self, title: str, value: str, icon: str, color: str):
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

    def create_recent_members_table(self):
        # Obtener los últimos 5 miembros registrados
        miembros_recientes = self.member_controller.get_members({
            'limit': 5,
            'order_by': 'fecha_registro',
            'order_direction': 'desc'
        })

        # Crear la tabla
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Miembros Recientes", size=20, weight=ft.FontWeight.BOLD),
                    ft.Column(
                        controls=[
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Fecha de Alta", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Tipo de Membresía", weight=ft.FontWeight.BOLD)),
                                ],
                                rows=[
                                    ft.DataRow(
                                        cells=[
                                            ft.DataCell(ft.Text(f"{miembro.nombre} {miembro.apellido}")),
                                            ft.DataCell(ft.Text(miembro.fecha_registro.strftime("%d/%m/%Y"))),
                                            ft.DataCell(ft.Text(miembro.tipo_membresia or "No especificado")),
                                        ]
                                    ) for miembro in miembros_recientes
                                ],
                                border=ft.border.all(1, ft.colors.GREY_300),
                                border_radius=10,
                                vertical_lines=ft.border.all(1, ft.colors.GREY_300),
                                horizontal_lines=ft.border.all(1, ft.colors.GREY_300),
                                column_spacing=50,
                                heading_row_color=ft.colors.GREY_100,
                                heading_text_style=ft.TextStyle(
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.GREY_800,
                                ),
                                data_row_color=ft.colors.WHITE,
                                data_text_style=ft.TextStyle(
                                    size=14,
                                    color=ft.colors.GREY_800,
                                ),
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        height=300,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.GREY_300,
            ),
        )

    def create_recent_payments_table(self):
        # Obtener los últimos 5 pagos
        pagos_recientes = self.payment_controller.get_payments({
            'limit': 5,
            'order_by': 'fecha_pago',
            'order_direction': 'desc'
        })

        # Crear la tabla
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Últimos Pagos", size=20, weight=ft.FontWeight.BOLD),
                    ft.Column(
                        controls=[
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Monto", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Método", weight=ft.FontWeight.BOLD)),
                                ],
                                rows=[
                                    ft.DataRow(
                                        cells=[
                                            ft.DataCell(ft.Text(f"{pago.miembro.nombre} {pago.miembro.apellido}")),
                                            ft.DataCell(ft.Text(pago.fecha_pago.strftime("%d/%m/%Y"))),
                                            ft.DataCell(ft.Text(f"${pago.monto:,.2f}")),
                                            ft.DataCell(ft.Text(pago.metodo_pago.descripcion)),
                                        ]
                                    ) for pago in pagos_recientes
                                ],
                                border=ft.border.all(1, ft.colors.GREY_300),
                                border_radius=10,
                                vertical_lines=ft.border.all(1, ft.colors.GREY_300),
                                horizontal_lines=ft.border.all(1, ft.colors.GREY_300),
                                column_spacing=50,
                                heading_row_color=ft.colors.GREY_100,
                                heading_text_style=ft.TextStyle(
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.GREY_800,
                                ),
                                data_row_color=ft.colors.WHITE,
                                data_text_style=ft.TextStyle(
                                    size=14,
                                    color=ft.colors.GREY_800,
                                ),
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        height=300,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.GREY_300,
            ),
            expand=True,  # Para que ocupe el espacio disponible
        )

    def handle_route_change(self, index: int):
        # Limpiar el contenido actual
        self.main_content.content = None
        previous_title = self.section_title # Guardar título anterior por si acaso

        # Título de sección según el índice
        if index == 0:  # Dashboard
            self.section_title = "Dashboard"
            self.main_content.content = ft.Column(
                controls=[
                    ft.Text(f"¡Bienvenido, {self.user_name}! 👋", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Selecciona una opción del menú para comenzar.", size=16, color=ft.colors.GREY_700),
                    ft.Container(height=20),
                    self.create_stats_row(),
                    ft.Container(height=30),  # Espacio entre las cards y las tablas
                    ft.Row(
                        controls=[
                            self.create_recent_members_table(),
                            ft.Container(width=20),  # Espacio entre tablas
                            self.create_recent_payments_table(),
                        ],
                        expand=True,
                    ),
                ],
                scroll=ft.ScrollMode.ADAPTIVE,  # Agregar scroll adaptativo aquí también
                spacing=0,  # Controlar espaciado con márgenes de los hijos
            )
        elif index == 1:  # Gestión de Miembros
            self.section_title = "Gestión de Miembros"
            view = MembersView(self.page)
            self.main_content.content = view.get_content()
        elif index == 2:  # Gestión de Rutinas
            self.section_title = "Gestión de Rutinas"
            view = RoutinesView(self.page)
            self.main_content.content = view.get_content()
        elif index == 3:  # Gestión de Pagos
            self.section_title = "Gestión de Pagos"
            view = PaymentsView(self.page)
            self.main_content.content = view.get_content()
        elif index == 4:  # Informes y Estadísticas
            self.section_title = "Informes y Estadísticas"
            view = ReportsView(self.page)
            self.main_content.content = view.get_content()
        elif index == 5:  # Métodos de Pago
            self.section_title = "Métodos de Pago"
            view = PaymentMethodsView(self.page)
            self.main_content.content = view.get_content()
        elif index == 6:  # Gestión de Usuarios
            self.section_title = "Gestión de Usuarios"
            view = UsersView(self.page)
            self.main_content.content = view.get_content()
        elif index == 7:  # Gestión de Backups
            self.section_title = "Gestión de Backups"
            view = BackupsView(self.page)
            self.main_content.content = view.get_content()
        
        # Actualizar el header con el nuevo título
        self.header = create_header(
            page=self.page,
            user_name=self.user_name,
            user_role=self.user_rol,
            on_logout=self.logout,
            section_title=self.section_title
        )
        
        # Reconstruir la interfaz
        self.page.controls.clear()
        self.page.add(
            ft.Column(
                controls=[
                    self.header,
                    ft.Row(
                        controls=[
                            self.sidebar,
                            ft.VerticalDivider(width=1),
                            self.main_content,
                        ],
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            )
        )
        self.page.update()

    def show_message(self, message: str, color: str):
        self.snack.bgcolor = color
        self.snack.content.value = message
        self.snack.open = True
        self.page.update()

    def logout(self, e):
        self.show_message("¡Hasta pronto! Cerrando sesión...", ft.colors.BLUE)
        # Esperar un momento para que se vea el mensaje
        self.page.update()
        # Navegar al login
        navigate_to_login(self.page) 