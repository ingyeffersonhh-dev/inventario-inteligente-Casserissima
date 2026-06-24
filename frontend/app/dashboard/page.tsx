"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import KPICard from "@/components/dashboard/KPICard";
import SalesChart from "@/components/dashboard/SalesChart";
import ProductRanking from "@/components/dashboard/ProductRanking";
import StockAlerts from "@/components/dashboard/StockAlerts";
import InsightsPanel from "@/components/predictions/InsightsPanel";
import { dashboardApi, insightsApi } from "@/lib/api";
import { useScenario } from "@/lib/scenarioContext";
import type { DashboardKPIs, SalesTrendItem, TopProductItem, IngredientStatus, Insight } from "@/lib/types";
import { motion } from "framer-motion";
import { RefreshCw } from "lucide-react";

export default function DashboardPage() {
  const [kpis, setKpis]       = useState<DashboardKPIs | null>(null);
  const [trend, setTrend]     = useState<SalesTrendItem[]>([]);
  const [products, setProds]  = useState<TopProductItem[]>([]);
  const [inventory, setInv]   = useState<{ ingredients: IngredientStatus[]; critical_count: number; warning_count: number } | null>(null);
  const [insights, setIns]    = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);
  const [key, setKey]         = useState(0);
  const { refreshKey }        = useScenario();

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      dashboardApi.kpis(),
      dashboardApi.salesTrend(8),
      dashboardApi.topProducts(30),
      dashboardApi.inventory(),
      insightsApi.get(),
    ])
      .then(([k, t, p, inv, ins]) => {
        setKpis(k);
        setTrend(t.trend);
        setProds(p.products);
        setInv(inv);
        setIns(ins.insights || []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [key, refreshKey]);

  const scenarioColor = kpis?.scenario?.color || "var(--accent-gold)";

  return (
    <AppShell
      title="Dashboard"
      subtitle={kpis ? `Escenario ${kpis.scenario.name} · ${kpis.history_days} días de historia` : "Cargando..."}
    >
      {/* Scenario banner */}
      {kpis && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-5 rounded-xl px-4 py-3 flex items-center gap-3"
          style={{
            background: `color-mix(in srgb, ${scenarioColor} 7%, transparent)`,
            border: `1px solid color-mix(in srgb, ${scenarioColor} 22%, transparent)`,
          }}
        >
          <div className="w-2 h-2 rounded-full flex-shrink-0 pulse-glow" style={{ background: scenarioColor }} />
          <p className="text-xs flex-1" style={{ color: "var(--text-secondary)" }}>
            <strong style={{ color: scenarioColor, fontFamily: "var(--font-mono)" }}>{kpis.scenario.label}</strong>
            {" — "}{kpis.scenario.description}
          </p>
          <button
            onClick={() => setKey((k) => k + 1)}
            className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-xl transition-all hover:opacity-80"
            style={{
              background: `color-mix(in srgb, ${scenarioColor} 15%, transparent)`,
              color: scenarioColor,
              border: `1px solid color-mix(in srgb, ${scenarioColor} 30%, transparent)`,
              fontFamily: "var(--font-mono)",
            }}
          >
            <RefreshCw size={11} />
            Actualizar
          </button>
        </motion.div>
      )}

      {error && (
        <div
          className="mb-4 p-4 rounded-xl text-sm"
          style={{
            background: "color-mix(in srgb, var(--danger) 10%, transparent)",
            border:     "1px solid color-mix(in srgb, var(--danger) 30%, transparent)",
            color:      "var(--danger)",
          }}
        >
          ⚠️ Error al cargar datos: {error}. ¿Está el backend corriendo en localhost:8000?
        </div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        <KPICard
          label="Ingresos del Mes"
          value={kpis?.current_month.revenue ?? 0}
          prefix="$"
          change={kpis?.changes.revenue_pct ?? null}
          icon="💰"
          color={scenarioColor}
          index={0}
          animate={!loading}
        />
        <KPICard
          label="Tortas Vendidas"
          value={kpis?.current_month.units ?? 0}
          suffix=" uds"
          change={kpis?.changes.units_pct ?? null}
          icon="🎂"
          color="#4DD9D0"
          index={1}
          animate={!loading}
        />
        <KPICard
          label="Días de Historia"
          value={kpis?.history_days ?? 0}
          suffix=" días"
          icon="📅"
          color="#A8E6CF"
          index={2}
          animate={!loading}
        />
        <KPICard
          label="Insumos Críticos"
          value={kpis?.critical_ingredients ?? 0}
          icon="⚠️"
          color={kpis?.critical_ingredients ? "var(--danger)" : "var(--success)"}
          index={3}
          animate={!loading}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
        <div className="lg:col-span-2">
          <SalesChart data={trend} scenarioColor={scenarioColor} />
        </div>
        <ProductRanking products={products} />
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {inventory && (
          <StockAlerts
            ingredients={inventory.ingredients}
            criticalCount={inventory.critical_count}
            warningCount={inventory.warning_count}
          />
        )}
        <InsightsPanel insights={insights} scenarioName={kpis?.scenario.name} />
      </div>
    </AppShell>
  );
}
