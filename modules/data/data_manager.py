import os
from datetime import datetime

try:
    from fpdf import FPDF

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


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


def append_to_file(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now().isoformat()}]\n{content}\n")
    return f"✅ Contenido añadido a: {path}"


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
