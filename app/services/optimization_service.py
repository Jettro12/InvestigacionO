from app.algorithms.linear_programming import solve_linear_program
import numpy as np
from groq import Groq
import os
from dotenv import load_dotenv

# Cargar .env desde la carpeta app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from app.algorithms.transportation import (
    balance_transportation_problem,
    northwest_corner_method,
    minimum_cost_method,
    vogel_approximation_method,
    modi_method
)
from app.algorithms.network_optimization import dijkstra_algorithm

# Configurar Groq AI con API key del .env
API_KEY = os.getenv("GROQ_API_KEY")
if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    client = None

def generate_sensitivity_analysis(solution, total_cost):
    """
    Genera un análisis de sensibilidad utilizando Groq AI con texto plano.
    """
    import json
    
    if not API_KEY:
        return "Error: GROQ_API_KEY no está configurada en .env"
    
    # Convertir solución a string JSON para evitar errores
    solution_str = json.dumps(solution.tolist() if hasattr(solution, 'tolist') else solution)
    
    prompt = f"""Analiza en detalle este problema de transporte:
    - Solución óptima: {solution_str}
    - Costo total: {total_cost}

Proporciona un análisis claro en texto plano. Usa estas marcas para resaltar:
- [CRÍTICO] para información de alta importancia
- [RECOMENDACIÓN] para sugerencias prácticas
- [RIESGO] para puntos débiles

Incluye:
1. Resumen de cómo se distribuyeron los envíos
2. Mejoras posibles
3. Impacto de cambios
4. Recomendaciones concretas
5. Ahorro potencial si se implementan mejoras
6. Riesgos a considerar

Presenta en texto limpio y comprensible para usuarios de negocios."""

    try:
        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        response_text = message.choices[0].message.content
        return response_text
    except Exception as e:
        print(f"Error en análisis de sensibilidad: {str(e)}")
        return f"Error al generar análisis: {str(e)}"

def calculate_total_cost(solution, costs):
    """
    Calcula el costo total de la solución basada en la matriz de costos.
    """
    total_cost = 0
    for i in range(len(solution)):
        for j in range(len(solution[i])):
            total_cost += solution[i][j] * costs[i][j] 
    return total_cost

def solve_optimization(problem_type, data):
    print(f"🚀 Recibida solicitud para {problem_type} con datos:", data)

    if problem_type == "linear":
        return solve_linear_program(data["c"], data["A_ub"], data["b_ub"])
    elif problem_type == "transport":
        try:
            # 🔍 Verificar si los datos existen
            if "supply" not in data or "demand" not in data or "costs" not in data:
                return {"status": "error", "message": "Faltan datos en la solicitud"}

            supply = data["supply"]
            demand = data["demand"]
            costs = np.array(data["costs"], dtype=float)

            # Guardamos el tamaño original
            original_supply_len = len(supply)
            original_demand_len = len(demand)

            # 🔍 Verificar si se necesita balancear el problema
            supply, demand, costs = balance_transportation_problem(supply, demand, costs)

            balance_message = None
            if len(supply) > original_supply_len:
                balance_message = "Se agregó un suministro ficticio para balancear el problema."
            elif len(demand) > original_demand_len:
                balance_message = "Se agregó una demanda ficticia para balancear el problema."

            # Seleccionar método inicial
            method = data.get("method", "northwest")

            if method == "northwest":
                initial_solution = northwest_corner_method(supply, demand)
            elif method == "minimum_cost":
                initial_solution = minimum_cost_method(supply, demand, costs)
            elif method == "vogel":
                initial_solution = vogel_approximation_method(supply, demand, costs)
            else:
                return {"status": "error", "message": "Método inválido"}
            
             # Optimización con MODI
            initial_cost = calculate_total_cost(initial_solution, costs)
            optimal_solution, total_cost = modi_method(initial_solution, costs)
            print("🟢 Matriz óptima (MODI) antes de calcular el costo:")
            print(optimal_solution)
            # 📌 Generar Análisis de Sensibilidad con Google Gemini AI
            sensitivity_analysis = generate_sensitivity_analysis(optimal_solution, total_cost)

            response = {
                "status": "success",
                "initial_solution": initial_solution.tolist(),
                "optimal_solution": optimal_solution,
                "initial_cost": initial_cost,
                "total_cost": total_cost,
                "sensitivity_analysis": sensitivity_analysis
            }

            print("📩 Respuesta enviada al frontend:", response)  # ✅ Verificar respuesta

            return response

        except Exception as e:
            print(f"❌ Error en solve_optimization: {str(e)}")
            return {"status": "error", "message": str(e)}
    elif problem_type == "network":
        return dijkstra_algorithm(data["graph"], data["start_node"])
    return {"status": "error", "message": "Unknown problem type"}
