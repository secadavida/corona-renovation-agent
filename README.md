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
