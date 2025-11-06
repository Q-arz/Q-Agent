import requests
import zipfile
import io
import os


# 🔒 Protege contra rutas peligrosas
def is_safe_path(path: str, base: str = "modules") -> bool:
    full_path = os.path.abspath(os.path.join(base, path))
    return full_path.startswith(os.path.abspath(base))


# 🚀 Instalador de módulos desde un ZIP remoto
def install_module_from_zip(url: str, name: str):
    print(f"[Q•AI] 📦 Descargando módulo: {name}")
    try:
        r = requests.get(url)
        r.raise_for_status()
    except Exception as e:
        print(f"[Q•AI] ❌ Error al descargar ZIP: {e}")
        return

    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
    except Exception as e:
        print(f"[Q•AI] ❌ ZIP inválido: {e}")
        return

    target_path = os.path.join("modules", name)
    os.makedirs(target_path, exist_ok=True)

    for file_info in z.infolist():
        filename = file_info.filename

        # ⚠️ Protección contra rutas fuera del módulo
        if ".." in filename or filename.startswith("/") or "\\" in filename:
            print(f"[Q•AI] ⚠️ Ruta peligrosa ignorada: {filename}")
            continue

        # ✅ Permitir solo archivos seguros
        if not filename.endswith((".py", ".json", ".md", ".txt")):
            print(f"[Q•AI] ⛔ Archivo no permitido: {filename}")
            continue

        destination = os.path.join(target_path, filename)
        if not is_safe_path(destination, "modules"):
            print(f"[Q•AI] ⚠️ Extracción bloqueada por seguridad: {filename}")
            continue

        z.extract(file_info, path=target_path)
        print(f"[Q•AI] ✅ Archivo instalado: {filename}")

    print(f"[Q•AI] ✅ Módulo instalado: {name}")
