import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

# Configurar Gemini AI
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_sensitivity(data, solution):
    from models.linear_program import solve_linear_problem  # Importación dentro de la función

    perturbation = 0.01
    sensitivities = {}

    # Verificar que la solución original sea válida
    if not solution or "objective_value" not in solution:
        print("❌ Solución original no válida para análisis de sensibilidad")
        return {}

    original_objective_value = solution["objective_value"]

    for i, var in enumerate(data["variables"]):
        try:
            # Crear una copia de los datos con el coeficiente modificado
            modified_coeffs = data["objective_coeffs"][:]
            modified_coeffs[i] += perturbation
            new_data = data.copy()
            new_data["objective_coeffs"] = modified_coeffs

            # Resolver el problema modificado
            new_solution = solve_linear_problem(new_data)
            
            # Verificar que la nueva solución sea válida
            if new_solution and "objective_value" in new_solution:
                # Calcular la sensibilidad
                sensitivity = (new_solution["objective_value"] - original_objective_value) / perturbation
                sensitivities[var] = sensitivity
                print(f"✅ Sensibilidad calculada para {var}: {sensitivity}")
            else:
                print(f"❌ No se pudo calcular sensibilidad para {var}: solución inválida")
                sensitivities[var] = 0.0
                
        except Exception as e:
            print(f"❌ Error calculando sensibilidad para {var}: {str(e)}")
            sensitivities[var] = 0.0

    print(f"📊 Análisis de sensibilidad completado: {sensitivities}")
    return sensitivities

def generate_intelligent_sensitivity_analysis(data, solution, sensitivities, method):
    """
    Genera un análisis de sensibilidad inteligente usando Gemini AI para programación lineal.
    """
    try:
        # Preparar la información para el análisis
        objective_type = "Maximización" if data["objective"] == "max" else "Minimización"
        variables_info = ", ".join([f"{var} (coef: {data['objective_coeffs'][i]})" 
                                   for i, var in enumerate(data["variables"])])
        
        constraints_info = []
        for i, constraint in enumerate(data["constraints"]):
            constraint_str = " + ".join([f"{constraint['coeffs'][j]}{data['variables'][j]}" 
                                       for j in range(len(constraint['coeffs']))])
            constraints_info.append(f"Restricción {i+1}: {constraint_str} {constraint['sign']} {constraint['rhs']}")
        
        prompt = f"""Realiza un análisis de sensibilidad detallado para un problema de programación lineal:

**Datos del Problema:**
- Tipo de objetivo: {objective_type}
- Variables: {variables_info}
- Restricciones: {chr(10).join(constraints_info)}
- Método de solución: {method}

**Solución Óptima:**
- Valor óptimo: {solution.get('objective_value', 'N/A')}
- Valores de variables: {solution.get('variable_values', {})}
- Estado: {solution.get('status', 'N/A')}

**Análisis de Sensibilidad (valores numéricos):**
{sensitivities}

**Instrucciones para el análisis:**
1️⃣ **Interpretación de Sensibilidad**: Explica qué significan estos valores de sensibilidad en términos prácticos.
2️⃣ **Variables Críticas**: Identifica qué variables son más sensibles y por qué.
3️⃣ **Recomendaciones de Gestión**: Sugiere estrategias para manejar las variables más sensibles.
4️⃣ **Análisis de Riesgo**: Evalúa qué tan robusta es la solución actual.
5️⃣ **Oportunidades de Mejora**: Identifica posibles ajustes que podrían optimizar mejor el resultado.

Presenta la respuesta de manera clara y estructurada, usando lenguaje comprensible para un usuario de negocios.
"""

        response = model.generate_content(prompt).text
        return response
        
    except Exception as e:
        print(f"❌ Error generando análisis inteligente: {str(e)}")
        return f"Error al generar análisis inteligente: {str(e)}"
