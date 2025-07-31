# Agenda Tradicional Encriptada

Aplicación de gestión de contactos con encriptación de datos.

## Características

- Gestión de contactos (agregar, buscar, editar, eliminar)
- Encriptación de datos sensibles
- Interfaz gráfica intuitiva
- Seguridad mediante contraseña

## Requisitos

- Python 3.6+
- Tkinter (incluido en la mayoría de instalaciones de Python)

## Instalación

### Para usuarios finales:

1. Descarga el archivo ejecutable `AgendaEncriptada.exe` (Windows)
2. Ejecuta el archivo

### Para desarrolladores:

```bash
# Clona el repositorio
git clone <url-del-repositorio>
cd agenda-proyecto

# Crea y activa entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Instala dependencias
pip install -r requirements.txt

# Ejecuta la aplicación
python agenda.py