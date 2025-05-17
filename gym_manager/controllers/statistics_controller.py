import flet as ft
from datetime import datetime, timedelta
from gym_manager.controllers.member_controller import MemberController
from gym_manager.controllers.payment_controller import PaymentController
from gym_manager.utils.navigation import db_session  # Importar la sesión global
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
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

        if report_type == "Informe de Pagos":
            filters = {}
            if start_date:
                filters['date_from'] = start_date
            if end_date:
                filters['date_to'] = end_date
            if membership_status and membership_status != "Todos":
                filters['membership_status'] = membership_status
            payments = self.payment_controller.get_payments(filters)
            count = len(payments)
            self._show_report_confirmation_dialog(
                f"¿Deseas exportar {count} pagos a PDF? El archivo se guardará en tu carpeta de Descargas.",
                lambda _: self._export_payments_to_pdf(payments)
            )
        elif report_type == "Informe de Miembros":
            filters = {}
            if start_date:
                filters['fecha_registro_desde'] = start_date
            if end_date:
                filters['fecha_registro_hasta'] = end_date
            if membership_status and membership_status != "Todos":
                filters['status'] = True if membership_status == "Activo" else False
            miembros = self.member_controller.get_members(filters)
            count = len(miembros)
            status_text = f" ({membership_status.lower()}s)" if membership_status != "Todos" else ""
            self._show_report_confirmation_dialog(
                f"¿Deseas exportar {count} miembros{status_text} a PDF? El archivo se guardará en tu carpeta de Descargas.",
                lambda _: self._export_members_to_pdf(miembros, membership_status)
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Tipo de informe '{report_type}' aún no implementado."),
                open=True,
            )
            self.page.update()

    def _show_report_confirmation_dialog(self, message, on_confirm):
        """Muestra un diálogo de confirmación antes de exportar el informe."""
        self.report_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exportación", size=22, weight=ft.FontWeight.BOLD),
            content=ft.Text(message, size=16),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._close_report_dialog(),
                    style=ft.ButtonStyle(bgcolor=ft.colors.WHITE, color=ft.colors.BLACK87)
                ),
                ft.ElevatedButton(
                    "Exportar",
                    on_click=on_confirm,
                    style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        self.page.overlay.append(self.report_dialog)
        self.report_dialog.open = True
        self.page.update()

    def _close_report_dialog(self):
        if hasattr(self, 'report_dialog'):
            self.report_dialog.open = False
            self.page.update()

    def _export_payments_to_pdf(self, payments):
        """Exporta los pagos a PDF (lógica copiada y adaptada de payment_view.py)."""
        try:
            downloads_path = str(Path.home() / "Downloads")
            filename = f"informe_pagos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(downloads_path, filename)

            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(letter),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )

            elements = []
            title = Paragraph("Informe de Pagos", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))

            # Tabla de datos
            data = [["Miembro", "Fecha", "Monto", "Método", "Observaciones", "Estado"]]
            for payment in payments:
                data.append([
                    f"{payment.miembro.nombre} {payment.miembro.apellido}",
                    payment.fecha_pago.strftime("%d/%m/%Y"),
                    f"${payment.monto:,.2f}",
                    payment.metodo_pago.descripcion,
                    payment.referencia if payment.referencia else "",
                    "Pagado" if payment.estado == 1 else "Cancelado"
                ])

            table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.5*inch, 2.5*inch, 1.2*inch])
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            ])
            for i, payment in enumerate(payments, 1):
                if payment.estado == 1:
                    table_style.add('BACKGROUND', (5, i), (5, i), colors.HexColor('#E2EFDA'))
                else:
                    table_style.add('BACKGROUND', (5, i), (5, i), colors.HexColor('#FFD9D9'))
            table.setStyle(table_style)
            elements.append(table)

            # Pie de página
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1
            )
            footer = Paragraph(
                f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                footer_style
            )
            elements.append(Spacer(1, 20))
            elements.append(footer)

            doc.build(elements)
            self._close_report_dialog()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Archivo PDF guardado en: {filepath}"),
                bgcolor=ft.colors.GREEN,
                open=True,
            )
            self.page.update()
        except Exception as e:
            self._close_report_dialog()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al generar PDF: {str(e)}"),
                bgcolor=ft.colors.RED,
                open=True,
            )
            self.page.update()

    def _export_members_to_pdf(self, miembros, membership_status="Todos"):
        try:
            downloads_path = str(Path.home() / "Downloads")
            status_suffix = f"_{membership_status.lower()}" if membership_status != "Todos" else ""
            filename = f"informe_miembros{status_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(downloads_path, filename)

            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(letter),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )

            elements = []
            status_text = f" - {membership_status}" if membership_status != "Todos" else ""
            title = Paragraph(f"Informe de Miembros{status_text}", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))

            # Tabla de datos
            data = [["Nombre", "Apellido", "Email", "Fecha de registro", "Estado"]]
            for m in miembros:
                data.append([
                    m.nombre,
                    m.apellido,
                    m.correo_electronico or "",
                    m.fecha_registro.strftime("%d/%m/%Y") if m.fecha_registro else "",
                    "Activo" if m.estado else "Inactivo"
                ])

            table = Table(data, colWidths=[1.5*inch, 2.5*inch, 2.2*inch, 1.5*inch, 1.2*inch])
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                ('ALIGN', (4, 1), (4, -1), 'CENTER'),
            ])
            # Colorear el estado según sea activo o inactivo
            for i, miembro in enumerate(miembros, 1):
                if miembro.estado:
                    table_style.add('BACKGROUND', (4, i), (4, i), colors.HexColor('#E2EFDA'))
                else:
                    table_style.add('BACKGROUND', (4, i), (4, i), colors.HexColor('#FFD9D9'))
            table.setStyle(table_style)
            elements.append(table)

            # Pie de página
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1
            )
            footer = Paragraph(
                f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                footer_style
            )
            elements.append(Spacer(1, 20))
            elements.append(footer)

            doc.build(elements)
            self._close_report_dialog()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Archivo PDF guardado en: {filepath}"),
                bgcolor=ft.colors.GREEN,
                open=True,
            )
            self.page.update()
        except Exception as e:
            self._close_report_dialog()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al generar PDF: {str(e)}"),
                bgcolor=ft.colors.RED,
                open=True,
            )
            self.page.update()

    async def handle_report_filter_change(self, e):
        print(f"Filtro de informe cambiado: {e.control.label} = {e.control.value}")
        
    async def handle_card_click(self, card_name: str):
        print(f"Tarjeta '{card_name}' clickeada.")

    def get_monthly_income_data(self):
        """Devuelve un diccionario con la suma de ingresos por mes del año actual."""
        pagos = self.payment_controller.get_payments({'year': self.current_year})
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        ingresos = [0]*12
        for pago in pagos:
            mes = pago.fecha_pago.month - 1
            ingresos[mes] += pago.monto
        return {"meses": meses, "ingresos": ingresos}

    def get_payment_methods_distribution(self):
        """Devuelve un diccionario con la suma de pagos por método de pago del año actual."""
        pagos = self.payment_controller.get_payments({'year': self.current_year})
        distribucion = {}
        for pago in pagos:
            metodo = pago.metodo_pago.descripcion
            distribucion[metodo] = distribucion.get(metodo, 0) + pago.monto
        return distribucion

    def get_new_members_per_month(self):
        """Devuelve un diccionario con la cantidad de nuevos miembros por mes del año actual."""
        miembros = self.member_controller.get_members({'year': self.current_year})
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        nuevos = [0]*12
        for m in miembros:
            if m.fecha_registro and m.fecha_registro.year == self.current_year:
                mes = m.fecha_registro.month - 1
                nuevos[mes] += 1
        return {"meses": meses, "nuevos": nuevos}

    def get_active_memberships_by_type(self):
        """Devuelve un diccionario con la cantidad de miembros activos por tipo de membresía."""
        miembros = self.member_controller.get_members({'status': True})
        tipos = {}
        for m in miembros:
            tipo = getattr(m, 'tipo_membresia', 'Sin tipo')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        return tipos

# No __main__ aquí. 