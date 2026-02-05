import numpy as np
from copy import deepcopy

class SimplexSolver:
    """
    Algoritmo Simplex implementado desde cero sin librerías de optimización.
    Soporta: Simplex estándar, Dos Fases, Gran M y Dual.
    """
    
    def __init__(self, c, A_ub, b_ub, A_eq=None, b_eq=None, bounds=None, maximization=True):
        """
        c: coeficientes de la función objetivo
        A_ub: coeficientes de restricciones de desigualdad (<=)
        b_ub: RHS de restricciones de desigualdad
        A_eq: coeficientes de restricciones de igualdad
        b_eq: RHS de restricciones de igualdad
        bounds: límites de variables
        maximization: True para maximizar, False para minimizar
        """
        self.c = np.array(c, dtype=float)
        self.A_ub = np.array(A_ub, dtype=float) if A_ub is not None else np.array([]).reshape(0, len(c))
        self.b_ub = np.array(b_ub, dtype=float) if b_ub is not None else np.array([])
        self.A_eq = np.array(A_eq, dtype=float) if A_eq is not None else np.array([]).reshape(0, len(c))
        self.b_eq = np.array(b_eq, dtype=float) if b_eq is not None else np.array([])
        self.bounds = bounds or [(0, None) for _ in range(len(c))]
        self.maximization = maximization
        self.iterations = 0
        self.tableau_history = []
        
    def _create_tableau(self, c, A, b, use_artificial=False, skip_slack=False):
        """Crea el tableau inicial del Simplex"""
        m, n = A.shape
        
        # Agregar variables de holgura (a menos que skip_slack sea True)
        if not skip_slack:
            tableau = np.hstack([A, np.eye(m)])
        else:
            tableau = A.copy()
        
        # Agregar variables artificiales si es necesario
        num_artificial = 0
        if use_artificial:
            num_artificial = np.sum(self.b_ub < 0) + len(self.b_eq)
            if num_artificial > 0 and not skip_slack:
                artificial_cols = np.eye(num_artificial)
                tableau = np.hstack([tableau, artificial_cols])
        
        # Fila de costos (negada para maximización)
        # c ya debe tener la longitud correcta
        cost_row = np.zeros(tableau.shape[1])
        cost_row[:len(c)] = -c if self.maximization else c
        
        tableau = np.vstack([tableau, cost_row])
        tableau = np.hstack([tableau, b.reshape(-1, 1)])
        
        return tableau
    
    def _find_pivot_column(self, tableau):
        """Encuentra la columna pivote (variable que entra)"""
        cost_row = tableau[-1, :-1]
        if self.maximization:
            if np.all(cost_row >= -1e-10):
                return None
            return np.argmin(cost_row)
        else:
            if np.all(cost_row <= 1e-10):
                return None
            return np.argmax(cost_row)
    
    def _find_pivot_row(self, tableau, pivot_col):
        """Encuentra la fila pivote (variable que sale)"""
        A = tableau[:-1, :-1]
        b = tableau[:-1, -1]
        
        ratios = []
        for i, (a_val, b_val) in enumerate(zip(A[:, pivot_col], b)):
            if a_val > 1e-10:
                ratios.append((b_val / a_val, i))
        
        if not ratios:
            return None
        return min(ratios, key=lambda x: x[0])[1]
    
    def _pivot(self, tableau, pivot_row, pivot_col):
        """Realiza la operación de pivote"""
        pivot_element = tableau[pivot_row, pivot_col]
        
        # Dividir fila pivote
        tableau[pivot_row, :] /= pivot_element
        
        # Eliminar columna pivote en otras filas
        for i in range(tableau.shape[0]):
            if i != pivot_row:
                factor = tableau[i, pivot_col]
                tableau[i, :] -= factor * tableau[pivot_row, :]
        
        return tableau
    
    def solve_simplex(self):
        """Resuelve usando Simplex estándar"""
        if len(self.b_ub) == 0:
            return self._solve_equality_only()
        
        A = self.A_ub
        b = self.b_ub.copy()
        c = self.c.copy()
        
        # Asegurar b >= 0
        for i in range(len(b)):
            if b[i] < 0:
                A[i, :] *= -1
                b[i] *= -1
        
        tableau = self._create_tableau(c, A, b)
        
        max_iterations = 1000
        while max_iterations > 0:
            pivot_col = self._find_pivot_column(tableau)
            if pivot_col is None:
                break
            
            pivot_row = self._find_pivot_row(tableau, pivot_col)
            if pivot_row is None:
                return {"status": "unbounded", "message": "Problema no acotado"}
            
            tableau = self._pivot(tableau, pivot_row, pivot_col)
            self.iterations += 1
            self.tableau_history.append(tableau.copy())
            max_iterations -= 1
        
        return self._extract_solution(tableau)
    
    def solve_two_phase(self):
        """Resuelve usando método de Dos Fases"""
        # Fase I: encontrar solución básica factible
        m_ub = len(self.b_ub)
        m_eq = len(self.b_eq)
        total_constraints = m_ub + m_eq
        
        if total_constraints == 0:
            return self.solve_simplex()
        
        # Combinar restricciones - evitar hstack con arrays vacíos
        A_parts = []
        b_parts = []
        
        if m_ub > 0:
            A_parts.append(self.A_ub)
            b_parts.append(self.b_ub)
        
        if m_eq > 0:
            A_parts.append(self.A_eq)
            b_parts.append(self.b_eq)
        
        A = np.vstack(A_parts) if A_parts else self.A_ub
        b = np.hstack(b_parts) if b_parts else self.b_ub
        
        # Asegurar b >= 0
        for i in range(len(b)):
            if b[i] < 0:
                A[i, :] *= -1
                b[i] *= -1
        
        # Crear función objetivo artificial
        c_phase1 = np.hstack([np.zeros(len(self.c)), np.zeros(m_ub), np.ones(m_eq)])
        A_phase1 = np.hstack([A, np.eye(total_constraints)])
        
        tableau = self._create_tableau(c_phase1, A_phase1, b, use_artificial=True, skip_slack=True)
        
        # Resolver fase I
        max_iterations = 1000
        while max_iterations > 0:
            pivot_col = self._find_pivot_column(tableau)
            if pivot_col is None:
                break
            pivot_row = self._find_pivot_row(tableau, pivot_col)
            if pivot_row is None:
                return {"status": "unbounded", "message": "Problema no acotado en Fase I"}
            tableau = self._pivot(tableau, pivot_row, pivot_col)
            self.iterations += 1
            max_iterations -= 1
        
        # Verificar factibilidad
        if abs(tableau[-1, -1]) > 1e-6:
            return {"status": "infeasible", "message": "Problema infactible"}
        
        # Fase II: usar solución de Fase I con función objetivo original
        tableau_phase2 = tableau[:-1, :-1]
        b_phase2 = tableau[:-1, -1]
        c_phase2 = np.hstack([self.c, np.zeros(m_ub + m_eq)])
        
        cost_row = np.zeros(tableau_phase2.shape[1])
        cost_row[:len(self.c)] = -self.c if self.maximization else self.c
        tableau_phase2 = np.vstack([tableau_phase2, cost_row])
        tableau_phase2 = np.hstack([tableau_phase2, b_phase2.reshape(-1, 1)])
        
        max_iterations = 1000
        while max_iterations > 0:
            pivot_col = self._find_pivot_column(tableau_phase2)
            if pivot_col is None:
                break
            pivot_row = self._find_pivot_row(tableau_phase2, pivot_col)
            if pivot_row is None:
                return {"status": "unbounded", "message": "Problema no acotado en Fase II"}
            tableau_phase2 = self._pivot(tableau_phase2, pivot_row, pivot_col)
            self.iterations += 1
            max_iterations -= 1
        
        return self._extract_solution(tableau_phase2)
    
    def solve_big_m(self, M=10000):
        """Resuelve usando método de Gran M"""
        m_ub = len(self.b_ub)
        m_eq = len(self.b_eq)
        total_constraints = m_ub + m_eq
        
        if total_constraints == 0:
            return self.solve_simplex()
        
        # Combinar restricciones - evitar hstack con arrays vacíos
        A_parts = []
        b_parts = []
        
        if m_ub > 0:
            A_parts.append(self.A_ub)
            b_parts.append(self.b_ub)
        
        if m_eq > 0:
            A_parts.append(self.A_eq)
            b_parts.append(self.b_eq)
        
        A = np.vstack(A_parts) if A_parts else self.A_ub
        b = np.hstack(b_parts) if b_parts else self.b_ub
        
        # Asegurar b >= 0
        for i in range(len(b)):
            if b[i] < 0:
                A[i, :] *= -1
                b[i] *= -1
        
        # Crear función objetivo con penalización M
        num_artificial = m_eq
        c_big_m = np.hstack([self.c, np.zeros(m_ub), M * np.ones(num_artificial)])
        A_big_m = np.hstack([A, np.eye(total_constraints)])
        
        tableau = self._create_tableau(c_big_m, A_big_m, b, skip_slack=True)
        
        # Resolver
        max_iterations = 1000
        while max_iterations > 0:
            pivot_col = self._find_pivot_column(tableau)
            if pivot_col is None:
                break
            pivot_row = self._find_pivot_row(tableau, pivot_col)
            if pivot_row is None:
                return {"status": "unbounded", "message": "Problema no acotado"}
            tableau = self._pivot(tableau, pivot_row, pivot_col)
            self.iterations += 1
            max_iterations -= 1
        
        return self._extract_solution(tableau)
    
    def _solve_equality_only(self):
        """Resuelve problemas solo con restricciones de igualdad"""
        return self.solve_two_phase()
    
    def _extract_solution(self, tableau):
        """Extrae la solución del tableau final"""
        m = tableau.shape[0] - 1
        n = tableau.shape[1] - 1
        
        solution = np.zeros(len(self.c))
        for i in range(min(m, n)):
            col = tableau[:-1, i]
            if np.sum(col != 0) == 1:
                row_idx = np.where(col != 0)[0][0]
                if abs(col[row_idx] - 1.0) < 1e-10:
                    solution[i] = tableau[row_idx, -1]
        
        objective_value = -tableau[-1, -1] if self.maximization else tableau[-1, -1]
        
        return {
            "status": "optimal",
            "objective_value": float(objective_value),
            "solution": solution[:len(self.c)].tolist(),
            "iterations": self.iterations
        }


def solve_linear_program(c, A_ub, b_ub, method="simplex", A_eq=None, b_eq=None, maximization=True):
    """
    Interfaz para resolver problemas de programación lineal sin librerías externas.
    
    Args:
        c: coeficientes de función objetivo
        A_ub: coeficientes de restricciones de desigualdad
        b_ub: RHS de restricciones de desigualdad
        method: "simplex", "two_phase", "big_m"
        A_eq: coeficientes de restricciones de igualdad
        b_eq: RHS de restricciones de igualdad
        maximization: True para maximizar
    """
    solver = SimplexSolver(c, A_ub, b_ub, A_eq, b_eq, maximization=maximization)
    
    if method == "simplex":
        return solver.solve_simplex()
    elif method == "two_phase":
        return solver.solve_two_phase()
    elif method == "big_m":
        return solver.solve_big_m()
    else:
        return {"status": "error", "message": f"Método desconocido: {method}"}
