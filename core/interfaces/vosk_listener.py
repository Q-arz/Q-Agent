# core/interfaces/voice/vosk_listener.py
import vosk
import pyaudio
import json
import numpy as np
import pygame
import time
import random
import os

ACTIVADORES_VALIDOS = ["oye qai", "oye kuai", "oye quai"]
RESPUESTAS_ACTIVACION = ["Te escucho.", "Aquí estoy.", "Dime."]

base_path = os.path.dirname(__file__)
default_model_path = os.path.join(base_path, "voice", "vosk", "model")


class VoskListener:
    def __init__(self, on_text_callback, rate=16000, language="es", model_dir=None):
        self.rate = rate
        self.chunk = 1024
        self.channels = 1
        self.on_text_callback = on_text_callback
        print(f"[Vosk] 📦 Cargando modelo desde: {model_path}")
        self.language = language
        # si hay model_dir explícito úsalo; si no, intenta model_<lang>; fallback al default
        lang_model = os.path.join(base_path, "voice", "vosk", f"model_{self.language}")
        resolved = model_dir or (lang_model if os.path.isdir(lang_model) else default_model_path)
        print(f"[Vosk] 📦 Modelo resuelto: {resolved}")
        self.model = vosk.Model(resolved)
        self.cooldown = 2
        self.last_trigger = 0
        self.running = False
        self._noise_floor = 500.0  # valor inicial, se autoajusta

    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 400))
        pygame.display.set_caption("Q•AI Escuchando (Vosk)...")

        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        rec = vosk.KaldiRecognizer(self.model, self.rate)
        print("[🌀 Q•AI] Vosk activo. Escuchando...")
        clock = pygame.time.Clock()
        self.running = True
        while self.running:
            data = stream.read(self.chunk, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip().lower()

                if text:
                    print(f"[Tú] {text}")
                    for trigger in ACTIVADORES_VALIDOS:
                        if text.startswith(trigger):
                            now = time.time()
                            if now - self.last_trigger > self.cooldown:
                                self.last_trigger = now
                                command = text[len(trigger) :].strip()
                                if not command:
                                    self.on_text_callback(
                                        random.choice(RESPUESTAS_ACTIVACION)
                                    )
                                else:
                                    self.on_text_callback(command)
                            break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    pygame.quit()
                    self.running = False
                    return

            # visual
            audio_np = np.frombuffer(data, np.int16)
            volume = float(np.abs(audio_np).mean())
            # suavizado del nivel (EMA) y umbral de silencio dinámico
            self._noise_floor = 0.95 * self._noise_floor + 0.05 * volume
            silence_threshold = self._noise_floor * 1.6
            is_silence = volume < silence_threshold
            screen.fill((0, 0, 0))
            # limitar el radio para que no explote visualmente
            base = 40
            scale = 0 if is_silence else min(int((volume - self._noise_floor) / 25), 140)
            radius = max(35, base + scale)
            pygame.draw.circle(screen, (200, 50, 255), (200, 200), radius)
            pygame.display.flip()
            clock.tick(30)

    def stop(self):
        self.running = False
