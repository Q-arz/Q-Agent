from core.auto import board
from datetime import datetime
from core.logs.logger import setup_logger
logger = setup_logger("qai.suggester")
import json
from pathlib import Path


def _load_config():
    try:
        cfg_path = Path(__file__).resolve().parents[1] / "config" / "qai_config.json"
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def sugerir_acciones():
    tareas = board.load_tasks()
    cfg = _load_config()
    ahora = datetime.now()
    propuestas = []

    # reglas activables por config
    rules_cfg = ((cfg.get("suggester", {}) or {}).get("rules", {}) or {})
    daily_limit = (cfg.get("suggester", {}) or {}).get("daily_limit", 5)

    titulos = [t.get("title", "").lower() for t in tareas]

    def r_video():
        if any("video" in t for t in titulos):
            return None
        return {"type": "publicar", "title": "Crear nuevo video sobre", "prioridad": "media", "target": "x", "source": "suggester"}

    def r_reel():
        if any("reel" in t for t in titulos):
            return None
        return {"type": "publicar", "title": "Subir reel simbólico de bienvenida a Q•zar", "prioridad": "alta", "target": "discord", "source": "suggester"}

    def r_responder():
        if any("comentario" in t or "responder" in t for t in titulos):
            return None
        return {"type": "responder", "title": "Responder comentarios recientes de TikTok", "prioridad": "alta", "source": "suggester"}

    def r_articulo():
        if any("artículo" in t or "medium" in t for t in titulos):
            return None
        return {"type": "publicar", "title": "Publicar artículo breve sobre coherencia simbólica", "prioridad": "media", "target": "medium", "source": "suggester"}

    rules = [
        ("video", r_video),
        ("reel", r_reel),
        ("responder", r_responder),
        ("articulo", r_articulo),
    ]

    count_added_today = 0
    for key, rule in rules:
        if rules_cfg and not rules_cfg.get(key, True):
            continue
        if count_added_today >= daily_limit:
            break
        p = rule()
        if not p:
            continue
        if not board.was_already_done(p["title"], p["type"]):
            logger.info(f"[Sugerencia] 💡 {p['title']}")
            board.add_task(p)
            count_added_today += 1
        else:
            logger.info(f"[Sugerencia] (Ignorada, ya fue hecha): {p['title']}")
