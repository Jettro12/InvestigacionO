"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { solveTransport } from "../services/transportService";
import "bootstrap/dist/css/bootstrap.min.css";
import { Spinner } from "react-bootstrap";
import styles from "./modules.module.css";

export default function TransportPage({ onResult, isModule }) {
  const [numSuppliers, setNumSuppliers] = useState(3);
  const [numDemands, setNumDemands] = useState(4);
  const [supply, setSupply] = useState(new Array(3).fill(""));
  const [demand, setDemand] = useState(new Array(4).fill(""));
  const [costs, setCosts] = useState(
    Array.from({ length: 3 }, () => new Array(4).fill("")),
  );
  const [method, setMethod] = useState("northwest");
  const [solution, setSolution] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleDimensionsChange = (ns, nd) => {
    setNumSuppliers(ns);
    setNumDemands(nd);
    setSupply(new Array(ns).fill(""));
    setDemand(new Array(nd).fill(""));
    setCosts(Array.from({ length: ns }, () => new Array(nd).fill("")));
    setSolution(null); // Limpiar solución previa al cambiar dimensiones
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    const requestData = {
      supply: supply.map(Number),
      demand: demand.map(Number),
      costs: costs.map((row) => row.map(Number)),
      method,
    };

    try {
      const result = await solveTransport(requestData);
      setSolution(result);
      if (onResult && result?.status === "success") {
        onResult({
          costoTotal: result.total_cost,
          capacidadTotal: supply.reduce((a, b) => a + Number(b), 0),
          analisisResumen: `Costo logístico: $${result.total_cost}.`,
          raw: result,
        });
      }
    } catch (err) {
      console.error("Error en la petición:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.moduleContainer}>
      {!isModule && (
        <div className={styles.headerSection}>
          <div className="d-flex justify-content-between align-items-center p-4 text-white">
            <h1>🚚 Transporte</h1>
            <button
              onClick={() => router.push("/")}
              className="btn btn-outline-light"
            >
              Volver
            </button>
          </div>
        </div>
      )}

      <div className="container py-4">
        <div className="card shadow-sm p-4 mb-4">
          <div className="row g-3">
            <div className="col-md-4">
              <label className="fw-bold">Orígenes</label>
              <input
                type="number"
                className="form-control"
                value={numSuppliers}
                onChange={(e) =>
                  handleDimensionsChange(Number(e.target.value), numDemands)
                }
              />
            </div>
            <div className="col-md-4">
              <label className="fw-bold">Destinos</label>
              <input
                type="number"
                className="form-control"
                value={numDemands}
                onChange={(e) =>
                  handleDimensionsChange(numSuppliers, Number(e.target.value))
                }
              />
            </div>
            <div className="col-md-4">
              <label className="fw-bold">Método</label>
              <select
                className="form-select"
                value={method}
                onChange={(e) => setMethod(e.target.value)}
              >
                <option value="northwest">Noroeste</option>
                <option value="minimum_cost">Costo Mínimo</option>
                <option value="vogel">Vogel</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card shadow-sm p-4 overflow-auto">
          <table className="table table-bordered">
            <thead className="table-dark text-center">
              <tr>
                <th>O \ D</th>
                {demand.map((_, j) => (
                  <th key={j}>D{j + 1}</th>
                ))}
                <th className="bg-success">Oferta</th>
              </tr>
            </thead>
            <tbody>
              {costs.map((row, i) => (
                <tr key={i}>
                  <td className="fw-bold bg-light text-center">O{i + 1}</td>
                  {row.map((cost, j) => (
                    <td key={j}>
                      <input
                        type="number"
                        className="form-control form-control-sm"
                        value={cost}
                        onChange={(e) => {
                          const next = [...costs];
                          next[i][j] = e.target.value;
                          setCosts(next);
                        }}
                      />
                    </td>
                  ))}
                  <td>
                    <input
                      type="number"
                      className="form-control border-success text-center"
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
                <td className="bg-danger text-white fw-bold text-center">
                  Demanda
                </td>
                {demand.map((val, j) => (
                  <td key={j}>
                    <input
                      type="number"
                      className="form-control border-danger text-center"
                      value={val}
                      onChange={(e) => {
                        const next = [...demand];
                        next[j] = e.target.value;
                        setDemand(next);
                      }}
                    />
                  </td>
                ))}
                <td className="text-center fw-bold bg-light">Σ</td>
              </tr>
            </tbody>
          </table>
          <button
            className="btn btn-primary w-100 fw-bold shadow-sm"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? <Spinner size="sm" /> : "🚀 Calcular Transporte"}
          </button>
        </div>

        {solution && (
          <div className="mt-4 animate__animated animate__fadeIn">
            <div className="p-3 bg-primary text-white rounded shadow-sm text-center mb-4">
              <h3 className="mb-0 fw-bold">
                {/* SOLUCIÓN AL ERROR: Uso de opcional chaining ?. y fallback a "0" */}
                Costo Óptimo: ${solution.total_cost?.toLocaleString() ?? "0"}
              </h3>
            </div>

            {(solution.sensitivity_analysis ||
              solution.intelligent_analysis) && (
              <div className="card border-0 shadow-sm mt-4 bg-light">
                <div className="card-body">
                  <h5 className="text-primary fw-bold mb-3 d-flex align-items-center">
                    <span className="me-2">🤖</span> Análisis de Sensibilidad e
                    Interpretación
                  </h5>
                  <div
                    className="p-3 bg-white rounded border shadow-inner"
                    style={{
                      whiteSpace: "pre-line",
                      fontSize: "14.5px",
                      lineHeight: "1.6",
                      color: "#333",
                    }}
                  >
                    {solution.sensitivity_analysis ||
                      solution.intelligent_analysis}
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
