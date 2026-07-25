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

Configura `DATABASE_URL` antes de añadir persistencia. El valor esperado es una URL SQLAlchemy, por ejemplo:

```sh
export DATABASE_URL="postgresql+psycopg://usuario:contrasena@localhost:5432/corona"
```

El modelo ORM `backend/models/product.py` representa la tabla `products`. Las migraciones deben gestionarse con Alembic antes de desplegar.

La API se organiza en `api/routes`, los contratos HTTP en `schemas`, el acceso a PostgreSQL en `models` y `db`, y la logica de negocio e integraciones en `services`.
