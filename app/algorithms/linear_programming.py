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
        rows = len(self.constraints) + 1
        self.tableau = np.zeros((rows, cols))

    def _fill_constraints(self):
        s = self.num_vars
        e = s + self.num_slack
        a = e + self.num_surplus
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
                self.tableau[i, s + cs] = 1
                self.basic_vars.append(s + cs)
                cs += 1
            elif r["sign"] == ">=":
                self.tableau[i, e + ce] = -1
                self.tableau[i, a + ca] = 1
                self.basic_vars.append(a + ca)
                art_rows.append(i)
                ce += 1
                ca += 1
            elif r["sign"] == "=":
                self.tableau[i, a + ca] = 1
                self.basic_vars.append(a + ca)
                art_rows.append(i)
                ca += 1
        return art_rows

    def _save_step(self, desc, pivot=None):
        self.steps.append({
            "description": desc,
            "tableau": self.tableau.tolist(),
            "headers": self.col_headers,
            "basic_vars": [self.col_headers[i] for i in self.basic_vars],
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
        if np.all(z >= -1e-9):
            return None, None
        col = int(np.argmin(z))
        ratios = []
        for i in range(len(self.constraints)):
            val = self.tableau[i, col]
            if val > 1e-9:
                ratios.append((self.tableau[i, -1] / val, i))
        if not ratios:
            return col, None
        _, row = min(ratios)
        return col, row


    def _is_feasible(self):
        for i, bv_idx in enumerate(self.basic_vars):
            if self.col_headers[bv_idx].startswith("a"):
                if self.tableau[i, -1] > 1e-6:
                    return False
        return True

    def _extract_solution(self):
        solution = {f"x{i+1}": 0.0 for i in range(self.num_vars)}
        for row, col in enumerate(self.basic_vars):
            if col < self.num_vars:
                solution[f"x{col+1}"] = float(self.tableau[row, -1])

        z = float(self.tableau[-1, -1])
        if not self.is_max:
            z *= -1

        sensitivity = {"variables": [], "constraints": []}

        for j in range(self.num_vars):
            sensitivity["variables"].append({
                "name": f"x{j+1}",
                "final_value": solution[f"x{j+1}"],
                "reduced_cost": float(self.tableau[-1, j])
            })

        for i, bv in enumerate(self.basic_vars):
            name = self.col_headers[bv]
            slack = self.tableau[i, -1] if name.startswith("s") else 0.0
            dual = -self.tableau[-1, bv] if not name.startswith("s") else 0.0
            sensitivity["constraints"].append({
                "id": i + 1,
                "slack_value": float(slack),
                "dual_price": float(dual)
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
            if col is None:
                break
            if row is None:
                return {"status": "unbounded"}
            self._pivot(row, col)
            self._save_step("Iteración", (row, col))
        sol, z, sens = self._extract_solution()
        return {"status": "optimal", "objective_value": z,
                "variable_values": sol, "sensitivity_analysis": sens, "steps": self.steps}


class BigMSolver(BaseSimplex):
    def solve(self):
        self._initialize_matrix()
        self._fill_constraints()
        M = 1e6
        self.tableau[-1] = 0
        self.tableau[-1, :self.num_vars] = -self.c if self.is_max else self.c
        for j, h in enumerate(self.col_headers):
            if h.startswith("a"):
                self.tableau[-1, j] = M
        for i, bv in enumerate(self.basic_vars):
            coef = self.tableau[-1, bv]
            if abs(coef) > 1e-9:
                self.tableau[-1] -= coef * self.tableau[i]
        self._save_step("Tabla Inicial Gran M")
        for _ in range(200):
            col, row = self._find_pivot()
            if col is None:
                break
            self._pivot(row, col)
            self._save_step("Iteración Gran M", (row, col))
        sol, z, sens = self._extract_solution()
        return {"status": "optimal", "objective_value": z,
                "variable_values": sol, "sensitivity_analysis": sens, "steps": self.steps}


class TwoPhaseSolver(BaseSimplex):
    def solve(self):
        self._initialize_matrix()
        art_rows = self._fill_constraints()

        self.tableau[-1] = 0
        for r in art_rows:
            self.tableau[-1] -= self.tableau[r]
        self._save_step("Fase 1 - Tabla Inicial")

        for _ in range(100):
            col, row = self._find_pivot()
            if col is None:
                break
            self._pivot(row, col)
            self._save_step("Fase 1 - Iteración", (row, col))

        if abs(self.tableau[-1, -1]) > 1e-6:
            return {"status": "infeasible"}

        keep = [i for i, h in enumerate(self.col_headers) if not h.startswith("a")]
        self.tableau = self.tableau[:, keep]
        self.col_headers = [self.col_headers[i] for i in keep]
        self.basic_vars = [keep.index(bv) for bv in self.basic_vars if bv in keep]

        self.tableau[-1] = 0
        self.tableau[-1, :self.num_vars] = -self.c if self.is_max else self.c
        for i, bv in enumerate(self.basic_vars):
            coef = self.tableau[-1, bv]
            if abs(coef) > 1e-9:
                self.tableau[-1] -= coef * self.tableau[i]

        self._save_step("Fase 2 - Tabla Inicial")
        for _ in range(100):
            col, row = self._find_pivot()
            if col is None:
                break
            self._pivot(row, col)
            self._save_step("Fase 2 - Iteración", (row, col))

        sol, z, sens = self._extract_solution()
        return {"status": "optimal", "objective_value": z,
                "variable_values": sol, "sensitivity_analysis": sens, "steps": self.steps}


# ======================================================
#   FUNCIONES DE APOYO
# ======================================================

def solve_graphical(objective_coeffs, constraints, objective):
    if len(objective_coeffs) != 2:
        return {"status": "error", "message": "Solo 2 variables soportadas."}
    
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
    
    res = linprog(sign * c, A_ub=A if A else None, b_ub=b_list if b_list else None, 
                  bounds=[(0, None), (0, None)], method="highs")
    
    if not res.success:
        return {"status": "infeasible", "message": "No se encontró solución factible."}
    
    # --- GENERACIÓN DEL GRÁFICO ---
    plt.figure(figsize=(8, 6))
    abs_rhs = [abs(r["rhs"]) for r in constraints]
    limit = max(abs_rhs) * 1.5 if abs_rhs and max(abs_rhs) > 0 else 50
    x_vals = np.linspace(0, limit, 400)
    
    for i, r in enumerate(constraints):
        coeffs = r["coeffs"]
        rhs = r["rhs"]
        if coeffs[1] != 0:
            y_vals = (rhs - coeffs[0] * x_vals) / coeffs[1]
            plt.plot(x_vals, y_vals, label=f"R{i+1}: {coeffs[0]}x1 + {coeffs[1]}x2 {r['sign']} {rhs}")
        else: 
            plt.axvline(x=rhs/coeffs[0], label=f"R{i+1}: x1 {r['sign']} {rhs/coeffs[0]}", color='red')

    plt.plot(res.x[0], res.x[1], 'ro', label=f"Óptimo (Z={abs(res.fun):.2f})")
    plt.xlim(0, limit)
    plt.ylim(0, limit)
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.grid(True, linestyle='--')
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return {
        "status": "optimal", 
        "objective_value": float(abs(res.fun)), 
        "variable_values": {"x1": float(res.x[0]), "x2": float(res.x[1])}, 
        "graph_image": f"data:image/png;base64,{img_base64}"
    }

def solve_dual_linear_problem(objective, constraints):
    for c in constraints:
        if c["sign"] != "<=": return {"status": "error", "message": "Dual solo admite <="}
    A = [c["coeffs"] for c in constraints]
    b = [c["rhs"] for c in constraints]
    res = linprog(b, A_ub=-np.array(A).T, b_ub=-np.array(objective), bounds=[(0, None)], method="highs")
    if not res.success: return {"status": "error", "message": "Dual no factible."}
    return {"status": "optimal", "dual_solution": res.x.tolist(), "dual_optimal_value": float(res.fun)}

def solve_simplex(objective, constraints, obj_type="max"): 
    return SimplexSolver(objective, constraints, obj_type).solve()

def solve_big_m(objective, constraints, obj_type="max"): 
    return BigMSolver(objective, constraints, obj_type).solve()

def solve_two_phase(objective, constraints, obj_type="max"): 
    return TwoPhaseSolver(objective, constraints, obj_type).solve()

def solve_dual(objective, constraints): 
    return solve_dual_linear_problem(objective, constraints)

def generate_intelligent_report(data, result, client=None):
    if not client:
        return "⚠️ IA no configurada."

    if result.get("status") != "optimal":
        return "⚠️ El problema no tiene solución óptima. No se genera análisis estratégico."

    try:
        obj_type = "Maximización" if data["objective"] == "max" else "Minimización"
        sens = result.get("sensitivity_analysis", {})

        # Detección correcta de soluciones múltiples
        is_multiple = any(
            abs(v["reduced_cost"]) < 1e-6 and abs(v["final_value"]) < 1e-6
            for v in sens.get("variables", [])
        )

        nota_multiple = (
            "### 💡 NOTA: Se detectaron SOLUCIONES MÚLTIPLES. "
            "Existen otros puntos óptimos con el mismo valor de Z.\n"
            if is_multiple else ""
        )

        recursos_criticos = [
            f"R{c['id']}" for c in sens.get("constraints", [])
            if c.get("dual_price", 0) > 1e-6
        ]
        recursos_txt = ", ".join(recursos_criticos) if recursos_criticos else "Ninguno (todos tienen holgura)"

        prompt = f"""
Actúa como un Consultor Senior en Investigación de Operaciones.
Analiza estos resultados de Programación Lineal y genera un reporte estratégico en Markdown.
{nota_multiple}

### 📊 DATOS TÉCNICOS
- Objetivo: {obj_type} de la función Z
- Valor Óptimo (Z*): {result.get("objective_value")}
- Variables de Decisión Óptimas: {json.dumps(result.get("variable_values"))}
- Recursos Críticos (Precio Sombra > 0): {recursos_txt}

### 📋 INSTRUCCIONES
1. No menciones estadística descriptiva.
2. No utilices análisis de Pareto ni histogramas.
3. Interpreta únicamente resultados de optimización.
4. Estructura el reporte en:
   - Resumen Ejecutivo
   - Análisis de Recursos
   - Recomendaciones Estratégicas
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Error IA: {str(e)}"

# --- Función Maestra para conectar con el Servicio ---

def solve_linear_program(objective, constraints, method="simplex", obj_type="max"):
    """
    Función puente que redirige al algoritmo correcto según el método solicitado.
    """
    if method == "simplex":
        return solve_simplex(objective, constraints, obj_type)
    elif method == "big_m":
        return solve_big_m(objective, constraints, obj_type)
    elif method == "two_phase":
        return solve_two_phase(objective, constraints, obj_type)
    elif method == "graphical":
        return solve_graphical(objective, constraints, obj_type)
    elif method == "dual":
        return solve_dual(objective, constraints)
    else:
        return {"status": "error", "message": f"Método '{method}' no reconocido."}