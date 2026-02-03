"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import TransportPage from "./transport";
import NetworkPage from "./network";
import LinearPage from "./linear";
import "bootstrap/dist/css/bootstrap.min.css";

export default function SolveAll() {
  const [activeTab, setActiveTab] = useState("linear");
  const [results, setResults] = useState({
    linear: null,
    transport: null,
    network: null,
  });
  const router = useRouter();

  const handleCaptureResult = (type, data) => {
    setResults((prev) => ({ ...prev, [type]: data }));
  };

  const tabs = [
    { id: "linear", name: "🧮 Programación Lineal", icon: "🧮" },
    { id: "transport", name: "📦 Problema de Transporte", icon: "📦" },
    { id: "network", name: "🌐 Optimización en Redes", icon: "🌐" },
  ];

  // Renderiza el análisis de sensibilidad detallado de cada módulo
  const renderIndividualSensitivity = () => {
    return (
      <div className="row g-4 mb-5">
        {tabs.map((tab) => (
          <div className="col-12" key={tab.id}>
            <div
              className={`card shadow-sm border-0 ${results[tab.id] ? "border-start border-primary border-4" : ""}`}
            >
              <div className="card-header bg-light d-flex align-items-center">
                <span className="me-2 fs-4">{tab.icon}</span>
                <h5 className="mb-0 fw-bold">
                  Análisis de Sensibilidad: {tab.name}
                </h5>
              </div>
              <div className="card-body">
                {results[tab.id] ? (
                  <div
                    className="text-secondary"
                    style={{ whiteSpace: "pre-line" }}
                  >
                    {/* Mostramos el análisis inteligente detallado del raw data si existe */}
                    {results[tab.id].raw?.intelligent_analysis ||
                      results[tab.id].raw?.sensitivity_analysis ||
                      results[tab.id].raw?.shortest_path
                        ?.sensitivity_analysis_gemini ||
                      results[tab.id].analisisResumen}
                  </div>
                ) : (
                  <div className="text-center py-3 text-muted">
                    <small>
                      Resuelve este módulo para visualizar el análisis
                      detallado.
                    </small>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Lógica de Análisis Conjunto Detallado (Cross-Model Analysis)
  const renderCrossModelAnalysis = () => {
    const { linear, transport, network } = results;

    if (!linear && !transport && !network) {
      return (
        <div className="text-center p-5 text-muted bg-light rounded border">
          <p className="mb-0">
            Se requiere la resolución de los módulos para generar el diagnóstico
            técnico conjunto.
          </p>
        </div>
      );
    }

    return (
      <div className="p-3">
        <h4 className="text-primary fw-bold mb-4 border-bottom pb-2">
          🔍 Diagnóstico Técnico Conjunto
        </h4>

        <div className="row g-4">
          {/* Bloque 1: Interacción Producción-Distribución */}
          <div className="col-md-6">
            <h6 className="fw-bold text-dark">
              1. Relación Producción vs. Logística
            </h6>
            <p className="small text-muted">
              {linear && transport ? (
                <>
                  El modelo Lineal determina una producción óptima de{" "}
                  <strong>{linear.unidadesTotales.toFixed(2)}</strong> unidades.
                  La infraestructura de transporte posee una capacidad instalada
                  de <strong>{transport.capacidadTotal.toFixed(2)}</strong>{" "}
                  unidades.
                  <br />
                  <br />
                  <span
                    className={
                      transport.capacidadTotal >= linear.unidadesTotales
                        ? "text-success"
                        : "text-danger"
                    }
                  >
                    {transport.capacidadTotal >= linear.unidadesTotales
                      ? "✅ Factibilidad Logística: La red de distribución actual es CAPAZ de absorber el 100% de la producción óptima sin necesidad de expansiones."
                      : "❌ Restricción de Capacidad: Existe un cuello de botella logístico. La producción excede la capacidad de envío. Se recomienda revisar los nodos de oferta o habilitar rutas adicionales."}
                  </span>
                </>
              ) : (
                "Pendiente de datos de Programación Lineal y Transporte."
              )}
            </p>
          </div>

          {/* Bloque 2: Impacto Económico Integral */}
          <div className="col-md-6">
            <h6 className="fw-bold text-dark">
              2. Eficiencia de Márgenes y Flujos
            </h6>
            <p className="small text-muted">
              {linear && transport ? (
                <>
                  La Utilidad Bruta (Z) es de{" "}
                  <strong>${linear.valorOptimo.toLocaleString()}</strong>,
                  mientras que los Costos de Transporte ascienden a{" "}
                  <strong>${transport.costoTotal.toLocaleString()}</strong>.
                  <br />
                  <br />
                  El margen neto resultante es de{" "}
                  <strong>
                    $
                    {(
                      linear.valorOptimo - transport.costoTotal
                    ).toLocaleString()}
                  </strong>
                  . El costo logístico consume un{" "}
                  <strong>
                    {(
                      (transport.costoTotal / linear.valorOptimo) *
                      100
                    ).toFixed(2)}
                    %
                  </strong>{" "}
                  de la utilidad total.
                  {network &&
                    ` En términos de flujo, la red soporta una carga máxima de ${network.flujoTotal} unidades, lo que representa el límite físico del sistema.`}
                </>
              ) : (
                "Pendiente de datos para cálculo de márgenes integrados."
              )}
            </p>
          </div>

          {/* Bloque 3: Sensibilidad Crítica Final */}
          <div className="col-12 mt-3">
            <div className="alert alert-info border-0 shadow-sm">
              <h6 className="fw-bold">💡 Recomendación de Estabilidad:</h6>
              <p className="small mb-0">
                {linear && transport && network
                  ? `Para optimizar el sistema global, se debe prestar atención a los precios sombra del modelo lineal en conjunto con las rutas de costo mínimo. Si la demanda en los nodos de transporte varía un 5%, el flujo máximo detectado en la red (${network.flujoTotal}) podría verse comprometido, afectando la utilidad final de $${linear.valorOptimo.toLocaleString()}.`
                  : "Complete todos los módulos para obtener la recomendación de estabilidad de sistema completo."}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="container-fluid bg-light min-vh-100 pb-5">
      {/* Navbar */}
      <nav className="navbar navbar-dark bg-dark p-3 shadow mb-4">
        <button
          onClick={() => router.push("/")}
          className="btn btn-outline-light btn-sm"
        >
          ⬅ Regresar al Inicio
        </button>
        <h4 className="text-white mx-auto mb-0 fw-bold">
          🚀 PANEL DE OPTIMIZACIÓN INTEGRAL
        </h4>
        <div className="d-none d-md-block text-white-50 small">
          Investigación de Operaciones
        </div>
      </nav>

      <div className="container">
        {/* Card Principal de Módulos */}
        <div
          className="card shadow-lg border-0 mb-5 overflow-hidden"
          style={{ borderRadius: "15px" }}
        >
          <div className="card-header bg-white p-0 border-bottom">
            <ul className="nav nav-tabs nav-fill border-0">
              {tabs.map((tab) => (
                <li className="nav-item" key={tab.id}>
                  <button
                    className={`nav-link py-3 rounded-0 border-0 ${activeTab === tab.id ? "active fw-bold text-primary bg-light" : "text-muted"}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <span className="me-2">{tab.icon}</span> {tab.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <div
            className="card-body p-4 bg-white"
            style={{ minHeight: "500px" }}
          >
            {activeTab === "linear" && (
              <LinearPage
                onResult={(d) => handleCaptureResult("linear", d)}
                isModule={true}
              />
            )}
            {activeTab === "transport" && (
              <TransportPage
                onResult={(d) => handleCaptureResult("transport", d)}
                isModule={true}
              />
            )}
            {activeTab === "network" && (
              <NetworkPage
                onResult={(d) => handleCaptureResult("network", d)}
                isModule={true}
              />
            )}
          </div>
        </div>

        {/* SECCIÓN 1: ANALISIS DE SENSIBILIDAD INDIVIDUALES */}
        <h3 className="mb-4 fw-bold text-dark">
          📋 Análisis de Sensibilidad Individual
        </h3>
        {renderIndividualSensitivity()}

        {/* SECCIÓN 2: ANALISIS CONJUNTO DETALLADO */}
        <div
          className="card shadow-lg border-0 bg-white mb-5"
          style={{ borderRadius: "20px" }}
        >
          <div className="card-body p-0 overflow-hidden">
            <div className="bg-dark text-white p-3 text-center">
              <h5 className="mb-0">
                📊 REPORTE DE SENSIBILIDAD INTEGRAL (SISTEMA COMPLETO)
              </h5>
            </div>
            {renderCrossModelAnalysis()}
          </div>
        </div>
      </div>
    </div>
  );
}
