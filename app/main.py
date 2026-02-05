print(">>> CARGANDO app/main.py")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- IMPORTS DE RUTAS ---
# 1. Programación Lineal (EL QUE FUNCIONA)
from routes.linear_solver import router as linear_solver_router

# 2. Redes (Si este archivo no depende de lo borrado, funcionará)
try:
    from routes.optimization_routes_network import router as network_router
except ImportError as e:
    print(f"⚠️ Advertencia: No se pudo cargar Network Router: {e}")
    network_router = None

# 3. Transporte/General (ESTE ES EL QUE ROMPE TU APP PORQUE USA EL ALGORITMO VIEJO)
# Lo comentamos temporalmente para que el servidor arranque.
# from routes import optimization_routes 

print(">>> Creando instancia de FastAPI")
app = FastAPI(title="Optimization API")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta estática para imágenes de gráficos
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- INCLUIR RUTAS ---

# Ruta de Programación Lineal (Simplex, Gran M, Dos Fases, Gráfico)
print(">>> Incluyendo rutas de linear_solver_router")
app.include_router(linear_solver_router, prefix="/api")

# Ruta de Redes (Si cargó correctamente)
if network_router:
    print(">>> Incluyendo rutas de network_router")
    app.include_router(network_router, prefix="/api")

# Ruta General (Comentada hasta que se refactorice Transport)
# app.include_router(optimization_routes.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)