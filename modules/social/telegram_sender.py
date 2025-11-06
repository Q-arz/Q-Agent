import requests

TELEGRAM_BOT_TOKEN = "123456789:ABCdefGhIjkLmnoPQRstuVwxyz"
TELEGRAM_USER_ID = "123456789"  # tu ID personal


def send_to_telegram(texto: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_USER_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"[Telegram] ❌ Error al enviar mensaje: {e}")
