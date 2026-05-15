from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

# Importamos tus componentes estrella 🌟
from database import inicializar_db, guardar_mensaje, obtener_historial, obtener_todas_las_sesiones
from graph_agent import inicializar_agente_graph_rag, cadena_contextualizadora

app = FastAPI(
    title="API de Agente GraphRAG - Repositorio IA",
    description="Backend para la consulta de publicaciones académicas usando Neo4j y Gemini"
)

# 🚨 CRÍTICO: Configuración de CORS
# Como tu Frontend (React) correrá en un puerto (ej. 3000) y FastAPI en otro (8000),
# si no pones esto, el navegador bloqueará las peticiones por seguridad.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción pones la URL de tu React, "*" es libre para desarrollo local
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
    """1. Devuelve la lista de todos los IDs de sesiones previas para la barra lateral [cite: 43]"""
    return {"sessions": obtener_todas_las_sesiones()}

@app.get("/api/chats/{session_id}", tags=["Chats"])
def ver_detalle_chat(session_id: str):
    """2. Devuelve los mensajes de un chat específico al seleccionarlo [cite: 44]"""
    registros = obtener_historial(session_id)
    # Formateamos la data de SQLite a un JSON amigable para React
    historial_formateado = [{"role": rol, "content": contenido} for rol, contenido in registros]
    return {"session_id": session_id, "history": historial_formateado}

@app.post("/api/chats/{session_id}/message", tags=["Agente"])
def enviar_mensaje_agente(session_id: str, input_data: MessageInput):
    """3. Recibe una pregunta, re-inyecta el contexto de SQLite, consulta al grafo y responde [cite: 24, 30, 37, 42]"""
    if not agente_rag:
        raise HTTPException(status_code=500, detail="El agente GraphRAG no está inicializado.")
    
    pregunta_usuario = input_data.message.strip()
    if not pregunta_usuario:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    try:
        # A. Cargar el historial desde SQLite para re-inyectar el contexto [cite: 37]
        registros_viejos = obtener_historial(session_id)
        historial_chat = []
        for rol, contenido in registros_viejos:
            if rol == "human":
                historial_chat.append(HumanMessage(content=contenido))
            elif rol == "ai":
                historial_chat.append(AIMessage(content=contenido))

        # B. Aplicar ventana deslizante (Capa 2) y contextualizar si hay pasado [cite: 30, 52]
        if len(historial_chat) > 0:
            pregunta_final = cadena_contextualizadora.invoke({
                "chat_history": historial_chat[-4:],  # Mandamos solo los últimos 4 para ahorrar tokens
                "question": pregunta_usuario
            })
        else:
            pregunta_final = pregunta_usuario

        # C. Invocar al Agente para que traduzca a Cypher, vaya a Neo4j y responda [cite: 24]
        respuesta_agente = agente_rag.invoke({"query": pregunta_final})
        resultado_texto = respuesta_agente["result"]

        # D. Persistencia en SQLite (Capa 3): Guardamos la pregunta real y el marcador liviano [cite: 35]
        guardar_mensaje(session_id, "human", pregunta_usuario)
        guardar_mensaje(session_id, "ai", "Entendido. Te mostré los resultados correspondientes filtrados en el grafo.")

        # E. Le devolvemos al Frontend el texto real para que lo pinte en pantalla [cite: 42]
        return {
            "session_id": session_id,
            "user_message": pregunta_usuario,
            "agent_response": resultado_texto
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la consulta: {str(e)}")