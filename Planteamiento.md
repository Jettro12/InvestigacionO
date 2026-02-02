# Caso de Aplicabilidad: Optimización Logística Integral para "EcuaDistribuciones S.A."

## 1. Selección del Problema
**Empresa:** EcuaDistribuciones S.A., una empresa mediana dedicada a la distribución de productos de consumo masivo en Ecuador.

**Problema:** La empresa enfrenta altos costos operativos debido a rutas de distribución ineficientes, asignación subóptima de camiones desde sus bodegas a los puntos de venta, y falta de planificación en la producción de sus kits promocionales.

**Alcance:**
1.  **Programación Lineal (Producción):** Determinar la mezcla óptima de "kits promocionales" (Básico, Premium, Lujo) a armar para maximizar utilidades, sujeto a restricciones de inventario de productos base.
2.  **Transporte (Logística):** Asignar el envío de cajas desde 3 Bodegas principales (Quito, Guayaquil, Cuenca) hacia 4 Centros de Distribución Regionales (Norte, Sur, Costa, Sierra) minimizando costos.
3.  **Redes (Última Milla):** Determinar la ruta más corta para el camión de reparto en la ciudad de Quito (desde Centro Norte a 6 puntos de venta clave) para ahorrar combustible.

---

## 2. Formulación Matemática del Modelo

### A. Modelo de Producción (Programación Lineal - Método Simplex/Dos Fases)
**Variables de Decisión:**
*   $x_1$: Cantidad de Kits Básicos a producir.
*   $x_2$: Cantidad de Kits Premium a producir.

**Función Objetivo (Maximizar Utilidad):**
$$ Max \ Z = 15x_1 + 25x_2 $$

**Restricciones:**
1.  **Disponibilidad de Producto A:** Cada Kit Básico usa 2 unidades, Premium usa 3. Total disponible: 120.
    $$ 2x_1 + 3x_2 \leq 120 $$
2.  **Disponibilidad de Producto B:** Cada Kit Básico usa 1 unidad, Premium usa 4. Total disponible: 100.
    $$ 1x_1 + 4x_2 \leq 100 $$
3.  **Compromiso de Venta:** Se deben producir al menos 10 Kits Premium.
    $$ x_2 \geq 10 $$
4.  **No negatividad:** $x_1, x_2 \geq 0$

**JSON para la Aplicación:**
```json
{
  "method": "two_phase",
  "objective": "max",
  "variables": ["x1", "x2"],
  "objective_coeffs": [15, 25],
  "constraints": [
    { "coeffs": [2, 3], "sign": "<=", "rhs": 120 },
    { "coeffs": [1, 4], "sign": "<=", "rhs": 100 },
    { "coeffs": [0, 1], "sign": ">=", "rhs": 10 }
  ]
}
```

---

### B. Modelo de Transporte (Logística de Bodegas)
**Objetivo:** Minimizar Costo de Envío.

**Costos Unitarios ($/caja):**
| Origen \ Destino | Norte | Sur | Costa | Sierra | Oferta |
|-------------------|-------|-----|-------|--------|--------|
| **Quito**         | 10    | 20  | 50    | 40     | **500**|
| **Guayaquil**     | 60    | 50  | 15    | 30     | **700**|
| **Cuenca**        | 40    | 30  | 40    | 10     | **300**|
| **Demanda**       | **400**| **400**| **400**| **300**|        |

**JSON para la Aplicación:**
```json
{
  "supply": [500, 700, 300],
  "demand": [400, 400, 400, 300],
  "costs": [
    [10, 20, 50, 40],
    [60, 50, 15, 30],
    [40, 30, 40, 10]
  ]
}
```

---

### C. Modelo de Redes (Ruta Más Corta - Última Milla)
**Objetivo:** Encontrar la ruta más rápida desde el Nodo 'A' (Bodega Central) hasta el Nodo 'G' (Cliente Final más lejano), pasando por intersecciones.

**Grafo (Nodos y Distancias en km):**
*   A -> B: 4, A -> C: 2
*   B -> C: 1, B -> D: 5
*   C -> D: 8, C -> E: 10
*   D -> E: 2, D -> G: 6
*   E -> G: 3

