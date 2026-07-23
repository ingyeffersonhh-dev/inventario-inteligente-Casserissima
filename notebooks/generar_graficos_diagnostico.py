import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import os

# Create images folder if not exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '..', 'docs', 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Colors (Academic Blue-and-Grey Palette)
C_NAVY = "#1e3a8a"       # Navy Blue (Primary)
C_SLATE = "#475569"      # Slate Grey (Secondary)
C_GREY = "#94a3b8"       # Cool Grey (Tertiary)
C_CHARCOAL = "#1e293b"   # Dark Charcoal (Text and labels)
C_ICE_BLUE = "#eff6ff"   # Ice Blue (Zone A fill)
C_LIGHT_SLATE = "#f1f5f9"# Light Slate (Zone B fill)
C_VERY_LIGHT = "#f8fafc"  # Very Light Slate (Zone C fill)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = C_CHARCOAL
plt.rcParams['axes.labelcolor'] = C_CHARCOAL
plt.rcParams['xtick.color'] = C_CHARCOAL
plt.rcParams['ytick.color'] = C_CHARCOAL

# 1. Gráfico de Clasificación ABC (Pareto)
def generate_pareto():
    # Simulación realista de 20 insumos principales basada en los datos
    data = {
        'Insumo': ['Leche líquida', 'Huevos', 'Crema pastelera', 'Fresas/Frutas', 'Chocolate', 
                   'Arequipe', 'Mantequilla', 'Harina de trigo', 'Azúcar', 'Vainilla', 
                   'Polvo de hornear', 'Cacao', 'Nueces', 'Leche condensada', 'Queso crema',
                   'Gelatina', 'Esencias', 'Colorantes', 'Levadura', 'Sal'],
        'Costo Mensual ($)': [450, 380, 310, 250, 150, 110, 95, 80, 75, 45, 
                              35, 30, 28, 25, 20, 18, 15, 12, 10, 8]
    }
    
    df = pd.DataFrame(data)
    df = df.sort_values(by='Costo Mensual ($)', ascending=False)
    df['Porcentaje Acumulado'] = df['Costo Mensual ($)'].cumsum() / df['Costo Mensual ($)'].sum() * 100

    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Bar chart - color coded by Zone
    bar_colors = [C_NAVY]*4 + [C_SLATE]*3 + [C_GREY]*13
    
    bars = ax1.bar(df['Insumo'], df['Costo Mensual ($)'], color=bar_colors, alpha=0.85, edgecolor='#cbd5e1', linewidth=1)
    ax1.set_xlabel('Insumos Perecederos', fontweight='bold', fontsize=12, labelpad=10)
    ax1.set_ylabel('Costo de Consumo Mensual ($)', fontweight='bold', fontsize=12, labelpad=10)
    ax1.set_xticks(range(len(df['Insumo'])))
    ax1.set_xticklabels(df['Insumo'], rotation=45, ha='right', fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.3, color=C_GREY)

    # Line chart (Cumulative Percentage)
    ax2 = ax1.twinx()
    ax2.plot(df['Insumo'], df['Porcentaje Acumulado'], color=C_NAVY, marker='o', ms=6, lw=2, label='Acumulado %')
    ax2.set_ylabel('Porcentaje Acumulado (%)', fontweight='bold', fontsize=12, labelpad=10)
    ax2.yaxis.set_major_formatter(PercentFormatter())
    
    # Adjust limits to create headroom for the legend and prevent overlaps
    ax1.set_ylim(0, 530)
    ax2.set_ylim(0, 110)
    
    # 80% horizontal line (Threshold)
    ax2.axhline(80, color=C_SLATE, linestyle='dashed', alpha=0.7, linewidth=1.5)
    
    # Zones A, B, C shading in academic palette
    ax1.axvspan(-0.5, 3.5, color=C_ICE_BLUE, alpha=0.6, label='Zona A (80%)')
    ax1.axvspan(3.5, 6.5, color=C_LIGHT_SLATE, alpha=0.6, label='Zona B (15%)')
    ax1.axvspan(6.5, 19.5, color=C_VERY_LIGHT, alpha=0.6, label='Zona C (5%)')
    
    # Combined legend: placing in top-left with 2 columns to make it compact
    lines, labels = ax1.get_legend_handles_labels()
    line_handle = plt.Line2D([0], [0], color=C_NAVY, marker='o', linestyle='-', linewidth=2)
    lines.append(line_handle)
    labels.append('Porcentaje Acumulado')
    ax1.legend(lines, labels, loc='upper left', ncol=2, frameon=True, facecolor='white', edgecolor='#cbd5e1', shadow=False)

    plt.title('Gráfico de Pareto - Clasificación ABC de Insumos (Simulación)', fontsize=14, fontweight='bold', pad=15, color=C_NAVY)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'clasificacion_abc.png'), dpi=300)
    plt.close()

