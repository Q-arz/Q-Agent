import json
import os
from core.ui.popout import PopoutService


def open_module_ui(manifest: dict):
    base = manifest.get("_module_path")
    if not base:
        return "[Q•Agent] Module path not available."
    ui_json = os.path.join(base, "ui.json")
    if not os.path.exists(ui_json):
        return "[Q•Agent] No UI schema found for this module."
    try:
        with open(ui_json, "r", encoding="utf-8") as f:
            schema = json.load(f)
        PopoutService.instance().show_schema(schema.get("title") or manifest.get("name") or "Module UI", schema)
        return "[Q•Agent] Module UI opened."
    except Exception as e:
        return f"[Q•Agent] Failed to open UI: {e}"


