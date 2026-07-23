"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { LayoutDashboard, PenLine, BrainCircuit, ChevronLeft, ChevronRight, Receipt, LineChart } from "lucide-react";
import { createContext, useContext, useState, ReactNode } from "react";

// ── Sidebar collapse context ────────────────────────────────────────────────
interface SidebarCtx { collapsed: boolean; toggle: () => void; }
const SidebarContext = createContext<SidebarCtx>({ collapsed: false, toggle: () => {} });
export function useSidebar() { return useContext(SidebarContext); }
export function SidebarProvider({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <SidebarContext.Provider value={{ collapsed, toggle: () => setCollapsed((v) => !v) }}>
      {children}
    </SidebarContext.Provider>
  );
}

// ── Nav items & scenario dots ────────────────────────────────────────────────
const NAV_ITEMS = [
  { href: "/dashboard",    icon: LayoutDashboard, label: "Dashboard",    sub: "Estadísticas" },
  { href: "/ingreso",      icon: PenLine,          label: "Ingreso",      sub: "Datos del día" },
  { href: "/cierres",      icon: Receipt,          label: "Cierres",      sub: "Historial y Excel" },
  { href: "/predicciones", icon: BrainCircuit,     label: "Predicciones", sub: "Motor IA" },
  { href: "/validacion",   icon: LineChart,        label: "Validación",   sub: "Backtesting" },
];
const SCENARIO_DOTS = [
  { color: "#E8A04A", label: "Corto" },
  { color: "#3DD68C", label: "Óptimo" },
  { color: "#F04438", label: "Crítico" },
];

