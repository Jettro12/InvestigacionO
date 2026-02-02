import matplotlib.pyplot as plt
import io
import base64
import heapq
import matplotlib

matplotlib.use('Agg')


def dijkstra_algorithm(graph, start_node):
    """
    Ruta más corta usando Dijkstra DESDE CERO sin networkx.
    graph: lista de tuplas (origen, destino, peso, capacidad)
    """
    # Construir grafo como diccionario
    nodes = set()
    adj_list = {}
    for u, v, weight, capacity in graph:
        nodes.add(u)
        nodes.add(v)
        if u not in adj_list:
            adj_list[u] = []
        adj_list[u].append((v, weight))
    
    for node in nodes:
        if node not in adj_list:
            adj_list[node] = []
    
    # Dijkstra
    distances = {node: float('inf') for node in nodes}
    distances[start_node] = 0
    previous = {node: None for node in nodes}
    visited = set()
    pq = [(0, start_node)]  # (distancia, nodo)
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        for neighbor, weight in adj_list[current_node]:
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    # Encontrar nodo destino con mayor distancia
    end_node = max(distances.keys(), key=lambda x: distances[x] if distances[x] != float('inf') else -1)
    
    # Reconstruir camino
    path = []
    node = end_node
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    
    total_weight = distances[end_node] if distances[end_node] != float('inf') else float('inf')
    
    image = generate_graph_image(graph, path, "Ruta Más Corta (Dijkstra)")
    
    return {
        "total_weight": float(total_weight),
        "node_order": path,
        "start_node": start_node,
        "end_node": end_node,
        "graph_image": image
    }


class UnionFind:
    """Estructura de datos Union-Find para Kruskal"""
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


def minimum_spanning_tree(graph):
    """
    Árbol de Expansión Mínima usando Kruskal DESDE CERO sin networkx.
    """
    # Mapear nodos a índices
    nodes = set()
    edges = []
    for u, v, weight, capacity in graph:
        nodes.add(u)
        nodes.add(v)
        edges.append((weight, u, v))
    
    nodes_list = sorted(list(nodes))
    node_to_idx = {node: i for i, node in enumerate(nodes_list)}
    
    # Ordenar aristas por peso
    edges.sort()
    
    # Kruskal
    uf = UnionFind(len(nodes_list))
    mst_edges = []
    total_weight = 0
    
    for weight, u, v in edges:
        u_idx = node_to_idx[u]
        v_idx = node_to_idx[v]
        
        if uf.union(u_idx, v_idx):
            mst_edges.append((u, v, weight))
            total_weight += weight
    
    image = generate_graph_image(mst_edges, title="Árbol de Expansión Mínima (Kruskal)")
    
    return {
        "edges": mst_edges,
        "total_weight": float(total_weight),
        "graph_image": image
    }


def ford_fulkerson_algorithm(graph, source, sink):
    """
    Flujo Máximo usando Ford-Fulkerson DESDE CERO sin networkx.
    """
    # Construir capacidades
    nodes = set()
    capacity = {}
    adj_list = {}
    
    for u, v, weight, cap in graph:
        nodes.add(u)
        nodes.add(v)
        capacity[(u, v)] = cap
        if (v, u) not in capacity:
            capacity[(v, u)] = 0
        
        if u not in adj_list:
            adj_list[u] = []
        if v not in adj_list:
            adj_list[v] = []
        adj_list[u].append(v)
        adj_list[v].append(u)
    
    for node in nodes:
        if node not in adj_list:
            adj_list[node] = []
    
    def bfs_find_path():
        """BFS para encontrar camino aumentante"""
        visited = {source}
        queue = [source]
        parent = {}
        
        while queue:
            u = queue.pop(0)
            for v in adj_list[u]:
                cap = capacity.get((u, v), 0)
                if v not in visited and cap > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)
                    if v == sink:
                        return parent
        return None
    
    max_flow = 0
    iterations = []
    parent_map = bfs_find_path()
    
    while parent_map is not None:
        # Encontrar capacidad mínima en el camino
        path = []
        v = sink
        min_cap = float('inf')
        
        while v != source:
            u = parent_map[v]
            min_cap = min(min_cap, capacity.get((u, v), 0))
            path.append(u)
            v = u
        path.reverse()
        path.append(sink)
        
        # Actualizar capacidades
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            capacity[(u, v)] -= min_cap
            capacity[(v, u)] = capacity.get((v, u), 0) + min_cap
        
        max_flow += min_cap
        iterations.append({
            "path": " → ".join(map(str, path)),
            "capacity": min_cap
        })
        
        parent_map = bfs_find_path()
    
    image = generate_graph_image(graph, title="Flujo Máximo (Ford-Fulkerson)")
    
    return {
        "max_flow": float(max_flow),
        "iterations": iterations,
        "start_node": source,
        "end_node": sink,
        "graph_image": image
    }


