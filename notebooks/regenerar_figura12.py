import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'docs', 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Estilo global para máxima calidad en Word
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 12,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'savefig.dpi': 400,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
})

# Datos del Escenario Óptimo (reutilizados)
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

legend_rf = mpatches.Patch(facecolor='#1e3a8a', label='Random Forest')
legend_lgb = mpatches.Patch(facecolor='#94a3b8', label='LightGBM')

# Figura 1x3
fig, axes = plt.subplots(1, 3, figsize=(20, 8))

metrics_config = [
    ('MAPE', 'MAPE (Error Porcentual Medio)', axes[0]),
    ('RMSE', 'RMSE (Error Cuadrático Medio)', axes[1]),
    ('MAE', 'MAE (Error Absoluto Medio)', axes[2])
]

for metric, title, ax in metrics_config:
    sorted_df = df.sort_values(metric, ascending=False)
    colors = ['#1e3a8a' if m == 'Random Forest' else '#94a3b8' for m in sorted_df['Modelo']]
    
    bars = ax.barh(sorted_df['SKU'], sorted_df[metric], color=colors, edgecolor='white', linewidth=0.5, height=0.7)
    
    for bar, val in zip(bars, sorted_df[metric]):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', ha='left', fontsize=11, fontweight='bold')
        
    ax.set_xlabel(metric, fontsize=13)
    ax.set_title(title, fontweight='bold', fontsize=14, pad=15)
    
    # Expandir límite X un poco para dar espacio al texto
    ax.set_xlim(0, sorted_df[metric].max() * 1.2)
    ax.tick_params(axis='y', labelsize=12)

# Añadir leyenda general a la figura
fig.legend(handles=[legend_rf, legend_lgb], loc='lower center', ncol=2, fontsize=14, framealpha=0.9, bbox_to_anchor=(0.5, -0.05))

# Título global y fuente
fig.suptitle('Figura 12. Comparación de métricas de error (MAPE, RMSE, MAE) por SKU', fontweight='bold', fontsize=18, y=1.05)
fig.text(0.5, -0.12, 'Fuente: Elaboración propia (2026). Autores: Br. Jorfran Gil — Br. Yefferson Hernández.',
         ha='center', va='bottom', fontsize=11, color='#555555')

plt.tight_layout()

out_path = os.path.join(IMAGES_DIR, 'figura12_metricas_combinadas.png')
plt.savefig(out_path, dpi=400, bbox_inches='tight', facecolor='white')
print(f"Figura 12 (combinada) guardada en: {out_path}")
plt.close(fig)
