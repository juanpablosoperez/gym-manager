import flet as ft
from datetime import datetime, timedelta
from gym_manager.controllers.member_controller import MemberController
from gym_manager.controllers.payment_controller import PaymentController
from gym_manager.utils.navigation import db_session  # Importar la sesión global
# Importa aquí tus modelos o servicios necesarios. Ejemplo:
# from gym_manager.models.member_model import Member
# from gym_manager.models.payment_model import Payment
# from gym_manager.services.member_service import MemberService
# from gym_manager.services.payment_service import PaymentService

class StatisticsController:
    def __init__(self, view, page):
        self.view = view
        self.page = page
        self.current_year = datetime.now().year
        self.member_controller = MemberController(db_session)  # Usar la sesión global
        self.payment_controller = PaymentController(db_session)
        # self.member_service = MemberService() # Ejemplo
        # self.payment_service = PaymentService() # Ejemplo
        # NO llamar a _initialize_event_handlers() aquí

    def _initialize_event_handlers(self):
        """Conecta los manejadores de eventos a los controles de la vista."""
        if self.view is None:
            print("Error: La vista no está asignada al controlador al inicializar eventos.")
            return
            
        self.view.generate_report_button.on_click = self.handle_generate_report
        self.view.report_type_dropdown.on_change = self.handle_report_filter_change
        self.view.membership_status_dropdown.on_change = self.handle_report_filter_change
        
        # Conectar clics de tarjetas si se necesita alguna acción
        # self.view.total_members_card.on_click = lambda e: self.handle_card_click("total_members")
        # self.view.monthly_payments_card.on_click = lambda e: self.handle_card_click("monthly_payments")
        # self.view.most_used_method_card.on_click = lambda e: self.handle_card_click("most_used_method")
        # self.view.active_members_today_card.on_click = lambda e: self.handle_card_click("active_members_today")

    async def initialize_statistics(self):
        """Carga los datos iniciales para el panel de estadísticas."""
        print("Initializing statistics...")
        if self.view is None:
            print("Error: La vista no está asignada al cargar estadísticas.")
            return
        await self.load_summary_cards_data()
        await self.load_charts_data()
        self.page.update() # Cambiar self.view.update() a self.page.update()

    async def load_summary_cards_data(self):
        """Carga los datos para las tarjetas de resumen."""
        try:
            # Obtener el conteo de miembros activos
            active_members_count = self.member_controller.get_active_members_count()
            self.view.active_members_today_card.content.controls[1].controls[0].value = str(active_members_count)

            # Obtener la suma de pagos del mes actual
            current_month_payments = self.payment_controller.get_current_month_payments_sum()
            self.view.monthly_payments_card.content.controls[1].controls[0].value = f"${current_month_payments:,.2f}"

            # Obtener el conteo de membresías vencidas
            expired_memberships_count = self.member_controller.get_expired_memberships_count()
            self.view.expired_memberships_card.content.controls[1].controls[0].value = str(expired_memberships_count)

            # Obtener la suma de pagos del año actual
            annual_income = self.payment_controller.get_current_year_payments_sum()
            self.view.total_annual_income_card.content.controls[1].controls[0].value = f"${annual_income:,.2f}"
            # Actualizar el texto del año en la descripción
            self.view.total_annual_income_card.content.controls[1].controls[1].value = f"Ingresos {self.current_year}"
        except Exception as e:
            print(f"Error al cargar datos de resumen: {str(e)}")
            # En caso de error, mostrar valores por defecto
            self.view.active_members_today_card.content.controls[1].controls[0].value = "0"
            self.view.monthly_payments_card.content.controls[1].controls[0].value = "$0.00"
            self.view.expired_memberships_card.content.controls[1].controls[0].value = "0"
            self.view.total_annual_income_card.content.controls[1].controls[0].value = "$0.00"

    async def load_charts_data(self):
        """Carga y configura los datos para los gráficos."""
        print("Chart data loading (placeholder)...")

    async def handle_generate_report(self, e):
        """Maneja el evento de clic en el botón 'Generar Informe'."""
        report_type = self.view.report_type_dropdown.value
        start_date = self.view.start_date_picker.value
        end_date = self.view.end_date_picker.value
        membership_status = self.view.membership_status_dropdown.value

        print(f"Generando informe: {report_type}")
        print(f"Desde: {start_date}, Hasta: {end_date}, Estado: {membership_status}")
        
        self.page.show_snack_bar(
            ft.SnackBar(
                ft.Text(f"Informe '{report_type}' generado con éxito (simulado)."),
                open=True,
            )
        )

    async def handle_report_filter_change(self, e):
        print(f"Filtro de informe cambiado: {e.control.label} = {e.control.value}")
        
    async def handle_card_click(self, card_name: str):
        print(f"Tarjeta '{card_name}' clickeada.")

# No __main__ aquí. 