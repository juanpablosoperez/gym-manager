import flet as ft
from gym_manager.views.module_views import ModuleView
from gym_manager.utils.database import get_db_session
from gym_manager.models.routine import Rutina
from gym_manager.controllers.routine_controller import RoutineController

class RoutinesView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Rutinas")
        # Inicializar referencias
        self.new_routine_name = ft.Ref[ft.TextField]()
        self.new_routine_type = ft.Ref[ft.Dropdown]()
        self.new_routine_difficulty = ft.Ref[ft.Dropdown]()
        self.new_routine_duration = ft.Ref[ft.TextField]()
        self.new_routine_description = ft.Ref[ft.TextField]()
        
        # Inicializar controlador
        self.routine_controller = RoutineController()
        
        # FilePicker para el documento de la rutina
        self.routine_file_picker = ft.FilePicker(
            on_result=self.on_routine_file_selected
        )
        self.page.overlay.append(self.routine_file_picker)
        
        self.setup_confirm_dialog()
        self.setup_view()

    def on_routine_file_selected(self, e):
        if e.files:
            self.selected_file = e.files[0]
            self.file_selected_label.value = f"Archivo seleccionado: {self.selected_file.name}"
            self.page.update()

    def setup_view(self):
        # Título principal
        self.welcome_title = ft.Text(
            "¡Administra las rutinas de entrenamiento!",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK,
            text_align=ft.TextAlign.LEFT,
        )

        # Botón Nueva Rutina
        self.new_routine_btn = ft.ElevatedButton(
            text="Nueva Rutina",
            icon=ft.icons.ADD,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
            width=150,
            on_click=self.show_new_routine_modal
        )

        # Filtros
        self.search_field = ft.TextField(
            label="Buscar rutina",
            prefix_icon=ft.icons.SEARCH,
            border_radius=10,
            width=320,
            height=48,
            text_size=16,
            on_change=self.apply_filters
        )

        self.difficulty_filter = ft.Dropdown(
            label="Dificultad",
            width=150,
            options=[
                ft.dropdown.Option("Todas"),
                ft.dropdown.Option("Principiante"),
                ft.dropdown.Option("Intermedio"),
                ft.dropdown.Option("Avanzado")
            ],
            border_radius=10,
            text_size=16,
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
            ),
            on_click=self.clear_filters
        )

        # Tabla de rutinas
        self.routines_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Dificultad")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Miembros Asignados")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )

        # Contenedor principal
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    # Encabezado
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.welcome_title,
                                ft.Container(expand=True),
                                self.new_routine_btn,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=20),
                    ),
                    # Filtros
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.search_field,
                                self.difficulty_filter,
                                self.clear_btn,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=10,
                        ),
                        padding=ft.padding.only(bottom=20),
                    ),
                    # Tabla
                    ft.Container(
                        content=self.routines_table,
                        padding=ft.padding.only(top=10),
                    ),
                ],
                scroll=ft.ScrollMode.ALWAYS,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
            bgcolor=ft.colors.WHITE,
            border_radius=18,
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
            alignment=ft.alignment.top_left,
        )
        
        # Cargar datos iniciales
        self.load_data()

    def setup_confirm_dialog(self):
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Estás seguro de que deseas eliminar esta rutina?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_confirm_dialog),
                ft.TextButton("Eliminar", on_click=self.confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if self.confirm_dialog not in self.page.overlay:
            self.page.overlay.append(self.confirm_dialog)

    def close_confirm_dialog(self, e=None):
        self.confirm_dialog.open = False
        self.page.update()

    def confirm_delete(self, e):
        if hasattr(self, 'routine_to_delete'):
            success, message = self.routine_controller.delete_routine(self.routine_to_delete.id_rutina)
            if success:
                self.show_message("Rutina eliminada exitosamente", ft.colors.GREEN)
                self.load_data()
            else:
                self.show_message(f"Error al eliminar la rutina: {message}", ft.colors.RED)
        self.close_confirm_dialog()

    def load_data(self):
        """
        Carga los datos iniciales de la vista y actualiza la UI
        """
        print("[DEBUG - Rutinas] Iniciando load_data")
        try:
            print("[DEBUG - Rutinas] Llamando a routine_controller.get_routines()")
            rutinas = self.routine_controller.get_routines()
            print(f"[DEBUG - Rutinas] routine_controller.get_routines() devolvió {len(rutinas)} rutinas")
            
            if not rutinas:
                print("[DEBUG - Rutinas] No se encontraron rutinas")
                self.show_message("No hay rutinas registradas", ft.colors.ORANGE)
            
            print("[DEBUG - Rutinas] Llamando a update_routines_table")
            self.update_routines_table(rutinas)
            print("[DEBUG - Rutinas] Llamando a page.update()")
            self.page.update()
            print("[DEBUG - Rutinas] load_data finalizado")
            
        except Exception as ex:
            print(f"[DEBUG - Rutinas] Excepción en load_data: {str(ex)}")
            self.show_message(f"Error al cargar las rutinas: {str(ex)}", ft.colors.RED)

    def update_routines_table(self, rutinas):
        """
        Actualiza la tabla con las rutinas
        """
        print(f"[DEBUG - Rutinas] Actualizando tabla con {len(rutinas)} rutinas")
        self.routines_table.rows.clear()
        
        if not rutinas:
            print("[DEBUG - Rutinas] No hay rutinas para mostrar")
            self.routines_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No hay rutinas registradas", italic=True)),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ]
                )
            )
            self.page.update()
            return

        for rutina in rutinas:
            print(f"[DEBUG - Rutinas] Procesando rutina: {rutina.nombre}")
            
            self.routines_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(rutina.nombre)),
                        ft.DataCell(ft.Text(rutina.nivel_dificultad)),
                        ft.DataCell(ft.Text(rutina.descripcion or "-")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    "0",
                                    color=ft.colors.WHITE
                                ),
                                bgcolor=ft.colors.GREY,
                                border_radius=8,
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_color=ft.colors.BLUE,
                                    tooltip="Editar",
                                    on_click=lambda e, r=rutina: self.edit_routine(r)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    icon_color=ft.colors.RED,
                                    tooltip="Eliminar",
                                    on_click=lambda e, r=rutina: self.delete_routine(r)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    icon_color=ft.colors.GREEN,
                                    tooltip="Ver detalles",
                                    on_click=lambda e, r=rutina: self.view_routine_details(r)
                                ),
                            ])
                        ),
                    ]
                )
            )
        print("[DEBUG - Rutinas] Tabla actualizada exitosamente")
        self.page.update()

    def show_new_routine_modal(self, e):
        self.file_selected_label = ft.Text("")
        self.selected_file = None
        self.new_routine_modal = ft.AlertDialog(
            title=ft.Text("Nueva Rutina", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.TextField(
                            label="Nombre",
                            width=480,
                            border_radius=8,
                            text_size=16,
                            ref=self.new_routine_name
                        ),
                        ft.Container(height=8),
                        ft.Dropdown(
                            label="Dificultad",
                            width=480,
                            options=[
                                ft.dropdown.Option("Principiante"),
                                ft.dropdown.Option("Intermedio"),
                                ft.dropdown.Option("Avanzado")
                            ],
                            border_radius=8,
                            text_size=16,
                            ref=self.new_routine_difficulty
                        ),
                        ft.Container(height=8),
                        ft.TextField(
                            label="Descripción",
                            width=480,
                            border_radius=8,
                            text_size=16,
                            ref=self.new_routine_description,
                            multiline=True,
                            min_lines=3,
                            max_lines=5
                        ),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Seleccionar Documento de Rutina",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: self.routine_file_picker.pick_files(
                                allow_multiple=False,
                                allowed_extensions=['pdf', 'xlsx', 'xls', 'jpg', 'jpeg', 'png']
                            )
                        ),
                        self.file_selected_label,
                    ],
                    spacing=0,
                ),
                width=540,
                padding=20,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_modal),
                ft.ElevatedButton(
                    "Guardar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                    ),
                    on_click=self.save_routine,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if self.new_routine_modal not in self.page.overlay:
            self.page.overlay.append(self.new_routine_modal)
        self.new_routine_modal.open = True
        self.page.update()

    def close_modal(self, e):
        """
        Cierra el modal de rutina y limpia los campos
        """
        self.new_routine_modal.open = False
        # Limpiar campos
        self.new_routine_name.current.value = ""
        self.new_routine_difficulty.current.value = None
        self.new_routine_description.current.value = ""
        self.selected_file = None
        self.file_selected_label.value = ""
        self.page.update()

    def save_routine(self, e):
        print("[DEBUG] save_routine llamado")
        try:
            if not self.new_routine_name.current.value:
                print("[DEBUG] Falta nombre")
                self.show_message("El nombre es requerido", ft.colors.RED)
                return
            if not self.new_routine_difficulty.current.value:
                print("[DEBUG] Falta dificultad")
                self.show_message("La dificultad es requerida", ft.colors.RED)
                return
            if not hasattr(self, 'selected_file'):
                print("[DEBUG] Falta archivo")
                self.show_message("Por favor, seleccione un archivo de rutina", ft.colors.RED)
                return
            print("[DEBUG] Todos los campos requeridos presentes")
            with open(self.selected_file.path, 'rb') as file:
                file_content = file.read()
            import datetime
            now = datetime.datetime.now()
            routine_data = {
                'nombre': self.new_routine_name.current.value,
                'nivel_dificultad': self.new_routine_difficulty.current.value,
                'descripcion': self.new_routine_description.current.value,
                'documento_rutina': file_content,
                'fecha_creacion': now,
                'fecha_horario': now,
            }
            print(f"[DEBUG] routine_data a guardar: {routine_data}")
            success, message = self.routine_controller.create_routine(routine_data)
            print(f"[DEBUG] Resultado create_routine: success={success}, message={message}")
            if success:
                self.close_modal(e)
                self.load_data()
                self.show_message("Rutina creada exitosamente", ft.colors.GREEN)
            else:
                self.show_message(f"Error al crear la rutina: {message}", ft.colors.RED)
        except Exception as e:
            print(f"[DEBUG] Excepción inesperada en save_routine: {str(e)}")
            self.show_message(f"Error inesperado: {str(e)}", ft.colors.RED)

    def edit_routine(self, rutina):
        self.editing_routine = rutina
        self.file_selected_label = ft.Text("")
        self.selected_file = None
        self.new_routine_modal = ft.AlertDialog(
            title=ft.Text("Editar Rutina", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.TextField(
                            label="Nombre",
                            width=480,
                            border_radius=8,
                            text_size=16,
                            ref=self.new_routine_name,
                            value=rutina.nombre
                        ),
                        ft.Container(height=8),
                        ft.Dropdown(
                            label="Dificultad",
                            width=480,
                            options=[
                                ft.dropdown.Option("Principiante"),
                                ft.dropdown.Option("Intermedio"),
                                ft.dropdown.Option("Avanzado")
                            ],
                            border_radius=8,
                            text_size=16,
                            ref=self.new_routine_difficulty,
                            value=rutina.nivel_dificultad
                        ),
                        ft.Container(height=8),
                        ft.TextField(
                            label="Descripción",
                            width=480,
                            border_radius=8,
                            text_size=16,
                            ref=self.new_routine_description,
                            multiline=True,
                            min_lines=3,
                            max_lines=5,
                            value=rutina.descripcion
                        ),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Seleccionar Nuevo Documento",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: self.routine_file_picker.pick_files(
                                allow_multiple=False,
                                allowed_extensions=['pdf', 'xlsx', 'xls', 'jpg', 'jpeg', 'png']
                            )
                        ),
                        self.file_selected_label,
                    ],
                    spacing=0,
                ),
                width=540,
                padding=20,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_modal),
                ft.ElevatedButton(
                    "Actualizar",
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE,
                    ),
                    on_click=self.update_routine,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if self.new_routine_modal not in self.page.overlay:
            self.page.overlay.append(self.new_routine_modal)
        self.new_routine_modal.open = True
        self.page.update()

    def update_routine(self, e):
        try:
            if not self.new_routine_name.current.value:
                self.show_message("El nombre es requerido", ft.colors.RED)
                return
            if not self.new_routine_difficulty.current.value:
                self.show_message("La dificultad es requerida", ft.colors.RED)
                return
            routine_data = {
                'nombre': self.new_routine_name.current.value,
                'nivel_dificultad': self.new_routine_difficulty.current.value,
                'descripcion': self.new_routine_description.current.value,
            }
            if hasattr(self, 'selected_file') and self.selected_file:
                with open(self.selected_file.path, 'rb') as file:
                    routine_data['documento_rutina'] = file.read()
            success, message = self.routine_controller.update_routine(self.editing_routine.id_rutina, routine_data)
            if success:
                self.close_modal(e)
                self.load_data()
                self.show_message("Rutina actualizada exitosamente", ft.colors.GREEN)
            else:
                self.show_message(f"Error al actualizar la rutina: {message}", ft.colors.RED)
        except Exception as e:
            self.show_message(f"Error inesperado: {str(e)}", ft.colors.RED)

    def delete_routine(self, rutina):
        self.routine_to_delete = rutina
        self.confirm_dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def view_routine_details(self, rutina):
        controls = [
            ft.Text("Información General", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Nombre:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(rutina.nombre, size=14),
                    ]),
                    ft.Row([
                        ft.Text("Dificultad:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(rutina.nivel_dificultad, size=14),
                    ]),
                    ft.Row([
                        ft.Text("Descripción:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(rutina.descripcion or "-", size=14),
                    ]),
                    ft.Row([
                        ft.Text("Fecha de Creación:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(rutina.fecha_creacion.strftime("%d/%m/%Y %H:%M") if rutina.fecha_creacion else "-", size=14),
                    ]),
                ], spacing=10),
                padding=10,
            ),
            ft.Divider(),
        ]
        # Previsualización o descarga de archivo
        if hasattr(rutina, 'documento_rutina') and rutina.documento_rutina:
            controls.append(ft.Text("Documento de Rutina", size=16, weight=ft.FontWeight.BOLD))
            controls.append(
                ft.ElevatedButton(
                    "Previsualizar/Descargar Archivo",
                    icon=ft.icons.PICTURE_AS_PDF,
                    on_click=lambda e, r=rutina: self._preview_routine_file(r)
                )
            )
        details_modal = ft.AlertDialog(
            title=ft.Text(f"Detalles de la Rutina", size=26, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(controls=controls, spacing=0),
                width=600,
                padding=20,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog(details_modal)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if details_modal not in self.page.overlay:
            self.page.overlay.append(details_modal)
        details_modal.open = True
        self.page.update()

    def _preview_routine_file(self, rutina):
        import tempfile, os, webbrowser
        # Intentar determinar extensión (por ahora PDF por defecto)
        ext = '.pdf'
        # Si quieres mejorar esto, puedes guardar el nombre original del archivo y extraer la extensión
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(rutina.documento_rutina)
            tmp_file.flush()
            webbrowser.open(tmp_file.name)

    def apply_filters(self, e):
        """
        Aplica los filtros seleccionados
        """
        try:
            filters = {}
            
            if self.search_field.value:
                filters['search'] = self.search_field.value
            
            if self.difficulty_filter.value and self.difficulty_filter.value != "Todas":
                filters['nivel_dificultad'] = self.difficulty_filter.value
            
            print(f"[DEBUG] Aplicando filtros: {filters}")  # Debug log
            rutinas = self.routine_controller.get_routines(filters)
            print(f"[DEBUG] Rutinas encontradas: {len(rutinas)}")  # Debug log
            self.update_routines_table(rutinas)
        except Exception as ex:
            print(f"[DEBUG] Error al aplicar filtros: {str(ex)}")  # Debug log
            self.show_message(f"Error al aplicar filtros: {str(ex)}", ft.colors.RED)

    def clear_filters(self, e):
        self.search_field.value = ""
        self.difficulty_filter.value = "Todas"
        self.page.update()
        self.load_data() 