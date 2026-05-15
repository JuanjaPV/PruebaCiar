import sqlite3

DB_PATH = "historial_chats.db"

def inicializar_db():
    """Crea la tabla si no existe al arrancar el servidor"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()

def guardar_mensaje(session_id: str, role: str, content: str):
    """Inserta un nuevo mensaje (human o ai) en el chat correspondiente"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO historial (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()

def obtener_historial(session_id: str):
    """Trae los mensajes ordenados para re-inyectarlos al agente"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM historial WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        return cursor.fetchall()  # Devuelve [(role, content), ...]

def obtener_todas_las_sesiones():
    """
    Trae la lista de todos los chat_ids únicos.
    Para el endpoint GET /chats que alimentará la barra lateral en React.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT session_id FROM historial ORDER BY id DESC")
        # El list comprehension limpia las tuplas para devolver una lista de strings limpia: ['chat_nlp', 'chat_ia']
        return [row[0] for row in cursor.fetchall()]