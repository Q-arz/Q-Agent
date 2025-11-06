from core.router.router import CommandRouter

import pyttsx3

PELIGROSOS = ["rm ", "os.", "__import__", "eval(", "exec(", "subprocess"]


class IOHandler:
    def __init__(self, config):
        print("[DEBUG] Entrando a IOHandler.__init__()")
        self.config = config
        self.memory = config.get("memory")
        print("[DEBUG] Config y memoria asignadas")
        self.modo_actual = config.get("modo", "voz")
        self.language = (config.get("language") or config.get("asr", {}).get("language") or "es").lower()
        self.awaiting_confirmation = False
        self.last_input = None
        print("[DEBUG] Inicializando motor de voz...")
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", (config.get("tts", {}) or {}).get("rate", 180))
        self._set_voice_by_language(self.language, desired_id=(config.get("tts", {}) or {}).get("voice"))
        print("[DEBUG] Motor de voz listo")
        self.router = CommandRouter(config, self)
        try:
            from core.ui.popout import PopoutService
            PopoutService.instance().set_router(self.router)
        except Exception:
            pass
        print("[DEBUG] Router cargado")
        print(f"[IOHandler] Inicializando IOHandler en modo: {self.modo_actual}")

        modo_voz = (config.get("asr", {}) or {}).get("engine", config.get("voz_engine", "whisper"))
        print(f"[DEBUG] Modo de voz desde config: {modo_voz}")
        try:
            if modo_voz == "whisper":
                print("[IOHandler] Usando Whisper...")
                from core.interfaces.whisper_listener import WhisperListener
                self.listener = WhisperListener(on_text_callback=self.handle_text, model_name="tiny", rate=16000, language=self.language)
            elif modo_voz == "vosk":
                print("[IOHandler] Usando Vosk...")
                from core.interfaces.vosk_listener import VoskListener
                model_dir = (config.get("asr", {}) or {}).get("modelDir")
                self.listener = VoskListener(on_text_callback=self.handle_text, rate=16000, language=self.language, model_dir=model_dir)
            else:
                raise ValueError(f"Modo de voz desconocido: {modo_voz}")
        except Exception as e:
            print(f"[IOHandler] Fallo al cargar el listener de voz: {e}")
            if self.modo_actual == "voz":
                print("[IOHandler] ↩️ Degradando a modo TEXTO por fallo en voz.")
                self.modo_actual = "texto"

        print("[IOHandler] Inicialización completa.")

    def es_input_seguro(texto):
        return not any(p in texto.lower() for p in PELIGROSOS)

    def _set_voice_by_language(self, language_code: str, desired_id=None):
        try:
            voices = self.engine.getProperty("voices")
            selected = None
            # exact desired id
            if desired_id and desired_id != "auto":
                for v in voices:
                    if v.id == desired_id:
                        selected = v
                        break
            # locale match
            if not selected:
                lang = language_code.split("-")[0]
                for v in voices:
                    name = (getattr(v, "name", "") or "").lower()
                    vid = (getattr(v, "id", "") or "").lower()
                    if lang in vid or lang in name:
                        selected = v
                        break
            # spanish fallback
            if not selected and language_code.startswith("es"):
                for v in voices:
                    if "spanish" in (getattr(v, "name", "") or "").lower():
                        selected = v
                        break
            if selected:
                self.engine.setProperty("voice", selected.id)
        except Exception:
            pass

    def speak(self, text: str):
        self.engine.stop()
        self.engine.say(text)
        self.engine.runAndWait()

    def handle_text(self, text: str):
        text = text.strip().lower()
        print(f"[Tú] {text}")
        if self.memory:
            self.memory.store_message("user", text)

        # ✅ Corrección simbólica
        if self.awaiting_confirmation and text.startswith("no, dije"):
            correccion = text.replace("no, dije", "").strip(": ").strip()
            print(f"[Q•AI] ✅ Corrigiendo a: “{correccion}”")
            if self.memory:
                self.memory.store_message(
                    "correccion",
                    {"mal_interpretado": self.last_input, "corregido_a": correccion},
                )
            self.awaiting_confirmation = False
            self.handle_text(correccion)  # Reprocesa el nuevo texto
            return

        # ✅ Confirmación directa positiva (ej: "sí", "correcto")
        if self.awaiting_confirmation and text in (
            "sí",
            "si",
            "correcto",
            "afirmativo",
        ):
            print(f"[Q•AI] ✅ Confirmado: “{self.last_input}”")
            response = self.router.route(self.last_input)
            if response:
                print(f"[Q•AI] {response}")
                self.speak(response)
                if self.memory:
                    self.memory.store_message("qai", response)
            self.awaiting_confirmation = False
            return

        # 🔁 Cambio de modo
        if text in ("modo texto", "desactiva voz", "quiero escribir"):
            self.switch_to_text_mode()
            return

        if text in ("exit", "quit", "salir"):
            print("[Q•AI] Hasta luego.")
            if self.memory:
                self.memory.store_message("qai", "Hasta luego.")
            exit()

        # 🧠 Confirmación previa si viene de voz
        if self.config.get("modo") == "voz":
            self.last_input = text
            self.awaiting_confirmation = True
            confirm_msg = f"Entendí bien?: {text}"
            print(f"[Q•AI] {confirm_msg}")
            self.speak(confirm_msg)
            return

        # ✨ Procesamiento normal (modo texto o ya confirmado)
        response = self.router.route(text)
        if response:
            print(f"[Q•AI] {response}")
            self.speak(response)
            if self.memory:
                self.memory.store_message("qai", response)
        self.awaiting_confirmation = False

    def start(self):
        print("[IOHandler] Entrando a start()")
        if self.modo_actual == "voz":
            print("[IOHandler] Modo VOZ detectado.")
            retries = 0
            max_retries = 3
            while retries <= max_retries:
                try:
                    self.listener.start()
                    print("[IOHandler] Listener terminó inesperadamente.")
                except Exception as e:
                    print(f"[IOHandler] Error en listener: {e}")
                retries += 1
                if retries <= max_retries:
                    print(f"[IOHandler] Reiniciando listener (intento {retries}/{max_retries})...")
                    continue
                break
        else:
            print("[IOHandler] Modo TEXTO detectado.")
            self.loop_consola()

    def loop_consola(self):
        print("[Modo texto activo. Escribe tus comandos.]")
        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() in ("exit", "salir", "quit"):
                    print("[Q•AI] Hasta luego.")
                    if self.memory:
                        self.memory.store_message("qai", "Hasta luego.")
                    break
                self.handle_text(user_input)
            except KeyboardInterrupt:
                print("\n[Q•Agent] Interrumpido por el usuario.")
                break

    def switch_mode(self, nuevo_modo: str):
        if nuevo_modo == self.modo_actual:
            return f"[Q•AI] Ya estás en modo {nuevo_modo}."

        if nuevo_modo == "texto":
            if self.listener:
                self.listener.stop()
            self.modo_actual = "texto"
            return "⌨️ Modo texto activado."

        elif nuevo_modo == "voz":
            self.modo_actual = "voz"
            return "🎙️ Modo voz activado."

    def set_language(self, new_lang: str):
        self.language = new_lang.lower()
        self._set_voice_by_language(self.language, desired_id=(self.config.get("tts", {}) or {}).get("voice"))
        # reiniciar listener si corresponde
        try:
            if self.modo_actual == "voz" and getattr(self, "listener", None):
                try:
                    self.listener.stop()
                except Exception:
                    pass
                modo_voz = (self.config.get("asr", {}) or {}).get("engine", self.config.get("voz_engine", "whisper"))
                if modo_voz == "whisper":
                    self.listener = WhisperListener(on_text_callback=self.handle_text, model_name="tiny", rate=16000, language=self.language)
                elif modo_voz == "vosk":
                    model_dir = (self.config.get("asr", {}) or {}).get("modelDir")
                    self.listener = VoskListener(on_text_callback=self.handle_text, rate=16000, language=self.language, model_dir=model_dir)
        except Exception as e:
            print(f"[IOHandler] ⚠️ No se pudo reconfigurar listener: {e}")
