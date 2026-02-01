"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { solveNetwork } from "../services/networkService";
import "bootstrap/dist/css/bootstrap.min.css";
import { Modal, Spinner, Badge } from "react-bootstrap";
import styles from "./modules.module.css";

export default function NetworkPage() {
  const [graph, setGraph] = useState([]);
  const [solution, setSolution] = useState(null);
  const [edgeData, setEdgeData] = useState({
    from: "",
    to: "",
    weight: "",
    capacity: "",
  });
  const [selectedImage, setSelectedImage] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const router = useRouter();

  const validateForm = () => {
    const errors = {};
    const nodes = new Set(graph.flatMap(([u, v]) => [u, v]));

    if (graph.length === 0) errors.graph = "Agregue al menos una arista.";
    else if (nodes.size < 2)
      errors.graph = "Se requieren al menos 2 nodos distintos.";

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const addEdge = () => {
    const { from, to, weight, capacity } = edgeData;
    const cleanFrom = from.trim().toUpperCase();
    const cleanTo = to.trim().toUpperCase();

    if (!cleanFrom || !cleanTo || weight === "" || capacity === "") {
      setValidationErrors({ edge: "Todos los campos son obligatorios" });
      return;
    }

    if (cleanFrom === cleanTo) {
      setValidationErrors({ edge: "No se permiten bucles (Origen = Destino)" });
      return;
    }

    // Evitar duplicados
    if (graph.some(([u, v]) => u === cleanFrom && v === cleanTo)) {
      setValidationErrors({ edge: "Esta conexión ya existe" });
      return;
    }

    setGraph([
      ...graph,
      [cleanFrom, cleanTo, parseFloat(weight), parseFloat(capacity)],
    ]);
    setEdgeData({ from: "", to: "", weight: "", capacity: "" });
    setValidationErrors({});
  };

  const removeEdge = (index) => {
    setGraph(graph.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const result = await solveNetwork({ graph });
      setSolution(result);
      setValidationErrors({});
    } catch (err) {
      setValidationErrors({ submit: err.message || "Error en el servidor" });
    } finally {
      setIsLoading(false);
    }
  };

  const metodoNombres = {
    shortest_path: "Ruta Más Corta",
    mst: "Árbol de Expansión Mínima (MST)",
    max_flow: "Flujo Máximo",
    min_cost_flow: "Flujo de Costo Mínimo",
  };

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
            <h1 className={styles.moduleTitle}>🔗 Optimización en Redes</h1>
            <p className={styles.moduleSubtitle}>
              Algoritmos de Grafos para Logística y Redes
            </p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="btn btn-outline-light"
          >
            Regresar
          </button>
        </div>
      </div>

      <div className="container py-4">
        <div className="row g-4">
          {/* Configuración */}
          <div className="col-lg-5">
            <div className="card shadow-sm p-4 border-0">
              <h5 className="text-primary mb-3">🛠️ Nueva Conexión</h5>
              <div className="row g-2">
                <div className="col-6">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Origen"
                    value={edgeData.from}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, from: e.target.value })
                    }
                  />
                </div>
                <div className="col-6">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Destino"
                    value={edgeData.to}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, to: e.target.value })
                    }
                  />
                </div>
                <div className="col-6">
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Peso/Costo"
                    value={edgeData.weight}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, weight: e.target.value })
                    }
                  />
                </div>
                <div className="col-6">
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Capacidad"
                    value={edgeData.capacity}
                    onChange={(e) =>
                      setEdgeData({ ...edgeData, capacity: e.target.value })
                    }
                  />
                </div>
                <div className="col-12 mt-2">
                  <button className="btn btn-primary w-100" onClick={addEdge}>
                    Agregar Arista
                  </button>
                </div>
              </div>
              {validationErrors.edge && (
                <div className="text-danger small mt-2">
                  {validationErrors.edge}
                </div>
              )}

              <hr />
              <div className="d-flex justify-content-between align-items-center">
                <span>
                  Nodos:{" "}
                  <strong>
                    {new Set(graph.flatMap((e) => [e[0], e[1]])).size}
                  </strong>
                </span>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => setGraph([])}
                >
                  Limpiar Grafo
                </button>
              </div>
            </div>
          </div>

          {/* Listado de Aristas */}
          <div className="col-lg-7">
            <div
              className="card shadow-sm p-4 border-0"
              style={{ minHeight: "250px" }}
            >
              <h5 className="mb-3">📌 Estructura de la Red</h5>
              <div className="d-flex flex-wrap gap-2">
                {graph.map(([u, v, w, c], i) => (
                  <Badge
                    key={i}
                    bg="light"
                    text="dark"
                    className="border p-2 d-flex align-items-center gap-2"
                  >
                    <span className="text-primary fw-bold">{u}</span> →
                    <span className="text-success fw-bold">{v}</span>
                    <span className="text-muted small">
                      | W:{w} C:{c}
                    </span>
                    <span
                      className="text-danger ms-2 cursor-pointer"
                      style={{ cursor: "pointer" }}
                      onClick={() => removeEdge(i)}
                    >
                      ✕
                    </span>
                  </Badge>
                ))}
                {graph.length === 0 && (
                  <p className="text-muted italic">No hay aristas definidas.</p>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="text-center my-4">
          <button
            className="btn btn-success btn-lg px-5 shadow"
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

        {/* Resultados */}
        {solution && (
          <div className="row g-4 mt-2">
            {Object.entries(metodoNombres).map(([key, label]) => {
              const res = solution[key];
              if (!res) return null;
              return (
                <div key={key} className="col-md-6">
                  <div className="card shadow-sm border-0 h-100">
                    <div className="card-header bg-white fw-bold">{label}</div>
                    <div className="card-body text-center">
                      <div className="mb-3 p-2 bg-light rounded">
                        {key === "max_flow"
                          ? `Flujo: ${res.max_flow}`
                          : key === "min_cost_flow"
                            ? `Costo: ${res.min_cost}`
                            : `Peso Total: ${res.total_weight}`}
                      </div>
                      {res.graph_image && (
                        <img
                          src={`data:image/png;base64,${res.graph_image}`}
                          className="img-fluid rounded cursor-pointer shadow-sm hover-zoom"
                          alt={label}
                          onClick={() => {
                            setSelectedImage(res);
                            setShowModal(true);
                          }}
                        />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <Modal
        show={showModal}
        onHide={() => setShowModal(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Visualización Detallada</Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center p-0">
          {selectedImage && (
            <img
              src={`data:image/png;base64,${selectedImage.graph_image}`}
              className="w-100"
              alt="Full"
            />
          )}
        </Modal.Body>
      </Modal>
    </div>
  );
}
