import React from 'react';

export default function ChatWindow({ 
  messages, 
  loading, 
  inputMessage, 
  setInputMessage, 
  onSendMessage, 
  currentSessionId 
}) {
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSendMessage();
  };

  return (
    <div style={styles.chatArea}>
      {/* Cabecera de la ventana */}
      <div style={styles.header}>
        <h3>Agente GraphRAG 🧠 - {currentSessionId || 'Nueva Sesión'}</h3>
      </div>

      {/* Zona de Mensajes */}
      <div style={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div style={styles.welcomeContainer}>
            <h2>¡Hola! Realiza consultas sobre el repositorio de IA</h2>
            <p>El agente traducirá tu pregunta a un query Cypher y buscará relaciones en Neo4j AuraDB.</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              style={{
                ...styles.messageRow,
                backgroundColor: msg.role === 'human' ? '#343541' : '#444654'
              }}
            >
              <div style={styles.messageContent}>
                <strong style={styles.roleLabel}>
                  {msg.role === 'human' ? '👤 Tú:' : '🤖 Agente:'}
                </strong>
                <span style={styles.messageText}>{msg.content}</span>
              </div>
            </div>
          ))
        )}

        {/* Indicador de carga (Pensando) */}
        {loading && (
          <div style={{ ...styles.messageRow, backgroundColor: '#444654' }}>
            <div style={styles.messageContent}>
              <strong style={styles.roleLabel}>🤖 Agente:</strong>
              <span style={styles.loadingText}>Pensando y consultando al grafo de Neo4j... 🔄</span>
            </div>
          </div>
        )}
      </div>

      {/* Formulario con barra de texto inferior */}
      <form onSubmit={handleSubmit} style={styles.inputForm}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Haz una pregunta (Ej: ¿Qué publicaciones hay sobre NLP?)..."
          style={styles.inputField}
          disabled={loading}
        />
        <button 
          type="submit" 
          style={{
            ...styles.sendBtn,
            backgroundColor: (loading || !inputMessage.trim()) ? '#107d50' : '#19c37d',
            cursor: (loading || !inputMessage.trim()) ? 'not-allowed' : 'pointer'
          }} 
          disabled={loading || !inputMessage.trim()}
        >
          Enviar
        </button>
      </form>
    </div>
  );
}

const styles = {
  chatArea: { flex: 1, display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#343541' },
  header: { padding: '10px 20px', backgroundColor: '#343541', borderBottom: '1px solid #2d2d30', textAlign: 'center', color: '#ececf1' },
  messagesContainer: { flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' },
  welcomeContainer: { flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: '#c5c5d2', textAlign: 'center', padding: '20px' },
  messageRow: { width: '100%', padding: '20px 0', borderBottom: '1px solid #2d2d30' },
  messageContent: { maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '15px', padding: '0 20px', boxSizing: 'border-box' },
  roleLabel: { minWidth: '80px', color: '#d1d5db' },
  messageText: { whiteSpace: 'pre-wrap', lineHeight: '1.5', color: '#ececf1' },
  loadingText: { color: '#9ca3af', fontStyle: 'italic' },
  inputForm: { padding: '20px', backgroundColor: '#343541', display: 'flex', justifyContent: 'center', gap: '10px' },
  inputField: { width: '100%', maxWidth: '750px', padding: '14px', backgroundColor: '#40414f', color: '#fff', border: 'none', borderRadius: '5px', boxShadow: '0 0 15px rgba(0,0,0,0.1)', fontSize: '15px', outline: 'none' },
  sendBtn: { padding: '0 20px', color: '#fff', border: 'none', borderRadius: '5px', fontWeight: 'bold', fontSize: '14px', transition: 'background 0.2s' }
};