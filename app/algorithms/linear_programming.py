import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from scipy.optimize import linprog

# Carga de entorno
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GROQ_API_KEY")

# ======================================================
#   BASE SIMPLEX
# ======================================================

class BaseSimplex:
    def __init__(self, c, constraints, objective="max"):
        self.c = np.array(c, dtype=float)
        self.constraints = constraints
        self.objective = objective
        self.is_max = objective == "max"
        self.num_vars = len(c)
        self.tableau = None
        self.basic_vars = []
        self.steps = []
        self.col_headers = []
        self.num_constraints = len(constraints)

    def _initialize_matrix(self):
        self.num_slack = self.num_surplus = self.num_artificial = 0
        self.col_headers = [f"x{i+1}" for i in range(self.num_vars)]

        for r in self.constraints:
            if r["sign"] == "<=":
                self.num_slack += 1
            elif r["sign"] == ">=":
                self.num_surplus += 1
                self.num_artificial += 1
            elif r["sign"] == "=":
                self.num_artificial += 1

        cols = (self.num_vars + self.num_slack + self.num_surplus + self.num_artificial + 1)
        rows = self.num_constraints + 1
        self.tableau = np.zeros((rows, cols))

    def _fill_constraints(self):
        s_ptr = self.num_vars
        e_ptr = s_ptr + self.num_slack
        a_ptr = e_ptr + self.num_surplus
        
        cs = ce = ca = 0
        art_rows = []

        self.col_headers += [f"s{i+1}" for i in range(self.num_slack)]
        self.col_headers += [f"e{i+1}" for i in range(self.num_surplus)]
        self.col_headers += [f"a{i+1}" for i in range(self.num_artificial)]
        self.col_headers.append("RHS")

        for i, r in enumerate(self.constraints):
            self.tableau[i, :self.num_vars] = r["coeffs"]
            self.tableau[i, -1] = r["rhs"]
            if r["sign"] == "<=":
                self.tableau[i, s_ptr + cs] = 1
                self.basic_vars.append(s_ptr + cs)
                cs += 1
            elif r["sign"] == ">=":
                self.tableau[i, e_ptr + ce] = -1
                self.tableau[i, a_ptr + ca] = 1
                self.basic_vars.append(a_ptr + ca)
                art_rows.append(i)
                ce += 1
                ca += 1
            elif r["sign"] == "=":
                self.tableau[i, a_ptr + ca] = 1
                self.basic_vars.append(a_ptr + ca)
                art_rows.append(i)
                ca += 1
        return art_rows

    def _save_step(self, desc, pivot=None):
        self.steps.append({
            "description": desc,
            "tableau": self.tableau.tolist(),
            "headers": self.col_headers,
            "basic_vars": [self.col_headers[i] if i is not None else "None" for i in self.basic_vars],
            "pivot": pivot
        })

    def _pivot(self, r, c):
        self.tableau[r] /= self.tableau[r, c]
        for i in range(self.tableau.shape[0]):
            if i != r:
                self.tableau[i] -= self.tableau[i, c] * self.tableau[r]
        self.basic_vars[r] = c

    def _find_pivot(self):
        z = self.tableau[-1, :-1]
        if np.all(z >= -1e-11):
            return None, None
        
        # Regla de Bland para evitar ciclos
        negative_indices = np.where(z < -1e-11)[0]
        col = int(negative_indices[0])
        
        ratios = []
        for i in range(self.num_constraints):
            val = self.tableau[i, col]
            if val > 1e-11:
                ratios.append((self.tableau[i, -1] / val, i))
        
        if not ratios:
            return col, None
        
        _, row = min(ratios, key=lambda x: (x[0], x[1]))
        return col, row

    def _extract_solution(self):
        solution = {f"x{i+1}": 0.0 for i in range(self.num_vars)}
        for row, col in enumerate(self.basic_vars):
            if col is not None and col < self.num_vars:
                solution[f"x{col+1}"] = float(max(0, self.tableau[row, -1]))

        z = float(self.tableau[-1, -1])
        # Ajuste de signo: Si minimizamos, el valor interno de la tabla suele ser -Z
        if not self.is_max:
            z = abs(z)

        sensitivity = {"variables": [], "constraints": []}
        for j in range(self.num_vars):
            sensitivity["variables"].append({
                "name": f"x{j+1}",
                "final_value": solution[f"x{j+1}"],
                "reduced_cost": float(self.tableau[-1, j])
            })

        for i, bv in enumerate(self.basic_vars):
            if bv is not None:
                name = self.col_headers[bv]
                sensitivity["constraints"].append({
                    "id": i + 1,
                    "slack_value": float(self.tableau[i, -1]) if name.startswith("s") or name.startswith("e") else 0.0,
                    "dual_price": float(abs(self.tableau[-1, bv])) if not (name.startswith("x") or name.startswith("s")) else 0.0
                })

        return solution, z, sensitivity

