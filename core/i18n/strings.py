STRINGS = {
    "es": {
        "help_title": "Comandos disponibles:",
    },
    "en": {
        "help_title": "Available commands:",
    }
}


def t(lang: str, key: str) -> str:
    lang = (lang or "es").split("-")[0]
    return STRINGS.get(lang, STRINGS["es"]).get(key, key)


