from store.downloader import install_module_from_zip
from store.mcp_importer import transform_from_definition
import requests
import tempfile

STORE = {
    "organizer": "https://tudominio.com/modules/organizer.zip",
    "social": "https://tudominio.com/modules/social.zip",
}


def handle(command, router):
    if command.startswith("transforma mcp desde"):
        path = command.split("transforma mcp desde", 1)[1].strip()
        transform_from_definition(path)
        return f"🧠 MCP transformado desde {path}"
    if command.startswith("instala módulo"):
        return instalar_modulo(command)
    return None


def conectar_mcp_estandar(base_url):
    try:
        r = requests.get(f"{base_url.rstrip('/')}/qai-module.json")
        r.raise_for_status()

        temp_path = tempfile.mktemp(suffix=".json")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(r.text)

        transform_from_definition(temp_path)
        return f"✅ MCP estándar conectado desde {base_url}"

    except Exception as e:
        return f"❌ Error al conectar con MCP estándar: {e}"


def instalar_modulo(command: str):
    try:
        partes = command.split("instala módulo", 1)[1].strip().split("desde")
        nombre = partes[0].strip().lower()

        if len(partes) == 2:
            url = partes[1].strip()
        else:
            url = STORE.get(nombre)
            if not url:
                return f"❌ No tengo la URL de descarga para el módulo: {nombre}"

        install_module_from_zip(url, nombre)
        return f"📦 Módulo {nombre} instalado."
    except Exception as e:
        return f"❌ Error al instalar módulo: {e}"
