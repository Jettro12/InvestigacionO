"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import TransportPage from "./transport";
import NetworkPage from "./network";
import LinearPage from "./linear";
import "bootstrap/dist/css/bootstrap.min.css";

export default function SolveAll() {
  const [activeTab, setActiveTab] = useState("linear");
  const [error] = useState(null);
  const router = useRouter();

  const tabs = [
    { id: "linear", name: "🧮 Programación Lineal", icon: "🧮" },
    { id: "transport", name: "📦 Problema de Transporte", icon: "📦" },
    { id: "network", name: "🌐 Optimización en Redes", icon: "🌐" }
  ];

  const renderActiveComponent = () => {
    switch (activeTab) {
      case "linear":
        return <LinearPage />;
      case "transport":
        return <TransportPage />;
      case "network":
        return <NetworkPage />;
      default:
        return <LinearPage />;
    }
  };

  return (
    <div className="container-fluid bg-light min-vh-100">
      {/* Navbar mejorado */}
      <nav className="navbar navbar-dark bg-dark p-3 shadow">
        <button onClick={() => router.push("/")} className="btn btn-outline-light">
          ⬅ Regresar al Inicio
        </button>
        <h3 className="text-white mx-auto mb-0">
          🚀 Optimización Completa del Negocio
        </h3>
        <div className="text-white">
          <small>Solución Integral</small>
        </div>
      </nav>

      {/* Espacio para evitar solapamiento con el Navbar */}
      <div className="pt-5 mt-5">
        <div className="container my-4">
          
          {/* Header principal */}
          <div className="text-center mb-5">
            <h1 className="text-primary mb-3">
              📊 Optimización Completa del Negocio
            </h1>
            <p className="text-muted fs-5">
              Soluciona todos tus problemas de optimización en una sola plataforma
            </p>
          </div>

          {/* Tabs de navegación */}
          <div className="card shadow-lg border-0 mb-4" style={{ borderRadius: "15px" }}>
            <div className="card-body p-0">
              <ul className="nav nav-tabs nav-fill" id="optimizationTabs" role="tablist">
                {tabs.map((tab) => (
                  <li className="nav-item" role="presentation" key={tab.id}>
                    <button
                      className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
                      id={`${tab.id}-tab`}
                      data-bs-toggle="tab"
                      data-bs-target={`#${tab.id}`}
                      type="button"
                      role="tab"
                      aria-controls={tab.id}
                      aria-selected={activeTab === tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      style={{
                        border: 'none',
                        borderRadius: activeTab === tab.id ? '15px 15px 0 0' : '0',
                        backgroundColor: activeTab === tab.id ? '#fff' : '#f8f9fa',
                        color: activeTab === tab.id ? '#0d6efd' : '#6c757d',
                        fontWeight: activeTab === tab.id ? 'bold' : 'normal',
                        fontSize: '16px',
                        padding: '15px 20px'
                      }}
                    >
                      <span style={{ fontSize: '20px', marginRight: '8px' }}>
                        {tab.icon}
                      </span>
                      {tab.name}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Contenido principal */}
          <div className="card shadow-lg border-0" style={{ borderRadius: "15px", minHeight: "600px" }}>
            <div className="card-body p-4">
              <div className="tab-content" id="optimizationTabContent">
                <div
                  className={`tab-pane fade ${activeTab === 'linear' ? 'show active' : ''}`}
                  id="linear"
                  role="tabpanel"
                  aria-labelledby="linear-tab"
                >
                  <div className="text-center mb-4">
                    <h3 className="text-primary">
                      🧮 Programación Lineal
                    </h3>
                    <p className="text-muted">
                      Optimiza funciones lineales con múltiples restricciones usando métodos avanzados
                    </p>
                  </div>
                  <LinearPage />
                </div>

                <div
                  className={`tab-pane fade ${activeTab === 'transport' ? 'show active' : ''}`}
                  id="transport"
                  role="tabpanel"
                  aria-labelledby="transport-tab"
                >
                  <div className="text-center mb-4">
                    <h3 className="text-primary">
                      📦 Problema de Transporte
                    </h3>
                    <p className="text-muted">
                      Optimiza la distribución de productos desde orígenes a destinos
                    </p>
                  </div>
                  <TransportPage />
                </div>

                <div
                  className={`tab-pane fade ${activeTab === 'network' ? 'show active' : ''}`}
                  id="network"
                  role="tabpanel"
                  aria-labelledby="network-tab"
                >
                  <div className="text-center mb-4">
                    <h3 className="text-primary">
                      🌐 Optimización en Redes
                    </h3>
                    <p className="text-muted">
                      Analiza grafos para encontrar rutas óptimas y flujos máximos
                    </p>
                  </div>
                  <NetworkPage />
                </div>
              </div>
            </div>
          </div>

          {/* Análisis de Sensibilidad Global */}
          <div className="mt-5">
            <div className="card shadow-lg border-0" style={{ borderRadius: "15px" }}>
              <div className="card-header bg-success text-white">
                <h3 className="mb-0 text-center">
                  📊 Análisis de Sensibilidad Global
                </h3>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-4 text-center">
                    <div className="border rounded p-3 mb-3">
                      <span role="img" aria-label="lineal" style={{ fontSize: "3rem" }}>🧮</span>
                      <h5 className="mt-2">Programación Lineal</h5>
                      <p className="text-muted small">
                        Análisis de sensibilidad de coeficientes y restricciones
                      </p>
                    </div>
                  </div>
                  <div className="col-md-4 text-center">
                    <div className="border rounded p-3 mb-3">
                      <span role="img" aria-label="transporte" style={{ fontSize: "3rem" }}>📦</span>
                      <h5 className="mt-2">Problema de Transporte</h5>
                      <p className="text-muted small">
                        Análisis de costos y capacidades de distribución
                      </p>
                    </div>
                  </div>
                  <div className="col-md-4 text-center">
                    <div className="border rounded p-3 mb-3">
                      <span role="img" aria-label="redes" style={{ fontSize: "3rem" }}>🌐</span>
                      <h5 className="mt-2">Optimización en Redes</h5>
                      <p className="text-muted small">
                        Análisis de conectividad y flujos en grafos
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="text-center mt-4">
                  <div className="alert alert-info">
                    <h5>🤖 Análisis Inteligente con IA</h5>
                    <p className="mb-0">
                      Cada módulo incluye análisis de sensibilidad inteligente usando Google Gemini AI
                      para proporcionar recomendaciones prácticas y comprensibles.
                    </p>
                  </div>
                </div>

                <div className="border p-4 bg-light rounded text-center" style={{ minHeight: "200px" }}>
                  <span role="img" aria-label="analisis" style={{ fontSize: "3rem" }}>🔎</span>
                  <p className="mt-3 text-muted">
                    Los análisis de sensibilidad se generan automáticamente en cada módulo
                    para proporcionar insights valiosos sobre la robustez de las soluciones.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Información adicional */}
          <div className="mt-5">
            <div className="row">
              <div className="col-md-6">
                <div className="card border-0 bg-light">
                  <div className="card-body">
                    <h5 className="text-primary">🎯 Características Principales</h5>
                    <ul className="list-unstyled">
                      <li>✅ Múltiples algoritmos de optimización</li>
                      <li>✅ Análisis de sensibilidad con IA</li>
                      <li>✅ Visualizaciones interactivas</li>
                      <li>✅ Validaciones en tiempo real</li>
                      <li>✅ Interfaz moderna y responsiva</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="col-md-6">
                <div className="card border-0 bg-light">
                  <div className="card-body">
                    <h5 className="text-success">🚀 Beneficios</h5>
                    <ul className="list-unstyled">
                      <li>📈 Optimización de costos y recursos</li>
                      <li>🎯 Toma de decisiones informada</li>
                      <li>⚡ Procesamiento rápido y eficiente</li>
                      <li>🔍 Análisis detallado y comprensible</li>
                      <li>💡 Recomendaciones inteligentes</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert-danger text-center shadow-lg" style={{
          position: "fixed",
          top: "100px",
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 1000,
          maxWidth: "600px"
        }}>
          {error}
        </div>
      )}
    </div>
  );
}