# ======================================================
#   SOLVERS
# ======================================================

class SimplexSolver(BaseSimplex):
    def solve(self):
        self._initialize_matrix()
        self._fill_constraints()
        self.tableau[-1, :self.num_vars] = -self.c if self.is_max else self.c
        self._save_step("Tabla Inicial")
        for _ in range(100):
            col, row = self._find_pivot()
            if col is None: break
            if row is None: return {"status": "unbounded"}
            self._pivot(row, col)
            self._save_step("Iteración", (row, col))
        sol, z, sens = self._extract_solution()
        return {"status": "optimal", "objective_value": z, "variable_values": sol, "sensitivity_analysis": sens, "steps": self.steps}

class BigMSolver(BaseSimplex):
    def solve(self):
        self._initialize_matrix()
        art_rows = self._fill_constraints()
        # M dinámico para evitar desbordamiento o falta de precisión
        M = max(1000, np.max(np.abs(self.c)) * 100)
        
        self.tableau[-1, :self.num_vars] = -self.c if self.is_max else self.c
        for j, h in enumerate(self.col_headers):
            if h.startswith("a"):
                self.tableau[-1, j] = M
        
        for i in art_rows:
            self.tableau[-1] -= self.tableau[-1, self.basic_vars[i]] * self.tableau[i]
            
        self._save_step("Tabla Inicial Gran M")
        for _ in range(200):
            col, row = self._find_pivot()
            if col is None: break
            if row is None: return {"status": "unbounded"}
            self._pivot(row, col)
            self._save_step("Iteración Gran M", (row, col))
            
        sol, z, sens = self._extract_solution()
        return {"status": "optimal", "objective_value": z, "variable_values": sol, "sensitivity_analysis": sens, "steps": self.steps}

class TwoPhaseSolver(BaseSimplex):
    def solve(self):
        self._initialize_matrix()
        art_rows = self._fill_constraints()

        # FASE 1
        self.tableau[-1] = 0
        for i, h in enumerate(self.col_headers):
            if h.startswith("a"): self.tableau[-1, i] = 1
        for r in art_rows: self.tableau[-1] -= self.tableau[r]
        self._save_step("Fase 1 - Inicial")

        for _ in range(100):
            col, row = self._find_pivot()
            if col is None: break
            self._pivot(row, col)
            self._save_step("Fase 1 - Iteración", (row, col))

        if abs(self.tableau[-1, -1]) > 1e-6: return {"status": "infeasible"}

        # TRANSICIÓN
        keep = [i for i, h in enumerate(self.col_headers) if not h.startswith("a")]
        self.tableau = self.tableau[:, keep]
        self.col_headers = [self.col_headers[i] for i in keep]
        
        # Re-sincronizar básicas
        new_basics = []
        for r in range(self.num_constraints):
            found_col = None
            for c in range(self.tableau.shape[1]-1):
                col_data = self.tableau[:self.num_constraints, c]
                if abs(self.tableau[r, c] - 1) < 1e-9 and np.sum(np.abs(col_data)) < 1.00001:
                    found_col = c
                    break
            new_basics.append(found_col)
        self.basic_vars = new_basics

        # FASE 2
        self.tableau[-1] = 0
        self.tableau[-1, :self.num_vars] = -self.c if self.is_max else self.c
        for r, bv in enumerate(self.basic_vars):
            if bv is not None:
                coef = self.tableau[-1, bv]
                self.tableau[-1] -= coef * self.tableau[r]

        self._save_step("Fase 2 - Inicial")
        for _ in range(100):
            col, row = self._find_pivot()
            if col is None: break
            self._pivot(row, col)
            self._save_step("Fase 2 - Iteración", (row, col))

        sol, z, sens = self._extract_solution()
        return {"status": "optimal", "objective_value": z, "variable_values": sol, "sensitivity_analysis": sens, "steps": self.steps}

# ======================================================
#   FUNCIONES DE APOYO
# ======================================================

