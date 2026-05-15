import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain
# 🛠️ Importamos la función de tu provider estrella
from graph_provider import obtener_grafo_ia
from langchain_core.prompts import PromptTemplate
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

# 1. Cargar el entorno de forma absoluta calculando la ruta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "../.env"))

# 2. Definimos una plantilla con instrucciones estrictas en español
plantilla_qa = """Eres un asistente virtual experto en análisis de datos para el repositorio de publicaciones de Inteligencia Artificial.
Tu objetivo es responder a la consulta del usuario de manera profesional, clara y educada, utilizando ÚNICAMENTE el contexto provisto extraído de la base de datos de grafos (Neo4j).

Contexto obtenido del grafo:
{context}

Pregunta del usuario: {question}

⚠️ REGLAS CRÍTICAS DE RESPUESTA:
1. Si el contexto contiene información útil, redacta una respuesta amigable, bien estructurada y detallada en español.
2. Si el contexto está completamente vacío, es una lista vacía `[]`, o no contiene datos relacionados con la pregunta, NO inventes nada. Responde exactamente con este formato:
   "Lo siento, actualmente no tengo registros en la base de datos que coincidan con '[aquí repite el término buscado por el usuario]'. Por favor, verifica que el nombre esté bien escrito (respetando mayúsculas y tildes) o intenta con otra consulta sobre áreas como IA Generativa, Machine Learning o Robótica."
"""

PROMPT_QA_PERSONALIZADO = PromptTemplate(
    input_variables=["context", "question"], 
    template=plantilla_qa
)
def inicializar_agente_graph_rag():
    """
    Inicializa a Gemini y lo acopla con el grafo de Neo4j
    para traducir lenguaje natural a consultas Cypher.
    """
    # Traemos la conexión limpia del provider
    grafo = obtener_grafo_ia()
    
    if not grafo:
        print("❌ No se pudo inicializar el agente porque falló la conexión al grafo.")
        return None
        
    
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # 
        temperature=0
    )
    
    # Creamos la cadena inteligente de LangChain para grafos
    # verbose=True nos permitirá ver en la terminal la query de Cypher que Gemini inventa en vivo
    cadena_ia = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=grafo,
        verbose=True,
        allow_dangerous_requests=True, 
        qa_prompt=PROMPT_QA_PERSONALIZADO
    )
    
    return cadena_ia

# ==============================================================================
# Laboratorio de pruebas interactivo en la Terminal
# ==============================================================================
if __name__ == "__main__":
    print(" Inicializando Agente GraphRAG con Gemini...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print(" Error: No se encontró GOOGLE_API_KEY en el archivo .env")
        exit(1)
        
    agente = inicializar_agente_graph_rag()
    
    if agente:
        print("\n ¡Agente de IA operativo y conectado a AuraDB!")
        print("Escribe tu pregunta sobre los datos del grafo (o escribe 'salir' para terminar):")
        print("---------------------------------------------------------------------------------")
        
        while True:
            pregunta = input("\n👤 Tú: ")
            if pregunta.lower() in ["salir", "exit", "quit"]:
                print(" ¡Nos vemos! Apagando agente de IA.")
                break
                
            if not pregunta.strip():
                continue
                
            try:
                print("🧠 Gemini procesando e iterando con el grafo...")
                # Invocamos a la cadena inteligente
                respuesta = agente.invoke({"query": pregunta})
                
                print("\n🤖 Agente:")
                print(respuesta["result"])
                
            except Exception as e:
                print(f"\n❌ Ocurrió un error al procesar la consulta: {e}")