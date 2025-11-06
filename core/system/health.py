def check_dependencies(config: dict) -> dict:
    """Return a possibly adjusted config after dependency checks.
    - If voice deps missing, degrade to text mode.
    - If chosen ASR engine missing, switch to available or text.
    """
    cfg = dict(config or {})
    asr = (cfg.get("asr", {}) or {})
    engine = asr.get("engine", cfg.get("voz_engine", "whisper"))

    whisper_ok = _has_module("whisper") and _has_module("pyaudio") and _has_module("pygame")
    vosk_ok = _has_module("vosk") and _has_module("pyaudio") and _has_module("pygame")

    desired_ok = (engine == "whisper" and whisper_ok) or (engine == "vosk" and vosk_ok)
    if not desired_ok:
        if whisper_ok:
            asr["engine"] = "whisper"
            cfg["asr"] = asr
            cfg["modo"] = "voz"
        elif vosk_ok:
            asr["engine"] = "vosk"
            cfg["asr"] = asr
            cfg["modo"] = "voz"
        else:
            cfg["modo"] = "texto"
    return cfg


def _has_module(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False



