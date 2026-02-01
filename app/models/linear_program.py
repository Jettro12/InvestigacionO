import pulp
import re
import numpy as np
import matplotlib
from fastapi.encoders import jsonable_encoder

matplotlib.use('Agg')  # Usar un backend no interactivo
import matplotlib.pyplot as plt
from pulp import LpProblem, LpMaximize, LpMinimize, LpVariable, lpSum, value

def sanitize_variable_name(name):
    """Corrige los nombres de variables para que sean válidos en PuLP."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def solve_linear_problem(data):
    method = data.get("method", "simplex")  # Método por defecto: Simplex

    # Crear problema de programación lineal
    problem = pulp.LpProblem("Linear_Problem", 
                             pulp.LpMaximize if data["objective"] == "max" else pulp.LpMinimize)
    # Definir variables de decisión
    variables = {var: pulp.LpVariable(sanitize_variable_name(var), lowBound=0) 
                 for var in data["variables"]}

    # Diccionario para almacenar las variables artificiales
    artificial_variables = {}

    if method in ["two_phase", "m_big"]:
        M = 10000  # Valor grande para Gran M, puedes ajustarlo según sea necesario
        for i, constraint in enumerate(data["constraints"]):
            if constraint["sign"] in [">=", "="]:
                artificial_var = pulp.LpVariable(f"artificial_{i}", lowBound=0)
                artificial_variables[f"artificial_{i}"] = artificial_var
                lhs = pulp.lpSum(constraint["coeffs"][j] * variables[data["variables"][j]]
                                 for j in range(len(constraint["coeffs"])))
                if method == "m_big":  # Gran M
                    if constraint["sign"] == ">=":
                        problem += lhs - artificial_var >= constraint["rhs"] - M * artificial_var
                    elif constraint["sign"] == "=":
                        problem += lhs == constraint["rhs"]
                else:  # Método de Dos Fases
                    if constraint["sign"] == ">=":
                        problem += lhs - artificial_var >= constraint["rhs"]
                    elif constraint["sign"] == "=":
                        problem += lhs == constraint["rhs"]

    # Construir la función objetivo
    if data["objective"] == "max" and method == "m_big":
        # Penalizamos las variables artificiales para evitar que tengan valor en la solución
        penalty = M * pulp.lpSum(artificial_variables[a] for a in artificial_variables)
        objective_expr = (pulp.lpSum(data["objective_coeffs"][i] * variables[var]
                         for i, var in enumerate(data["variables"])) - penalty)
    else:
        objective_expr = pulp.lpSum(data["objective_coeffs"][i] * variables[var]
                                    for i, var in enumerate(data["variables"]))
    
    problem += objective_expr, "Objective"

    # Agregar restricciones (sin variables artificiales)
    for i, constraint in enumerate(data["constraints"]):
        lhs = pulp.lpSum(constraint["coeffs"][j] * variables[data["variables"][j]]
                         for j in range(len(constraint["coeffs"])))
        if constraint["sign"] == "<=":
            problem += lhs <= constraint["rhs"]

    # Selección del solver
    solver = pulp.PULP_CBC_CMD(msg=True, logPath="solver_log.txt")
    problem.solve(solver)
    
    # Verificar el estado del problema
    status = pulp.LpStatus[problem.status]
    if status == "Infeasible":
        return jsonable_encoder({"error": "El problema es infactible"})
    elif status == "Unbounded":
        return jsonable_encoder({"error": "El problema es no acotado"})

    # Leer el log de iteraciones y extraer el número de iteraciones
    with open("solver_log.txt", "r") as file:
        log_lines = file.readlines()
    iteration_line = [line for line in log_lines if "iterations" in line]
    iterations_count = 0
    if iteration_line:
        match = re.search(r'(\d+)\s+iterations', iteration_line[0])
        if match:
            iterations_count = int(match.group(1))
    
    artificial_variables_cleaned = {
        f"a{i+1}": (value(var) if var is not None else 0)
        for i, var in enumerate(artificial_variables.values())
    }

    solution = {
        "status": status,
        "objective_value": pulp.value(problem.objective),
        "variable_values": {str(var): pulp.value(variables[var]) for var in data["variables"]},
        "artificial_variables": artificial_variables_cleaned if method in ["m_big", "two_phase"] else None,
        "iterations": iterations_count
    }
    
    return jsonable_encoder(solution)

def solve_m_big_linear_problem(objective_coeffs, variable_names, constraints, objective_type, M=10000):
    model = LpProblem("M_Big_Problem", LpMaximize if objective_type == "max" else LpMinimize)
    variables = {name: LpVariable(name, lowBound=0) for name in variable_names}
    artificial_variables = []
    
    for i, constraint in enumerate(constraints):
        if constraint['sign'] == '>=':
            artificial_var = LpVariable(f"a{i+1}", lowBound=0)
            artificial_variables.append(artificial_var)
            model += lpSum([constraint['coeffs'][j] * variables[variable_names[j]] 
                            for j in range(len(variable_names))]) - artificial_var >= constraint['rhs'] - M * artificial_var
        elif constraint['sign'] == '=':
            artificial_var = LpVariable(f"a{i+1}", lowBound=0)
            artificial_variables.append(artificial_var)
            model += lpSum([constraint['coeffs'][j] * variables[variable_names[j]] 
                            for j in range(len(variable_names))]) - artificial_var >= constraint['rhs']
            model += lpSum([constraint['coeffs'][j] * variables[variable_names[j]] 
                            for j in range(len(variable_names))]) + artificial_var <= constraint['rhs']
        else:
            model += lpSum([constraint['coeffs'][j] * variables[variable_names[j]] 
                            for j in range(len(variable_names))]) >= constraint['rhs']
    
    model += lpSum([objective_coeffs[i] * variables[variable_names[i]] 
                    for i in range(len(variable_names))]), "Objective"
    model.solve()
    
    artificial_variables_cleaned = {
        f"a{i+1}": (value(var) if var is not None else 0)
        for i, var in enumerate(artificial_variables)
    }
    
    if value(model.objective) > 0:
        solution = {
            'status': 'Optimal' if value(model.objective) > 0 else 'Infeasible',
            'objective_value': value(model.objective),
            'variable_values': {name: value(variables[name]) for name in variable_names},
            'artificial_variables': artificial_variables_cleaned,
        }
    else:
        solution = {
            'status': 'Infeasible',
            'objective_value': 0,
            'variable_values': {name: 0 for name in variable_names},
            'artificial_variables': {f"a{i+1}": 0 for i in range(len(artificial_variables))}
        }
    
    return solution
def solve_two_phase_linear_problem(objective_coeffs, variable_names, constraints, objective_type):
    # **Fase 1: Resolver para eliminar variables artificiales**
    phase1 = LpProblem("Phase1", LpMinimize)

    # Crear variables originales
    variables = {name: LpVariable(name, lowBound=0) for name in variable_names}

    # Diccionario para almacenar variables artificiales
    artificial_vars = {}

    # Agregar restricciones y variables artificiales
    for i, constraint in enumerate(constraints):
        lhs = lpSum(constraint["coeffs"][j] * variables[variable_names[j]] for j in range(len(constraint["coeffs"])))
        if constraint["sign"] in [">=", "="]:  
            art = LpVariable(f"artificial_{i+1}", lowBound=0)  
            artificial_vars[f"artificial_{i+1}"] = art  
            phase1 += lhs - art == constraint["rhs"]
        elif constraint["sign"] == "<=":  
            phase1 += lhs <= constraint["rhs"]

    # **Función objetivo Fase 1:** Minimizar la suma de las artificiales
    phase1 += lpSum(artificial_vars[a] for a in artificial_vars), "Phase1_Objective"

    # Resolver Fase 1
    phase1.solve()

    # Revisar si la solución de la fase 1 es factible
    artificial_values = {a: value(artificial_vars[a]) for a in artificial_vars}
    artificial_sum = sum(artificial_values.values())

    if artificial_sum > 1e-5:  # Si las artificiales no son cero, el problema es infactible
        return {
            "status": "Infeasible",
            "message": "No existe solución factible (fase 1).",
            "artificial_variables": artificial_values
        }

    # **Fase 2: Resolver el problema original sin variables artificiales**
    phase2 = LpProblem("Phase2", LpMaximize if objective_type == "max" else LpMinimize)

    # Función objetivo Fase 2
    phase2 += lpSum(objective_coeffs[i] * variables[variable_names[i]] for i in range(len(variable_names))), "Objective"

    # Agregar restricciones sin variables artificiales
    for i, constraint in enumerate(constraints):
        lhs = lpSum(constraint["coeffs"][j] * variables[variable_names[j]] for j in range(len(constraint["coeffs"])))
        if constraint["sign"] == "<=":
            phase2 += lhs <= constraint["rhs"]
        elif constraint["sign"] == ">=":
            phase2 += lhs >= constraint["rhs"]
        elif constraint["sign"] == "=":
            phase2 += lhs == constraint["rhs"]

    # Resolver Fase 2
    phase2.solve()

    # Construir la respuesta final
    solution = {
        "status": pulp.LpStatus[phase2.status],
        "objective_value": value(phase2.objective),
        "variable_values": {name: value(variables[name]) for name in variable_names},
        "artificial_variables": artificial_values  # **Se incluyen las artificiales de Fase 1**
    }

    return solution

def solve_graphical(data):
    if len(data["variables"]) != 2:
        return {"error": "El método gráfico solo se puede usar con 2 variables."}
    
    coeffs = data["objective_coeffs"]
    constraints = data["constraints"]
    x = np.linspace(0, 10, 200)
    y = []
    for constraint in constraints:
        if constraint["coeffs"][1] != 0:
            y_val = (constraint["rhs"] - constraint["coeffs"][0] * x) / constraint["coeffs"][1]
        else:
            y_val = np.full_like(x, np.nan)
        y.append(y_val)
    
    plt.figure(figsize=(10, 6))
    y_min = np.zeros_like(x)
    for i, y_vals in enumerate(y):
        if constraints[i]["sign"] == "<=":
            plt.fill_between(x, y_min, y_vals, where=(y_vals >= y_min), color='lightblue', alpha=0.3, label=f'Restricción {i + 1}')
        elif constraints[i]["sign"] == ">=":
            plt.fill_between(x, y_min, y_vals, where=(y_vals <= y_min), color='lightblue', alpha=0.3, label=f'Restricción {i + 1}')
        else:
            plt.plot(x, y_vals, label=f'Restricción {i + 1}')
    
    y_obj = (coeffs[0] * x) / coeffs[1] if coeffs[1] != 0 else np.full_like(x, np.nan)
    plt.plot(x, y_obj, label='Función Objetivo', color='red', linestyle='--')
    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.title('Método Gráfico')
    plt.axhline(0, color='black', linewidth=0.5, ls='--')
    plt.axvline(0, color='black', linewidth=0.5, ls='--')
    plt.grid()
    plt.legend()
    
    intersection_points = []
    for i in range(len(constraints)):
        for j in range(i + 1, len(constraints)):
            A = np.array([constraints[i]["coeffs"], constraints[j]["coeffs"]])
            b = np.array([constraints[i]["rhs"], constraints[j]["rhs"]])
            if np.linalg.matrix_rank(A) == 2:
                point = np.linalg.solve(A, b)
                if all(point >= 0):
                    intersection_points.append(point)
    
    optimal_value = float('-inf')
    optimal_point = None
    for point in intersection_points:
        val = coeffs[0] * point[0] + coeffs[1] * point[1]
        if val > optimal_value:
            optimal_value = val
            optimal_point = point
    
    if intersection_points:
        table_data = [[f'Punto {i+1}', f'{p[0]:.2f}', f'{p[1]:.2f}'] for i, p in enumerate(intersection_points)]
        table_data.append(["Valor óptimo", f'{optimal_point[0]:.2f}', f'{optimal_point[1]:.2f}'])
        table_data.append(["Objetivo", f'{optimal_value:.2f}', ''])
        table = plt.table(cellText=table_data, colLabels=['Punto', 'x1', 'x2'], loc='lower right', cellLoc='center', colColours=["#f5f5f5"]*3)
        table.scale(1.2, 1.2)
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.auto_set_column_width([0, 1, 2])
    
    plt.subplots_adjust(bottom=0.3)
    plt.savefig('static/graph_with_table.png', bbox_inches='tight')
    plt.close()
    
    return {
        "status": "optimal",
        "objective_value": optimal_value,
        "variable_values": {"x1": optimal_point[0], "x2": optimal_point[1]},
        "graph": "/graph_with_table.png"
    }

def solve_dual_linear_problem(data):
    """
    Resuelve el problema dual derivado del problema primal dado en 'data'.

    Se asume que:
      - Si el objetivo primal es "max", las restricciones son del tipo "Ax <= b" y
        el dual es: min b^T y, sujeto a A^T y >= c, y >= 0.
      - Si el objetivo primal es "min", las restricciones son del tipo "Ax >= b" y
        el dual es: max b^T y, sujeto a A^T y <= c, y >= 0.

    Parámetros en 'data':
      - "objective": "max" o "min"
      - "variables": lista de nombres de variables del problema primal.
      - "objective_coeffs": lista de coeficientes (vector c) de la función objetivo primal.
      - "constraints": lista de restricciones, cada una con:
            - "coeffs": coeficientes de la fila de A.
            - "rhs": valor de b.
    Retorna un diccionario con:
      - "status": estado de la solución.
      - "objective_value": valor óptimo del dual.
      - "dual_variable_values": diccionario con los valores de las variables duales.
    """
    import pulp
    from pulp import LpProblem, LpMinimize, LpMaximize, LpVariable, lpSum, value

    primal_objective = data["objective"]
    primal_vars = data["variables"]
    c = data["objective_coeffs"]
    constraints = data["constraints"]

    m = len(constraints)
    n = len(primal_vars)

    if primal_objective == "max":
        dual_problem = LpProblem("Dual_Problem", LpMinimize)
        dual_vars = [LpVariable(f"y{i+1}", lowBound=0) for i in range(m)]
        dual_problem += lpSum(constraints[i]["rhs"] * dual_vars[i] for i in range(m)), "Dual_Objective"
        for j in range(n):
            dual_problem += lpSum(constraints[i]["coeffs"][j] * dual_vars[i] for i in range(m)) >= c[j], f"Dual_Constraint_{j+1}"
    elif primal_objective == "min":
        dual_problem = LpProblem("Dual_Problem", LpMaximize)
        dual_vars = [LpVariable(f"y{i+1}", lowBound=0) for i in range(m)]
        dual_problem += lpSum(constraints[i]["rhs"] * dual_vars[i] for i in range(m)), "Dual_Objective"
        for j in range(n):
            dual_problem += lpSum(constraints[i]["coeffs"][j] * dual_vars[i] for i in range(m)) <= c[j], f"Dual_Constraint_{j+1}"
    else:
        raise ValueError("El tipo de objetivo debe ser 'max' o 'min'.")

    dual_problem.solve()
    dual_status = pulp.LpStatus[dual_problem.status]
    dual_objective_value = value(dual_problem.objective)
    variable_values = {var.name: value(var) for var in dual_problem.variables()}

    return {
        "status": dual_status,
        "objective_value": dual_objective_value,
        "variable_values": variable_values
    }
