"use client";
import { motion } from "framer-motion";
import type { Insight } from "@/lib/types";

const PRIORITY_CONFIG = {
  critical: { bg: "color-mix(in srgb, var(--danger)  10%, transparent)", border: "color-mix(in srgb, var(--danger)  30%, transparent)", bar: "var(--danger)",  label: "CRÍTICO" },
  high:     { bg: "color-mix(in srgb, var(--warning)  9%, transparent)", border: "color-mix(in srgb, var(--warning) 28%, transparent)", bar: "var(--warning)", label: "ALTO"    },
  medium:   { bg: "color-mix(in srgb, var(--warning)  7%, transparent)", border: "color-mix(in srgb, var(--warning) 18%, transparent)", bar: "var(--warning)", label: "MEDIO"   },
  info:     { bg: "color-mix(in srgb, var(--info)      7%, transparent)", border: "color-mix(in srgb, var(--info)    15%, transparent)", bar: "var(--info)",    label: "INFO"    },
};

interface InsightsPanelProps {
  insights:     Insight[];
  scenarioName?: string;
}

export default function InsightsPanel({ insights, scenarioName }: InsightsPanelProps) {
  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center gap-2.5 mb-4">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{
            background: "color-mix(in srgb, var(--accent-gold) 12%, transparent)",
            border:     "1px solid color-mix(in srgb, var(--accent-gold) 25%, transparent)",
          }}
        >
          🧠
        </div>
        <div>
          <h3
            className="text-sm font-semibold"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
          >
            Insights IA
          </h3>
          <p className="text-xs" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            {scenarioName ? `Escenario ${scenarioName}` : "Recomendaciones contextuales"}
          </p>
        </div>
      </div>

      {/* Insights list */}
      <div className="flex flex-col gap-2.5">
        {insights.slice(0, 5).map((insight, i) => {
          const cfg = PRIORITY_CONFIG[insight.priority];
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07, ease: [0.22, 1, 0.36, 1] }}
              className="relative rounded-xl p-3 overflow-hidden"
              style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}
            >
              {/* Left accent bar */}
              <div
                className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl"
                style={{ background: cfg.bar }}
              />
              <div className="pl-3">
                <div className="flex items-start gap-2 mb-1">
                  <span className="text-sm flex-shrink-0">{insight.icon}</span>
                  <p
                    className="text-xs font-semibold flex-1"
                    style={{ color: "var(--text-primary)" }}
                  >
                    {insight.title}
                  </p>
                  <span
                    className="text-[9px] font-bold px-1.5 py-0.5 rounded flex-shrink-0"
                    style={{
                      background: `color-mix(in srgb, ${cfg.bar} 18%, transparent)`,
                      color: cfg.bar,
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    {cfg.label}
                  </span>
                </div>
                <p
                  className="text-[11px] leading-snug mb-1.5"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {insight.message}
                </p>
                <p
                  className="text-[10px] font-semibold"
                  style={{ color: cfg.bar, fontFamily: "var(--font-mono)" }}
                >
                  → {insight.action}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