def min_cost_flow_algorithm(graph, source, sink):
    """
    Flujo de Costo Mínimo usando algoritmo de caminos sucesivos DESDE CERO.
    """
    # Construir grafo
    nodes = set()
    edges_dict = {}
    capacity = {}
    cost = {}
    adj_list = {}
    
    for u, v, weight, cap in graph:
        nodes.add(u)
        nodes.add(v)
        capacity[(u, v)] = cap
        cost[(u, v)] = weight
        
        if (v, u) not in capacity:
            capacity[(v, u)] = 0
            cost[(v, u)] = -weight
        
        if u not in adj_list:
            adj_list[u] = []
        if v not in adj_list:
            adj_list[v] = []
        if v not in adj_list[u]:
            adj_list[u].append(v)
        if u not in adj_list[v]:
            adj_list[v].append(u)
    
    for node in nodes:
        if node not in adj_list:
            adj_list[node] = []
    
    def dijkstra_shortest_path():
        """Dijkstra para encontrar camino de costo mínimo"""
        dist = {node: float('inf') for node in nodes}
        dist[source] = 0
        parent = {}
        visited = set()
        pq = [(0, source)]
        
        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            
            for v in adj_list[u]:
                if capacity.get((u, v), 0) > 0:
                    new_dist = d + cost.get((u, v), 0)
                    if new_dist < dist[v]:
                        dist[v] = new_dist
                        parent[v] = u
                        heapq.heappush(pq, (new_dist, v))
        
        if dist[sink] == float('inf'):
            return None, float('inf')
        
        path = []
        v = sink
        while v != source:
            u = parent[v]
            path.append(u)
            v = u
        path.reverse()
        path.append(sink)
        
        return path, dist[sink]
    
    total_cost = 0
    total_flow = 0
    iterations = []
    
    while True:
        path, path_cost = dijkstra_shortest_path()
        if path is None:
            break
        
        # Encontrar capacidad mínima
        min_cap = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            min_cap = min(min_cap, capacity.get((u, v), 0))
        
        if min_cap == 0:
            break
        
        # Actualizar flujo
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            capacity[(u, v)] -= min_cap
            capacity[(v, u)] = capacity.get((v, u), 0) + min_cap
        
        total_flow += min_cap
        total_cost += min_cap * path_cost
        
        iterations.append({
            "path": " → ".join(map(str, path)),
            "flow": min_cap,
            "cost": min_cap * path_cost
        })
    
    image = generate_graph_image(graph, title="Flujo Costo Mínimo")
    
    return {
        "total_flow": float(total_flow),
        "min_cost": float(total_cost),
        "iterations": iterations,
        "start_node": source,
        "end_node": sink,
        "graph_image": image
    }


def generate_graph_image(graph, paths=None, title="Grafo"):
    """Genera una imagen del grafo con Matplotlib"""
    try:
        import networkx as nx
        
        G = nx.DiGraph()
        for edge in graph:
            if len(edge) == 4:
                u, v, weight, capacity = edge
                G.add_edge(u, v, weight=weight)
            elif len(edge) == 3:
                u, v, weight = edge
                G.add_edge(u, v, weight=weight)
            else:
                raise ValueError("Formato de arista no soportado")

        pos = nx.spring_layout(G)
        labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}

        plt.figure(figsize=(6, 4))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        if paths:
            edges = [(paths[i], paths[i + 1]) for i in range(len(paths) - 1)]
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='red', width=2)

        plt.title(title)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        return image_base64
    except:
        # Si falla NetworkX, retornar imagen vacía
        return ""

    # Obtener nodo destino con la mayor distancia encontrada
    end_node = max(path_lengths, key=path_lengths.get)
    total_weight = path_lengths[end_node]
    node_order = paths[end_node] if end_node in paths else []

    image = generate_graph_image(graph, node_order, "Ruta Más Corta")

    return {
        "total_weight": total_weight,
        "node_order": node_order,
        "start_node": start_node,
        "end_node": end_node,
        "graph_image": image
    }

def sensitivity_analysis_shortest_path(graph, start_node, end_node):
    """
    Análisis de sensibilidad: calcula impacto de eliminar cada arista.
    Implementado sin librerías externas.
    """
    # Calcular distancia base
    result_base = dijkstra_algorithm(graph, start_node)
    base_length = result_base["total_weight"]
    
    results = {}
    for idx, (u, v, weight, capacity) in enumerate(graph):
        # Crear grafo sin esta arista
        graph_temp = [edge for i, edge in enumerate(graph) if i != idx]
        
        if not graph_temp:
            results[f"({u},{v})"] = "Sin ruta" if base_length != float('inf') else "Sin cambio"
            continue
        
        try:
            result_temp = dijkstra_algorithm(graph_temp, start_node)
            new_length = result_temp["total_weight"]
            
            if new_length == float('inf'):
                impact = "Sin ruta"
            else:
                impact = new_length - base_length
            results[f"({u},{v})"] = impact
        except:
            results[f"({u},{v})"] = "Error"
    
    return results


def solve_all_problems(graph):
    """Resuelve todos los problemas de redes y devuelve datos completos"""
    if not graph:
        return {"error": "Grafo vacío"}
    
    source = graph[0][0]
    sink = graph[-1][1]

    return {
        "shortest_path": dijkstra_algorithm(graph, source),
        "mst": minimum_spanning_tree(graph),
        "max_flow": ford_fulkerson_algorithm(graph, source, sink),
        "min_cost_flow": min_cost_flow_algorithm(graph, source, sink),
    }

