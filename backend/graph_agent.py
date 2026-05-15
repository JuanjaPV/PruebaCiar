import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain
# 🛠️ Importamos la función de tu provider estrella
from graph_provider import obtener_grafo_ia
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

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
1. Si el contexto contiene información útil, redacta una respuesta amigable, bien estructurada y detailed en español.
2. Si el contexto está completamente vacío, es una lista vacía `[]`, o no contiene datos relacionados con la pregunta, NO inventes nada. Responde exactamente con este formato:
   "Lo siento, actualmente no tengo registros en la base de datos que coincidan con '[aquí repite el término buscado por el usuario]'. Por favor, verifica que el nombre esté bien escrito (respetando mayúsculas y tildes) o intenta con otra consulta sobre áreas como IA Generativa, Machine Learning o Robótica."
"""

PROMPT_QA_PERSONALIZADO = PromptTemplate(
    input_variables=["context", "question"], 
    template=plantilla_qa
)

# ==============================================================================
# 🌟 INSTANCIA GLOBAL DE GEMINI (Centralizado para importación externa)
# ==============================================================================
# Al dejarlo global, main.py lo puede importar sin problemas para su aduana de control
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

instruccion_contexto = """Dado el siguiente historial de conversación y una pregunta de seguimiento del usuario, 
reformula la pregunta para que sea una consulta independiente y explícita que se pueda entender 
SIN necesidad de ver el historial. 

⚠️ REGLA CRÍTICA DE REFORMULACIÓN:
Mantén los términos técnicos, siglas, acrónimos y nombres propios EXACTAMENTE igual a como se mencionaron en la conversación. 
Por ejemplo:
- Si el usuario dice "NLP", mantén "NLP". NO lo expandas a "Procesamiento de Lenguaje Natural".
- Si dice "IA Generativa", mantén "IA Generativa".
Respeta mayúsculas, minúsculas y siglas de los conceptos clave para no romper las búsquedas.

NO respondas la pregunta, solo reformúlala en español."""

prompt_contexto = ChatPromptTemplate.from_messages([
    ("system", instruccion_contexto),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# Reutilizamos la misma instancia global de 'llm' aquí
cadena_contextualizadora = prompt_contexto | llm | StrOutputParser()


def inicializar_agente_graph_rag():
    """
    Inicializa la cadena GraphCypherQAChain acoplada con el grafo de Neo4j
    reutilizando la instancia global del LLM.
    """
    grafo = obtener_grafo_ia()
    
    if not grafo:
        print("❌ No se pudo inicializar el agente porque falló la conexión al grafo.")
        return None
        
    # Usamos el 'llm' global que ya declaramos arriba
    cadena_ia = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=grafo,
        verbose=True,
        allow_dangerous_requests=True, 
        qa_prompt=PROMPT_QA_PERSONALIZADO,
        top_k=50  
    )
    
    return cadena_ia

# ==============================================================================
# Laboratorio de pruebas interactivo en la Terminal con Memoria Contextual
# ==============================================================================
if __name__ == "__main__":
    print(" Inicializando Agente GraphRAG con Gemini...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print(" Error: No se encontró GOOGLE_API_KEY en el archivo .env")
        exit(1)
        
    agente = inicializar_agente_graph_rag()
    
    if agente:
        historial_chat = []

        print("\n ¡Agente de IA operativo y conectado a AuraDB (Con Memoria de Contexto Opciones de Ahorro)!")
        print("Escribe tu pregunta sobre los datos del grafo (o escribe 'salir' para terminar):")
        print("---------------------------------------------------------------------------------")
        
        while True:
            pregunta_usuario = input("\n👤 Tú: ")
            if pregunta_usuario.lower() in ["salir", "exit", "quit"]:
                print(" ¡Nos vemos! Apagando agente de IA.")
                break
                
            if not pregunta_usuario.strip():
                continue
                
            try:
                if len(historial_chat) > 0:
                    pregunta_final = cadena_contextualizadora.invoke({
                        "chat_history": historial_chat[-4:],  
                        "question": pregunta_usuario
                    })
                else:
                    pregunta_final = pregunta_usuario

                print("🧠 Gemini procesando e iterando con el grafo...")
                
                respuesta = agente.invoke({"query": pregunta_final})
                
                print("\n🤖 Agente:")
                print(respuesta["result"])
                
                historial_chat.append(HumanMessage(content=pregunta_usuario))
                historial_chat.append(AIMessage(content="Entendido. Te mostré los resultados correspondientes filtrados en el grafo."))
                
            except Exception as e:
                print(f"\n❌ Ocurrió un error al procesar la consulta: {e}")