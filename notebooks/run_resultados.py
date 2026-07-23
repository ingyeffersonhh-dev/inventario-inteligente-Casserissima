import sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'figure.figsize': (12, 5), 'figure.dpi': 150, 'savefig.dpi': 300, 'savefig.bbox': 'tight', 'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11})

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'docs', 'images')
sys.path.insert(0, SRC_DIR)
os.makedirs(IMAGES_DIR, exist_ok=True)

def save_fig(fig, name):
    path = os.path.join(IMAGES_DIR, f'{name}.png')
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'  Saved: {path}')

from db.database import SessionLocal, init_db
from db.models import Product, SaleTransaction
from core.ml.model_trainer import train_product_model

init_db()
db = SessionLocal()
products = db.query(Product).filter(Product.is_active == True).all()

sku_mapping = {
    'TF-3LECHES': 'TF-001', 'TF-HELADO': 'TF-002', 'TF-BESO': 'TF-003',
    'TF-PARCH': 'TF-004', 'TF-DULCE': 'TF-005', 'TF-MARQ': 'TF-006',
    'TC-CHOCB': 'TC-001', 'TC-PINA': 'TC-002', 'TC-MARM': 'TC-003',
    'TC-VAIN': 'TC-004', 'TC-OVO': 'TC-005', 'TC-ZANH': 'TC-006'
}

SCENARIO_ID = 2
results = []
for idx, prod in enumerate(products, 1):
    db_sku = sku_mapping.get(prod.sku, prod.sku)
    sales_rows = db.query(SaleTransaction.sale_date, SaleTransaction.quantity_sold).filter(SaleTransaction.scenario_id == SCENARIO_ID, SaleTransaction.product_id == db_sku).order_by(SaleTransaction.sale_date).all()
    if len(sales_rows) < 7: continue
    sales_df = pd.DataFrame([(r.sale_date.isoformat(), float(r.quantity_sold)) for r in sales_rows], columns=['sale_date', 'quantity_sold'])
    try:
        result = train_product_model(sales_df=sales_df, product_id=prod.id, sku=prod.sku, shelf_life_days=prod.shelf_life_days, n_cv_splits=3)
        model_type = result['version_tag'].split('_')[0]
        results.append({'Producto': prod.name, 'SKU': prod.sku, 'Categoría': prod.category, 'Modelo Ganador': 'LightGBM' if model_type == 'lgbm' else 'Random Forest', 'MAPE': result['mape_val'], 'RMSE': result['rmse_val'], 'MAE': result['mae_val'], 'Filas': result['training_rows']})
    except Exception as e:
        print(f'Error con {prod.name}: {e}')

results_df = pd.DataFrame(results)

# Figure 1
fig, ax = plt.subplots(figsize=(12, 6))
sorted_df = results_df.sort_values('MAE', ascending=True)
colors = ['#1e3a8a' if m == 'Random Forest' else '#94a3b8' for m in sorted_df['Modelo Ganador']]
bars = ax.barh(sorted_df['Producto'], sorted_df['MAE'], color=colors, edgecolor='white', linewidth=0.5)
ax.set_xlabel('MAE (Error Absoluto Medio en unidades de torta)')
ax.set_title('Figura 1: Error Absoluto Medio (MAE) por Producto — Escenario Óptimo', fontweight='bold')
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#1e3a8a', label='Random Forest'), Patch(facecolor='#94a3b8', label='LightGBM')]
ax.legend(handles=legend_elements, loc='lower right')
for bar, val in zip(bars, sorted_df['MAE']):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, f'{val:.3f}', va='center', fontsize=9)
plt.tight_layout()
save_fig(fig, 'fig01_mae_por_producto')
plt.close()

# Figure 2
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
metrics = [('MAPE', 'MAPE (Error Porcentual)', '#1e3a8a'), ('RMSE', 'RMSE (Error Cuadrático)', '#3b82f6'), ('MAE', 'MAE (Error Absoluto)', '#64748b')]
for ax, (metric, title, color) in zip(axes, metrics):
    sorted_by = results_df.sort_values(metric, ascending=True)
    ax.barh(sorted_by['SKU'], sorted_by[metric], color=color, alpha=0.8)
    ax.set_xlabel(metric)
    ax.set_title(title, fontweight='bold')
plt.suptitle('Figura 2: Comparación de Métricas de Error por Producto', fontweight='bold', fontsize=14, y=1.02)
plt.tight_layout()
save_fig(fig, 'fig02_metricas_comparadas')
plt.close()

# Figure 3
winner_counts = results_df['Modelo Ganador'].value_counts()
fig, ax = plt.subplots(figsize=(6, 6))
colors = ['#1e3a8a' if w == 'Random Forest' else '#94a3b8' for w in winner_counts.index]
wedges, texts, autotexts = ax.pie(winner_counts.values, labels=winner_counts.index, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 12})
for autotext in autotexts: autotext.set_fontweight('bold')
ax.set_title('Figura 3: Distribución de Modelos Ganadores\n(seleccionados por menor RMSE)', fontweight='bold')
save_fig(fig, 'fig03_modelos_ganadores')
plt.close()
