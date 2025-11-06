def handle(command, router):
    command = command.strip().lower()
    memory = router.memory

    # Comandos directos (tu estilo original)
    if command.startswith("remember "):
        content = command[len("remember ") :].strip()
        memory.store_message("user", content)
        return "🧠 Memory stored."

    elif command.startswith("recall"):
        mensajes = memory.get_recent_messages()
        texto = "\n".join([f"[{m['role']}] {m['content']}" for m in mensajes])
        return f"🗃️ Memory:\n{texto}"

    # Comandos simbólicos naturales
    if command.startswith("recuérdame esto:"):
        valor = command.split("recuérdame esto:", 1)[1].strip()
        memory.set_fact("recordatorio", valor)
        return f"🧠 Recordado simbólicamente: “{valor}”"

    if command.startswith("quiero que recuerdes que"):
        valor = command.split("quiero que recuerdes que", 1)[1].strip()
        memory.set_fact("hecho_personal", valor)
        return f"📌 Hecho registrado simbólicamente: “{valor}”"

    if "establece el foco en" in command:
        nuevo_foco = command.split("establece el foco en", 1)[1].strip()
        memory.set_focus(nuevo_foco)
        return f"🎯 Foco simbólico establecido en: {nuevo_foco}"

    if "cambia el plan general a" in command:
        nuevo_plan = command.split("cambia el plan general a", 1)[1].strip()
        memory.set_fact("plan_general", nuevo_plan)
        return f"📌 Nuevo plan general registrado: {nuevo_plan}"

    return None
