"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { scenariosApi } from "@/lib/api";
import type { ScenarioMeta } from "@/lib/types";

interface ScenarioSwitcherProps {
  onScenarioChange?: (id: number) => void;
}

const SCENARIO_ICONS = { 1: "📅", 2: "🏆", 3: "⚡" };
const SCENARIO_COLORS = {
  1: { border: "var(--scenario-1)", bg: "color-mix(in srgb, var(--scenario-1) 8%, transparent)", text: "var(--scenario-1)", glow: "color-mix(in srgb, var(--scenario-1) 20%, transparent)" },
  2: { border: "var(--scenario-2)", bg: "color-mix(in srgb, var(--scenario-2) 8%, transparent)", text: "var(--scenario-2)", glow: "color-mix(in srgb, var(--scenario-2) 20%, transparent)" },
  3: { border: "var(--scenario-3)", bg: "color-mix(in srgb, var(--scenario-3) 8%, transparent)", text: "var(--scenario-3)", glow: "color-mix(in srgb, var(--scenario-3) 20%, transparent)" },
};

export default function ScenarioSwitcher({ onScenarioChange }: ScenarioSwitcherProps) {
  const [scenarios, setScenarios] = useState<ScenarioMeta[]>([]);
  const [activeId, setActiveId]   = useState<number>(1);
  const [loading, setLoading]     = useState(false);
  const [open, setOpen]           = useState(false);

  useEffect(() => {
    scenariosApi.list().then((data) => {
      setScenarios(data.scenarios);
      setActiveId(data.active_scenario_id);
    });
  }, []);

  const active = scenarios.find((s) => s.id === activeId);
  const colors = SCENARIO_COLORS[activeId as 1 | 2 | 3] || SCENARIO_COLORS[1];

  const handleSwitch = async (id: number) => {
    if (id === activeId || loading) return;
    setLoading(true);
    try {
      await scenariosApi.switch(id);
      setActiveId(id);
      onScenarioChange?.(id);
      setOpen(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative">
      {/* Trigger button */}
      <motion.button
        onClick={() => setOpen((v) => !v)}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        style={{
          background: colors.bg,
          border: `1px solid ${colors.border}`,
          boxShadow: open ? `0 0 16px ${colors.glow}` : "none",
        }}
        className="flex items-center gap-2 px-3 py-1.5 rounded-xl transition-all duration-200 cursor-pointer"
      >
        <span className="text-sm">{SCENARIO_ICONS[activeId as 1|2|3]}</span>
        <span className="text-xs font-semibold" style={{ color: colors.text, fontFamily: "var(--font-mono)" }}>
          {loading ? "Cambiando..." : `Esc. ${activeId}: ${active?.name || "..."}`}
        </span>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-[10px]"
          style={{ color: colors.text }}
        >
          ▾
        </motion.span>
      </motion.button>

      {/* Dropdown panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.97 }}
            transition={{ duration: 0.18 }}
            className="absolute right-0 top-12 w-[360px] z-50 rounded-xl overflow-hidden"
            style={{
              background: "var(--bg-surface)",
              border:     "1px solid var(--bg-border)",
              boxShadow:  "var(--shadow-lg)",
            }}
          >
            <div className="px-4 py-3" style={{ borderBottom: "1px solid var(--bg-border)" }}>
              <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                Modo de Demostración
              </p>
              <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
                Cambia el dataset activo en tiempo real
              </p>
            </div>

            <div className="p-2 flex flex-col gap-1.5">
              {scenarios.map((s) => {
                const sc = SCENARIO_COLORS[s.id as 1 | 2 | 3];
                const isActive = s.id === activeId;
                return (
                  <motion.button
                    key={s.id}
                    onClick={() => handleSwitch(s.id)}
                    whileHover={{ x: 2 }}
                    disabled={loading}
                    style={{
                      background: isActive ? sc.bg : "transparent",
                      border: `1px solid ${isActive ? sc.border : "transparent"}`,
                    }}
                    className="w-full text-left px-3 py-2.5 rounded-xl transition-all duration-150 disabled:opacity-50 cursor-pointer"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-base">{SCENARIO_ICONS[s.id as 1|2|3]}</span>
                      <span
                        className="text-sm font-semibold"
                        style={{ color: isActive ? sc.text : "var(--text-primary)" }}
                      >
                        {s.name}
                      </span>
                      {isActive && (
                        <span
                          className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full"
                          style={{ background: sc.bg, color: sc.text, border: `1px solid ${sc.border}`, fontFamily: "var(--font-mono)" }}
                        >
                          ACTIVO
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] leading-snug pl-6" style={{ color: "var(--text-muted)" }}>
                      {s.description.slice(0, 90)}…
                    </p>
                    <div className="flex gap-3 mt-1.5 pl-6">
                      <span className="text-[10px]" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                        📊 {s.days} días de historia
                      </span>
                    </div>
                  </motion.button>
                );
              })}
            </div>

            <div className="px-4 py-2.5" style={{ borderTop: "1px solid var(--bg-border)" }}>
              <p className="text-[10px]" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                💡 Al cambiar, dashboard y predicciones se actualizan automáticamente
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setOpen(false)}
        />
      )}
    </div>
  );
}
