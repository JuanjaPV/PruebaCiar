# PruebaCiar
## 📊 Modelo de Grafos Propuesto

Se diseñó e implementó un modelo de datos basado en grafos (Property Graph Model) utilizando **Neo4j AuraDB**. El objetivo del diseño es normalizar el dataset plano original (`publicaciones_ia.csv`), eliminando la redundancia de datos.

![Modelo de Grafo Propuesto](./img/modelo-grafo.png)

### 🧬 Anatomía del Esquema

#### 1. Nodos 
* **`Publicacion`**: Nodo central del dataset. Su clave única (`Key`) es `id_publicacion`. Almacena la propiead titulo y propiedades cuantitativas indexables como `año` (Integer) y `numero_citas` (Integer).
* **`Autor`**: Representa a los investigadores. Clave única: `nombre_autor`.
* **`Institucion`**: Entidad de afiliación. Clave única: `nombre_institucion`. Almacena  la propiedad `pais_institucion`.
* **`Topico`**, **`Palabra_clave`** y **`venue`**: Nodos categóricos y taxonómicos que actúan como índices estructurales para agrupar la producción científica por áreas de IA, etiquetas y medios de difusión respectivamente.

#### 2. Relaciones 
* `(:Autor)-[:ESCRIBIÓ]->(:Publicacion)`: Relación dirigida que incluye la propiedad contextual `orden_autor` (determina autoría principal o secundaria).
* `(:Autor)-[:AFILIADO_A]->(:Institucion)`: a que institucion pertenece el autor.
* `(:Publicacion)-[:PERTENECE_A]->(:Topico)`: Clasificación temática principal del artículo.
* `(:Publicacion)-[:TIENE_TAG]->(:Palabra_clave)`: Busqueda por palabras claves de la publicacion.
* `(:Publicacion)-[:PUBLICADA_EN]->(:venue)`: Donde fue publicada.


### Instrucciones de Setup y Despliegue (Paso a Paso)
Siga estas instrucciones para levantar el entorno de desarrollo local partiendo desde cero de manera idéntica a como fue concebido.

📌 Prerrequisitos
Python 3.10 o superior instalado.

Node.js (v18 o superior) y npm.

Una instancia activa de Neo4j AuraDB Free.

Una API Key activa de Google AI Studio (Gemini).

Paso 1: Clonar el Repositorio

Abra su terminal y clone el proyecto de forma local:

