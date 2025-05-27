import flet as ft

class BaseView:
    def __init__(self, page: ft.Page):
        self.page = page

    def show_message(self, content: str, bgcolor: str = ft.colors.BLUE):
        """Muestra un mensaje en la interfaz"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(content),
            bgcolor=bgcolor,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def get_content(self):
        """Método que debe ser implementado por las clases hijas"""
        raise NotImplementedError("Las clases hijas deben implementar get_content()") 