"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const pathname = usePathname();

  const tabs = [
    { href: "/", label: "Inicio", icon: "🏠" },
    { href: "/linear", label: "Programación Lineal", icon: "📈" },
    { href: "/transport", label: "Transporte", icon: "🚚" },
    { href: "/network", label: "Redes", icon: "🔗" },
  ];

  const isActive = (href) => pathname === href;

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <h1 className={styles.title}>
          <span className={styles.logoIcon}>◆</span>
          Optimización
        </h1>
        <div className={styles.tabsContainer}>
          {tabs.map((tab) => (
            <Link
              key={tab.href}
              href={tab.href}
              className={`${styles.tab} ${isActive(tab.href) ? styles.active : ""}`}
              title={tab.label}
            >
              <span className={styles.tabIcon}>{tab.icon}</span>
              <span className={styles.tabLabel}>{tab.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
