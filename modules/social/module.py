from modules.social.social import post_to_network
from modules.social.tiktok_exporter import export_tiktok_post
from core.auto.board import was_already_done


def get_manifest():
    return {
        "id": "qai.modules.social",
        "name": "Social Module",
        "version": "0.1.0",
        "description": "Post to social networks and prepare TikTok content.",
        "permissions": ["network.request"],
        "commands": [
            {
                "trigger": "post ",
                "description": "Post text to configured social networks.",
                "args": [{"name": "text", "type": "string", "required": True}],
                "synonyms": ["publish", "share", "publicar", "compartir"],
                "handler": handle_post,
            },
            {
                "trigger": "prepare_tiktok ",
                "description": "Create a TikTok post package from a phrase.",
                "args": [{"name": "phrase", "type": "string", "required": True}],
                "synonyms": ["tiktok", "prep_tiktok", "preparar_tiktok"],
                "handler": handle_prepare_tiktok,
            },
        ],
        "mcp": {
            "capabilities": [],
            "resources": [],
        },
    }


def get_commands():
    return [
        {"trigger": "post ", "function": handle_post},
        {"trigger": "prepare_tiktok ", "function": handle_prepare_tiktok},
    ]


def handle_post(command, router):
    text = command[len("post ") :].strip()
    post_to_network(text)
    return "✅ Post enviado a redes simbólicas."


def handle_prepare_tiktok(command, router):
    frase = command[len("prepare_tiktok ") :].strip()
    if not frase:
        return "Frase simbólica requerida para TikTok."

    if was_already_done(frase, "tiktok"):
        return "⚠️ Esta idea ya fue publicada antes en TikTok."

    content = {
        "title": frase[:60],
        "hook": f"¿Te has preguntado por qué {frase.lower()}?",
        "body": f"{frase}\n\nExplora más con Q•AI y la Ley de Coherencia Fundamental.",
        "hashtags": ["#QAI", "#Simbolismo", "#Coherencia", "#Qark"],
        "music": "default_theme.mp3",
        "video_path": "placeholder.mp4",
    }

    export_tiktok_post(content)
    return "📹 Publicación TikTok preparada y registrada."
