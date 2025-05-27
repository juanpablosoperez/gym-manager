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
        from gym_manager.views.member_view import MembersView as MembersViewImpl
        self.members_view = MembersViewImpl(page)
        self.content = self.members_view.get_content()
        self.page.update()

class RoutinesView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Rutinas")
        from gym_manager.views.routine_view import RoutinesView as RoutinesViewImpl
        self.routines_view = RoutinesViewImpl(page)
        self.content = self.routines_view.get_content()
        self.page.update()

class PaymentsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Pagos")
        from gym_manager.views.payment_view import PaymentsView as PaymentViewImpl
        self.payment_view = PaymentViewImpl(page)
        self.content = self.payment_view.get_content()
        self.page.update()

class ReportsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Informes y Estadísticas")
        from gym_manager.views.statistics_view import StatisticsView as StatisticsViewImpl
        self.statistics_view = StatisticsViewImpl(page)
        self.content = self.statistics_view.get_content()
        self.page.update()

class PaymentMethodsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Métodos de Pago")
        from gym_manager.views.payment_method_view import PaymentMethodView as PaymentMethodViewImpl
        self.payment_method_view = PaymentMethodViewImpl(page)
        self.content = self.payment_method_view.get_content()
        self.page.update()

class UsersView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Usuarios")
        from gym_manager.views.user_view import UsersView as UserViewImpl
        self.user_view = UserViewImpl(page)
        self.content = self.user_view.get_content()
        self.page.update()

class BackupsView(ModuleView):
    def __init__(self, page: ft.Page):
        super().__init__(page, "Gestión de Backups")
        from gym_manager.views.backup_view import BackupView as BackupViewImpl
        self.backup_view = BackupViewImpl(page)
        self.content = self.backup_view.get_content()
        self.page.update() 