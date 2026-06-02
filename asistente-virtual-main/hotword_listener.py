import queue
import sounddevice as sd
import vosk
import json
import threading

# Cambia a tu modelo de idioma si deseas otro (como "vosk-model-small-es-0.42")
MODEL_PATH = "vosk-model-small-es-0.42"
TRIGGER_WORD = "moka"
DETECTED_CALLBACK = None

def listen_hotword(callback):
    global DETECTED_CALLBACK
    DETECTED_CALLBACK = callback
    threading.Thread(target=_run_hotword_loop, daemon=True).start()

def _run_hotword_loop():
    q = queue.Queue()
    model = vosk.Model(MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, 16000)

    def callback(indata, frames, time, status):
        if status:
            print("Status:", status)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print(" Esperando la palabra de activación...")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "")
                print(" Reconocido:", text)
                if TRIGGER_WORD in text.lower():
                    print(" ¡Palabra clave detectada!")
                    if DETECTED_CALLBACK:
                        DETECTED_CALLBACK()
