ejecucion de servidor:
uvicorn src.app:app --reload --host 127.0.0.1 --port 8080

Descripción breve del Mini-ERP “CAFETAL SAC”.

Pila: FastAPI + SQL Server + React/Vite.

Prerequisitos: Python 3.11/3.12, Node 18+/20+, SQL Server, ODBC Driver 18 x64.

Setup Backend, Setup Frontend, Variables de entorno (copiar .env.example a .env).

Comandos clave (ver abajo).

--PASOS
# 1) Crear venv e instalar deps

python -m venv .venv
.\.venv\Scripts\activate         # Windows
pip install -r requirements.txt  # cargar librerias

o sino ejecutar esto:
pip install fastapi uvicorn sqlalchemy pyodbc pydantic-settings python-dateutil pytz

# 2) Variables de entorno
copy .env.example .env
# Edita .env con tu cadena ODBC (usa el formato odbc_connect que te funcionó)

# 3) Correr
uvicorn src.app:app --reload --host 127.0.0.1 --port 8080

# 4) Probar
# http://127.0.0.1:8080/health
# http://127.0.0.1:8080/docs