import os
import requests

MEDIUM_API_URL = "https://api.medium.com/v1"
TOKEN = os.getenv("MEDIUM_INTEGRATION_TOKEN")


def get_user_id():
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    response = requests.get(f"{MEDIUM_API_URL}/me", headers=headers)
    if response.status_code == 200:
        return response.json()["data"]["id"]
    else:
        print(f"[Medium] Error al obtener usuario: {response.text}")
        return None


def post_to_medium(content: str, title: str = "Artículo de Q•AI", tags=None):
    if not TOKEN:
        print("[Medium] Token no configurado.")
        return

    user_id = get_user_id()
    if not user_id:
        return

    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

    data = {
        "title": title,
        "contentFormat": "markdown",
        "content": content,
        "tags": tags or ["QAI", "simbología", "coherencia"],
        "publishStatus": "public",
    }

    response = requests.post(
        f"{MEDIUM_API_URL}/users/{user_id}/posts", headers=headers, json=data
    )

    if response.status_code == 201:
        post_url = response.json()["data"]["url"]
        print(f"[Medium] Artículo publicado: {post_url}")
    else:
        print(f"[Medium] Error al publicar: {response.text}")
