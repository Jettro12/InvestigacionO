from algorithms.custom_simplex import SimplexSolver

def solve_linear_program(c, A_ub, b_ub):
    """
    Legacy wrapper for existing service calls using custom Simplex.
    Refers to standard form: Max/Min c*x subject to A_ub * x <= b_ub
    """
    # Assumptions for this wrapper based on typical scipy.linprog behavior (Minimization)
    
    signs = ['<='] * len(b_ub)
    
    # Scipy linprog usually takes 'Min c'.
    # So we set objective='min'.
    
    solver = SimplexSolver(c, A_ub, b_ub, signs, objective='min', method='simplex')
    result = solver.solve()
    
    return {
        "status": "success" if result["status"] == "Optimal" else "failed",
        "solution": list(result["variable_values"].values()), # Just values list
        "message": result["status"]
    }
