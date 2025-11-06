from datetime import datetime, timedelta
from core.auto import board
from core.logs.logger import setup_logger
from modules.social.social import post_to_network
import time
import json
from pathlib import Path


class BoardExecutor:
    def __init__(self):
        self.logger = setup_logger("qai.board")
        self.actions = {
            "publicar": self.publicar_contenido,
            "responder": self.responder_comentario,
            "evento": self.recordar_evento,
        }
        self.cooldowns = {}
        self.cfg = self._load_config()

    def run_supervisor_mode(self):
        """No ejecuta tareas. Solo evalúa y propone decisiones"""
        from core.auto import board
        from datetime import datetime, timedelta

        tareas = board.load_tasks()
        ahora = datetime.now()

        for i, t in enumerate(tareas):
            if t.get("status") != "pending":
                continue

            fecha = t.get("fecha")
            prioridad = t.get("prioridad", "media")

            if fecha:
                try:
                    fecha_dt = datetime.fromisoformat(fecha)
                    tiempo_restante = fecha_dt - ahora

                    if tiempo_restante < timedelta(minutes=0):
                        self.logger.info(f"[Supervisor] ⚠️ Tarea vencida: {t['title']} ({prioridad})")
                    elif tiempo_restante < timedelta(minutes=30):
                        self.logger.info(f"[Supervisor] ⏳ En breve: {t['title']} ({prioridad})")
                except Exception as e:
                    self.logger.warning(f"[Supervisor] ❌ Fecha malformada en tarea: {e}")
            else:
                self.logger.info(f"[Supervisor] 🧠 Tarea sin fecha: {t['title']} ({prioridad})")

    def run_auto_executor(self):
        tareas = board.load_tasks()
        ahora = datetime.now()

        for i, t in enumerate(tareas):
            if t.get("status") != "pending":
                continue

            tipo = t.get("type")
            prioridad = t.get("prioridad", "media").lower()
            fecha_txt = t.get("fecha")
            action = self.actions.get(tipo)

            if not action:
                self.logger.warning(f"[Executor] ⚠️ Tipo no soportado: {tipo}")
                continue

            minutos_faltantes = 99999
            if fecha_txt:
                try:
                    fecha_dt = datetime.fromisoformat(fecha_txt)
                    minutos_faltantes = (fecha_dt - ahora).total_seconds() / 60
                except Exception as e:
                    log(f"[Executor] ❌ Fecha inválida: {e}")

            if prioridad == "alta" and minutos_faltantes < 10:
                # policy: dry_run unless allowed
                if not self._can_execute(type=tipo, task=t):
                    self.logger.info(f"[AUTO] 🔒 Dry-run: {t['title']}")
                    continue
                if self._is_in_cooldown(t):
                    self.logger.info(f"[AUTO] ⏳ Cooldown activo para: {t['title']}")
                    continue
                self.logger.info(f"[AUTO] 🔥 Ejecutando urgente: {t['title']}")
                try:
                    self._execute_with_retries(action, t)
                    self._set_cooldown(t)
                    board.complete_task(i + 1)
                except Exception as e:
                    self.logger.exception(f"[Executor] ❌ Error: {e}")
            else:
                self.logger.info(
                    f"[AUTO] 🧠 Tarea pendiente observada: {t['title']} (Prioridad: {prioridad}, faltan {int(minutos_faltantes)}m)"
                )

    def publicar_contenido(self, task):
        target = task.get("target", "all")
        mensaje = f"📤 Publicación automática: {task.get('title')}"
        self.logger.info(f"[AUTO] {mensaje}")
        post_to_network(mensaje, target)

    def responder_comentario(self, task):
        self.logger.info(f"[AUTO] 💬 Respondiendo simbólicamente: {task.get('title')}")

    def recordar_evento(self, task):
        self.logger.info(f"[AUTO] 📅 Recordatorio de evento: {task.get('title')}")

    def _load_config(self):
        try:
            cfg_path = Path(__file__).resolve().parents[1] / "config" / "qai_config.json"
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _can_execute(self, type: str, task: dict) -> bool:
        ex = (self.cfg.get("executor", {}) or {})
        if ex.get("auto_execute", False):
            return True
        # allowlist per type/target optional
        allow_types = set((ex.get("allow_types", []) or []))
        if allow_types and type not in allow_types:
            return False
        return False

    def _execute_with_retries(self, action, task):
        ex = (self.cfg.get("executor", {}) or {})
        max_retries = ex.get("max_retries", task.get("retries", 1))
        delay = ex.get("retry_delay_seconds", 5)
        attempt = 0
        last_err = None
        while attempt <= max_retries:
            try:
                return action(task)
            except Exception as e:
                last_err = e
                attempt += 1
                time.sleep(delay * (2 ** (attempt - 1)))
        raise last_err

    def _cooldown_key(self, task: dict) -> str:
        return f"{task.get('type')}::{task.get('target','all')}"

    def _is_in_cooldown(self, task: dict) -> bool:
        ex = (self.cfg.get("executor", {}) or {})
        seconds = (ex.get("cooldown_seconds", {}) or {}).get(task.get("type"), 0)
        if seconds <= 0:
            return False
        key = self._cooldown_key(task)
        until = self.cooldowns.get(key)
        return until is not None and until > time.time()

    def _set_cooldown(self, task: dict):
        ex = (self.cfg.get("executor", {}) or {})
        seconds = (ex.get("cooldown_seconds", {}) or {}).get(task.get("type"), 0)
        if seconds <= 0:
            return
        key = self._cooldown_key(task)
        self.cooldowns[key] = time.time() + seconds
