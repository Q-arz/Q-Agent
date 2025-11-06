import os
import zipfile
from pathlib import Path

try:
    import requests
except Exception:
    requests = None


DEFAULT_VOSK_MODELS = {
    "es": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip",
    "en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
}


def get_vosk_model_dir(language: str) -> Path:
    base = Path(__file__).resolve().parents[2] / "core" / "interfaces" / "voice" / "vosk"
    return base / f"model_{language}"


def ensure_vosk_model(language: str, url: str | None = None) -> str:
    lang = (language or "es").split("-")[0]
    dest = get_vosk_model_dir(lang)
    if dest.exists() and any(dest.iterdir()):
        return f"[Q•AI] Vosk model present: {dest}"
    if requests is None:
        return "[Q•AI] 'requests' not available. Cannot download model."
    model_url = url or DEFAULT_VOSK_MODELS.get(lang)
    if not model_url:
        return f"[Q•AI] No default model URL for language '{lang}'."
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp_zip = dest.parent / f"{dest.name}.zip"
    try:
        with requests.get(model_url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(tmp_zip, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        with zipfile.ZipFile(tmp_zip, "r") as zf:
            # Extract into temp dir then move if needed
            zf.extractall(dest.parent)
        # find extracted folder if name doesn't match
        if not dest.exists():
            # pick first folder containing 'model' or 'vosk'
            for p in dest.parent.iterdir():
                if p.is_dir() and ("vosk" in p.name or "model" in p.name):
                    p.rename(dest)
                    break
        return f"[Q•AI] Vosk model ready at: {dest}"
    except Exception as e:
        return f"[Q•AI] Failed to download/extract model: {e}"
    finally:
        try:
            if tmp_zip.exists():
                tmp_zip.unlink()
        except Exception:
            pass



