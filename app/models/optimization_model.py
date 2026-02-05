from sqlalchemy import Column, Integer, String, JSON
from database.db import Base

class OptimizationProblem(Base):
    __tablename__ = "optimization_problems"

    id = Column(Integer, primary_key=True, index=True)
    problem_type = Column(String, index=True)  # "linear", "transport", "network"
    input_data = Column(JSON)  # Datos en JSON
    solution = Column(JSON)  # Resultado en JSON
