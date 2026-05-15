import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { apiService } from './services/api';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState('');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  // 1. Cargar las sesiones previas en la barra lateral al abrir la página
  useEffect(() => {
    cargarHistorialSesiones();
  }, []);

  const cargarHistorialSesiones = async () => {
    try {
      const data = await apiService.listarChats();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error("⚠️ Error al conectar con el backend para listar sesiones:", err);
    }
  };

  // 2. Cambiar de chat al hacer clic en un ID de la barra lateral
  const manejarSeleccionarChat = async (sessionId) => {
    setCurrentSessionId(sessionId);
    setLoading(true);
    try {
      const data = await apiService.obtenerDetalleChat(sessionId);
      setMessages(data.history || []);
    } catch (err) {
      console.error("⚠️ Error al recuperar el historial del chat:", err);
    } finally {
      setLoading(false);
    }
  };

  // 3. Botón "Nuevo Chat" (Limpia la pantalla y prepara un ID temporal único)
  const manejarNuevoChat = () => {
    const nuevoId = `chat-${Date.now()}`;
    setCurrentSessionId(nuevoId);
    setMessages([]);
  };

  // 4. Enviar mensaje (POST) con actualización optimista en pantalla
  const manejarEnviarMensaje = async () => {
    if (!inputMessage.trim()) return;

    let sessionIdActual = currentSessionId;
    // Si el usuario escribe directo en una pantalla vacía sin crear sesión antes
    if (!sessionIdActual) {
      sessionIdActual = `chat-${Date.now()}`;
      setCurrentSessionId(sessionIdActual);
    }

    const textoUsuario = inputMessage.trim();
    setInputMessage(''); // Limpiar la caja de texto al instante

    // Pintar de inmediato el mensaje del usuario (Fila Humana)
    const historialActualizado = [...messages, { role: 'human', content: textoUsuario }];
    setMessages(historialActualizado);
    setLoading(true);

    try {
      const data = await apiService.enviarMensaje(sessionIdActual, textoUsuario);
      
      // Agregar la respuesta real de Gemini al flujo de la pantalla
      setMessages([...historialActualizado, { role: 'ai', content: data.agent_response }]);
      
      // Refrescar la barra lateral por si es un chat nuevo para que aparezca en la lista
      cargarHistorialSesiones();
    } catch (err) {
      console.error("⚠️ Error al enviar el mensaje al agente:", err);
      setMessages([
        ...historialActualizado, 
        { role: 'ai', content: "❌ Hubo un error de comunicación con el Agente GraphRAG." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.appContainer}>
      {/* Columna Izquierda: Barra Lateral */}
      <Sidebar 
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectChat={manejarSeleccionarChat}
        onNewChat={manejarNuevoChat}
      />

      {/* Columna Derecha: Ventana Principal del Chat */}
      <ChatWindow 
        messages={messages}
        loading={loading}
        inputMessage={inputMessage}
        setInputMessage={setInputMessage}
        onSendMessage={manejarEnviarMensaje}
        currentSessionId={currentSessionId}
      />
    </div>
  );
}

const styles = {
  appContainer: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    fontFamily: 'Arial, sans-serif',
    overflow: 'hidden',
    backgroundColor: '#343541'
  }
};