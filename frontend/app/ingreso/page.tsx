"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { salesApi, inventoryApi, predictionsApi } from "@/lib/api";
import type { Product, IngredientStatus } from "@/lib/types";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Minus, Save, CheckCircle, Package } from "lucide-react";

const CATEGORIES = ["Tortas frías", "Tortas Caseras"];
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
    "Helado Sureño":         "Torta Helada Sureño",
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

export default function IngresoPage() {
  const [products, setProducts]     = useState<Product[]>([]);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [ingredients, setIngredients] = useState<IngredientStatus[]>([]);
  const [saving, setSaving]         = useState(false);
  const [saved, setSaved]           = useState(false);
  const [updatingIng, setUpdatingIng] = useState<number | null>(null);
  const [ingValues, setIngValues]   = useState<Record<number, number>>({});
  const [activeTab, setActiveTab]   = useState<"sales" | "inventory">("sales");

  // Estados para la gestión de precios/costos
  const [editCatalogMode, setEditCatalogMode] = useState(false);
  const [customPrices, setCustomPrices]       = useState<Record<string, number>>({});
  const [catalogPrices, setCatalogPrices]     = useState<Record<string, number>>({});
  const [catalogCosts, setCatalogCosts]       = useState<Record<string, number>>({});
  const [updatingProduct, setUpdatingProduct] = useState<string | null>(null);
  const [catalogSavedStatus, setCatalogSavedStatus] = useState<Record<string, boolean>>({});

  useEffect(() => {
    predictionsApi.products().then((d) => {
      setProducts(d.products);
      const initQty: Record<string, number> = {};
      const initPrices: Record<string, number> = {};
      const initCosts: Record<string, number> = {};
      d.products.forEach((p: Product) => {
        initQty[p.id] = 0;
        initPrices[p.id] = p.price;
        initCosts[p.id] = p.cost || 0;
      });
      setQuantities(initQty);
      setCustomPrices(initPrices);
      setCatalogPrices(initPrices);
      setCatalogCosts(initCosts);
    });
    inventoryApi.list().then((d) => {
      setIngredients(d.ingredients);
      const initIng: Record<number, number> = {};
      d.ingredients.forEach((i: IngredientStatus) => { initIng[i.id] = i.current_stock; });
      setIngValues(initIng);
    });
  }, []);

  const adjust = (id: string, delta: number) => {
    setQuantities((prev) => ({ ...prev, [id]: Math.max(0, (prev[id] || 0) + delta) }));
  };

  const setQtyExact = (id: string, val: number) => {
    setQuantities((prev) => ({ ...prev, [id]: Math.max(0, val) }));
  };

  const handleSaveSales = async () => {
    const items = Object.entries(quantities)
      .filter(([, q]) => q > 0)
      .map(([product_id, quantity_sold]) => {
        const payloadItem: any = { product_id, quantity_sold };
        const catalogProd = products.find((p) => p.id === product_id);
        const currentPrice = customPrices[product_id];
        if (catalogProd && currentPrice !== catalogProd.price) {
          payloadItem.price_override = currentPrice;
        }
        return payloadItem;
      });

    if (!items.length) return;
    setSaving(true);
    try {
      await salesApi.register({ items });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
      const resetQty: Record<string, number> = {};
      const resetPrices: Record<string, number> = {};
      products.forEach((p) => {
        resetQty[p.id] = 0;
        resetPrices[p.id] = p.price;
      });
      setQuantities(resetQty);
      setCustomPrices(resetPrices);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveCatalogPrice = async (productId: string) => {
    setUpdatingProduct(productId);
    try {
      const price = catalogPrices[productId];
      const cost = catalogCosts[productId];
      await predictionsApi.updatePrice(productId, price, cost);
      setProducts((prev) =>
        prev.map((p) => p.id === productId ? { ...p, price, cost } : p)
      );
      setCustomPrices((prev) => ({ ...prev, [productId]: price }));
      setCatalogSavedStatus((prev) => ({ ...prev, [productId]: true }));
      setTimeout(() => {
        setCatalogSavedStatus((prev) => ({ ...prev, [productId]: false }));
      }, 2000);
    } catch (err: any) {
      alert("Error al actualizar catálogo: " + err.message);
    } finally {
      setUpdatingProduct(null);
    }
  };

  const handleSaveIngredient = async (id: number) => {
    setUpdatingIng(id);
    try {
      await inventoryApi.update(id, ingValues[id]);
      setIngredients((prev) => prev.map((i) => i.id === id ? { ...i, current_stock: ingValues[id] } : i));
    } finally {
      setUpdatingIng(null);
    }
  };

  const totalToday = Object.values(quantities).reduce((s, v) => s + v, 0);
  const byCategory = CATEGORIES.map((cat) => ({
    cat,
    products: products.filter((p) => p.category === cat),
  }));

  return (
    <AppShell title="Ingreso de Datos" subtitle="Registra el cierre del día en segundos">
      {/* ── Tabs ── */}
      <div className="flex gap-2 mb-5">
        {[
          { key: "sales",     label: "🎂 Ventas del Día" },
          { key: "inventory", label: "📦 Inventario" },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as any)}
            className="px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200"
            style={{
              background: activeTab === key
                ? "color-mix(in srgb, var(--accent-gold) 12%, transparent)"
                : "transparent",
              border: activeTab === key
                ? "1px solid color-mix(in srgb, var(--accent-gold) 30%, transparent)"
                : "1px solid var(--bg-border)",
              color: activeTab === key ? "var(--accent-gold)" : "var(--text-muted)",
              fontFamily: "var(--font-mono)",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === "sales" && (
          <motion.div
            key="sales"
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 12 }}
            transition={{ duration: 0.22 }}
          >
            {/* ── Summary bar ── */}
            <div
              className="mb-5 flex flex-wrap items-center justify-between gap-3 px-5 py-3 rounded-xl"
              style={{
                background: editCatalogMode
                  ? "color-mix(in srgb, #4DD9D0 5%, transparent)"
                  : totalToday > 0
                  ? "color-mix(in srgb, var(--accent-gold) 8%, transparent)"
                  : "var(--bg-surface)",
                border: `1px solid ${
                  editCatalogMode ? "color-mix(in srgb, #4DD9D0 20%, transparent)"
                  : totalToday > 0 ? "color-mix(in srgb, var(--accent-gold) 25%, transparent)"
                  : "var(--bg-border)"
                }`,
              }}
            >
              <div>
                {editCatalogMode ? (
                  <>
                    <p className="text-xs font-semibold" style={{ color: "#4DD9D0", fontFamily: "var(--font-mono)" }}>Catálogo de Productos</p>
                    <p className="text-lg font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}>Configura Precios y Costos</p>
                  </>
                ) : (
                  <>
                    <p className="text-xs" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>Total del día</p>
                    <p className="text-2xl font-bold" style={{ fontFamily: "var(--font-mono)", color: totalToday > 0 ? "var(--accent-gold)" : "var(--text-muted)" }}>
                      {totalToday} <span className="text-sm font-normal">tortas</span>
                    </p>
                  </>
                )}
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setEditCatalogMode(!editCatalogMode)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold transition-all"
                  style={{
                    background: editCatalogMode ? "color-mix(in srgb, #4DD9D0 12%, transparent)" : "transparent",
                    border:     `1px solid ${editCatalogMode ? "#4DD9D0" : "var(--bg-border)"}`,
                    color:      editCatalogMode ? "#4DD9D0" : "var(--text-secondary)",
                    fontFamily: "var(--font-mono)",
                  }}
                >
                  {editCatalogMode ? "🔒 Salir Edición Catálogo" : "✏️ Configurar Catálogo"}
                </button>

                {!editCatalogMode && (
                  <motion.button
                    onClick={handleSaveSales}
                    disabled={saving || totalToday === 0}
                    whileHover={totalToday > 0 ? { scale: 1.03 } : {}}
                    whileTap={totalToday > 0 ? { scale: 0.97 } : {}}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-200"
                    style={{
                      background: saved
                        ? "color-mix(in srgb, var(--success) 15%, transparent)"
                        : totalToday > 0
                        ? "color-mix(in srgb, var(--accent-gold) 15%, transparent)"
                        : "var(--bg-elevated)",
                      border: saved
                        ? "1px solid color-mix(in srgb, var(--success) 40%, transparent)"
                        : totalToday > 0
                        ? "1px solid color-mix(in srgb, var(--accent-gold) 40%, transparent)"
                        : "1px solid var(--bg-border)",
                      color: saved ? "var(--success)" : totalToday > 0 ? "var(--accent-gold)" : "var(--text-muted)",
                      cursor: totalToday > 0 ? "pointer" : "not-allowed",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    {saved ? <CheckCircle size={16} /> : <Save size={16} />}
                    {saved ? "¡Guardado!" : saving ? "Guardando..." : "Guardar Cierre"}
                  </motion.button>
                )}
              </div>
            </div>

            {/* ── Product grid by category ── */}
            <div className="flex flex-col gap-6">
              {byCategory.map(({ cat, products: catProds }, catIdx) => {
                const catColor = CATEGORY_COLORS[cat];
                return (
                  <motion.div
                    key={cat}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: catIdx * 0.08, ease: [0.22, 1, 0.36, 1] }}
                  >
                    {/* Category header */}
                    <div className="flex items-center gap-2 mb-3">
                      <div className="h-px flex-1" style={{ background: `color-mix(in srgb, ${catColor} 30%, transparent)` }} />
                      <span
                        className="text-[11px] font-bold px-3 py-1 rounded-full flex items-center gap-1.5"
                        style={{
                          background: `color-mix(in srgb, ${catColor} 10%, transparent)`,
                          color: catColor,
                          border: `1px solid color-mix(in srgb, ${catColor} 25%, transparent)`,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        <span>{CATEGORY_ICONS[cat] || "🍩"}</span>
                        {cat}
                      </span>
                      <div className="h-px flex-1" style={{ background: `color-mix(in srgb, ${catColor} 30%, transparent)` }} />
                    </div>

                    {/* Product cards */}
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {catProds.map((prod, prodIdx) => {
                        if (editCatalogMode) {
                          const isSaved = catalogSavedStatus[prod.id];
                          return (
                            <motion.div
                              key={prod.id}
                              initial={{ opacity: 0, scale: 0.96 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: prodIdx * 0.04 }}
                              className="p-3 rounded-xl flex flex-col justify-between min-h-[145px]"
                              style={{
                                background: "color-mix(in srgb, #4DD9D0 3%, transparent)",
                                border: `1px solid ${isSaved ? "color-mix(in srgb, var(--success) 40%, transparent)" : "var(--bg-border)"}`,
                              }}
                            >
                              <div>
                                <p className="text-xs font-semibold mb-2 leading-snug" style={{ color: "var(--text-primary)" }}>
                                  {formatName(prod.name)}
                                </p>
                                <div className="flex flex-col gap-1.5 mb-3">
                                  <div>
                                    <span className="text-[9px] block mb-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>Precio Venta ($)</span>
                                    <input
                                      type="number"
                                      step="0.5"
                                      min="0.1"
                                      value={catalogPrices[prod.id] !== undefined ? catalogPrices[prod.id] : prod.price}
                                      onChange={(e) => setCatalogPrices(prev => ({ ...prev, [prod.id]: parseFloat(e.target.value) || 0 }))}
                                      className="w-full px-2 py-0.5 rounded-lg text-xs outline-none"
                                      style={{ background: "var(--bg-base)", border: "1px solid var(--bg-border)", fontFamily: "var(--font-mono)", color: "var(--text-primary)" }}
                                    />
                                  </div>
                                  <div>
                                    <span className="text-[9px] block mb-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>Costo Unitario ($)</span>
                                    <input
                                      type="number"
                                      step="0.5"
                                      min="0.0"
                                      value={catalogCosts[prod.id] !== undefined ? catalogCosts[prod.id] : (prod.cost || 0)}
                                      onChange={(e) => setCatalogCosts(prev => ({ ...prev, [prod.id]: parseFloat(e.target.value) || 0 }))}
                                      className="w-full px-2 py-0.5 rounded-lg text-xs outline-none"
                                      style={{ background: "var(--bg-base)", border: "1px solid var(--bg-border)", fontFamily: "var(--font-mono)", color: "var(--text-primary)" }}
                                    />
                                  </div>
                                </div>
                              </div>
                              <button
                                onClick={() => handleSaveCatalogPrice(prod.id)}
                                disabled={updatingProduct === prod.id}
                                className="w-full py-1 rounded-lg text-[10px] font-bold transition-all flex items-center justify-center gap-1"
                                style={{
                                  background: isSaved ? "color-mix(in srgb, var(--success) 12%, transparent)" : "color-mix(in srgb, #4DD9D0 12%, transparent)",
                                  border:     `1px solid ${isSaved ? "color-mix(in srgb, var(--success) 30%, transparent)" : "color-mix(in srgb, #4DD9D0 30%, transparent)"}`,
                                  color:      isSaved ? "var(--success)" : "#4DD9D0",
                                  fontFamily: "var(--font-mono)",
                                }}
                              >
                                {isSaved ? (
                                  <><CheckCircle size={10} /> Guardado</>
                                ) : updatingProduct === prod.id ? (
                                  "Guardando..."
                                ) : (
                                  "Guardar Base"
                                )}
                              </button>
                            </motion.div>
                          );
                        }

                        const qty = quantities[prod.id] || 0;
                        const active = qty > 0;
                        return (
                          <motion.div
                            key={prod.id}
                            initial={{ opacity: 0, scale: 0.96 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: prodIdx * 0.04 }}
                            whileHover={{ y: -2, scale: 1.01 }}
                            className="p-3 rounded-xl transition-all duration-150 flex flex-col justify-between min-h-[145px]"
                            style={{
                              background: active
                                ? `color-mix(in srgb, ${catColor} 8%, transparent)`
                                : "var(--bg-surface)",
                              border: `1px solid ${active
                                ? `color-mix(in srgb, ${catColor} 30%, transparent)`
                                : "var(--bg-border)"
                              }`,
                              boxShadow: active ? `0 0 16px color-mix(in srgb, ${catColor} 12%, transparent)` : "none",
                            }}
                          >
                            <div>
                              <p className="text-xs font-semibold mb-1 leading-snug" style={{ color: "var(--text-primary)" }}>
                                {formatName(prod.name)}
                              </p>
                              {active ? (
                                <div className="mb-2">
                                  <span className="text-[9px] block mb-0.5" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>Precio de hoy ($):</span>
                                  <input
                                    type="number"
                                    step="0.5"
                                    value={customPrices[prod.id] !== undefined ? customPrices[prod.id] : prod.price}
                                    onChange={(e) => setCustomPrices(prev => ({ ...prev, [prod.id]: parseFloat(e.target.value) || 0 }))}
                                    className="w-full px-2 py-0.5 rounded-lg text-xs outline-none"
                                    style={{
                                      background: "var(--bg-base)",
                                      border: `1px solid color-mix(in srgb, ${catColor} 40%, transparent)`,
                                      fontFamily: "var(--font-mono)",
                                      color: "var(--text-primary)",
                                    }}
                                  />
                                </div>
                              ) : (
                                <p className="text-[10px] mb-3" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>${prod.price}</p>
                              )}
                            </div>
                            <div className="flex items-center justify-between mt-1">
                              <motion.button
                                onClick={() => adjust(prod.id, -1)}
                                disabled={qty === 0}
                                whileTap={{ scale: 0.85 }}
                                className="w-7 h-7 rounded-lg flex items-center justify-center transition-all disabled:opacity-30 flex-shrink-0"
                                style={{ background: "var(--bg-base)", border: "1px solid var(--bg-border)" }}
                              >
                                <Minus size={12} style={{ color: "var(--text-secondary)" }} />
                              </motion.button>
                              
                              <input
                                type="number"
                                min="0"
                                value={qty || ""}
                                placeholder="0"
                                onChange={(e) => setQtyExact(prod.id, parseInt(e.target.value) || 0)}
                                className="text-lg font-bold w-12 text-center bg-transparent border-none outline-none"
                                style={{
                                  fontFamily: "var(--font-mono)", 
                                  color: active ? catColor : "var(--text-muted)"
                                }}
                              />

                              <motion.button
                                onClick={() => adjust(prod.id, 1)}
                                whileTap={{ scale: 0.85 }}
                                className="w-7 h-7 rounded-lg flex items-center justify-center transition-all flex-shrink-0"
                                style={{
                                  background: active ? `color-mix(in srgb, ${catColor} 18%, transparent)` : "var(--bg-base)",
                                  border: `1px solid ${active ? `color-mix(in srgb, ${catColor} 40%, transparent)` : "var(--bg-border)"}`,
                                }}
                              >
                                <Plus size={12} style={{ color: active ? catColor : "var(--text-secondary)" }} />
                              </motion.button>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

        {activeTab === "inventory" && (
          <motion.div
            key="inventory"
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -12 }}
            transition={{ duration: 0.22 }}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {ingredients.map((ing, i) => {
                const status = ing.current_stock <= ing.alert_threshold ? "critical"
                             : ing.current_stock <= ing.alert_threshold * 1.5 ? "warning" : "ok";
                const color  = status === "critical" ? "var(--danger)" : status === "warning" ? "var(--warning)" : "var(--success)";
                return (
                  <motion.div
                    key={ing.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04, ease: [0.22, 1, 0.36, 1] }}
                    className="p-4 rounded-xl"
                    style={{
                      background: `color-mix(in srgb, ${color} 6%, transparent)`,
                      border: `1px solid color-mix(in srgb, ${color} 22%, transparent)`,
                    }}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-sm font-semibold" style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}>{ing.name}</p>
                      <span
                        className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                        style={{
                          background: `color-mix(in srgb, ${color} 15%, transparent)`,
                          color,
                          border: `1px solid color-mix(in srgb, ${color} 30%, transparent)`,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {status === "critical" ? "🔴 CRÍTICO" : status === "warning" ? "🟡 BAJO" : "✅ OK"}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1">
                        <input
                          type="number"
                          min={0}
                          step={0.1}
                          value={ingValues[ing.id] ?? ing.current_stock}
                          onChange={(e) => setIngValues((prev) => ({ ...prev, [ing.id]: parseFloat(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 rounded-xl text-sm font-semibold outline-none"
                          style={{
                            background: "var(--bg-base)",
                            border: `1px solid color-mix(in srgb, ${color} 35%, transparent)`,
                            fontFamily: "var(--font-mono)",
                            color: "var(--text-primary)",
                          }}
                        />
                        <p className="text-[10px] mt-1" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                          Umbral: {ing.alert_threshold} {ing.unit}
                        </p>
                      </div>
                      <span className="text-xs w-10 flex-shrink-0" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>{ing.unit}</span>
                      <button
                        onClick={() => handleSaveIngredient(ing.id)}
                        disabled={updatingIng === ing.id}
                        className="px-3 py-2 rounded-xl text-xs font-semibold transition-all"
                        style={{
                          background: `color-mix(in srgb, ${color} 15%, transparent)`,
                          color,
                          border: `1px solid color-mix(in srgb, ${color} 30%, transparent)`,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {updatingIng === ing.id ? "..." : "Guardar"}
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </AppShell>
  );
}
