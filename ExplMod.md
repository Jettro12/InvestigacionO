# Explicación de Modelos Matemáticos Implementados

Este documento detalla la formulación matemática y la lógica algorítmica de los métodos implementados "desde cero" en el sistema `InvestigacionO`, sin el uso de librerías externas de optimización como `SciPy` o `PuLP`.

---

## 1. Programación Lineal: Método Simplex Modificado

### 1.1. Algoritmo Simplex Estándar
Se implementa el método tabular clásico.
*   **Problema:** Maximizar $Z = c^T x$ sujeto a $Ax \leq b, x \geq 0$.
*   **Estrategia:** Se introducen variables de holgura ($s_i$) para convertir las desigualdades en igualdades.
*   **Criterio de Entrada (Pivote):** Se selecciona la columna con el coeficiente más negativo en la fila de la función objetivo ($Z_j - C_j$).
*   **Criterio de Salida:** Regla del cociente mínimo ($\min \{b_i / a_{ij} \mid a_{ij} > 0\}$) para asegurar factibilidad.
*   **Operación Pivote:** Transformaciones elementales de fila (Gauss-Jordan) para hacer unitario el vector de la variable de entrada y anular el resto de la columna.

### 1.2. Método de la Gran M (Penalización)
Para restricciones $\geq$ o $=$, no tenemos una base inicial factible evidente.
*   **Técnica:** Se agregan variables artificiales ($a_i$) en las restricciones que no tienen holgura positiva.
*   **Función Objetivo Modificada:** Se penalizan las variables artificiales en la función objetivo con un valor muy grande $M$.
    *   Maximizando: Coeficiente $-M$.
*   **Lógica:** Si el algoritmo termina con alguna variable artificial en la base con valor positivo, el problema es infactible.

### 1.3. Método de las Dos Fases
Alternativa numérica más estable que la Gran M.
*   **Fase 1:** Se minimiza la suma de las variables artificiales ($W = \sum a_i$).
    *   Si $\min W > 0$, el problema original es infactible.
    *   Si $\min W = 0$, hemos encontrado una Solución Básica Factible (SBF) inicial para el problema original.
*   **Fase 2:** Se retoma la función objetivo original ($Z$), eliminando las columnas artificiales, y se continúa iterando con el Simplex estándar desde la base encontrada.

### 1.4. Dualidad
El sistema construye el problema dual automáticamente:
*   Para un primal de Maximización con restricciones $\leq$, el Dual es de Minimización con variables $\geq 0$.
*   La matriz $A$ se transpone ($A^T$).
*   El vector de costos $c$ se convierte en el RHS ($b$) del dual y viceversa.

---

## 2. Modelos de Transporte

El objetivo es minimizar el costo total de envío desde $m$ orígenes a $n$ destinos.

### 2.1. Solución Inicial Factible
Se implementaron tres heurísticas para encontrar el punto de partida:
1.  **Esquina Noroeste:** Asignación secuencial desde la celda $(0,0)$ llenando demanda y oferta sin considerar costos. Rápida pero subóptima.
2.  **Costo Mínimo:** Se priorizan las celdas con el menor costo unitario global ($c_{ij}$) hasta agotar oferta/demanda.
3.  **Aproximación de Vogel (VAM):**
    *   Calcula penalizaciones para cada fila y columna (diferencia entre los dos costos más bajos).
    *   Asigna en la fila/columna con mayor penalización, escogiendo la celda de menor costo.
    *   Produce soluciones iniciales muy cercanas al óptimo.

### 2.2. Optimización (Prueba de Optimalidad)
Implementación del método **MODI (Modified Distribution Method)**:
*   Se asocia un multiplicador $u_i$ a cada fila y $v_j$ a cada columna tal que $u_i + v_j = c_{ij}$ para variables básicas.
*   Se calculan los costos reducidos para las variables no básicas: $z_{ij} - c_{ij} = u_i + v_j - c_{ij}$.
*   Si algún costo reducido es positivo (para minimización), se puede mejorar la solución introduciendo esa ruta.
*   Se ajusta la asignación mediante un circuito cerrado (loop) alternando $+ \theta$ y $- \theta$.

---

## 3. Optimización de Redes y Grafos

Los algoritmos se basan en teoría de grafos, modelando nodos y aristas con pesos.

### 3.1. Ruta Más Corta (Dijkstra)
*   **Propósito:** Encontrar el camino de menor costo desde un nodo origen a todos los demás (o uno específico).
*   **Algoritmo:** Greedy. Mantiene un conjunto de distancias tentativas. En cada paso, selecciona el nodo no visitado con menor distancia acumulada, lo marca como visitado y relaja (actualiza) las distancias de sus vecinos.
*   **Estructura de Datos:** Se utiliza una cola de prioridad (Priority Queue / Heap) para eficiencia $O(E \log V)$.

### 3.2. Árbol de Expansión Mínima (Kruskal)
*   **Propósito:** Conectar todos los nodos del grafo con el menor costo total posible, sin formar ciclos.
*   **Algoritmo:**
    1.  Ordenar todas las aristas por peso ascendente.
    2.  Iterar aristas y añadir al árbol si los nodos extremos no están ya conectados (usando estructura Disjoint Set Union / Union-Find).
    3.  Detenerse cuando se tengan $V-1$ aristas.

### 3.3. Flujo Máximo (Edmonds-Karp)
*   **Propósito:** Encontrar la cantidad máxima de flujo que puede pasar de una Fuente a un Sumidero.
*   **Algoritmo:** Implementación del método Ford-Fulkerson usando BFS (Breadth-First Search) para encontrar caminos de aumento.
    *   Mientras exista un camino con capacidad residual disponible en el grafo residual, se envía el flujo máximo posible por ese camino.
    *   Se actualizan las capacidades residuales (restando flujo en dirección directa, sumando en reversa).

### 3.4. Flujo de Costo Mínimo
*   **Propósito:** Enviar una cantidad fija de flujo con el menor costo.
*   **Algoritmo:** Successive Shortest Path (Camino más corto sucesivo).
    *   Mientras falte flujo por enviar, se busca el camino más corto (usando costos como distancias) en el grafo residual.
    *   Se utiliza una variación de Bellman-Ford o Potenciales para manejar costos negativos que pueden surgir en el grafo residual.
