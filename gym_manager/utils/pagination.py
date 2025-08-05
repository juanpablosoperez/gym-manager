import flet as ft
from typing import List, Callable, Any

class PaginationController:
    """Controlador de paginación reutilizable para todas las vistas"""
    
    def __init__(self, items_per_page: int = 10):
        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_items = 0
        self.total_pages = 0
        self.all_items = []
        
    def set_items(self, items: List[Any]):
        """Establece los elementos a paginar"""
        self.all_items = items
        self.total_items = len(items)
        self.total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
        self.current_page = min(self.current_page, self.total_pages)
        
    def get_current_page_items(self) -> List[Any]:
        """Obtiene los elementos de la página actual"""
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        return self.all_items[start_index:end_index]
        
    def go_to_page(self, page: int):
        """Va a una página específica"""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            
    def next_page(self):
        """Va a la siguiente página"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            
    def previous_page(self):
        """Va a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            
    def get_page_info(self) -> dict:
        """Obtiene información de la página actual"""
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, self.total_items)
        
        return {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'total_items': self.total_items,
            'start_item': start_item,
            'end_item': end_item,
            'items_per_page': self.items_per_page
        }

class PaginationWidget:
    """Widget de paginación reutilizable"""
    
    def __init__(self, controller: PaginationController, on_page_change: Callable = None):
        self.controller = controller
        self.on_page_change = on_page_change
        
        # Controles de paginación
        self.page_info_text = ft.Text("", size=14, color=ft.colors.GREY_700)
        self.prev_button = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            icon_color=ft.colors.BLUE,
            tooltip="Página anterior",
            on_click=self._on_prev_click,
            disabled=True
        )
        self.next_button = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD,
            icon_color=ft.colors.BLUE,
            tooltip="Página siguiente",
            on_click=self._on_next_click,
            disabled=True
        )
        self.first_button = ft.IconButton(
            icon=ft.icons.FIRST_PAGE,
            icon_color=ft.colors.BLUE,
            tooltip="Primera página",
            on_click=self._on_first_click,
            disabled=True
        )
        self.last_button = ft.IconButton(
            icon=ft.icons.LAST_PAGE,
            icon_color=ft.colors.BLUE,
            tooltip="Última página",
            on_click=self._on_last_click,
            disabled=True
        )
        
        # Selector de elementos por página
        self.items_per_page_dropdown = ft.Dropdown(
            label="Elementos por página",
            width=150,
            options=[
                ft.dropdown.Option("5"),
                ft.dropdown.Option("10"),
                ft.dropdown.Option("20"),
                ft.dropdown.Option("50"),
            ],
            value="10",
            on_change=self._on_items_per_page_change
        )
        
        # Contenedor principal
        self.container = ft.Container(
            content=ft.Row(
                controls=[
                    self.first_button,
                    self.prev_button,
                    self.page_info_text,
                    self.next_button,
                    self.last_button,
                    ft.VerticalDivider(width=20),
                    self.items_per_page_dropdown,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.padding.symmetric(vertical=10),
            alignment=ft.alignment.center,
        )
        
    def _on_prev_click(self, e):
        """Maneja el clic en el botón anterior"""
        self.controller.previous_page()
        self._update_pagination()
        if self.on_page_change:
            self.on_page_change()
            
    def _on_next_click(self, e):
        """Maneja el clic en el botón siguiente"""
        self.controller.next_page()
        self._update_pagination()
        if self.on_page_change:
            self.on_page_change()
            
    def _on_first_click(self, e):
        """Maneja el clic en el botón primera página"""
        self.controller.go_to_page(1)
        self._update_pagination()
        if self.on_page_change:
            self.on_page_change()
            
    def _on_last_click(self, e):
        """Maneja el clic en el botón última página"""
        self.controller.go_to_page(self.controller.total_pages)
        self._update_pagination()
        if self.on_page_change:
            self.on_page_change()
            
    def _on_items_per_page_change(self, e):
        """Maneja el cambio en elementos por página"""
        new_items_per_page = int(self.items_per_page_dropdown.value)
        self.controller.items_per_page = new_items_per_page
        self.controller.current_page = 1
        self.controller.total_pages = max(1, (self.controller.total_items + self.controller.items_per_page - 1) // self.controller.items_per_page)
        self._update_pagination()
        if self.on_page_change:
            self.on_page_change()
    
    def _update_pagination(self):
        """Actualiza el estado de los controles de paginación"""
        info = self.controller.get_page_info()
        
        # Actualizar texto de información
        if self.controller.total_items > 0:
            self.page_info_text.value = f"Página {info['current_page']} de {info['total_pages']} ({info['start_item']}-{info['end_item']} de {info['total_items']} elementos)"
        else:
            self.page_info_text.value = "No hay elementos para mostrar"
        
        # Actualizar estado de botones
        self.prev_button.disabled = info['current_page'] <= 1
        self.next_button.disabled = info['current_page'] >= info['total_pages']
        self.first_button.disabled = info['current_page'] <= 1
        self.last_button.disabled = info['current_page'] >= info['total_pages']
        
        # Actualizar colores de botones
        self.prev_button.icon_color = ft.colors.BLUE if not self.prev_button.disabled else ft.colors.GREY_400
        self.next_button.icon_color = ft.colors.BLUE if not self.next_button.disabled else ft.colors.GREY_400
        self.first_button.icon_color = ft.colors.BLUE if not self.first_button.disabled else ft.colors.GREY_400
        self.last_button.icon_color = ft.colors.BLUE if not self.last_button.disabled else ft.colors.GREY_400
        
        self.container.update()
    
    def update_items(self, items: List[Any]):
        """Actualiza los elementos y refresca la paginación"""
        self.controller.set_items(items)
        self._update_pagination()
    
    def get_widget(self) -> ft.Container:
        """Retorna el widget de paginación"""
        return self.container 