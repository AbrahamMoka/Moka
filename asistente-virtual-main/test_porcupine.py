import os
import pvporcupine
import pyaudio
from dotenv import load_dotenv

load_dotenv()

WAKE_WORD_PATH = "wakeword/Ok-Moka_en_windows_v3_0_0.ppn"
ACCESS_KEY = os.getenv("PICOVOICE_KEY")

porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keyword_paths=[WAKE_WORD_PATH]
)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("🟡 Diga 'ok moka'...")

try:
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = [int.from_bytes(pcm[i:i + 2], byteorder='little', signed=True) for i in range(0, len(pcm), 2)]
        if porcupine.process(pcm) >= 0:
            print("✅ ¡Palabra clave detectada!")
except KeyboardInterrupt:
    print("Saliendo...")
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
