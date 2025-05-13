import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

def get_downloads_path():
    """
    Obtiene la ruta de la carpeta de descargas del usuario
    """
    return os.path.join(os.path.expanduser("~"), "Downloads")

def export_members_to_excel(members, file_path=None):
    """
    Exporta una lista de miembros a un archivo Excel.
    :param members: lista de objetos Miembro
    :param file_path: ruta del archivo Excel a generar (opcional)
    :return: ruta del archivo generado
    """
    data = []
    for m in members:
        data.append({
            'ID': m.id_miembro,
            'Nombre': m.nombre,
            'Apellido': m.apellido,
            'Documento': m.documento,
            'Fecha de Nacimiento': m.fecha_nacimiento.strftime('%d/%m/%Y') if m.fecha_nacimiento else '',
            'Género': m.genero,
            'Email': m.correo_electronico,
            'Estado': 'Activo' if m.estado else 'Inactivo',
            'Tipo de Membresía': m.tipo_membresia,
            'Dirección': m.direccion or '',
            'Teléfono': m.telefono or '',
            'Fecha de Registro': m.fecha_registro.strftime('%d/%m/%Y') if m.fecha_registro else '',
            'Condiciones Médicas': m.informacion_medica or ''
        })
    df = pd.DataFrame(data)
    if not file_path:
        downloads_path = get_downloads_path()
        file_path = os.path.join(downloads_path, f"reporte_miembros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    df.to_excel(file_path, index=False)
    return file_path

def export_members_to_pdf(members, file_path=None):
    """
    Exporta una lista de miembros a un archivo PDF.
    :param members: lista de objetos Miembro
    :param file_path: ruta del archivo PDF a generar (opcional)
    :return: ruta del archivo generado
    """
    if not file_path:
        downloads_path = get_downloads_path()
        file_path = os.path.join(downloads_path, f"reporte_miembros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Reporte de Miembros', ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    headers = [
        'ID', 'Nombre', 'Apellido', 'Documento', 'Fecha de Nacimiento', 'Género',
        'Email', 'Estado', 'Tipo de Membresía', 'Dirección', 'Teléfono', 'Fecha de Registro', 'Condiciones Médicas'
    ]
    col_widths = [10, 25, 25, 25, 25, 15, 40, 15, 30, 35, 25, 25, 40]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C')
    pdf.ln()
    pdf.set_font('Arial', '', 9)
    for m in members:
        row = [
            str(m.id_miembro),
            m.nombre,
            m.apellido,
            m.documento,
            m.fecha_nacimiento.strftime('%d/%m/%Y') if m.fecha_nacimiento else '',
            m.genero,
            m.correo_electronico,
            'Activo' if m.estado else 'Inactivo',
            m.tipo_membresia,
            m.direccion or '',
            m.telefono or '',
            m.fecha_registro.strftime('%d/%m/%Y') if m.fecha_registro else '',
            m.informacion_medica or ''
        ]
        for i, value in enumerate(row):
            pdf.cell(col_widths[i], 8, str(value)[:30], border=1)
        pdf.ln()
    pdf.output(file_path)
    return file_path

