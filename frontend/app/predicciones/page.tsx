"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import ForecastChart from "@/components/predictions/ForecastChart";
import InsightsPanel from "@/components/predictions/InsightsPanel";
import { predictionsApi, insightsApi, scenariosApi } from "@/lib/api";
import { useScenario } from "@/lib/scenarioContext";
import type { Product, PredictionResult, Insight } from "@/lib/types";
import { motion, AnimatePresence } from "framer-motion";
import { BrainCircuit, RefreshCw } from "lucide-react";

const SCENARIO_COLORS: Record<number, string> = { 1: "#E8A04A", 2: "#3DD68C", 3: "#F04438" };
const CATEGORY_COLORS: Record<string, string> = {
  "Tortas frías":    "#4DD9D0", // Celeste / Cyan
  "Tortas Caseras":  "#D4A853", // Dorado Artesanal
};
const CATEGORY_ICONS: Record<string, string> = {
  "Tortas frías":    "🧊",
  "Tortas Caseras":  "🍰",
};

const formatName = (name: string): string => {
  const mapping: Record<string, string> = {
    "3leches":               "3 Leches Tradicional",
    "Helado Sureño":         "Helado Sureño",
    "Beso de amor":          "Torta Beso de Amor",
    "Parchita":              "Torta de Parchita",
    "Dulcemaria":            "Torta Dulcemaría",
    "Marquesa de chocolate": "Marquesa de Chocolate",
    "Chocolate brownie":     "Chocolate Brownie",
    "Piña":                  "Volteado de Piña",
    "Marmoleada":            "Torta Marmoleada",
    "Vainilla":              "Torta de Vainilla",
    "Ovomaltina":            "Torta de Ovomaltina",
    "Zanahoria":             "Torta de Zanahoria",
  };
  return mapping[name] || name;
};

