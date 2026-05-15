const BASE_URL = 'http://127.0.0.1:8000/api';

export const apiService = {
  // 1. GET /api/chats -> Trae la lista de sesiones previas para la barra lateral
  async listarChats() {
    const response = await fetch(`${BASE_URL}/chats`);
    if (!response.ok) throw new Error('Error al obtener el historial de sesiones');
    return response.json(); 
  },

  // 2. GET /api/chats/{session_id} -> Recupera el historial de mensajes de un chat específico
  async obtenerDetalleChat(sessionId) {
    const response = await fetch(`${BASE_URL}/chats/${sessionId}`);
    if (!response.ok) throw new Error('Error al obtener el detalle del chat');
    return response.json(); 
  },

  // 3. POST /api/chats/{session_id}/message -> Envía la pregunta a Gemini + Neo4j
  async enviarMensaje(sessionId, mensaje) {
    const response = await fetch(`${BASE_URL}/chats/${sessionId}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: mensaje }),
    });
    if (!response.ok) throw new Error('Error en la respuesta del agente');
    return response.json(); 
  }
};