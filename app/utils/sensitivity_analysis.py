from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

# Configurar Groq AI
API_KEY = os.getenv("GROQ_API_KEY")
if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    print("⚠️ Advertencia: GROQ_API_KEY no está configurada en .env")
    client = None

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
    Genera un análisis de sensibilidad inteligente usando Groq AI para programación lineal.
    Retorna texto plano con énfasis en puntos importantes.
    """
    if not client:
        return "Error: API de Groq no configurada. Verifica tu GROQ_API_KEY en .env"
    
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
        
        # Convertir diccionarios a strings JSON para evitar errores con f-strings
        import json
        sensitivities_str = json.dumps(sensitivities) if sensitivities else "{}"
        variable_values_str = json.dumps(solution.get('variable_values', {}))
        
        prompt = f"""Realiza un análisis de sensibilidad detallado para un problema de programación lineal.

**Datos del Problema:**
- Tipo de objetivo: {objective_type}
- Variables: {variables_info}
- Restricciones: {chr(10).join(constraints_info)}
- Método de solución: {method}

**Solución Óptima:**
- Valor óptimo: {solution.get('objective_value', 'N/A')}
- Valores de variables: {variable_values_str}
- Estado: {solution.get('status', 'N/A')}

**Análisis de Sensibilidad (valores numéricos):**
{sensitivities_str}

Presenta un análisis claro y práctico. Usa estas marcas para resaltar información:
- [CRÍTICO] para información importante que afecta la solución
- [RECOMENDACIÓN] para sugerencias accionables
- [RIESGO] para puntos débiles de la solución
Presenta el análisis en texto limpio y comprensible para un usuario de negocios."""

        message = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        response = message.choices[0].message.content
        return response
        
    except Exception as e:
        print(f"❌ Error generando análisis inteligente: {str(e)}")
        return f"Error al generar análisis inteligente: {str(e)}"
