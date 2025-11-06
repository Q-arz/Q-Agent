import os
import json
from datetime import datetime


class MemoryManager:
    def __init__(self):
        self.memory_path = os.path.join("logs", "memory_store.json")
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump({"log": [], "facts": {}, "focus": None}, f, indent=2)

        with open(self.memory_path, "r", encoding="utf-8") as f:
            self.memory = json.load(f)

    def store_message(self, role: str, content: str):
        contenido = content.strip().lower()
        if contenido in ("", "enable voice", "disabled voice", "hmm...", "no entendí"):
            return

        self.memory["log"].append(
            {"timestamp": datetime.now().isoformat(), "role": role, "content": content}
        )
        self._save()

    def set_fact(self, key: str, value: str):
        """Guarda hechos persistentes (ej. nombre, objetivo, proyecto actual)."""
        self.memory["facts"][key] = value
        self._save()

    def get_fact(self, key: str):
        return self.memory["facts"].get(key)

    def set_focus(self, topic: str):
        self.memory["focus"] = topic
        self._save()

    def get_focus(self):
        return self.memory["focus"]

    def get_recent_messages(self, n=10):
        return self.memory["log"][-n:]

    def clear_context(self):
        self.memory["log"] = []
        self._save()

    def _save(self):
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
