"use client";
import { useState, useEffect } from "react";
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Cell,
} from "recharts";
import type { SalesTrendItem } from "@/lib/types";
import { motion } from "framer-motion";
import { BarChart2, TrendingUp } from "lucide-react";

interface SalesChartProps {
  data: SalesTrendItem[];
  scenarioColor?: string;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  const rev   = payload.find((p: any) => p.dataKey === "revenue");
  const units = payload.find((p: any) => p.dataKey === "units");
  return (
    <div
      className="rounded-xl px-4 py-3 text-xs"
      style={{
        background:    "var(--bg-elevated)",
        border:        "1px solid var(--bg-border)",
        boxShadow:     "var(--shadow-lg)",
        fontFamily:    "var(--font-mono)",
        minWidth:      "160px",
      }}
    >
      <p
        className="font-semibold mb-2 text-[11px]"
        style={{ color: "var(--text-primary)", fontFamily: "var(--font-body)" }}
      >
        {label}
      </p>
      {rev && (
        <div className="flex items-center justify-between gap-4 mb-1">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-sm" style={{ background: rev.fill }} />
            <span style={{ color: "var(--text-secondary)" }}>Ingresos</span>
          </div>
          <span className="font-bold" style={{ color: "var(--text-primary)" }}>
            ${rev.value?.toFixed(0)}
          </span>
        </div>
      )}
      {units && (
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ background: units.stroke }} />
            <span style={{ color: "var(--text-secondary)" }}>Unidades</span>
          </div>
          <span className="font-bold" style={{ color: "var(--text-primary)" }}>
            {units.value?.toFixed(1)}
          </span>
        </div>
      )}
    </div>
  );
};

const CustomLegend = ({ items }: { items: { color: string; label: string; type: "bar" | "line" }[] }) => (
  <div className="flex gap-5 mt-3 justify-center">
    {items.map((item) => (
      <div key={item.label} className="flex items-center gap-1.5">
        {item.type === "bar" ? (
          <div className="w-3 h-3 rounded-sm" style={{ background: item.color }} />
        ) : (
          <div className="flex items-center gap-0.5">
            <div className="w-2 h-[2px]" style={{ background: item.color }} />
            <div className="w-1.5 h-1.5 rounded-full" style={{ background: item.color }} />
            <div className="w-2 h-[2px]" style={{ background: item.color }} />
          </div>
        )}
        <span className="text-xs" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
          {item.label}
        </span>
      </div>
    ))}
  </div>
);

export default function SalesChart({ data, scenarioColor = "var(--accent-gold)" }: SalesChartProps) {
  const [view, setView] = useState<"revenue" | "units">("revenue");
  const [isMounted, setIsMounted] = useState(false);
  
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const avg = data.length ? data.reduce((s, d) => s + d.revenue, 0) / data.length : 0;
  const maxRev = data.length ? Math.max(...data.map((d) => d.revenue)) : 1;

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3
            className="text-sm font-semibold"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
          >
            Tendencia de Ventas
          </h3>
          <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            Ingresos y unidades semanales
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
            Prom. ${avg.toFixed(0)}/sem
          </span>
          {/* View toggle */}
          <div
            className="flex gap-1 p-1 rounded-lg"
            style={{ background: "var(--bg-elevated)" }}
          >
            {[
              { id: "revenue" as const, icon: BarChart2, title: "Ingresos" },
              { id: "units" as const, icon: TrendingUp, title: "Unidades" },
            ].map(({ id, icon: Icon, title }) => (
              <motion.button
                key={id}
                onClick={() => setView(id)}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-semibold transition-all"
                style={{
                  background: view === id ? scenarioColor : "transparent",
                  color: view === id ? "var(--bg-base)" : "var(--text-muted)",
                }}
                title={title}
              >
                <Icon size={11} />
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div style={{ height: 220, width: "100%" }}>
      {isMounted && (
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={scenarioColor} stopOpacity={0.95} />
              <stop offset="100%" stopColor={scenarioColor} stopOpacity={0.45} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--bg-border)" vertical={false} />
          <XAxis
            dataKey="week"
            tick={{ fill: "var(--text-muted)", fontSize: 10 }}
            tickFormatter={(v) => v.replace(/\d{4}-/, "")}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "var(--text-muted)", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => view === "revenue" ? `$${v}` : `${v}`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
          <ReferenceLine
            y={avg}
            stroke={scenarioColor}
            strokeDasharray="5 4"
            strokeOpacity={0.45}
          />
          <Bar
            dataKey={view === "revenue" ? "revenue" : "units"}
            name={view}
            fill="url(#barGrad)"
            radius={[5, 5, 0, 0]}
            maxBarSize={48}
          >
            {data.map((entry, i) => (
              <Cell
                key={`cell-${i}`}
                fill={`url(#barGrad)`}
                opacity={entry.revenue === maxRev ? 1 : 0.78}
              />
            ))}
          </Bar>
          <Line
            dataKey={view === "revenue" ? "units" : "revenue"}
            stroke={scenarioColor}
            strokeWidth={2}
            strokeOpacity={0.4}
            dot={{ fill: scenarioColor, r: 2.5, strokeWidth: 0 }}
            activeDot={{ r: 4, fill: scenarioColor, stroke: "var(--bg-base)", strokeWidth: 2 }}
            type="monotone"
          />
        </ComposedChart>
      </ResponsiveContainer>
      )}
      </div>

      <CustomLegend
        items={[
          { color: scenarioColor, label: view === "revenue" ? "Ingresos" : "Unidades", type: "bar" },
          { color: scenarioColor, label: view === "revenue" ? "Tendencia uds." : "Tendencia $", type: "line" },
        ]}
      />
    </div>
  );
}
