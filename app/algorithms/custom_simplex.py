import math

class SimplexSolver:
    def __init__(self, c, A, b, signs, objective='max', method='simplex', variable_names=None):
        """
        c: List of objective coefficients
        A: Matrix of constraint coefficients
        b: List of RHS values
        signs: List of constraint signs ('<=', '>=', '=')
        objective: 'max' or 'min'
        method: 'simplex', 'm_big', 'two_phase'
        """
        self.original_c = list(c)
        self.original_A = [list(row) for row in A]
        self.original_b = list(b)
        self.signs = list(signs)
        self.objective = objective
        self.method = method
        self.variable_names = variable_names if variable_names else [f"x{i+1}" for i in range(len(c))]
        
        # Internal state
        self.tableau = []
        self.basic_vars = []  # Indices of basic variables
        self.num_vars = len(c)
        self.num_constraints = len(b)
        self.M = 10000.0  # Big M value
        
        self.status = "Not Started"
        self.iterations = 0
        self.solution = {}
        self.objective_value = 0.0
        self.art_vars_indices = []

    def _prepare_tableau(self):
        """Converts problem to standard form and builds initial tableau."""
        
        # Adjust objective for Minimization -> standard is Maximization
        # Min Z <=> Max -Z
        if self.objective == 'min':
            self.c = [-val for val in self.original_c]
        else:
            self.c = list(self.original_c)

        # Initialize extended matrix
        self.A = [list(row) for row in self.original_A]
        self.b = list(self.original_b)
        
        # Track types of added variables for reporting
        self.col_names = list(self.variable_names)
        
        next_var_idx = self.num_vars
        
        # Add Slack, Surplus, Artificial variables
        self.art_vars_indices = []
        
        for i, sign in enumerate(self.signs):
            if sign == '<=':
                # Add Slack (s_i)
                for row in self.A: row.append(0.0)
                self.A[i][-1] = 1.0
                self.c.append(0.0)
                self.col_names.append(f"s{i+1}")
                self.basic_vars.append(next_var_idx)
                next_var_idx += 1
                
            elif sign == '>=':
                # Add Surplus (s_i) - coeff -1
                for row in self.A: row.append(0.0)
                self.A[i][-1] = -1.0
                self.c.append(0.0)
                self.col_names.append(f"s{i+1}") # surplus
                next_var_idx += 1
                
                # Add Artificial (a_i)
                for row in self.A: row.append(0.0)
                self.A[i][-1] = 1.0
                if self.method == 'm_big':
                    self.c.append(-self.M)
                else:
                     # For Two Phase (Phase 1), coeffs are handle differently, 
                     # but here we set 0 for original obj, handled later
                    self.c.append(0.0) # Placeholder
                    
                self.col_names.append(f"a{i+1}")
                self.basic_vars.append(next_var_idx)
                self.art_vars_indices.append(next_var_idx)
                next_var_idx += 1
                
            elif sign == '=':
                # Add Artificial (a_i)
                for row in self.A: row.append(0.0)
                self.A[i][-1] = 1.0
                if self.method == 'm_big':
                    self.c.append(-self.M)
                else:
                    self.c.append(0.0) # Placeholder
                self.col_names.append(f"a{i+1}")
                self.basic_vars.append(next_var_idx)
                self.art_vars_indices.append(next_var_idx)
                next_var_idx += 1

        # Build full tableau
        # Rows: Constraints
        # Last Row: Z - (C_B * B^-1 * A) ... essentially reduced costs
        # But standard Simplex Tableau often computed as:
        # Z row = C_j - Z_j where Z_j = C_B * column_j.
        # Ideally, we put:
        # [ A |  b ]
        # [ c |  0 ] (reduced costs row)
        
        # NOTE: For Two-Phase, we might change the Z row completely in Phase 1.
        
        num_cols = len(self.c)
        self.tableau = []
        for i in range(self.num_constraints):
            row = self.A[i] + [self.b[i]]
            self.tableau.append(row)
            
        # Z Row (Initial)
        # We need to canonicalize the Z row if basic vars have non-zero costs (Big M)
        # Z starts as sum(c_j * x_j). In tableau we treat it as row 0.
        # Row 0: -c_1, -c_2, ..., 0 (rhs) if basic vars are slacks (cost 0).
        # If Artificials are basic, we must eliminate them from Z row.
        
        z_row = [-val for val in self.c] + [0.0]
        self.tableau.append(z_row)
        
        # Canonicalize (make basic column coeffs 0 in Z row)
        for i, basic_idx in enumerate(self.basic_vars):
            pivot_row = self.tableau[i]
            z_coeff = self.tableau[-1][basic_idx]
            if abs(z_coeff) > 1e-9:
                # Row_Z = Row_Z - z_coeff * Row_i (Wait, basic col should have 1 in row_i)
                # Ensure the basic column has 1 in the pivot row? Yes, by construction it does.
                for j in range(len(z_row)):
                    self.tableau[-1][j] += z_coeff * pivot_row[j] # Adding because z_row started with -c

    def solve(self):
        # Check if we need simple Two Phase dispatch based on constraints
        # Artificial vars are needed for '>=' and '='
        needs_artificial = any(s in ['>=', '='] for s in self.signs)
        
        if self.method == 'two_phase' and needs_artificial:
            return self._solve_two_phase()
        else:
            # Standard or Big M (Big M handles logic in _prepare_tableau via costs)
            self._prepare_tableau()
            return self._simplex_algorithm()

    def _solve_two_phase(self):
        # Phase 1: Minimize sum of artificial variables
        # Construct Phase 1 Tableau
        # Keep original logic for A and b, but change c temporarily
        
        # 1. Prepare basics
        self._prepare_tableau()
        
        # 2. Modify Z row for Phase 1
        # Objective: Min W = Sum(Artificials) => Max -W = -Sum(Artificials)
        # So coeffs for Artificials are -1. Coeffs for others are 0.
        
        phase1_c = [0.0] * (len(self.tableau[0]) - 1)
        for idx in self.art_vars_indices:
            phase1_c[idx] = -1.0
            
        # Replace Z row
        self.tableau[-1] = [-val for val in phase1_c] + [0.0]
        
        # Canonicalize Phase 1 Z row
        for i, basic_idx in enumerate(self.basic_vars):
            if basic_idx in self.art_vars_indices: # Should be all artificials initially basic?
                # The basic vars for rows with artificials ARE the artificials.
                z_coeff = self.tableau[-1][basic_idx]
                if abs(z_coeff) > 1e-9:
                     # The coeff in Z row is likely 1.0 (from -(-1)).
                     # We subtract the row to make it 0.
                     # Actually, since we want to ZERO out the basic column in Z row:
                     # current_val + factor * row_val = 0 => factor = -current_val (assuming row_val is 1)
                     pivot_row = self.tableau[i]
                     factor = -self.tableau[-1][basic_idx]
                     for j in range(len(self.tableau[-1])):
                         self.tableau[-1][j] += factor * pivot_row[j]
                         
        # Solve Phase 1
        result = self._simplex_algorithm(phase_one=True)
        if result['status'] != 'Optimal':
            return result
            
        # Check Optimal Value of Phase 1
        w_val = self.tableau[-1][-1]
        
        # If W < 0 (since we Maximized -W), then Sum(Artificials) > 0 => Infeasible
        # Tolerance check
        if abs(w_val) > 1e-6:
             self.status = 'Infeasible'
             return self._format_result()
             
        # Phase 2
        # Remove Artificial Columns? Or just ensure they don't enter.
        # Restore original Objective Function
        
        # Re-build Z row with original costs
        z_row = [-val for val in self.c] + [0.0] # self.c has original costs (with 0 placeholder for artificials)
        self.tableau[-1] = z_row
        
        # Canonicalize Z row again with current basis
        for i, basic_idx in enumerate(self.basic_vars):
            pivot_row = self.tableau[i]
            # Normalize pivot row if needed? Should be 1 already if properly pivoted.
            
            z_coeff = self.tableau[-1][basic_idx]
            if abs(z_coeff) > 1e-9:
                # Eliminate
                factor = -z_coeff # Assuming pivot element is 1
                for j in range(len(self.tableau[-1])):
                    self.tableau[-1][j] += factor * pivot_row[j]
                    
        # Solve Phase 2
        return self._simplex_algorithm()

    def _simplex_algorithm(self, phase_one=False):
        max_iter = 1000
        while self.iterations < max_iter:
            self.iterations += 1
            
            # 1. Check Optimality
            # Find entering variable (Most negative value in Z row for reduced costs if minimized? 
            # Structure: Z row has (C_B B^-1 N - C_N).
            # If we used z_row = -c initially and added rows, we effectively have Z_j - C_j.
            # For Maximization, we want to enter if Z_j - C_j < 0.
            # In our tableau, the Z row represents Z_j - C_j (reduced costs).
            # If any value is negative, we can improve.
            
            z_row = self.tableau[-1][:-1]
            min_val = min(z_row)
            if min_val >= -1e-9:
                self.status = 'Optimal'
                break
                
            entering_col = z_row.index(min_val)
            
            # 2. Ratio Test (Leaving Variable)
            min_ratio = float('inf')
            leaving_row = -1
            
            for i in range(self.num_constraints):
                rhs = self.tableau[i][-1]
                coeff = self.tableau[i][entering_col]
                
                if coeff > 1e-9:
                    ratio = rhs / coeff
                    if ratio < min_ratio:
                        min_ratio = ratio
                        leaving_row = i
                        
            if leaving_row == -1:
                self.status = 'Unbounded'
                return self._format_result()
                
            # 3. Pivot
            self._pivot(leaving_row, entering_col)
            self.basic_vars[leaving_row] = entering_col
            
        return self._format_result()

    def _pivot(self, row_idx, col_idx):
        pivot_val = self.tableau[row_idx][col_idx]
        
        # Normalize pivot row
        self.tableau[row_idx] = [val / pivot_val for val in self.tableau[row_idx]]
        
        # Eliminate other rows
        for i in range(len(self.tableau)):
            if i != row_idx:
                factor = self.tableau[i][col_idx]
                self.tableau[i] = [
                    self.tableau[i][j] - factor * self.tableau[row_idx][j]
                    for j in range(len(self.tableau[i]))
                ]
                
    def _format_result(self):
        # Extract variables
        vars_values = {}
        for i, name in enumerate(self.col_names):
            vars_values[name] = 0.0
            
        for i, basic_idx in enumerate(self.basic_vars):
            if basic_idx < len(self.col_names):
                vars_values[self.col_names[basic_idx]] = self.tableau[i][-1]
                
        # Objective Value
        z_val = self.tableau[-1][-1]
        
        # If Min, result in tableau is Max(-Z), so Z = -Result. But we carry Z row math.
        # Wait, if we reversed C initially, the Optimal Z in tableau relates to -OriginalZ?
        # Let's double check. 
        # Max Z' = -c x. Matches tableau value.
        # Real Z = - Z'.
        
        if self.objective == 'min':
            z_val = -z_val 

        # Filter out slack/artificial for clean output
        clean_vars = {k: v for k, v in vars_values.items() if k in self.variable_names}

        # Artificial checks
        art_vals = {}
        for idx in self.art_vars_indices:
            name = self.col_names[idx]
            art_vals[name] = vars_values.get(name, 0)

        return {
            "status": self.status,
            "objective_value": z_val,
            "variable_values": clean_vars,
            "artificial_variables": art_vals if art_vals else None,
            "iterations": self.iterations
        }

