from .discord_poster import post_to_discord
from .x_poster import post_to_x
from .medium_poster import post_to_medium
from .telegram_sender import send_to_telegram


def post_to_network(message: str, target: str = "all") -> None:
    if target in ("all", "discord"):
        post_to_discord(message)
    if target in ("all", "x"):
        post_to_x(message)
    if target in ("all", "medium"):
        post_to_medium(message)
    if target in ("all", "telegram"):
        send_to_telegram(message)
