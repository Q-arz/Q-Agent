from core.memory.memory import MemoryManager
from core.generators.generator import Generator
from core.router.dynamic_router import dynamic_commands, dynamic_manifests, load_all_modules
from core.security.permissions import PermissionManager
from core.nlu.intent import IntentMatcher
from core.metrics.metrics import metrics
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging
from core.router import core_commands, memory_commands
from core.router import board_commands, module_commands
import random


FRASES_NO_ENTENDIDO = [
    "No entendí bien, ¿puedes repetir?",
    "¿Eso era un comando?",
    "No tengo eso registrado como acción.",
    "Hmm... no capté ninguna instrucción clara.",
    "¿Puedes decirlo otra vez de otro modo?",
]


class CommandRouter:
    def __init__(self, config, io_handler):
        print("[CommandRouter] Iniciando construcción del router...")
        self.config = config
        self.io = io_handler
        self.memory = config.get("memory") or MemoryManager()
        self.generator = Generator(config)
        whitelist = (self.config or {}).get("permissions_whitelist", {})
        self.permissions = PermissionManager(io_handler, whitelist=whitelist)
        load_all_modules()
        print("MCP Command Router modularizado.")
        self.intent_matcher = IntentMatcher(dynamic_manifests)
        self.logger = logging.getLogger("qai.router")
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.timeout_seconds = (self.config or {}).get("command_timeout_seconds", 10)
        self.max_retries = (self.config or {}).get("command_max_retries", 1)
        self.security_cfg = (self.config or {}).get("security", {})

        # Esto debe ir aquí, dentro del __init__
        self.command_modules = [
            core_commands,
            memory_commands,
            board_commands,
            module_commands,
        ]

    def route(self, command):
        command = command.strip()
        if not command:
            return "No command received."

        # permissions: ensure manifest permissions via PermissionManager
        def has_permission(manifest):
            return self.permissions.ensure_permissions(manifest)

        for module in self.command_modules:
            result = module.handle(command, self)
            if result is not None:
                return result

        for dyn in dynamic_commands:
            if command.startswith(dyn["trigger"]):
                manifest = dyn.get("_manifest")
                if manifest:
                    self.permissions.context = {"command": command, "module": manifest.get("id")}
                # allow/deny filters
                if manifest:
                    mid = manifest.get("id")
                    if mid:
                        deny = set(self.security_cfg.get("deny", {}).get(mid, []))
                        allow = set(self.security_cfg.get("allow", {}).get(mid, []))
                        trig = dyn["trigger"]
                        if trig in deny:
                            return "[Q•AI] Command denied by policy."
                        if allow and trig not in allow:
                            return "[Q•AI] Command not allowed by policy."
                if manifest and not has_permission(manifest):
                    return "[Q•AI] Permission denied for this command."
                # metrics & timeout/retry
                end_timer = metrics.time_block("command.time")
                attempt = 0
                last_err = None
                while attempt <= self.max_retries:
                    try:
                        future = self.executor.submit(dyn["function"], command, self)
                        result = future.result(timeout=self.timeout_seconds)
                        break
                    except TimeoutError:
                        self.logger.warning("Command timed out: %s", command)
                        last_err = "timeout"
                        attempt += 1
                    except Exception as e:
                        self.logger.exception("Command error: %s", command)
                        last_err = str(e)
                        attempt += 1
                end_timer()
                metrics.inc("command.count")
                if last_err and attempt > self.max_retries:
                    return f"[Q•AI] Command failed: {last_err}"
                try:
                    if self.memory:
                        self.memory.store_message("audit", {"command": command, "module": manifest.get("id") if manifest else None, "result": result})
                except Exception:
                    pass
                return result

        # NLU: try synonyms-based intent matching
        intent = self.intent_matcher.match(command)
        if intent:
            manifest, cmd = intent
            self.permissions.context = {"command": command, "module": manifest.get("id")}
            if not has_permission(manifest):
                return "[Q•AI] Permission denied for this command."
            handler = cmd.get("handler")
            trigger = cmd.get("trigger", "")
            if callable(handler):
                # timeout/retry
                end_timer = metrics.time_block("command.time")
                attempt = 0
                last_err = None
                cmdline = command if command.startswith(trigger) else f"{trigger}{command[len(command.split(' ')[0]):]}"
                while attempt <= self.max_retries:
                    try:
                        future = self.executor.submit(handler, cmdline, self)
                        out = future.result(timeout=self.timeout_seconds)
                        break
                    except TimeoutError:
                        self.logger.warning("Command timed out: %s", cmdline)
                        last_err = "timeout"
                        attempt += 1
                    except Exception as e:
                        self.logger.exception("Command error: %s", cmdline)
                        last_err = str(e)
                        attempt += 1
                end_timer()
                metrics.inc("command.count")
                if last_err and attempt > self.max_retries:
                    return f"[Q•AI] Command failed: {last_err}"
                try:
                    if self.memory:
                        self.memory.store_message("audit", {"command": command, "module": manifest.get("id"), "result": out})
                except Exception:
                    pass
                return out

        # Fallback: use Generator to suggest an action
        try:
            suggestion = self.generator.create(f"Given the user input, propose an actionable command trigger and arguments succinctly. Input: '{command}'")
            if suggestion and isinstance(suggestion, str):
                return suggestion
        except Exception:
            pass
        return random.choice(FRASES_NO_ENTENDIDO)
