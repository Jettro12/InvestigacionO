
# Calculadora Operativa

## Requisitos
- Python 3.13+
- Node.js 18+

## Backend (FastAPI)
1) Crear y activar el entorno virtual:
	- Windows (PowerShell):
	  - `python -m venv .venv`
	  - `.venv\Scripts\Activate.ps1`
2) Instalar dependencias:
	- `pip install -r requirements.txt`
3) Ejecutar el backend:
	- `cd app`
	- `python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload`

El backend queda en http://127.0.0.1:8000

## Frontend (Next.js)
1) Instalar dependencias:
	- `cd frontend/frontend`
	- `npm install`
2) Ejecutar el frontend:
	- `npm run dev`

El frontend queda en http://localhost:3000

## Notas
- Si cambias puertos, actualiza las llamadas en el frontend.