// ── Sidebar component ────────────────────────────────────────────────────────
export default function Sidebar() {
  const pathname = usePathname();
  const { collapsed, toggle } = useSidebar();

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 240 }}
      transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
      className="flex-shrink-0 h-screen sticky top-0 z-40"
      style={{ overflow: "visible" }}
    >
      {/* Inner Container: Holds all content and handles overflow clipping during width transitions */}
      <div
        className="w-full h-full flex flex-col overflow-hidden"
        style={{
          background:   "var(--bg-base)",
          borderRight:  "1px solid var(--bg-border)",
          transition:   "background-color 0.3s ease, border-color 0.3s ease",
        }}
      >
        {/* ── Header: Logo + Brand ── */}
        <div
          className="flex items-center px-3 py-4 relative"
          style={{ 
            borderBottom: "1px solid var(--bg-border)", 
            minHeight: 64,
            justifyContent: collapsed ? "center" : "flex-start"
          }}
        >
          {/* Logo icon — always visible */}
          <motion.div
            whileHover={{ rotate: 10, scale: 1.05 }}
            transition={{ type: "spring", stiffness: 400, damping: 15 }}
            className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden border border-[var(--bg-border)]"
            style={{
              boxShadow:  "0 4px 12px rgba(0,0,0,0.15)",
            }}
          >
            <img 
              src="/logo.jpg" 
              alt="Casserissima Logo" 
              className="w-full h-full object-cover"
            />
          </motion.div>

          {/* Brand text — hidden when collapsed */}
          <AnimatePresence initial={false}>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, x: -8, width: 0 }}
                animate={{ opacity: 1, x: 0, width: "auto" }}
                exit={{ opacity: 0, x: -8, width: 0 }}
                transition={{ duration: 0.2 }}
                className="ml-3 overflow-hidden"
              >
                <p
                  className="text-sm font-bold leading-tight whitespace-nowrap"
                  style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
                >
                  CASSERISSIMA
                </p>
                <p
                  className="text-[9px] tracking-widest whitespace-nowrap"
                  style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}
                >
                  v2.0 · IA INDUSTRIAL
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* ── Nav ── */}
        <nav className="flex-1 px-2 py-3 flex flex-col gap-1 overflow-hidden">
          {/* Section label */}
          <AnimatePresence initial={false}>
            {!collapsed && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-[9px] font-semibold tracking-widest uppercase px-2 mb-2 whitespace-nowrap"
                style={{ color: "var(--text-faint)", fontFamily: "var(--font-mono)" }}
              >
                Navegación
              </motion.p>
            )}
          </AnimatePresence>

          {NAV_ITEMS.map((item) => {
            const active = pathname.startsWith(item.href);
            const Icon   = item.icon;
            return (
              <Link key={item.href} href={item.href} title={collapsed ? item.label : undefined}>
                <motion.div
                  whileHover={{ x: collapsed ? 0 : 4, scale: collapsed ? 1.05 : 1 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center rounded-xl cursor-pointer relative overflow-hidden"
                  style={{
                    gap:        collapsed ? 0 : 12,
                    padding:    "10px 12px",
                    justifyContent: collapsed ? "center" : "flex-start",
                    background: active
                      ? "color-mix(in srgb, var(--accent-gold) 10%, transparent)"
                      : "transparent",
                    border: active
                      ? "1px solid color-mix(in srgb, var(--accent-gold) 22%, transparent)"
                      : "1px solid transparent",
                    transition: "background 0.18s, border-color 0.18s",
                  }}
                >
                  {/* Active indicator */}
                  {active && (
                    <motion.div
                      layoutId="nav-indicator"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-full"
                      style={{ background: "linear-gradient(180deg, var(--accent-gold), var(--accent-amber))" }}
                    />
                  )}

                  <Icon
                    size={18}
                    style={{ color: active ? "var(--accent-gold)" : "var(--text-muted)", flexShrink: 0 }}
                    strokeWidth={active ? 2.2 : 1.8}
                  />

                  {/* Label — hidden when collapsed */}
                  <AnimatePresence initial={false}>
                    {!collapsed && (
                      <motion.div
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: "auto" }}
                        exit={{ opacity: 0, width: 0 }}
                        transition={{ duration: 0.18 }}
                        className="overflow-hidden"
                      >
                        <p
                          className="text-sm font-semibold leading-tight whitespace-nowrap"
                          style={{ color: active ? "var(--text-primary)" : "var(--text-secondary)" }}
                        >
                          {item.label}
                        </p>
                        <p
                          className="text-[10px] whitespace-nowrap"
                          style={{ color: active ? "var(--accent-gold)" : "var(--text-muted)" }}
                        >
                          {item.sub}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </Link>
            );
          })}
        </nav>

        {/* ── Footer: scenario dots ── */}
        <div
          className="px-3 py-4 overflow-hidden"
          style={{ borderTop: "1px solid var(--bg-border)" }}
        >
          <AnimatePresence initial={false}>
            {!collapsed ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.18 }}
              >
                <p
                  className="text-[9px] font-semibold uppercase tracking-widest mb-2"
                  style={{ color: "var(--text-faint)", fontFamily: "var(--font-mono)" }}
                >
                  Escenarios
                </p>
                {SCENARIO_DOTS.map((s) => (
                  <div key={s.label} className="flex items-center gap-2 mb-1.5">
                    <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: s.color }} />
                    <span className="text-[10px] whitespace-nowrap" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                      {s.label}
                    </span>
                  </div>
                ))}
                <p className="text-[9px] mt-2" style={{ color: "var(--text-faint)", fontFamily: "var(--font-mono)" }}>
                  RF · Newsvendor · ROP — v2.0.0
                </p>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-2"
              >
                {SCENARIO_DOTS.map((s) => (
                  <span key={s.label} className="w-1.5 h-1.5 rounded-full" style={{ background: s.color }} />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Floating Toggle Button: Absolutely positioned on the border of the aside */}
      <motion.button
        onClick={toggle}
        whileHover={{ scale: 1.15, backgroundColor: "var(--accent-gold)", color: "var(--bg-base)" }}
        whileTap={{ scale: 0.95 }}
        className="absolute -right-3 top-8 -translate-y-1/2 z-50 w-6 h-6 rounded-full flex items-center justify-center border transition-all shadow-md cursor-pointer"
        style={{
          background: "var(--bg-surface)",
          borderColor: "var(--bg-border)",
          color: "var(--text-muted)",
        }}
        aria-label={collapsed ? "Expandir sidebar" : "Colapsar sidebar"}
      >
        {collapsed ? <ChevronRight size={10} /> : <ChevronLeft size={10} />}
      </motion.button>
    </motion.aside>
  );
}
