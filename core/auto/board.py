import os
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

BOARD_PATH = LOGS_DIR / "board.json"
ARCHIVE_PATH = LOGS_DIR / "board_archive.json"

if not BOARD_PATH.exists():
    BOARD_PATH.write_text("[]", encoding="utf-8")

if not ARCHIVE_PATH.exists():
    ARCHIVE_PATH.write_text("[]", encoding="utf-8")


def _normalize_task(task: dict) -> dict:
    now = datetime.now().isoformat()
    t = dict(task)
    t["id"] = t.get("id") or str(uuid.uuid4())
    t["type"] = (t.get("type") or "generic").lower()
    t["title"] = t.get("title") or ""
    t["status"] = t.get("status") or "pending"
    t["priority"] = (t.get("prioridad") or t.get("priority") or "media").lower()
    t["prioridad"] = t["priority"]
    t["due"] = t.get("due") or t.get("fecha") or None
    t["created_at"] = t.get("created_at") or now
    t["updated_at"] = now
    t["source"] = t.get("source") or "manual"
    t["module"] = t.get("module") or None
    t["params"] = t.get("params") or {}
    t["retries"] = int(t.get("retries", 1))
    t["last_error"] = t.get("last_error") or None
    t["cooldown_until"] = t.get("cooldown_until") or None
    t["tags"] = t.get("tags") or []
    # dedupe hash
    key = (t["type"], t["title"].strip().lower(), str(t.get("target", "")))
    t["dedupe_hash"] = hashlib.sha1("|".join(key).encode("utf-8")).hexdigest()
    return t


def _atomic_write(path: Path, data_obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data_obj, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def add_task(task: dict, force: bool = False):
    tasks = load_tasks()
    t = _normalize_task(task)
    if not force:
        if any(x.get("dedupe_hash") == t["dedupe_hash"] for x in tasks):
            print("[Board] Saltada por duplicada.")
            return
    tasks.append(t)
    _atomic_write(BOARD_PATH, tasks)
    print(f"[Board] Tarea añadida: {t['type']}")


def load_tasks():
    return json.loads(BOARD_PATH.read_text(encoding="utf-8"))


def show_tasks():
    tasks = load_tasks()
    if not tasks:
        print("[Board] No hay tareas pendientes.")
        return
    for i, task in enumerate(tasks):
        status = task.get("status", "pending")
        print(f"{i+1}. [{task['type'].upper()}] {task.get('title', '...')} ({status})")


def clear_tasks():
    _atomic_write(BOARD_PATH, [])
    print("[Board] Tareas borradas.")


def complete_task(index: int):
    tasks = load_tasks()
    if index < 1 or index > len(tasks):
        print(f"[Board] Índice fuera de rango. Total: {len(tasks)} tareas.")
        return

    completed = tasks[index - 1]
    completed["status"] = "done"

    # Guardar en board_archive.json
    archive = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))
    archive.append(completed)
    _atomic_write(ARCHIVE_PATH, archive)

    # Eliminar de board.json
    tasks.pop(index - 1)
    _atomic_write(BOARD_PATH, tasks)

    print(f"[Board] Tarea #{index} marcada como completada y archivada.")


def show_archive():
    if not ARCHIVE_PATH.exists():
        print("[Archive] No hay historial aún.")
        return

    archive = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))

    if not archive:
        print("[Archive] El historial está vacío.")
        return

    print("[Archive] Tareas completadas:")
    for i, task in enumerate(archive):
        print(
            f"{i+1}. [{task['type'].upper()}] {task.get('title', '...')} ({task.get('timestamp', '')})"
        )


def was_already_done(title: str, type_filter: str = None) -> bool:
    if not os.path.exists(ARCHIVE_PATH):
        return False
    with open(ARCHIVE_PATH, "r", encoding="utf-8") as f:
        archive = json.load(f)
    for task in archive:
        if type_filter and task.get("type") != type_filter:
            continue
        if title.lower().strip() in task.get("title", "").lower():
            return True
    return False
