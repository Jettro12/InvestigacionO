"use client";
import React, { useState } from "react";
import { solveLinear } from "../services/linearService";
import Image from "next/image";
import { useRouter } from "next/navigation";
import "bootstrap/dist/css/bootstrap.min.css";
import { Modal, Spinner } from "react-bootstrap";
import styles from "./modules.module.css";

export default function LinearPage() {
  const [method, setMethod] = useState("simplex");
  const [objective, setObjective] = useState("max");
  const [numVariables, setNumVariables] = useState(2);
  const [numConstraints, setNumConstraints] = useState(2);
  const [modelGenerated, setModelGenerated] = useState(false);
  const [objectiveCoeffs, setObjectiveCoeffs] = useState([]);
  const [constraints, setConstraints] = useState([]);
  const [solution, setSolution] = useState(null);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const router = useRouter();

  const validateForm = () => {
    const errors = {};
    if (objectiveCoeffs.length === 0) {
      errors.objective = "Debe generar el modelo primero";
    } else if (
      objectiveCoeffs.some((coeff) => coeff === "" || coeff === null)
    ) {
      errors.objective =
        "Complete todos los coeficientes de la función objetivo";
    }

    if (constraints.length === 0) {
      errors.constraints = "Debe generar el modelo primero";
    } else {
      constraints.forEach((constraint, index) => {
        if (constraint.coeffs.some((coeff) => coeff === "" || coeff === null)) {
          errors.constraints = `Complete los coeficientes de la restricción ${index + 1}`;
        }
        if (constraint.rhs === "" || constraint.rhs === null) {
          errors.constraints = `Complete el valor (RHS) de la restricción ${index + 1}`;
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
    setError(null);
    setValidationErrors({});
  };

  const clearForm = () => {
    setMethod("simplex");
    setObjective("max");
    setNumVariables(2);
    setNumConstraints(2);
    setObjectiveCoeffs([]);
    setConstraints([]);
    setModelGenerated(false);
    setSolution(null);
    setError(null);
    setValidationErrors({});
  };

  const handleObjectiveCoeffChange = (index, value) => {
    const newCoeffs = [...objectiveCoeffs];
    newCoeffs[index] = value;
    setObjectiveCoeffs(newCoeffs);
  };

  const handleConstraintCoeffChange = (row, col, value) => {
    const newConstraints = [...constraints];
    newConstraints[row].coeffs[col] = value;
    setConstraints(newConstraints);
  };

  const handleConstraintSignChange = (row, value) => {
    const newConstraints = [...constraints];
    newConstraints[row].sign = value;
    setConstraints(newConstraints);
  };

  const handleConstraintRHSChange = (row, value) => {
    const newConstraints = [...constraints];
    newConstraints[row].rhs = value;
    setConstraints(newConstraints);
  };

  const solveProblem = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);

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

    try {
      const result = await solveLinear(requestData);
      setSolution(result);
    } catch (err) {
      setError(err.message || "Error al conectar con el backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const getMethodName = (m) => {
    const names = {
      simplex: "Simplex",
      two_phase: "Dos Fases",
      m_big: "Gran M",
      dual: "Dual",
      graphical: "Gráfico",
    };
    return names[m] || m;
  };

  return (
    <div className={styles.moduleContainer}>
      <div className={styles.headerSection}>
        <div className={styles.headerContent}>
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <div>
              <h1 className={styles.moduleTitle}>📈 Programación Lineal</h1>
              <p className={styles.moduleSubtitle}>
                Optimización avanzada para Ingeniería de Sistemas.
              </p>
            </div>
            <button
              onClick={() => router.push("/")}
              className="btn btn-outline-light"
            >
              ← Regresar
            </button>
          </div>
        </div>
      </div>

      <div className={styles.mainContent + " container py-4"}>
        {/* Configuración */}
        <div className="card shadow-sm p-4 mb-4">
          <h2 className="h4 mb-4">⚙️ Configuración del Modelo</h2>
          <div className="row g-3">
            <div className="col-md-3">
              <label className="form-label fw-bold">Método</label>
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
              <label className="form-label fw-bold">Objetivo</label>
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
              <label className="form-label fw-bold">Variables</label>
              <input
                type="number"
                className="form-control"
                value={numVariables}
                onChange={(e) => setNumVariables(e.target.value)}
                min="1"
                max="10"
              />
            </div>
            <div className="col-md-3">
              <label className="form-label fw-bold">Restricciones</label>
              <input
                type="number"
                className="form-control"
                value={numConstraints}
                onChange={(e) => setNumConstraints(e.target.value)}
                min="1"
                max="10"
              />
            </div>
          </div>
          <div className="row mt-4">
            <div className="col-md-6">
              <button className="btn btn-primary w-100" onClick={generateModel}>
                Generar Modelo
              </button>
            </div>
            <div className="col-md-6">
              <button
                className="btn btn-outline-secondary w-100"
                onClick={clearForm}
              >
                Limpiar
              </button>
            </div>
          </div>
        </div>

        {modelGenerated && (
          <>
            {/* Función Objetivo */}
            <div className="card shadow-sm p-4 mb-4">
              <h4 className="fw-bold mb-3">🎯 Función Objetivo</h4>
              <div className="d-flex align-items-center gap-2 mb-3 bg-light p-2 rounded">
                <span className="fw-bold">Z = </span>
                {objectiveCoeffs.map((coef, i) => (
                  <span key={i}>
                    {i > 0 && Number(coef) >= 0 ? "+ " : ""}
                    {coef || 0}x<sub>{i + 1}</sub>{" "}
                  </span>
                ))}
              </div>
              <div className="row g-2">
                {objectiveCoeffs.map((coef, i) => (
                  <div key={i} className="col-md-2">
                    <input
                      type="number"
                      className="form-control"
                      placeholder={`x${i + 1}`}
                      value={coef}
                      onChange={(e) =>
                        handleObjectiveCoeffChange(i, e.target.value)
                      }
                    />
                  </div>
                ))}
              </div>
              {validationErrors.objective && (
                <div className="text-danger mt-2 small">
                  {validationErrors.objective}
                </div>
              )}
            </div>

            {/* Restricciones */}
            <div className="card shadow-sm p-4 mb-4">
              <h4 className="fw-bold mb-3">🔗 Restricciones</h4>
              {constraints.map((row, i) => (
                <div key={i} className="row g-2 mb-3 align-items-center">
                  <div className="col-auto fw-bold">{i + 1}.</div>
                  {row.coeffs.map((coef, j) => (
                    <div key={j} className="col">
                      <input
                        type="number"
                        className="form-control"
                        placeholder={`x${j + 1}`}
                        value={coef}
                        onChange={(e) =>
                          handleConstraintCoeffChange(i, j, e.target.value)
                        }
                      />
                    </div>
                  ))}
                  <div className="col-md-2">
                    <select
                      className="form-select"
                      value={row.sign}
                      onChange={(e) =>
                        handleConstraintSignChange(i, e.target.value)
                      }
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
                      onChange={(e) =>
                        handleConstraintRHSChange(i, e.target.value)
                      }
                    />
                  </div>
                </div>
              ))}
              {validationErrors.constraints && (
                <div className="text-danger small">
                  {validationErrors.constraints}
                </div>
              )}
            </div>

            <div className="text-center mb-5">
              <button
                className="btn btn-success btn-lg px-5"
                onClick={solveProblem}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Spinner size="sm" />
                ) : (
                  `Resolver con ${getMethodName(method)}`
                )}
              </button>
            </div>
          </>
        )}

        {/* Resultados */}
        {solution?.solution && (
          <div className="card shadow-lg p-4 border-success">
            <h3 className="text-success mb-4">
              ✅ Resultado: {solution.solution.status}
            </h3>
            <div className="row text-center mb-4">
              <div className="col-md-6 border-end">
                <h5>Valor Óptimo (Z)</h5>
                <div className="display-6 fw-bold">
                  {solution.solution.objective_value?.toFixed(4)}
                </div>
              </div>
              <div className="col-md-6">
                <h5>Variables de Decisión</h5>
                <div className="d-flex justify-content-center gap-3 flex-wrap">
                  {Object.entries(solution.solution.variable_values).map(
                    ([k, v]) => (
                      <div key={k} className="badge bg-primary fs-6">
                        {k} = {v.toFixed(2)}
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>

            {solution.solution.graph && (
              <div className="text-center mt-4">
                <h5>Representación Gráfica</h5>
                <img
                  src={`http://127.0.0.1:8000${solution.solution.graph}`}
                  alt="Gráfico"
                  className="img-fluid rounded shadow-sm cursor-pointer"
                  style={{ maxHeight: "300px", cursor: "zoom-in" }}
                  onClick={() => setShowModal(true)}
                />
              </div>
            )}

            {/* Análisis Inteligente con IA */}
            {solution.intelligent_analysis && (
              <div
                className="card border-0 shadow-lg p-4 bg-gradient mt-4"
                style={{
                  background:
                    "linear-gradient(135deg, #f5f7fa 0%, #e8eef7 100%)",
                }}
              >
                <h5 className="mb-4">
                  🤖 Análisis de Sensibilidad e Interpretación
                </h5>

                {/* Variables críticas destacadas */}
                {solution.sensitivity &&
                  Object.entries(solution.sensitivity).length > 0 && (
                    <div className="row mb-4">
                      <div className="col-12">
                        <h6 className="text-muted mb-3">
                          📊 Variables Críticas
                        </h6>
                        <div className="d-flex gap-2 flex-wrap">
                          {Object.entries(solution.sensitivity).map(
                            ([varName, sensValue]) => (
                              <div
                                key={varName}
                                className="badge bg-primary fs-6 p-3"
                              >
                                <span className="fw-bold">{varName}</span>
                                <br />
                                <small>
                                  Sensibilidad: {sensValue.toFixed(4)}
                                </small>
                              </div>
                            ),
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                {/* Análisis de texto con resaltes visuales */}
                <div
                  className="p-4 bg-white rounded"
                  style={{ lineHeight: "1.8" }}
                >
                  {typeof solution.intelligent_analysis === "string"
                    ? solution.intelligent_analysis
                        .split("\n")
                        .filter((line) => line.trim())
                        .map((line, idx) => {
                          let bgColor = "";
                          let borderColor = "";
                          let icon = "";

                          if (line.includes("[CRÍTICO]")) {
                            bgColor = "#fff5f5";
                            borderColor = "#dc3545";
                            icon = "🔴";
                          } else if (line.includes("[RECOMENDACIÓN]")) {
                            bgColor = "#f0fdf4";
                            borderColor = "#28a745";
                            icon = "✅";
                          } else if (line.includes("[RIESGO]")) {
                            bgColor = "#fffbf0";
                            borderColor = "#ffc107";
                            icon = "⚠️";
                          }

                          return (
                            <div
                              key={idx}
                              className="mb-3 p-3 rounded"
                              style={{
                                backgroundColor: bgColor || "transparent",
                                borderLeft: borderColor
                                  ? `4px solid ${borderColor}`
                                  : "none",
                              }}
                            >
                              <p className="mb-0 text-secondary">
                                {icon && (
                                  <span className="me-2 fw-bold">{icon}</span>
                                )}
                                {line.replace(
                                  /\[(CRÍTICO|RECOMENDACIÓN|RIESGO)\]/g,
                                  "",
                                )}
                              </p>
                            </div>
                          );
                        })
                    : solution.intelligent_analysis}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal Gráfico */}
      <Modal
        show={showModal}
        onHide={() => setShowModal(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Visualización del Problema</Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center">
          {solution?.solution?.graph && (
            <img
              src={`http://127.0.0.1:8000${solution.solution.graph}`}
              className="img-fluid"
              alt="Gráfico full"
            />
          )}
        </Modal.Body>
      </Modal>
    </div>
  );
}
