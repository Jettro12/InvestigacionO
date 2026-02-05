from groq import Groq
import os
import json
from dotenv import load_dotenv
import numpy as np

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY) if API_KEY else None

from algorithms.network_optimization import (
    solve_all_problems, sensitivity_analysis_shortest_path
)

def gemini_network_sensitivity_analysis(graph, shortest_path_result, max_flow_result):
    if not client:
        return "⚠️ Error: API de Groq no configurada."
    
    try:
        # CORRECCIÓN: Convertir a lista estándar si es un array de numpy
        clean_graph = graph.tolist() if isinstance(graph, np.ndarray) else graph
        
        # Preparar datos legibles
        graph_data = [{"desde": e[0], "hacia": e[1], "costo": e[2], "capacidad": e[3]} for e in clean_graph]
        
        prompt = f"""Actúa como un experto en Ingeniería de Redes. Analiza esta red:
        
        **DATOS TÉCNICOS:**
        - Estructura (Aristas): {json.dumps(graph_data)}
        - Ruta Más Corta: {shortest_path_result.get('node_order', [])}
        - Peso Total: {shortest_path_result.get('total_weight', 0)}
        - Flujo Máximo: {max_flow_result.get('max_flow', 0)}

        **INSTRUCCIONES:**
        1. Identifica Puntos de Falla Únicos [CRÍTICO].
        2. Analiza Cuellos de Botella basándote en la capacidad [RIESGO].
        3. Evalúa la Resiliencia y da una [RECOMENDACIÓN].
        
        Sé técnico y directo."""

        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2 
        )
        return message.choices[0].message.content
    except Exception as e:
        print(f"❌ Error en IA de Redes: {e}")
        return f"No se pudo generar el análisis: {str(e)}"

def solve_optimization_network(problem_type, data):
    graph = data["graph"]
    
    # Aseguramos que el algoritmo reciba el formato correcto
    results = solve_all_problems(graph)
    
    all_nodes = sorted(list(set([node for edge in graph for node in edge[:2]])))
    start_node = data.get("start_node", all_nodes[0])
    end_node = data.get("end_node", all_nodes[-1])

    # Inyectamos el análisis de sensibilidad
    results["shortest_path"]["sensitivity_analysis_gemini"] = gemini_network_sensitivity_analysis(
        graph, 
        results["shortest_path"], 
        results.get("max_flow", {})
    )
    
    return results