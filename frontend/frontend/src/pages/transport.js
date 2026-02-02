"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { solveTransport } from "../services/transportService";
import "bootstrap/dist/css/bootstrap.min.css";
import { Modal, Spinner } from "react-bootstrap";
import styles from "./modules.module.css";

export default function TransportPage() {
  const [numSuppliers, setNumSuppliers] = useState(3);
  const [numDemands, setNumDemands] = useState(4);
  const [supply, setSupply] = useState(new Array(3).fill(""));
  const [demand, setDemand] = useState(new Array(4).fill(""));
  const [costs, setCosts] = useState(
    Array.from({ length: 3 }, () => new Array(4).fill("")),
  );
  const [method, setMethod] = useState("northwest");
  const [solution, setSolution] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const router = useRouter();

  // Actualizar dimensiones globalmente
  const handleDimensionsChange = (newSuppliers, newDemands) => {
    setNumSuppliers(newSuppliers);
    setNumDemands(newDemands);
    setSupply(new Array(newSuppliers).fill(""));
    setDemand(new Array(newDemands).fill(""));
    setCosts(
      Array.from({ length: newSuppliers }, () =>
        new Array(newDemands).fill(""),
      ),
    );
    setValidationErrors({});
    setSolution(null);
  };

  const validateForm = () => {
    const errors = {};
    if (supply.some((val) => val === "" || Number(val) < 0))
      errors.supply = "La oferta no puede estar vacía o ser negativa";
    if (demand.some((val) => val === "" || Number(val) < 0))
      errors.demand = "La demanda no puede estar vacía o ser negativa";
    if (
      costs.some((row) => row.some((cost) => cost === "" || Number(cost) < 0))
    )
      errors.costs = "Todos los costos son requeridos";

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCostChange = (i, j, value) => {
    const newCosts = costs.map((row, rowIndex) =>
      rowIndex === i
        ? row.map((col, colIndex) => (colIndex === j ? value : col))
        : row,
    );
    setCosts(newCosts);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);

    try {
      const requestData = {
        supply: supply.map(Number),
        demand: demand.map(Number),
        costs: costs.map((row) => row.map(Number)),
        method,
      };
      const result = await solveTransport(requestData);
      setSolution(result);
    } catch (err) {
      setError(err.message || "Error al procesar el modelo.");
    } finally {
      setIsLoading(false);
    }
  };

  const renderMatrixTable = (matrix, title, color = "primary") => (
    <div className="card mb-4 shadow-sm border-0">
      <div className={`card-header bg-${color} text-white fw-bold`}>
        {title}
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-sm table-bordered">
            <thead>
              <tr className="bg-light text-center">
                <th>Origen \ Destino</th>
                {matrix[0].map((_, j) => (
                  <th key={j}>D{j + 1}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.map((row, i) => (
                <tr key={i}>
                  <td className="fw-bold bg-light text-center">O{i + 1}</td>
                  {row.map((cell, j) => (
                    <td key={j} className="text-center">
                      {cell > 0 ? (
                        <span className="badge bg-success px-3">{cell}</span>
                      ) : (
                        <span className="text-muted">0</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const totalSupply = supply.reduce((sum, val) => sum + (Number(val) || 0), 0);
  const totalDemand = demand.reduce((sum, val) => sum + (Number(val) || 0), 0);

  return (
    <div className={styles.moduleContainer}>
      <div className={styles.headerSection}>
        <div
          className={
            styles.headerContent +
            " d-flex justify-content-between align-items-center"
          }
        >
          <div>
            <h1 className={styles.moduleTitle}>🚚 Problema de Transporte</h1>
            <p className={styles.moduleSubtitle}>
              Métodos Esquina Noroeste, Costo Mínimo y Vogel
            </p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="btn btn-outline-light"
          >
            Volver
          </button>
        </div>
      </div>

      <div className="container py-4">
        <div className="card shadow-sm p-4 mb-4 border-0">
          <h4 className="mb-4">⚙️ Configuración</h4>
          <div className="row g-3">
            <div className="col-md-4">
              <label className="form-label fw-bold">Cant. Orígenes</label>
              <input
                type="number"
                className="form-control"
                value={numSuppliers}
                onChange={(e) =>
                  handleDimensionsChange(Number(e.target.value), numDemands)
                }
                min="1"
                max="10"
              />
            </div>
            <div className="col-md-4">
              <label className="form-label fw-bold">Cant. Destinos</label>
              <input
                type="number"
                className="form-control"
                value={numDemands}
                onChange={(e) =>
                  handleDimensionsChange(numSuppliers, Number(e.target.value))
                }
                min="1"
                max="10"
              />
            </div>
            <div className="col-md-4">
              <label className="form-label fw-bold">Método Inicial</label>
              <select
                className="form-select"
                value={method}
                onChange={(e) => setMethod(e.target.value)}
              >
                <option value="northwest">Esquina Noroeste</option>
                <option value="minimum_cost">Costo Mínimo</option>
                <option value="vogel">Vogel (Penalizaciones)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card shadow-sm p-4 mb-4 border-0">
          <h4 className="text-primary mb-3">📋 Matriz de Costos y Balance</h4>
          <div className="table-responsive">
            <table className="table table-bordered">
              <thead className="table-dark text-center">
                <tr>
                  <th>Origen / Destino</th>
                  {demand.map((_, j) => (
                    <th key={j}>Destino {j + 1}</th>
                  ))}
                  <th className="bg-success text-white">Oferta</th>
                </tr>
              </thead>
              <tbody>
                {costs.map((row, i) => (
                  <tr key={i}>
                    <td className="fw-bold bg-light">Origen {i + 1}</td>
                    {row.map((cost, j) => (
                      <td key={j}>
                        <input
                          type="number"
                          className="form-control form-control-sm"
                          value={cost}
                          onChange={(e) =>
                            handleCostChange(i, j, e.target.value)
                          }
                        />
                      </td>
                    ))}
                    <td>
                      <input
                        type="number"
                        className="form-control form-control-sm border-success"
                        value={supply[i]}
                        onChange={(e) => {
                          const next = [...supply];
                          next[i] = e.target.value;
                          setSupply(next);
                        }}
                      />
                    </td>
                  </tr>
                ))}
                <tr>
                  <td className="fw-bold bg-danger text-white">Demanda</td>
                  {demand.map((val, j) => (
                    <td key={j}>
                      <input
                        type="number"
                        className="form-control form-control-sm border-danger"
                        value={val}
                        onChange={(e) => {
                          const next = [...demand];
                          next[j] = e.target.value;
                          setDemand(next);
                        }}
                      />
                    </td>
                  ))}
                  <td
                    className={`fw-bold text-center ${totalSupply === totalDemand ? "text-success" : "text-warning"}`}
                  >
                    {totalSupply} / {totalDemand}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {totalSupply !== totalDemand && (
            <div className="alert alert-info mt-3 small">
              ℹ️ <strong>Problema no balanceado:</strong> El algoritmo añadirá
              automáticamente un nodo ficticio para equilibrar la oferta y
              demanda.
            </div>
          )}

          <div className="text-center mt-4">
            <button
              className="btn btn-primary btn-lg px-5"
              onClick={handleSubmit}
              disabled={isLoading}
            >
              {isLoading ? (
                <Spinner size="sm" className="me-2" />
              ) : (
                "🚀 Calcular Optimización"
              )}
            </button>
          </div>
        </div>

        {error && <div className="alert alert-danger shadow-sm">{error}</div>}

        {solution && (
          <div className="fade-in">
            <div className="row g-3 mb-4">
              <div className="col-md-6">
                <div className="card border-0 shadow-sm bg-light p-3 text-center">
                  <span className="text-muted">Costo Inicial</span>
                  <h3 className="fw-bold text-warning">
                    ${solution.initial_cost?.toLocaleString()}
                  </h3>
                </div>
              </div>
              <div className="col-md-6">
                <div className="card border-0 shadow-sm bg-primary text-white p-3 text-center">
                  <span className="opacity-75">Costo Óptimo Final</span>
                  <h3 className="fw-bold">
                    ${solution.total_cost?.toLocaleString()}
                  </h3>
                </div>
              </div>
            </div>

            {renderMatrixTable(
              solution.optimal_solution,
              "🏆 Asignación Óptima de Recursos (Matriz de Flujos)",
              "success",
            )}

            {solution.sensitivity_analysis && (
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

                {/* Información del costo */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <div className="p-3 bg-warning text-dark rounded">
                      <small className="text-muted">Costo Inicial</small>
                      <h6 className="fw-bold mb-0">
                        ${solution.initial_cost?.toLocaleString()}
                      </h6>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="p-3 bg-success text-white rounded">
                      <small>Costo Óptimo</small>
                      <h6 className="fw-bold mb-0">
                        ${solution.total_cost?.toLocaleString()}
                      </h6>
                    </div>
                  </div>
                </div>

                {/* Análisis de texto con resaltes visuales */}
                <div
                  className="p-4 bg-white rounded"
                  style={{ lineHeight: "1.8" }}
                >
                  {typeof solution.sensitivity_analysis === "string"
                    ? solution.sensitivity_analysis
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
                    : solution.sensitivity_analysis}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
