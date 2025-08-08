import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.colors import HexColor
from reportlab.platypus import Flowable

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def build_table(data, header):
    table = Table([header] + data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#f9f9f9'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000')
    ]))
    return table

class HorizontalLine(Flowable):
    """Línea decorativa para usar con Platypus."""
    def __init__(self, width, thickness=1, color=HexColor("#2E86C1")):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)

def build_header(styles, width=500):
    header = []
    app_name = Paragraph("<b><font size=16 color='#2E86C1'>ContactVault</font></b>", styles['Normal'])
    header.append(app_name)
    header.append(Spacer(1, 6))
    header.append(HorizontalLine(width, 2))
    header.append(Spacer(1, 12))
    return header

def export_contact_to_pdf(contact):
    """Exporta un contacto individual a PDF."""
    try:
        filename = f"contacto_{contact.get('name', 'SinNombre').replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(EXPORT_DIR, filename)
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.extend(build_header(styles))
        story.append(Paragraph(f"<b>Contacto - {contact.get('name', 'Sin nombre')}</b>", styles['Title']))
        story.append(Spacer(1, 12))

        data = [
            ["Campo", "Valor"],
            ["Nombre", contact.get('name', '')],
            ["Teléfono", contact.get('phone', '')],
            ["Correo", contact.get('email', '')],
            ["Dirección", contact.get('address', '')],
            ["Cumpleaños", contact.get('birthday', '')]
        ]

        story.append(build_table(data[1:], data[0]))
        story.append(Spacer(1, 12))

        story.append(Paragraph(f"Exportado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))

        doc.build(story)
        return True, f"Contacto exportado a {filepath}"

    except Exception as e:
        return False, f"Error al exportar contacto: {e}"

def export_contacts_to_pdf(contacts, filename_prefix="contactos_exportados", title="Contactos"):
    """Exporta una lista de contactos a PDF (usado por export_selected y export_all)."""
    try:
        if not contacts:
            return False, "No hay contactos para exportar"

        filename = f"{filename_prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(EXPORT_DIR, filename)
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.extend(build_header(styles))
        story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
        story.append(Spacer(1, 12))

        data = []
        for c in contacts:
            data.append([
                c.get('name', ''),
                c.get('phone', ''),
                c.get('email', ''),
                c.get('birthday', '')
            ])

        header = ["Nombre", "Teléfono", "Correo", "Cumpleaños"]
        story.append(build_table(data, header))
        story.append(Spacer(1, 12))

        story.append(Paragraph(f"Total de contactos: {len(contacts)}", styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Exportado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))

        doc.build(story)
        return True, f"Contactos exportados a {filepath}"

    except Exception as e:
        return False, f"Error al exportar contactos: {e}"

# Aliases para usarlos desde la app
export_selected_to_pdf = lambda selected: export_contacts_to_pdf(
    selected, "contactos_seleccionados", "Contactos Seleccionados")

export_all_to_pdf = lambda all_contacts: export_contacts_to_pdf(
    all_contacts, "agenda_completa", "Agenda Completa")
