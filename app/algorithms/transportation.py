import numpy as np

def balance_transportation_problem(supply, demand, costs):
    """
    Verifica si el problema de transporte está balanceado. Si no lo está,
    agrega una fila o columna ficticia con costo cero.
    """
    total_supply = sum(supply)
    total_demand = sum(demand)

    print(f"📌 Total Supply: {total_supply}, Total Demand: {total_demand}")  # 🔍 Agregar log

    if None in supply or None in demand or None in costs:
        raise ValueError("❌ Se encontraron valores None en supply, demand o costs.")

    if total_supply > total_demand:
        # 🔹 Agregar columna ficticia con demanda extra
        demand.append(total_supply - total_demand)
        costs = np.hstack((costs, np.zeros((costs.shape[0], 1))))  # ✅ Usar np.hstack en vez de append

    elif total_demand > total_supply:
        # 🔹 Agregar fila ficticia con oferta extra
        supply.append(total_demand - total_supply)
        costs = np.vstack((costs, np.zeros((1, costs.shape[1]))))  # ✅ Usar np.vstack en vez de append

    return supply, demand, costs

def northwest_corner_method(supply, demand):
    """
    Método de Esquina Noroeste para encontrar una solución inicial.
    """
    supply = supply.copy()
    demand = demand.copy()
    allocation = np.zeros((len(supply), len(demand)), dtype=float)  # ✅ Convertir a float

    i, j = 0, 0
    while i < len(supply) and j < len(demand):
        min_val = min(supply[i], demand[j])
        allocation[i, j] = min_val  # ✅ Asegurar que no queden valores None
        supply[i] -= min_val
        demand[j] -= min_val

        if supply[i] == 0:
            i += 1
        if demand[j] == 0:
            j += 1

    print("✅ Solución Inicial (Esquina Noroeste):\n", allocation)
    return allocation

def minimum_cost_method(supply, demand, costs):
    """
    Método de Costo Mínimo para encontrar una solución inicial.
    """
    supply = supply.copy()
    demand = demand.copy()
    costs = np.array(costs, dtype=float)  # ✅ Convertir costos a float
    allocation = np.zeros((len(supply), len(demand)), dtype=float)  # ✅ Convertir a float

    # Obtener lista de todas las celdas ordenadas por costo mínimo
    cost_indices = [(i, j) for i in range(len(supply)) for j in range(len(demand))]
    cost_indices.sort(key=lambda x: costs[x[0], x[1]])  # Ordenar por costo mínimo

    for i, j in cost_indices:
        if supply[i] > 0 and demand[j] > 0:
            min_val = min(supply[i], demand[j])
            allocation[i, j] = min_val  # ✅ Asegurar que no queden valores None
            supply[i] -= min_val
            demand[j] -= min_val

    print("✅ Solución Inicial (Costo Mínimo):\n", allocation)
    return allocation

def vogel_approximation_method(supply, demand, costs):
    """
    Método de Aproximación de Vogel para encontrar una solución inicial.
    """
    supply = supply.copy()
    demand = demand.copy()
    costs = np.array(costs, dtype=float)  # ✅ Convertir a float para evitar errores con np.inf
    allocation = np.zeros((len(supply), len(demand)))

    while np.any(supply) and np.any(demand):
        penalties = []

        # Calcular penalizaciones por fila y columna
        for i, row in enumerate(costs):
            if supply[i] > 0:
                sorted_row = sorted(row)
                penalties.append((sorted_row[1] - sorted_row[0], 'row', i))

        for j, col in enumerate(costs.T):
            if demand[j] > 0:
                sorted_col = sorted(col)
                penalties.append((sorted_col[1] - sorted_col[0], 'col', j))

        # Seleccionar la fila o columna con la mayor penalización
        max_penalty = max(penalties, key=lambda x: x[0])

        if max_penalty[1] == 'row':
            i = max_penalty[2]
            j = np.argmin(costs[i])
        else:
            j = max_penalty[2]
            i = np.argmin(costs[:, j])

        # Asignar la cantidad máxima posible
        min_val = min(supply[i], demand[j])
        allocation[i][j] = min_val
        supply[i] -= min_val
        demand[j] -= min_val

        # ✅ Asegurarse de que costs[i, j] sea float antes de asignar np.inf
        costs[i, j] = float('inf')  # ✅ Convertir explícitamente a float

    return allocation

# 1. Función para calcular el costo total de una asignación

def calcular_costo_total(asignacion, costos):
    """Calcula el costo total de una asignación dada una matriz de costos."""
    import numpy as np
    asignacion = np.array(asignacion)
    costos = np.array(costos)
    return float(np.sum(asignacion * costos))

# 2. MODI mejorado

