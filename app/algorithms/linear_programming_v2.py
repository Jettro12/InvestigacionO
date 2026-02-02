import numpy as np
from copy import deepcopy

class SimplexSolverV2:
    """
    Algoritmo Simplex robusto implementado desde cero.
    Normaliza problemas a minimización y maneja múltiples tipos de restricciones.
    """
    
    def __init__(self, c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, maximization=True):
        self.c_orig = np.array(c, dtype=float)
        self.n_vars = len(self.c_orig)
        self.maximization = maximization
        
        # Convertir a minimización internamente (min -Z)
        self.c = -self.c_orig if self.maximization else self.c_orig
        
        self.A_ub = np.array(A_ub, dtype=float) if A_ub is not None and len(A_ub) > 0 else np.empty((0, self.n_vars))
        self.b_ub = np.array(b_ub, dtype=float) if b_ub is not None and len(b_ub) > 0 else np.empty(0)
        
        self.A_eq = np.array(A_eq, dtype=float) if A_eq is not None and len(A_eq) > 0 else np.empty((0, self.n_vars))
        self.b_eq = np.array(b_eq, dtype=float) if b_eq is not None and len(b_eq) > 0 else np.empty(0)
        
        self._normalize_rhs()
        
        self.iterations = 0
        self.column_to_var = {} # Mapeo dinámico para extraer la solución

    def solve(self, method='simplex'):
        """
        Método unificado (puente) para llamar a los algoritmos específicos.
        """
        if method == 'two_phase':
            return self.solve_two_phase()
        elif method == 'big_m':
            return self.solve_big_m()
        else:
            return self.solve_simplex()

    def _normalize_rhs(self):
        """Asegura b >= 0 multiplicando la fila por -1 si es necesario"""
        for i in range(len(self.b_ub)):
            if self.b_ub[i] < 0:
                self.A_ub[i] *= -1
                self.b_ub[i] *= -1
        for i in range(len(self.b_eq)):
            if self.b_eq[i] < 0:
                self.A_eq[i] *= -1
                self.b_eq[i] *= -1

    def _build_tableau(self, c_vector, add_slack=True, add_artificial=False):
        """
        Construye el tableau garantizando consistencia dimensional.
        """
        num_ub = len(self.b_ub)
        num_eq = len(self.b_eq)
        total_m = num_ub + num_eq
        
        A_combined = []
        if num_ub > 0: A_combined.append(self.A_ub)
        if num_eq > 0: A_combined.append(self.A_eq)
        
        A_final = np.vstack(A_combined)
        b_final = np.concatenate([self.b_ub, self.b_eq])
        
        # Limpiar mapeo previo
        self.column_to_var = {}
        for i in range(self.n_vars):
            self.column_to_var[i] = ('original', i)

        tableau_cols = [A_final]
        curr_col = self.n_vars

        # Variables de holgura (Slack)
        if add_slack and num_ub > 0:
            slack_matrix = np.zeros((total_m, num_ub))
            slack_matrix[:num_ub, :num_ub] = np.eye(num_ub)
            tableau_cols.append(slack_matrix)
            for i in range(num_ub):
                self.column_to_var[curr_col + i] = ('slack', i)
            curr_col += num_ub

        # Variables artificiales
        if add_artificial:
            art_matrix = np.eye(total_m)
            tableau_cols.append(art_matrix)
            for i in range(total_m):
                self.column_to_var[curr_col + i] = ('artificial', i)

        main_mat = np.hstack(tableau_cols)
        z_row = np.zeros(main_mat.shape[1])
        z_row[:len(c_vector)] = c_vector
        
        tableau = np.vstack([main_mat, z_row])
        rhs_col = np.append(b_final, 0).reshape(-1, 1)
        tableau = np.hstack([tableau, rhs_col])
        
        return tableau

    def _find_pivot(self, tableau):
        """Busca columna y fila pivote usando la prueba de la razón mínima."""
        cost_row = tableau[-1, :-1]
        if np.all(cost_row >= -1e-10): 
            return None, None
        
        pivot_col = np.argmin(cost_row)
        
        b = tableau[:-1, -1]
        a_col = tableau[:-1, pivot_col]
        
        ratios = []
        for i in range(len(b)):
            if a_col[i] > 1e-10:
                ratios.append(b[i] / a_col[i])
            else:
                ratios.append(np.inf)
        
        pivot_row = np.argmin(ratios)
        if ratios[pivot_row] == np.inf: 
            return pivot_col, None
        
        return pivot_col, pivot_row

    def _pivot(self, tableau, row, col):
        """Operación de Gauss-Jordan."""
        tableau[row, :] /= tableau[row, col]
        for i in range(tableau.shape[0]):
            if i != row:
                tableau[i, :] -= tableau[i, col] * tableau[row, :]
        return tableau

    def solve_simplex(self):
        tableau = self._build_tableau(self.c)
        return self._run_iterations(tableau)

    def solve_two_phase(self):
        """Método de Dos Fases."""
        c_phase1 = np.zeros(self.n_vars) 
        tableau = self._build_tableau(c_phase1, add_slack=True, add_artificial=True)
        art_cols = [idx for idx, (t, _) in self.column_to_var.items() if t == 'artificial']
        
        tableau[-1, art_cols] = 1
        for col in art_cols:
            row = col - (self.n_vars + (len(self.b_ub) if len(self.b_ub) > 0 else 0))
            tableau[-1, :] -= tableau[row, :]

        self._run_iterations(tableau)
        
        if abs(tableau[-1, -1]) > 1e-6:
            return {"status": "Infeasible", "message": "El problema no tiene solución factible."}

        # Fase II
        new_tableau = np.delete(tableau, art_cols, axis=1)
        new_tableau[-1, :] = 0
        new_tableau[-1, :self.n_vars] = self.c
        
        # Re-mapear columnas tras eliminar artificiales
        self.column_to_var = {k: v for k, v in self.column_to_var.items() if v[0] != 'artificial'}

        # Re-ajustar base para que los costos de variables básicas sean 0
        for j in range(new_tableau.shape[1] - 1):
            col_data = new_tableau[:-1, j]
            if np.sum(col_data == 1) == 1 and np.sum(np.abs(col_data) > 1e-10) == 1:
                row = np.where(col_data == 1)[0][0]
                new_tableau[-1, :] -= new_tableau[-1, j] * new_tableau[row, :]

        return self._run_iterations(new_tableau)

    def solve_big_m(self, M=1000000):
        tableau = self._build_tableau(self.c, add_slack=True, add_artificial=True)
        art_cols = [idx for idx, (t, _) in self.column_to_var.items() if t == 'artificial']
        
        tableau[-1, art_cols] = M
        for col in art_cols:
            row = col - (self.n_vars + (len(self.b_ub) if len(self.b_ub) > 0 else 0))
            tableau[-1, :] -= M * tableau[row, :]

        return self._run_iterations(tableau)

    def _run_iterations(self, tableau):
        max_iter = 1000
        while self.iterations < max_iter:
            col, row = self._find_pivot(tableau)
            if col is None: break
            if row is None: return {"status": "Unbounded", "message": "Problema no acotado."}
            
            tableau = self._pivot(tableau, row, col)
            self.iterations += 1
            
        return self._extract_solution(tableau)

    def _extract_solution(self, tableau):
        """Extrae la solución y corrige el signo del valor óptimo."""
        x = np.zeros(self.n_vars)
        for j in range(tableau.shape[1] - 1):
            col_data = tableau[:-1, j]
            # Identificar columna básica (un 1 y el resto ceros)
            if np.abs(np.sum(col_data) - 1.0) < 1e-10 and np.count_nonzero(np.abs(col_data) > 1e-10) == 1:
                row = np.where(np.abs(col_data - 1.0) < 1e-10)[0][0]
                if j in self.column_to_var:
                    type_v, idx_v = self.column_to_var[j]
                    if type_v == 'original':
                        x[idx_v] = max(0, tableau[row, -1])
        
        # El valor en tableau[-1, -1] ya es correcto sin necesidad de negar
        # Para maximización: se minimiza -Z, resultado es -Z, pero se almacena como valor positivo en tableau
        # Así que simplemente usamos el valor como está
        tableau_value = tableau[-1, -1]
        final_z = float(tableau_value)
        
        return {
            "status": "Optimal",
            "objective_value": round(final_z, 4),
            "variable_values": {f"x{i+1}": round(float(val), 4) for i, val in enumerate(x)},
            "iterations": self.iterations
        }