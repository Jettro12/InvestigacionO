"use client";

import React, { useState } from "react";

import { solveLinear } from "../services/linearService";

import { useRouter } from "next/navigation";

import "bootstrap/dist/css/bootstrap.min.css";

import { Spinner } from "react-bootstrap";

import styles from "./modules.module.css";

import ReactMarkdown from "react-markdown";

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

  const router = useRouter();

  const getSolutionValue = (sol, path) => {
    if (!sol) return null;

    if (sol[path] !== undefined) return sol[path];

    if (sol.solution && sol.solution[path] !== undefined)
      return sol.solution[path];

    return null;
  };

  const fmt = (num) =>
    num !== undefined && num !== null ? Number(num).toFixed(4) : "0.0000";

  const generateModel = () => {
    const n = Number(numVariables);

    const m = Number(numConstraints);

    setObjectiveCoeffs(new Array(n).fill(""));

    setConstraints(
      new Array(m)

        .fill(null)

        .map(() => ({ coeffs: new Array(n).fill(""), sign: "<=", rhs: "" })),
    );

    setModelGenerated(true);

    setSolution(null);
  };

  const solveProblem = async () => {
    setIsLoading(true);

    setError(null);

    setSolution(null);

    if (
      objectiveCoeffs.some((c) => c === "") ||
      constraints.some(
        (row) => row.rhs === "" || row.coeffs.some((c) => c === ""),
      )
    ) {
      setError("Completa todos los campos.");

      setIsLoading(false);

      return;
    }

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

      if (
        result.status === "error" ||
        result.status === "Unbounded" ||
        result.status === "infeasible"
      ) {
        setError(result.message || `Error: ${result.status}`);

        setSolution(null);
      } else {
        setSolution(result);
      }
    } catch (err) {
      setError(err.message);
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
                <option value="simplex">Simplex Estándar</option>

                <option value="graphical">Método Gráfico</option>

                <option value="m_big">Gran M</option>

                <option value="two_phase">Dos Fases</option>
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
                min="2"
              />
            </div>

            <div className="col-md-3">
              <label className="form-label">Restricciones</label>

              <input
                type="number"
                className="form-control"
                value={numConstraints}
                onChange={(e) => setNumConstraints(e.target.value)}
                min="1"
              />
            </div>
          </div>

          <button
            className="btn btn-primary mt-3 w-100"
            onClick={generateModel}
          >
            Generar Tabla
          </button>
        </div>

        {modelGenerated && (
          <div className="card shadow-sm p-4 mb-4">
            <h5 className="mb-3">Función Objetivo</h5>

            <div className="row g-2 mb-4 align-items-center">
              <div className="col-auto">
                <span className="fw-bold">
                  {objective === "max" ? "Max" : "Min"} Z ={" "}
                </span>
              </div>

              {objectiveCoeffs.map((coef, i) => (
                <div key={i} className="col-md-2 d-flex align-items-center">
                  <input
                    type="number"
                    className="form-control me-1"
                    placeholder={`c${i + 1}`}
                    value={coef}
                    onChange={(e) => {
                      const next = [...objectiveCoeffs];

                      next[i] = e.target.value;

                      setObjectiveCoeffs(next);
                    }}
                  />

                  <label>x{i + 1}</label>
                </div>
              ))}
            </div>

            <h5 className="mb-3">Restricciones</h5>

            {constraints.map((row, i) => (
              <div key={i} className="row g-2 mb-2 align-items-center">
                {row.coeffs.map((coef, j) => (
                  <div key={j} className="col d-flex align-items-center">
                    <input
                      type="number"
                      className="form-control me-1"
                      value={coef}
                      onChange={(e) => {
                        const next = [...constraints];

                        next[i].coeffs[j] = e.target.value;

                        setConstraints(next);
                      }}
                    />

                    <label>x{j + 1}</label>
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
                    <option value="<=">≤</option> <option value=">=">≥</option>{" "}
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
              {isLoading ? <Spinner size="sm" /> : "🚀 Calcular"}
            </button>
          </div>
        )}

        {error && <div className="alert alert-danger mt-3">{error}</div>}

        {/* RESULTADOS */}

        {solution && (
          <div className="mt-4 animate__animated animate__fadeInUp">
            {/* 1. Z OPTIMO */}

            <div className="card border-success shadow mb-4">
              <div className="card-header bg-success text-white">
                <h5 className="mb-0">
                  ✅ Z = {fmt(getSolutionValue(solution, "objective_value"))}
                </h5>
              </div>

              <div className="card-body">
                <div className="d-flex gap-3 flex-wrap">
                  {(() => {
                    const vars = getSolutionValue(solution, "variable_values");

                    return vars
                      ? Object.entries(vars).map(([k, v]) => (
                          <span
                            key={k}
                            className="badge bg-light text-dark border p-2"
                          >
                            {k} = {fmt(v)}
                          </span>
                        ))
                      : null;
                  })()}
                </div>
              </div>
            </div>

            {/* 2. TABLA PASO A PASO (NUEVO) */}

            {solution.steps && solution.steps.length > 0 && (
              <div className="card shadow-sm mb-4 border-0">
                <div className="card-header bg-dark text-white">
                  <h5 className="mb-0">🔄 Iteraciones Paso a Paso</h5>
                </div>

                <div
                  className="card-body bg-light p-2"
                  style={{ maxHeight: "600px", overflowY: "auto" }}
                >
                  {solution.steps.map((step, idx) => (
                    <div key={idx} className="card mb-4 border shadow-sm">
                      <div className="card-header bg-secondary text-white d-flex justify-content-between">
                        <span>{step.description}</span>

                        {step.pivot && (
                          <small>
                            Pivote en fila {step.pivot[0] + 1}, columna{" "}
                            {step.pivot[1] + 1}
                          </small>
                        )}
                      </div>

                      <div className="table-responsive">
                        <table
                          className="table table-bordered table-sm mb-0 text-center font-monospace"
                          style={{ fontSize: "0.9rem" }}
                        >
                          <thead className="table-light">
                            <tr>
                              <th className="bg-light">Base</th>

                              {step.headers.map((h, i) => (
                                <th key={i}>{h}</th>
                              ))}
                            </tr>
                          </thead>

                          <tbody>
                            {step.tableau.map((row, rIdx) => (
                              <tr
                                key={rIdx}
                                className={
                                  rIdx === step.tableau.length - 1
                                    ? "table-warning fw-bold"
                                    : ""
                                }
                              >
                                {/* Variable básica de esta fila (o Z) */}

                                <td className="fw-bold bg-light">
                                  {rIdx === step.tableau.length - 1
                                    ? "Z"
                                    : step.basic_vars[rIdx]}
                                </td>

                                {row.map((val, cIdx) => {
                                  // Highlight Pivot

                                  const isPivot =
                                    step.pivot &&
                                    step.pivot[0] === rIdx &&
                                    step.pivot[1] === cIdx;

                                  return (
                                    <td
                                      key={cIdx}
                                      className={
                                        isPivot
                                          ? "bg-warning text-dark fw-bold border border-dark"
                                          : ""
                                      }
                                    >
                                      {Number(val).toFixed(2)}
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 3. SENSIBILIDAD */}

            {/* 3. SENSIBILIDAD */}

            {solution.sensitivity_analysis &&
              Array.isArray(solution.sensitivity_analysis.variables) &&
              Array.isArray(solution.sensitivity_analysis.constraints) && (
                <div className="row g-4 mb-4">
                  <div className="col-md-6">
                    <div className="card h-100 shadow-sm">
                      <div className="card-header bg-primary text-white">
                        Variables
                      </div>

                      <table className="table table-sm mb-0 text-center">
                        <thead>
                          <tr>
                            <th>Var</th>
                            <th>Valor</th>
                            <th>Costo Red.</th>
                          </tr>
                        </thead>

                        <tbody>
                          {solution.sensitivity_analysis.variables.map(
                            (v, i) => (
                              <tr key={i}>
                                <td>{v.name}</td>
                                <td>{fmt(v.final_value)}</td>
                                <td>{fmt(v.reduced_cost)}</td>
                              </tr>
                            ),
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div className="col-md-6">
                    <div className="card h-100 shadow-sm">
                      <div className="card-header bg-warning text-dark">
                        Restricciones
                      </div>

                      <table className="table table-sm mb-0 text-center">
                        <thead>
                          <tr>
                            <th>#</th>
                            <th>Holgura</th>
                            <th>Dual</th>
                          </tr>
                        </thead>

                        <tbody>
                          {solution.sensitivity_analysis.constraints.map(
                            (c, i) => (
                              <tr key={i}>
                                <td>R{c.id}</td>
                                <td>{fmt(c.slack_value)}</td>
                                <td>{fmt(c.dual_price)}</td>
                              </tr>
                            ),
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

            {/* 4. GRÁFICO / IA */}

            {solution.graph_image && (
              <img
                src={solution.graph_image}
                className="img-fluid rounded border mb-4"
                alt="Graph"
              />
            )}

            {/* SECCIÓN DE RESULTADOS EN LinearPage.js */}

            {/* ... (tus tablas y gráfico anteriores) ... */}

            {/* 4. ANÁLISIS INTELIGENTE (IA) */}

            {solution.intelligent_analysis && (
              <div className="card border-0 shadow-sm mt-4">
                <div className="card-header bg-gradient bg-primary text-white">
                  <h5 className="mb-0 fw-bold">🤖 Informe de Consultoría IA</h5>
                </div>

                <div className="card-body bg-light">
                  <div
                    className="markdown-content text-dark"
                    style={{ lineHeight: "1.7", fontSize: "0.95rem" }}
                  >
                    <ReactMarkdown
                      components={{
                        h3: ({ node, ...props }) => (
                          <h4
                            className="text-primary mt-4 mb-3 fw-bold"
                            {...props}
                          />
                        ),

                        ul: ({ node, ...props }) => (
                          <ul
                            className="list-group list-group-flush bg-transparent mb-3"
                            {...props}
                          />
                        ),

                        li: ({ node, ...props }) => (
                          <li
                            className="list-group-item bg-transparent border-0 py-1 ps-0"
                            {...props}
                          >
                            <span className="me-2">•</span>

                            {props.children}
                          </li>
                        ),

                        strong: ({ node, ...props }) => (
                          <span className="fw-bold text-dark" {...props} />
                        ),
                      }}
                    >
                      {solution.intelligent_analysis}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
