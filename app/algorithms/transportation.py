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
    total = 0.0
    rows = len(asignacion)
    cols = len(asignacion[0]) if rows > 0 else 0
    for i in range(rows):
        for j in range(cols):
            total += float(asignacion[i][j]) * float(costos[i][j])
    return total

# 2. MODI mejorado - Implementación desde cero sin librerías de optimización

def modi_method(asignacion_inicial, costos, max_iter=100):
    """
    Método MODI (Modified Distribution Method) para optimizar un problema de transporte.
    Implementado completamente desde cero sin usar librerías de optimización.
    
    Parámetros:
    - asignacion_inicial: Matriz de asignación inicial (de Northwest, Vogel, o Costo Mínimo)
    - costos: Matriz de costos unitarios
    - max_iter: Número máximo de iteraciones
    
    Retorna:
    - (asignacion_optima, costo_total)
    """
    # Convertir a listas para trabajar sin numpy en la lógica
    if hasattr(asignacion_inicial, 'tolist'):
        asignacion = [row[:] for row in asignacion_inicial.tolist()]
    else:
        asignacion = [row[:] for row in asignacion_inicial]
    
    if hasattr(costos, 'tolist'):
        costos_lista = [row[:] for row in costos.tolist()]
    else:
        costos_lista = [row[:] for row in costos]
    
    m = len(asignacion)  # número de orígenes
    n = len(asignacion[0]) if m > 0 else 0  # número de destinos
    
    print(f"📊 MODI: Iniciando optimización. Matriz {m}x{n}")
    
    for iteracion in range(max_iter):
        print(f"\n🔄 Iteración MODI #{iteracion + 1}")
        
        # Paso 1: Obtener las celdas básicas (con asignación > 0)
        celdas_basicas = []
        for i in range(m):
            for j in range(n):
                if asignacion[i][j] > 1e-9:
                    celdas_basicas.append((i, j))
        
        print(f"   Celdas básicas: {celdas_basicas}")
        
        # Verificar degeneración: necesitamos m + n - 1 celdas básicas
        num_basicas_requeridas = m + n - 1
        if len(celdas_basicas) < num_basicas_requeridas:
            print(f"   ⚠️ Solución degenerada: {len(celdas_basicas)} < {num_basicas_requeridas}")
            # Agregar épsilon a celdas no básicas para resolver degeneración
            epsilon = 1e-9
            for i in range(m):
                for j in range(n):
                    if len(celdas_basicas) >= num_basicas_requeridas:
                        break
                    if asignacion[i][j] <= 1e-9:
                        asignacion[i][j] = epsilon
                        celdas_basicas.append((i, j))
                if len(celdas_basicas) >= num_basicas_requeridas:
                    break
        
        # Paso 2: Calcular los multiplicadores U y V
        U = [None] * m
        V = [None] * n
        U[0] = 0  # Fijar U[0] = 0 arbitrariamente
        
        # Resolver el sistema U[i] + V[j] = C[i][j] para celdas básicas
        cambio = True
        max_intentos = m * n + 10
        intentos = 0
        while cambio and intentos < max_intentos:
            cambio = False
            intentos += 1
            for (i, j) in celdas_basicas:
                costo = costos_lista[i][j]
                if U[i] is not None and V[j] is None:
                    V[j] = costo - U[i]
                    cambio = True
                elif V[j] is not None and U[i] is None:
                    U[i] = costo - V[j]
                    cambio = True
        
        # Rellenar valores None con 0 si quedaron
        U = [0 if u is None else u for u in U]
        V = [0 if v is None else v for v in V]
        
        print(f"   U = {U}")
        print(f"   V = {V}")
        
        # Paso 3: Calcular costos reducidos para celdas no básicas
        # Costo reducido = C[i][j] - U[i] - V[j]
        celda_entrante = None
        min_costo_reducido = 0
        
        for i in range(m):
            for j in range(n):
                if asignacion[i][j] <= 1e-9:  # Celda no básica
                    costo_reducido = costos_lista[i][j] - U[i] - V[j]
                    if costo_reducido < min_costo_reducido - 1e-9:
                        min_costo_reducido = costo_reducido
                        celda_entrante = (i, j)
        
        # Si no hay costos reducidos negativos, la solución es óptima
        if celda_entrante is None:
            print(f"   ✅ Solución óptima encontrada en iteración {iteracion + 1}")
            break
        
        print(f"   Celda entrante: {celda_entrante} con costo reducido {min_costo_reducido:.4f}")
        
        # Paso 4: Encontrar el ciclo cerrado (stepping stone path)
        ciclo = encontrar_ciclo_modi(asignacion, celda_entrante, m, n)
        
        if ciclo is None or len(ciclo) < 4:
            print(f"   ❌ No se encontró ciclo válido para la celda {celda_entrante}")
            break
        
        print(f"   Ciclo encontrado: {ciclo}")
        
        # Paso 5: Determinar theta (cantidad a transferir)
        # theta = mínimo de las asignaciones en posiciones impares del ciclo (las que se restan)
        theta = float('inf')
        for idx in range(1, len(ciclo), 2):  # Posiciones impares (1, 3, 5, ...)
            i, j = ciclo[idx]
            if asignacion[i][j] < theta:
                theta = asignacion[i][j]
        
        if theta <= 0 or theta == float('inf'):
            print(f"   ❌ Theta inválido: {theta}")
            break
        
        print(f"   Theta (cantidad a transferir): {theta}")
        
        # Paso 6: Actualizar la asignación
        for idx, (i, j) in enumerate(ciclo):
            if idx % 2 == 0:  # Posiciones pares: sumar
                asignacion[i][j] += theta
            else:  # Posiciones impares: restar
                asignacion[i][j] -= theta
                if asignacion[i][j] < 1e-9:
                    asignacion[i][j] = 0
        
        costo_actual = calcular_costo_total(asignacion, costos_lista)
        print(f"   Costo después de actualización: {costo_actual}")
    
    # Limpiar valores muy pequeños
    for i in range(m):
        for j in range(n):
            if asignacion[i][j] < 1e-7:
                asignacion[i][j] = 0
    
    costo_final = calcular_costo_total(asignacion, costos_lista)
    print(f"\n🎯 MODI completado. Costo final: {costo_final}")
    
    return asignacion, costo_final


