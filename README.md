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

