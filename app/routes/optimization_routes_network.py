from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Union  # ✅ Permite que los pesos sean int o float
from services.optimization_service_network import solve_optimization_network

router = APIRouter()

class NetworkProblemRequest(BaseModel):
    graph: List[List[Union[str, int, float]]]  # ✅ Ahora acepta nombres de nodos como str y pesos como int o float

@router.post("/solve_network")
def solve_network_problem(request: NetworkProblemRequest):
    print(">>> ENTRANDO AL ENDPOINT /api/solve_network")
    print(f"Payload recibido: {request.graph}")
    result = solve_optimization_network("all", {"graph": request.graph})
    print(">>> Resultado de solve_optimization_network:", result)
    return result
