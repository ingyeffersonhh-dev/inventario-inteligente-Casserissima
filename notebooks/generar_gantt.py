"""
Cronograma / Diagrama de Gantt — Tesis de Grado
Sistema Predictivo ML para Inventarios Perecederos — Pastelería Casserissima
Autores: Br. Jorfran Gil, Br. Yefferson Hernández
Universidad de Oriente, Núcleo de Monagas

Ejecutar desde la raíz del proyecto: python notebooks/generar_gantt.py
Salida: docs/images/gantt_cronograma.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os
from datetime import date, timedelta

# ── Paleta Académica (Azules y Grises Coherentes) ────────────────────────────
C_NAVY_DARK  = "#1e3a8a"  # Azul Marino Oscuro (Fase I / OE1)
C_BLUE_MED   = "#2b6cb0"  # Azul Académico Medio (Fase II / OE2)
C_SLATE_MED  = "#475569"  # Gris Pizarra Medio (Fase III / OE3)
C_GREY_COOL  = "#64748b"  # Gris Azulado Muted (Fase IV / OE4)
C_GREY_LIGHT = "#94a3b8"  # Gris Claro (Revisión Inicial Capítulos)
C_CHARCOAL   = "#1e293b"  # Gris Carbón Oscuro (Revisión Final)

# ── Datos: (Fase, Descripción, Semana inicio, Duración semanas, Color) ──────
# Alineados con el Cuadro 1 — Diseño Operativo de la Investigación
# Ajustado a 13 semanas (Abril 1 - Junio 26)
FILAS = [
    ("Revisión y ajuste de Capítulos I al III",
     1, 2, C_GREY_LIGHT),

    ("Fase I: Diagnóstico del Sistema Actual",
     3, 2, C_NAVY_DARK),

    ("Fase II: Modelado Predictivo (Machine Learning)",
     5, 3, C_BLUE_MED),

    ("Fase III: Desarrollo del Tablero Gerencial",
     8, 3, C_SLATE_MED),

    ("Fase IV: Validación y Backtesting",
     11, 2, C_GREY_COOL),

    ("Revisión final y entrega al tutor",
     13, 1, C_CHARCOAL),
]

TOTAL_SEMANAS = 13
DATE_START    = date(2026, 4, 1)

# ── Figura ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FAFAFA")

n = len(FILAS)
ax.set_xlim(0, TOTAL_SEMANAS)
ax.set_ylim(-0.5, n - 0.5)
ax.invert_yaxis()

# ── Etiquetas del eje X (meses) ───────────────────────────────────────────
meses_vistos = {}
ticks_x, labels_x = [], []
for w in range(1, TOTAL_SEMANAS + 1):
    d = DATE_START + timedelta(weeks=w - 1)
    mes_key = d.strftime("%B %Y")
    if mes_key not in meses_vistos:
        meses_vistos[mes_key] = w - 1
    ticks_x.append(w - 1)
    labels_x.append(f"S{w}")

ax.set_xticks(ticks_x)
ax.set_xticklabels(labels_x, fontsize=10, color="#444444")
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")

# Línea divisoria de meses
prev_month = None
for w in range(1, TOTAL_SEMANAS + 1):
    d = DATE_START + timedelta(weeks=w - 1)
    m = d.month
    if prev_month and m != prev_month:
        ax.axvline(w - 1, color="#CCCCCC", linewidth=1.2, linestyle="--", zorder=1)
    prev_month = m

# ── Etiqueta de meses encima ─────────────────────────────────────────────
nombres_meses = {4: "Abril", 5: "Mayo", 6: "Junio"}
mes_ranges = {}
for w in range(1, TOTAL_SEMANAS + 1):
    d   = DATE_START + timedelta(weeks=w - 1)
    mes = d.month
    if mes not in mes_ranges:
        mes_ranges[mes] = [w - 1, w - 1]
    mes_ranges[mes][1] = w - 1

ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.set_facecolor("none")
ax2.set_xticks([])
ax2.set_xticklabels([])
for mes, (ini, fin) in mes_ranges.items():
    mid = (ini + fin + 1) / 2 # Ajuste al centro de la celda
    ax2.text(mid, -0.7, nombres_meses.get(mes, ""),
             ha="center", va="bottom", fontsize=11,
             fontweight="bold", color="#333333")

# ── Grid vertical suave ─────────────────────────────────────────────────────
for x in ticks_x:
    ax.axvline(x, color="#E8E8E8", linewidth=0.5, zorder=0)

# ── Filas alternadas ────────────────────────────────────────────────────────
for i in range(n):
    bg = "#F0F4F8" if i % 2 == 0 else "#FAFAFA"
    ax.axhspan(i - 0.48, i + 0.48, color=bg, zorder=0)

# ── Etiquetas eje Y ─────────────────────────────────────────────────────────
ax.set_yticks(range(n))
ax.set_yticklabels([f[0] for f in FILAS],
                   fontsize=12, color="#222222", linespacing=1.4)
ax.tick_params(axis="y", length=0, pad=8)

# ── Barras de Gantt ─────────────────────────────────────────────────────────
for i, (_, ini, dur, color) in enumerate(FILAS):
    rect = FancyBboxPatch(
        (ini - 1, i - 0.36), dur, 0.72,
        boxstyle="round,pad=0.06",
        linewidth=0, facecolor=color, alpha=0.90, zorder=3,
    )
    ax.add_patch(rect)

    # Duración en semanas dentro de la barra
    lbl = f"S{ini}" if dur <= 1 else f"S{ini} – S{ini + dur - 1}"
    ax.text(ini - 1 + dur / 2, i, lbl,
            ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=4)

# ── Separadores horizontales entre fases ────────────────────────────────────
for i in range(1, n):
    ax.axhline(i - 0.5, color="#CCCCCC", linewidth=0.8, zorder=2)

# ── Títulos y fuente ────────────────────────────────────────────────────────
ax.set_xlabel("Semanas de ejecución (abril – junio 2026)",
              fontsize=11, labelpad=8, color="#444444")
ax.xaxis.set_label_position("bottom")

fig.suptitle(
    "Figura X. Cronograma de ejecución de la investigación",
    x=0.01, y=0.995, ha="left",
    fontsize=14, fontweight="bold", color="#111111",
)
fig.text(0.01, -0.02,
     "Fuente: Elaboración propia (2026). "
     "Autores: Br. Jorfran Gil — Br. Yefferson Hernández.",
     fontsize=9, color="#777777")

# ── Leyenda compacta ────────────────────────────────────────────────────────
leyenda = [
    mpatches.Patch(color=C_NAVY_DARK,  label="OE1 — Diagnóstico"),
    mpatches.Patch(color=C_BLUE_MED,   label="OE2 — Modelado"),
    mpatches.Patch(color=C_SLATE_MED,  label="OE3 — Desarrollo"),
    mpatches.Patch(color=C_GREY_COOL,  label="OE4 — Validación"),
]
ax.legend(handles=leyenda, loc="lower right", fontsize=10,
      framealpha=0.9, ncol=4, edgecolor="#CCCCCC",
      bbox_to_anchor=(1, -0.16))

ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
ax.tick_params(axis="x", colors="#666666", length=3)

plt.tight_layout(rect=[0, 0.06, 1, 0.97])

# ── Guardar ─────────────────────────────────────────────────────────────────
out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "images")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "gantt_cronograma.png")
plt.savefig(out_path, dpi=400, bbox_inches="tight", facecolor="white")
print(f"Gantt guardado en: {os.path.abspath(out_path)}")
plt.close()
