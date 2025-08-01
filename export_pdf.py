import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def export_contact_to_pdf(contact):
    """Exporta un contacto específico a PDF."""
    try:
        # Crear nombre de archivo
        filename = f"contacto_{contact['name'].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Crear documento PDF
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title = Paragraph("Contacto - " + contact['name'], styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Información del contacto
        data = [
            ["Campo", "Valor"],
            ["Nombre", contact['name']],
            ["Teléfono", contact['phone']],
            ["Correo", contact['email']],
            ["Dirección", contact['address']],
            ["Cumpleaños", contact['birthday']]
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#f0f0f0'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Fecha de exportación
        date_para = Paragraph(f"Exportado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        story.append(date_para)
        
        # Generar PDF
        doc.build(story)
        return True, f"Contacto exportado a {filename}"
        
    except Exception as e:
        return False, f"No se pudo exportar el contacto: {str(e)}"

def export_selected_to_pdf(selected_contacts):
    """Exporta los contactos seleccionados a PDF."""
    try:
        if not selected_contacts:
            return False, "No hay contactos seleccionados"
            
        filename = f"contactos_seleccionados_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Crear documento PDF
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title = Paragraph("Lista de Contactos", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Datos de todos los contactos seleccionados
        data = [["Nombre", "Teléfono", "Correo", "Cumpleaños"]]
        
        for contact in selected_contacts:
            data.append([
                contact['name'],
                contact['phone'],
                contact['email'],
                contact['birthday']
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Resumen
        summary = Paragraph(f"Total de contactos exportados: {len(selected_contacts)}", styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 12))
        
        # Fecha de exportación
        date_para = Paragraph(f"Exportado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        story.append(date_para)
        
        # Generar PDF
        doc.build(story)
        return True, f"Contactos exportados a {filename}"
        
    except Exception as e:
        return False, f"No se pudieron exportar los contactos: {str(e)}"

def export_all_to_pdf(all_contacts):
    """Exporta todos los contactos a PDF."""
    try:
        if not all_contacts:
            return False, "No hay contactos para exportar"
            
        filename = f"agenda_completa_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Crear documento PDF
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title = Paragraph("Agenda Completa", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Datos de todos los contactos
        data = [["Nombre", "Teléfono", "Correo", "Cumpleaños"]]
        
        for contact in all_contacts:
            data.append([
                contact['name'],
                contact['phone'],
                contact['email'],
                contact['birthday']
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Resumen
        summary = Paragraph(f"Total de contactos: {len(all_contacts)}", styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 12))
        
        # Fecha de exportación
        date_para = Paragraph(f"Exportado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        story.append(date_para)
        
        # Generar PDF
        doc.build(story)
        return True, f"Agenda exportada a {filename}"
        
    except Exception as e:
        return False, f"No se pudo exportar la agenda: {str(e)}"