def encontrar_ciclo_modi(asignacion, celda_entrante, m, n):
    """
    Encuentra un ciclo cerrado para el método MODI usando BFS.
    El ciclo alterna entre movimientos horizontales y verticales,
    pasando solo por celdas básicas (excepto la celda entrante).
    
    Retorna una lista de tuplas (i, j) que forman el ciclo, o None si no existe.
    """
    start_i, start_j = celda_entrante
    
    # Obtener celdas básicas
    celdas_basicas = set()
    for i in range(m):
        for j in range(n):
            if asignacion[i][j] > 1e-9:
                celdas_basicas.add((i, j))
    
    # Agregar la celda entrante temporalmente
    celdas_basicas.add(celda_entrante)
    
    # BFS para encontrar el ciclo
    # Estado: (fila, columna, es_movimiento_horizontal, camino)
    from collections import deque
    
    # Intentar empezando con movimiento horizontal
    for direccion_inicial in [True, False]:  # True = horizontal, False = vertical
        cola = deque()
        cola.append((start_i, start_j, direccion_inicial, [(start_i, start_j)]))
        
        while cola:
            ci, cj, es_horizontal, camino = cola.popleft()
            
            if es_horizontal:
                # Buscar en la misma fila
                for nj in range(n):
                    if nj != cj and (ci, nj) in celdas_basicas:
                        if (ci, nj) == celda_entrante and len(camino) >= 3:
                            # Encontramos el ciclo!
                            return camino
                        if (ci, nj) not in camino:
                            nuevo_camino = camino + [(ci, nj)]
                            if len(nuevo_camino) <= m + n:  # Límite de longitud
                                cola.append((ci, nj, False, nuevo_camino))
            else:
                # Buscar en la misma columna
                for ni in range(m):
                    if ni != ci and (ni, cj) in celdas_basicas:
                        if (ni, cj) == celda_entrante and len(camino) >= 3:
                            # Encontramos el ciclo!
                            return camino
                        if (ni, cj) not in camino:
                            nuevo_camino = camino + [(ni, cj)]
                            if len(nuevo_camino) <= m + n:  # Límite de longitud
                                cola.append((ni, cj, True, nuevo_camino))
    
    return None


# 3. update_allocation (mantenido por compatibilidad, pero ya no se usa directamente)

def update_allocation(asignacion, ciclo):
    """Actualiza la asignación según el ciclo MODI, robusto a errores y negativos."""
    if ciclo is None or len(ciclo) < 4:
        return asignacion
    
    # Encontrar theta
    theta = float('inf')
    for idx in range(1, len(ciclo), 2):
        i, j = ciclo[idx]
        val = asignacion[i][j] if hasattr(asignacion, '__getitem__') else asignacion[i, j]
        if val < theta:
            theta = val
    
    if theta <= 0:
        return asignacion
    
    # Actualizar
    for idx, (i, j) in enumerate(ciclo):
        if idx % 2 == 0:
            if hasattr(asignacion, '__getitem__') and hasattr(asignacion[i], '__setitem__'):
                asignacion[i][j] += theta
            else:
                asignacion[i, j] += theta
        else:
            if hasattr(asignacion, '__getitem__') and hasattr(asignacion[i], '__setitem__'):
                asignacion[i][j] -= theta
                if asignacion[i][j] < 0:
                    asignacion[i][j] = 0
            else:
                asignacion[i, j] -= theta
                if asignacion[i, j] < 0:
                    asignacion[i, j] = 0
    
    return asignacion


# 4. find_loop (mantenido por compatibilidad)

def find_loop(asignacion, celda_entrada):
    """Busca un ciclo alternante válido para MODI. Usa la nueva implementación."""
    if hasattr(asignacion, 'shape'):
        m, n = asignacion.shape
    else:
        m = len(asignacion)
        n = len(asignacion[0]) if m > 0 else 0
    
    # Convertir a lista si es necesario
    if hasattr(asignacion, 'tolist'):
        asig_lista = asignacion.tolist()
    else:
        asig_lista = asignacion
    
    return encontrar_ciclo_modi(asig_lista, celda_entrada, m, n)

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