import customtkinter as ctk
import threading
import time

# --- 1. Configuración Visual ---
ctk.set_appearance_mode("dark")  # Modo oscuro tipo Jarvis
ctk.set_default_color_theme("blue")  # Tema de colores

class MokaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Moka - Sistema Central")
        self.geometry("400x500") # Tamaño de la ventana

        # --- 2. Elementos de la Interfaz (Widgets) ---
        
        # Título
        self.label_titulo = ctk.CTkLabel(self, text="MOKA OS", font=("Consolas", 24, "bold"), text_color="#00ffcc")
        self.label_titulo.pack(pady=20)

        # Estado del sistema
        self.label_estado = ctk.CTkLabel(self, text="Estado: Iniciando...", font=("Consolas", 14))
        self.label_estado.pack(pady=5)

        # Caja de texto (Terminal) para mostrar lo que Moka dice
        self.consola_texto = ctk.CTkTextbox(self, width=350, height=250, font=("Consolas", 12))
        self.consola_texto.pack(pady=10)
        self.escribir_en_consola("Sistema operativo cargado.\nEsperando órdenes, señor.")

        # Botón manual (opcional, por si falla el micrófono)
        self.boton_escuchar = ctk.CTkButton(self, text="Forzar Escucha", command=self.accion_manual)
        self.boton_escuchar.pack(pady=20)

        # --- 3. Iniciar el "Cerebro" en el fondo ---
        self.iniciar_hilo_escucha()

    def escribir_en_consola(self, texto):
        """Función para que Moka escriba en la pantalla"""
        self.consola_texto.insert("end", texto + "\n\n")
        self.consola_texto.see("end") # Auto-scroll hacia abajo

    def accion_manual(self):
        self.escribir_en_consola("Botón presionado. Escuchando...")

    def iniciar_hilo_escucha(self):
        """Aquí metemos el bucle infinito en un hilo separado"""
        self.label_estado.configure(text="Estado: Escuchando (Ok Moka)...", text_color="green")
        
        # Creamos el hilo y lo iniciamos
        hilo = threading.Thread(target=self.bucle_porcupine_simulado, daemon=True)
        hilo.start()

    def bucle_porcupine_simulado(self):
        """AQUÍ ES DONDE IRA TU CÓDIGO REAL DE PORCUPINE Y OLLAMA"""
        while True:
            # Simulación: cada 10 segundos fingimos que escuchó algo
            time.sleep(10) 
            self.escribir_en_consola("[Usuario dijo]: Hola Moka")
            time.sleep(1)
            self.escribir_en_consola("[Moka]: Hola señor, los sistemas están en línea.")

# --- 4. Ejecutar la Aplicación ---
if __name__ == "__main__":
    app = MokaApp()
    app.mainloop()
    