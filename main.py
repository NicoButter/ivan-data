import json
import os
import sys
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import tkinter as tk
from tkinter import ttk, messagebox
import re

# Archivo para los datos encriptados
AGENDA_FILE = "agenda.json.enc"

# Importar funciones de otros módulos
from export_pdf import export_contact_to_pdf, export_selected_to_pdf, export_all_to_pdf
from backup_manager import create_backup
from messaging import send_email, send_whatsapp

class AgendaApp:
    def __init__(self, root: tk.Tk):
        """Inicializa la aplicación de agenda."""
        self.root = root
        self.root.title("Agenda Tradicional (Encriptada)")
        self.root.geometry("1024x800")
        self.root.minsize(600, 400)
        
        # Variable para almacenar la contraseña
        self.password = None
        self.agenda = []
        
        # Configurar estilo de ventana principal
        self.root.configure(bg='white')
        
        # Mostrar ventana de autenticación
        if not self.show_authentication():
            self.root.destroy()
            return
            
        # Cargar agenda
        self.agenda = self.load_agenda()
        
        # Configurar la interfaz gráfica
        self.setup_ui()
    
    def show_authentication(self) -> bool:
        """Muestra ventana de autenticación y devuelve True si es exitosa."""
        try:
            # Crear ventana modal de autenticación
            auth_window = tk.Toplevel(self.root)
            auth_window.title("Autenticación")
            auth_window.geometry("400x250")
            auth_window.transient(self.root)
            auth_window.grab_set()
            
            # Centrar ventana
            auth_window.update_idletasks()
            x = (auth_window.winfo_screenwidth() // 2) - (auth_window.winfo_width() // 2)
            y = (auth_window.winfo_screenheight() // 2) - (auth_window.winfo_height() // 2)
            auth_window.geometry(f"+{x}+{y}")
            
            # Marco principal
            main_frame = tk.Frame(auth_window, bg='white', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            tk.Label(main_frame, text="🔐 Autenticación", 
                    font=("Arial", 14, "bold"),
                    fg='black',
                    bg='white').pack(pady=10)
            
            # Campo de contraseña
            tk.Label(main_frame, text="Contraseña:", font=("Arial", 10),
                    fg='black', bg='white').pack(anchor=tk.W)
            password_entry = tk.Entry(main_frame, show="*", width=30, font=("Arial", 10))
            password_entry.pack(pady=5)
            password_entry.focus_set()
            
            # Confirmar contraseña si es nueva
            confirm_entry = None
            if not os.path.exists(AGENDA_FILE):
                tk.Label(main_frame, text="Confirmar contraseña:", font=("Arial", 10),
                        fg='black', bg='white').pack(anchor=tk.W, pady=(10, 0))
                confirm_entry = tk.Entry(main_frame, show="*", width=30, font=("Arial", 10))
                confirm_entry.pack(pady=5)
            
            def submit_auth():
                password = password_entry.get()
                if not os.path.exists(AGENDA_FILE):
                    confirm = confirm_entry.get() if confirm_entry else ""
                    if password and password == confirm:
                        self.password = password
                        auth_window.destroy()
                        return
                    else:
                        messagebox.showerror("Error", "Las contraseñas no coinciden o están vacías.")
                        return
                else:
                    if password:
                        self.password = password
                        auth_window.destroy()
                        return
                    else:
                        messagebox.showerror("Error", "La contraseña no puede estar vacía.")
                        return
            
            def cancel_auth():
                self.password = None
                auth_window.destroy()
            
            # Botones con atajos de teclado
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(pady=20)
            
            accept_btn = tk.Button(button_frame, text="ACEPTAR", command=submit_auth, 
                                 width=10, height=1, bg='#4CAF50', fg='white',
                                 font=("Arial", 10, "bold"))
            accept_btn.pack(side=tk.LEFT, padx=5)
            
            # Asociar Enter al botón de aceptar
            accept_btn.bind('<Return>', lambda event: submit_auth())
            accept_btn.focus_set()  # Enfocar el botón de aceptar
            
            cancel_btn = tk.Button(button_frame, text="CANCELAR", command=cancel_auth, 
                                 width=10, height=1, bg='#f44336', fg='white',
                                 font=("Arial", 10, "bold"))
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            # Asociar Esc al botón de cancelar
            cancel_btn.bind('<Escape>', lambda event: cancel_auth())
            
            # Manejar cierre de ventana
            def on_closing():
                self.password = None
                auth_window.destroy()
            
            auth_window.protocol("WM_DELETE_WINDOW", on_closing)
            
            # Permitir que Enter active el botón de aceptar
            auth_window.bind('<Return>', lambda event: submit_auth())
            # Permitir que Esc active el botón de cancelar
            auth_window.bind('<Escape>', lambda event: cancel_auth())
            
            # Esperar a que se cierre la ventana
            auth_window.wait_window()
            
            return self.password is not None
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return False
    
    def derive_key(self, password: str) -> bytes:
        """Deriva una clave Fernet desde la contraseña usando PBKDF2."""
        salt = b'agenda_salt'  # Salt fijo para consistencia
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        return key
    
    def load_agenda(self) -> List[Dict]:
        """Carga los contactos desde el archivo encriptado."""
        if not os.path.exists(AGENDA_FILE):
            return []
        try:
            if self.password is None:
                raise ValueError("Contraseña no inicializada.")
            key = self.derive_key(self.password)
            fernet = Fernet(key)
            with open(AGENDA_FILE, 'rb') as file:
                encrypted_data = file.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            agenda = json.loads(decrypted_data.decode('utf-8'))
            # Asegurar que cada contacto tenga el campo 'birthday'
            for contact in agenda:
                contact.setdefault("birthday", "")
            return agenda
        except (json.JSONDecodeError, ValueError, Exception):
            messagebox.showerror("Error", "Contraseña incorrecta o archivo corrupto. Iniciando con agenda vacía.")
            return []
    
    def save_agenda(self) -> None:
        """Guarda los contactos en el archivo encriptado."""
        try:
            if self.password is None:
                raise ValueError("Contraseña no inicializada.")
            key = self.derive_key(self.password)
            fernet = Fernet(key)
            data = json.dumps(self.agenda, indent=4, ensure_ascii=False).encode('utf-8')
            encrypted_data = fernet.encrypt(data)
            with open(AGENDA_FILE, 'wb') as file:
                file.write(encrypted_data)
        except (IOError, ValueError) as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")
    
    def setup_ui(self) -> None:
        """Configura la interfaz gráfica."""
        # Marco para botones
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Botones principales
        buttons_config = [
            ("Agregar Contacto", self.add_contact_window),
            ("Buscar Contacto", self.search_contact_window),
            ("Editar Contacto", self.edit_contact_window),
            ("Eliminar Contacto", self.delete_contact),
            ("Exportar", self.export_menu),  # Nuevo botón de exportación
            ("Configuración", self.config_window),
            ("Salir", self.root.quit)
        ]
        
        for text, command in buttons_config:
            btn = tk.Button(button_frame, text=text, command=command, 
                           width=15, height=2, bg='#2196F3', fg='white',
                           font=("Arial", 10, "bold"))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Marco para la tabla
        table_frame = tk.Frame(self.root, bg='white')
        table_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Tabla de contactos
        columns = ("Nombre", "Teléfono", "Correo", "Dirección", "Cumpleaños")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configurar encabezados
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar elementos
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Vincular eventos de clic
        self.tree.bind('<Button-3>', self.show_context_menu)  # Botón derecho
        self.tree.bind('<Double-1>', self.edit_contact_double_click)  # Doble clic
        
        # Actualizar tabla
        self.update_table()
    
    def show_context_menu(self, event):
        """Muestra el menú contextual cuando se hace clic derecho en un contacto."""
        # Obtener el ítem bajo el cursor
        item = self.tree.identify_row(event.y)
        if item:
            # Seleccionar el ítem
            self.tree.selection_set(item)
            
            # Crear menú contextual
            context_menu = tk.Menu(self.root, tearoff=0)
            
            # Obtener datos del contacto seleccionado
            index = self.tree.index(item)
            contact = self.agenda[index]
            
            # Agregar opciones al menú
            context_menu.add_command(label="📧 Enviar Email", 
                                   command=lambda: self.send_email_action(contact))
            context_menu.add_command(label="📱 WhatsApp", 
                                   command=lambda: self.send_whatsapp_action(contact))
            
            # Agregar separador
            context_menu.add_separator()
            
            # Opciones de edición
            context_menu.add_command(label="Editar Contacto", 
                                   command=lambda: self.edit_contact_by_index(index))
            context_menu.add_command(label="Eliminar Contacto", 
                                   command=lambda: self.delete_contact_by_index(index))
            
            # Mostrar menú contextual
            context_menu.post(event.x_root, event.y_root)
    
    def edit_contact_double_click(self, event):
        """Edita un contacto con doble clic."""
        item = self.tree.identify_row(event.y)
        if item:
            index = self.tree.index(item)
            self.edit_contact_by_index(index)
    
    def send_email_action(self, contact):
        """Envía un correo electrónico al contacto."""
        success, message = send_email(contact)
        if success:
            messagebox.showinfo("Éxito", message)
        else:
            messagebox.showerror("Error", message)
    
    def send_whatsapp_action(self, contact):
        """Envía un mensaje de WhatsApp al contacto."""
        success, message = send_whatsapp(contact)
        if success:
            messagebox.showinfo("Éxito", message)
        else:
            messagebox.showerror("Error", message)
    
    def edit_contact_by_index(self, index):
        """Edita un contacto por su índice."""
        if index < len(self.agenda):
            contact = self.agenda[index]
            # Crear ventana de edición
            window = tk.Toplevel(self.root)
            window.title("Editar Contacto")
            window.geometry("450x400")
            window.transient(self.root)
            window.grab_set()
            
            # Centrar ventana
            window.update_idletasks()
            x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
            y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
            window.geometry(f"+{x}+{y}")
            
            # Formulario
            form_frame = tk.Frame(window, padx=20, pady=20)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(form_frame, text="Nombre *:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
            name_entry = tk.Entry(form_frame, width=30)
            name_entry.insert(0, contact["name"])
            name_entry.grid(row=1, column=0, sticky=tk.W, pady=5)
            
            tk.Label(form_frame, text="Teléfono:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
            phone_entry = tk.Entry(form_frame, width=30)
            phone_entry.insert(0, contact["phone"])
            phone_entry.grid(row=3, column=0, sticky=tk.W, pady=5)
            
            tk.Label(form_frame, text="Correo:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
            email_entry = tk.Entry(form_frame, width=30)
            email_entry.insert(0, contact["email"])
            email_entry.grid(row=5, column=0, sticky=tk.W, pady=5)
            
            tk.Label(form_frame, text="Dirección:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=5)
            address_entry = tk.Entry(form_frame, width=30)
            address_entry.insert(0, contact["address"])
            address_entry.grid(row=7, column=0, sticky=tk.W, pady=5)
            
            tk.Label(form_frame, text="Cumpleaños (DD/MM/YYYY):", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=5)
            birthday_entry = tk.Entry(form_frame, width=30)
            birthday_entry.insert(0, contact.get("birthday", ""))
            birthday_entry.grid(row=9, column=0, sticky=tk.W, pady=5)
            
            def save_changes():
                name = name_entry.get().strip()
                birthday = birthday_entry.get().strip()
                if not name:
                    messagebox.showerror("Error", "El nombre es obligatorio.")
                    return
                if not self.validate_date(birthday):
                    messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY o déjelo vacío.")
                    return
                self.agenda[index] = {
                    "name": name,
                    "phone": phone_entry.get().strip(),
                    "email": email_entry.get().strip(),
                    "address": address_entry.get().strip(),
                    "birthday": birthday
                }
                self.save_agenda()
                self.update_table()
                messagebox.showinfo("Éxito", f"Contacto '{name}' actualizado correctamente.")
                window.destroy()
            
            # Botones con atajos de teclado
            button_frame = tk.Frame(window)
            button_frame.pack(pady=10)
            
            save_btn = tk.Button(button_frame, text="Guardar", command=save_changes, 
                                bg='#4CAF50', fg='white', width=10)
            save_btn.pack(side=tk.LEFT, padx=5)
            save_btn.bind('<Return>', lambda event: save_changes())
            
            cancel_btn = tk.Button(button_frame, text="Cancelar", command=window.destroy, 
                                  bg='#f44336', fg='white', width=10)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            cancel_btn.bind('<Escape>', lambda event: window.destroy())
            
            # Permitir que Enter active el botón de guardar
            window.bind('<Return>', lambda event: save_changes())
            # Permitir que Esc cierre la ventana
            window.bind('<Escape>', lambda event: window.destroy())
    
    def delete_contact_by_index(self, index):
        """Elimina un contacto por su índice."""
        if index < len(self.agenda):
            contact = self.agenda[index]
            if messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Estás seguro de que deseas eliminar a '{contact['name']}'?"):
                self.agenda.pop(index)
                self.save_agenda()
                self.update_table()
                messagebox.showinfo("Éxito", f"Contacto '{contact['name']}' eliminado correctamente.")
    
    def update_table(self, contacts: Optional[List[Dict]] = None) -> None:
        """Actualiza la tabla con los contactos proporcionados o todos los contactos."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        contacts = contacts or self.agenda
        for contact in contacts:
            if contact is None:
                continue
            self.tree.insert("", tk.END, values=(
                contact.get("name", ""), 
                contact.get("phone", ""), 
                contact.get("email", ""), 
                contact.get("address", ""), 
                contact.get("birthday", "")
            ))
    
    def validate_date(self, date: str) -> bool:
        """Valida que la fecha tenga el formato DD/MM/YYYY o esté vacía."""
        if not date:
            return True
        pattern = r"^\d{2}/\d{2}/\d{4}$"
        return bool(re.match(pattern, date))
    
    def add_contact_window(self) -> None:
        """Abre una ventana para agregar un contacto."""
        window = tk.Toplevel(self.root)
        window.title("Agregar Contacto")
        window.geometry("450x400")
        window.transient(self.root)
        window.grab_set()
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")
        
        # Formulario
        form_frame = tk.Frame(window, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame, text="Nombre *:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Teléfono:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        phone_entry = tk.Entry(form_frame, width=30)
        phone_entry.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Correo:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        email_entry = tk.Entry(form_frame, width=30)
        email_entry.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Dirección:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=5)
        address_entry = tk.Entry(form_frame, width=30)
        address_entry.grid(row=7, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Cumpleaños (DD/MM/YYYY):", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=5)
        birthday_entry = tk.Entry(form_frame, width=30)
        birthday_entry.grid(row=9, column=0, sticky=tk.W, pady=5)
        
        def save_contact():
            name = name_entry.get().strip()
            birthday = birthday_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "El nombre es obligatorio.")
                return
            if not self.validate_date(birthday):
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY o déjelo vacío.")
                return
            contact = {
                "name": name,
                "phone": phone_entry.get().strip(),
                "email": email_entry.get().strip(),
                "address": address_entry.get().strip(),
                "birthday": birthday
            }
            self.agenda.append(contact)
            self.save_agenda()
            self.update_table()
            messagebox.showinfo("Éxito", f"Contacto '{name}' agregado correctamente.")
            window.destroy()
        
        # Botones con atajos de teclado
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        save_btn = tk.Button(button_frame, text="Guardar", command=save_contact, 
                            bg='#4CAF50', fg='white', width=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        save_btn.bind('<Return>', lambda event: save_contact())
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=window.destroy, 
                              bg='#f44336', fg='white', width=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn.bind('<Escape>', lambda event: window.destroy())
        
        # Permitir que Enter active el botón de guardar
        window.bind('<Return>', lambda event: save_contact())
        # Permitir que Esc cierre la ventana
        window.bind('<Escape>', lambda event: window.destroy())
    
    def search_contact_window(self) -> None:
        """Abre una ventana para buscar contactos."""
        window = tk.Toplevel(self.root)
        window.title("Buscar Contacto")
        window.geometry("400x150")
        window.transient(self.root)
        window.grab_set()
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")
        
        tk.Label(window, text="Nombre a buscar:").pack(pady=10)
        search_entry = tk.Entry(window, width=30)
        search_entry.pack(pady=5)
        
        def search():
            search_term = search_entry.get().strip().lower()
            if not search_term:
                self.update_table()
                return
            found_contacts = [
                contact for contact in self.agenda if search_term in contact["name"].lower()
            ]
            self.update_table(found_contacts)
            if not found_contacts:
                messagebox.showinfo("Resultado", "No se encontraron contactos.")
            window.destroy()
        
        # Botones con atajos de teclado
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        search_btn = tk.Button(button_frame, text="Buscar", command=search)
        search_btn.pack(side=tk.LEFT, padx=5)
        search_btn.bind('<Return>', lambda event: search())
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn.bind('<Escape>', lambda event: window.destroy())
        
        # Permitir que Enter active el botón de buscar
        window.bind('<Return>', lambda event: search())
        # Permitir que Esc cierre la ventana
        window.bind('<Escape>', lambda event: window.destroy())
    
    def edit_contact_window(self) -> None:
        """Abre una ventana para editar un contacto seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un contacto para editar.")
            return
        index = self.tree.index(selected[0])
        contact = self.agenda[index]
        window = tk.Toplevel(self.root)
        window.title("Editar Contacto")
        window.geometry("450x400")
        window.transient(self.root)
        window.grab_set()
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")
        
        # Formulario
        form_frame = tk.Frame(window, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame, text="Nombre *:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.insert(0, contact["name"])
        name_entry.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Teléfono:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        phone_entry = tk.Entry(form_frame, width=30)
        phone_entry.insert(0, contact["phone"])
        phone_entry.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Correo:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        email_entry = tk.Entry(form_frame, width=30)
        email_entry.insert(0, contact["email"])
        email_entry.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Dirección:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=5)
        address_entry = tk.Entry(form_frame, width=30)
        address_entry.insert(0, contact["address"])
        address_entry.grid(row=7, column=0, sticky=tk.W, pady=5)
        
        tk.Label(form_frame, text="Cumpleaños (DD/MM/YYYY):", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=5)
        birthday_entry = tk.Entry(form_frame, width=30)
        birthday_entry.insert(0, contact.get("birthday", ""))
        birthday_entry.grid(row=9, column=0, sticky=tk.W, pady=5)
        
        def save_changes():
            name = name_entry.get().strip()
            birthday = birthday_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "El nombre es obligatorio.")
                return
            if not self.validate_date(birthday):
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY o déjelo vacío.")
                return
            self.agenda[index] = {
                "name": name,
                "phone": phone_entry.get().strip(),
                "email": email_entry.get().strip(),
                "address": address_entry.get().strip(),
                "birthday": birthday
            }
            self.save_agenda()
            self.update_table()
            messagebox.showinfo("Éxito", f"Contacto '{name}' actualizado correctamente.")
            window.destroy()
        
        # Botones con atajos de teclado
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        save_btn = tk.Button(button_frame, text="Guardar", command=save_changes, 
                            bg='#4CAF50', fg='white', width=10)
        save_btn.pack(side=tk.LEFT, padx=5)
        save_btn.bind('<Return>', lambda event: save_changes())
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=window.destroy, 
                              bg='#f44336', fg='white', width=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn.bind('<Escape>', lambda event: window.destroy())
        
        # Permitir que Enter active el botón de guardar
        window.bind('<Return>', lambda event: save_changes())
        # Permitir que Esc cierre la ventana
        window.bind('<Escape>', lambda event: window.destroy())
    
    def delete_contact(self) -> None:
        """Elimina un contacto seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un contacto para eliminar.")
            return
        index = self.tree.index(selected[0])
        contact = self.agenda.pop(index)
        self.save_agenda()
        self.update_table()
        messagebox.showinfo("Éxito", f"Contacto '{contact['name']}' eliminado correctamente.")
    
    def config_window(self) -> None:
        """Abre una ventana para actualizar la contraseña."""
        window = tk.Toplevel(self.root)
        window.title("Configuración - Cambiar Contraseña")
        window.geometry("400x250")
        window.transient(self.root)
        window.grab_set()
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")
        
        tk.Label(window, text="Cambiar Contraseña", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(window, text="Nueva contraseña:").pack(pady=5)
        new_password_entry = tk.Entry(window, show="*", width=30)
        new_password_entry.pack(pady=5)
        
        tk.Label(window, text="Confirmar nueva contraseña:").pack(pady=5)
        confirm_password_entry = tk.Entry(window, show="*", width=30)
        confirm_password_entry.pack(pady=5)
        
        def change_password():
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()
            if not new_password:
                messagebox.showerror("Error", "La contraseña no puede estar vacía.")
                return
            if new_password != confirm_password:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return
            # Re-encriptar los datos con la nueva contraseña
            old_password = self.password
            self.password = new_password
            try:
                self.save_agenda()
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
                window.destroy()
            except Exception as e:
                self.password = old_password  # Restaurar contraseña anterior si falla
                messagebox.showerror("Error", f"No se pudo actualizar la contraseña: {str(e)}")
        
        # Botones con atajos de teclado
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        save_btn = tk.Button(button_frame, text="Guardar", command=change_password, 
                            bg='#4CAF50', fg='white', width=15)
        save_btn.pack(side=tk.LEFT, padx=5)
        save_btn.bind('<Return>', lambda event: change_password())
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=window.destroy, 
                              bg='#f44336', fg='white', width=15)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn.bind('<Escape>', lambda event: window.destroy())
        
        # Permitir que Enter active el botón de guardar
        window.bind('<Return>', lambda event: change_password())
        # Permitir que Esc cierre la ventana
        window.bind('<Escape>', lambda event: window.destroy())
    
    def export_menu(self):
        """Muestra menú de opciones de exportación."""
        menu_window = tk.Toplevel(self.root)
        menu_window.title("Exportar Contactos")
        menu_window.geometry("300x200")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        # Centrar ventana
        menu_window.update_idletasks()
        x = (menu_window.winfo_screenwidth() // 2) - (menu_window.winfo_width() // 2)
        y = (menu_window.winfo_screenheight() // 2) - (menu_window.winfo_height() // 2)
        menu_window.geometry(f"+{x}+{y}")
        
        tk.Label(menu_window, text="Seleccionar opción de exportación:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Botones de exportación
        tk.Button(menu_window, text="Exportar Contacto Seleccionado", 
                 command=self.export_selected_to_pdf, width=30).pack(pady=5)
        
        tk.Button(menu_window, text="Exportar Todos los Contactos", 
                 command=self.export_all_to_pdf, width=30).pack(pady=5)
        
        # Eliminar esta línea ya que no existe la función
        # tk.Button(menu_window, text="Exportar Contacto Individual", 
        #          command=self.export_individual_contact, width=30).pack(pady=5)
        
        tk.Button(menu_window, text="Cancelar", command=menu_window.destroy, 
                 width=15).pack(pady=10)
    
    def export_selected_to_pdf(self):
        """Exporta los contactos seleccionados a PDF."""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showerror("Error", "Seleccione al menos un contacto para exportar.")
                return
                
            # Obtener contactos seleccionados
            selected_contacts = []
            for item in selected:
                index = self.tree.index(item)
                selected_contacts.append(self.agenda[index])
            
            success, message = export_selected_to_pdf(selected_contacts)
            if success:
                messagebox.showinfo("Éxito", message)
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron exportar los contactos: {str(e)}")
    
    def export_all_to_pdf(self):
        """Exporta todos los contactos a PDF."""
        try:
            if not self.agenda:
                messagebox.showinfo("Información", "No hay contactos para exportar.")
                return
            
            success, message = export_all_to_pdf(self.agenda)
            if success:
                messagebox.showinfo("Éxito", message)
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar la agenda: {str(e)}")
    
    def export_individual_contact(self):
        """Exporta un contacto individual seleccionado."""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showerror("Error", "Seleccione un contacto para exportar.")
                return
            
            index = self.tree.index(selected[0])
            contact = self.agenda[index]
            success, message = export_contact_to_pdf(contact)
            if success:
                messagebox.showinfo("Éxito", message)
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el contacto: {str(e)}")
    
    def create_backup(self):
        """Crea una copia de seguridad de los datos."""
        if os.path.exists(AGENDA_FILE):
            backup_file = AGENDA_FILE + ".backup"
            try:
                with open(AGENDA_FILE, 'rb') as f:
                    data = f.read()
                with open(backup_file, 'wb') as f:
                    f.write(data)
                print("Backup creado exitosamente")
                messagebox.showinfo("Éxito", "Backup creado exitosamente")
            except Exception as e:
                print(f"Error creando backup: {e}")
                messagebox.showerror("Error", f"Error creando backup: {str(e)}")

def main():
    """Inicia la aplicación."""
    print("Arrancando app...")
    root = tk.Tk()
    app = AgendaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()