def modi_method(asignacion_inicial, costos, max_iter=100):
    """
    Método MODI robusto: optimiza la asignación inicial y retorna (asignación_final, costo_total).
    Solo actualiza si la solución mejora o es igual. Elimina asignaciones degeneradas (<1e-7).
    """
    import numpy as np
    asignacion = np.array(asignacion_inicial, dtype=float)
    costos = np.array(costos, dtype=float)
    m, n = asignacion.shape
    iteraciones = 0

    def limpiar_degeneradas(asig):
        asig[asig < 1e-7] = 0
        return asig

    # Costo inicial
    asignacion = limpiar_degeneradas(asignacion)
    costo_inicial = calcular_costo_total(asignacion, costos)
    mejor_asignacion = asignacion.copy()
    mejor_costo = costo_inicial

    while iteraciones < max_iter:
        iteraciones += 1
        U, V = calculate_potentials(asignacion, costos)
        reduced_costs = calculate_reduced_costs(U, V, costos)
        entering_cell = find_entering_cell(reduced_costs, asignacion)
        if entering_cell is None:
            break
        ciclo = find_loop(asignacion, entering_cell)
        if ciclo is None or len(ciclo) < 4:
            # No se encontró ciclo válido, termina
            break
        nueva_asignacion = update_allocation(asignacion.copy(), ciclo)
        nueva_asignacion = limpiar_degeneradas(nueva_asignacion)
        nuevo_costo = calcular_costo_total(nueva_asignacion, costos)
        # Solo actualiza si mejora o iguala el costo
        if nuevo_costo <= mejor_costo:
            asignacion = nueva_asignacion
            mejor_asignacion = nueva_asignacion.copy()
            mejor_costo = nuevo_costo
        else:
            break
    mejor_asignacion = limpiar_degeneradas(mejor_asignacion)
    return mejor_asignacion.tolist(), mejor_costo

# 3. update_allocation robusto

def update_allocation(asignacion, ciclo):
    """Actualiza la asignación según el ciclo MODI, robusto a errores y negativos."""
    import numpy as np
    if ciclo is None or len(ciclo) < 4:
        return asignacion
    valores = [asignacion[i, j] for idx, (i, j) in enumerate(ciclo[1::2]) if asignacion[i, j] > 0]
    if not valores:
        return asignacion
    theta = min(valores)
    if theta <= 0 or np.isnan(theta):
        return asignacion
    for idx, (i, j) in enumerate(ciclo):
        if idx % 2 == 0:
            asignacion[i, j] += theta
        else:
            asignacion[i, j] -= theta
            if asignacion[i, j] < 0:
                asignacion[i, j] = 0
    return asignacion

# 4. find_loop robusto

def find_loop(asignacion, celda_entrada):
    """Busca un ciclo alternante válido para MODI. Retorna None si no existe."""
    import numpy as np
    rows, cols = asignacion.shape
    start = celda_entrada
    def backtrack(pos, path, visited, is_row):
        i, j = pos
        if len(path) > 3 and pos == start:
            return path
        if is_row:
            for nj in range(cols):
                if nj != j and (asignacion[i, nj] > 0 or (i, nj) == start):
                    next_pos = (i, nj)
                    if next_pos not in visited or (next_pos == start and len(path) > 3):
                        res = backtrack(next_pos, path + [next_pos], visited | {next_pos}, not is_row)
                        if res:
                            return res
        else:
            for ni in range(rows):
                if ni != i and (asignacion[ni, j] > 0 or (ni, j) == start):
                    next_pos = (ni, j)
                    if next_pos not in visited or (next_pos == start and len(path) > 3):
                        res = backtrack(next_pos, path + [next_pos], visited | {next_pos}, not is_row)
                        if res:
                            return res
        return None
    ciclo = backtrack(start, [start], {start}, True)
    if not ciclo:
        ciclo = backtrack(start, [start], {start}, False)
    if not ciclo or len(ciclo) < 4:
        return None
    return ciclo

def calculate_potentials(allocation, costs):
    """
    Calcula los potenciales U y V para el método MODI.
    """
    rows, cols = allocation.shape
    U = [None] * rows
    V = [None] * cols

    # 🔹 Inicializamos el primer potencial arbitrariamente en 0
    U[0] = 0  

    assigned_cells = [(i, j) for i in range(rows) for j in range(cols) if allocation[i][j] > 0]

    updated = True
    while updated:
        updated = False
        for i, j in assigned_cells:
            if U[i] is not None and V[j] is None:
                V[j] = costs[i][j] - U[i]
                updated = True
            elif V[j] is not None and U[i] is None:
                U[i] = costs[i][j] - V[j]
                updated = True

    # ✅ Asignar 0 a cualquier valor None restante
    U = [0 if u is None else u for u in U]
    V = [0 if v is None else v for v in V]

    print(f"✅ Potenciales corregidos: U = {U}, V = {V}")
    return U, V

def calculate_reduced_costs(U, V, costs):
    """
    Calcula los costos reducidos Z[i][j] = C[i][j] - (U[i] + V[j]).
    """
    rows, cols = costs.shape
    reduced_costs = np.zeros((rows, cols))

    for i in range(rows):
        for j in range(cols):
            if U[i] is not None and V[j] is not None:
                reduced_costs[i][j] = costs[i][j] - (U[i] + V[j])
            else:
                reduced_costs[i][j] = float('inf')  # ✅ Evita errores si hay valores None

    return reduced_costs

def find_entering_cell(reduced_costs, allocation):
    """
    Encuentra la celda con el menor costo reducido negativo que NO está asignada.
    """
    min_value = np.min(reduced_costs)
    if min_value >= 0:
        return None  # La solución ya es óptima

    candidates = []
    for i in range(reduced_costs.shape[0]):
        for j in range(reduced_costs.shape[1]):
            if reduced_costs[i, j] == min_value and allocation[i, j] == 0:
                candidates.append((i, j))
    if not candidates:
        print("❌ No se encontró celda entrante válida.")
        return None
    print(f"🔄 Celda(s) entrante(s) seleccionada(s): {candidates} con costo reducido {min_value}")
    return candidates[0]  # O puedes probar todas en orden si quieres robustez