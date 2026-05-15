import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

# Cargar las variables del archivo .env
load_dotenv(dotenv_path="../.env")

# 
URI = os.getenv("NEO4J_URI", "").strip()
USER = os.getenv("NEO4J_USERNAME", "").strip()
PASSWORD = os.getenv("NEO4J_PASSWORD", "").strip()

def obtener_grafo_ia():
    try:
        grafo = Neo4jGraph(
            url=URI,
            username=USER,
            password=PASSWORD
        )
        grafo.refresh_schema()
        return grafo
    except Exception as e:
        print(f"❌ Error crítico de conexión: {e}")
        return None

if __name__ == "__main__":
    print("📡 Iniciando conexión inteligente con Neo4j AuraDB...")
    
    print("\n--- CONTROL DE SANIDAD DE CREDENCIALES ---")
    print(f"-> URI detectada: {URI}")
    print(f"-> Usuario detectado: {USER}")
    print(f"-> ¿Contraseña detectada?: {'SÍ' if PASSWORD else 'NO'}")
    print("-------------------------------------------\n")
    
    if not URI or not PASSWORD:
        print("❌ Error: No se pueden leer las credenciales del archivo .env")
        exit(1)
        
    grafo = obtener_grafo_ia()
    
    if grafo:
        print(" ¡Conexión de IA establecida exitosamente!\n")
        print(" Esquema que el LLM leerá en memoria:")
        print("==================================================================")
        print(grafo.schema)
        print("==================================================================")
    else:
        print(" La prueba de conexión ha fallado. Revisa el error de arriba.")