def solve_graphical(objective_coeffs, constraints, objective):
    if len(objective_coeffs) != 2:
        return {"status": "error", "message": "Solo 2 variables soportadas."}
    
    # Limpiar cualquier rastro de gráficos anteriores
    plt.clf()
    plt.cla()
    
    c = np.array(objective_coeffs, dtype=float)
    sign = -1 if objective == "max" else 1
    A, b_list = [], []

    for r in constraints:
        if r["sign"] == "<=":
            A.append(r["coeffs"])
            b_list.append(r["rhs"])
        elif r["sign"] == ">=":
            A.append([-x for x in r["coeffs"]])
            b_list.append(-r["rhs"])
        # Para el gráfico, las igualdades se grafican pero no se meten al linprog de scipy de esta forma simple
    
    res = linprog(sign * c, A_ub=A if A else None, b_ub=b_list if b_list else None, 
                  bounds=[(0, None), (0, None)], method="highs")
    
    if not res.success:
        return {"status": "infeasible", "message": "No se encontró solución factible."}
    
    # --- GENERACIÓN DEL GRÁFICO ---
    fig, ax = plt.subplots(figsize=(8, 6)) # Usar fig y ax es más seguro para hilos
    
    limit = max([abs(r["rhs"]) for r in constraints] + [10]) * 1.2
    x_vals = np.linspace(0, limit, 400)
    
    for i, r in enumerate(constraints):
        coeffs = r["coeffs"]
        rhs = r["rhs"]
        if coeffs[1] != 0:
            y_vals = (rhs - coeffs[0] * x_vals) / coeffs[1]
            ax.plot(x_vals, y_vals, label=f"R{i+1}: {coeffs[0]}x1 + {coeffs[1]}x2 {r['sign']} {rhs}")
        else: 
            ax.axvline(x=rhs/coeffs[0], label=f"R{i+1}: x1 {r['sign']} {rhs/coeffs[0]}", color='red')

    # Dibujar el punto óptimo
    ax.plot(res.x[0], res.x[1], 'ro', markersize=10, label=f"Óptimo (Z={abs(res.fun):.2f})")
    
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    ax.grid(True, linestyle='--')
    ax.legend()
    
    # --- LA PARTE CRÍTICA: EXTRACCIÓN DEL BASE64 ---
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig) # Liberar memoria
    
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Debug en consola para que veas si ahora sí genera datos
    print(f"DEBUG: Imagen generada con éxito ({len(img_str)} caracteres)")
    
    return {
        "status": "optimal", 
        "objective_value": float(abs(res.fun)), 
        "variable_values": {"x1": float(res.x[0]), "x2": float(res.x[1])}, 
        "graph_image": f"data:image/png;base64,{img_str}"
    }

def solve_linear_program(objective, constraints, method="simplex", obj_type="max"):
    if method == "simplex": return SimplexSolver(objective, constraints, obj_type).solve()
    if method == "big_m": return BigMSolver(objective, constraints, obj_type).solve()
    if method == "two_phase": return TwoPhaseSolver(objective, constraints, obj_type).solve()
    if method == "graphical": return solve_graphical(objective, constraints, obj_type)
    return {"status": "error", "message": "Método no reconocido"}

def generate_intelligent_report(data, result, client=None):
    if not client or result.get("status") != "optimal":
        return "⚠️ IA no disponible o problema sin solución óptima."
    
    prompt = f"""Analiza estos resultados de PL y genera un reporte estratégico en Markdown:
    - Objetivo: {data['objective']}
    - Z*: {result['objective_value']}
    - Solución: {json.dumps(result['variable_values'])}
    Incluye: Resumen Ejecutivo, Análisis de Recursos y Recomendaciones Estratégicas."""
    
    completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
    return completion.choices[0].message.content
def solve_dual_linear_problem(objective, constraints):
    # Esta función estaba en tu código original, asegúrate de incluirla:
    for c in constraints:
        if c["sign"] != "<=": return {"status": "error", "message": "Dual solo admite <="}
    A = [c["coeffs"] for c in constraints]
    b = [c["rhs"] for c in constraints]
    # Usamos c negativo para maximizar el dual (que es minimizar el primal)
    res = linprog(b, A_ub=-np.array(A).T, b_ub=-np.array(objective), bounds=[(0, None)], method="highs")
    if not res.success: return {"status": "error", "message": "Dual no factible."}
    return {"status": "optimal", "dual_solution": res.x.tolist(), "dual_optimal_value": float(res.fun)}