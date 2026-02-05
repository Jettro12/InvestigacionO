"use client";
import Link from "next/link";
import { useState } from "react";
import styles from "./home.module.css";

export default function Home() {
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  const modules = [
    {
      id: "linear",
      title: "Programación Lineal",
      subtitle: "Optimización de restricciones",
      description:
        "Resuelve problemas de optimización lineal con métodos avanzados incluidos Simplex, Dos Fases, Gran M y análisis de dualidad.",
      features: [
        "Múltiples métodos de resolución",
        "Análisis de sensibilidad completo",
        "Visualización de soluciones",
        "Integración con IA",
      ],
      icon: "📈",
      color: "#2563eb", // Azul
      glowColor: "rgba(37, 99, 235, 0.15)",
    },
    {
      id: "transport",
      title: "Problema de Transporte",
      subtitle: "Optimización de distribución",
      description:
        "Optimiza la asignación de recursos desde múltiples orígenes a destinos, minimizando costos logísticos.",
      features: [
        "Métodos: Esquina Noroeste, Costo Mínimo, Vogel",
        "Método MODI para mejora iterativa",
        "Análisis de factibilidad",
        "Reportes detallados",
      ],
      icon: "🚚",
      color: "#059669", // Verde
      glowColor: "rgba(5, 150, 105, 0.15)",
    },
    {
      id: "network",
      title: "Optimización en Redes",
      subtitle: "Análisis de grafos complejos",
      description:
        "Encuentra rutas óptimas, maximiza flujos y calcula árboles de expansión mínima en estructuras de red complejas.",
      features: [
        "Algoritmos: Dijkstra, Ford-Fulkerson",
        "Árbol de expansión mínima",
        "Análisis de conectividad",
        "Visualización de grafos",
      ],
      icon: "🔗",
      color: "#0891b2", // Cian
      glowColor: "rgba(8, 145, 178, 0.15)",
    },
  ];

  return (
    <div
      className={styles.pageWrapper}
      style={{ backgroundColor: "#ffffff", minHeight: "100vh" }}
    >
      {/* Hero Section: Máximo Contraste */}
      <section
        className={styles.heroSection}
        style={{
          padding: "100px 0",
          backgroundColor: "#f8fafc",
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        <div className="container">
          <div className={styles.heroContent} style={{ maxWidth: "850px" }}>
            <span
              style={{
                backgroundColor: "#1e293b",
                color: "#f8fafc",
                padding: "8px 20px",
                borderRadius: "30px",
                fontWeight: "700",
                fontSize: "0.85rem",
                display: "inline-block",
                marginBottom: "25px",
                textTransform: "uppercase",
              }}
            >
              🚀 Plataforma de Optimización 2026
            </span>
            <h1
              style={{
                color: "#0f172a",
                fontSize: "4rem",
                fontWeight: "900",
                lineHeight: "1.1",
                marginBottom: "25px",
                letterSpacing: "-0.03em",
              }}
            >
              Soluciones Avanzadas de Optimización Empresarial
            </h1>
            <p
              style={{
                color: "#334155",
                fontSize: "1.35rem",
                lineHeight: "1.6",
                marginBottom: "45px",
                maxWidth: "750px",
              }}
            >
              Resuelve problemas complejos de programación lineal, transporte y
              redes con análisis inteligente y visualizaciones profesionales.
            </p>
            <div style={{ display: "flex", gap: "20px" }}>
              <Link href="/linear">
                <button
                  style={{
                    backgroundColor: "#2563eb",
                    color: "#ffffff",
                    padding: "18px 36px",
                    borderRadius: "12px",
                    border: "none",
                    fontWeight: "700",
                    fontSize: "1.1rem",
                    cursor: "pointer",
                    boxShadow: "0 10px 20px -5px rgba(37, 99, 235, 0.4)",
                  }}
                >
                  Explorar Módulos
                </button>
              </Link>
              <Link href="/solve-all">
                <button
                  style={{
                    backgroundColor: "transparent",
                    color: "#0f172a",
                    padding: "18px 36px",
                    borderRadius: "12px",
                    border: "2px solid #0f172a",
                    fontWeight: "700",
                    fontSize: "1.1rem",
                    cursor: "pointer",
                  }}
                >
                  Solución Completa
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Módulos Principales: Tarjetas con Glow */}
      <section style={{ padding: "100px 0" }}>
        <div className="container">
          <div style={{ marginBottom: "60px", textAlign: "center" }}>
            <h2
              style={{
                color: "#0f172a",
                fontSize: "2.8rem",
                fontWeight: "800",
              }}
            >
              Herramientas Especializadas
            </h2>
            <p style={{ color: "#475569", fontSize: "1.2rem" }}>
              Selecciona un área de estudio para comenzar la optimización
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "30px",
            }}
          >
            {modules.map((module) => (
              <Link
                key={module.id}
                href={`/${module.id}`}
                style={{ textDecoration: "none" }}
              >
                <div
                  onMouseEnter={() => setHoveredCard(module.id)}
                  onMouseLeave={() => setHoveredCard(null)}
                  style={{
                    backgroundColor: "#ffffff",
                    border: `1px solid ${hoveredCard === module.id ? module.color : "#e2e8f0"}`,
                    borderRadius: "24px",
                    padding: "40px",
                    height: "100%",
                    transition: "all 0.4s cubic-bezier(0.23, 1, 0.32, 1)",
                    position: "relative",
                    overflow: "hidden",
                    boxShadow:
                      hoveredCard === module.id
                        ? `0 20px 40px -10px ${module.glowColor}`
                        : "0 4px 6px -1px rgba(0,0,0,0.05)",
                    transform:
                      hoveredCard === module.id
                        ? "translateY(-12px)"
                        : "translateY(0)",
                  }}
                >
                  {/* Efecto de Brillo Interno (Glow) */}
                  <div
                    style={{
                      position: "absolute",
                      top: "-20%",
                      right: "-20%",
                      width: "200px",
                      height: "200px",
                      background: module.glowColor,
                      filter: "blur(60px)",
                      borderRadius: "50%",
                      opacity: hoveredCard === module.id ? 1 : 0,
                      transition: "opacity 0.4s ease",
                    }}
                  />

                  <div style={{ position: "relative", zIndex: 1 }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "20px",
                        marginBottom: "30px",
                      }}
                    >
                      <span style={{ fontSize: "3.5rem" }}>{module.icon}</span>
                      <div>
                        <h3
                          style={{
                            color: "#0f172a",
                            fontSize: "1.6rem",
                            fontWeight: "800",
                            margin: 0,
                          }}
                        >
                          {module.title}
                        </h3>
                        <p
                          style={{
                            color: module.color,
                            fontWeight: "700",
                            fontSize: "1rem",
                            margin: 0,
                          }}
                        >
                          {module.subtitle}
                        </p>
                      </div>
                    </div>

                    <p
                      style={{
                        color: "#334155",
                        fontSize: "1.1rem",
                        lineHeight: "1.6",
                        marginBottom: "35px",
                      }}
                    >
                      {module.description}
                    </p>

                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "12px",
                      }}
                    >
                      {module.features.map((f, i) => (
                        <div
                          key={i}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "12px",
                            color: "#1e293b",
                            fontWeight: "600",
                          }}
                        >
                          <span
                            style={{
                              width: "8px",
                              height: "8px",
                              backgroundColor: module.color,
                              borderRadius: "50%",
                            }}
                          />
                          {f}
                        </div>
                      ))}
                    </div>

                    <div
                      style={{
                        marginTop: "40px",
                        paddingTop: "25px",
                        borderTop: "1px solid #f1f5f9",
                        color: module.color,
                        fontWeight: "800",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                      }}
                    >
                      EXPLORAR MÓDULO{" "}
                      <span style={{ fontSize: "1.3rem" }}>→</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Footer Profundo para Contraste Final */}
      <footer
        style={{
          backgroundColor: "#0f172a",
          color: "#f8fafc",
          padding: "80px 0 40px 0",
        }}
      >
        <div className="container">
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "40px",
            }}
          >
            <div style={{ maxWidth: "400px" }}>
              <h4
                style={{
                  fontSize: "1.5rem",
                  fontWeight: "800",
                  marginBottom: "20px",
                }}
              >
                Plataforma de Optimización
              </h4>
              <p style={{ color: "#94a3b8", lineHeight: "1.6" }}>
                Herramienta académica desarrollada para la resolución eficiente
                de problemas de Investigación de Operaciones.
              </p>
            </div>
            <div>
              <h5
                style={{
                  fontSize: "1.2rem",
                  fontWeight: "700",
                  marginBottom: "20px",
                }}
              >
                Desarrolladores
              </h5>
              <div
                style={{
                  color: "#cbd5e1",
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                  fontWeight: "500",
                }}
              >
                <span>Jair Folleco</span>
                <span>Ariel Guerron</span>
                <span>Damian Quezada</span>
                <span>Jose Saltos</span>
              </div>
            </div>
          </div>
          <div
            style={{
              marginTop: "60px",
              paddingTop: "30px",
              borderTop: "1px solid #1e293b",
              textAlign: "center",
              color: "#64748b",
            }}
          >
            © 2026 Plataforma de Optimización • Facultad de Ingeniería en
            Sistemas
          </div>
        </div>
      </footer>
    </div>
  );
}
