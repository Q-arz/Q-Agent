import json
import os


def transform_from_definition(json_path: str):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ No se pudo leer el archivo JSON: {e}")
        return

    base_url = data["base_url"]
    mod_name = data["name"]
    endpoints = data["endpoints"]

    mod_path = f"modules/{mod_name}"
    os.makedirs(mod_path, exist_ok=True)

    CMD_TEMPLATE = '        {{"trigger": "{cmd}", "function": {fn}}},'
    FN_TEMPLATE = """
def {fn}(command, router):
    r = requests.{method}(f"{{BASE_URL}}/{path}")
    return r.text
"""

    commands = []
    functions = []

    for ep in endpoints:
        path = ep["path"]
        method = ep.get("method", "get").lower()
        command = ep.get("command", f"llama {mod_name} {path}")
        fn = command.replace(" ", "_").replace("/", "_").replace("-", "_") + "_handler"

        commands.append(CMD_TEMPLATE.format(cmd=command, fn=fn))
        functions.append(FN_TEMPLATE.format(fn=fn, method=method, path=path))

    TEMPLATE = f"""import requests

BASE_URL = "{base_url}"

def get_commands():
    return [
{chr(10).join(commands)}
    ]

{chr(10).join(functions)}
"""
    with open(f"{mod_path}/module.py", "w", encoding="utf-8") as f:
        f.write(TEMPLATE)

    print(
        f"[Q•AI] ✅ MCP '{mod_name}' transformado en módulo con comandos definidos por el usuario."
    )
