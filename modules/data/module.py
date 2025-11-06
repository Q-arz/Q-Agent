import os
from datetime import datetime

try:
    from fpdf import FPDF

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def get_commands():
    return [
        {"trigger": "crear carpeta", "function": handle_create_folder},
        {"trigger": "crear archivo", "function": handle_create_file},
        {"trigger": "leer archivo", "function": handle_read_file},
        {"trigger": "listar archivos", "function": handle_list_files},
        {"trigger": "generar pdf", "function": handle_generate_pdf},
    ]


def handle_create_folder(command, router):
    path = extraer_path(command, "crear carpeta")
    return create_folder(path)


def handle_create_file(command, router):
    path = extraer_path(command, "crear archivo")
    return create_file(path, "Archivo generado por Q•AI.")


def handle_read_file(command, router):
    path = extraer_path(command, "leer archivo")
    return read_file(path)


def handle_list_files(command, router):
    path = extraer_path(command, "listar archivos")
    return "\n".join(list_files_in_folder(path))


def handle_generate_pdf(command, router):
    path = extraer_path(command, "generar pdf")
    return generate_pdf(path, "Contenido generado simbólicamente.")


# 🧠 Funciones internas


def extraer_path(command, clave):
    return command.split(clave, 1)[-1].strip()


def create_folder(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return f"📁 Carpeta creada (o ya existente): {path}"


def create_file(path: str, content: str = "") -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"📄 Archivo creado en: {path}"


def read_file(path: str) -> str:
    if not os.path.exists(path):
        return "❌ Archivo no encontrado."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_files_in_folder(path: str) -> list:
    if not os.path.exists(path):
        return []
    return os.listdir(path)


def generate_pdf(path: str, content: str) -> str:
    if not PDF_AVAILABLE:
        return "❌ No se pudo generar PDF. Instala `fpdf` con pip install fpdf."
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.splitlines():
        pdf.cell(200, 10, txt=line, ln=1, align="L")
    pdf.output(path)
    return f"📄 PDF generado en: {path}"
