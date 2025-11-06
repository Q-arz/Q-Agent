def handle(command, router):
    command = command.strip().lower()

    if command.startswith("repite esto"):
        msg = command[len("repite esto") :].strip()
        router.io.speak(msg)
        return "El mensaje ha sido leído."

    elif command.startswith("genera sobre"):
        prompt = command[len("genera sobre") :].strip()
        return router.generator.create(prompt)

    elif command in ("help", "ayuda"):
        from core.i18n.strings import t
        lines = [t(router.io.language, "help_title")]
        # built-ins
        lines.append("- repite esto <texto>")
        lines.append("- genera sobre <prompt>")
        lines.append("- board list | board done <n> | board clear | board archive")
        lines.append("- suggest now")
        lines.append("- board ui (open popout window)")
        lines.append("- ui demo (table/text popout demo)")
        lines.append("- ui open <module_id>")
        lines.append("- models ensure vosk <lang> [<url>]")
        lines.append("- setup beforeui")
        lines.append("- setup voice (install voice deps)")
        lines.append("- palette (open command palette)")
        # dynamic
        from core.router.dynamic_router import dynamic_manifests
        for m in dynamic_manifests:
            mid = m.get("id", "module")
            for c in m.get("commands", []):
                trig = c.get("trigger", "").strip()
                syns = ", ".join(c.get("synonyms", [])) if c.get("synonyms") else ""
                lines.append(f"- {mid}: {trig}  {('['+syns+']') if syns else ''}")
        return "\n".join(lines)

    elif command.startswith("set language "):
        code = command[len("set language ") :].strip()
        if not code:
            return "[Q•AI] Missing language code."
        router.io.set_language(code)
        router.config["language"] = code
        if "asr" in router.config:
            router.config["asr"]["language"] = code
        return f"[Q•AI] Language set to {code}."

    # Board management commands
    elif command == "board list":
        from core.auto import board
        board.show_tasks()
        return "[Q•Agent] Board listado."

    elif command.startswith("board done "):
        from core.auto import board
        num = command[len("board done ") :].strip()
        try:
            idx = int(num)
            board.complete_task(idx)
            return f"[Q•Agent] Tarea #{idx} marcada como completada."
        except Exception:
            return "[Q•AI] Uso: board done <n>"

    elif command == "board clear":
        from core.auto import board
        board.clear_tasks()
        return "[Q•Agent] Board limpiado."

    elif command == "board archive":
        from core.auto import board
        board.show_archive()
        return "[Q•Agent] Archivo mostrado."

    elif command == "suggest now":
        from core.auto.idea_suggester import sugerir_acciones
        sugerir_acciones()
        return "[Q•Agent] Sugeridor ejecutado."

    elif command == "board ui":
        from core.ui.popout import PopoutService
        PopoutService.instance().show_board()
        return "[Q•Agent] Board UI abierta."

    elif command == "ui demo":
        from core.ui.popout import PopoutService
        svc = PopoutService.instance()
        svc.show_text("Q•Agent", "This is a demo popout window.\nYou can open multiple windows.")
        svc.show_table("Demo Table", ["Col A", "Col B", "Col C"], [["1","foo","bar"],["2","hello","world"]])
        return "[Q•Agent] UI demo abierta."

    elif command.startswith("ui open "):
        mod_id = command[len("ui open ") :].strip()
        from core.router.dynamic_router import dynamic_manifests
        from core.ui.schema import open_module_ui
        for m in dynamic_manifests:
            if m.get("id") == mod_id:
                return open_module_ui(m)
        return "[Q•Agent] Module not found."

    elif command == "palette":
        from core.ui.popout import PopoutService
        svc = PopoutService.instance()
        def _submit(text: str):
            try:
                router.io.handle_text(text)
            except Exception:
                pass
        svc.show_palette(_submit)
        return "[Q•Agent] Command palette open."

    elif command.startswith("models ensure vosk "):
        parts = command.split(" ")
        lang = parts[3] if len(parts) >= 4 else "es"
        url = parts[4] if len(parts) >= 5 else None
        from core.system.models import ensure_vosk_model
        return ensure_vosk_model(lang, url)

    elif command == "setup beforeui":
        from core.ui.beforeui import open_before_ui
        open_before_ui(router)
        return "[Q•Agent] Setup UI abierta."

    elif command.startswith("setup apply "):
        parts = command.split(" ")
        try:
            _, _, language, asr_engine, asr_language, tts_rate = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        except Exception:
            return "[Q•Agent] Usage: setup apply <language> <asr_engine> <asr_language> <tts_rate>"
        from core.ui.beforeui import apply_setup
        return apply_setup(router, language, asr_engine, asr_language, tts_rate)

    elif command == "setup voice":
        import sys, subprocess
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        script = root / "scripts" / "setup_voice.py"
        try:
            subprocess.check_call([sys.executable, str(script)])
            return "[Q•Agent] Voice dependencies installed."
        except Exception as e:
            return f"[Q•Agent] Failed to install voice deps: {e}"

    elif command == "enable voice":
        router.io.switch_mode("voz")
        router.io.start()
        return "Modo voz activado."

    elif command == "disable voice":
        router.io.switch_mode("texto")
        router.io.start()
        return "Modo texto activado."
