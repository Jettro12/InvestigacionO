"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { solveNetwork } from "../services/networkService";
import "bootstrap/dist/css/bootstrap.min.css";
import { Spinner, Badge, Card, Row, Col, Alert, Tabs, Tab, Table } from "react-bootstrap";
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
    setSolution(null);
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
            ? `Flujo máximo detectado: ${result.max_flow.max_flow} unidades.`
            : "Optimización de red completada.",
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
      {!isModule && (
        <div className={styles.headerSection}>
          <div className="d-flex justify-content-between align-items-center p-4 text-white">
            <h1 className={styles.moduleTitle}>🌐 Optimización en Redes</h1>
            <button onClick={() => router.push("/")} className="btn btn-outline-light">
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
                    placeholder="Origen (A)"
                    className="form-control"
                    value={edgeData.from}
                    onChange={(e) => setEdgeData({ ...edgeData, from: e.target.value })}
                  />
                </div>
                <div className="col-6">
                  <input
                    placeholder="Destino (B)"
                    className="form-control"
                    value={edgeData.to}
                    onChange={(e) => setEdgeData({ ...edgeData, to: e.target.value })}
                  />
                </div>
                <div className="col-6">
                  <label className="small text-muted">Costo / Peso</label>
                  <input
                    type="number"
                    className="form-control"
                    value={edgeData.weight}
                    onChange={(e) => setEdgeData({ ...edgeData, weight: e.target.value })}
                  />
                </div>
                <div className="col-6">
                  <label className="small text-muted">Capacidad</label>
                  <input
                    type="number"
                    className="form-control"
                    value={edgeData.capacity}
                    onChange={(e) => setEdgeData({ ...edgeData, capacity: e.target.value })}
                  />
                </div>
              </div>
              <button className="btn btn-primary w-100 mt-3 fw-bold" onClick={addEdge}>
                Agregar Arista
              </button>
            </div>
          </div>

          {/* Grafo Actual */}
          <div className="col-md-7">
            <div className="card shadow-sm p-4 border-0" style={{ minHeight: "220px" }}>
              <h6 className="fw-bold mb-3">📌 Estructura de la Red</h6>
              <div className="d-flex flex-wrap gap-2 mb-4">
                {graph.map((e, i) => (
                  <Badge key={i} bg="light" text="dark" className="border p-2 shadow-sm">
                    <span className="text-primary">{e[0]}</span> → <span className="text-success">{e[1]}</span>
                    <span className="ms-2 text-muted small">(W:{e[2]} C:{e[3]})</span>
                    <span className="ms-2 text-danger" style={{ cursor: "pointer" }} onClick={() => removeEdge(i)}>
                      &times;
                    </span>
                  </Badge>
                ))}
                {graph.length === 0 && <p className="text-muted small">No hay conexiones definidas.</p>}
              </div>
              <button
                className="btn btn-success mt-auto fw-bold py-2 shadow-sm"
                onClick={handleSubmit}
                disabled={isLoading || graph.length === 0}
              >
                {isLoading ? <Spinner size="sm" /> : "🚀 Calcular Todo"}
              </button>
            </div>
          </div>
        </div>

        {/* --- SECCIÓN DE RESULTADOS --- */}
        {solution && (
          <div className="mt-4 animate__animated animate__fadeIn">
            
            {solution.max_flow && (
              <Alert variant="primary" className="shadow-sm text-center border-0 bg-primary bg-opacity-10 text-primary">
                <h4 className="mb-0 fw-bold">🌊 Flujo Máximo: {solution.max_flow.max_flow} unidades</h4>
                <small>Capacidad total optimizada de la red</small>
              </Alert>
            )}

            <Row className="g-3">
              {/* Dijkstra + Análisis de Sensibilidad */}
              {solution.shortest_path && (
                <Col md={5}>
                  <Card className="h-100 border-0 shadow-sm p-3">
                    <h6 className="text-danger fw-bold">📍 Ruta Corta (Dijkstra)</h6>
                    <div className="d-flex justify-content-between align-items-center mb-2">
                        <span className="h4 fw-bold mb-0">{solution.shortest_path.total_weight}</span>
                        <Badge bg="danger" className="bg-opacity-10 text-danger border border-danger">Costo Mínimo</Badge>
                    </div>
                    <p className="small text-muted bg-light p-2 rounded">
                        <strong>Camino:</strong> {solution.shortest_path.node_order?.join(" → ")}
                    </p>

                    {/* NUEVO: Tabla de Sensibilidad Integrada */}
                    {solution.sensitivity && (
                      <div className="mt-3">
                        <h6 className="small fw-bold text-uppercase text-muted border-bottom pb-1">Impacto por eliminación:</h6>
                        <div style={{maxHeight: '150px', overflowY: 'auto'}}>
                            <Table size="sm" hover className="mb-0">
                                <thead>
                                    <tr>
                                        <th className="small">Arista</th>
                                        <th className="small text-end">Variación</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.entries(solution.sensitivity).map(([edge, impact]) => (
                                        <tr key={edge}>
                                            <td className="small">{edge}</td>
                                            <td className={`small text-end fw-bold ${impact === "Ruta se vuelve imposible" ? "text-danger" : "text-primary"}`}>
                                                {impact === 0 ? "—" : impact > 0 ? `+${impact}` : impact}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>
                        </div>
                      </div>
                    )}
                  </Card>
                </Col>
              )}

              {/* MST y Costo Mínimo */}
              <Col md={7}>
                <Row className="g-3">
                    {solution.mst && (
                        <Col md={12}>
                        <Card className="border-0 shadow-sm p-3">
                            <h6 className="text-success fw-bold">🌲 Expansión Mínima (MST)</h6>
                            <div className="d-flex justify-content-between">
                                <span className="h4 fw-bold mb-0">{solution.mst.total_weight}</span>
                                <div className="text-end">
                                    {solution.mst.edges.slice(0, 3).map((edge, i) => (
                                        <Badge key={i} bg="success" className="ms-1 bg-opacity-10 text-success border border-success small">
                                            {edge[0]}-{edge[1]}
                                        </Badge>
                                    ))}
                                    {solution.mst.edges.length > 3 && <span className="small text-muted ms-1">...</span>}
                                </div>
                            </div>
                        </Card>
                        </Col>
                    )}

                    {solution.min_cost_flow && (
                        <Col md={12}>
                        <Card className="border-0 shadow-sm p-3 bg-dark text-white">
                            <h6 className="text-warning fw-bold">💰 Flujo de Costo Mínimo</h6>
                            <div className="d-flex justify-content-between align-items-center">
                                <div>
                                    <span className="h4 fw-bold">${solution.min_cost_flow.min_cost}</span>
                                    <span className="ms-3 text-muted small">Total: {solution.min_cost_flow.total_flow} u.</span>
                                </div>
                                <Badge bg="warning" text="dark">Optimizado</Badge>
                            </div>
                        </Card>
                        </Col>
                    )}
                </Row>
              </Col>
            </Row>

            {/* --- VISUALIZACIÓN GRÁFICA --- */}
            <Card className="mt-4 border-0 shadow-sm overflow-hidden">
              <Card.Header className="bg-white border-0 pt-3">
                <h6 className="fw-bold text-muted text-uppercase small mb-0 text-center">Gráficos de Optimización</h6>
              </Card.Header>
              <Card.Body>
                <Tabs defaultActiveKey="flow" id="graph-tabs" className="mb-3 justify-content-center custom-tabs">
                  {solution.max_flow?.graph_image && (
                    <Tab eventKey="flow" title="Flujo (Corte Mínimo)">
                      <div className="text-center p-2">
                        <img src={`data:image/png;base64,${solution.max_flow.graph_image}`} alt="Flow" className="img-fluid rounded shadow-sm" style={{maxHeight: '420px'}} />
                        <p className="mt-2 text-muted small">Muestra <b>Flujo Enviado / Capacidad</b> de cada arista.</p>
                      </div>
                    </Tab>
                  )}
                  {solution.shortest_path?.graph_image && (
                    <Tab eventKey="shortest" title="Ruta Dijkstra">
                      <div className="text-center p-2">
                        <img src={`data:image/png;base64,${solution.shortest_path.graph_image}`} alt="Dijkstra" className="img-fluid rounded shadow-sm" style={{maxHeight: '420px'}} />
                        <p className="mt-2 text-muted small">La ruta más barata se resalta en <b>rojo</b>.</p>
                      </div>
                    </Tab>
                  )}
                  {solution.mst?.graph_image && (
                    <Tab eventKey="mst" title="Estructura MST">
                      <div className="text-center p-2">
                        <img src={`data:image/png;base64,${solution.mst.graph_image}`} alt="MST" className="img-fluid rounded shadow-sm" style={{maxHeight: '420px'}} />
                        <p className="mt-2 text-muted small">La red de conexión más económica está en <b>verde</b>.</p>
                      </div>
                    </Tab>
                  )}
                </Tabs>
              </Card.Body>
            </Card>

            {/* Análisis Inteligente */}
            {solution.intelligent_analysis && (
              <Card className="border-0 shadow-sm mt-4 bg-light">
                <Card.Body>
                  <h5 className="text-primary fw-bold mb-3">🤖 Análisis Estratégico</h5>
                  <div className="p-3 bg-white rounded border shadow-sm" style={{ whiteSpace: "pre-line", fontSize: "14px", color: "#333" }}>
                    {solution.intelligent_analysis}
                  </div>
                </Card.Body>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}