import eventlet
eventlet.monkey_patch()

import os
import json
import threading
import pvporcupine
import pyaudio
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from transcriber import Transcriber
from llm import LLM
from weather import Weather
from tts import TTS
from pc_command import PcCommand

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
llm = LLM()

# Ruta al archivo .ppn personalizado
WAKE_WORD_PATH = "wakeword/Ok-Moka_en_windows_v3_0_0.ppn"
ACCESS_KEY = os.getenv("PICOVOICE_KEY")

# -------------------------------------------------------------
# CUANDO EL FRONTEND PIDA "start-listener", SE EMPIEZA A ESCUCHAR
# -------------------------------------------------------------
@socketio.on('start-listener')
def handle_start_listener():
    print("➡️ Cliente solicitó iniciar listener de wake word")
    start_wake_word_listener()

# -------------------------------------------------------------
# FUNCIÓN DE ESCUCHA CON PORCUPINE
# -------------------------------------------------------------
def start_wake_word_listener():
    def run():
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[WAKE_WORD_PATH]
        )

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("✅ Listener de 'ok moka' activo")

        try:
            while True:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = [int.from_bytes(pcm[i:i+2], byteorder="little", signed=True)
                       for i in range(0, len(pcm), 2)]

                if porcupine.process(pcm) >= 0:
                    print("🎤 Activación detectada: 'ok moka'")

                    # Pedir al frontend que inicie grabación
                    socketio.emit("activar_microfono", {"flag": 1})

                    # Solo se dice “Te escucho, señor” al inicio del ciclo
                    tts_file = TTS().process("Te escucho, señor.")
                    if tts_file:
                        socketio.emit("reproducir_audio", {"file": tts_file})

                    break

        except Exception as e:
            print("❌ Error en Porcupine:", e)

        finally:
            audio_stream.stop_stream()
            audio_stream.close()
            pa.terminate()
            porcupine.delete()
            print("🛑 Porcupine detenido")

    threading.Thread(target=run, daemon=True).start()

# -------------------------------------------------------------
# RENDER DEL FRONTEND
# -------------------------------------------------------------
@app.route("/")
def index():
    return render_template("recorder.html")

# -------------------------------------------------------------
# RECIBIR AUDIO DEL USUARIO -> PROCESAR -> GENERAR RESPUESTA
# -------------------------------------------------------------
@app.route("/audio", methods=["POST"])
def audio():
    audio = request.files.get("audio")
    text = Transcriber().transcribe(audio)
    print(f"📝 Texto recibido: {text}")
    print("🧠 Procesando entrada con Gemini...")

    # Reiniciar memoria si se detecta comando especial
    if "reinicio de emergencia" in text.lower():
        llm.reset_memory()
        final_response = "Memoria reiniciada, señor."
        tts_file = TTS().process(final_response)

        # Volver a escuchar automáticamente
        socketio.emit("iniciar_escucha_nuevamente")

        return {"result": "ok", "text": final_response, "file": tts_file}

    # Procesar funciones del modelo
    function_name, args, message = llm.process_functions(text)

    if function_name:
        if function_name == "get_weather":
            function_response = Weather().get(args["ubicacion"])
            final_response = llm.process_response(
                text, message, function_name, json.dumps(function_response)
            )
        elif function_name == "open_chrome":
            PcCommand().open_chrome(args.get("website"))
            final_response = f"Listo, ya abrí el sitio {args.get('website')}, señor."
        else:
            final_response = "Función detectada, pero no implementada, señor."
    else:
        print("🧩 Enviando mensaje a LLaMA 3 local...")
        final_response = llm.respuesta_natural(text) or "No entendí bien eso, señor."

    # Generar voz
    tts_file = TTS().process(final_response)

    # 🔁 Después de hablar, volver al modo de escucha
    socketio.emit("iniciar_escucha_nuevamente")

    return {"result": "ok", "text": final_response, "file": tts_file}

# -------------------------------------------------------------
# ARRANQUE
# -------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Iniciando Moka en Flask con SocketIO...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

print("tu asistente yace en http://127.0.0.1:5000")

