import React from 'react';

export default function Sidebar({ sessions, currentSessionId, onSelectChat, onNewChat }) {
  return (
    <div style={styles.sidebar}>
      <button onClick={onNewChat} style={styles.newChatBtn}>
        ➕ Nuevo Chat
      </button>
      <div style={styles.sessionList}>
        <p style={styles.sidebarTitle}>Chats Anteriores</p>
        {sessions.length === 0 ? (
          <p style={styles.noChats}>No hay chats grabados</p>
        ) : (
          sessions.map((id) => (
            <button
              key={id}
              onClick={() => onSelectChat(id)}
              style={{
                ...styles.sessionItem,
                backgroundColor: currentSessionId === id ? '#343541' : 'transparent'
              }}
            >
              💬 {id}
            </button>
          ))
        )}
      </div>
    </div>
  );
}

const styles = {
  sidebar: { width: '260px', backgroundColor: '#202123', display: 'flex', flexDirection: 'column', padding: '10px', boxSizing: 'border-box' },
  newChatBtn: { width: '100%', padding: '12px', backgroundColor: 'transparent', color: '#fff', border: '1px solid #4d4d4f', borderRadius: '5px', cursor: 'pointer', textAlign: 'left', fontSize: '14px', marginBottom: '20px' },
  sessionList: { flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '5px' },
  sidebarTitle: { fontSize: '12px', color: '#8e8ea0', fontWeight: 'bold', margin: '0 0 10px 5px', textTransform: 'uppercase' },
  noChats: { fontSize: '13px', color: '#6f707e', paddingLeft: '5px' },
  sessionItem: { width: '100%', padding: '10px', color: '#ececf1', border: 'none', borderRadius: '5px', cursor: 'pointer', textAlign: 'left', fontSize: '13px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }
};