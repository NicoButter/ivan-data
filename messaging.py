"""
Módulo de mensajería para la aplicación Agenda
Contiene funciones para enviar emails y mensajes de WhatsApp
"""

import webbrowser
import tkinter as tk
from tkinter import messagebox

def send_email(contact):
    """
    Envía un correo electrónico al contacto seleccionado.
    
    Args:
        contact (dict): Diccionario con los datos del contacto
        
    Returns:
        tuple: (bool, mensaje) - Resultado de la operación
    """
    try:
        # Verificar si tiene correo
        if not contact.get("email"):
            return False, "Este contacto no tiene correo electrónico registrado."
        
        # Intentar abrir el cliente de correo predeterminado
        email = contact["email"]
        subject = "Mensaje desde Agenda Encriptada"
        body = "Hola, este es un mensaje automático desde tu agenda."
        mailto_url = f"mailto:{email}?subject={subject}&body={body}"
        webbrowser.open(mailto_url)
        return True, f"Abriendo cliente de correo para: {email}"
        
    except Exception as e:
        return False, f"No se pudo abrir el cliente de correo: {str(e)}"

def send_whatsapp(contact):
    """
    Envía un mensaje de WhatsApp al contacto seleccionado.
    
    Args:
        contact (dict): Diccionario con los datos del contacto
        
    Returns:
        tuple: (bool, mensaje) - Resultado de la operación
    """
    try:
        # Verificar si tiene teléfono
        if not contact.get("phone"):
            return False, "Este contacto no tiene número de teléfono registrado."
        
        # Limpiar número de teléfono (quitar caracteres no numéricos)
        phone = ''.join(filter(str.isdigit, contact["phone"]))
        
        # Verificar que tenga al menos 10 dígitos
        if len(phone) < 10:
            return False, "Número de teléfono inválido."
        
        # Construir URL correcta para WhatsApp Web
        # Formato correcto: https://wa.me/NUMERO_DE_TELEFONO
        whatsapp_url = f"https://wa.me/{phone}"
        
        # Intentar abrir WhatsApp Web
        webbrowser.open(whatsapp_url)
        return True, f"Abriendo WhatsApp para: {contact['phone']}"
        
    except Exception as e:
        return False, f"No se pudo abrir WhatsApp: {str(e)}"