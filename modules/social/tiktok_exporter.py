import os
from datetime import datetime
from core.auto.board import add_task

EXPORT_PATH = os.path.join("logs", "tiktok_exports")
os.makedirs(EXPORT_PATH, exist_ok=True)


def export_tiktok_post(content: dict):
    """
    content = {
        "title": "La coherencia no es una opción",
        "hook": "¿Sabías que la realidad no es caótica?",
        "body": "Según la Ley de Coherencia Fundamental...",
        "hashtags": ["#Coherencia", "#Simbolismo", "#QAI"],
        "music": "sonido_inspirador.mp3",  # opcional
        "video_path": "placeholder.mp4"    # opcional
    }
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(EXPORT_PATH, f"tiktok_{timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Título: {content.get('title', '')}\n")
        f.write(f"Hook: {content.get('hook', '')}\n\n")
        f.write(f"Descripción:\n{content.get('body', '')}\n\n")
        f.write("Hashtags: " + " ".join(content.get("hashtags", [])) + "\n")
        f.write(f"Música sugerida: {content.get('music', 'ninguna')}\n")
        f.write(f"Video asociado: {content.get('video_path', 'placeholder.mp4')}\n")

    print(f"[TikTok] Publicación preparada: {filename}")

    task_entry = {
        "type": "tiktok",
        "title": content.get("title", "Publicación de TikTok"),
        "hook": content.get("hook", ""),
        "video": content.get("video_path", "placeholder.mp4"),
        "hashtags": content.get("hashtags", []),
        "timestamp": timestamp,
        "file": filename,
    }
    add_task(task_entry)
