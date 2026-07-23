// CASSERIISSIMA 2.0 — API Client
// Wrapper fetch hacia el backend FastAPI (vía proxy Next.js)

import type { BacktestSummary } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

// ─── Escenarios ──────────────────────────────────────────────────────────────
export const scenariosApi = {
  list:      ()  => apiFetch<any>('/scenarios'),
  getActive: ()  => apiFetch<any>('/scenarios/active'),
  switch:    (id: number) => apiFetch<any>(`/scenarios/${id}`, { method: 'PUT' }),
};

// ─── Dashboard ───────────────────────────────────────────────────────────────
export const dashboardApi = {
  kpis:        ()             => apiFetch<any>('/dashboard/kpis'),
  salesTrend:  (weeks = 8)    => apiFetch<any>(`/dashboard/sales-trend?weeks=${weeks}`),
  topProducts: (days = 30)    => apiFetch<any>(`/dashboard/top-products?days=${days}`),
  inventory:   ()             => apiFetch<any>('/dashboard/inventory'),
};

// ─── Ventas ──────────────────────────────────────────────────────────────────
export const salesApi = {
  register: (payload: any) => apiFetch<any>('/sales', { method: 'POST', body: JSON.stringify(payload) }),
  recent:   (days = 7)     => apiFetch<any>(`/sales/recent?days=${days}`),
  getClosures:       () => apiFetch<any>('/sales/closures'),
  getClosureDetails: (date: string) => apiFetch<any>(`/sales/closures/${date}`),
  updateClosure:     (date: string, items: any[]) => apiFetch<any>(`/sales/closures/${date}`, {
    method: 'PUT',
    body: JSON.stringify({ items }),
  }),
  getExportUrl:      () => `${API_BASE}/sales/export`,
};

// ─── Inventario ──────────────────────────────────────────────────────────────
export const inventoryApi = {
  list:   ()                            => apiFetch<any>('/inventory'),
  update: (id: number, stock: number)   => apiFetch<any>(`/inventory/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ current_stock: stock }),
  }),
};

// ─── Predicciones ────────────────────────────────────────────────────────────
export const predictionsApi = {
  products: ()              => apiFetch<any>('/products'),
  predict:  (productId: string, horizon = 14) =>
    apiFetch<any>(`/predict/${productId}`, {
      method: 'POST',
      body: JSON.stringify({ horizon_days: horizon, service_level: 0.97, force_retrain: false }),
    }),
  updatePrice: (productId: string, price: number, cost?: number) =>
    apiFetch<any>(`/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify({ selling_price: price, unit_cost: cost }),
    }),
};

// ─── Insights ────────────────────────────────────────────────────────────────
export const insightsApi = {
  get: () => apiFetch<any>('/insights'),
};

// ─── Backtesting / Validación OE4 ────────────────────────────────────────────
// Reads the precomputed results/backtest_resumen.json via the backend.
export async function getBacktestSummary(): Promise<BacktestSummary> {
  return apiFetch<BacktestSummary>('/backtest/summary');
}

export const backtestApi = {
  getSummary: () => getBacktestSummary(),
};
