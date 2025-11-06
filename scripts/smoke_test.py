import json
import sys
import os
from pathlib import Path

# Add project root to sys.path to enable implicit namespace package 'core'
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Ensure UTF-8 output on Windows consoles
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from core.interfaces.io import IOHandler
from core.router.router import CommandRouter
from core.memory.boot_context import SymbolicContext


def load_config():
    base = Path(__file__).resolve().parents[1]
    cfg_path = base / "core" / "config" / "qai_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    # Force text mode and disable heavy features for smoke run
    cfg["modo"] = "texto"
    cfg["reflejo_sistemico"] = False
    return cfg


def run_case(name: str, func):
    print(f"\n=== {name} ===")
    try:
        out = func()
        if out is not None:
            print(out)
        print(f"[OK] {name}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        raise


def main():
    cfg = load_config()
    with SymbolicContext() as mem:
        cfg["memory"] = mem
        io = IOHandler(cfg)
        router = CommandRouter(cfg, io)

        run_case("help", lambda: router.route("help"))
        run_case("suggest now", lambda: router.route("suggest now"))
        run_case("board list (after suggest)", lambda: router.route("board list"))
        run_case("generator (simulated ok)", lambda: router.route("genera sobre prueba de generador"))

        # UI-related commands are skipped in smoke test to avoid GUI dependency
        # run_case("ui demo", lambda: router.route("ui demo"))

        print("\nAll smoke tests completed.")


if __name__ == "__main__":
    main()


