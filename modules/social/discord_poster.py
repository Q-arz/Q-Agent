import os
import requests

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def post_to_discord(message: str) -> None:
    if not DISCORD_WEBHOOK_URL:
        print("[Discord] Webhook no configurado.")
        return

    data = {"content": message}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("[Discord] Mensaje enviado correctamente.")
        else:
            print(f"[Discord] Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Discord] Fallo al enviar mensaje: {e}")
