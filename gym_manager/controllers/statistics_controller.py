import flet as ft
from datetime import datetime, timedelta
# Importa aquí tus modelos o servicios necesarios. Ejemplo:
# from gym_manager.models.member_model import Member
# from gym_manager.models.payment_model import Payment
# from gym_manager.services.member_service import MemberService
# from gym_manager.services.payment_service import PaymentService

class StatisticsController:
    def __init__(self, view, page):
        self.view = view
        self.page = page
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
        # --- Total de Miembros ---
        # total_members = await self.member_service.get_total_members_count() # Ejemplo
        total_members = 150 # Dummy data
        self.view.total_members_card.content.controls[1].value = str(total_members)

        # --- Pagos del Mes ---
        # current_month_payments = await self.payment_service.get_current_month_payments_sum() # Ejemplo
        current_month_payments = 125000.00 # Dummy data
        self.view.monthly_payments_card.content.controls[1].value = f"${current_month_payments:,.2f}"

        # --- Método de Pago Más Usado ---
        # most_used_method_data = await self.payment_service.get_most_used_payment_method_info() # Ejemplo
        # (method_name, count)
        most_used_method_data = ("Efectivo", 64) # Dummy data
        self.view.most_used_method_card.content.controls[1].value = f"Método más usado: {most_used_method_data[0]}"
        self.view.most_used_method_card.content.controls[2].value = f"{most_used_method_data[1]} pagos"
        
        # --- Miembros Activos Hoy ---
        # active_today = await self.member_service.get_active_members_today_count() # Ejemplo
        active_today = 25 # Dummy data
        self.view.active_members_today_card.content.controls[1].value = str(active_today)
        
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