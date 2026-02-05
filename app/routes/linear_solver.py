from fastapi import APIRouter, HTTPException
# Eliminamos las funciones que ya no existen en models.linear_program
from app.models.linear_program import solve_linear_problem, solve_graphical, solve_dual_linear_problem
from app.utils.validations import validate_linear_problem
from app.utils.sensitivity_analysis import analyze_sensitivity, generate_intelligent_sensitivity_analysis

router = APIRouter()

@router.post("/solve_linear")
def solve_linear(data: dict):
    print("Datos recibidos:", data)
    
    # 1. Validaciones previas
    errors = validate_linear_problem(data)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    
    method = data.get("method", "simplex")
    
    try:
        # 2. Selección de motor de cálculo
        if method == "graphical":
            solution = solve_graphical(data)
        elif method == "dual":
            solution = solve_dual_linear_problem(data)
        else:
            # Esta función unificada ahora resuelve 'simplex', 'two_phase' y 'm_big'
            # pasando el método interno a SimplexSolverV2
            solution = solve_linear_problem(data)

        # Validar que la solución no sea None
        if solution is None:
            raise ValueError("El motor de cálculo no devolvió una respuesta válida.")

        # 3. Análisis de sensibilidad (No aplica a Gráfico)
        sensitivity = None
        intelligent_analysis = None
        
        if method != "graphical":
            try:
                # Calcular valores numéricos de sensibilidad
                sensitivity = analyze_sensitivity(data, solution)
                
                # Generar interpretación con IA (Groq/Gemini)
                intelligent_analysis = generate_intelligent_sensitivity_analysis(
                    data, solution, sensitivity, method
                )
            except Exception as e:
                print(f"❌ Error en análisis de sensibilidad: {str(e)}")
                sensitivity = {}
                intelligent_analysis = "Error al generar análisis de sensibilidad."

        # 4. Construcción de la respuesta final
        response = {
            "solution": solution, 
            "sensitivity": sensitivity, 
            "intelligent_analysis": intelligent_analysis
        }

        # Manejo de la ruta de la imagen para el gráfico
        if method == "graphical" and "graph" in solution:
            # Mantenemos la ruta que viene del modelo o la forzamos a la estática
            response["solution"]["graph"] = solution.get("graph", "/static/graph_with_table.png")
        else:
            # Aseguramos que la llave exista como None para evitar errores en el frontend
            if "solution" in response and isinstance(response["solution"], dict):
                response["solution"]["graph"] = None

        print("✅ Respuesta exitosa generada")
        return response

    except Exception as e:
        print(f"🔥 Error crítico en solve_linear: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")