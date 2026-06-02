import whisper

# Convertir audio en texto usando Whisper local
class Transcriber:
    def __init__(self):
        self.model = whisper.load_model("base")  # Puedes usar "tiny", "small", "medium", "large"

    def transcribe(self, audio):
        audio.save("audio.mp3")
        result = self.model.transcribe("audio.mp3", fp16=False)
        return result["text"]
