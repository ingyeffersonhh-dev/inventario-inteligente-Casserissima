"use client";
import { motion } from "framer-motion";
import type { IngredientStatus } from "@/lib/types";
import { AlertTriangle, CheckCircle, AlertCircle } from "lucide-react";

interface StockAlertsProps {
  ingredients:   IngredientStatus[];
  criticalCount: number;
  warningCount:  number;
}

const STATUS_CONFIG = {
  ok:       { icon: CheckCircle,   color: "var(--success)",  label: "OK",      pulse: false },
  warning:  { icon: AlertTriangle, color: "var(--warning)",  label: "BAJO",    pulse: false },
  critical: { icon: AlertCircle,   color: "var(--danger)",   label: "CRÍTICO", pulse: true  },
};

/** Inline SVG semicircular gauge */
function Gauge({ pct, color }: { pct: number; color: string }) {
  const r = 16;
  const circ = Math.PI * r; // half circle circumference
  const dash = (pct / 100) * circ;
  return (
    <svg width="40" height="22" viewBox="0 0 40 22" fill="none" className="flex-shrink-0">
      {/* Track */}
      <path
        d="M4 20 A16 16 0 0 1 36 20"
        stroke="var(--bg-border)"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
      />
      {/* Fill */}
      <path
        d="M4 20 A16 16 0 0 1 36 20"
        stroke={color}
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
        strokeDasharray={`${dash} ${circ}`}
        style={{ transition: "stroke-dasharray 0.6s ease" }}
      />
    </svg>
  );
}

export default function StockAlerts({ ingredients, criticalCount, warningCount }: StockAlertsProps) {
  const sorted = [...ingredients].sort((a, b) => a.ratio - b.ratio);

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3
            className="text-sm font-semibold"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
          >
            Inventario de Insumos
          </h3>
          <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            Estado actual de materia prima
          </p>
        </div>
        <div className="flex gap-2">
          {criticalCount > 0 && (
            <span
              className="text-[10px] font-bold px-2 py-0.5 rounded-full badge-critical pulse-glow"
            >
              {criticalCount} CRÍTICO{criticalCount > 1 ? "S" : ""}
            </span>
          )}
          {warningCount > 0 && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full badge-warning">
              {warningCount} BAJO{warningCount > 1 ? "S" : ""}
            </span>
          )}
          {criticalCount === 0 && warningCount === 0 && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full badge-ok">
              TODO OK
            </span>
          )}
        </div>
      </div>

      {/* Ingredients list */}
      <div className="flex flex-col gap-2">
        {sorted.map((ing, i) => {
          const cfg = STATUS_CONFIG[ing.status];
          const Icon = cfg.icon;
          const fillPct = Math.min(100, (ing.current_stock / (ing.alert_threshold * 3)) * 100);

          return (
            <motion.div
              key={ing.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04, ease: [0.22, 1, 0.36, 1] }}
              className="flex items-center gap-3 p-2.5 rounded-xl"
              style={{
                background: `color-mix(in srgb, ${cfg.color} 7%, transparent)`,
                border:     `1px solid color-mix(in srgb, ${cfg.color} 18%, transparent)`,
              }}
            >
              {/* Gauge */}
              <Gauge pct={fillPct} color={cfg.color} />

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-0.5">
                  <div className="flex items-center gap-1.5">
                    <Icon size={12} style={{ color: cfg.color, flexShrink: 0 }} />
                    <p
                      className="text-xs font-medium truncate"
                      style={{ color: "var(--text-primary)" }}
                    >
                      {ing.name}
                    </p>
                  </div>
                  <span
                    className="text-[10px] ml-2 flex-shrink-0"
                    style={{ fontFamily: "var(--font-mono)", color: cfg.color }}
                  >
                    {ing.current_stock.toFixed(1)} {ing.unit}
                  </span>
                </div>
                <div
                  className="h-1 rounded-full overflow-hidden"
                  style={{ background: "var(--bg-elevated)" }}
                >
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${fillPct}%` }}
                    transition={{ duration: 0.55, delay: i * 0.05 }}
                    className={`h-full rounded-full ${cfg.pulse ? "pulse-glow" : ""}`}
                    style={{ background: cfg.color }}
                  />
                </div>
              </div>

              {/* Badge */}
              <span
                className="text-[9px] font-bold px-1.5 py-0.5 rounded flex-shrink-0"
                style={{
                  background: `color-mix(in srgb, ${cfg.color} 18%, transparent)`,
                  color: cfg.color,
                  fontFamily: "var(--font-mono)",
                }}
              >
                {cfg.label}
              </span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
