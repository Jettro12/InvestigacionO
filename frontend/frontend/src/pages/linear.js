"use client";
import React, { useState } from "react";
import { solveLinear } from "../services/linearService";
import { useRouter } from "next/navigation";
import "bootstrap/dist/css/bootstrap.min.css";
import { Spinner } from "react-bootstrap";
import styles from "./modules.module.css";

export default function LinearPage({ onResult, isModule }) {
  const [method, setMethod] = useState("simplex");
  const [objective, setObjective] = useState("max");
  const [numVariables, setNumVariables] = useState(2);
  const [numConstraints, setNumConstraints] = useState(2);
  const [modelGenerated, setModelGenerated] = useState(false);
  const [objectiveCoeffs, setObjectiveCoeffs] = useState([]);
  const [constraints, setConstraints] = useState([]);
  const [solution, setSolution] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const router = useRouter();

  // Helper para obtener valores de la solución en cualquier formato
  const getSolutionValue = (sol, path) => {
    if (!sol) return null;

    // Intenta acceso directo primero
    const directValue = sol[path];
    if (directValue !== undefined) return directValue;

    // Intenta acceso anidado en solution.solution
    if (sol.solution && sol.solution[path] !== undefined) {
      return sol.solution[path];
    }

    return null;
  };

  const validateForm = () => {
    const errors = {};
    if (objectiveCoeffs.length === 0) {
      errors.objective = "Debe generar el modelo primero";
    } else if (
      objectiveCoeffs.some((coeff) => coeff === "" || coeff === null)
    ) {
      errors.objective = "Complete todos los coeficientes";
    }
    if (constraints.length === 0) {
      errors.constraints = "Debe generar el modelo primero";
    } else {
      constraints.forEach((c, idx) => {
        if (c.coeffs.some((v) => v === "") || c.rhs === "") {
          errors.constraints = `Complete la restricción ${idx + 1}`;
        }
      });
    }
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const generateModel = () => {
    const n = Number(numVariables);
    const m = Number(numConstraints);
    setObjectiveCoeffs(new Array(n).fill(""));
    setConstraints(
      new Array(m).fill(null).map(() => ({
        coeffs: new Array(n).fill(""),
        sign: "<=",
        rhs: "",
      })),
    );
    setModelGenerated(true);
    setSolution(null);
  };

  const solveProblem = async () => {
    if (!validateForm()) return;
    setIsLoading(true);
    setError(null);
    setSolution(null);

    const requestData = {
      objective,
      variables: objectiveCoeffs.map((_, i) => `x${i + 1}`),
      objective_coeffs: objectiveCoeffs.map(Number),
      constraints: constraints.map((c) => ({
        coeffs: c.coeffs.map(Number),
        sign: c.sign,
        rhs: Number(c.rhs),
      })),
      method,
    };

    console.log("📤 Enviando al backend:", requestData);

    try {
      const result = await solveLinear(requestData);
      console.log("📥 Recibido del backend:", result);

      setSolution(result);

      if (onResult) {
        const objValue = getSolutionValue(result, "objective_value");
        const varValues = getSolutionValue(result, "variable_values");

        onResult({
          valorOptimo: objValue || 0,
          unidadesTotales: varValues
            ? Object.values(varValues).reduce((a, b) => a + b, 0)
            : 0,
          analisisResumen: `Z = ${objValue?.toFixed(2) ?? "N/A"}.`,
          raw: result,
        });
      }
    } catch (err) {
      console.error("❌ Error:", err);
      setError(err.message || "Error al conectar con el backend.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.moduleContainer}>
      {!isModule && (
        <div className={styles.headerSection}>
          <div className="d-flex justify-content-between align-items-center p-4">
            <h1 className={styles.moduleTitle}>📈 Programación Lineal</h1>
            <button
              onClick={() => router.push("/")}
              className="btn btn-outline-light"
            >
              ← Regresar
            </button>
          </div>
        </div>
      )}

      <div className="container py-4 text-dark">
        {/* CONFIGURACIÓN */}
        <div className="card shadow-sm p-4 mb-4">
          <h5 className="mb-3">⚙️ Configuración</h5>
          <div className="row g-3">
            <div className="col-md-3">
              <label className="form-label">Método</label>
              <select
                className="form-select"
                value={method}
                onChange={(e) => setMethod(e.target.value)}
              >
                <option value="simplex">Simplex</option>
                <option value="graphical">Gráfico</option>
                <option value="m_big">Gran M</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Objetivo</label>
              <select
                className="form-select"
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
              >
                <option value="max">Maximizar</option>
                <option value="min">Minimizar</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Variables</label>
              <input
                type="number"
                className="form-control"
                value={numVariables}
                onChange={(e) => setNumVariables(e.target.value)}
                disabled={method === "graphical"}
              />
              {method === "graphical" && (
                <small className="text-muted d-block">
                  Fijo en 2 variables
                </small>
              )}
            </div>
            <div className="col-md-3">
              <label className="form-label">Restricciones</label>
              <input
                type="number"
                className="form-control"
                value={numConstraints}
                onChange={(e) => setNumConstraints(e.target.value)}
              />
            </div>
          </div>
          <button
            className="btn btn-primary mt-3 w-100"
            onClick={generateModel}
          >
            Generar Modelo
          </button>
        </div>

        {modelGenerated && (
          <div className="card shadow-sm p-4 mb-4">
            <h5 className="mb-3">🎯 Definición de Coeficientes</h5>
            <div className="row g-2 mb-4">
              {objectiveCoeffs.map((coef, i) => (
                <div key={i} className="col-md-2">
                  <input
                    type="number"
                    className="form-control"
                    placeholder={`x${i + 1}`}
                    value={coef}
                    onChange={(e) => {
                      const next = [...objectiveCoeffs];
                      next[i] = e.target.value;
                      setObjectiveCoeffs(next);
                    }}
                  />
                </div>
              ))}
            </div>
            <h5 className="mb-3">🔗 Restricciones</h5>
            {constraints.map((row, i) => (
              <div key={i} className="row g-2 mb-2 align-items-center">
                {row.coeffs.map((coef, j) => (
                  <div key={j} className="col">
                    <input
                      type="number"
                      className="form-control"
                      value={coef}
                      onChange={(e) => {
                        const next = [...constraints];
                        next[i].coeffs[j] = e.target.value;
                        setConstraints(next);
                      }}
                    />
                  </div>
                ))}
                <div className="col-md-2">
                  <select
                    className="form-select"
                    value={row.sign}
                    onChange={(e) => {
                      const next = [...constraints];
                      next[i].sign = e.target.value;
                      setConstraints(next);
                    }}
                  >
                    <option value="<=">≤</option>
                    <option value=">=">≥</option>
                    <option value="=">=</option>
                  </select>
                </div>
                <div className="col-md-2">
                  <input
                    type="number"
                    className="form-control"
                    placeholder="RHS"
                    value={row.rhs}
                    onChange={(e) => {
                      const next = [...constraints];
                      next[i].rhs = e.target.value;
                      setConstraints(next);
                    }}
                  />
                </div>
              </div>
            ))}
            <button
              className="btn btn-success w-100 mt-4"
              onClick={solveProblem}
              disabled={isLoading}
            >
              {isLoading ? <Spinner size="sm" /> : "🚀 Calcular Optimización"}
            </button>
          </div>
        )}

        {/* RESULTADOS */}
        {solution && (
          <div className="mt-4 animate__animated animate__fadeIn">
            {/* Información de depuración - puedes comentar después */}
            <details className="mb-3">
              <summary>🔍 Ver datos recibidos (debug)</summary>
              <pre className="bg-dark text-light p-3 small">
                {JSON.stringify(solution, null, 2)}
              </pre>
            </details>

            <div className="alert alert-success shadow-sm">
              <h5>
                Resultado Óptimo Z:{" "}
                {(() => {
                  const objValue = getSolutionValue(
                    solution,
                    "objective_value",
                  );
                  return objValue?.toFixed(4) ?? "N/A";
                })()}
              </h5>
              <div className="d-flex gap-2 flex-wrap">
                {(() => {
                  const varValues = getSolutionValue(
                    solution,
                    "variable_values",
                  );
                  if (varValues && typeof varValues === "object") {
                    return Object.entries(varValues).map(([k, v]) => (
                      <span key={k} className="badge bg-primary fs-6">
                        {k} = {typeof v === "number" ? v.toFixed(2) : v}
                      </span>
                    ));
                  }
                  return null;
                })()}
              </div>
            </div>

            {/* ⭐ GRÁFICO */}
            {solution.graph_image && (
              <div className="card border-0 shadow-sm mt-4 text-center">
                <div className="card-header bg-white border-0">
                  <h5 className="text-primary fw-bold mb-0">
                    📊 Representación Gráfica
                  </h5>
                </div>
                <div className="card-body">
                  <img
                    src={solution.graph_image}
                    alt="Gráfico del método gráfico"
                    className="img-fluid rounded border"
                    style={{ maxHeight: "500px", maxWidth: "100%" }}
                    onError={(e) => {
                      console.error("Error cargando imagen");
                      e.target.style.display = "none";
                    }}
                  />
                </div>
              </div>
            )}

            {/* ⭐ ANÁLISIS IA */}
            {(solution.intelligent_analysis ||
              solution.sensitivity_analysis) && (
              <div className="card border-0 shadow-sm mt-4 bg-light">
                <div className="card-body">
                  <h5 className="text-primary fw-bold mb-3 d-flex align-items-center">
                    <span className="me-2">🤖</span> Análisis de Sensibilidad
                  </h5>
                  <div
                    className="p-3 bg-white rounded border shadow-inner"
                    style={{
                      whiteSpace: "pre-line",
                      fontSize: "14.5px",
                      lineHeight: "1.6",
                    }}
                  >
                    {solution.intelligent_analysis ||
                      solution.sensitivity_analysis}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {error && <div className="alert alert-danger mt-3">{error}</div>}
      </div>
    </div>
  );
}
