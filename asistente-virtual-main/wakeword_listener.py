import pvporcupine
import pyaudio
import struct
import threading

class WakeWordDetector:
    def __init__(self, callback, keyword_path, access_key):
        self.callback = callback
        self.keyword_path = keyword_path
        self.access_key = access_key
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def _run(self):
        porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[self.keyword_path]
        )

        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        while self.running:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            result = porcupine.process(pcm)
            if result >= 0:
                print("🟢 Wake word detectada: Ok Moka")
                self.callback()

        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
