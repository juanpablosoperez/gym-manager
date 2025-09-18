import flet as ft

from gym_manager.views.module_views import ModuleView
from gym_manager.utils.database import get_db_session
from gym_manager.models.payment_method import MetodoPago
from gym_manager.controllers.payment_method_controller import PaymentMethodController

class PaymentMethodView(ModuleView):
    def __init__(self, page: ft.Page):
        # Inicializar variables básicas
        self.page = page
        self.title = "Gestión de Métodos de Pago"
        self.content = None
        
        # Inicializar controlador
        self.payment_method_controller = PaymentMethodController(get_db_session())
        
        # Inicializar paginación ANTES de setup_payment_method_view
        from gym_manager.utils.pagination import PaginationController, PaginationWidget
        self.pagination_controller = PaginationController(items_per_page=10)
        self.pagination_widget = PaginationWidget(
            self.pagination_controller, 
            on_page_change=self._on_page_change
        )
        
        # Ahora llamar setup_payment_method_view después de inicializar todo
        self.setup_payment_method_view()
        self.setup_history_modal()
        # NO llamar load_data aquí, se llamará cuando la vista se muestre

    def setup_payment_method_view(self):
        # Título principal (alineado a MembersView)
        self.welcome_title = ft.Text(
            "¡Administra y consulta tus métodos de pago!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        # Tarjeta del método más utilizado
        self.most_used_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.icons.STAR,
                                color=ft.colors.AMBER_700,
                                size=32
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Método más Utilizado",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.AMBER_700
                                    ),
                                    ft.Text(
                                        "N/A",  # Se actualizará dinámicamente
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.AMBER_700
                                    ),
                                    ft.Text(
                                        "0 pagos",  # Se actualizará dinámicamente
                                        size=14,
                                        color=ft.colors.GREY_600
                                    )
                                ],
                                spacing=2
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10
                    )
                ],
                spacing=5,
            ),
            padding=20,
            border_radius=12,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.GREY_300,
            ),
            width=300
        )

        # Botón Agregar Método de Pago
        self.new_method_btn = ft.ElevatedButton(
            text="Agregar Método de Pago",
            icon=ft.icons.ADD,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
            on_click=self.show_new_method_modal
        )

        # Campo de búsqueda
        self.search_field = ft.TextField(
            label="Buscar método de pago",
            prefix_icon=ft.icons.SEARCH,
            border_radius=10,
            width=260,
            height=48,
            text_size=16,
            on_change=self.apply_filters
        )

        # Filtro de estado
        self.status_filter = ft.Dropdown(
            label="Estado",
            width=120,
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Activo"),
                ft.dropdown.Option("Inactivo")
            ],
            border_radius=10,
            text_size=16,
            value="Activo",
            on_change=self.apply_filters
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

        # Tabla de métodos de pago
        self.methods_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", size=18, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", size=18, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=12,
            vertical_lines=ft.border.all(1, ft.colors.GREY_300),
            horizontal_lines=ft.border.all(1, ft.colors.GREY_300),
            column_spacing=120,
            heading_row_color=ft.colors.GREY_100,
            heading_row_height=60,
            data_row_color=ft.colors.WHITE,
            data_row_min_height=56,
            expand=True,
        )

        # Modal de nuevo método de pago
        self.new_method_name_field = ft.TextField(
            label="Nombre del método",
            border_radius=8,
            width=500,
            height=48,
            text_size=16,
        )

        self.new_method_status_switch = ft.Switch(
            label="Activo",
            value=True,
            label_position=ft.LabelPosition.LEFT,
        )

        self.new_method_modal = ft.AlertDialog(
            title=ft.Text("Agregar Método de Pago", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Nombre del método", size=16, weight=ft.FontWeight.BOLD),
                    self.new_method_name_field,
                    ft.Text("Estado", size=16, weight=ft.FontWeight.BOLD),
                    self.new_method_status_switch,
                ],
                spacing=18,
                width=500,
                height=150,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.close_modal,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.ElevatedButton(
                    "Guardar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD)
                    ),
                    on_click=self.save_method
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )

        # Modal de edición
        self.edit_method_name_field = ft.TextField(
            label="Nombre del método",
            border_radius=8,
            width=500,
            height=48,
            text_size=16,
        )

        self.edit_method_status_switch = ft.Switch(
            label="Activo",
            value=True,
            label_position=ft.LabelPosition.LEFT,
        )

        self.edit_method_modal = ft.AlertDialog(
            title=ft.Text("Editar Método de Pago", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Nombre del método", size=16, weight=ft.FontWeight.BOLD),
                    self.edit_method_name_field,
                    ft.Text("Estado", size=16, weight=ft.FontWeight.BOLD),
                    self.edit_method_status_switch,
                ],
                spacing=18,
                width=540,
                height=150,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.close_edit_modal,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.ElevatedButton(
                    "Actualizar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_900,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD)
                    ),
                    on_click=self.update_method
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )

        # Modal de confirmación de eliminación
        self.delete_confirm_modal = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación", size=22, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "¿Estás seguro que deseas eliminar este método de pago?",
                size=16
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.close_delete_modal,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.ElevatedButton(
                    "Eliminar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.RED_700,
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    ),
                    on_click=self.confirm_delete_method
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )

        # Agregar modales al overlay de la página
        self.page.overlay.extend([
            self.new_method_modal,
            self.edit_method_modal,
            self.delete_confirm_modal
        ])

        # Variables de estado
        self.selected_method = None
        self.selected_method_to_delete = None

        # (sin contador en esta vista)

        # Layout principal
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    # Encabezado (título a la izquierda, alta a la derecha)
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.welcome_title,
                                ft.Row(
                                    controls=[
                                        self.new_method_btn,
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=20, top=0, left=10, right=10),
                        alignment=ft.alignment.top_left,
                        
                    ),
                    # Filtros (más compactos)
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.search_field,
                                self.status_filter,
                                self.clear_btn,
                                ft.Container(expand=True),
                                ft.Row([self.most_used_card], alignment=ft.MainAxisAlignment.END),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=ft.padding.only(bottom=10, left=10, right=10),
                        alignment=ft.alignment.top_left,
                        
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=self.methods_table,
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

    def setup_history_modal(self):
        self.history_modal = ft.AlertDialog(
            title=ft.Text("Historial de Uso del Método", size=22, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Cargando...", key="stats"),
                    ft.Text("Últimos pagos", size=16, weight=ft.FontWeight.BOLD),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Fecha")),
                            ft.DataColumn(ft.Text("Monto")),
                            ft.DataColumn(ft.Text("Miembro")),
                        ],
                        rows=[],
                        key="pagos_table"
                    )
                ],
                spacing=16,
                width=540,
            ),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=self.close_history_modal,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.WHITE,
                        color=ft.colors.BLACK87,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=28, vertical=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        self.page.overlay.append(self.history_modal)

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
            
            methods = self.payment_method_controller.get_payment_methods()
            
            # Actualizar paginación
            self.pagination_controller.set_items(methods)
            self.pagination_controller.current_page = 1
            self.pagination_widget.update_items(methods)
            
            # Actualizar tabla y estadísticas
            self.update_methods_table(methods)
            self.update_stats_cards(methods)
            
        except Exception as e:
            self.update_methods_table([])
    
    def _on_page_change(self):
        """Callback cuando cambia la página"""
        self.update_methods_table()

    def load_data(self, preserve_page=False):
        """
        Carga los datos iniciales de la vista
        """
        methods = self.payment_method_controller.get_payment_methods()
        
        # Guardar la página actual si se debe preservar
        current_page = self.pagination_controller.current_page if preserve_page else 1
        
        self.pagination_controller.set_items(methods)
        self.pagination_controller.current_page = current_page
        
        # Ajustar la página si está fuera de rango
        total_pages = self.pagination_controller.total_pages
        if current_page > total_pages and total_pages > 0:
            self.pagination_controller.current_page = total_pages
        
        self.pagination_widget.update_items(methods)
        self.update_methods_table()
        self.update_stats_cards(methods)

    def _collect_method_filters(self):
        """
        Construye el dict de filtros actuales según los controles visibles.
        """
        filters = {}
        if getattr(self, 'search_field', None) and self.search_field.value:
            filters['search'] = self.search_field.value
        if getattr(self, 'status_filter', None) and self.status_filter.value and self.status_filter.value != "Todos":
            filters['status'] = self.status_filter.value == "Activo"
        return filters

    def refresh_methods_preserving_state(self):
        """
        Recarga la grilla de métodos preservando filtros y la página actual.
        """
        try:
            current_page = self.pagination_controller.current_page
            filters = self._collect_method_filters()
            methods = self.payment_method_controller.get_payment_methods(filters)
            
            self.pagination_controller.set_items(methods)
            total_pages = self.pagination_controller.total_pages if hasattr(self.pagination_controller, 'total_pages') else self.pagination_controller.get_total_pages()
            if current_page > total_pages and total_pages > 0:
                current_page = total_pages
            if total_pages == 0:
                current_page = 1
            self.pagination_controller.current_page = current_page
            self.pagination_widget.update_items(methods)
            self.update_methods_table()
            self.update_stats_cards(methods)
            self.page.update()
        except Exception:
            # Como fallback, al menos refrescar la tabla con lo que haya
            self.update_methods_table()

    def update_methods_table(self, methods=None):
        """
        Actualiza la tabla de métodos de pago
        """
        try:
            self.methods_table.rows.clear()
            
            # Obtener métodos de la página actual
            if methods is None:
                methods = self.pagination_controller.get_current_page_items()
            
            # (contador removido en esta vista)
            
            if not methods:
                # Mostrar mensaje cuando no hay métodos (estado vacío consistente)
                self.methods_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Icon(name=ft.icons.PAYMENT, size=48, color=ft.colors.GREY_400),
                                            ft.Text(
                                                "No se encontraron métodos de pago",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.colors.GREY_700
                                            ),
                                            ft.Text(
                                                "Agrega tu primer método de pago usando el botón 'Agregar Método de Pago'",
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
                        ]
                    )
                )
            else:
                for method in methods:
                    try:
                        estado_texto = "Activo" if method['estado'] else "Inactivo"
                        color_estado = ft.colors.BLUE_900 if method['estado'] else ft.colors.GREY_600
                        bg_color = ft.colors.BLUE_100 if method['estado'] else ft.colors.GREY_100
                        
                        self.methods_table.rows.append(
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(
                                        ft.Text(method['descripcion'])
                                    ),
                                    ft.DataCell(
                                        ft.Container(
                                            content=ft.Text(
                                                estado_texto,
                                                color=color_estado
                                            ),
                                            bgcolor=bg_color,
                                            border_radius=8,
                                            padding=5,
                                        )
                                    ),
                                    ft.DataCell(
                                        ft.Row(
                                            controls=[
                                                ft.IconButton(
                                                    icon=ft.icons.HISTORY,
                                                    icon_color=ft.colors.AMBER_700,
                                                    tooltip="Ver historial de uso",
                                                    on_click=lambda e, m=method: self.show_history_modal(m)
                                                ),
                                                ft.IconButton(
                                                    icon=ft.icons.EDIT,
                                                    icon_color=ft.colors.BLUE,
                                                    tooltip="Editar",
                                                    on_click=lambda e, m=method: self.edit_method(m)
                                                ),
                                                ft.IconButton(
                                                    icon=ft.icons.TOGGLE_ON if method['estado'] else ft.icons.TOGGLE_OFF,
                                                    icon_color=ft.colors.GREEN if method['estado'] else ft.colors.GREY_600,
                                                    tooltip="Activar" if not method['estado'] else "Desactivar",
                                                    on_click=lambda e, m=method: self.toggle_method_status(m)
                                                ),
                                                ft.IconButton(
                                                    icon=ft.icons.DELETE,
                                                    icon_color=ft.colors.RED,
                                                    tooltip="Eliminar",
                                                    on_click=lambda e, m=method: self.delete_method(m)
                                                ),
                                            ],
                                            spacing=0,
                                        )
                                    ),
                                ]
                            )
                        )
                    except Exception as e:
                        continue
        except Exception as e:
            self.show_message("Error al cargar los métodos de pago", ft.colors.RED)
        finally:
            # Forzar refresco de la tabla sin depender del update global
            try:
                self.methods_table.update()
            except Exception:
                pass
            self.page.update()

    def update_stats_cards(self, methods):
        """
        Actualiza la tarjeta del método más utilizado
        """
        try:
            # Encontrar el método más utilizado
            most_used_method = None
            max_payments = 0
            for method in methods:
                payment_count = len(method['pagos'])
                if payment_count > max_payments:
                    max_payments = payment_count
                    most_used_method = method

            # Actualizar tarjeta del método más utilizado
            if most_used_method:
                self.most_used_card.content.controls[0].controls[1].controls[1].value = most_used_method['descripcion']
                self.most_used_card.content.controls[0].controls[1].controls[2].value = f"{max_payments} pagos"
            else:
                self.most_used_card.content.controls[0].controls[1].controls[1].value = "N/A"
                self.most_used_card.content.controls[0].controls[1].controls[2].value = "0 pagos"

            self.page.update()
        except Exception as e:
            self.show_message("Error al actualizar estadísticas", ft.colors.RED)

    def show_new_method_modal(self, e):
        """
        Muestra el modal para agregar un nuevo método de pago
        """
        self.new_method_name_field.value = ""
        self.new_method_status_switch.value = True
        self.new_method_modal.open = True
        self.page.update()

    def close_modal(self, e):
        """
        Cierra el modal de nuevo método
        """
        self.new_method_modal.open = False
        self.page.update()

    def save_method(self, e):
        """
        Guarda un nuevo método de pago
        """
        if not self.new_method_name_field.value:
            self.show_message("Debe ingresar un nombre para el método de pago", ft.colors.RED)
            return

        method_data = {
            'descripcion': self.new_method_name_field.value,
            'estado': self.new_method_status_switch.value
        }

        success, message = self.payment_method_controller.create_payment_method(method_data)
        if success:
            self.show_message(message, ft.colors.GREEN)
            self.close_modal(e)
            self.refresh_methods_preserving_state()
        else:
            self.show_message(message, ft.colors.RED)

    def edit_method(self, method):
        """
        Abre el modal para editar un método de pago
        """
        self.selected_method = method
        self.edit_method_name_field.value = method['descripcion']
        self.edit_method_status_switch.value = method['estado']
        self.edit_method_modal.open = True
        self.page.update()

    def close_edit_modal(self, e):
        """
        Cierra el modal de edición
        """
        self.edit_method_modal.open = False
        self.selected_method = None
        self.page.update()

    def update_method(self, e):
        """
        Actualiza un método de pago existente
        """
        if not self.selected_method:
            self.show_message("No hay método seleccionado para editar", ft.colors.RED)
            return

        if not self.edit_method_name_field.value:
            self.show_message("Debe ingresar un nombre para el método de pago", ft.colors.RED)
            return

        method_data = {
            'descripcion': self.edit_method_name_field.value,
            'estado': self.edit_method_status_switch.value
        }

        success, message = self.payment_method_controller.update_payment_method(
            self.selected_method['id_metodo_pago'],
            method_data
        )

        if success:
            self.show_message(message, ft.colors.GREEN)
            self.close_edit_modal(e)
            self.refresh_methods_preserving_state()
        else:
            self.show_message(message, ft.colors.RED)

    def delete_method(self, method):
        """
        Abre el modal de confirmación para eliminar un método
        """
        self.selected_method_to_delete = method
        self.delete_confirm_modal.open = True
        self.page.update()

    def close_delete_modal(self, e):
        """
        Cierra el modal de confirmación de eliminación
        """
        self.delete_confirm_modal.open = False
        self.selected_method_to_delete = None
        self.page.update()

    def confirm_delete_method(self, e):
        """
        Confirma la eliminación de un método de pago
        """
        if not self.selected_method_to_delete:
            self.show_message("No hay método seleccionado para eliminar", ft.colors.RED)
            return

        success, message = self.payment_method_controller.delete_payment_method(
            self.selected_method_to_delete['id_metodo_pago']
        )

        if success:
            self.show_message(message, ft.colors.GREEN)
            self.close_delete_modal(e)
            self.refresh_methods_preserving_state()
        else:
            self.show_message(message, ft.colors.RED)

    def apply_filters(self, e):
        """
        Aplica los filtros de búsqueda
        """
        try:
            filters = {}
            
            if self.search_field.value:
                filters['search'] = self.search_field.value
            
            if self.status_filter.value and self.status_filter.value != "Todos":
                filters['status'] = self.status_filter.value == "Activo"
            
            methods = self.payment_method_controller.get_payment_methods(filters)
            
            # Actualizar paginación con los datos filtrados
            self.pagination_controller.set_items(methods)
            # Solo resetear a página 1 si hay cambios significativos en los filtros
            # Para cambios menores, mantener la página actual si es posible
            total_pages = self.pagination_controller.total_pages
            if self.pagination_controller.current_page > total_pages and total_pages > 0:
                self.pagination_controller.current_page = total_pages
            elif total_pages == 0:
                self.pagination_controller.current_page = 1
            # Si la página actual es válida, mantenerla
            
            self.pagination_widget.update_items(methods)
            self.update_methods_table()
            self.update_stats_cards(methods)
        except Exception as e:
            self.show_message(f"Error al aplicar filtros: {str(e)}", ft.colors.RED)
            self.update_methods_table([])

    def clear_filters(self, e):
        """
        Limpia los filtros de búsqueda
        """
        self.search_field.value = ""
        self.status_filter.value = "Activo"
        # Recargar datos sin filtros usando el método asíncrono
        self.page.loop.create_task(self._load_data_async())

    def show_message(self, message: str, color: str):
        """
        Muestra un mensaje toast
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=color),
            bgcolor=ft.colors.WHITE,
            duration=3000,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def toggle_method_status(self, method):
        """
        Cambia el estado de un método de pago (activo/inactivo)
        """
        method_data = {
            'estado': not method['estado']
        }

        success, message = self.payment_method_controller.update_payment_method(
            method['id_metodo_pago'],
            method_data
        )

        if success:
            self.show_message(
                f"Método de pago {'activado' if method_data['estado'] else 'desactivado'} exitosamente",
                ft.colors.GREEN
            )
            self.refresh_methods_preserving_state()
        else:
            self.show_message(message, ft.colors.RED)

    def show_history_modal(self, method):
        try:
            # Obtener todos los métodos para calcular el total de pagos
            all_methods = self.payment_method_controller.get_payment_methods()
            total_pagos = sum(len(m['pagos']) for m in all_methods)
            pagos = method['pagos'][-5:] if len(method['pagos']) > 0 else []
            total_acumulado = sum(p['monto'] for p in method['pagos'])
            porcentaje = (len(method['pagos']) / total_pagos * 100) if total_pagos > 0 else 0

            # Actualizar contenido del modal
            stats_text = f"Total acumulado: ${total_acumulado:,.2f} | Cantidad de pagos: {len(method['pagos'])} | % del total: {porcentaje:.1f}%"
            
            pagos_rows = []
            for pago in pagos:
                miembro_nombre = f"{pago['miembro']['nombre']} {pago['miembro']['apellido']}" if pago['miembro'] else "N/A"
                pagos_rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(pago['fecha_pago'].strftime("%d/%m/%Y"))),
                        ft.DataCell(ft.Text(f"${pago['monto']:,.2f}")),
                        ft.DataCell(ft.Text(miembro_nombre)),
                    ])
                )

            # Buscar los controles por key
            for c in self.history_modal.content.controls:
                if hasattr(c, 'key') and c.key == "stats":
                    c.value = stats_text
                if hasattr(c, 'key') and c.key == "pagos_table":
                    c.rows = pagos_rows

            self.history_modal.open = True
            self.page.update()
        except Exception as e:
            self.show_message("Error al cargar el historial de pagos", ft.colors.RED)

    def close_history_modal(self, e):
        self.history_modal.open = False
        self.page.update() 