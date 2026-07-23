"""
CASSERISISSIMA 2.0 — Mockup del Tablero de Control Gerencial
Genera una imagen PNG que muestra el diseño conceptual del dashboard:
- KPI cards (ROP, Stock, Alertas)
- Gráfico de pronóstico por SKU
- Panel de alertas de reposición
- Selector de escenario

Basado en: frontend/app/dashboard/, frontend/components/dashboard/
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '..', 'docs', 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Paleta Academica
C_NAVY       = "#1e3a8a"
C_BLUE       = "#2b6cb0"
C_SLATE      = "#475569"
C_GREY_LIGHT = "#e2e8f0"
C_GREY_BG    = "#f8fafc"
C_CHARCOAL   = "#334155"
C_WHITE      = "#ffffff"
C_GREEN      = "#166534"
C_GREEN_LIGHT= "#dcfce7"
C_AMBER      = "#92400e"
C_AMBER_LIGHT= "#fef3c7"
C_RED        = "#991b1b"
C_RED_LIGHT  = "#fee2e2"
C_BORDER     = "#cbd5e1"

fig = plt.figure(figsize=(16, 10), facecolor=C_GREY_BG)
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax_main = fig.add_axes([0, 0, 1, 1])
ax_main.set_xlim(0, 16)
ax_main.set_ylim(0, 10)
ax_main.axis('off')

def rounded_box(ax, x, y, w, h, color, alpha=1.0, radius=0.15, ec=None, lw=1.5):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad={radius}",
                         facecolor=color, edgecolor=ec or C_BORDER,
                         linewidth=lw, alpha=alpha, zorder=2)
    ax.add_patch(box)
    return box

def label(ax, x, y, text, size=9, color=C_CHARCOAL, ha='center', va='center',
          bold=False, zorder=3):
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, text, fontsize=size, color=color,
            ha=ha, va=va, fontweight=weight,
            fontfamily='sans-serif', zorder=zorder)

# ─────────────────────────────────────────────────────────────────────────────
# TOPBAR
rounded_box(ax_main, 0.1, 9.3, 15.8, 0.55, C_NAVY, ec=C_NAVY)
label(ax_main, 0.5, 9.57, "CASSERIISSIMA 2.0", size=13, color=C_WHITE, ha='left', bold=True)
label(ax_main, 4.5, 9.57, "Motor Predictivo de Inventario Perecedero", size=10, color="#93c5fd", ha='left')

# Selector escenario
rounded_box(ax_main, 11.0, 9.35, 2.0, 0.4, "#1e40af", ec="#3b82f6", lw=1)
label(ax_main, 12.0, 9.55, "Escenario: Optimo (2 anos)", size=8, color=C_WHITE, bold=True)
rounded_box(ax_main, 13.2, 9.35, 1.1, 0.4, "#1d4ed8", ec="#60a5fa", lw=1)
label(ax_main, 13.75, 9.55, "Actualizar", size=8, color=C_WHITE)

# ─────────────────────────────────────────────────────────────────────────────
# KPI CARDS (fila superior)
kpis = [
    ("Productos\nActivos",       "12",   "SKUs en catalogo",   C_BLUE,  "#dbeafe"),
    ("Alertas\nCriticas",        "3",    "Requieren reorden",  C_RED,   C_RED_LIGHT),
    ("ROP Promedio",             "8.4",  "unidades / producto", C_GREEN, C_GREEN_LIGHT),
    ("Precision\nModelo",        "91.5%","MAPE promedio",       C_AMBER, C_AMBER_LIGHT),
]
kpi_w, kpi_h = 3.5, 1.5
kpi_x_start  = 0.2
kpi_y        = 7.55

for i, (title, value, subtitle, color, bg) in enumerate(kpis):
    kx = kpi_x_start + i * (kpi_w + 0.3)
    rounded_box(ax_main, kx, kpi_y, kpi_w, kpi_h, bg, ec=color, lw=2)
    label(ax_main, kx + 0.18, kpi_y + kpi_h - 0.28, title, size=8.5,
          color=color, ha='left', bold=True)
    label(ax_main, kx + kpi_w/2, kpi_y + 0.55, value, size=26,
          color=color, ha='center', bold=True)
    label(ax_main, kx + kpi_w/2, kpi_y + 0.18, subtitle, size=7.5,
          color=C_SLATE, ha='center')

# ─────────────────────────────────────────────────────────────────────────────
# PANEL IZQUIERDO — Grafico de pronostico (sparkline)
rounded_box(ax_main, 0.2, 1.5, 9.8, 5.85, C_WHITE, ec=C_BORDER, lw=1.5)
label(ax_main, 0.5, 7.15, "Pronostico de Demanda — Torta 3leches (TF-001)", size=10,
      color=C_NAVY, ha='left', bold=True)
label(ax_main, 0.5, 6.85, "Proximo ciclo: 14 dias | Modelo: Random Forest | MAPE: 8.5%",
      size=8, color=C_SLATE, ha='left')

# Inset axes para la grafica de pronostico
ax_chart = fig.add_axes([0.035, 0.17, 0.575, 0.43])
ax_chart.set_facecolor(C_WHITE)

dias = np.arange(1, 30)
hist_d = np.arange(1, 22)
hist_v = np.array([4, 3, 6, 5, 7, 4, 3, 5, 6, 8, 4, 3, 7, 6, 5, 4, 8, 7, 5, 6, 4])
pred_d = np.arange(21, 30)
pred_v = np.array([5.2, 6.1, 7.3, 6.8, 5.5, 7.1, 8.0, 6.4, 5.9])
lower  = pred_v - np.array([1.1, 1.3, 1.5, 1.4, 1.2, 1.4, 1.7, 1.3, 1.2])
upper  = pred_v + np.array([1.1, 1.3, 1.5, 1.4, 1.2, 1.4, 1.7, 1.3, 1.2])

ax_chart.plot(hist_d, hist_v, color=C_NAVY, lw=2, label='Ventas reales', marker='o', ms=4)
ax_chart.plot(pred_d, pred_v, color=C_AMBER, lw=2, ls='--', label='Pronostico RF', marker='s', ms=4)
ax_chart.fill_between(pred_d, lower, upper, alpha=0.18, color=C_AMBER, label='Intervalo 90%')
ax_chart.axvline(x=21, color=C_SLATE, ls=':', lw=1.5, alpha=0.7)
ax_chart.text(21.3, 8.3, 'Hoy', fontsize=8, color=C_SLATE)

# Linea ROP
ax_chart.axhline(y=6.2, color=C_RED, lw=1.5, ls='-.', alpha=0.8, label='ROP(t) = 6.2')
ax_chart.text(1, 6.4, 'ROP(t)', fontsize=8, color=C_RED, fontweight='bold')

ax_chart.set_xlabel('Dia del ciclo', fontsize=8, color=C_SLATE)
ax_chart.set_ylabel('Unidades', fontsize=8, color=C_SLATE)
ax_chart.tick_params(labelsize=7, colors=C_SLATE)
ax_chart.spines['top'].set_visible(False)
ax_chart.spines['right'].set_visible(False)
ax_chart.spines['left'].set_color(C_BORDER)
ax_chart.spines['bottom'].set_color(C_BORDER)
ax_chart.set_facecolor(C_GREY_BG)
ax_chart.legend(fontsize=7, loc='upper left', framealpha=0.9)
ax_chart.grid(True, alpha=0.3, color=C_BORDER)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL DERECHO — Alertas de reposicion
rounded_box(ax_main, 10.3, 1.5, 5.5, 5.85, C_WHITE, ec=C_BORDER, lw=1.5)
label(ax_main, 10.6, 7.15, "Alertas de Reposicion — Todos los SKUs",
      size=10, color=C_NAVY, ha='left', bold=True)

alertas = [
    ("TF-001  3leches",        "CRITICO",    "Stock: 2  |  ROP: 6.2",  C_RED,   C_RED_LIGHT),
    ("TF-004  Pie de Limon",   "CRITICO",    "Stock: 1  |  ROP: 5.8",  C_RED,   C_RED_LIGHT),
    ("TF-007  Marmoleada",     "CRITICO",    "Stock: 0  |  ROP: 4.1",  C_RED,   C_RED_LIGHT),
    ("TF-002  Profiteroles",   "ALTO",       "Stock: 5  |  ROP: 7.3",  C_AMBER, C_AMBER_LIGHT),
    ("TF-005  Vainilla",       "ALTO",       "Stock: 6  |  ROP: 8.0",  C_AMBER, C_AMBER_LIGHT),
    ("TF-003  Chocolate",      "NORMAL",     "Stock: 9  |  ROP: 7.1",  C_SLATE, C_GREY_LIGHT),
    ("TF-006  Parchita",       "SIN ALERTA", "Stock: 14 |  ROP: 6.5",  C_GREEN, C_GREEN_LIGHT),
]

al_y = 6.8
for prod, status, detail, color, bg in alertas:
    al_y -= 0.73
    rounded_box(ax_main, 10.45, al_y, 5.2, 0.62, bg, ec=color, lw=1.5)
    label(ax_main, 10.65, al_y + 0.41, prod, size=8, color=C_CHARCOAL, ha='left', bold=True)
    label(ax_main, 10.65, al_y + 0.19, detail, size=7, color=C_SLATE, ha='left')

    # Badge de status
    badge_w = 1.05
    rounded_box(ax_main, 14.55, al_y + 0.14, badge_w, 0.35, color, ec=color, lw=1)
    label(ax_main, 14.55 + badge_w/2, al_y + 0.315, status, size=7.5, color=C_WHITE, bold=True)

# ─────────────────────────────────────────────────────────────────────────────
# BARRA INFERIOR — Selector producto + metrica
rounded_box(ax_main, 0.2, 0.3, 9.8, 1.0, C_WHITE, ec=C_BORDER, lw=1)
label(ax_main, 0.5, 0.9, "Producto activo:", size=8, color=C_SLATE, ha='left')
rounded_box(ax_main, 1.8, 0.55, 2.5, 0.5, C_GREY_LIGHT, ec=C_BLUE, lw=1)
label(ax_main, 3.05, 0.8, "3leches (TF-001)", size=8.5, color=C_NAVY, bold=True)

for i, (met, val) in enumerate([("MAE", "1.42"), ("RMSE", "1.85"), ("MAPE", "8.5%")]):
    mx = 5.5 + i * 1.55
    rounded_box(ax_main, mx, 0.52, 1.3, 0.55, C_GREY_LIGHT, ec=C_SLATE, lw=1)
    label(ax_main, mx + 0.65, 0.86, met, size=7.5, color=C_SLATE, bold=True)
    label(ax_main, mx + 0.65, 0.63, val, size=9, color=C_NAVY, bold=True)

rounded_box(ax_main, 10.3, 0.3, 5.5, 1.0, C_WHITE, ec=C_BORDER, lw=1)
label(ax_main, 10.6, 0.9, "Historial ROP(t) — 3leches", size=8, color=C_SLATE, ha='left', bold=True)

ax_rop = fig.add_axes([0.648, 0.04, 0.325, 0.085])
ax_rop.set_facecolor(C_WHITE)
rop_t = np.array([5.1, 5.4, 5.8, 6.0, 6.2, 6.2, 6.5, 6.3, 6.2])
ax_rop.plot(rop_t, color=C_GREEN, lw=2, marker='o', ms=4)
ax_rop.fill_between(range(len(rop_t)), rop_t, alpha=0.15, color=C_GREEN)
ax_rop.tick_params(labelsize=6, colors=C_SLATE)
ax_rop.spines['top'].set_visible(False)
ax_rop.spines['right'].set_visible(False)
ax_rop.spines['left'].set_color(C_BORDER)
ax_rop.spines['bottom'].set_color(C_BORDER)
ax_rop.set_facecolor(C_GREY_BG)
ax_rop.set_ylabel('ROP', fontsize=6, color=C_SLATE)

# Titulo y fuente
label(ax_main, 8.0, 0.06,
      "Figura N. Mockup del Tablero de Control Gerencial — CASSERIISSIMA 2.0. "
      "Fuente: Elaboracion propia (2026).",
      size=7.5, color=C_SLATE)

output_path = os.path.join(IMAGES_DIR, 'mockup_dashboard.png')
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=C_GREY_BG)
plt.close()
print("Mockup guardado en:", output_path)
