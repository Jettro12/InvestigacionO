import matplotlib.pyplot as plt
import io
import base64
import heapq
import matplotlib
import networkx as nx

# Configurar Matplotlib para entornos sin interfaz gráfica
matplotlib.use('Agg')

# ==========================================
# 1. MOTOR DE RENDERIZADO (SOLO DIBUJO)
# ==========================================
def generate_graph_image(graph_data, paths=None, title="Grafo", edge_labels=None, edge_color='gray', highlight_color='red'):
    """
    Usa NetworkX solo para posicionar nodos y dibujar.
    La lógica de qué nodos y qué pesos mostrar viene del cálculo manual.
    """
    try:
        plt.figure(figsize=(7, 5))
        G = nx.DiGraph()
        
        for edge in graph_data:
            u, v = edge[0], edge[1]
            w = edge[2] if len(edge) > 2 else 0
            G.add_edge(u, v, weight=w)

        # Posicionamiento consistente de los nodos
        pos = nx.spring_layout(G, seed=42) 
        
        if edge_labels is None:
            edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}

        # Dibujar base del grafo
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                edge_color=edge_color, node_size=2000, font_size=10, 
                arrowsize=20, width=1.5)
        
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

        # Resaltar camino (para Dijkstra o flujo)
        if paths and len(paths) > 1:
            edges_path = [(paths[i], paths[i + 1]) for i in range(len(paths) - 1)]
            nx.draw_networkx_edges(G, pos, edgelist=edges_path, edge_color=highlight_color, width=3)

        plt.title(title, fontweight='bold')
        plt.axis('off')

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        return image_base64
    except Exception as e:
        print(f"Error en renderizado: {e}")
        return ""

# ==========================================
# 2. LÓGICA DESDE CERO (SIN LIBRERÍAS DE GRAFOS)
# ==========================================

def dijkstra_algorithm(graph, start_node):
    nodes = set()
    adj_list = {}
    for u, v, weight, capacity in graph:
        nodes.add(u); nodes.add(v)
        if u not in adj_list: adj_list[u] = []
        adj_list[u].append((v, weight))
    
    for node in nodes:
        if node not in adj_list: adj_list[node] = []

    distances = {node: float('inf') for node in nodes}
    distances[start_node] = 0
    previous = {node: None for node in nodes}
    pq = [(0, start_node)]
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        if current_dist > distances[current_node]: continue
        
        for neighbor, weight in adj_list[current_node]:
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    end_node = max(distances.keys(), key=lambda x: distances[x] if distances[x] != float('inf') else -1)
    
    path = []
    curr = end_node
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()
    
    img = generate_graph_image(graph, path, "Ruta Más Corta (Dijkstra)")
    
    return {
        "total_weight": float(distances[end_node]),
        "node_order": path,
        "graph_image": img
    }

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
    def find(self, x):
        if self.parent[x] != x: self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        rootX, rootY = self.find(x), self.find(y)
        if rootX != rootY:
            self.parent[rootX] = rootY
            return True
        return False

def minimum_spanning_tree(graph):
    nodes = sorted(list(set([edge[0] for edge in graph] + [edge[1] for edge in graph])))
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    
    edges = sorted([(edge[2], edge[0], edge[1]) for edge in graph])
    uf = UnionFind(len(nodes))
    mst_edges = []
    total_weight = 0
    
    for weight, u, v in edges:
        if uf.union(node_to_idx[u], node_to_idx[v]):
            mst_edges.append((u, v, weight))
            total_weight += weight
            
    img = generate_graph_image(mst_edges, title="Árbol de Expansión Mínima (Kruskal)", edge_color='green')
    
    return {
        "edges": mst_edges,
        "total_weight": float(total_weight),
        "graph_image": img
    }