# 2. Gráfico de Patrones de Demanda
def generate_demand_patterns():
    # Queremos sacar datos reales del SQLite para la torta 3 leches (producto estrella)
    db_path = os.path.join(BASE_DIR, '..', 'src', 'casserisissima.db')
    if not os.path.exists(db_path):
        print("Database not found. Using simulated data.")
        # Simular patrón
        dates = pd.date_range(start='2024-05-23', periods=30)
        np.random.seed(42)
        base = 1.0
        sales = base + np.random.choice([0.0, 1.0], size=30, p=[0.7, 0.3])
        # Weekends
        for i, d in enumerate(dates):
            if d.weekday() >= 4:
                sales[i] = np.random.choice([1.0, 2.0], p=[0.6, 0.4])
        df = pd.DataFrame({'Fecha': dates, 'Ventas': sales})
    else:
        conn = sqlite3.connect(db_path)
        # Producto 3 leches (ID=1 o el de mas venta). Vamos a buscar el más vendido en escenario 2
        query = """
        SELECT sale_date, SUM(quantity_sold) as Ventas 
        FROM sales_transactions 
        WHERE scenario_id = 2 AND product_id = 'TF-001' 
        GROUP BY sale_date 
        ORDER BY sale_date ASC
        LIMIT 30
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        df['Fecha'] = pd.to_datetime(df['sale_date'])

    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot real data in Navy Blue
    ax.plot(df['Fecha'], df['Ventas'], marker='o', linestyle='-', color=C_NAVY, label='Ventas Diarias', linewidth=1.5, ms=5)
    
    # Moving average (trend) in Slate Grey
    df['Media_Movil'] = df['Ventas'].rolling(window=3, min_periods=1).mean()
    ax.plot(df['Fecha'], df['Media_Movil'], linestyle='--', color=C_SLATE, linewidth=2, label='Tendencia (Media Móvil 3 días)')

    # Highlight weekends with soft Light Slate
    first_weekend = True
    for date_item in df['Fecha']:
        if date_item.weekday() >= 4: # Friday, Saturday, Sunday
            label = 'Fines de semana (Picos de Demanda)' if first_weekend else ""
            ax.axvspan(date_item - pd.Timedelta(hours=12), date_item + pd.Timedelta(hours=12), color=C_LIGHT_SLATE, alpha=0.5, label=label)
            first_weekend = False

    # Adjust vertical limits to make room for legend at the top
    ax.set_ylim(-0.1, 2.4)

    # Note on the plot for weekends (shifted right and lowered to prevent overlaps with legend)
    if len(df) > 10:
        x_pos = df['Fecha'].iloc[10]
    elif len(df) > 0:
        x_pos = df['Fecha'].iloc[len(df)//2]
    else:
        x_pos = pd.Timestamp.now()
    
    y_pos = df['Ventas'].max() * 0.62 if not df.empty else 1.2
    
    ax.text(x_pos, y_pos, 'Fines de semana\n(Picos de Demanda)', 
            fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='#cbd5e1', boxstyle='round,pad=0.5'),
            ha='center', va='center')

    ax.set_xlabel('Fecha', fontweight='bold', fontsize=12, labelpad=10)
    ax.set_ylabel('Unidades Vendidas', fontweight='bold', fontsize=12, labelpad=10)
    ax.set_title('Patrón de Demanda Diaria - Torta Tres Leches (Estacionalidad Semanal)', fontsize=14, fontweight='bold', pad=15, color=C_NAVY)
    ax.grid(axis='y', linestyle='--', alpha=0.3, color=C_GREY)
    ax.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#cbd5e1')

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'patrones_demanda.png'), dpi=300)
    plt.close()

if __name__ == '__main__':
    print("Generando Gráfico Pareto...")
    generate_pareto()
    print("Generando Gráfico Patrones de Demanda...")
    generate_demand_patterns()
    print("¡Gráficos generados exitosamente en docs/images/!")

