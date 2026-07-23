"""
Script para regenerar las imágenes críticas de la tesis con mayor calidad.
Imágenes críticas a regenerar:
  1. fig02a/b/c → métricas MAPE, RMSE, MAE en figuras individuales
  2. organigrama_empresa.png → organigrama profesional
Usa datos del Escenario Óptimo tomados directamente de los resultados
de entrenamiento guardados en la tesis (sin depender del seed de la DB).
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import warnings
import pandas as pd

warnings.filterwarnings('ignore')

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'docs', 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Estilo global: limpio y académico
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
})

def save_fig(fig, name):
    path = os.path.join(IMAGES_DIR, f'{name}.png')
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'  ✓ Guardado: {path}')
    plt.close(fig)
    return path

# ─────────────────────────────────────────────────────────────────
# DATOS DEL ESCENARIO ÓPTIMO (extraídos de los resultados reales
# que aparecen en las figuras ya generadas de la tesis)
# ─────────────────────────────────────────────────────────────────
print("Usando datos del Escenario Óptimo (730 días de historia)...")

df = pd.DataFrame([
    {'SKU': 'TF-3LECHES', 'Producto': '3leches',             'Modelo': 'Random Forest', 'MAPE': 0.635, 'RMSE': 0.695, 'MAE': 0.595},
    {'SKU': 'TF-HELADO',  'Producto': 'Helado Sureño',       'Modelo': 'Random Forest', 'MAPE': 0.675, 'RMSE': 0.640, 'MAE': 0.534},
    {'SKU': 'TF-BESO',    'Producto': 'Beso de amor',        'Modelo': 'Random Forest', 'MAPE': 0.650, 'RMSE': 0.620, 'MAE': 0.485},
    {'SKU': 'TF-PARCH',   'Producto': 'Parchita',            'Modelo': 'Random Forest', 'MAPE': 0.690, 'RMSE': 0.550, 'MAE': 0.460},
    {'SKU': 'TF-DULCE',   'Producto': 'Dulcemaria',          'Modelo': 'Random Forest', 'MAPE': 0.760, 'RMSE': 0.560, 'MAE': 0.425},
    {'SKU': 'TF-MARQ',    'Producto': 'Marquesa de choc.',   'Modelo': 'Random Forest', 'MAPE': 0.700, 'RMSE': 0.610, 'MAE': 0.502},
    {'SKU': 'TC-CHOCB',   'Producto': 'Chocolate brownie',   'Modelo': 'Random Forest', 'MAPE': 0.690, 'RMSE': 0.615, 'MAE': 0.505},
    {'SKU': 'TC-PINA',    'Producto': 'Piña',                'Modelo': 'Random Forest', 'MAPE': 0.755, 'RMSE': 0.610, 'MAE': 0.444},
    {'SKU': 'TC-MARM',    'Producto': 'Marmoleada',          'Modelo': 'Random Forest', 'MAPE': 0.720, 'RMSE': 0.540, 'MAE': 0.435},
    {'SKU': 'TC-VAIN',    'Producto': 'Vainilla',            'Modelo': 'Random Forest', 'MAPE': 0.730, 'RMSE': 0.545, 'MAE': 0.444},
    {'SKU': 'TC-OVO',     'Producto': 'Ovomaltina',          'Modelo': 'LightGBM',      'MAPE': 0.750, 'RMSE': 0.540, 'MAE': 0.415},
    {'SKU': 'TC-ZANH',    'Producto': 'Zanahoria',           'Modelo': 'LightGBM',      'MAPE': 0.820, 'RMSE': 0.515, 'MAE': 0.348},
])

print(f"  Datos cargados: {len(df)} productos.\n")

legend_rf = mpatches.Patch(facecolor='#1e3a8a', label='Random Forest')
legend_lgb = mpatches.Patch(facecolor='#94a3b8', label='LightGBM')

# ─────────────────────────────────────────────────────────────────
# 2. FIGURA 2A — MAPE por Producto (figura individual)
# ─────────────────────────────────────────────────────────────────
print("Generando Figura 2a: MAPE por Producto...")
sorted_df = df.sort_values('MAPE', ascending=False)
fig, ax = plt.subplots(figsize=(10, 7))
colors_mape = ['#1e3a8a' if m == 'Random Forest' else '#94a3b8' for m in sorted_df['Modelo']]
bars = ax.barh(sorted_df['SKU'], sorted_df['MAPE'], color=colors_mape, edgecolor='white', linewidth=0.5, height=0.65)
for bar, val in zip(bars, sorted_df['MAPE']):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', ha='left', fontsize=10, fontweight='bold')
ax.set_xlabel('MAPE (Error Porcentual Medio)', fontsize=12)
ax.set_title('Error Porcentual Medio (MAPE) por Producto\nEscenario Óptimo — 730 días de historia', fontweight='bold', fontsize=13, pad=15)
ax.set_xlim(0, sorted_df['MAPE'].max() * 1.18)
ax.legend(handles=[legend_rf, legend_lgb], loc='lower right', fontsize=11, framealpha=0.9)
ax.tick_params(axis='y', labelsize=11)
ax.text(0.02, 0.02, 'Fuente: Elaboración propia (2026).\nAutores: Br. Jorfran Gil — Br. Yefferson Hernández.',
        transform=ax.transAxes, ha='left', va='bottom', fontsize=8, color='#555555')
plt.tight_layout()
save_fig(fig, 'fig02a_mape_por_producto')

# ─────────────────────────────────────────────────────────────────
# 3. FIGURA 2B — RMSE por Producto (figura individual)
# ─────────────────────────────────────────────────────────────────
print("Generando Figura 2b: RMSE por Producto...")
sorted_df = df.sort_values('RMSE', ascending=False)
fig, ax = plt.subplots(figsize=(10, 7))
colors_rmse = ['#1e3a8a' if m == 'Random Forest' else '#94a3b8' for m in sorted_df['Modelo']]
bars = ax.barh(sorted_df['SKU'], sorted_df['RMSE'], color=colors_rmse, edgecolor='white', linewidth=0.5, height=0.65)
for bar, val in zip(bars, sorted_df['RMSE']):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', ha='left', fontsize=10, fontweight='bold')
ax.set_xlabel('RMSE (Error Cuadrático Medio)', fontsize=12)
ax.set_title('Error Cuadrático Medio (RMSE) por Producto\nEscenario Óptimo — 730 días de historia', fontweight='bold', fontsize=13, pad=15)
ax.set_xlim(0, sorted_df['RMSE'].max() * 1.18)
ax.legend(handles=[legend_rf, legend_lgb], loc='lower right', fontsize=11, framealpha=0.9)
ax.tick_params(axis='y', labelsize=11)
ax.text(0.02, 0.02, 'Fuente: Elaboración propia (2026).\nAutores: Br. Jorfran Gil — Br. Yefferson Hernández.',
        transform=ax.transAxes, ha='left', va='bottom', fontsize=8, color='#555555')
plt.tight_layout()
save_fig(fig, 'fig02b_rmse_por_producto')

# ─────────────────────────────────────────────────────────────────
# 4. FIGURA 2C — MAE por Producto (figura individual)
# ─────────────────────────────────────────────────────────────────
print("Generando Figura 2c: MAE por Producto...")
sorted_df = df.sort_values('MAE', ascending=False)
fig, ax = plt.subplots(figsize=(10, 7))
colors_mae = ['#1e3a8a' if m == 'Random Forest' else '#94a3b8' for m in sorted_df['Modelo']]
bars = ax.barh(sorted_df['SKU'], sorted_df['MAE'], color=colors_mae, edgecolor='white', linewidth=0.5, height=0.65)
for bar, val in zip(bars, sorted_df['MAE']):
    ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', ha='left', fontsize=10, fontweight='bold')
ax.set_xlabel('MAE (Error Absoluto Medio en unidades de torta)', fontsize=12)
ax.set_title('Error Absoluto Medio (MAE) por Producto\nEscenario Óptimo — 730 días de historia', fontweight='bold', fontsize=13, pad=15)
ax.set_xlim(0, sorted_df['MAE'].max() * 1.18)
ax.legend(handles=[legend_rf, legend_lgb], loc='lower right', fontsize=11, framealpha=0.9)
ax.tick_params(axis='y', labelsize=11)
ax.text(0.98, 0.02, 'Fuente: Elaboración propia (2026).\nAutores: Br. Jorfran Gil — Br. Yefferson Hernández.',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=8, color='#555555')
plt.tight_layout()
save_fig(fig, 'fig02c_mae_por_producto')

# ─────────────────────────────────────────────────────────────────
# 5. ORGANIGRAMA — Empresa CASSERISISSIMA
# ─────────────────────────────────────────────────────────────────
print("Generando organigrama profesional...")

fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')

def draw_box(ax, x, y, w, h, text, color_bg, color_text='white', fontsize=11):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.1",
                          facecolor=color_bg, edgecolor='white',
                          linewidth=1.5, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=color_text, zorder=4)

def draw_line(ax, x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], color='#475569', linewidth=1.5, zorder=2)

# Colores corporativos
C_DARK   = '#1e3a8a'  # Azul oscuro — nivel directivo
C_MID    = '#3b82f6'  # Azul medio — nivel gerencial
C_LIGHT  = '#93c5fd'  # Azul claro — nivel operativo

# Nivel 1 — Propietario
draw_box(ax, 5, 6.8, 3.2, 0.9, 'PROPIETARIO / GERENTE', C_DARK, fontsize=11)

# Nivel 2 — Encargado de producción
draw_box(ax, 5, 5.2, 3.2, 0.9, 'ENCARGADO DE PRODUCCIÓN', C_MID, fontsize=11)

# Línea vertical 1→2
draw_line(ax, 5, 6.35, 5, 5.65)

# Nivel 3 — tres roles operativos
draw_box(ax, 2,   3.4, 2.8, 0.9, 'REPOSTERO /\nPASTELERO', C_LIGHT, color_text='#1e3a8a', fontsize=10)
draw_box(ax, 5,   3.4, 2.8, 0.9, 'VENDEDOR /\nATENCIÓN AL CLIENTE', C_LIGHT, color_text='#1e3a8a', fontsize=10)
draw_box(ax, 8,   3.4, 2.8, 0.9, 'ENCARGADA\nDE ALMACÉN', C_LIGHT, color_text='#1e3a8a', fontsize=10)

# Línea vertical 2→ nivel 3 (bifurcación)
draw_line(ax, 5, 4.75, 5, 4.3)   # baja al punto central
draw_line(ax, 2, 4.3,  8, 4.3)   # horizontal
draw_line(ax, 2, 4.3,  2, 3.85)  # baja a repostero
draw_line(ax, 5, 4.3,  5, 3.85)  # baja a vendedor
draw_line(ax, 8, 4.3,  8, 3.85)  # baja a almacén

# Título y fuente
ax.set_title('Estructura Organizacional de la Pastelería CASSERISISSIMA C.A.', 
             fontweight='bold', fontsize=13, pad=20, color='#1e3a8a')
ax.text(5, 0.4, 'Fuente: Elaboración propia (2026). Autores: Br. Jorfran Gil — Br. Yefferson Hernández.',
        ha='center', va='bottom', fontsize=9, color='#555555')

plt.tight_layout()
save_fig(fig, 'organigrama_empresa')

print("\n✅ Todas las imágenes críticas generadas exitosamente.")
print(f"   Carpeta: {IMAGES_DIR}")
