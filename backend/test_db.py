from database import inicializar_db, guardar_mensaje, obtener_historial, obtener_todas_las_sesiones
import os

print("🚀 Iniciando prueba de persistencia en SQLite...")

# 1. Inicializar la base de datos (creará el archivo .db si no existe)
inicializar_db()

# Definimos un ID de sesión de prueba
SESSION_TEST = "chat_test_nlp"

print("\n1. Guardando mensajes de prueba...")
guardar_mensaje(SESSION_TEST, "human", "¿Qué publicaciones hay sobre NLP?")
# Guardamos el marcador de posición ligero como haríamos en producción
guardar_mensaje(SESSION_TEST, "ai", "Entendido. Te mostré los resultados correspondientes filtrados en el grafo.")
print("✅ Mensajes guardados con éxito.")

print("\n2. Recuperando el historial de la sesión...")
historial = obtener_historial(SESSION_TEST)
for rol, contenido in historial:
    print(f"   [{rol.upper()}]: {contenido}")

print("\n3. Recuperando la lista de todos los chats activos...")
sesiones = obtener_todas_las_sesiones()
print(f"   Chats encontrados: {sesiones}")

# Verificación final en el disco
if os.path.exists("historial_chats.db"):
    print("\n🎉 ¡PRUEBA EXITOSA! El archivo 'historial_chats.db' se creó localmente.")
else:
    print("\n❌ Algo falló, no se encuentra el archivo de la base de datos.")