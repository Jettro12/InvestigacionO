from algorithms.linear_programming import solve_linear_program
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

from algorithms.transportation import (
    balance_transportation_problem,
    northwest_corner_method,
    minimum_cost_method,
    vogel_approximation_method,
    modi_method
)
from algorithms.network_optimization import dijkstra_algorithm

model = genai.GenerativeModel("models/gemini-1.5-flash")

def generate_sensitivity_analysis(solution, total_cost):
    """
    Genera un análisis de sensibilidad utilizando Google Gemini AI con una estructura detallada.
    """
    prompt = f"""Dado un problema de transporte con la solución óptima:
    {solution} y un costo total de {total_cost}, realiza un análisis de sensibilidad detallado.

    1️⃣ **Resumen de la Solución**: Explica cómo se distribuyeron los envíos.
    2️⃣ **Posibles Mejoras**: Identifica qué ajustes podrían reducir costos o mejorar eficiencia.
    3️⃣ **Impacto en Costos y Tiempos**: Evalúa cómo los cambios pueden afectar la operación.
    4️⃣ **Recomendaciones Finales**: Proporciona consejos concretos para optimizar la distribución.

    Presenta la respuesta de manera clara y estructurada para que sea fácil de entender por un usuario de negocios.
    """

    response = model.generate_content(prompt).text
    return response

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