export default function PrediccionesPage() {
  const [products, setProducts]                = useState<Product[]>([]);
  const [selectedId, setSelectedId]            = useState<string>("");
  const [result, setResult]                    = useState<PredictionResult | null>(null);
  const [insights, setInsights]                = useState<Insight[]>([]);
  const [loading, setLoading]                  = useState(false);
  const [error, setError]                      = useState<string | null>(null);
  const [horizon, setHorizon]                  = useState(14);
  const [activeScenario, setActiveScenario]    = useState(1);
  const { refreshKey }                          = useScenario();

  useEffect(() => {
    predictionsApi.products().then((d) => {
      setProducts(d.products);
      if (d.products.length) setSelectedId(d.products[0].id);
    });
    insightsApi.get().then((d) => setInsights(d.insights || []));
    scenariosApi.getActive().then((d) => setActiveScenario(d.id));
  }, [refreshKey]);

  const handlePredict = async () => {
    if (!selectedId) return;
    setLoading(true);
    setError(null);
    try {
      const r = await predictionsApi.predict(selectedId, horizon);
      setResult(r);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const scenarioColor   = SCENARIO_COLORS[activeScenario] || "var(--accent-gold)";
  const selectedProduct = products.find((p) => p.id === selectedId);
  const byCategory: Record<string, Product[]> = {};
  products.forEach((p) => {
    if (!byCategory[p.category]) byCategory[p.category] = [];
    byCategory[p.category].push(p);
  });

  return (
    <AppShell title="Motor Predictivo" subtitle="Pronóstico Random Forest · Newsvendor · ROP Evolutivo">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* ── Left panel: controls ── */}
        <div className="flex flex-col gap-4">

          {/* Product card-picker */}
          <div className="card">
            <p
              className="text-[10px] font-semibold uppercase tracking-wider mb-3"
              style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
            >
              Producto a Pronosticar
            </p>

            {/* Card grid picker by category */}
            <div className="flex flex-col gap-3 mb-4 max-h-60 overflow-y-auto pr-1">
              {Object.entries(byCategory).map(([cat, prods]) => {
                const catColor = CATEGORY_COLORS[cat] || "var(--accent-gold)";
                return (
                  <div key={cat}>
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <span className="text-xs">{CATEGORY_ICONS[cat] || "🍩"}</span>
                      <p
                        className="text-[10px] font-bold uppercase tracking-wider"
                        style={{ color: catColor, fontFamily: "var(--font-mono)" }}
                      >
                        {cat}
                      </p>
                    </div>
                    <div className="grid grid-cols-2 gap-1.5">
                      {prods.map((p) => {
                        const isSelected = p.id === selectedId;
                        return (
                          <motion.button
                            key={p.id}
                            onClick={() => setSelectedId(p.id)}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.97 }}
                            className="text-left px-2.5 py-2 rounded-xl transition-all duration-150"
                            style={{
                              background: isSelected
                                ? `color-mix(in srgb, ${catColor} 14%, transparent)`
                                : "var(--bg-elevated)",
                              border: isSelected
                                ? `1.5px solid ${catColor}`
                                : "1.5px solid var(--bg-border)",
                              boxShadow: isSelected
                                ? `0 0 12px color-mix(in srgb, ${catColor} 25%, transparent)`
                                : "none",
                            }}
                          >
                            <p
                              className="text-xs font-semibold truncate"
                              style={{ color: isSelected ? catColor : "var(--text-primary)" }}
                              title={formatName(p.name)}
                            >
                              {formatName(p.name)}
                            </p>
                            <p
                              className="text-[10px] mt-0.5"
                              style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                            >
                              ${p.price}
                            </p>
                          </motion.button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Horizon selector */}
            <p className="text-[10px] mb-2" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
              Horizonte de pronóstico
            </p>
            <div className="flex gap-2 mb-4">
              {[7, 14, 21].map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizon(h)}
                  className="flex-1 py-1.5 rounded-xl text-xs font-bold transition-all"
                  style={{
                    background: horizon === h
                      ? `color-mix(in srgb, ${scenarioColor} 18%, transparent)`
                      : "var(--bg-elevated)",
                    border: `1px solid ${horizon === h ? scenarioColor : "var(--bg-border)"}`,
                    color: horizon === h ? scenarioColor : "var(--text-muted)",
                    fontFamily: "var(--font-mono)",
                  }}
                >
                  {h}d
                </button>
              ))}
            </div>

            {/* Predict button */}
            <motion.button
              onClick={handlePredict}
              disabled={loading || !selectedId}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold transition-all"
              style={{
                background: loading
                  ? "var(--bg-elevated)"
                  : `linear-gradient(135deg, color-mix(in srgb, ${scenarioColor} 85%, transparent), ${scenarioColor})`,
                color: loading ? "var(--text-muted)" : "var(--bg-base)",
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? (
                <><RefreshCw size={15} className="animate-spin" /> Entrenando modelo...</>
              ) : (
                <><BrainCircuit size={15} /> Generar Pronóstico</>
              )}
            </motion.button>
          </div>

          {/* Model metrics */}
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <p
                className="text-[10px] font-semibold uppercase tracking-wider mb-3"
                style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
              >
                Métricas del Modelo
              </p>
              <div className="flex flex-col gap-2">
                {[
                  { label: "MAPE",     val: `${(result.model.mape_val * 100).toFixed(1)}%`, good: result.model.mape_val < 0.2 },
                  { label: "RMSE",     val: result.model.rmse_val.toFixed(3), good: result.model.rmse_val < 0.5 },
                  { label: "Filas entrenamiento", val: result.model.training_rows.toString(), good: result.model.training_rows > 100 },
                  { label: "ROP",      val: result.reorder.rop.rop.toFixed(2), good: true },
                  { label: "Q* Newsvendor", val: `${result.reorder.newsvendor.q_star_rounded} uds`, good: true },
                  { label: "Nivel Servicio", val: `${(result.reorder.rop.service_level * 100).toFixed(0)}%`, good: true },
                ].map(({ label, val, good }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-xs" style={{ color: "var(--text-muted)" }}>{label}</span>
                    <span
                      className="text-xs font-bold"
                      style={{ fontFamily: "var(--font-mono)", color: good ? scenarioColor : "var(--danger)" }}
                    >
                      {val}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-3 pt-2" style={{ borderTop: "1px solid var(--bg-border)" }}>
                <p className="text-[10px] truncate" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                  v: {result.model.version_tag}
                </p>
              </div>
            </motion.div>
          )}

          {/* Insights */}
          <InsightsPanel insights={insights.slice(0, 3)} scenarioName={`${activeScenario}`} />
        </div>

        {/* ── Right panel: chart + production plan ── */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          {error && (
            <div
              className="p-4 rounded-xl text-sm"
              style={{
                background: "color-mix(in srgb, var(--danger) 10%, transparent)",
                border:     "1px solid color-mix(in srgb, var(--danger) 30%, transparent)",
                color:      "var(--danger)",
              }}
            >
              ⚠️ {error}
            </div>
          )}

          {!result && !loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex-1 flex flex-col items-center justify-center card text-center py-16"
            >
              <div className="text-6xl mb-4">🧠</div>
              <p className="text-sm font-semibold mb-2" style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}>
                Motor listo para pronosticar
              </p>
              <p className="text-xs max-w-xs" style={{ color: "var(--text-muted)" }}>
                Selecciona un producto y haz clic en &ldquo;Generar Pronóstico&rdquo;. El modelo se entrenará con los datos del escenario activo.
              </p>
              <p
                className="text-[11px] mt-4 px-3 py-1.5 rounded-xl"
                style={{
                  background: `color-mix(in srgb, ${scenarioColor} 12%, transparent)`,
                  color: scenarioColor,
                  fontFamily: "var(--font-mono)",
                }}
              >
                Escenario {activeScenario} activo → {activeScenario === 1 ? "~172 días" : activeScenario === 2 ? "~730 días" : "~243 días con anomalías"}
              </p>
            </motion.div>
          )}

          <AnimatePresence>
            {result && (
              <motion.div
                key={result.product.id + result.model.version_tag}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex flex-col gap-4"
              >
                {/* Forecast chart */}
                <ForecastChart
                  forecasts={result.forecasts}
                  productName={result.product.name}
                  mape={result.model.mape_val}
                  scenarioColor={scenarioColor}
                  scenarioId={result.scenario.id}
                  category={selectedProduct?.category}
                />

                {/* Production plan table with heatmap */}
                <div className="card">
                  <p
                    className="text-[10px] font-semibold uppercase tracking-wider mb-3"
                    style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                  >
                    Plan de Producción Recomendado
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr style={{ borderBottom: "1px solid var(--bg-border)" }}>
                          {["Fecha", "Predicción", "Mín (90%)", "Máx (90%)", "Producir"].map((h, idx) => (
                            <th
                              key={h}
                              className={`py-2 font-medium ${idx === 0 ? "text-left" : "text-center"}`}
                              style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                            >
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.forecasts.slice(0, 7).map((f, i) => {
                          const recommended = Math.ceil(f.upper);
                          const date = new Date(f.forecast_date);
                          const isWeekend = date.getDay() === 0 || date.getDay() === 6;
                          const isPayday  = [14, 15, 28, 29, 30, 31].includes(date.getDate());
                          return (
                            <motion.tr
                              key={f.forecast_date}
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              transition={{ delay: i * 0.05 }}
                              style={{
                                borderBottom: i < 6 ? "1px solid var(--bg-border)" : "none",
                                background: isWeekend
                                  ? "color-mix(in srgb, var(--accent-gold) 5%, transparent)"
                                  : isPayday
                                  ? "color-mix(in srgb, var(--success) 5%, transparent)"
                                  : "transparent",
                              }}
                            >
                              <td className="py-2" style={{ fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
                                <span>{f.forecast_date}</span>
                                {isWeekend && (
                                  <span
                                    className="ml-1.5 text-[8px] font-bold px-1 py-0.5 rounded"
                                    style={{ background: "color-mix(in srgb, var(--accent-gold) 15%, transparent)", color: "var(--accent-gold)" }}
                                  >
                                    FDS
                                  </span>
                                )}
                                {isPayday && (
                                  <span
                                    className="ml-1 text-[8px] font-bold px-1 py-0.5 rounded"
                                    style={{ background: "color-mix(in srgb, var(--success) 15%, transparent)", color: "var(--success)" }}
                                  >
                                    QUINCENA
                                  </span>
                                )}
                              </td>
                              <td className="text-center font-bold" style={{ fontFamily: "var(--font-mono)", color: scenarioColor }}>
                                {f.predicted.toFixed(2)}
                              </td>
                              <td className="text-center" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                                {f.lower.toFixed(2)}
                              </td>
                              <td className="text-center" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                                {f.upper.toFixed(2)}
                              </td>
                              <td className="text-center">
                                <span
                                  className="font-bold px-2 py-0.5 rounded-lg"
                                  style={{
                                    fontFamily: "var(--font-mono)",
                                    background: `color-mix(in srgb, ${scenarioColor} 18%, transparent)`,
                                    color: scenarioColor,
                                  }}
                                >
                                  {recommended}
                                </span>
                              </td>
                            </motion.tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                  <p className="text-[10px] mt-3" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                    💡 &ldquo;Producir&rdquo; = techo del intervalo superior. Garantiza servicio del {(result.reorder.rop.service_level * 100).toFixed(0)}%.
                    <span className="ml-2" style={{ color: "var(--accent-gold)" }}>■</span> Fin de semana
                    <span className="ml-2" style={{ color: "var(--success)" }}>■</span> Quincena
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </AppShell>
  );
}
