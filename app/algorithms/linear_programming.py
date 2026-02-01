from scipy.optimize import linprog

def solve_linear_program(c, A_ub, b_ub):
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, method="highs")
    return {
        "status": "success" if result.success else "failed",
        "solution": result.x.tolist() if result.success else None,
        "message": result.message
    }
