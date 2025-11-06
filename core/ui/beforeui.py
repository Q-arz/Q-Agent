import json
from pathlib import Path
from core.ui.popout import PopoutService


def _load_config():
    cfg_path = Path(__file__).resolve().parents[2] / "core" / "config" / "qai_config.json"
    try:
        return cfg_path, json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return cfg_path, {}


def open_before_ui(router):
    cfg_path, cfg = _load_config()
    lang = cfg.get("language", "es")
    asr = (cfg.get("asr", {}) or {})
    tts = (cfg.get("tts", {}) or {})

    schema = {
        "title": "Q•Agent Setup",
        "views": [
            {
                "type": "form",
                "title": "Language & Voice",
                "fields": [
                    {"name": "language", "label": "Language", "value": lang},
                    {"name": "asr_engine", "label": "ASR Engine (whisper/vosk)", "value": asr.get("engine", "whisper")},
                    {"name": "asr_language", "label": "ASR Language", "value": asr.get("language", lang)},
                    {"name": "tts_rate", "label": "TTS Rate", "value": str(tts.get("rate", 180))}
                ],
                "submit": {"label": "Save", "command": "setup apply {language} {asr_engine} {asr_language} {tts_rate}"}
            }
        ]
    }
    PopoutService.instance().show_schema("Q•Agent Setup", schema)


def apply_setup(router, language: str, asr_engine: str, asr_language: str, tts_rate: str):
    cfg_path, cfg = _load_config()
    cfg["language"] = language
    cfg.setdefault("asr", {})
    cfg["asr"]["engine"] = asr_engine
    cfg["asr"]["language"] = asr_language
    cfg.setdefault("tts", {})
    try:
        cfg["tts"]["rate"] = int(tts_rate)
    except Exception:
        pass
    cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    # reflect at runtime
    router.config.update(cfg)
    try:
        router.io.set_language(language)
    except Exception:
        pass
    return "[Q•Agent] Settings saved."



