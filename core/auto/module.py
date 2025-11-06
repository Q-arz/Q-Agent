from core.auto.board import (
    add_task as add_board_task,
    complete_task,
    show_tasks,
    show_archive,
)


def get_commands():
    return [
        {"trigger": "add_task ", "function": handle_add_task},
        {"trigger": "complete ", "function": handle_complete_task},
        {"trigger": "show_tasks", "function": handle_show_tasks},
        {"trigger": "show_archive", "function": handle_show_archive},
    ]


def handle_add_task(command, router):
    contenido = command[len("add_task ") :].strip()
    if not contenido:
        return "No se puede añadir una tarea vacía."
    task = {"type": "idea", "title": contenido}
    add_board_task(task)
    return "📝 Tarea simbólica añadida al board."


def handle_complete_task(command, router):
    index_str = command[len("complete ") :].strip()
    if not index_str.isdigit():
        return "Debes indicar el número de la tarea. Ej: complete 2"
    complete_task(int(index_str))
    return f"✅ Tarea #{index_str} marcada como completada."


def handle_show_tasks(command, router):
    show_tasks()
    return "📋 Mostrando tareas pendientes."


def handle_show_archive(command, router):
    show_archive()
    return "🗂️ Historial mostrado."