-git clone [https://github.com/JuanjaPV/PruebaCiar.git](https://github.com/JuanjaPV/PruebaCiar.git)
-cd PruebaCiar

Paso 2: Configurar el Entorno Virtual del Backend
Navegue a la carpeta del backend, cree un entorno virtual aislado y actívelo:

En Windows (Git Bash / CMD):

-cd backend
-python -m venv venv
-source venv/Scripts/activate

En macOS / Linux:

-cd backend
-ython -m venv venv
-source venv/bin/activate

Paso 3: Instalar Dependencias del Backend
-pip install fastapi uvicorn pydantic langchain-core langchain-neo4j langchain-google-genai python-dotenv

Paso 4: Configurar Variables de Entorno (.env)
Cree un archivo de configuración llamado .env dentro de la carpeta del backend (backend/.env). Complete la siguiente estructura con sus credenciales de desarrollo correspondientes:

Fragmento de código

Configuración del LLM (Google AI Studio):
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui

Configuración de Base de Datos de Grafos (Neo4j AuraDB):
NEO4J_URI=neo4j+s://xxxxxx.databases.neo4j.io
NEO4J_USERNAME=tu_usuario_aqui
NEO4J_PASSWORD=tu_contraseña_de_auradb_aqui


Paso 5: Inicializar y Ejecutar el Backend
Inicie el servidor de desarrollo ASGI utilizando Uvicorn:

-uvicorn main:app --reload

Al arrancar, el backend ejecutará de forma automática una rutina que crea y configura la base de datos relacional local historial_chats.db en SQLite para el control de la persistencia de mensajería.

Paso 6: Configurar y Ejecutar el Frontend (React)
Abra una nueva pestaña de la terminal y navegue a la carpeta del frontend:

cd frontend
Instale los módulos de Node de forma limpia:
-npm install

Levante el servidor de desarrollo del cliente web:
-npm run dev

Abra su navegador en la dirección local provista (típicamente http://localhost:5173) para interactuar con la interfaz del Agente GraphRAG.



### Extra 1: Guardrails de Seguridad (Defensa Perimetral Híbrida)
Se implementó una arquitectura de seguridad en dos niveles para mitigar vulnerabilidades y blindar la base de datos Neo4j AuraDB contra escrituras o alteraciones maliciosas:

1. **Capa Estricta Determinista (Python Local):** Antes de enviar cualquier consulta a internet, el backend escanea el texto del usuario en milisegundos mediante una función determinista local. Si detecta palabras clave reservadas de Cypher (CREATE, MERGE, DELETE, DROP, SET, REMOVE, LOAD CSV, CALL) o sus equivalentes semánticos en español (BORRAR, ELIMINAR, MODIFICAR, ACTUALIZAR, CREAR), la petición se bloquea con cero costo de tokens y latencia nula, retornando un mensaje restrictivo controlado.

2. **Capa Semántica Avanzada (LLM Aduana)**: Si el input pasa el primer filtro, es evaluado por un prompt clasificador especializado ejecutado por Gemini. Este clasifica el mensaje en tres categorías: MALICIOUS (para inyecciones de prompt latentes, jailbreaks o intentos evasivos de borrado en lenguaje natural como "¿puedes quitar los nodos del 2024?"), OUT_OF_DOMAIN o VALIDO. Las peticiones sospechosas reciben un escudo de contención inmediato, previniendo inyecciones de código destructivo en la base de datos.

###  Extra 2: Manejo de Ventana de Contexto del LLM
"chat_history": historial_chat[-4:]
Para que la cadena_contextualizadora entienda que "esas" se refiere a NLP, matemáticamente solo necesita mirar el turno inmediatamente anterior (1 mensaje humano + 1 respuesta de la IA = 2 mensajes). Al configurar la ventana en -4, se esta dejando 2 turnos completos de interacción IA-Humano, lo cual es un margen de seguridad más que suficiente para resolver cualquier hilo conversacional directo sin arrastrar basura del inicio del chat.

###  Extra 3: Flujo de Agente Mejorado (Arquitectura Asíncrona y Resiliente)
En cumplimiento con la flexibilidad de la rúbrica para proponer mejoras relevantes al flujo, se rediseñó el ciclo de vida de la petición de una estructura lineal a un pipeline optimizado con dos características avanzadas:

1. **Estrategia de Cortocircuito Conversacional (Short-Circuiting):** El flujo de datos no es pasivo. Implementa validaciones perimetrales secuenciales (Capa 1: Determinista local / Capa 2: Semántica por Clasificación). Si la consulta infringe las políticas de seguridad (maliciosa o fuera de dominio), el flujo se interrumpe inmediatamente mediante un *early return*. Esto mitiga por completo el riesgo de alucinación y evita el consumo innecesario de token de las apis free tier

2. **Mecanismo Fail-safe con Persistencia Coherente (Tolerancia a Fallos 429):**
   Debido a las limitaciones de token de las apis free tier de gemini (*Resource Exhausted / Error 429*), el flujo del backend implementa una degradación elegante controlada. Al capturar la excepción del proveedor externo, el sistema no colapsa; genera una respuesta estructurada de contingencia y la persiste activamente en SQLite. Esto asegura que la base de datos local y el estado del frontend se mantengan 100% síncronos y libres de corrupción de datos, permitiendo la continuidad del chat una vez restablecido el servicio.


### Que se quedo afuera y porque
Siguiendo las recomendaciones del propio enunciado de la prueba técnica, decidí priorizar un flujo end-to-end funcional y sólido antes de arriesgar la estabilidad con lógicas complejas de validación sintáctica, semántica contra el esquema o auto-corrección de Cypher. Sin embargo, aprovechando la flexibilidad de la rúbrica para proponer mejoras alternativas, enfoqué el Extra 3 en un problema real y crítico de producción: la tolerancia al Error 429 por límite de cuota y el cortocircuito semántico. Diseñé un pipeline que intercepta peticiones inválidas en el perímetro y degrada el servicio amigablemente sin corromper el historial en SQLite.