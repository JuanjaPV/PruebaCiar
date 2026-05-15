import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Cargar el entorno de forma exacta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "../.env"))

API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

print(" --- DIAGNÓSTICO DE TU ENTORNO ---")
if not API_KEY:
    print("❌ Error: No se detecta ninguna GOOGLE_API_KEY en tu .env")
    exit(1)
else:
    
    print(f"🔑 Llave detectada en memoria: {API_KEY[:8]}...{API_KEY[-4:]}")


genai.configure(api_key=API_KEY)

print("\n📡 Conectando con Google AI Studio para listar tus modelos activos...")
try:
    modelos_disponibles = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            
            nombre_limpio = m.name.replace("models/", "")
            modelos_disponibles.append(nombre_limpio)
    
    print("✅ ¡Conexión exitosa! Tu cuenta tiene acceso a estos modelos:")
    print("------------------------------------------------------------")
    for modelo in sorted(modelos_disponibles):
        print(f"  • {modelo}")
    print("------------------------------------------------------------")
    print("💡 Si ves 'gemini-2.0-flash' en la lista, el problema es puramente de cuota temporal.")

except Exception as e:
    print("\n❌ GOOGLE RECHAZÓ LA SOLICITUD:")
    print(f"Detalle del error: {e}")
    print("\n💡 Si aquí te vuelve a salir RESOURCE_EXHAUSTED, tu API Key actual está bloqueada con cuota 0.")