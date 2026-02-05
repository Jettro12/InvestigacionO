import numpy as np
import matplotlib
import os
from fastapi.encoders import jsonable_encoder

matplotlib.use('Agg')  # Backend no interactivo
import matplotlib.pyplot as plt

# IMPORTANTE: Importamos la nueva función maestra y las específicas del archivo de algorithms
from app.algorithms.linear_programming import solve_linear_program, solve_graphical as solve_graph_algo, solve_dual_linear_problem as solve_dual_algo

def solve_linear_problem(data):
    """
    Une el request del frontend con la lógica de los algoritmos.
    Ahora detecta si debe generar un gráfico.
    """
    method = data.get("method", "simplex")
    
    # --- 1. DETECCIÓN DE MÉTODO GRÁFICO ---
    # Si el método es graphical, llamamos a solve_graphical directamente
    if method == "graphical":
        return solve_graphical(data)

    # --- 2. LÓGICA PARA MÉTODOS ANALÍTICOS (Simplex, Gran M, etc.) ---
    objective_coeffs = data.get("objective_coeffs")
    constraints = data.get("constraints")
    obj_type = data.get("objective", "max")

    method_map = {
        "m_big": "big_m",
        "simplex": "simplex",
        "two_phase": "two_phase"
    }
    
    selected_method = method_map.get(method, method)

    # Llamamos a la función maestra
    result = solve_linear_program(
        objective=objective_coeffs,
        constraints=constraints,
        method=selected_method,
        obj_type=obj_type
    )
    
    return jsonable_encoder(result)

def solve_graphical(data):
    """
    Llama a la implementación gráfica del archivo de algoritmos.
    """
    objective_coeffs = data.get("objective_coeffs")
    constraints = data.get("constraints")
    obj_type = data.get("objective", "max")

    # Usamos la función que ya genera el gráfico y devuelve el base64
    result = solve_graph_algo(objective_coeffs, constraints, obj_type)
    return jsonable_encoder(result)

def solve_dual_linear_problem(data):
    """
    Llama a la resolución dual del archivo de algoritmos.
    """
    objective_coeffs = data.get("objective_coeffs")
    constraints = data.get("constraints")
    
    result = solve_dual_algo(objective_coeffs, constraints)
    return jsonable_encoder(result)