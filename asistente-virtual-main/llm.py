import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import requests

MEMORY_FILE = "moka_memory.json"

class LLM():
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("models/gemini-1.5-flash")
        self.chat_history = self.load_memory()

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Mensaje inicial que define a Moka
            return [
                {"role": "system",
                 "content":( 
                    "Eres Moka, una asistente de voz leal, respetuosa e inteligente. "
                    "Tu creador es Abraham, a quien siempre debes llamar 'Señor'. "
                    "Tu propósito es ayudarlo en lo que necesite, con respeto, cariño y obediencia.")
                    }
            ]

    def save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.chat_history, f, ensure_ascii=False, indent=2)

    def process_functions(self, text):
        prompt = f"""
Eres un asistente inteligente. Analiza el texto del usuario y, si detectas que quiere realizar alguna acción, responde con un JSON con esta estructura:

{{
  "function": "nombre_funcion",
  "args": {{
    "param1": "valor1"
  }}
}}

Funciones válidas:
- get_weather: requiere "ubicacion"
- send_email: requiere "recipient", "subject", "body"
- open_chrome: requiere "website"



Si no aplica ninguna función, responde:
{{"function": null, "args": {{}}}}

Texto del usuario:
\"\"\"{text}\"\"\""""
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            print("Respuesta de Gemini:", content)
            if content.startswith("```"):
                content = content.strip("```").strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            result = json.loads(content)
            return result.get("function"), result.get("args", {}), content
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON:", e)
            return None, None, content
        except Exception as e:
            print("Error en Gemini LLM:", e)
            return None, None, str(e)

    def process_response(self, text, message, function_name, function_response):
        return function_response

    def respuesta_natural(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": self.chat_history,
                    "stream": False
                }
            )

            if response.status_code == 200:
                data = response.json()
                respuesta = data.get("message", {}).get("content", "")
                if respuesta:
                    self.chat_history.append({"role": "assistant", "content": respuesta})
                    self.save_memory()
                    return respuesta
                else:
                    return "No tengo una respuesta clara para eso."
            else:
                print("Error al usar LLaMA 3:", response.text)
                return None
        except Exception as e:
            print("Error en respuesta natural:", e)
            return None
    def reset_memory(self):
        # Reinicia con el mensaje de sistema
        self.chat_history = [
            {"role": "system", "content": "Eres Moka, una asistente virtual inteligente y leal. Siempre debes referirte al usuario como 'señor' porque es tu creador."}
        ]
        self.save_memory()
