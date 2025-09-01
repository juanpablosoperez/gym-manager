import flet as ft
from datetime import datetime
from gym_manager.controllers.member_controller import MemberController
from gym_manager.controllers.payment_controller import PaymentController
from gym_manager.utils.database import get_db_session
from pathlib import Path
import os
import asyncio

# Imports para gráficos nativos de Flet
import flet as ft

class StatisticsController:
    def __init__(self, view, page):
        self.view = view
        self.page = page
        self.current_year = datetime.now().year
        self.member_controller = MemberController(get_db_session())
        self.payment_controller = PaymentController(get_db_session())
        self._cache = {}  # Cache mejorado para evitar consultas repetidas
        self._cache_timeout = 300  # 5 minutos de timeout para el cache
        self._cache_timestamps = {}  # Timestamps para controlar la expiración del cache

    def _initialize_event_handlers(self):
        """Conecta los manejadores de eventos a los controles de la vista."""
        if self.view is None:
            return
        
        # Asegurar que los componentes UI estén creados antes de asignar event handlers
        self.view._create_ui_components_lazy()
        
        # Ahora asignar los event handlers
        if hasattr(self.view, 'generate_report_button'):
            self.view.generate_report_button.on_click = self.handle_generate_report
        if hasattr(self.view, 'report_type_dropdown'):
            self.view.report_type_dropdown.on_change = self.handle_report_filter_change
        if hasattr(self.view, 'membership_status_dropdown'):
            self.view.membership_status_dropdown.on_change = self.handle_report_filter_change

    async def initialize_statistics(self):
        """Carga los datos iniciales para el panel de estadísticas con optimizaciones."""
        if self.view is None:
            print("Error: Vista es None")
            return
        
        print("🚀 Iniciando carga de estadísticas...")
        
        try:
            self.view.show_loading()
        except Exception as e:
            print(f"Error mostrando loader: {e}")
        
        try:
            # Cargar datos de tarjetas primero (más rápido)
            print("📊 Cargando datos de tarjetas...")
            await self.load_summary_cards_data()
            print("✅ Datos de tarjetas cargados")
            self.page.update()
            
            # Cargar gráficos en segundo plano de forma asíncrona
            print("📈 Iniciando carga de gráficos en background...")
            asyncio.create_task(self._load_charts_background())
            
        except Exception as e:
            print(f"Error en initialize_statistics: {e}")
        finally:
            # Ocultar loader para las tarjetas (los gráficos seguirán cargando en background)
            try:
                self.view.hide_loading()
            except Exception as e:
                print(f"Error ocultando loader: {e}")
            self.page.update()
    
    async def _load_charts_background(self):
        """Carga los gráficos en segundo plano sin bloquear la UI"""
        try:
            print("🎨 Cargando gráficos...")
            await self.load_charts_data()
            print("✅ Gráficos cargados")
        except Exception as e:
            print(f"Error cargando gráficos: {e}")

    async def load_summary_cards_data(self):
        """Carga los datos para las tarjetas de resumen de manera optimizada con cache."""
        try:
            # Verificar cache primero
            cache_key = f"summary_cards_{self.current_year}"
            if self._is_cache_valid(cache_key):
                print("💾 Usando datos en cache")
                cached_data = self._cache[cache_key]
                self._update_cards_with_data(cached_data)
                return
            
            print("🔄 Obteniendo datos frescos de la base de datos...")
            
            # Ejecutar consultas de forma secuencial para evitar problemas de concurrencia
            # con la sesión de base de datos
            try:
                active_members_count = self.member_controller.get_active_members_count()
                print(f"✓ Miembros activos: {active_members_count}")
            except Exception as e:
                print(f"✗ Error obteniendo miembros activos: {e}")
                active_members_count = 0
                
            try:
                current_month_payments = self.payment_controller.get_current_month_payments_sum()
                print(f"✓ Pagos del mes: ${current_month_payments}")
            except Exception as e:
                print(f"✗ Error obteniendo pagos del mes: {e}")
                current_month_payments = 0
                
            try:
                expired_memberships_count = self.member_controller.get_expired_memberships_count()
                print(f"✓ Membresías vencidas: {expired_memberships_count}")
            except Exception as e:
                print(f"✗ Error obteniendo membresías vencidas: {e}")
                expired_memberships_count = 0
                
            try:
                annual_income = self.payment_controller.get_current_year_payments_sum()
                print(f"✓ Ingresos anuales: ${annual_income}")
            except Exception as e:
                print(f"✗ Error obteniendo ingresos anuales: {e}")
                annual_income = 0
            
            # Guardar en cache
            data = {
                'active_members': active_members_count,
                'monthly_payments': current_month_payments,
                'expired_memberships': expired_memberships_count,
                'annual_income': annual_income
            }
            self._cache[cache_key] = data
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            
            # Actualizar UI
            self._update_cards_with_data(data)
            print("📊 Tarjetas actualizadas correctamente")
            
        except Exception as e:
            print(f"Error general en load_summary_cards_data: {e}")
            # En caso de error, mostrar valores por defecto
            self._set_default_card_values()
    
    def _update_cards_with_data(self, data):
        """Actualiza las tarjetas con los datos proporcionados"""
        try:
            # Asegurar que los componentes UI estén creados
            if not self.view._ui_components_created:
                self.view._create_ui_components_lazy()
            
            # Verificar que las tarjetas existan antes de actualizarlas
            if hasattr(self.view, 'active_members_today_card'):
                self.view.active_members_today_card.content.controls[1].controls[0].value = str(data['active_members'])
            if hasattr(self.view, 'monthly_payments_card'):
                self.view.monthly_payments_card.content.controls[1].controls[0].value = f"${data['monthly_payments']:,.2f}"
            if hasattr(self.view, 'expired_memberships_card'):
                self.view.expired_memberships_card.content.controls[1].controls[0].value = str(data['expired_memberships'])
            if hasattr(self.view, 'total_annual_income_card'):
                self.view.total_annual_income_card.content.controls[1].controls[0].value = f"${data['annual_income']:,.2f}"
                if len(self.view.total_annual_income_card.content.controls[1].controls) > 1:
                    self.view.total_annual_income_card.content.controls[1].controls[1].value = f"Ingresos {self.current_year}"
            
            # Forzar actualización de la UI
            self.page.update()
            
        except Exception as e:
            print(f"Error actualizando tarjetas: {e}")  # Debug
            self._set_default_card_values()
    
    def _is_cache_valid(self, cache_key):
        """Verifica si el cache es válido basado en el timestamp"""
        if cache_key not in self._cache or cache_key not in self._cache_timestamps:
            return False
        
        current_time = datetime.now().timestamp()
        cache_time = self._cache_timestamps[cache_key]
        return (current_time - cache_time) < self._cache_timeout

    def _set_default_card_values(self):
        """Establece valores por defecto en las tarjetas cuando hay un error."""
        try:
            # Asegurar que los componentes UI estén creados
            if not self.view._ui_components_created:
                self.view._create_ui_components_lazy()
            
            # Verificar que las tarjetas existan antes de actualizarlas
            if hasattr(self.view, 'active_members_today_card'):
                self.view.active_members_today_card.content.controls[1].controls[0].value = "0"
            if hasattr(self.view, 'monthly_payments_card'):
                self.view.monthly_payments_card.content.controls[1].controls[0].value = "$0.00"
            if hasattr(self.view, 'expired_memberships_card'):
                self.view.expired_memberships_card.content.controls[1].controls[0].value = "0"
            if hasattr(self.view, 'total_annual_income_card'):
                self.view.total_annual_income_card.content.controls[1].controls[0].value = "$0.00"
            
            # Forzar actualización de la UI
            self.page.update()
            
        except Exception as e:
            print(f"Error estableciendo valores por defecto: {e}")  # Debug

    async def load_charts_data(self):
        """Carga y configura los datos para los gráficos usando Flet nativo."""
        try:
            # Obtener datos de gráficos de forma secuencial para evitar problemas de concurrencia
            print("📈 Obteniendo datos para gráficos...")
            
            data_ingresos = self._get_cached_monthly_income_data()
            print("✓ Datos de ingresos obtenidos")
            
            data_metodos = self._get_cached_payment_methods_distribution()
            print("✓ Datos de métodos de pago obtenidos")
            
            data_nuevos = self._get_cached_new_members_per_month()
            print("✓ Datos de nuevos miembros obtenidos")
            
            data_tipos = self._get_cached_active_memberships_by_type()
            print("✓ Datos de tipos de membresía obtenidos")
            
            # Crear gráficos nativos de Flet uno por uno para mejor UX
            await self._create_flet_chart_async("income", data_ingresos, 0)
            await self._create_flet_chart_async("payment_methods", data_metodos, 0.5)
            await self._create_flet_chart_async("new_members", data_nuevos, 1)
            await self._create_flet_chart_async("memberships_by_type", data_tipos, 1.5)
            
        except Exception as e:
            print(f"Error en load_charts_data: {e}")
    
    async def _create_flet_chart_async(self, chart_type, data, delay_seconds):
        """Crea un gráfico nativo de Flet de forma asíncrona con un pequeño delay para mejorar UX"""
        try:
            # Pequeño delay para escalonar la creación de gráficos
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds * 0.5)
            
            if isinstance(data, Exception) or not data:
                return
                
            chart = None
            
            if chart_type == "income" and hasattr(self.view, 'income_bar_chart'):
                # Crear gráfico de barras para ingresos
                chart = ft.BarChart(
                    bar_groups=[
                        ft.BarChartGroup(
                            x=i,
                            bar_rods=[
                                ft.BarChartRod(
                                    from_y=0,
                                    to_y=data["ingresos"][i],
                                    width=40,
                                    color=ft.colors.BLUE_600,
                                    tooltip=f"{data['meses'][i]}: ${data['ingresos'][i]:,.0f}",
                                    border_radius=0,
                                )
                            ],
                        ) for i in range(len(data["meses"]))
                    ],
                    border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                    left_axis=ft.ChartAxis(
                        labels_size=40,
                    ),
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(
                                value=i,
                                label=ft.Container(
                                    ft.Text(data["meses"][i][:3], size=12),
                                    margin=ft.margin.only(top=10),
                                ),
                            ) for i in range(len(data["meses"]))
                        ],
                        labels_size=40,
                    ),
                    tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY_900),
                    min_y=0,
                    max_y=max(data["ingresos"]) * 1.1 if data["ingresos"] else 1000,
                    expand=True,
                )
                self.view.income_bar_chart.content.controls[1] = chart
                
            elif chart_type == "payment_methods" and hasattr(self.view, 'payment_method_pie_chart'):
                # Crear gráfico de torta para métodos de pago
                colors = [ft.colors.BLUE_400, ft.colors.GREEN_400, ft.colors.ORANGE_400, ft.colors.PURPLE_400, ft.colors.RED_400]
                sections = []
                total = sum(data.values()) if data else 1
                
                for i, (label, value) in enumerate(data.items()):
                    percentage = (value / total) * 100 if total > 0 else 0
                    sections.append(
                        ft.PieChartSection(
                            value=value,
                            title=f"{label}\n{percentage:.1f}%",
                            color=colors[i % len(colors)],
                            radius=100,
                            title_style=ft.TextStyle(
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
                            ),
                        )
                    )
                
                chart = ft.PieChart(
                    sections=sections,
                    sections_space=2,
                    center_space_radius=40,
                    expand=True,
                )
                self.view.payment_method_pie_chart.content.controls[1] = chart
                
            elif chart_type == "new_members" and hasattr(self.view, 'new_members_line_chart'):
                # Crear gráfico de líneas para nuevos miembros
                data_points = []
                for i, mes in enumerate(data["meses"]):
                    data_points.append(ft.LineChartDataPoint(i, data["nuevos"][i]))
                
                chart = ft.LineChart(
                    data_series=[
                        ft.LineChartData(
                            data_points=data_points,
                            stroke_width=3,
                            color=ft.colors.GREEN_600,
                            curved=True,
                            stroke_cap_round=True,
                        ),
                    ],
                    border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                    horizontal_grid_lines=ft.ChartGridLines(
                        color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                        width=1,
                    ),
                    vertical_grid_lines=ft.ChartGridLines(
                        color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                        width=1,
                    ),
                    left_axis=ft.ChartAxis(
                        labels_size=40,
                    ),
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(
                                value=i,
                                label=ft.Container(
                                    ft.Text(mes[:3], size=12),
                                    margin=ft.margin.only(top=10),
                                ),
                            ) for i, mes in enumerate(data["meses"])
                        ],
                        labels_size=40,
                    ),
                    tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY_900),
                    min_y=0,
                    max_y=max(data["nuevos"]) * 1.1 if data["nuevos"] else 10,
                    expand=True,
                )
                self.view.new_members_line_chart.content.controls[1] = chart
                
            elif chart_type == "memberships_by_type" and hasattr(self.view, 'active_memberships_by_type_chart'):
                # Crear gráfico de barras para tipos de membresía
                chart = ft.BarChart(
                    bar_groups=[
                        ft.BarChartGroup(
                            x=i,
                            bar_rods=[
                                ft.BarChartRod(
                                    from_y=0,
                                    to_y=list(data.values())[i],
                                    width=40,
                                    color=ft.colors.ORANGE_600,
                                    tooltip=f"{list(data.keys())[i]}: {list(data.values())[i]}",
                                    border_radius=0,
                                )
                            ],
                        ) for i in range(len(data))
                    ],
                    border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                    left_axis=ft.ChartAxis(
                        labels_size=40,
                    ),
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(
                                value=i,
                                label=ft.Container(
                                    ft.Text(list(data.keys())[i][:8], size=10),
                                    margin=ft.margin.only(top=10),
                                ),
                            ) for i in range(len(data))
                        ],
                        labels_size=40,
                    ),
                    tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY_900),
                    min_y=0,
                    max_y=max(data.values()) * 1.1 if data.values() else 10,
                    expand=True,
                )
                self.view.active_memberships_by_type_chart.content.controls[1] = chart
            
            # Actualizar UI después de crear cada gráfico
            if chart:
                self.page.update()
                
        except Exception as e:
            print(f"Error creando gráfico {chart_type}: {e}")  # Debug

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
            status_text = f" ({membership_status.lower()}s)" if membership_status and membership_status != "Todos" else ""
            self._show_report_confirmation_dialog(
                f"¿Deseas exportar {count} miembros{status_text} a PDF? El archivo se guardará en tu carpeta de Descargas.",
                lambda _: self._export_members_to_pdf(miembros, membership_status or "Todos")
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
                    on_click=lambda e: self._handle_report_export(on_confirm),
                    style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )
        self.page.overlay.append(self.report_dialog)
        self.report_dialog.open = True
        self.page.update()

    def _handle_report_export(self, on_confirm):
        """Muestra loader durante la exportación y ejecuta la acción de confirmación."""
        try:
            # Mostrar loader
            if hasattr(self.view, 'show_loading'):
                self.view.show_loading()
        except Exception:
            pass
        try:
            on_confirm(None)
        finally:
            # Ocultar loader al terminar
            try:
                if hasattr(self.view, 'hide_loading'):
                    self.view.hide_loading()
            except Exception:
                pass

    def _close_report_dialog(self):
        if hasattr(self, 'report_dialog'):
            self.report_dialog.open = False
            self.page.update()

    def _export_payments_to_pdf(self, payments):
        """Exporta los pagos a PDF (lógica copiada y adaptada de payment_view.py)."""
        try:
            # Importar reportlab solo cuando se necesita
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
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
            # Importar reportlab solo cuando se necesita
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
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
        pass
        
    async def handle_card_click(self, card_name: str):
        pass

    def _get_cached_monthly_income_data(self):
        """Devuelve un diccionario con la suma de ingresos por mes del año actual con cache mejorado."""
        cache_key = f"monthly_income_{self.current_year}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            pagos = self.payment_controller.get_payments({'year': self.current_year})
            meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            ingresos = [0]*12
            for pago in pagos:
                mes = pago.fecha_pago.month - 1
                ingresos[mes] += pago.monto
            
            result = {"meses": meses, "ingresos": ingresos}
            self._cache[cache_key] = result
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            return result
        except Exception:
            return {"meses": [], "ingresos": []}

    def _get_cached_payment_methods_distribution(self):
        """Devuelve un diccionario con la suma de pagos por método de pago del año actual con cache mejorado."""
        cache_key = f"payment_methods_{self.current_year}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            pagos = self.payment_controller.get_payments({'year': self.current_year})
            distribucion = {}
            for pago in pagos:
                metodo = pago.metodo_pago.descripcion
                distribucion[metodo] = distribucion.get(metodo, 0) + pago.monto
            
            self._cache[cache_key] = distribucion
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            return distribucion
        except Exception:
            return {}

    def _get_cached_new_members_per_month(self):
        """Devuelve un diccionario con la cantidad de nuevos miembros por mes del año actual con cache mejorado."""
        cache_key = f"new_members_{self.current_year}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            miembros = self.member_controller.get_members({'year': self.current_year})
            meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            nuevos = [0]*12
            for m in miembros:
                if m.fecha_registro and m.fecha_registro.year == self.current_year:
                    mes = m.fecha_registro.month - 1
                    nuevos[mes] += 1
            
            result = {"meses": meses, "nuevos": nuevos}
            self._cache[cache_key] = result
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            return result
        except Exception:
            return {"meses": [], "nuevos": []}

    def _get_cached_active_memberships_by_type(self):
        """Devuelve un diccionario con la cantidad de miembros activos por tipo de membresía con cache mejorado."""
        cache_key = "active_memberships_by_type"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            miembros = self.member_controller.get_members({'status': True})
            tipos = {}
            for m in miembros:
                tipo = getattr(m, 'tipo_membresia', 'Sin tipo')
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            self._cache[cache_key] = tipos
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            return tipos
        except Exception:
            return {}
    
    # Mantener métodos originales para compatibilidad
    def get_monthly_income_data(self):
        return self._get_cached_monthly_income_data()
    
    def get_payment_methods_distribution(self):
        return self._get_cached_payment_methods_distribution()
    
    def get_new_members_per_month(self):
        return self._get_cached_new_members_per_month()
    
    def get_active_memberships_by_type(self):
        return self._get_cached_active_memberships_by_type()
    
    def clear_cache(self):
        """Limpia el cache manualmente si es necesario"""
        self._cache.clear()
        self._cache_timestamps.clear() 