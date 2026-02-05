import numpy as np
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Algoritmos de transporte
from algorithms.transportation import (
    balance_transportation_problem,
    northwest_corner_method,
    minimum_cost_method,
    vogel_approximation_method,
    modi_method
)
# Otros algoritmos
from models.linear_program import solve_linear_problem as solve_linear_program
from algorithms.network_optimization import dijkstra_algorithm

load_dotenv()

# Configurar Groq AI
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY) if API_KEY else None

def generate_sensitivity_analysis(optimal_solution, total_cost, costs, supply, demand, method):
    """
    Genera un análisis de sensibilidad técnico basado en dualidad y costos logísticos.
    """
    if not client:
        return "⚠️ Error: API de Groq no configurada. Verifica la variable GROQ_API_KEY."

    try:
        # CORRECCIÓN DEFINITIVA: Convertir a listas de Python estándar para evitar error 'tolist'
        sol_list = optimal_solution.tolist() if isinstance(optimal_solution, np.ndarray) else optimal_solution
        costs_list = costs.tolist() if isinstance(costs, np.ndarray) else costs
        
        # Serializar a JSON para que la IA reciba una estructura clara
        sol_json = json.dumps(sol_list)
        costs_json = json.dumps(costs_list)
    except Exception as e:
        print(f"⚠️ Error serializando datos para IA: {e}")
        sol_json = str(optimal_solution)
        costs_json = str(costs)

    # Prompt de Ingeniería de Operaciones optimizado
    prompt = f"""Actúa como un experto en Logística y Optimización Matemática (Investigación de Operaciones). 
Analiza los resultados de este Modelo de Transporte resuelto con el método {method} y optimizado mediante MODI.

**DATOS TÉCNICOS DEL MODELO:**
- Matriz de Costos Unitarios (C): {costs_json}
- Capacidades de Oferta (Si): {supply}
- Requerimientos de Demanda (Dj): {demand}
- Costo Total Óptimo (Z): ${total_cost}

**MATRIZ DE ASIGNACIÓN ÓPTIMA (Flujos):**
{sol_json}

**DIRECTRICES PARA EL ANÁLISIS:**
1. **Flujos y Conectividad:** Identifica las rutas Origen-Destino con mayor volumen. Usa términos 'Orígenes' y 'Destinos'.
2. **Restricciones Activas:** Indica qué Orígenes agotaron su oferta por completo.
3. **Interpretación Dual:** Explica el beneficio de aumentar la capacidad en los orígenes más críticos (Precios Sombra).
4. **Costos de Oportunidad:** Analiza las celdas con flujo cero e indica si hay ineficiencias o soluciones alternativas.

**REQUERIMIENTOS DE FORMATO:**
Usa etiquetas:
- [CRÍTICO] para saturación de capacidad o penalizaciones por nodos ficticios.
- [RECOMENDACIÓN] para expansión de infraestructura o renegociación.
- [RIESGO] para rutas sensibles a variaciones de precio.

Sé técnico, directo y evita introducciones genéricas."""

    try:
        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2 
        )
        return message.choices[0].message.content
    except Exception as e:
        return f"Error al generar análisis inteligente: {str(e)}"

def calculate_total_cost(solution, costs):
    """
    Calcula el costo total asegurando compatibilidad con tipos NumPy y Listas.
    """
    sol_array = np.array(solution)
    costs_array = np.array(costs)
    return float(np.sum(sol_array * costs_array))

def solve_optimization(problem_type, data):
    """
    Punto de entrada único para resolver problemas de optimización.
    """
    print(f"🚀 Procesando {problem_type}...")

    if problem_type == "transport":
        try:
            supply = data.get("supply")
            demand = data.get("demand")
            costs_input = np.array(data.get("costs"), dtype=float)
            method = data.get("method", "northwest")

            if supply is None or demand is None or costs_input is None:
                return {"status": "error", "message": "Datos de entrada incompletos."}

            # 1. Balanceo Automático
            s_bal, d_bal, c_bal = balance_transportation_problem(supply, demand, costs_input)

            # 2. Solución Básica Inicial
            if method == "northwest":
                initial_solution = northwest_corner_method(s_bal, d_bal)
            elif method == "minimum_cost":
                initial_solution = minimum_cost_method(s_bal, d_bal, c_bal)
            else:
                initial_solution = vogel_approximation_method(s_bal, d_bal, c_bal)

            initial_cost = calculate_total_cost(initial_solution, c_bal)

            # 3. Optimización con MODI
            optimal_solution, total_cost = modi_method(initial_solution, c_bal)

            # 4. Generar Análisis Técnico
            sensitivity = generate_sensitivity_analysis(
                optimal_solution, 
                total_cost, 
                c_bal, 
                s_bal, 
                d_bal, 
                method
            )

            # 5. Respuesta segura (convertir todo a tipos serializables por JSON)
            return {
                "status": "success",
                "initial_solution": initial_solution.tolist() if isinstance(initial_solution, np.ndarray) else initial_solution,
                "optimal_solution": optimal_solution.tolist() if isinstance(optimal_solution, np.ndarray) else optimal_solution,
                "initial_cost": float(initial_cost),
                "total_cost": float(total_cost),
                "sensitivity_analysis": sensitivity
            }

        except Exception as e:
            print(f"❌ Error en transporte: {str(e)}")
            return {"status": "error", "message": str(e)}

    elif problem_type == "linear":
        try:
            result = solve_linear_program(data["c"], data["A_ub"], data["b_ub"])
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    elif problem_type == "network":
        try:
            result = dijkstra_algorithm(data["graph"], data["start_node"])
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": "Tipo de problema no soportado."}
