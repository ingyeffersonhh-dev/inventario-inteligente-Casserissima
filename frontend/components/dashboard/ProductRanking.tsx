"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { PieChart, Pie, Cell, Tooltip, Label } from "recharts";
import type { TopProductItem } from "@/lib/types";

const CATEGORY_COLORS: Record<string, string> = {
  "Tortas frías":    "#4DD9D0", // Cyan / Celeste
  "Tortas Caseras":  "#D4A853", // Dorado Artesanal
};

const CATEGORY_ICONS: Record<string, string> = {
  "Tortas frías":    "🧊",
  "Tortas Caseras":  "🍰",
};

interface ProductRankingProps {
  products: TopProductItem[];
}

const formatName = (name: string): string => {
  const mapping: Record<string, string> = {
    "3leches":               "3 Leches",
    "Helado Sureño":         "Helado Sureño",
    "Beso de amor":          "Beso de Amor",
    "Parchita":              "Parchita",
    "Dulcemaria":            "Dulcemaría",
    "Marquesa de chocolate": "M. Chocolate",
    "Chocolate brownie":     "Choc. Brownie",
    "Piña":                  "Volt. Piña",
    "Marmoleada":            "Marmoleada",
    "Vainilla":              "Vainilla",
    "Ovomaltina":            "Ovomaltina",
    "Zanahoria":             "Zanahoria",
  };
  return mapping[name] || name;
};

const CustomPieTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  return (
    <div
      className="rounded-xl px-3 py-2 text-xs"
      style={{
        background: "var(--bg-elevated)",
        border:     "1px solid var(--bg-border)",
        boxShadow:  "var(--shadow-md)",
        fontFamily: "var(--font-mono)",
      }}
    >
      <p style={{ color: item.payload.color || "var(--accent-gold)", fontWeight: 700 }}>
        {item.name}
      </p>
      <p style={{ color: "var(--text-secondary)" }}>{item.value?.toFixed(0)} uds vendidos</p>
      <p className="text-[9px] mt-1 opacity-70">Participación: {item.payload.share_pct?.toFixed(1)}%</p>
    </div>
  );
};

