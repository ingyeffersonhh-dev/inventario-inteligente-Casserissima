"use client";
import { useState, useEffect } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";
import type { ForecastPoint } from "@/lib/types";
import { motion } from "framer-motion";

interface ForecastChartProps {
  forecasts:      ForecastPoint[];
  productName:    string;
  mape?:          number;
  scenarioColor?: string;
  scenarioId?:    number;
  category?:      string;
}

const SCENARIO_LABELS: Record<number, string> = {
  1: "Escenario Corto — Intervalos amplios (< 6 meses)",
  2: "Escenario Óptimo — Alta precisión (2 años de historia)",
  3: "Escenario Crítico — Alta incertidumbre (anomalías)",
};

const CATEGORY_COLORS: Record<string, string> = {
  "Tortas frías":    "#4DD9D0", // Celeste / Cyan
  "Tortas Caseras":  "#D4A853", // Dorado Artesanal
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

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  const p = payload[0]?.payload;
  return (
    <div
      className="rounded-xl px-4 py-3 text-xs"
      style={{
        background:  "var(--bg-elevated)",
        border:      "1px solid var(--bg-border)",
        boxShadow:   "var(--shadow-lg)",
        fontFamily:  "var(--font-mono)",
        minWidth:    "180px",
      }}
    >
      <p
        className="font-semibold mb-2"
        style={{ color: "var(--text-primary)", fontFamily: "var(--font-body)", fontSize: "11px" }}
      >
        📅 {label}
        {p?.isWeekend && <span className="ml-2 text-[9px] font-mono px-1 py-0.5 rounded" style={{ background: "color-mix(in srgb, var(--accent-gold) 15%, transparent)", color: "var(--accent-gold)" }}>FIN DE SEM.</span>}
        {p?.isPayday && <span className="ml-1 text-[9px] font-mono px-1 py-0.5 rounded" style={{ background: "color-mix(in srgb, var(--success) 15%, transparent)", color: "var(--success)" }}>QUINCENA</span>}
      </p>
      <div className="flex flex-col gap-1">
        <div className="flex justify-between gap-6">
          <span style={{ color: "var(--text-muted)" }}>Predicción</span>
          <span className="font-bold" style={{ color: "var(--accent-gold)" }}>{p?.predicted?.toFixed(2)} uds</span>
        </div>
        <div className="flex justify-between gap-6">
          <span style={{ color: "var(--text-muted)" }}>Rango 90%</span>
          <span style={{ color: "var(--text-secondary)" }}>{p?.lower?.toFixed(2)} – {p?.upper?.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};

export default function ForecastChart({
  forecasts, productName, mape, scenarioColor = "var(--accent-gold)", scenarioId, category,
}: ForecastChartProps) {
  const [isMounted, setIsMounted] = useState(false);
  
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const avgDemand = forecasts.length
    ? forecasts.reduce((s, f) => s + f.predicted, 0) / forecasts.length
    : 0;

  const catColor = (category && CATEGORY_COLORS[category]) || scenarioColor;

  const chartData = forecasts.map((f, idx) => {
    const date = new Date(f.forecast_date);
    const dayOfWeek = date.getDay();
    return {
      date:      f.forecast_date.slice(5),
      predicted: f.predicted,
      lower:     f.lower,
      upper:     f.upper,
      isWeekend: dayOfWeek === 0 || dayOfWeek === 6,
      isPayday:  [14, 15, 28, 29, 30, 31].includes(date.getDate()),
    };
  });

  const mapeColor = !mape ? "var(--text-muted)"
    : mape < 0.2  ? "var(--success)"
    : mape < 0.45 ? "var(--warning)"
    : "var(--danger)";

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h3
              className="text-sm font-bold"
              style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
            >
              {formatName(productName)}
            </h3>
            {category && (
              <span
                className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                style={{
                  background: `color-mix(in srgb, ${catColor} 15%, transparent)`,
                  color: catColor,
                  fontFamily: "var(--font-mono)",
                }}
              >
                {category.replace("Tortas ", "")}
              </span>
            )}
          </div>
          <p className="text-xs" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            Pronóstico {forecasts.length} días · Intervalo de confianza 90%
          </p>
          {scenarioId && (
            <p className="text-[10px] mt-1" style={{ color: scenarioColor, fontFamily: "var(--font-mono)" }}>
              {SCENARIO_LABELS[scenarioId]}
            </p>
          )}
        </div>
        <div className="text-right">
          <p
            className="text-xl font-bold"
            style={{ fontFamily: "var(--font-mono)", color: scenarioColor }}
          >
            {avgDemand.toFixed(2)}
          </p>
          <p className="text-[10px]" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            ud/día promedio
          </p>
          {mape !== undefined && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-[11px] font-bold mt-1"
              style={{ color: mapeColor, fontFamily: "var(--font-mono)" }}
            >
              MAPE {(mape * 100).toFixed(1)}%
            </motion.p>
          )}
        </div>
      </div>

      {/* Chart */}
      <div style={{ height: 250, width: "100%" }}>
      {isMounted && (
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
            <defs>
            {/* Confidence band gradient */}
            <linearGradient id="bandGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor={scenarioColor} stopOpacity={0.18} />
              <stop offset="100%" stopColor={scenarioColor} stopOpacity={0.03} />
            </linearGradient>
            {/* Prediction line fill */}
            <linearGradient id="predGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor={scenarioColor} stopOpacity={0.35} />
              <stop offset="100%" stopColor={scenarioColor} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--bg-border)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={avgDemand}
            stroke={scenarioColor}
            strokeDasharray="5 4"
            strokeOpacity={0.45}
            label={{ value: "media", fill: "var(--text-muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
          />
          {/* Confidence band — upper fill */}
          <Area
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="url(#bandGrad)"
            isAnimationActive={true}
            animationDuration={900}
          />
          {/* Confidence band — lower fill (masks to create band effect) */}
          <Area
            type="monotone"
            dataKey="lower"
            stroke="none"
            fill="var(--bg-surface)"
            isAnimationActive={true}
            animationDuration={900}
          />
          {/* Prediction line */}
          <Area
            type="monotone"
            dataKey="predicted"
            stroke={scenarioColor}
            strokeWidth={2.5}
            fill="url(#predGrad)"
            dot={{ fill: scenarioColor, r: 3, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: scenarioColor, stroke: "var(--bg-base)", strokeWidth: 2 }}
            isAnimationActive={true}
            animationDuration={1100}
          />
        </AreaChart>
      </ResponsiveContainer>
      )}
      </div>

      {/* Legend */}
      <div className="flex gap-5 mt-2 justify-center">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-[2px] rounded" style={{ background: scenarioColor }} />
          <span className="text-[10px]" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>Predicción central</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm opacity-50" style={{ background: scenarioColor }} />
          <span className="text-[10px]" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>Intervalo 90%</span>
        </div>
      </div>
    </div>
  );
}
