// CASSERIISSIMA 2.0 — TypeScript types compartidos

// ─── Escenarios ──────────────────────────────────────────────────────────────
export interface ScenarioMeta {
  id: 1 | 2 | 3;
  name: string;
  label: string;
  description: string;
  color: string;
  days: number;
  is_active: boolean;
}

export interface ScenariosResponse {
  scenarios: ScenarioMeta[];
  active_scenario_id: number;
}

// ─── Dashboard ───────────────────────────────────────────────────────────────
export interface DashboardKPIs {
  scenario: {
    id: number;
    name: string;
    label: string;
    color: string;
    description: string;
  };
  current_month: {
    revenue: number;
    units: number;
    days_with_data: number;
  };
  changes: {
    revenue_pct: number | null;
    units_pct: number | null;
  };
  top_product: string;
  history_days: number;
  critical_ingredients: number;
}

export interface SalesTrendItem {
  week: string;
  units: number;
  revenue: number;
  days: number;
}

export interface TopProductItem {
  id: string;
  name: string;
  category: string;
  price: number;
  total_units: number;
  total_revenue: number;
  share_pct: number;
}

export interface IngredientStatus {
  id: number;
  name: string;
  unit: string;
  current_stock: number;
  alert_threshold: number;
  ratio: number;
  status: 'ok' | 'warning' | 'critical';
}

// ─── Ventas ──────────────────────────────────────────────────────────────────
export interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  price: number;
  cost?: number;
}

export interface SaleEntryItem {
  product_id: string;
  quantity_sold: number;
  price_override?: number;
}

// ─── Predicciones ────────────────────────────────────────────────────────────
export interface ForecastPoint {
  forecast_date: string;
  predicted: number;
  lower: number;
  upper: number;
}

export interface PredictionResult {
  product: { id: string; sku: string; name: string };
  scenario: { id: number; name: string };
  model: {
    version_tag: string;
    mape_val: number;
    rmse_val: number;
    training_rows: number;
  };
  forecasts: ForecastPoint[];
  reorder: {
    rop: {
      rop: number;
      safety_stock: number;
      service_level: number;
    };
    newsvendor: {
      q_star: number;
      q_star_rounded: number;
      service_level_at_q: number;
    };
    critical_ratio: number;
    avg_daily_demand: number;
  };
}

// ─── Insights ────────────────────────────────────────────────────────────────
export interface Insight {
  type: string;
  priority: 'critical' | 'high' | 'medium' | 'info';
  icon: string;
  title: string;
  message: string;
  action: string;
}

export interface InsightsResponse {
  scenario_id: number;
  scenario_name: string;
  generated_at: string;
  context: {
    today: string;
    tomorrow_name: string;
    days_to_next_holiday: number;
    days_to_payday: number;
    top_product_week: string | null;
    critical_ingredients_count: number;
  };
  insights: Insight[];
}

// ─── Backtesting / Validación OE4 ────────────────────────────────────────────
// Mirrors results/backtest_resumen.json verbatim. Note: waste_pct_* and
// fill_rate_* are fractions (0..1); waste_reduction_pct and mean_waste_reduction_pct
// are already percentages (e.g. 12.65); mape is a fraction.
export interface BacktestConfig {
  scenario_id: number;
  scenario_name: string;
  train_window_days: number;
  horizon: number;
  retrain_every: number;
  baseline_k: number;
  baseline_buffer: number;
  max_products: number;
}

export interface BacktestAggregatedMetrics {
  mape: number;
  rmse: number;
  mae: number;
  n_windows: number;
  n_predictions: number;
}

export interface BacktestComparison {
  waste_pct_system: number;
  waste_pct_baseline: number;
  waste_reduction_pct: number;
  fill_rate_system: number;
  fill_rate_baseline: number;
  fill_rate_delta: number;
}

export interface BacktestProductMetrics {
  sku: string;
  name: string;
  category: string;
  shelf_life_days: number;
  aggregated_metrics: BacktestAggregatedMetrics;
  comparison: BacktestComparison;
  baseline_params: { k: number; buffer: number };
  n_days_compared: number;
  n_windows: number;
  n_predictions: number;
}

export interface BacktestAggregated {
  n_products: number;
  mean_mae: number;
  mean_mape: number;
  mean_rmse: number;
  mean_waste_pct_system: number;
  mean_waste_pct_baseline: number;
  mean_waste_reduction_pct: number;
  mean_fill_rate_system: number;
  mean_fill_rate_baseline: number;
  mean_fill_rate_delta: number;
}

export interface BacktestProductRow {
  product_id: string;
  sku: string;
  name: string;
  category: string;
  shelf_life_days: number;
  mae: number;
  mape: number;
  rmse: number;
  waste_pct_system: number;
  waste_pct_baseline: number;
  waste_reduction_pct: number;
  fill_rate_system: number;
  fill_rate_baseline: number;
  fill_rate_delta: number;
  n_windows: number;
  n_predictions: number;
}

export interface BacktestSummary {
  config: BacktestConfig;
  per_product: Record<string, BacktestProductMetrics>;
  aggregated: BacktestAggregated;
  aggregated_table: BacktestProductRow[];
  summary: string;
}