def ford_fulkerson_algorithm(graph, source=None, sink=None):
    adj = {}
    caps = {}
    original_graph = []
    all_nodes = set()

    # 1. Mapeo de la red y detección automática de Source/Sink
    for u, v, w, cap in graph:
        all_nodes.update([u, v])
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
        # Manejamos el caso de aristas duplicadas sumando capacidades
        caps[(u, v)] = caps.get((u, v), 0) + cap
        caps.setdefault((v, u), 0) 
        original_graph.append((u, v, w, cap))

    # 2. Lógica de detección automática si no se pasan por parámetro
    if source is None or sink is None:
        # Fuente: Nodo que solo tiene salidas (o la primera letra del alfabeto)
        # Sumidero: Nodo que solo tiene entradas (o la última letra del alfabeto)
        sorted_nodes = sorted(list(all_nodes))
        source = sorted_nodes[0]
        sink = sorted_nodes[-1]

    def bfs():
        parent = {source: None}
        queue = [source]
        while queue:
            u = queue.pop(0)
            for v in adj.get(u, []):
                # IMPORTANTE: Verificamos capacidad residual real
                if v not in parent and caps.get((u, v), 0) > 0:
                    parent[v] = u
                    queue.append(v)
                    if v == sink: return parent
        return None

    max_flow = 0
    # 3. Bucle principal de Ford-Fulkerson (Edmonds-Karp)
    while True:
        parent = bfs()
        if not parent: break
        
        # Hallar la capacidad residual mínima en el camino encontrado
        path_flow = float('inf')
        s = sink
        while s != source:
            path_flow = min(path_flow, caps[(parent[s], s)])
            s = parent[s]
            
        max_flow += path_flow
        # Actualizar capacidades residuales
        v = sink
        while v != source:
            u = parent[v]
            caps[(u, v)] -= path_flow
            caps[(v, u)] += path_flow
            v = parent[v]

    # Generar etiquetas para el gráfico: "Enviado / Capacidad"
    flow_labels = {}
    for u, v, w, cap_orig in original_graph:
        # El flujo enviado es la capacidad inicial menos lo que quedó libre
        enviado = cap_orig - caps.get((u, v), 0)
        # Aseguramos que no muestre valores negativos por aristas inversas
        enviado = max(0, enviado)
        flow_labels[(u, v)] = f"{int(enviado)} / {int(cap_orig)}"

    img = generate_graph_image(original_graph, title=f"Max Flow: {max_flow} ({source} a {sink})", edge_labels=flow_labels)

    return {
        "max_flow": float(max_flow),
        "graph_image": img,
        "source": source,
        "sink": sink
    }

    # Generar etiquetas dinámicas: "Flujo / Capacidad"
    flow_labels = {}
    for u, v, w, cap_orig in original_graph:
        enviado = cap_orig - caps[(u, v)]
        flow_labels[(u, v)] = f"{int(enviado)} / {int(cap_orig)}"

    img = generate_graph_image(original_graph, title="Flujo Máximo (Enviado / Capacidad)", edge_labels=flow_labels)

    return {
        "max_flow": float(max_flow),
        "graph_image": img
    }
def sensitivity_analysis_shortest_path(graph, start_node, end_node):
    """
    Análisis de sensibilidad: calcula el impacto de eliminar cada arista 
    en la ruta más corta original.
    """
    # 1. Calcular la distancia base
    base_result = dijkstra_algorithm(graph, start_node)
    base_length = base_result["total_weight"]
    
    # Si de entrada no hay ruta, no hay mucho que analizar
    if base_length == float('inf'):
        return {"error": "No existe una ruta inicial entre los nodos seleccionados"}

    sensitivities = {}
    
    # 2. Probar eliminando una arista a la vez
    for i, edge in enumerate(graph):
        u_rem, v_rem = edge[0], edge[1]
        
        # Crear un grafo temporal sin la arista actual
        temp_graph = [e for j, e in enumerate(graph) if i != j]
        
        try:
            temp_result = dijkstra_algorithm(temp_graph, start_node)
            new_length = temp_result["total_weight"]
            
            if new_length == float('inf'):
                impact = "Ruta se vuelve imposible"
            else:
                impact = new_length - base_length
                
            sensitivities[f"{u_rem} -> {v_rem}"] = impact
        except Exception as e:
            sensitivities[f"{u_rem} -> {v_rem}"] = f"Error: {str(e)}"
            
    return sensitivities
# ==========================================
# 3. PUNTO DE ENTRADA PRINCIPAL
# ==========================================
def solve_all_problems(graph):
    if not graph:
        return {"error": "Grafo vacío"}
    
    # 1. IDENTIFICACIÓN ESTÁTICA DE NODOS (Agnóstica al orden)
    all_nodes = set()
    for u, v, w, cap in graph:
        all_nodes.update([u, v])
    
    # Ordenamos alfabéticamente para que el 'mínimo' siempre sea el inicio 
    # y el 'máximo' el final, sin importar el orden del array.
    sorted_nodes = sorted(list(all_nodes))
    source = sorted_nodes[0]
    sink = sorted_nodes[-1]

    # 2. EJECUCIÓN DE ALGORITMOS PASANDO LOS NODOS EXPLÍCITOS
    # Pasamos 'source' a Dijkstra para que siempre empiece en el mismo lugar
    res_dijkstra = dijkstra_algorithm(graph, source)
    
    # MST no depende de source/sink, así que este suele estar bien
    res_mst = minimum_spanning_tree(graph)
    
    # Pasamos source y sink explícitos a Ford-Fulkerson
    res_max_flow = ford_fulkerson_algorithm(graph, source, sink)
    
    # Ejecutamos análisis de sensibilidad con los mismos nodos consistentes
    sensibilidad = sensitivity_analysis_shortest_path(graph, source, sink)

    # 3. CONSTRUCCIÓN DE RESULTADOS
    results = {
        "shortest_path": res_dijkstra,
        "mst": res_mst,
        "max_flow": res_max_flow,
        "sensitivity": sensibilidad,
        "graph_image_base64": res_dijkstra["graph_image"]
    }
    
    print(f"✅ Cálculos consistentes completados: {source} -> {sink}")
    return results