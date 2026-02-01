from fastapi import APIRouter, HTTPException
from models.linear_program import solve_linear_problem, solve_graphical, solve_two_phase_linear_problem, solve_m_big_linear_problem, solve_dual_linear_problem

from utils.validations import validate_linear_problem
from utils.sensitivity_analysis import analyze_sensitivity, generate_intelligent_sensitivity_analysis

router = APIRouter()

@router.post("/solve_linear")
def solve_linear(data: dict):
    print("Datos recibidos:", data)
    errors = validate_linear_problem(data)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    
    # Determinar el método a utilizar
    method = data.get("method", "simplex")  # Método por defecto: Simplex
    try:
        if method == "graphical":
            solution = solve_graphical(data)  # Llamar al método gráfico
        elif method == "two_phase":
            # Llamar al método de Dos Fases
            solution = solve_two_phase_linear_problem(
                data["objective_coeffs"],
                data["variables"],
                data["constraints"],
                data["objective"]
            )
        elif method == "m_big":  # Para el método Gran M
            solution = solve_m_big_linear_problem(
                data["objective_coeffs"],
                data["variables"],
                data["constraints"],
                data["objective"]
            )
        elif method == "dual":
            solution = solve_dual_linear_problem(data)    
                
        else:
            solution = solve_linear_problem(data)  # Llamar al método de programación lineal

        # Análisis de sensibilidad solo se aplica a métodos de programación lineal
        sensitivity = None
        intelligent_analysis = None
        if method != "graphical":
            try:
                # Calcular valores de sensibilidad
                sensitivity = analyze_sensitivity(data, solution)
                print(f"📊 Análisis de sensibilidad generado: {sensitivity}")
                
                # Generar análisis inteligente con Gemini AI
                intelligent_analysis = generate_intelligent_sensitivity_analysis(data, solution, sensitivity, method)
                print(f"🤖 Análisis inteligente generado con Gemini AI")
                
            except Exception as e:
                print(f"❌ Error en análisis de sensibilidad: {str(e)}")
                sensitivity = {}
                intelligent_analysis = "Error al generar análisis de sensibilidad."

     # En tu método solve_linear:
        response = {"solution": solution, "sensitivity": sensitivity, "intelligent_analysis": intelligent_analysis}
        if method == "graphical":
            response["solution"]["graph"] = "/static/graph_with_table.png"
        else:
            response["solution"]["graph"] = None

        print("Respuesta del backend:", response)  # Para depuración
        return response

    except Exception as e:
        print("Error en solve_linear:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    # En el método gráfico (supongamos que es dentro de 'solve_graphical')
def save_graph_to_file():
    graph_path = "static/graph_with_table.png"  # Guardar la imagen en la carpeta pública
    # Código para generar el gráfico y guardarlo en graph_path

