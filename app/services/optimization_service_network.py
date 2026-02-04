print(">>> CARGANDO app/services/optimization_service_network.py")

from groq import Groq
import os
from dotenv import load_dotenv

# Cargar .env desde la carpeta app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Cargar API key desde .env
API_KEY = os.getenv("GROQ_API_KEY")
if API_KEY:
    client = Groq(api_key=API_KEY)
    print(f"✅ API_KEY configurada para Groq (primeros 20 caracteres): {API_KEY[:20]}...")
else:
    print("❌ ERROR: GROQ_API_KEY no está configurada en .env")
    client = None

from app.algorithms.network_optimization import (
    solve_all_problems, sensitivity_analysis_shortest_path
)

def gemini_network_sensitivity_analysis(graph, shortest_path_result):
    if not client:
        return "Error: API de Groq no configurada. Verifica tu GROQ_API_KEY en .env"
    
    print(">>> ENTRANDO a groq_network_sensitivity_analysis")
    import json
    
    # Convertir datos a strings JSON
    graph_str = json.dumps(graph)
    node_order_str = json.dumps(shortest_path_result.get('node_order', []))
    
    prompt = f"""Analiza la sensibilidad de esta red:
    Grafo: {graph_str}
    Ruta más corta encontrada: {node_order_str}
    Peso total: {shortest_path_result.get('total_weight', 'N/A')}

Proporciona un análisis claro en texto plano. Usa estas marcas:
- [CRÍTICO] para información importante
- [RECOMENDACIÓN] para mejoras sugeridas
- [RIESGO] para puntos débiles

Incluye:
1. Qué aristas son críticas para la ruta
2. Impacto si se elimina una arista crítica
3. Evaluación de robustez de la red
4. Mejoras para mejorar la red
5. Análisis de rutas alternativas
6. Recomendaciones concretas

Presenta en texto limpio y comprensible."""
    
    try:
        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        response = message.choices[0].message.content
        print(">>> RESPUESTA DE GROQ:", response)
        return response
    except Exception as e:
        response = f"Error al generar análisis con Groq: {str(e)}"
        print(">>> ERROR DE GROQ:", response)
        return response

def solve_optimization_network(problem_type, data):
    print(f">>> solve_optimization_network llamado con problem_type={problem_type}")
    graph = data["graph"]
    results = solve_all_problems(graph)
    # Agregar análisis de sensibilidad solo a shortest_path
    start_node = graph[0][0]
    end_node = graph[-1][1]
    results["shortest_path"]["sensitivity_analysis"] = sensitivity_analysis_shortest_path(graph, start_node, end_node)
    results["shortest_path"]["sensitivity_analysis_gemini"] = gemini_network_sensitivity_analysis(graph, results["shortest_path"])
    return results