def solve_dual_problem(data):
    # Construct Dual Problem
    # Primal: Max cx s.t. Ax <= b
    # Dual: Min bT y s.t. AT y >= c
    
    # This implementation assumes canonical form for simplicity or handles general conversion
    # Given the complexity of "Dual Simplex" vs "Solving the Dual",
    # solving the Dual problem via Simplex is a valid valid approach for "Dual" requirement in many courses.
    
    # 1. Parse Primal
    c = data["objective_coeffs"]
    A = []
    b = []
    signs = []
    for const in data["constraints"]:
        A.append(const["coeffs"])
        signs.append(const["sign"])
        b.append(const["rhs"])
    
    primal_obj = data["objective"]
    
    # Transposing A
    # A is (m x n). Dual A' is (n x m)
    m = len(A)
    n = len(A[0])
    
    A_dual = [[0.0] * m for _ in range(n)]
    for i in range(m):
        for j in range(n):
            A_dual[j][i] = A[i][j]
            
    # Dual RHS is Primal c
    b_dual = c
    
    # Dual Objective coeffs is Primal b
    c_dual = b
    
    # Determine Dual Signs and Objective
    # Standard Rules:
    # Max Z -> Min W
    # Constraints <=  -> Variables >= 0
    # Constraints >=  -> Variables <= 0
    # Constraints =   -> Variables Unrestricted
    # Variables >= 0  -> Dual Constraints >= (for Min)
    
    # Simplified assumption: Standard Linear Problem (All vars >= 0)
    # If Primal Max, Constraints <= -> Dual Min, Constraints >=
    
    dual_signs = []
    if primal_obj == 'max':
        dual_target = 'min'
        # Check primal constraint signs to determine dual var bounds (ignored here as Simplex assumes x>=0)
        # Check primal var bounds (assumed >=0) to determine Dual Signs
        # Primal Var xi >= 0 -> Dual Constraint i >= (for Min problem)
        
        # Let's stick to simple matrix transposition for standard form
        dual_signs = ['>='] * n
    else:
        dual_target = 'max'
        dual_signs = ['<='] * n
        
    # Solve Dual
    solver = SimplexSolver(c_dual, A_dual, b_dual, dual_signs, objective=dual_target, method='simplex')
    result = solver.solve()
    return result

