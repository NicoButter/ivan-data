import os
import datetime

def create_backup(agenda_file):
    """Crea una copia de seguridad de los datos."""
    if os.path.exists(agenda_file):
        backup_file = agenda_file + ".backup"
        try:
            with open(agenda_file, 'rb') as f:
                data = f.read()
            with open(backup_file, 'wb') as f:
                f.write(data)
            return True, "Backup creado exitosamente"
        except Exception as e:
            return False, f"Error creando backup: {e}"
    return False, "Archivo no encontrado"