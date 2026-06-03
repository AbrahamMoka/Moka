import requests

def generar_respuesta_local(texto_usuario):
    # Esta es la dirección local donde Ollama está escuchando
    url = "http://localhost:11434/api/chat"
    
    # Aquí configuramos a Qwen 2.5 y le damos la personalidad de Moka
    payload = {
        "model": "qwen2.5",
        "messages": [
            {
                "role": "system", 
                "content": "Eres Moka, una asistente virtual avanzada, sarcástica pero muy leal. Responde de manera concisa, natural y en español."
            },
            {
                "role": "user", 
                "content": texto_usuario
            }
        ],
        "stream": False # Falso para que nos dé la respuesta completa de golpe
    }
    
    try:
        respuesta = requests.post(url, json=payload)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return datos["message"]["content"]
        else:
            return f"(Error de conexión con el cerebro local: {respuesta.status_code})"
    except Exception as e:
        return f"(El motor de Ollama parece estar apagado, Señor. Error: {e})"