**JSON para la Aplicación:**
```json
{
    "graph": [
        ["A", "B", 4],
        ["A", "C", 2],
        ["B", "C", 1],
        ["B", "D", 5],
        ["C", "D", 8],
        ["C", "E", 10],
        ["D", "E", 2],
        ["D", "G", 6],
        ["E", "G", 3]
    ]
}
```

---

### D. Modelo de Árbol de Expansión Mínima (Infraestructura)
**Objetivo:** Conectar 6 servidores en las nuevas oficinas con cableado de fibra óptica, utilizando la menor cantidad de cable posible.

**Grafo (Nodos y Metros de Cable):**
* Servidores: S1, S2, S3, S4, S5, S6
* Conexiones posibles y distancias:
  - S1-S2: 4, S1-S3: 2
  - S2-S3: 5, S2-S4: 10
  - S3-S5: 3
  - S4-S6: 11
  - S5-S6: 8
  - S4-S5: 4

**JSON para la Aplicación (MST):**
```json
{
    "graph": [
      ["S1", "S2", 4], ["S1", "S3", 2],
      ["S2", "S3", 5], ["S2", "S4", 10],
      ["S3", "S5", 3],
      ["S4", "S6", 11], ["S4", "S5", 4],
      ["S5", "S6", 8]
    ]
}
```

---

### E. Modelo de Flujo Máximo (Capacidad Logística)
**Objetivo:** Determinar la capacidad máxima de envío de cajas por hora desde la Planta Central (P) hasta el Puerto de Exportación (E) a través de centros de tránsito.

**Red (Capacidades en cajas/hora):**
* P -> A: 10, P -> B: 10
* A -> C: 4, A -> D: 8, A -> B: 2
* B -> D: 9
* C -> E: 10
* D -> C: 6, D -> E: 10

**JSON para la Aplicación (Max Flow):**
```json
{
    "graph": [
      ["P", "A", 10], ["P", "B", 10],
      ["A", "C", 4], ["A", "D", 8], ["A", "B", 2],
      ["B", "D", 9],
      ["C", "E", 10],
      ["D", "C", 6], ["D", "E", 10]
    ],
    "source": "P",
    "sink": "E"
}
```

---

### F. Modelo de Flujo de Costo Mínimo
**Objetivo:** Enviar 50 unidades desde la Fuente (F) al Destino (T) minimizando costos, sujeto a capacidades y costos por ruta.

**Red [Origen, Destino, Costo, Capacidad]:**
1. F -> A: Costo 2, Cap 40
2. F -> B: Costo 4, Cap 40
3. A -> B: Costo 1, Cap 20
4. A -> T: Costo 5, Cap 30
5. B -> T: Costo 3, Cap 30

**JSON para la Aplicación:**
```json
{
    "graph": [
       ["F", "A", 2, 40],
       ["F", "B", 4, 40],
       ["A", "B", 1, 20],
       ["A", "T", 5, 30],
       ["B", "T", 3, 30]
    ],
    "source": "F",
    "sink": "T",
    "flow_amount": 50
}
```

---

## 3. Simulación e Impacto (Resultados Esperados del Software)

### Beneficios Estimados:
1.  **Producción:** La solución indicará la cantidad exacta a producir para no desperdiciar materia prima (slack = 0) y cumplir contratos.
    *   *Integración IA:* El análisis de sensibilidad podría recomendar "Aumentar el stock del Producto B en X unidades aumentaría la utilidad en Y dólares por unidad (Precio Sombra)".
2.  **Transporte:** Reducción estimada del 15% en costos comparado con la asignación manual.
    *   *Solución:* Priorizar envíos locales (Cuenca -> Sierra, GYE -> Costa).
3.  **Redes:** Identificación de la ruta crítica. Si la ruta A -> C -> ... se bloquea, el sistema recalcula instantáneamente.

Esta implementación integral demuestra el valor de la Ingeniería de Software aplicada a la Investigación Operativa, cumpliendo con la restricción de desarrollo propio de algoritmos.
