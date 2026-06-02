from gtts import gTTS
import os
import uuid

class TTS():
    def __init__(self):
        pass

    def process(self, text):
        if not text:
            return None
        
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"response_{unique_id}.mp3"
        output_path = os.path.join("static", file_name)

        tts = gTTS(text=text, lang='es', tld='com.mx', slow=False)
        tts.save(output_path)

        return file_name
