# Bibliopedia

API REST para una biblioteca personal: catálogo de libros, reseñas/calificaciones y listas de lectura por usuario.

**Stack:** FastAPI · SQLAlchemy 2.0 · SQLite (por defecto) · pytest

## Requisitos

- Python 3.11+
- (Opcional) Docker

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

Copia o crea un archivo `.env` en la raíz del proyecto con la URL de la base de datos:

```bash
DATABASE_URL=sqlite:///./data/bibliopedia.db
```

`DATABASE_URL` es opcional; si no se define, se usa `sqlite:///./data/bibliopedia.db` por defecto. Para usar otra base (por ejemplo PostgreSQL):

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/bibliopedia
```

## Desarrollo (local)

Ejecuta el servidor desde la raíz del proyecto:

```bash
fastapi dev app/main.py
```

O directamente con uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> ⚠️ Importante: ejecuta siempre desde la raíz del proyecto (donde está la carpeta `app/`) y con el entorno virtual activado.

La API queda disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs` (Swagger UI) u `http://localhost:8000/redoc` (ReDoc).

La aplicación web está disponible en `http://localhost:8000`. Al iniciar con una base vacía, crea un usuario de prueba (`lector@bibliopedia.local`, ID `1`) y un catálogo inicial. Desde la interfaz puedes buscar esos libros, agregarlos a tu lista de lectura, cambiar su estado y guardar reseñas. El usuario de prueba no tiene contraseña ni autenticación: la aplicación todavía no incluye registro o inicio de sesión.

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Interfaz web de Bibliopedia |
| `GET` | `/books/search?keyword={q}` | Busca libros por título, autor o ISBN |
| `GET` | `/books/{id_book}` | Retorna un libro por su id |
| `POST` | `/reviews` | Crea una reseña/calificación |
| `GET` | `/booklists/{user_id}` | Lista de lectura del usuario |
| `PATCH` | `/booklists/{user_id}/books/{book_id}/read-status?is_read={bool}` | Marca un libro como leído/pendiente |

Ejemplos:

```bash
# Buscar libros
curl "http://localhost:8000/books/search?keyword=clean"

# Marcar un libro como leído (regla: solo se puede calificar un libro leído)
curl -X PATCH "http://localhost:8000/booklists/1/books/1/read-status?is_read=true"

# Crear reseña (requiere el libro marcado como leído)
curl -X POST "http://localhost:8000/reviews" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1, "qualifications": 5, "description": "Excelente"}'
```

## Tests

```bash
pytest
```

Los tests usan SQLite en memoria (no tocan tu base local) y cubren modelos, repositorios, servicios y rutas de la API.

## Estructura del proyecto

```
app/
├── main.py             # FastAPI app + handlers de excepciones
├── core/               # Excepciones del dominio
├── models/             # Modelos SQLAlchemy (Base, User, Book, Review, BookList)
├── repositories/       # Conexión/sesión a la BD (database.py) + repositorios
├── services/           # Lógica de negocio (reglas de lectura/calificación)
└── api/                # Router principal + routes/ por recurso
tests/                  # Tests por capa: modelos, repositorios, services, API
data/                   # Base de datos SQLite local (ignorada por git)
```

### Reglas de negocio principales

- Un usuario solo puede calificar un libro **si ya lo marcó como leído**.
- La calificación es obligatoria; la reseña (descripción) es opcional y puede escribirse después.
- Cada usuario solo ve y modifica su propia lista de lectura.

## Producción (Docker)

Construir la imagen:

```bash
docker build -t bibliopedia .
```

Correr el contenedor (pasando la configuración por variables de entorno):

```bash
docker run -p 8000:8000 --env-file .env bibliopedia
```

La API queda disponible en `http://localhost:8000`. Para cambiar el puerto del host:

```bash
docker run -p 8080:8000 bibliopedia
```

En producción puedes sobreescribir `DATABASE_URL` mediante variables de entorno (no olvides montar un volumen para persistir la base SQLite si la usas, p. ej. `-v $(pwd)/data:/app/data`).
