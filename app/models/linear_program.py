import numpy as np
import matplotlib
import os
from fastapi.encoders import jsonable_encoder

matplotlib.use('Agg')  # Backend no interactivo para servidores
import matplotlib.pyplot as plt
from app.algorithms.linear_programming_v2 import SimplexSolverV2

def solve_linear_problem(data):
    """
    Resuelve problemas de PL usando la implementación robusta SimplexSolverV2.
    """
    method = data.get("method", "simplex")
    c = np.array(data["objective_coeffs"], dtype=float)
    num_vars = len(c)
    
    A_ub, b_ub = [], []
    A_eq, b_eq = [], []
    
    for constraint in data["constraints"]:
        coeffs = list(constraint["coeffs"])
        # Normalización de dimensiones
        while len(coeffs) < num_vars: coeffs.append(0)
        coeffs = coeffs[:num_vars]
        
        sign = constraint.get("sign", "<=")
        rhs = float(constraint.get("rhs", 0))
        
        if sign == "<=":
            A_ub.append(coeffs)
            b_ub.append(rhs)
        elif sign == "=":
            A_eq.append(coeffs)
            b_eq.append(rhs)
        elif sign == ">=":
            # Convertir >= a <= multiplicando por -1
            A_ub.append([-x for x in coeffs])
            b_ub.append(-rhs)
    
    # Asegurar que las matrices no sean None para el constructor
    A_ub = np.array(A_ub) if A_ub else None
    b_ub = np.array(b_ub) if b_ub else None
    A_eq = np.array(A_eq) if A_eq else None
    b_eq = np.array(b_eq) if b_eq else None
    
    maximization = data["objective"] == "max"
    solver = SimplexSolverV2(c, A_ub, b_ub, A_eq, b_eq, maximization=maximization)
    
    # Mapeo de métodos internos
    method_map = {
        "simplex": "simplex",
        "two_phase": "two_phase",
        "m_big": "big_m"
    }
    
    result = solver.solve(method_map.get(method, "simplex"))
    return jsonable_encoder(result)

def solve_graphical(data):
    """
    Resuelve y grafica problemas de PL de 2 variables.
    """
    if len(data["variables"]) != 2:
        return {"status": "error", "message": "El método gráfico requiere exactamente 2 variables."}
    
    try:
        coeffs = np.array(data["objective_coeffs"], dtype=float)
        constraints = data["constraints"]
        is_max = data["objective"] == "max"
        
        # 1. Definir límites del gráfico dinámicamente
        rhs_values = [c["rhs"] for c in constraints if c["rhs"] > 0]
        limit = max(rhs_values) * 1.2 if rhs_values else 10
        x_vals = np.linspace(0, limit, 400)
        
        plt.figure(figsize=(10, 8))
        
        # 2. Encontrar puntos de intersección (vértices candidatos)
        # Empezamos con el origen y los cruces con los ejes
        points = [np.array([0.0, 0.0])]
        
        for i, cons in enumerate(constraints):
            a1, a2 = cons["coeffs"]
            b = cons["rhs"]
            
            # Graficar líneas de restricción
            if a2 != 0:
                y_plot = (b - a1 * x_vals) / a2
                plt.plot(x_vals, y_plot, label=f'R{i+1}')
                points.append(np.array([0.0, b/a2])) # Cruce eje Y
            else:
                plt.axvline(x=b/a1, label=f'R{i+1}')
            
            if a1 != 0: points.append(np.array([b/a1, 0.0])) # Cruce eje X

        # Intersecciones entre todas las restricciones
        for i in range(len(constraints)):
            for j in range(i + 1, len(constraints)):
                A = np.array([constraints[i]["coeffs"], constraints[j]["coeffs"]])
                B = np.array([constraints[i]["rhs"], constraints[j]["rhs"]])
                if np.linalg.matrix_rank(A) == 2:
                    points.append(np.linalg.solve(A, B))

        # 3. Filtrar puntos factibles
        feasible_points = []
        for p in points:
            if p[0] >= -1e-9 and p[1] >= -1e-9: # Primer cuadrante
                is_feasible = True
                for cons in constraints:
                    val = cons["coeffs"][0] * p[0] + cons["coeffs"][1] * p[1]
                    if cons["sign"] == "<=" and val > cons["rhs"] + 1e-7: is_feasible = False
                    if cons["sign"] == ">=" and val < cons["rhs"] - 1e-7: is_feasible = False
                if is_feasible: feasible_points.append(p)

        if not feasible_points:
            plt.close()
            return {"status": "Infeasible", "message": "No existe región factible."}

        # 4. Encontrar el punto óptimo
        optimal_val = float('-inf') if is_max else float('inf')
        optimal_p = feasible_points[0]
        
        for p in feasible_points:
            z = coeffs[0] * p[0] + coeffs[1] * p[1]
            if is_max:
                if z > optimal_val: optimal_val, optimal_p = z, p
            else:
                if z < optimal_val: optimal_val, optimal_p = z, p

        # 5. Estética del gráfico
        plt.scatter(optimal_p[0], optimal_p[1], color='red', s=100, zorder=5, label='Óptimo')
        plt.title(f'Método Gráfico ({data["objective"].upper()})')
        plt.xlabel('x1'); plt.ylabel('x2')
        plt.xlim(0, limit); plt.ylim(0, limit)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()

        # Crear carpeta estática si no existe
        if not os.path.exists('static'): os.makedirs('static')
        img_path = 'static/graph_with_table.png'
        plt.savefig(img_path, bbox_inches='tight')
        plt.close()

        return {
            "status": "Optimal",
            "objective_value": float(optimal_val),
            "variable_values": {"x1": round(float(optimal_p[0]), 4), "x2": round(float(optimal_p[1]), 4)},
            "graph": "/static/graph_with_table.png"
        }
    except Exception as e:
        plt.close()
        return {"status": "error", "message": str(e)}

def solve_dual_linear_problem(data):
    """
    Construye y resuelve el problema Dual.
    """
    primal_is_max = data["objective"] == "max"
    c_primal = np.array(data["objective_coeffs"], dtype=float)
    
    A_ub, b_ub = [], []
    for cons in data["constraints"]:
        if cons["sign"] == "<=":
            A_ub.append(cons["coeffs"])
            b_ub.append(cons["rhs"])
    
    A = np.array(A_ub)
    b = np.array(b_ub)
    
    # El Dual de un Max (Ax <= b) es un Min (A^T y >= c)
    c_dual = b
    b_dual = c_primal
    A_dual = A.T 
    
    # Resolvemos el dual usando Simplex (convertido a <= para el solver)
    solver = SimplexSolverV2(c_dual, A_ub=-A_dual, b_ub=-b_dual, maximization=not primal_is_max)
    result = solver.solve('simplex')
    
    return jsonable_encoder(result)
