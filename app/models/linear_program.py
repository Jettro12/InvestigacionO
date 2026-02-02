import re
import math
import matplotlib
from fastapi.encoders import jsonable_encoder

matplotlib.use('Agg')  # Usar un backend no interactivo
import matplotlib.pyplot as plt

# Import Custom Simplex Solver
# Note: Ensure algorithms/custom_simplex.py exists and is in python path
from algorithms.custom_simplex import SimplexSolver, solve_dual_problem

def sanitize_variable_name(name):
    """Corrige los nombres de variables (Simple utility)"""
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def _parse_data_to_matrices(data):
    """Parses the input dictionary to SimplexSolver compatible lists."""
    c = data.get("objective_coeffs", [])
    
    # If objective coeffs are missing, maybe they are in 'c' key in schemas but data here seems to rely on objective_coeffs
    
    A = []
    b = []
    signs = []
    
    # Check if constraints exist
    constraints = data.get("constraints", [])
    if constraints:
        for constraint in constraints:
            coeffs = constraint.get("coeffs", [])
            A.append(coeffs)
            b.append(float(constraint.get("rhs", 0)))
            signs.append(constraint.get("sign", "<="))
            
    return c, A, b, signs

def solve_linear_problem(data):
    """Solves LP using Custom Simplex (Default)"""
    method = data.get("method", "simplex")
    c, A, b, signs = _parse_data_to_matrices(data)
    
    solver = SimplexSolver(
        c, A, b, signs, 
        objective=data.get("objective", "max"),
        method=method,
        variable_names=data.get("variables", [])
    )
    
    solution = solver.solve()
    return jsonable_encoder(solution)

def solve_m_big_linear_problem(objective_coeffs, variable_names, constraints, objective_type, M=10000):
    """Wrapper for Big M Method"""
    # Reconstruct data structure
    data = {
        "objective_coeffs": objective_coeffs,
        "variables": variable_names,
        "constraints": constraints,
        "objective": objective_type,
        "method": "m_big"
    }
    return solve_linear_problem(data)

def solve_two_phase_linear_problem(objective_coeffs, variable_names, constraints, objective_type):
    """Wrapper for Two Phase Method"""
    data = {
        "objective_coeffs": objective_coeffs,
        "variables": variable_names,
        "constraints": constraints,
        "objective": objective_type,
        "method": "two_phase"
    }
    return solve_linear_problem(data)

def solve_dual_linear_problem(data):
    """Solves Dual Problem"""
    # We call our custom dual solver which returns same structure
    solution = solve_dual_problem(data)
    return jsonable_encoder(solution)

def solve_graphical(data):
    if len(data.get("variables", [])) != 2:
        return {"error": "El método gráfico solo se puede usar con 2 variables."}
    
    coeffs = data.get("objective_coeffs", [0, 0])
    constraints = data.get("constraints", [])
    
    # 1. Generate Lines
    # Use manual linspace to avoid numpy
    points = 200
    x_vals = [i * (10.0 / (points - 1)) for i in range(points)] 
    
    y_lines = []
    for constraint in constraints:
        c_coeffs = constraint["coeffs"]
        rhs = constraint["rhs"]
        y_points = []
        for x in x_vals:
            # a*x + b*y = rhs => y = (rhs - a*x)/b
            if abs(c_coeffs[1]) > 1e-9:
                y = (rhs - c_coeffs[0] * x) / c_coeffs[1]
                y_points.append(y)
            else:
                y_points.append(None) # Vertical line
        y_lines.append(y_points)
    
    plt.figure(figsize=(10, 6))
    
    for i, y_points in enumerate(y_lines):
        clean_x = []
        clean_y = []
        for k, y in enumerate(y_points):
            if y is not None:
                clean_x.append(x_vals[k])
                clean_y.append(y)
        
        plt.plot(clean_x, clean_y, label=f'Restricción {i + 1}')
    
    # 3. Find Intersections (Manual)
    intersection_points = []
    
    # Intersects between constraints
    n_const = len(constraints)
    for i in range(n_const):
        for j in range(i + 1, n_const):
            a1, b1 = constraints[i]["coeffs"]
            c1 = constraints[i]["rhs"]
            a2, b2 = constraints[j]["coeffs"]
            c2 = constraints[j]["rhs"]
            
            det = a1 * b2 - a2 * b1
            if abs(det) > 1e-9:
                x = (c1 * b2 - c2 * b1) / det
                y = (a1 * c2 - a2 * c1) / det
                if x >= 0 and y >= 0:
                    intersection_points.append([x, y])
                    
    # Intersects with axes (x=0, y=0)
    for const in constraints:
        a, b_coef = const["coeffs"]
        rhs = const["rhs"]
        if abs(b_coef) > 1e-9:
             y_intercept = rhs / b_coef
             if y_intercept >= 0:
                 intersection_points.append([0, y_intercept])
                 
        if abs(a) > 1e-9:
             x_intercept = rhs / a
             if x_intercept >= 0:
                 intersection_points.append([x_intercept, 0])
                 
    intersection_points.append([0, 0])

    # 4. Check Feasibility
    feasible_points = []
    for p in intersection_points:
        x, y = p
        is_feasible = True
        for const in constraints:
             val = const["coeffs"][0]*x + const["coeffs"][1]*y
             sign = const["sign"]
             rhs = const["rhs"]
             
             if sign == "<=":
                 if val > rhs + 1e-5: is_feasible = False
             elif sign == ">=":
                 if val < rhs - 1e-5: is_feasible = False
             elif sign == "=":
                 if abs(val - rhs) > 1e-5: is_feasible = False
        
        if is_feasible:
            feasible_points.append(p)
            
    # 5. Optimal
    optimal_value = -float('inf') if data.get("objective") == "max" else float('inf')
    optimal_point = [0, 0]
    
    status = "Infeasible"
    variable_values = {"x1": 0, "x2": 0}

    if feasible_points:
        status = "Optimal"
        for p in feasible_points:
            val = coeffs[0]*p[0] + coeffs[1]*p[1]
            
            if data.get("objective") == "max":
                if val > optimal_value:
                    optimal_value = val
                    optimal_point = p
            else:
                 if val < optimal_value:
                    optimal_value = val
                    optimal_point = p
        variable_values = {"x1": optimal_point[0], "x2": optimal_point[1]}

    # Plot Optimal Point
    plt.plot(optimal_point[0], optimal_point[1], 'ro', label='Óptimo')

    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.grid()
    plt.legend()
    plt.savefig('static/graph_with_table.png', bbox_inches='tight')
    plt.close()

    return {
        "status": status,
        "objective_value": optimal_value if status == "Optimal" else 0,
        "variable_values": variable_values,
        "graph": "/graph_with_table.png"
    }
