"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import KPICard from "@/components/dashboard/KPICard";
import { getBacktestSummary } from "@/lib/api";
import type { BacktestSummary } from "@/lib/types";
import { motion } from "framer-motion";
import { RefreshCw } from "lucide-react";

// ── Formatting helpers ───────────────────────────────────────────────────────
// waste_pct_* and fill_rate_* arrive as fractions (0..1) and are shown as %.
const pct = (frac: number, decimals = 2) => (frac * 100).toFixed(decimals);
// waste_reduction_pct is ALREADY a percentage number (e.g. 12.65).
const pctRaw = (val: number, decimals = 2) => val.toFixed(decimals);
const signedPct = (frac: number, decimals = 2) =>
  (frac >= 0 ? "+" : "") + (frac * 100).toFixed(decimals);

// Friendly product name mapping (mirrors predicciones/page.tsx convention).
const formatName = (name: string): string => {
  const mapping: Record<string, string> = {
    "3leches": "3 Leches Tradicional",
    "Helado Sureño": "Helado Sureño",
    "Beso de amor": "Torta Beso de Amor",
  };
  return mapping[name] || name;
};

export default function ValidacionPage() {
  const [data, setData] = useState<BacktestSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [key, setKey] = useState(0);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getBacktestSummary()
      .then((d) => setData(d))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [key]);

  const agg = data?.aggregated;
  const rows = data?.aggregated_table ?? [];

  return (
    <AppShell title="Validación Walk-Forward" subtitle="">
      {/* Refresh banner */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-5 rounded-xl px-4 py-3 flex items-center gap-3"
        style={{
          background: "color-mix(in srgb, var(--success) 7%, transparent)",
          border: "1px solid color-mix(in srgb, var(--success) 22%, transparent)",
        }}
      >
        <div
          className="w-2 h-2 rounded-full flex-shrink-0 pulse-glow"
          style={{ background: "var(--success)" }}
        />
        <p className="text-xs flex-1" style={{ color: "var(--text-secondary)" }}>
          <strong style={{ color: "var(--success)", fontFamily: "var(--font-mono)" }}>Backtesting</strong>
          {" — "}validación walk-forward del escenario óptimo
        </p>
        <button
          onClick={() => setKey((k) => k + 1)}
          className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-xl transition-all hover:opacity-80"
          style={{
            background: "color-mix(in srgb, var(--success) 15%, transparent)",
            color: "var(--success)",
            border: "1px solid color-mix(in srgb, var(--success) 30%, transparent)",
            fontFamily: "var(--font-mono)",
          }}
        >
          <RefreshCw size={11} />
          Actualizar
        </button>
      </motion.div>

      {/* Error card */}
      {error && (
        <div
          className="mb-4 p-4 rounded-xl text-sm"
          style={{
            background: "color-mix(in srgb, var(--danger) 10%, transparent)",
            border: "1px solid color-mix(in srgb, var(--danger) 30%, transparent)",
            color: "var(--danger)",
          }}
        >
          No hay datos de validación disponibles.
        </div>
      )}

      {/* Loading skeleton */}
      {loading && !data && (
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="card animate-pulse" style={{ height: 132 }} />
            ))}
          </div>
          <div className="card animate-pulse" style={{ height: 320 }} />
        </div>
      )}

      {data && agg && (
        <>
          {/* ── Aggregated KPI cards ── */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
            <KPICard
              label="Reducción de Merma"
              value={pctRaw(agg.mean_waste_reduction_pct)}
              suffix="%"
              icon="📉"
              color="var(--success)"
              index={0}
              animate={!loading}
            />
            <KPICard
              label="Merma del Sistema"
              value={pct(agg.mean_waste_pct_system)}
              suffix="%"
              icon="🗑️"
              color="#F04438"
              index={1}
              animate={!loading}
            />
            <KPICard
              label="Merma Baseline (Pastelero)"
              value={pct(agg.mean_waste_pct_baseline)}
              suffix="%"
              icon="🥖"
              color="var(--text-secondary)"
              index={2}
              animate={!loading}
            />
            <KPICard
              label="Fill Rate del Sistema"
              value={pct(agg.mean_fill_rate_system)}
              suffix="%"
              icon="📦"
              color="#4DD9D0"
              index={3}
              animate={!loading}
            />
          </div>

          {/* ── Per-product comparison bars ── */}
          <div className="card mb-4">
            <p
              className="text-[10px] font-semibold uppercase tracking-wider mb-4"
              style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
            >
              Merma por Producto — Sistema vs Baseline (Pastelero)
            </p>
            <div className="flex flex-col gap-5">
              {rows.map((r, i) => {
                const sysW = Math.min(Math.max(r.waste_pct_system * 100, 2), 100);
                const baseW = Math.min(Math.max(r.waste_pct_baseline * 100, 2), 100);
                return (
                  <motion.div
                    key={r.product_id}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span
                        className="text-xs font-semibold"
                        style={{ color: "var(--text-primary)" }}
                      >
                        {formatName(r.name)}
                      </span>
                      <span
                        className="text-[10px] font-bold"
                        style={{ color: "var(--success)", fontFamily: "var(--font-mono)" }}
                      >
                        {r.waste_reduction_pct > 0
                          ? `-${pctRaw(r.waste_reduction_pct, 2)}%`
                          : r.waste_reduction_pct < 0
                            ? `+${pctRaw(Math.abs(r.waste_reduction_pct), 2)}%`
                            : "0.00%"}
                      </span>
                    </div>

                    {/* Sistema bar */}
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className="text-[10px] w-14 flex-shrink-0"
                        style={{ color: "var(--success)", fontFamily: "var(--font-mono)" }}
                      >
                        Sistema
                      </span>
                      <div className="flex-1 rounded-full overflow-hidden" style={{ background: "var(--bg-elevated)", height: 14 }}>
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${sysW}%` }}
                          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: i * 0.08 }}
                          className="h-full rounded-full"
                          style={{ background: "var(--success)" }}
                        />
                      </div>
                      <span
                        className="text-[10px] w-12 text-right"
                        style={{ color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}
                      >
                        {pct(r.waste_pct_system)}%
                      </span>
                    </div>

                    {/* Baseline bar */}
                    <div className="flex items-center gap-2">
                      <span
                        className="text-[10px] w-14 flex-shrink-0"
                        style={{ color: "var(--danger)", fontFamily: "var(--font-mono)" }}
                      >
                        Baseline
                      </span>
                      <div className="flex-1 rounded-full overflow-hidden" style={{ background: "var(--bg-elevated)", height: 14 }}>
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${baseW}%` }}
                          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: i * 0.08 + 0.1 }}
                          className="h-full rounded-full"
                          style={{ background: "var(--danger)" }}
                        />
                      </div>
                      <span
                        className="text-[10px] w-12 text-right"
                        style={{ color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}
                      >
                        {pct(r.waste_pct_baseline)}%
                      </span>
                    </div>
                  </motion.div>
                );
              })}
            </div>
            <p className="text-[10px] mt-4" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
              <span className="mr-3" style={{ color: "var(--success)" }}>■</span> Merma del sistema
              <span className="ml-2 mr-3" style={{ color: "var(--danger)" }}>■</span> Merma baseline (regla del pastelero)
            </p>
          </div>

          {/* ── Per-product table ── */}
          <div className="card">
            <p
              className="text-[10px] font-semibold uppercase tracking-wider mb-3"
              style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
            >
              Métricas por Producto (Walk-Forward)
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--bg-border)" }}>
                    {[
                      "Producto", "Categoría", "Vida Útil", "Merma Sistema", "Merma Baseline",
                      "Reducción", "Fill Rate Sistema", "Fill Rate Baseline", "Δ Fill Rate",
                    ].map((h, idx) => (
                      <th
                        key={h}
                        className={`py-2 font-medium ${idx <= 1 ? "text-left" : "text-center"}`}
                        style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)", whiteSpace: "nowrap" }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => {
                    const reducColor = r.waste_reduction_pct > 0 ? "var(--success)" : "var(--danger)";
                    const deltaFrac = r.fill_rate_delta;
                    const deltaColor = deltaFrac >= 0 ? "var(--success)" : "var(--danger)";
                    return (
                      <motion.tr
                        key={r.product_id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.05 }}
                        style={{ borderBottom: i < rows.length - 1 ? "1px solid var(--bg-border)" : "none" }}
                      >
                        <td className="py-2 pr-3" style={{ color: "var(--text-primary)" }}>
                          {formatName(r.name)}
                        </td>
                        <td className="py-2 pr-3" style={{ color: "var(--text-muted)" }}>
                          {r.category}
                        </td>
                        <td className="py-2 text-center" style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
                          {r.shelf_life_days}d
                        </td>
                        <td className="py-2 text-center font-semibold" style={{ fontFamily: "var(--font-mono)", color: "var(--success)" }}>
                          {pct(r.waste_pct_system)}%
                        </td>
                        <td className="py-2 text-center" style={{ fontFamily: "var(--font-mono)", color: "var(--danger)" }}>
                          {pct(r.waste_pct_baseline)}%
                        </td>
                        <td
                          className="py-2 text-center font-bold"
                          style={{ fontFamily: "var(--font-mono)", color: reducColor }}
                        >
                          {r.waste_reduction_pct > 0
                            ? `-${pctRaw(r.waste_reduction_pct, 2)}%`
                            : r.waste_reduction_pct < 0
                              ? `+${pctRaw(Math.abs(r.waste_reduction_pct), 2)}%`
                              : "0.00%"}
                        </td>
                        <td className="py-2 text-center" style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
                          {pct(r.fill_rate_system)}%
                        </td>
                        <td className="py-2 text-center" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                          {pct(r.fill_rate_baseline)}%
                        </td>
                        <td
                          className="py-2 text-center font-bold"
                          style={{ fontFamily: "var(--font-mono)", color: deltaColor }}
                        >
                          {signedPct(deltaFrac)}%
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}