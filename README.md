
# 🔐 ContactVault

**ContactVault** es una aplicación de gestión de contactos personales con cifrado de datos, ideal para mantener tu agenda privada, segura y accesible.

🔐 Porque hasta los números de tu suegra merecen privacidad.

---

## ✨ Características

- ✅ **Agregar, buscar, editar y eliminar contactos**
- 📄 **Exportación de contactos a PDF**
- 🔐 **Encriptación de datos sensibles con contraseña maestra**
- 🖼️ **Interfaz gráfica amigable (Tkinter)**
- 💾 **Backups automáticos de tus datos**
- ⚙️ Totalmente offline y sin necesidad de internet

---

## 💻 Entorno de desarrollo

Proyecto creado y probado en:

- 🐍 **Python 3.11+**
- 🧪 **openSUSE Tumbleweed**
- 💻 Laptop: **Victus16 by HP**
- GUI: **Tkinter**
- Cifrado con [`cryptography`](https://pypi.org/project/cryptography/)

---

## 🗂️ Estructura del proyecto

```
contactvault/
├── main.py                 # Archivo principal (contiene la clase AgendaApp)
├── export_pdf.py           # Funciones de exportación a PDF
├── backup_manager.py       # Funciones de backup
├── utils.py                # Funciones auxiliares
├── requirements.txt        # Dependencias
├── README.md               # Documentación
└── agenda.json.enc         # Archivo de datos (opcional)
```

---

## ☁️ Copias de seguridad

- Los datos se almacenan encriptados en `agenda.json.enc`.
- Se generan backups automáticos con extensión `.backup`.

---

## 🚀 Instalación

### 🔰 Para usuarios finales (Windows):

📦 *Próximamente disponible:* instalador `.exe` para que tus contactos puedan usarla sin complicaciones.

1. Descargá el instalador desde la sección de **Releases**
2. Ejecutalo normalmente

### 👨‍💻 Para desarrolladores:

```bash
git clone <url-del-repositorio>
cd contactvault

python -m venv venv
source venv/bin/activate      # Linux / MacOS
# o venv\Scripts\activate   # Windows

pip install -r requirements.txt

python main.py
```

---

## 🧾 Licencia

Este proyecto está bajo la **Licencia MIT**.  
Podés usarlo, modificarlo, compartirlo y mejorarlo libremente.

Ver el archivo [`LICENSE`](./LICENSE) para más información.

---

## 📬 Contacto

Desarrollado por **Nicolás Butterfield**  
📧 nicobutter@gmail.com

¡Se aceptan ideas, sugerencias, mejoras o memes!

---

## 🛣️ Roadmap

- [ ] Generar instalador `.exe` para Windows
- [ ] Mejoras visuales a la interfaz
- [ ] Buscador con filtros avanzados
- [ ] Sincronización entre dispositivos (opcional)
