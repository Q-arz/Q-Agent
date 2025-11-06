import sys
import json
import traceback
from pathlib import Path

# Asegura acceso a rutas internas
sys.path.append("core")

from core.memory.boot_context import SymbolicContext
from core.interfaces.io import IOHandler
from core.logs.logger import setup_logger
from core.system.health import check_dependencies
import signal
import argparse

# Logger
_logger = setup_logger("qai")
def log(msg):
    _logger.info(msg)


# Carga configuración
def load_config():
    try:
        base_dir = Path(__file__).resolve().parent
        config_path = base_dir / "core" / "config" / "qai_config.json"
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"Error al cargar configuración: {e}")
        return {}


# 🧠 Inicializa Q•AI
def main():
    config = load_config()
    config = check_dependencies(config)

    with SymbolicContext() as memory:
        config["memory"] = memory
    print("[Q•Agent] Contexto cerrado. Continuando...")
    if config.get("reflejo_sistemico", True):
        try:
            from core.auto.board_executor import BoardExecutor
            from core.auto.idea_suggester import sugerir_acciones

            log("Iniciando reflejo simbólico del sistema...")
            BoardExecutor().run_supervisor_mode()
            sugerir_acciones()
        except Exception as e:
            log(f"Fallo reflejo simbólico: {e}")
    io = None
    try:
        io = IOHandler(config)
        print("[Q•Agent] IOHandler construido.")
        log("Bienvenido a Q.Agent Console")
        # parse optional CLI run commands
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--run", type=str, nargs="?")
        args, _ = parser.parse_known_args()
        if args.run:
            # execute semicolon-separated commands non-interactively
            commands = [c.strip() for c in args.run.split(";") if c.strip()]
            for c in commands:
                try:
                    io.handle_text(c)
                except Exception:
                    log(f"Error ejecutando comando: {c}")
            return
        # graceful shutdown handlers
        def _shutdown(signum, frame):
            try:
                if io and getattr(io, "listener", None):
                    io.listener.stop()
            except Exception:
                pass
            try:
                from core.ui.popout import PopoutService
                svc = PopoutService.instance()
                if getattr(svc, "_root", None):
                    svc._root.after(0, svc._root.quit)
            except Exception:
                pass
        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(s, _shutdown)
            except Exception:
                pass
        io.start()
    except Exception as e:
        log("Error iniciando Q•AI:")
        log(str(e))
        log(traceback.format_exc())


if __name__ == "__main__":
    main()
