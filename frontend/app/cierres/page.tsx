"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import { salesApi } from "@/lib/api";
import { 
  Calendar, 
  FileSpreadsheet, 
  Edit3, 
  Save, 
  X, 
  Plus, 
  Minus, 
  Search, 
  RefreshCw,
  ShoppingBag,
  Info
} from "lucide-react";

interface ClosureMeta {
  sale_date: string;
  total_revenue: number;
  total_units: number;
  items_count: number;
}

interface ClosureDetailItem {
  product_id: string;
  product_name: string;
  category: string;
  unit_price: number;
  quantity_sold: number;
  revenue: number;
  exists_in_db: boolean;
}

export default function CierresPage() {
  const [closures, setClosures] = useState<ClosureMeta[]>([]);
  const [filteredClosures, setFilteredClosures] = useState<ClosureMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  
  // Modal State
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [detailItems, setDetailItems] = useState<ClosureDetailItem[]>([]);
  const [modalLoading, setModalLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Fetch closures
  const fetchClosures = async () => {
    setLoading(true);
    try {
      const data = await salesApi.getClosures();
      setClosures(data.closures || []);
      setFilteredClosures(data.closures || []);
    } catch (err) {
      console.error("Error al obtener cierres:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClosures();
  }, []);

  // Filter closures by search query
  useEffect(() => {
    if (!searchTerm) {
      setFilteredClosures(closures);
    } else {
      const filtered = closures.filter(c => 
        c.sale_date.includes(searchTerm)
      );
      setFilteredClosures(filtered);
    }
  }, [searchTerm, closures]);

  // Open modal and fetch closure details
  const handleOpenEdit = async (date: string) => {
    setSelectedDate(date);
    setModalLoading(true);
    try {
      const data = await salesApi.getClosureDetails(date);
      setDetailItems(data.items || []);
    } catch (err) {
      console.error("Error al obtener detalles del cierre:", err);
    } finally {
      setModalLoading(false);
    }
  };

  // Adjust quantity in modal
  const handleAdjustQty = (productId: string, amount: number) => {
    setDetailItems(prev => prev.map(item => {
      if (item.product_id === productId) {
        const newQty = Math.max(0, Math.min(10, Number((item.quantity_sold + amount).toFixed(1))));
        return {
          ...item,
          quantity_sold: newQty,
          revenue: Number((newQty * item.unit_price).toFixed(2))
        };
      }
      return item;
    }));
  };

  // Direct manual change in input
  const handleInputChange = (productId: string, val: string) => {
    const numVal = Math.max(0, Math.min(10, parseFloat(val) || 0));
    setDetailItems(prev => prev.map(item => {
      if (item.product_id === productId) {
        return {
          ...item,
          quantity_sold: numVal,
          revenue: Number((numVal * item.unit_price).toFixed(2))
        };
      }
      return item;
    }));
  };

  // Save changes
  const handleSaveChanges = async () => {
    if (!selectedDate) return;
    setSaving(true);
    try {
      const payload = detailItems.map(item => ({
        product_id: item.product_id,
        quantity_sold: item.quantity_sold
      }));
      await salesApi.updateClosure(selectedDate, payload);
      await fetchClosures(); // reload main table
      setSelectedDate(null);
    } catch (err) {
      console.error("Error al guardar cambios:", err);
      alert("Error al guardar cambios en el cierre.");
    } finally {
      setSaving(false);
    }
  };

  // Export excel trigger
  const handleExportExcel = () => {
    const url = salesApi.getExportUrl();
    window.open(url, "_blank");
  };

  // Group items by category for prettier modal layout
  const categoriesMap: { [key: string]: ClosureDetailItem[] } = {};
  detailItems.forEach(item => {
    if (!categoriesMap[item.category]) {
      categoriesMap[item.category] = [];
    }
    categoriesMap[item.category].push(item);
  });

  return (
    <AppShell title="Cierres de Caja" subtitle="Historial de ventas diarias registradas y reportes">
      
      {/* Top action section */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-stretch sm:items-center mb-6">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
          <input 
            type="text"
            placeholder="Buscar por fecha (AAAA-MM-DD)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl text-sm focus:outline-none focus:ring-1 focus:ring-[var(--accent-gold)]"
            style={{
              background: "var(--bg-surface)",
              border: "1px solid var(--bg-border)",
              color: "var(--text-primary)",
              fontFamily: "var(--font-mono)"
            }}
          />
        </div>

        {/* Buttons */}
        <div className="flex gap-2.5">
          <button 
            onClick={fetchClosures}
            className="p-2 rounded-xl flex items-center justify-center border transition-all cursor-pointer"
            style={{
              background: "var(--bg-surface)",
              borderColor: "var(--bg-border)",
              color: "var(--text-secondary)"
            }}
            title="Recargar datos"
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          </button>
          
          <button 
            onClick={handleExportExcel}
            className="px-4 py-2 rounded-xl flex items-center gap-2 text-sm font-semibold transition-all cursor-pointer shadow-sm hover:shadow-md"
            style={{
              background: "linear-gradient(135deg, var(--accent-gold), var(--accent-amber))",
              color: "var(--bg-base)"
            }}
          >
            <FileSpreadsheet size={16} />
            Exportar Excel
          </button>
        </div>
      </div>

      {/* Main closures list */}
      <div 
        className="rounded-2xl border overflow-hidden glass"
        style={{ borderColor: "var(--bg-border)" }}
      >
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center gap-3">
            <RefreshCw size={28} className="animate-spin text-[var(--accent-gold)]" />
            <p className="text-xs text-[var(--text-muted)] font-mono">Cargando histórico de cierres...</p>
          </div>
        ) : filteredClosures.length === 0 ? (
          <div className="py-20 flex flex-col items-center justify-center gap-3 text-center px-4">
            <ShoppingBag size={36} className="text-[var(--text-faint)]" />
            <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>No se encontraron cierres</p>
            <p className="text-xs text-[var(--text-muted)] max-w-sm">
              Registra las ventas del día en la pestaña de **Ingreso** para empezar a guardar históricos.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr 
                  className="text-[10px] font-bold uppercase tracking-wider font-mono border-b"
                  style={{ 
                    background: "color-mix(in srgb, var(--bg-surface) 40%, transparent)",
                    borderColor: "var(--bg-border)",
                    color: "var(--text-muted)"
                  }}
                >
                  <th className="py-3 px-5">Fecha de Venta</th>
                  <th className="py-3 px-5 text-right">Unidades Vendidas</th>
                  <th className="py-3 px-5 text-right">Ingresos Totales</th>
                  <th className="py-3 px-5 text-center">Productos Activos</th>
                  <th className="py-3 px-5 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--bg-border)]">
                {filteredClosures.map((closure) => (
                  <tr 
                    key={closure.sale_date}
                    className="hover:bg-[color-mix(in srgb,var(--bg-surface)_25%,transparent)] transition-all duration-150"
                  >
                    <td className="py-3.5 px-5 font-semibold font-mono" style={{ color: "var(--text-primary)" }}>
                      <div className="flex items-center gap-2">
                        <Calendar size={14} className="text-[var(--accent-gold)]" />
                        {closure.sale_date}
                      </div>
                    </td>
                    <td className="py-3.5 px-5 text-right font-mono" style={{ color: "var(--text-secondary)" }}>
                      {closure.total_units.toFixed(1)} uds
                    </td>
                    <td className="py-3.5 px-5 text-right font-mono font-semibold" style={{ color: "var(--accent-gold)" }}>
                      ${closure.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="py-3.5 px-5 text-center font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                      {closure.items_count} prod.
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      <button
                        onClick={() => handleOpenEdit(closure.sale_date)}
                        className="px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 mx-auto transition-all cursor-pointer"
                        style={{
                          background: "color-mix(in srgb, var(--accent-gold) 6%, transparent)",
                          borderColor: "color-mix(in srgb, var(--accent-gold) 18%, transparent)",
                          color: "var(--accent-gold)"
                        }}
                      >
                        <Edit3 size={12} />
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail / Edit Modal */}
      <AnimatePresence>
        {selectedDate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => !saving && setSelectedDate(null)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />

            {/* Modal Body */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ type: "spring", duration: 0.4 }}
              className="relative w-full max-w-2xl max-h-[85vh] flex flex-col rounded-2xl border shadow-2xl glass overflow-hidden"
              style={{ 
                background: "var(--bg-surface)", 
                borderColor: "var(--bg-border)",
                boxShadow: "0 24px 48px -12px rgba(0,0,0,0.5)"
              }}
            >
              {/* Header */}
              <div 
                className="flex items-center justify-between px-5 py-4 border-b"
                style={{ borderColor: "var(--bg-border)", background: "color-mix(in srgb, var(--bg-base) 20%, transparent)" }}
              >
                <div>
                  <h3 className="text-base font-bold flex items-center gap-2" style={{ fontFamily: "var(--font-display)", color: "var(--text-primary)" }}>
                    <Calendar size={16} className="text-[var(--accent-gold)]" />
                    Editar Cierre — {selectedDate}
                  </h3>
                  <p className="text-[10px] font-mono mt-0.5" style={{ color: "var(--text-muted)" }}>
                    Modifica las unidades vendidas por producto para esta fecha
                  </p>
                </div>
                <button
                  onClick={() => setSelectedDate(null)}
                  disabled={saving}
                  className="p-1.5 rounded-lg hover:bg-[color-mix(in srgb,var(--bg-border)_50%,transparent)] text-[var(--text-muted)] transition-colors cursor-pointer"
                >
                  <X size={16} />
                </button>
              </div>

              {/* Content area */}
              <div className="flex-1 overflow-y-auto p-5">
                {modalLoading ? (
                  <div className="py-20 flex flex-col items-center justify-center gap-3">
                    <RefreshCw size={24} className="animate-spin text-[var(--accent-gold)]" />
                    <p className="text-xs text-[var(--text-muted)] font-mono">Cargando detalles del cierre...</p>
                  </div>
                ) : (
                  <div className="flex flex-col gap-6">
                    {/* Category Sections */}
                    {Object.keys(categoriesMap).map(category => (
                      <div key={category} className="flex flex-col gap-2.5">
                        <h4 
                          className="text-[10px] font-bold uppercase tracking-wider font-mono border-b pb-1 flex items-center gap-1.5"
                          style={{ color: "var(--accent-gold)", borderColor: "color-mix(in srgb, var(--accent-gold) 15%, transparent)" }}
                        >
                          {category}
                        </h4>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {categoriesMap[category].map(item => (
                            <div 
                              key={item.product_id}
                              className="p-3 rounded-xl border flex items-center justify-between gap-3 bg-[color-mix(in srgb,var(--bg-base)_25%,transparent)]"
                              style={{ borderColor: "var(--bg-border)" }}
                            >
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                                  {item.product_name}
                                </p>
                                <div className="flex items-center gap-2 mt-0.5">
                                  <span className="text-[9px] font-mono" style={{ color: "var(--text-muted)" }}>
                                    P.U. ${item.unit_price.toFixed(2)}
                                  </span>
                                  {item.quantity_sold > 0 && (
                                    <span className="text-[9px] font-mono font-semibold" style={{ color: "var(--accent-gold)" }}>
                                      Tot: ${item.revenue.toFixed(2)}
                                    </span>
                                  )}
                                </div>
                              </div>

                              {/* Quantity controls */}
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleAdjustQty(item.product_id, -1)}
                                  className="w-7 h-7 rounded-lg border flex items-center justify-center hover:bg-[color-mix(in srgb,var(--bg-border)_40%,transparent)] active:scale-95 transition-all text-[var(--text-secondary)] cursor-pointer"
                                  style={{ borderColor: "var(--bg-border)" }}
                                >
                                  <Minus size={12} />
                                </button>
                                
                                <input
                                  type="number"
                                  min="0"
                                  max="10"
                                  step="0.1"
                                  value={item.quantity_sold === 0 ? "" : item.quantity_sold}
                                  placeholder="0"
                                  onChange={(e) => handleInputChange(item.product_id, e.target.value)}
                                  className="w-11 text-center font-mono text-xs font-bold focus:outline-none focus:ring-1 focus:ring-[var(--accent-gold)] rounded py-0.5 border"
                                  style={{
                                    background: "var(--bg-base)",
                                    borderColor: "var(--bg-border)",
                                    color: "var(--text-primary)"
                                  }}
                                />

                                <button
                                  onClick={() => handleAdjustQty(item.product_id, 1)}
                                  className="w-7 h-7 rounded-lg border flex items-center justify-center hover:bg-[color-mix(in srgb,var(--bg-border)_40%,transparent)] active:scale-95 transition-all text-[var(--text-secondary)] cursor-pointer"
                                  style={{ borderColor: "var(--bg-border)" }}
                                >
                                  <Plus size={12} />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div 
                className="px-5 py-3.5 border-t flex items-center justify-between"
                style={{ borderColor: "var(--bg-border)", background: "color-mix(in srgb, var(--bg-base) 20%, transparent)" }}
              >
                <div className="flex items-center gap-1 text-[10px] text-[var(--text-muted)] font-mono">
                  <Info size={12} />
                  Las cantidades se limitan entre 0 y 10.
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedDate(null)}
                    disabled={saving}
                    className="px-4 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer hover:bg-[color-mix(in srgb,var(--bg-border)_25%,transparent)]"
                    style={{ borderColor: "var(--bg-border)", color: "var(--text-secondary)" }}
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleSaveChanges}
                    disabled={saving || modalLoading}
                    className="px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer shadow-md shadow-[var(--accent-gold)]/10"
                    style={{
                      background: "linear-gradient(135deg, var(--accent-gold), var(--accent-amber))",
                      color: "var(--bg-base)"
                    }}
                  >
                    <Save size={13} />
                    {saving ? "Guardando..." : "Guardar Cambios"}
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </AppShell>
  );
}
