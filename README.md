# Preview Agent
<img width="1600" height="934" alt="imagen" src="https://github.com/user-attachments/assets/ee88096c-d223-4df0-b8f7-5c1b7073858e" />
<img width="1816" height="1066" alt="imagen" src="https://github.com/user-attachments/assets/145f3f3d-9444-4480-bc12-6f3569d2bcfd" />
<img width="1811" height="1063" alt="imagen" src="https://github.com/user-attachments/assets/6d2f0e5e-b5ec-49b8-a59f-4340c6809805" />
<img width="1813" height="1071" alt="imagen" src="https://github.com/user-attachments/assets/b41630bc-a86d-4791-8565-53ed3c9ecc9f" />




# Dev

## Install Dependencies

```sh
python3 -m venv venv

# Linux
source venv/bin/activate

# Windows
venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt
```

## Run Program

```sh
uvicorn backend.api.main:app --reload
```

## PostgreSQL

El entorno se carga automáticamente desde `.env`. Usa `.env.example` como referencia y configura al menos `DATABASE_URL` antes de añadir persistencia. El valor esperado es una URL SQLAlchemy, por ejemplo:

```sh
export DATABASE_URL="postgresql+psycopg://usuario:contrasena@localhost:5432/corona"
```

El modelo ORM `backend/models/product.py` representa la tabla `products`. Las migraciones deben gestionarse con Alembic antes de desplegar.

Antes de la primera importacion, crea la tabla con:

```sh
alembic upgrade head
```

Para sincronizar todas las paginas disponibles de una busqueda y guardar sus productos:

```sh
curl -X POST "http://localhost:8000/api/catalog/import?q=piso&max_pages=100"
```

El proceso se detiene al encontrar una pagina vacia o repetida. `max_pages` evita recorridos indefinidos y puede ajustarse hasta 500.

La API se organiza en `api/routes`, los contratos HTTP en `schemas`, el acceso a PostgreSQL en `models` y `db`, y la logica de negocio e integraciones en `services`.

Las variables disponibles son `APP_ENV`, `APP_HOST`, `APP_PORT`, `LOG_LEVEL`, `DATABASE_URL`, `CORS_ORIGINS`, `CORONA_BASE_URL`, `HTTP_TIMEOUT_SECONDS` y `SCRAPER_MAX_RETRIES`.

## Agente de Renovación

Configura `LLM_PROVIDER` (`openai`, `anthropic` o `google`), `LLM_MODEL` y la clave del proveedor correspondiente. El agente consulta primero la tabla local `products`; al solicitar una ficha técnica sin datos almacenados, consulta Corona y persiste las especificaciones obtenidas.

```sh
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Busco un piso para mi baño con presupuesto limitado"}'
```

Puedes continuar una conversación enviando el `session_id` retornado. Para analizar una imagen, incluye `image_url` en el mismo cuerpo.
