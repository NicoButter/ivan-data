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

class AgendaApp:
    def __init__(self, root: tk.Tk):
        """Inicializa la aplicación de agenda."""
        self.root = root
        self.root.title("Agenda Tradicional (Encriptada)")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Variables de paginación
        self.current_page = 1
        self.items_per_page = 20  # Cambia este valor según necesites
        
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
            
            # Botones
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(pady=20)
            
            tk.Button(button_frame, text="ACEPTAR", command=submit_auth, 
                     width=10, height=1, bg='#4CAF50', fg='white',
                     font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="CANCELAR", command=cancel_auth, 
                     width=10, height=1, bg='#f44336', fg='white',
                     font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
            
            # Manejar cierre de ventana
            def on_closing():
                self.password = None
                auth_window.destroy()
            
            auth_window.protocol("WM_DELETE_WINDOW", on_closing)
            
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
        
        # Botones
        buttons_config = [
            ("Agregar Contacto", self.add_contact_window),
            ("Buscar Contacto", self.search_contact_window),
            ("Editar Contacto", self.edit_contact_window),
            ("Eliminar Contacto", self.delete_contact),
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
        
        # Marco para paginación
        pagination_frame = tk.Frame(self.root, bg='white')
        pagination_frame.pack(pady=10)
        
        # Botones de paginación
        self.prev_button = tk.Button(pagination_frame, text="Anterior", command=self.previous_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.page_label = tk.Label(pagination_frame, text="", bg='white')
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.next_button = tk.Button(pagination_frame, text="Siguiente", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Actualizar tabla
        self.update_table_paginated()
    
    def get_paginated_contacts(self) -> List[Dict]:
        """Obtiene los contactos para la página actual."""
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        return self.agenda[start_index:end_index]
    
    def update_table_paginated(self) -> None:
        """Actualiza la tabla con los contactos de la página actual."""
        # Limpiar tabla existente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener contactos de la página actual
        page_contacts = self.get_paginated_contacts()
        
        # Insertar contactos
        for contact in page_contacts:
            if contact is None:
                continue
            self.tree.insert("", tk.END, values=(
                contact.get("name", ""), 
                contact.get("phone", ""), 
                contact.get("email", ""), 
                contact.get("address", ""), 
                contact.get("birthday", "")
            ))
        
        # Actualizar etiqueta de página
        total_pages = (len(self.agenda) + self.items_per_page - 1) // self.items_per_page
        self.page_label.config(text=f"Página {self.current_page} de {total_pages}")
        
        # Habilitar/deshabilitar botones
        self.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED)
    
    def previous_page(self) -> None:
        """Va a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table_paginated()
    
    def next_page(self) -> None:
        """Va a la página siguiente."""
        total_pages = (len(self.agenda) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_table_paginated()
    
    def update_table(self, contacts: Optional[List[Dict]] = None) -> None:
        """Actualiza la tabla con los contactos proporcionados o todos los contactos."""
        # Esta función ahora se usa solo para operaciones que no requieren paginación
        # Para paginación, usamos update_table_paginated()
        pass
    
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
            self.update_table_paginated()  # Actualizar tabla paginada
            messagebox.showinfo("Éxito", f"Contacto '{name}' agregado correctamente.")
            window.destroy()
        
        # Botones
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Guardar", command=save_contact, 
                 bg='#4CAF50', fg='white', width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancelar", command=window.destroy, 
                 bg='#f44336', fg='white', width=10).pack(side=tk.LEFT, padx=5)
    
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
                self.update_table_paginated()
                return
            
            # Buscar en todos los contactos (no paginados)
            found_contacts = [
                contact for contact in self.agenda if search_term in contact["name"].lower()
            ]
            
            # Mostrar resultados en la primera página
            self.agenda = found_contacts
            self.current_page = 1
            self.update_table_paginated()
            
            if not found_contacts:
                messagebox.showinfo("Resultado", "No se encontraron contactos.")
            
            window.destroy()
        
        tk.Button(window, text="Buscar", command=search).pack(pady=10)
        tk.Button(window, text="Cancelar", command=window.destroy).pack(pady=5)
    
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
            self.update_table_paginated()  # Actualizar tabla paginada
            messagebox.showinfo("Éxito", f"Contacto '{name}' actualizado correctamente.")
            window.destroy()
        
        # Botones
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Guardar", command=save_changes, 
                 bg='#4CAF50', fg='white', width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancelar", command=window.destroy, 
                 bg='#f44336', fg='white', width=10).pack(side=tk.LEFT, padx=5)
    
    def delete_contact(self) -> None:
        """Elimina un contacto seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un contacto para eliminar.")
            return
        index = self.tree.index(selected[0])
        contact = self.agenda.pop(index)
        self.save_agenda()
        self.update_table_paginated()  # Actualizar tabla paginada
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
        
        tk.Button(window, text="Guardar", command=change_password, 
                 bg='#4CAF50', fg='white', width=15).pack(pady=10)
        tk.Button(window, text="Cancelar", command=window.destroy, 
                 bg='#f44336', fg='white', width=15).pack(pady=5)
    
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
            except Exception as e:
                print(f"Error creando backup: {e}")

def main():
    """Inicia la aplicación."""
    print("Arrancando app...")
    root = tk.Tk()
    app = AgendaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()