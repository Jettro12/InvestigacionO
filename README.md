# Calculadora Operativa - Investigación Operativa

## 🎯 Descripción

Sistema completo de Investigación Operativa con algoritmos implementados desde cero. Resuelve problemas de:

- Programación Lineal (Simplex, Gran M, Dos Fases, Dual)
- Problemas de Transporte (4 métodos)
- Algoritmos de Redes (Dijkstra, Kruskal, Ford-Fulkerson, Flujo Costo Mínimo)
- Análisis de Sensibilidad con IA (Groq)

**✅ Todos los algoritmos desarrollados SIN librerías de optimización (pulp, scipy, networkx)**

## 📋 Requisitos

- Python 3.13+
- Node.js 18+

## 🚀 Instalación y Ejecución

### Backend (FastAPI)

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell

# 2. Instalar dependencias
cd app
pip install -r requirements.txt

# 3. Ejecutar servidor
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend disponible en: **http://127.0.0.1:8000**

### Frontend (Next.js)

```bash
cd frontend/frontend
npm install
npm run dev
```

Frontend disponible en: **http://localhost:3000**

## 📊 Capacidades Implementadas

### ✅ Programación Lineal

| Método        | Estado          | Detalles                                       |
| ------------- | --------------- | ---------------------------------------------- |
| **Simplex**   | ✅ Implementado | Método tableau, pivoteo automático             |
| **Gran M**    | ✅ Implementado | Penalización de variables artificiales         |
| **Dos Fases** | ✅ Implementado | Fase I de viabilidad + Fase II de optimización |
| **Dual**      | ✅ Implementado | Transformación automática del dual             |

### ✅ Problemas de Transporte

| Método               | Estado          | Características                 |
| -------------------- | --------------- | ------------------------------- |
| **Esquina Noroeste** | ✅ Implementado | Asignación sistemática          |
| **Costo Mínimo**     | ✅ Implementado | Celdas de menor costo           |
| **Vogel**            | ✅ Implementado | Penalizaciones por fila/columna |
| **MODI**             | ✅ Implementado | Prueba de optimalidad           |

### ✅ Algoritmos de Redes

| Algoritmo              | Estado          | Detalles                     |
| ---------------------- | --------------- | ---------------------------- |
| **Dijkstra**           | ✅ Implementado | Heap-based, O((V+E) log V)   |
| **Kruskal**            | ✅ Implementado | Union-Find, MST              |
| **Ford-Fulkerson**     | ✅ Implementado | BFS para caminos aumentantes |
| **Flujo Costo Mínimo** | ✅ Implementado | Caminos sucesivos            |

### ✅ IA para Sensibilidad

- **Groq API Integration** para análisis inteligente
- Interpretación automática de cambios
- Recomendaciones empresariales basadas en IA

## 📁 Estructura del Proyecto

```
app/
├── algorithms/
│   ├── linear_programming.py    (Simplex, Gran M, Dos Fases, Dual)
│   ├── transportation.py         (4 métodos de transporte)
│   └── network_optimization.py   (Dijkstra, Kruskal, Ford-Fulkerson, etc)
├── models/
│   ├── linear_program.py        (Interfaz de programación lineal)
│   └── optimization_model.py
├── services/
│   ├── optimization_service.py
│   └── optimization_service_network.py
├── routes/
│   ├── linear_solver.py         (API de PL)
│   ├── optimization_routes.py   (API de transporte)
│   └── optimization_routes_network.py (API de redes)
├── utils/
│   ├── sensitivity_analysis.py  (IA con Groq)
│   └── validations.py
└── main.py                      (Aplicación principal)

frontend/
└── frontend/                    (Next.js + React)
    ├── src/pages/              (Linear, Transport, Network, Solve-All)
    └── src/components/         (Navbar, componentes UI)
```

## 🔌 Endpoints Principales

### Programación Lineal

```
POST /solve_linear
Body: {
  "variables": ["x1", "x2"],
  "objective_coeffs": [3, 2],
  "objective": "max",
  "constraints": [
    {"coeffs": [1, 1], "sign": "<=", "rhs": 4}
  ],
  "method": "simplex|two_phase|m_big|dual|graphical"
}
```

### Transporte

```
POST /solve_transport
Body: {
  "supply": [10, 20],
  "demand": [15, 15],
  "costs": [[1, 2], [3, 1]],
  "method": "northwest|min_cost|vogel"
}
```

### Redes

```
POST /solve_network
Body: {
  "graph": [[1, 2, 4, 10], [1, 3, 2, 10]],
  "source": 1,
  "sink": 4,
  "method": "dijkstra|kruskal|ford_fulkerson|min_cost_flow"
}
```

## 🔐 Variables de Entorno

Crear `.env` en la carpeta `app/`:

```
GROQ_API_KEY=tu_clave_groq_aqui
```

## 📝 Notas Importantes

- Si cambias puertos, actualiza las llamadas en el frontend
- El análisis de sensibilidad requiere configurar GROQ_API_KEY
- Todos los algoritmos funcionan sin dependencias de optimización externa

## ✨ Características Especiales

- Historial de iteraciones del Simplex
- Visualización de grafos (Dijkstra, MST, etc.)
- Análisis automático de sensibilidad con IA
- Validación de entrada robusta
- Interfaz web moderna con Tailwind CSS

## 📚 Documentación Adicional

Ver [VERIFICACION_REQUISITOS.md](VERIFICACION_REQUISITOS.md) para detalles completos de implementación.