export default function ProductRanking({ products }: ProductRankingProps) {
  const [isMounted, setIsMounted] = useState(false);
  
  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!products || products.length === 0) {
    return (
      <div className="card flex flex-col justify-between">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3
              className="text-sm font-semibold tracking-wide"
              style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
            >
              Top Sabores
            </h3>
            <p className="text-[10px] mt-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
              Últimos 30 días
            </p>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center py-8">
          <p className="text-xs" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            Sin datos suficientes
          </p>
        </div>
      </div>
    );
  }

  let coldIndex = 0;
  let warmIndex = 0;

  // We assign a specific sub-color from a palette to each flavor based on category
  const pieData = products.map((p) => {
    const isCold = p.category === "Tortas frías";
    const color = isCold 
      ? ["#4DD9D0", "#4ECDC4", "#2BB1B1", "#06D6A0", "#C7F464", "#0E9594"][coldIndex++ % 6]
      : ["#D4A853", "#FF9F1C", "#FF6B6B", "#F78C6B", "#EF476F", "#E07A5F"][warmIndex++ % 6];
      
    return {
      name: formatName(p.name),
      value: p.total_units,
      category: p.category,
      share_pct: p.share_pct,
      color: color
    };
  });

  const totalUnits = pieData.reduce((s, d) => s + d.value, 0);
  const top5 = products.slice(0, 5);
  const maxUnits = top5[0]?.total_units || 1;

  // Re-calculate category stats just for the summary
  const byCategory: Record<string, number> = {};
  products.forEach((p) => {
    byCategory[p.category] = (byCategory[p.category] || 0) + p.total_units;
  });
  const categoryStats = Object.entries(byCategory).map(([name, value]) => {
    const pct = totalUnits > 0 ? (value / totalUnits) * 100 : 0;
    return { name, value, pct };
  });

  return (
    <div className="card flex flex-col justify-between">
      {/* Cabecera */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3
            className="text-sm font-semibold tracking-wide"
            style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}
          >
            Top Sabores
          </h3>
          <p className="text-[10px] mt-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            Últimos 30 días
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {/* Sección superior: Gráfico circular y leyenda en bloque */}
        <div
          className="flex items-center gap-4 p-3 rounded-xl"
          style={{ background: "color-mix(in srgb, var(--bg-elevated) 50%, transparent)", border: "1px solid var(--bg-border)" }}
        >
          {/* Gráfico circular */}
          <div className="w-[110px] h-[110px] flex-shrink-0 flex items-center justify-center relative">
            {isMounted && (
              <PieChart width={110} height={110}>
                <defs>
                  {pieData.map((entry) => {
                    const cleanName = entry.name.replace(/[^a-zA-Z0-9]/g, "");
                    const color = entry.color;
                    return (
                      <radialGradient
                        key={`grad-${entry.name}`}
                        id={`grad-${cleanName}`}
                        cx="50%" cy="50%" r="50%"
                      >
                        <stop offset="0%" stopColor={color} stopOpacity={1} />
                        <stop offset="100%" stopColor={color} stopOpacity={0.65} />
                      </radialGradient>
                    );
                  })}
                </defs>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={28}
                  outerRadius={45}
                  paddingAngle={3}
                  dataKey="value"
                  strokeWidth={0}
                  isAnimationActive
                  animationBegin={50}
                  animationDuration={800}
                >
                  {pieData.map((entry) => {
                    const cleanName = entry.name.replace(/[^a-zA-Z0-9]/g, "");
                    return (
                      <Cell
                        key={entry.name}
                        fill={`url(#grad-${cleanName})`}
                        stroke={entry.color}
                        strokeWidth={0.5}
                        strokeOpacity={0.4}
                      />
                    );
                  })}
                  <Label
                    content={({ viewBox }: any) => {
                      const { cx, cy } = viewBox;
                      return (
                        <g>
                          <text
                            x={cx}
                            y={cy - 2}
                            textAnchor="middle"
                            fill="var(--text-primary)"
                            fontSize={13}
                            fontWeight={700}
                            fontFamily="var(--font-mono)"
                          >
                            {totalUnits.toFixed(0)}
                          </text>
                          <text
                            x={cx}
                            y={cy + 10}
                            textAnchor="middle"
                            fill="var(--text-muted)"
                            fontSize={8}
                            fontFamily="var(--font-mono)"
                          >
                            uds
                          </text>
                        </g>
                      );
                    }}
                  />
                </Pie>
                <Tooltip content={<CustomPieTooltip />} />
              </PieChart>
            )}
          </div>

          {/* Resumen de categorías al lado */}
          <div className="flex-1 flex flex-col gap-2 min-w-0">
            {categoryStats.map(({ name, value, pct }) => {
              const color = CATEGORY_COLORS[name] || "var(--accent-gold)";
              const icon = CATEGORY_ICONS[name] || "🍩";
              return (
                <div key={name} className="flex items-center justify-between text-[11px] min-w-0">
                  <div className="flex items-center gap-1.5 min-w-0">
                    <span className="text-xs flex-shrink-0">{icon}</span>
                    <span className="font-medium truncate text-secondary" style={{ color: "var(--text-secondary)" }}>
                      {name.replace("Tortas ", "")}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-[9px] text-right flex-shrink-0">
                    <span className="text-muted">{value.toFixed(0)}</span>
                    <span className="font-semibold" style={{ color }}>{pct.toFixed(1)}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Sección inferior: Lista de Top 5 Productos */}
        <div className="flex flex-col gap-2">
          {top5.map((p, i) => {
            const relWidth = (p.total_units / maxUnits) * 100;
            const icon     = CATEGORY_ICONS[p.category] || "🍩";
            const formattedName = formatName(p.name);
            // Get the color assigned to this product in the pie chart
            const pieMatch = pieData.find(pd => pd.name === formattedName);
            const color = pieMatch?.color || CATEGORY_COLORS[p.category] || "var(--accent-gold)";

            return (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05, ease: "easeOut" }}
                className="flex items-center justify-between gap-3 p-2 rounded-xl transition-all hover:bg-elevated/40"
                style={{
                  background: "var(--bg-elevated)",
                  border: "1px solid var(--bg-border)",
                }}
              >
                {/* Ranking, Icono, Nombre y Barra */}
                <div className="flex-1 min-w-0 flex items-center gap-2.5">
                  {/* Badge de Ranking */}
                  <div
                    className="w-5 h-5 rounded-lg flex items-center justify-center text-xs font-bold font-mono flex-shrink-0"
                    style={{
                      background: i === 0 ? `color-mix(in srgb, ${color} 15%, transparent)` : "var(--bg-base)",
                      color: i === 0 ? color : "var(--text-secondary)",
                      border: i === 0 ? `1px solid ${color}` : "1px solid var(--bg-border)",
                    }}
                  >
                    {i + 1}
                  </div>

                  {/* Nombre y Barra */}
                  <div className="flex-1 min-w-0 flex flex-col gap-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[11px] flex-shrink-0">{icon}</span>
                      <p
                         className="text-[11px] font-semibold truncate"
                         style={{ color: "var(--text-primary)" }}
                         title={formattedName}
                      >
                         {formattedName}
                      </p>
                    </div>
                    {/* Barra de progreso */}
                    <div
                      className="h-1 rounded-full overflow-hidden w-full"
                      style={{ background: "var(--bg-base)" }}
                    >
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${relWidth}%` }}
                        transition={{ duration: 0.8, delay: i * 0.06, ease: "easeOut" }}
                        className="h-full rounded-full"
                        style={{
                          background: `linear-gradient(90deg, ${color} 30%, color-mix(in srgb, ${color} 75%, white) 100%)`,
                          boxShadow: `0 0 6px ${color}33`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Unidades vendidas y porcentaje de participación */}
                <div className="flex items-center gap-3 flex-shrink-0 text-right font-mono">
                  <div className="w-10">
                    <span className="text-[11px] font-semibold text-primary" style={{ color: "var(--text-primary)" }}>
                      {p.total_units.toFixed(0)}
                    </span>
                    <span className="text-[8px] text-muted ml-0.5">ud</span>
                  </div>
                  <div className="w-8 text-right">
                    <span className="text-[11px] font-semibold" style={{ color }}>
                      {p.share_pct.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
