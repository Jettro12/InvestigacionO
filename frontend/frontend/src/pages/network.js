"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { solveNetwork } from "../services/networkService";
import "bootstrap/dist/css/bootstrap.min.css";
import { Modal, Spinner, Badge } from "react-bootstrap";
import styles from "./modules.module.css";

export default function NetworkPage({ onResult, isModule }) {
  const [graph, setGraph] = useState([]);
  const [solution, setSolution] = useState(null);
  const [edgeData, setEdgeData] = useState({
    from: "",
    to: "",
    weight: "",
    capacity: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const addEdge = () => {
    if (!edgeData.from || !edgeData.to) return;
    setGraph([
      ...graph,
      [
        edgeData.from.toUpperCase(),
        edgeData.to.toUpperCase(),
        parseFloat(edgeData.weight || 0),
        parseFloat(edgeData.capacity || 0),
      ],
    ]);
    setEdgeData({ from: "", to: "", weight: "", capacity: "" });
    setSolution(null); // Limpiar resultados previos al cambiar el grafo
  };

  const removeEdge = (index) => {
    setGraph(graph.filter((_, i) => i !== index));
    setSolution(null);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const result = await solveNetwork({ graph });
      setSolution(result);

      if (onResult) {
        onResult({
          flujoTotal: result.max_flow?.max_flow || 0,
          analisisResumen: result.max_flow
            ? `Flujo máximo de la red: ${result.max_flow.max_flow} unidades.`
            : "Red optimizada.",
          raw: result,
        });
      }
    } catch (err) {
      console.error("Error al resolver la red:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.moduleContainer}>
      {/* Header adaptable */}
      {!isModule && (
        <div className={styles.headerSection}>
          <div className="d-flex justify-content-between align-items-center p-4 text-white">
            <h1 className={styles.moduleTitle}>🌐 Optimización en Redes</h1>
            <button
              onClick={() => router.push("/")}
              className="btn btn-outline-light"
            >
              Regresar
            </button>
          </div>
        </div>
      )}

      <div className="container py-4">
        <div className="row g-3">
          {/* Formulario de Entrada */}
          <div className="col-md-5">
            <div className="card shadow-sm p-4 border-0">
              <h6 className="text-primary fw-bold mb-3">🛠️ Nueva Conexión</h6>
              <div className="row g-2">
                <div className="col-6">
                  <input
                    placeholder="Origen"
                    className="form-control"
                    value={edgeData.from}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, from: e.target.value })
                    }
                  />
                </div>
                <div className="col-6">
                  <input
                    placeholder="Destino"
                    className="form-control"
                    value={edgeData.to}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, to: e.target.value })
                    }
                  />
                </div>
                <div className="col-6">
                  <input
                    placeholder="Costo"
                    type="number"
                    className="form-control"
                    value={edgeData.weight}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, weight: e.target.value })
                    }
                  />
                </div>
                <div className="col-6">
                  <input
                    placeholder="Capacidad"
                    type="number"
                    className="form-control"
                    value={edgeData.capacity}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, capacity: e.target.value })
                    }
                  />
                </div>
              </div>
              <button
                className="btn btn-primary w-100 mt-3 fw-bold"
                onClick={addEdge}
              >
                Agregar Arista
              </button>
            </div>
          </div>

          {/* Listado de Aristas / Grafo */}
          <div className="col-md-7">
            <div
              className="card shadow-sm p-4 border-0"
              style={{ minHeight: "220px" }}
            >
              <h6 className="fw-bold mb-3">📌 Estructura de la Red</h6>
              <div className="d-flex flex-wrap gap-2 mb-4">
                {graph.map((e, i) => (
                  <Badge key={i} bg="light" text="dark" className="border p-2">
                    <span className="text-primary">{e[0]}</span> →{" "}
                    <span className="text-success">{e[1]}</span>
                    <span className="ms-2 text-muted small">
                      (W:{e[2]} C:{e[3]})
                    </span>
                    <span
                      className="ms-2 text-danger"
                      style={{ cursor: "pointer" }}
                      onClick={() => removeEdge(i)}
                    >
                      {" "}
                      ×{" "}
                    </span>
                  </Badge>
                ))}
                {graph.length === 0 && (
                  <p className="text-muted small italic">
                    No hay conexiones definidas.
                  </p>
                )}
              </div>
              <button
                className="btn btn-success mt-auto fw-bold py-2 shadow-sm"
                onClick={handleSubmit}
                disabled={isLoading || graph.length === 0}
              >
                {isLoading ? (
                  <Spinner size="sm" className="me-2" />
                ) : (
                  "🚀 Calcular Optimización"
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Sección de Resultados */}
        {solution && (
          <div className="mt-4 animate__animated animate__fadeIn">
            {/* Mostrar Flujo Máximo si existe en la respuesta */}
            {solution.max_flow && (
              <div className="alert alert-info shadow-sm text-center py-3">
                <h4 className="mb-0 fw-bold">
                  Flujo Máximo Detectado: {solution.max_flow.max_flow ?? "0"}
                </h4>
              </div>
            )}

            {/* ANÁLISIS DE SENSIBILIDAD INDIVIDUAL (IA) */}
            {(solution.shortest_path?.sensitivity_analysis_gemini ||
              solution.intelligent_analysis) && (
              <div className="card border-0 shadow-sm mt-4 bg-light">
                <div className="card-body">
                  <h5 className="text-primary fw-bold mb-3 d-flex align-items-center">
                    <span className="me-2">🤖</span> Análisis de Sensibilidad de
                    Red
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
                    {solution.shortest_path?.sensitivity_analysis_gemini ||
                      solution.intelligent_analysis}
                  </div>
                </div>
              </div>
            )}

            {/* Imagen del Grafo si el backend la genera */}
            {solution.shortest_path?.graph_image && (
              <div className="text-center mt-4 card p-3 border-0 shadow-sm">
                <h6 className="fw-bold mb-3 text-muted text-uppercase small">
                  Visualización de la Red Optimizada
                </h6>
                <img
                  src={`data:image/png;base64,${solution.shortest_path.graph_image}`}
                  alt="Grafo optimizado"
                  className="img-fluid rounded"
                  style={{ maxHeight: "400px", objectFit: "contain" }}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
