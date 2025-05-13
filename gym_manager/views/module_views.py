import flet as ft

class ModuleView:
    def __init__(self, page: ft.Page, title: str):
        self.page = page
        self.title = title
        self.content = None
        self.setup_view()

    def setup_view(self):
        """
        Método que debe ser implementado por las clases hijas
        para configurar la vista específica
        """
        pass

    def get_content(self):
        """
        Retorna el contenido de la vista
        """
        if self.content is None:
            self.setup_view()
        return self.content

    def show_message(self, message: str, color: str = ft.colors.RED_400):
        """
        Muestra un mensaje en la interfaz
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()

class MembersView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Miembros")

class PaymentsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Pagos")
        # Importar aquí para evitar circular import
        from gym_manager.views.payment_view import PaymentsView as PaymentViewImpl
        self.payment_view = PaymentViewImpl(page)
        self.content = self.payment_view.get_content()

class ReportsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Informes y Estadísticas")

class PaymentMethodsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Métodos de Pago")

class UsersView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Usuarios")
        # Importar aquí para evitar circular import
        from gym_manager.views.user_view import UsersView as UserViewImpl
        self.user_view = UserViewImpl(page)
        self.content = self.user_view.get_content()

class BackupsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Backups") 