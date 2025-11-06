import time


DEFAULT_SENSITIVE = {
    "filesystem.write",
    "process.spawn",
    "network.request",
    "ui.automation",
}


class PermissionManager:
    def __init__(self, io_handler=None, policy=None, whitelist=None):
        self.io = io_handler
        self.policy = policy or {}
        self.whitelist = whitelist or {}
        self._grants = {}
        self.context = {}

    def _key(self, module_id: str, perm: str) -> str:
        return f"{module_id}:{perm}"

    def is_granted(self, module_id: str, perm: str) -> bool:
        key = self._key(module_id, perm)
        info = self._grants.get(key)
        if not info:
            return False
        if info.get("expires_at") and info["expires_at"] < time.time():
            del self._grants[key]
            return False
        return info.get("granted", False)

    def grant(self, module_id: str, perm: str, seconds: int = 300):
        key = self._key(module_id, perm)
        self._grants[key] = {
            "granted": True,
            "expires_at": time.time() + seconds if seconds else None,
        }

    def revoke(self, module_id: str, perm: str):
        key = self._key(module_id, perm)
        if key in self._grants:
            del self._grants[key]

    def ensure_permissions(self, manifest: dict) -> bool:
        module_id = manifest.get("id", "unknown.module")
        perms = manifest.get("permissions", [])
        if not perms:
            return True

        for perm in perms:
            # whitelist auto-grant
            wl = self.whitelist.get(module_id, [])
            if perm in wl:
                self.grant(module_id, perm, seconds=600)
                continue
            if self.is_granted(module_id, perm):
                continue
            if perm in DEFAULT_SENSITIVE:
                if not self._prompt_user(module_id, perm):
                    return False
            else:
                # non-sensitive default allow for MVP
                self.grant(module_id, perm, seconds=600)
        return True

    def _prompt_user(self, module_id: str, perm: str) -> bool:
        cmd = (self.context or {}).get("command")
        summary = f"\nCommand: {cmd}" if cmd else ""
        message = f"[Q•AI] Module '{module_id}' requests permission '{perm}'.{summary}\nAllow for 5 minutes? (yes/no)"
        try:
            if self.io:
                try:
                    self.io.speak(message)
                except Exception:
                    pass
            print(message)
            answer = input("> ").strip().lower()
            if answer in ("y", "yes", "si", "sí"):
                self.grant(module_id, perm, seconds=300)
                return True
            return False
        except Exception:
            return False


