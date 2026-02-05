from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os # Para leer la API Key

# Importamos la lógica matemática Y la función de IA
from models.linear_program import (
    solve_simplex,
    solve_graphical,
    solve_big_m,
    solve_two_phase,
     
    generate_intelligent_report # <--- IMPORTANTE: Agregamos esto
)

# Configuración de Groq o el cliente de IA que uses
from groq import Groq 

# Inicializa el cliente (Asegúrate de tener la variable de entorno o poner tu key aquí)
client_ia = Groq(api_key=os.environ.get("GROQ_API_KEY", "tu_api_key_aqui"))

router = APIRouter()

class Constraint(BaseModel):
    coeffs: List[float]
    sign: str
    rhs: float

class LinearRequest(BaseModel):
    objective: str
    objective_coeffs: List[float]
    constraints: List[Constraint]
    method: str
    variables: Optional[List[str]] = None

@router.post("/solve_linear")
def solve_linear(req: LinearRequest):
    cons = [c.dict() for c in req.constraints]
    result = None

    # 1. Ejecutar el cálculo matemático según el método
    if req.method == "simplex":
        result = solve_simplex(req.objective_coeffs, cons, req.objective)
    elif req.method == "graphical":
        result = solve_graphical(req.objective_coeffs, cons, req.objective)
    elif req.method == "m_big":
        result = solve_big_m(req.objective_coeffs, cons, req.objective)
    elif req.method == "two_phase":
        result = solve_two_phase(req.objective_coeffs, cons, req.objective)
     
    else:
        raise HTTPException(status_code=400, detail="Método no reconocido")

    # 2. GENERAR EL ANÁLISIS DE IA (Solo si el resultado fue exitoso)
    if result and result.get("status") == "optimal":
        # Llamamos a la función de reporte pasando los datos originales y el resultado
        analysis = generate_intelligent_report(req.dict(), result, client=client_ia)
        # Inyectamos el reporte en el diccionario de respuesta
        result["intelligent_analysis"] = analysis

    return result