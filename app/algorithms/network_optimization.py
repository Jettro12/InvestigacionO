import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

import matplotlib
matplotlib.use('Agg')

def generate_graph_image(graph, paths=None, title="Grafo"):
    """Genera una imagen del grafo con NetworkX y Matplotlib"""
    G = nx.DiGraph()
    # Admite aristas de 3 o 4 valores
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


def dijkstra_algorithm(graph, start_node):
    """Ruta más corta con peso total y orden de nodos"""
    G = nx.DiGraph()
    for u, v, weight, capacity in graph:
        G.add_edge(u, v, weight=weight)

    path_lengths, paths = nx.single_source_dijkstra(G, start_node)

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

def min_cost_flow_algorithm(graph, source, sink):
    G = nx.DiGraph()
    for u, v, weight, capacity in graph:
        G.add_edge(u, v, capacity=capacity, weight=weight)
    try:
        flow_dict = nx.max_flow_min_cost(G, source, sink, capacity="capacity", weight="weight")
        cost = nx.cost_of_flow(G, flow_dict)
    except Exception as e:
        flow_dict = {}
        cost = str(e)
    return {
        "flow": flow_dict,
        "min_cost": cost,
        "start_node": source,
        "end_node": sink
    }



def sensitivity_analysis_shortest_path(graph, start_node, end_node):
    """
    Para cada arista, calcula el nuevo peso total de la ruta más corta si esa arista se elimina.
    """
    G = nx.DiGraph()
    for u, v, weight, capacity in graph:
        G.add_edge(u, v, capacity=capacity, weight=weight)
    try:
        base_length = nx.dijkstra_path_length(G, start_node, end_node)
    except nx.NetworkXNoPath:
        base_length = float('inf')
    results = {}
    for u, v, weight, capacity in graph:
        G_temp = G.copy()
        G_temp.remove_edge(u, v)
        try:
            new_length = nx.dijkstra_path_length(G_temp, start_node, end_node)
        except nx.NetworkXNoPath:
            new_length = float('inf')
        impact = new_length - base_length if new_length != float('inf') else 'Sin ruta'
        results[f"({u},{v})"] = impact
    return results



def minimum_spanning_tree(graph):
    """Árbol de Expansión Mínima con peso total"""
    G = nx.Graph()
    for u, v, weight, capacity in graph:
        G.add_edge(u, v, weight=weight)

    mst = nx.minimum_spanning_tree(G, algorithm="kruskal")
    mst_edges = [(u, v, d["weight"]) for u, v, d in mst.edges(data=True)]
    
    # ✅ Corrección: sumar pesos correctamente
    total_weight = sum(weight for _, _, weight in mst_edges)

    image = generate_graph_image(mst_edges, title="Árbol de Expansión Mínima")

    return {
        "edges": mst_edges,
        "total_weight": total_weight,
        "graph_image": image
    }

def max_flow_algorithm(graph, source, sink):
    """Flujo Máximo con detalle del flujo por nodo e iteraciones"""
    G = nx.DiGraph()
    
    # Agregar aristas con capacidad
    for u, v, weight, capacity in graph:
        G.add_edge(u, v, capacity=capacity)


    # Inicializar variables
    flow_value = 0
    iterations = []
    residual_graph = G.copy()

    # Aplicar algoritmo de Edmonds-Karp
    while True:
        try:
            # Encontrar camino aumentante con BFS
            path = nx.shortest_path(residual_graph, source=source, target=sink, weight=None)
            min_capacity = min(residual_graph[u][v]["capacity"] for u, v in zip(path, path[1:]))
            
            # Guardar la iteración
            iterations.append({
                "path": " → ".join(path),
                "capacity": min_capacity
            })

            # Actualizar capacidades del grafo residual
            for u, v in zip(path, path[1:]):
                residual_graph[u][v]["capacity"] -= min_capacity
                if residual_graph[u][v]["capacity"] == 0:
                    residual_graph.remove_edge(u, v)

            # Acumular flujo
            flow_value += min_capacity

        except nx.NetworkXNoPath:
            # No hay más caminos aumentantes
            break

    # Generar imagen del flujo máximo
    image = generate_graph_image(graph, title="Flujo Máximo")

    return {
        "max_flow": flow_value,
        "iterations": iterations,
        "start_node": source,
        "end_node": sink,
        "graph_image": image
    }


def solve_all_problems(graph):
    """Resuelve todos los problemas y devuelve datos completos"""
    source, sink = graph[0][0], graph[-1][1]

    return {
        "shortest_path": dijkstra_algorithm(graph, list(graph[0])[0]),
        "mst": minimum_spanning_tree(graph),
        "max_flow": max_flow_algorithm(graph, source, sink),
        "min_cost_flow": min_cost_flow_algorithm(graph, source, sink),
    }

