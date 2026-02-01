def validate_linear_problem(data):
    errors = []
    if "objective" not in data or data["objective"] not in ["min", "max"]:
        errors.append("El objetivo debe ser 'min' o 'max'.")
    if "variables" not in data or not isinstance(data["variables"], list):
        errors.append("Debe definir las variables correctamente.")

    # Solo forzar '<=' para Simplex estándar; permitir '=', '>=' para Gran M, Dos Fases, Dual
    allowed_signs = {
        "simplex": ["<="],
        "m_big": ["<=", ">=", "="],
        "two_phase": ["<=", ">=", "="],
        "dual": ["<=", ">=", "="],
        "graphical": ["<="],  # depende de implementación
    }
    method = data.get("method", "simplex")
    allowed = allowed_signs.get(method, ["<="])
    if "constraints" in data and isinstance(data["constraints"], list):
        for i, constraint in enumerate(data["constraints"]):
            if constraint.get("sign") not in allowed:
                errors.append(
                    f"La restricción #{i+1} debe ser de tipo {', '.join(allowed)} para el método {method.capitalize()}."
                )
    return errors

def validate_transport_problem(data):
    errors = []
    if "supply" not in data or not isinstance(data["supply"], list):
        errors.append("Missing or invalid 'supply' field.")
    if "demand" not in data or not isinstance(data["demand"], list):
        errors.append("Missing or invalid 'demand' field.")
    if "cost_matrix" not in data or not isinstance(data["cost_matrix"], list):
        errors.append("Missing or invalid 'cost_matrix' field.")
    
    return errors if errors else None
