from contextlib import contextmanager
from core.memory.memory import MemoryManager


@contextmanager
def SymbolicContext():
    memory = MemoryManager()

    nombre = memory.get_fact("nombre_usuario") or "desconocido"
    plan = memory.get_fact("plan_general") or "sin plan"
    foco = memory.get_focus() or "ninguno"

    print("[Q•Agent] Cargando contexto simbólico...")
    print(f"[Q•Agent] Usuario: {nombre}")
    print(f"[Q•Agent] Plan: {plan}")
    print(f"[Q•Agent] Foco actual: {foco}")
    print("[Q•Agent] Últimos mensajes:")
    for m in memory.get_recent_messages(3):
        print(f"[{m['role']}] {m['content']}")

    try:
        yield memory
    finally:
        try:
            print("[Q•Agent] Guardando snapshot de contexto...")
            memory._save()
            print("[Q•Agent] Memoria persistente actualizada.")
        except Exception as e:
            print(f"❌ Error al guardar memoria persistente: {e}")
