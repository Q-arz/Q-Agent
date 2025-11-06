# router/board_commands.py
from core.auto import board
from datetime import datetime


def handle(command, router):
    if command.startswith("agrega tarea"):
        return agregar_tarea(command)
    elif command.startswith("ver tareas"):
        return mostrar_tareas()
    elif command.startswith("marcar tarea "):
        return completar_tarea(command)
    elif command == "ejecuta tareas del board":
        from core.auto.board_executor import BoardExecutor
        executor = BoardExecutor()
        executor.run_auto_executor()
        return "[Q•AI] Ejecutor de board ejecutado."
    return None


def agregar_tarea(command):
    try:
        tipo = extraer_entre(command, "agrega tarea", "“").strip()
        titulo = extraer_entre(command, "“", "”").strip()

        # Extra opcionales
        fecha = extraer_despues(command, "el ")
        prioridad = (
            extraer_despues(command, "prioridad ").lower()
            if "prioridad" in command
            else "media"
        )

        tarea = {
            "type": tipo,
            "title": titulo,
            "prioridad": prioridad,
        }
        if fecha:
            try:
                fecha_obj = datetime.strptime(
                    fecha, "%d %B %Y a las %Hh"
                )  # Ej: 18 mayo 2025 a las 16h
                tarea["fecha"] = fecha_obj.isoformat()
            except:
                return "⚠️ Formato de fecha inválido. Usa: el 18 mayo 2025 a las 16h"

        board.add_task(tarea)
        return f"✅ Tarea agregada: {tipo.upper()} - {titulo}"
    except Exception as e:
        return f"❌ Error procesando tarea: {e}"


def mostrar_tareas():
    tareas = board.load_tasks()
    if not tareas:
        return "📭 No hay tareas activas."
    out = ["📋 Tareas activas:"]
    for i, t in enumerate(tareas):
        fecha = t.get("fecha", "")
        out.append(
            f"{i+1}. [{t['type']}] {t['title']} – Prioridad: {t['prioridad']} – {fecha}"
        )
    return "\n".join(out)


def completar_tarea(command):
    try:
        n = int(command.strip().split("marcar tarea")[1])
        board.complete_task(n)
        return f"✅ Tarea #{n} completada."
    except Exception as e:
        return f"❌ No se pudo completar la tarea: {e}"


# 🧠 Utilidades
def extraer_entre(texto, ini, fin):
    return texto.split(ini, 1)[1].split(fin, 1)[0]


def extraer_despues(texto, marcador):
    if marcador in texto:
        return texto.split(marcador, 1)[1].split(" prioridad")[0].strip()
    return ""
