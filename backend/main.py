from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

# Importamos tus componentes estrella 🌟
from database import inicializar_db, guardar_mensaje, obtener_historial, obtener_todas_las_sesiones
# 💡 NOTA: Asegúrate de que en tu 'graph_agent.py' tengas expuesta la variable de tu modelo (ej: llm = ChatGoogleGenerativeAI(...))
from graph_agent import inicializar_agente_graph_rag, cadena_contextualizadora, llm 

# Rediseñamos el prompt para que actúe como un enrutador (Router) ultra rápido y binario
PROMPT_FILTRO_DOMINIO = """
Analiza la siguiente pregunta del usuario y determina si está relacionada con el dominio de nuestro repositorio de publicaciones de Inteligencia Artificial (artículos científicos, autores, revistas, temas como NLP, Computer Vision, Machine Learning, etc.).

REGLA CRÍTICA DE CONTROL:
- Si la pregunta es de cultura general, geografía (ej: "¿cuál es la capital de Francia?"), chistes, saludos o cualquier tema fuera de la IA académica, responde ÚNICAMENTE con la palabra clave: OUT_OF_DOMAIN
- Si la pregunta está perfectamente dentro del dominio del repositorio de IA, responde ÚNICAMENTE con la palabra: VALIDO

Pregunta del usuario: {pregunta}
Respuesta:"""

app = FastAPI(
    title="API de Agente GraphRAG - Repositorio IA",
    description="Backend para la consulta de publicaciones académicas usando Neo4j y Gemini"
)

# Configuración de CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos la DB de SQLite y el Agente RAG al arrancar
inicializar_db()
agente_rag = inicializar_agente_graph_rag()

# Modelo para validar el JSON que nos mandará el Frontend
class MessageInput(BaseModel):
    message: str

@app.get("/api/chats", tags=["Chats"])
def listar_chats():
    """1. Devuelve la lista de todos los IDs de sesiones previas para la barra lateral"""
    return {"sessions": obtener_todas_las_sesiones()}

@app.get("/api/chats/{session_id}", tags=["Chats"])
def ver_detalle_chat(session_id: str):
    """2. Devuelve los mensajes de un chat específico al seleccionarlo"""
    registros = obtener_historial(session_id)
    historial_formateado = [{"role": rol, "content": contenido} for rol, contenido in registros]
    return {"session_id": session_id, "history": historial_formateado}

@app.post("/api/chats/{session_id}/message", tags=["Agente"])
def enviar_mensaje_agente(session_id: str, input_data: MessageInput):
    """3. Recibe una pregunta, filtra fuera de dominio, consulta al grafo si es válida y responde"""
    if not agente_rag:
        raise HTTPException(status_code=500, detail="El agente GraphRAG no está inicializado.")
    
    pregunta_usuario = input_data.message.strip()
    if not pregunta_usuario:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    try:
        # A. Cargar el historial desde SQLite para re-inyectar el contexto
        registros_viejos = obtener_historial(session_id)
        historial_chat = []
        for rol, contenido in registros_viejos:
            if rol == "human":
                historial_chat.append(HumanMessage(content=contenido))
            elif rol == "ai":
                historial_chat.append(AIMessage(content=contenido))

        # B. Aplicar ventana deslizante (Capa 2) y contextualizar si hay pasado
        if len(historial_chat) > 0:
            pregunta_final = cadena_contextualizadora.invoke({
                "chat_history": historial_chat[-4:],  
                "question": pregunta_usuario
            })
        else:
            pregunta_final = pregunta_usuario

        # 🚨 FILTRO CRÍTICO: Evaluación inmediata de Dominio (Evita alucinaciones y latencia)
        # 1. Le pedimos la respuesta cruda a Gemini
        respuesta_filtro = llm.invoke(PROMPT_FILTRO_DOMINIO.format(pregunta=pregunta_final))
        content_filtro = respuesta_filtro.content

        # 2. Convertimos el contenido a texto plano de forma segura (por si viene como lista o string)
        if isinstance(content_filtro, list):
            texto_evaluacion = "".join([bloque if isinstance(bloque, str) else bloque.get("text", "") for bloque in content_filtro])
        else:
            texto_evaluacion = str(content_filtro)

        evaluacion = texto_evaluacion.strip()

        # 3. Validamos si está fuera de dominio
        if "OUT_OF_DOMAIN" in evaluacion:
            mensaje_generico = (
                "Lo siento, actualmente no tengo registros en la base de datos que coincidan con tu consulta. "
                "Como agente especializado en el repositorio de IA, solo puedo responder preguntas relacionadas "
                "con publicaciones científicas, autores, revistas o áreas de Inteligencia Artificial."
            )
            
            # Guardamos la interacción en SQLite de forma limpia
            guardar_mensaje(session_id, "human", pregunta_usuario)
            guardar_mensaje(session_id, "ai", mensaje_generico)
            
            # Retornamos al Frontend a la velocidad de la luz
            return {
                "session_id": session_id,
                "user_message": pregunta_usuario,
                "agent_response": mensaje_generico
            }

        # C. Si la pregunta es VALIDA, sigue el flujo normal al Grafo
        respuesta_agente = agente_rag.invoke({"query": pregunta_final})
        resultado_texto = respuesta_agente["result"]

        # D. Persistencia en SQLite si el query al grafo fue exitoso
        guardar_mensaje(session_id, "human", pregunta_usuario)
        guardar_mensaje(session_id, "ai", resultado_texto)

        # E. Le devolvemos al Frontend la respuesta real de tu GraphRAG
        return {
            "session_id": session_id,
            "user_message": pregunta_usuario,
            "agent_response": resultado_texto
        }

    except Exception as e:
        print("🔴 ERROR REAL EN EL BACKEND:", str(e))
        
        # Si el error es por culpa de la cuota de Google (Error 429 / Resource Exhausted)
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            mensaje_error_api = (
                "⚠️ Servicio temporalmente degradado: El proveedor del modelo de lenguaje (Google Gemini API) "
                "ha alcanzado el límite de cuota para esta clave de desarrollo. La arquitectura GraphRAG y "
                "la base de datos Neo4j están operativas, pero las respuestas del LLM están pausadas por el proveedor."
            )
            # Guardamos el estado del error en SQLite para que el historial sea coherente
            guardar_mensaje(session_id, "human", pregunta_usuario)
            guardar_mensaje(session_id, "ai", mensaje_error_api)
            
            return {
                "session_id": session_id,
                "user_message": pregunta_usuario,
                "agent_response": mensaje_error_api
            }
            
        # Para cualquier otro error inesperado, mantén el comportamiento estándar
        raise HTTPException(status_code=500, detail=f"Error al procesar la consulta: {str(e)}")