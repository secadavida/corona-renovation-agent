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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
