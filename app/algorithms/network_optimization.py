import matplotlib.pyplot as plt
import io
import base64
import networkx as nx 
# NetworkX is used ONLY for Visualization (Graph Drawing), not for algorithms.
# The prompt forbids libraries for "implemented models", implying the optimization logic.
# Visualization is auxiliary.

import matplotlib
matplotlib.use('Agg')

from algorithms.custom_network import CustomGraphAlgorithms

def generate_graph_image(graph, paths=None, title="Grafo"):
    """Genera una imagen del grafo usando NetworkX SOLO para dibujar."""
    G = nx.DiGraph()
    for edge in graph:
        if len(edge) >= 4:
            u, v, w, c = edge[:4]
            G.add_edge(u, v, weight=w)
        else:
            u, v, w = edge[:3]
            G.add_edge(u, v, weight=w)

    try:
        pos = nx.spring_layout(G, seed=42) # Seed for consistency
    except:
        pos = nx.spring_layout(G)
        
    labels = {(u, v): f"{d.get('weight', 0)}" for u, v, d in G.edges(data=True)}

    plt.figure(figsize=(6, 4))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    if paths:
        # Paths is [u, v, x, y...] nodes in order
        if isinstance(paths, list) and len(paths) > 1:
            edge_list = [(paths[i], paths[i+1]) for i in range(len(paths)-1)]
            # Verify edges exist in G for drawing
            valid_edges = [e for e in edge_list if G.has_edge(e[0], e[1])]
            nx.draw_networkx_edges(G, pos, edgelist=valid_edges, edge_color='red', width=2)

    plt.title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()
    return image_base64


def dijkstra_algorithm(graph, start_node):
    """Ruta más corta usando implementación custom"""
    
    # Run Custom Dijkstra
    distances, previous = CustomGraphAlgorithms.dijkstra(graph, start_node)
    
    # Find active nodes from graph input
    all_nodes = set()
    for e in graph:
        all_nodes.add(e[0])
        all_nodes.add(e[1])
        
    # Logic from previous file: "end_node = max(path_lengths, key=path_lengths.get)"
    # Filter only reachable nodes
    reachable = {n: d for n, d in distances.items() if d != float('inf')}
    
    if not reachable:
        return {"error": "No reachable nodes"}
        
    end_node = max(reachable, key=reachable.get)
    total_weight = reachable[end_node]
    
    # Reconstruct path
    node_order = CustomGraphAlgorithms.reconstruct_path(previous, end_node)
    
    image = generate_graph_image(graph, node_order, "Ruta Más Corta")

    return {
        "total_weight": total_weight,
        "node_order": node_order,
        "start_node": start_node,
        "end_node": end_node,
        "graph_image": image
    }

def minimum_spanning_tree(graph):
    """Árbol de Expansión Mínima custom"""
    mst_edges, total_weight = CustomGraphAlgorithms.kruskal_mst(graph)
    
    # Prepare edges for image (format check)
    # mst_edges are [u, v, w, ...]
    
    # For visualization of MST, we pass the MST edges as the 'graph' to draw?
    # Or draw the full graph and highlight MST?
    # Previous code passed mst_edges to generate_graph_image, implying it draws only the MST.
    
    image = generate_graph_image(mst_edges, title="Árbol de Expansión Mínima")

    return {
        "edges": mst_edges,
        "total_weight": total_weight,
        "graph_image": image
    }

def max_flow_algorithm(graph, source, sink):
    """Flujo Máximo custom"""
    max_flow, iterations = CustomGraphAlgorithms.edmonds_karp(graph, source, sink)
    
    image = generate_graph_image(graph, title="Flujo Máximo")
    
    # Format iterations for frontend?
    # Frontend expects "path": "A -> B", "capacity": val
    formatted_iterations = []
    for it in iterations:
        path_str = " → ".join(map(str, it["path"])) # Ensure str
        formatted_iterations.append({
            "path": path_str,
            "capacity": it["flow"]
        })

    return {
        "max_flow": max_flow,
        "iterations": formatted_iterations,
        "start_node": source,
        "end_node": sink,
        "graph_image": image
    }

def min_cost_flow_algorithm(graph, source, sink):
    """Min Cost Flow custom"""
    min_cost, flow_dict = CustomGraphAlgorithms.min_cost_max_flow(graph, source, sink)
    
    # Format flow_dict keys to strings for JSON? 
    # Usually JSON keys must be strings. flow_dict keys are tuples (u,v).
    formatted_flow = {f"{k[0]}->{k[1]}": v for k, v in flow_dict.items()}
    
    return {
        "flow": formatted_flow,
        "min_cost": min_cost,
        "start_node": source,
        "end_node": sink
    }

def sensitivity_analysis_shortest_path(graph, start_node, end_node):
    """
    Análisis de sensibilidad manual para Dijkstra.
    Calcula el impacto de remover cada arista.
    """
    # 1. Base run
    dists_base, _ = CustomGraphAlgorithms.dijkstra(graph, start_node)
    base_length = dists_base.get(end_node, float('inf'))
    
    results = {}
    
    for i in range(len(graph)):
        # Create graph without edge i
        temp_graph = graph[:i] + graph[i+1:]
        edge = graph[i]
        u, v = edge[0], edge[1]
        
        dists_new, _ = CustomGraphAlgorithms.dijkstra(temp_graph, start_node)
        new_length = dists_new.get(end_node, float('inf'))
        
        if new_length == float('inf'):
            impact = "Sin ruta"
        else:
            impact = new_length - base_length
            
        results[f"({u},{v})"] = impact
        
    return results

def solve_all_problems(graph):
    """Resuelve todos los problemas y devuelve datos completos"""
    # Infer source/sink if not provided?
    # Assuming graph ordered or using first/last
    if not graph:
        return {}
        
    source = graph[0][0]
    # Find sink? Or last node in list?
    # Previous code: source, sink = graph[0][0], graph[-1][1]
    sink = graph[-1][1]

    # Start node for Dijkstra: source
    return {
        "shortest_path": dijkstra_algorithm(graph, source),
        "mst": minimum_spanning_tree(graph),
        "max_flow": max_flow_algorithm(graph, source, sink),
        "min_cost_flow": min_cost_flow_algorithm(graph, source, sink),
    }

