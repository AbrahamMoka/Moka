import customtkinter as ctk
import threading
import time
import os
import wave
import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model
from dotenv import load_dotenv
from transcriber import Transcriber
from llm import generar_respuesta_local

# --- CORRECCIÓN PARA LEER EL .ENV SIEMPRE ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_env = os.path.join(directorio_actual, ".env")
load_dotenv(ruta_env)
# --------------------------------------------

# --- 1. Configuración Visual ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MokaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Moka - Sistema Central")
        self.geometry("450x550")
        
        self.label_titulo = ctk.CTkLabel(self, text="MOKA OS", font=("Consolas", 24, "bold"), text_color="#00ffcc")
        self.label_titulo.pack(pady=20)

        self.label_estado = ctk.CTkLabel(self, text="Estado: Iniciando...", font=("Consolas", 14))
        self.label_estado.pack(pady=5)

        self.consola_texto = ctk.CTkTextbox(self, width=400, height=300, font=("Consolas", 12))
        self.consola_texto.pack(pady=10)
        self.escribir_en_consola("Sistema operativo cargado.\nCargando motor auditivo (Whisper)...")

        # Cargamos Whisper
        self.transcriber = Transcriber()
        self.escribir_en_consola("Whisper cargado con éxito. Oídos en línea.")

        self.boton_escuchar = ctk.CTkButton(self, text="Forzar Escucha", command=self.accion_manual)
        self.boton_escuchar.pack(pady=10)

        # --- Iniciar el "Cerebro" en el fondo ---
        self.iniciar_hilo_escucha()

    def escribir_en_consola(self, texto):
        self.consola_texto.insert("end", texto + "\n\n")
        self.consola_texto.see("end")

    def accion_manual(self):
        self.escribir_en_consola("Botón presionado. (Función de forzado pendiente)")

    def iniciar_hilo_escucha(self):
        self.label_estado.configure(text="Estado: Esperando 'Moka'...", text_color="green")
        hilo = threading.Thread(target=self.bucle_openwakeword_real, daemon=True)
        hilo.start()

    def bucle_openwakeword_real(self):
        """El nuevo cerebro auditivo 100% local con openWakeWord"""
        # Ruta a tu futuro modelo
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        WAKE_WORD_PATH = os.path.join(directorio_actual, "wakeword", "moka.onnx")

        self.escribir_en_consola("Cargando modelo openWakeWord (Descargando dependencias base si es necesario)...")
        
        # --- SOLUCIÓN: Descargar el melspectrogram faltante y forzar el uso de ONNX ---
        openwakeword.utils.download_models()
        oww_model = Model(wakeword_models=[WAKE_WORD_PATH], inference_framework="onnx")
        # ------------------------------------------------------------------------------

        FORMAT = pyaudio.paInt16
        # ... (todo el resto de tu código hacia abajo se queda exactamente igual)
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1280 # openWakeWord procesa en bloques de 1280

        pa = pyaudio.PyAudio()
        stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        self.label_estado.configure(text="Estado: Esperando 'Moka'...", text_color="green")

        while True:
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_np = np.frombuffer(audio_data, dtype=np.int16)

            # Le pasamos el audio a la IA
            prediction = oww_model.predict(audio_np)

            # Buscamos si detectó la palabra con más de 50% de seguridad
            for mdl in oww_model.prediction_buffer.keys():
                if prediction[mdl] > 0.5:
                    self.label_estado.configure(text="Estado: ¡Escuchando orden!", text_color="#00ffcc")
                    self.escribir_en_consola("✅ Moka detectada. Te escucho (5 segundos)...")
                    
                    stream.stop_stream()
                    
                    archivo_audio = self.grabar_orden_pyaudio(pa, duracion=5)
                    
                    self.label_estado.configure(text="Estado: Transcribiendo...", text_color="yellow")
                    resultado = self.transcriber.model.transcribe(archivo_audio, fp16=False)
                    texto_usuario = resultado["text"].strip()

                    if texto_usuario:
                     # Imprimimos lo que dijiste tú
                     self.escribir_en_consola(f"[Señor]: {texto_usuario}")

                     # Cambiamos el estado para saber que la IA está pensando
                     self.label_estado.configure(text="Estado: Procesando respuesta...", text_color="orange")

                     # Mandamos tu texto al cerebro de Qwen 2.5
                     respuesta_moka = generar_respuesta_local(texto_usuario)

                     # Imprimimos la respuesta de Moka
                     self.escribir_en_consola(f"[Moka]: {respuesta_moka}")

                    else:
                     self.escribir_en_consola("[Moka]: No logré escuchar nada, Señor.")
                     
                    
                    # Limpiamos la memoria auditiva para que no se active dos veces seguidas
                    oww_model.reset()
                    
                    self.label_estado.configure(text="Estado: Esperando 'Moka'...", text_color="green")
                    stream.start_stream()

    def grabar_orden_pyaudio(self, pa, duracion=5):
        """Función para grabar temporalmente la voz y mandarla a Whisper"""
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        
        stream_grabacion = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        
        for _ in range(0, int(RATE / CHUNK * duracion)):
            data = stream_grabacion.read(CHUNK)
            frames.append(data)
            
        stream_grabacion.stop_stream()
        stream_grabacion.close()
        
        nombre_archivo = "orden_temporal.wav"
        wf = wave.open(nombre_archivo, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pa.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return nombre_archivo

if __name__ == "__main__":
    app = MokaApp()
    app.mainloop()