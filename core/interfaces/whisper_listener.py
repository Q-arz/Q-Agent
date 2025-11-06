import pyaudio
import numpy as np
import time
import pygame
import random
import whisper
import tempfile
import wave

ACTIVADORES_VALIDOS = [
    "oye kuai",
    "oye qai",
    "oye quai",
    "oye quaii",
    "oye quai!",
    "oye quai kuai",
]

RESPUESTAS_ACTIVACION = [
    "Te escucho.",
    "¿Sí?",
    "Aquí estoy.",
    "Dime.",
    "Conectado, Kuai presente.",
    "Kuai operativo.",
    "Sistema en línea.",
    "Estoy contigo.",
    "¿En qué te puedo ayudar?",
    "Procesando tu atención simbólica.",
]


class WhisperListener:
    def __init__(self, on_text_callback, model_name="tiny", rate=16000, language="es"):
        self.chunk = 1024
        self.rate = rate
        self.channels = 1
        self.format = pyaudio.paInt16
        self.on_text_callback = on_text_callback
        self.model = whisper.load_model(model_name)
        self.cooldown = 2
        self.last_trigger = 0
        self.buffer = b""
        self.running = False
        self._noise_floor = 500.0
        self._speech_frames = 0
        self.language = language

    def transcribe_buffer(self, audio_bytes):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                temp_path = f.name

            with wave.open(temp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.rate)
                wf.writeframes(audio_bytes)

            result = self.model.transcribe(temp_path, language=self.language)
            return result.get("text", "").lower().strip()
        except Exception as e:
            print(f"[LiveListener] ❌ Error al transcribir audio: {e}")
            return ""
        finally:
            try:
                import os

                os.remove(temp_path)
            except Exception as e:
                print(f"[LiveListener] ⚠️ No se pudo eliminar archivo temporal: {e}")

    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 400))
        pygame.display.set_caption("Q•AI Escuchando...")

        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )
        stream.start_stream()

        print("[🌀 Q•AI] Visualizador activo. Esperando voz...")
        clock = pygame.time.Clock()
        self.running = True
        while self.running:
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                self.buffer += data
            except Exception as e:
                print(f"[LiveListener] ❌ Error al leer audio: {e}")
                continue

            audio_np = np.frombuffer(data, np.int16)
            volume = float(np.abs(audio_np).mean())
            # VAD simple con umbral dinámico
            self._noise_floor = 0.95 * self._noise_floor + 0.05 * volume
            silence_threshold = self._noise_floor * 1.6
            is_silence = volume < silence_threshold
            if is_silence:
                self._speech_frames = max(0, self._speech_frames - 1)
            else:
                self._speech_frames = min(1000, self._speech_frames + 1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    pygame.quit()
                    self.running = False
                    return

            screen.fill((0, 0, 0))
            base = 40
            scale = 0 if is_silence else min(int((volume - self._noise_floor) / 25), 140)
            radius = max(35, base + scale)
            pygame.draw.circle(screen, (0, 200, 255), (200, 200), radius)
            pygame.display.flip()

            # Procesar si hay suficiente habla o cada ~5s con habla
            bytes_per_sec = self.rate * 2
            has_speech = self._speech_frames > 10
            enough_audio = len(self.buffer) >= bytes_per_sec * 5
            if has_speech and enough_audio:
                text = self.transcribe_buffer(self.buffer)
                self.buffer = b""
                if text:
                    print(f"[Tú] {text}")
                    for trigger in ACTIVADORES_VALIDOS:
                        if text.startswith(trigger):
                            now = time.time()
                            if now - self.last_trigger > self.cooldown:
                                self.last_trigger = now
                                print(f"[🧠 Q•AI] Activado por: {trigger}")
                                command = text[len(trigger) :].strip()
                                if not command:
                                    self.on_text_callback(
                                        random.choice(RESPUESTAS_ACTIVACION)
                                    )
                                else:
                                    self.on_text_callback(command)
                            break
            clock.tick(30)

    def stop(self):
        self.running = False
