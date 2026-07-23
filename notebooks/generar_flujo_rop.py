"""
CASSERISISSIMA 2.0 — Diagrama de Flujo del Cálculo del ROP Evolutivo
Versión Mejorada: Estructura de Diagrama de Flujo de Ingeniería.
"""
import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE_DIR, '..', 'docs', 'images', 'flujo_rop_evolutivo.excalidraw')
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

C_NAVY       = "#1e3a8a"
C_BLUE       = "#2b6cb0"
C_SLATE      = "#475569"
C_GREY_LIGHT = "#f8fafc"
C_GREEN      = "#166534"
C_AMBER      = "#92400e"
C_RED        = "#991b1b"
C_CHARCOAL   = "#0f172a"
C_WHITE      = "#ffffff"
C_BG_GROUP   = "#e2e8f0"

elements = []
_id = 0

def nid():
    global _id
    _id += 1
    return f"rop_v2_{_id:04d}"

def draw_rect(x, y, w, h, fill, stroke, strokeWidth=2, dashed=False, roundness=3, opacity=100):
    rid = nid()
    elements.append({
        "type": "rectangle", "id": rid,
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": strokeWidth,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0, "opacity": opacity, "angle": 0,
        "seed": abs(hash(rid)) % 99999, "version": 1,
        "versionNonce": abs(hash(rid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "roundness": {"type": roundness} if roundness else None
    })
    return rid

def draw_diamond(x, y, w, h, fill, stroke):
    did = nid()
    elements.append({
        "type": "diamond", "id": did,
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(did)) % 99999, "version": 1,
        "versionNonce": abs(hash(did+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "roundness": None
    })
    return did

def text_node(x, y, w, h, text, color, size=18, bold=False, align="center"):
    tid = nid()
    elements.append({
        "type": "text", "id": tid,
        "x": x, "y": y, "width": w, "height": h,
        "text": text, "originalText": text,
        "fontSize": size, "fontFamily": 3, # Monospace academico
        "textAlign": align, "verticalAlign": "middle",
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(tid)) % 99999, "version": 1,
        "versionNonce": abs(hash(tid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "lineHeight": 1.25, "fontWeight": 700 if bold else 400
    })
    return tid

def block(x, y, w, h, fill, stroke, title, subtitle="", size=18):
    draw_rect(x, y, w, h, fill, stroke)
    if subtitle:
        text_node(x+10, y+10, w-20, h/2-10, title, stroke, size=size+2, bold=True)
        text_node(x+10, y+h/2, w-20, h/2-10, subtitle, C_CHARCOAL, size=size-2, bold=False)
    else:
        text_node(x+10, y, w-20, h, title, stroke, size=size, bold=True)

def arrow_pts(points, color=C_SLATE, dashed=False):
    aid = nid()
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    elements.append({
        "type": "arrow", "id": aid,
        "x": points[0][0], "y": points[0][1],
        "width": w if w!=0 else 1, "height": h if h!=0 else 1,
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(aid)) % 99999, "version": 1,
        "versionNonce": abs(hash(aid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "points": [[p[0]-points[0][0], p[1]-points[0][1]] for p in points],
        "startArrowhead": None, "endArrowhead": "arrow"
    })

# ── Título ──────────────────────────────────────────────────────────────────
text_node(40, 20, 1400, 40, "Figura N. Flujo de Control y Decisión: Punto de Reorden Evolutivo (ROP)", C_CHARCOAL, size=26, bold=True)

# ── 1. BLOQUES DE ENTRADA (Arriba) ──────────────────────────────────────────
# Grupo Entradas Operativas
draw_rect(80, 100, 400, 240, C_GREY_LIGHT, C_NAVY, dashed=True, roundness=3)
text_node(80, 110, 400, 30, "MÓDULO DE INVENTARIO", C_NAVY, size=16, bold=True)
block(110, 150, 340, 50, C_WHITE, C_NAVY, "μ = Demanda Media Diaria")
block(110, 210, 340, 50, C_WHITE, C_NAVY, "σ = Desviación Estándar")
block(110, 270, 340, 50, C_WHITE, C_NAVY, "LT = Tiempo de Entrega (Días)")

# Grupo Entradas Predictivas
draw_rect(960, 100, 400, 240, C_GREY_LIGHT, C_AMBER, dashed=True, roundness=3)
text_node(960, 110, 400, 30, "MOTOR PREDICTIVO (Random Forest)", C_AMBER, size=16, bold=True)
block(990, 170, 340, 60, C_WHITE, C_AMBER, "MAPE", "Error Porcentual Medio")
block(990, 250, 340, 60, C_WHITE, C_AMBER, "RMSE", "Error Cuadrático Medio")

# ── 2. MOTOR DE CÁLCULO CENTRAL ────────────────────────────────────────────
CY = 420
CX = 500
W = 440

# Fondo del motor de cálculo
draw_rect(CX-40, CY-40, W+80, 480, C_GREY_LIGHT, C_SLATE, strokeWidth=1, roundness=3)
text_node(CX, CY-30, W, 30, "CÁLCULO DEL INVENTARIO DE SEGURIDAD Y ROP", C_SLATE, size=16, bold=True)

# Step 1: Expected Demand
block(CX, CY + 20, W, 80, C_WHITE, C_NAVY, "1. Demanda Esperada en LT", "μ_LT = μ × LT", size=20)

# Step 2: Penalización de Volatilidad
block(CX, CY + 130, W, 80, C_WHITE, C_AMBER, "2. Ajuste de Volatilidad por Error ML", "σ_adj = σ × √(LT) × (1 + MAPE)", size=20)

# Step 3: Safety Stock
block(CX, CY + 240, W, 80, C_WHITE, C_BLUE, "3. Inventario de Seguridad Dinámico", "SS = z(97%) × σ_adj + [√(LT) × RMSE × 0.5]", size=20)

# Step 4: Final ROP
block(CX, CY + 350, W, 80, C_WHITE, C_NAVY, "4. Punto de Reorden Evolutivo", "ROP(t) = μ_LT + SS", size=24)

# Flechas centrales
arrow_pts([[CX+W/2, CY+100], [CX+W/2, CY+130]], C_SLATE)
arrow_pts([[CX+W/2, CY+210], [CX+W/2, CY+240]], C_SLATE)
arrow_pts([[CX+W/2, CY+320], [CX+W/2, CY+350]], C_SLATE)

# Flechas desde Entradas al Centro
arrow_pts([[280, 340], [280, 460], [CX, 460]], C_NAVY)    # Operativas -> Paso 1
arrow_pts([[1160, 340], [1160, 550], [CX+W, 550]], C_AMBER) # MAPE -> Paso 2
arrow_pts([[1160, 340], [1160, 660], [CX+W, 660]], C_AMBER) # RMSE -> Paso 3

# ── 3. LÓGICA DE DECISIÓN Y ALERTAS ─────────────────────────────────────────
DY = CY + 520
# Rombo de decisión
draw_diamond(CX+W/2 - 160, DY, 320, 140, C_WHITE, C_CHARCOAL)
text_node(CX+W/2 - 140, DY + 20, 280, 100, "¿Inventario Físico\n≤ ROP(t)?", C_CHARCOAL, size=22, bold=True)

# Flecha del ROP al Rombo
arrow_pts([[CX+W/2, CY+430], [CX+W/2, DY]], C_SLATE)

# Salidas del Rombo (NO y SI)
arrow_pts([[CX+W/2 - 160, DY+70], [240, DY+70], [240, DY+180]], C_GREEN)
text_node(CX+W/2 - 220, DY+40, 60, 30, "NO", C_GREEN, size=20, bold=True)

arrow_pts([[CX+W/2 + 160, DY+70], [950, DY+70], [950, DY+130]], C_RED)
text_node(CX+W/2 + 160, DY+40, 60, 30, "SÍ", C_RED, size=20, bold=True)

# ── 4. ALERTAS (Abajo) ──────────────────────────────────────────────────────
AY = DY + 180
AW = 300
AH = 100

# Izquierda (Estado Normal)
block(90, AY, AW, AH, C_WHITE, C_GREEN, "ESTADO: SIN ALERTA", "Stock saludable\n(> ROP × 1.2)", size=20)

# Derecha (Clasificación de Severidad - SI es menor al ROP)
AY_CRIT = DY + 180
# Sub-rombo para severidad? No, de frente a cajas
draw_rect(650, AY_CRIT - 50, 600, 190, C_GREY_LIGHT, C_RED, dashed=True)
text_node(650, AY_CRIT - 40, 600, 30, "EVALUACIÓN DE SEVERIDAD", C_RED, size=16, bold=True)

block(680, AY_CRIT, 250, AH, C_WHITE, C_RED, "ALERTA CRÍTICA", "Stock ≤ ROP × 0.5\n(Riesgo Inminente)", size=18)
block(960, AY_CRIT, 250, AH, C_WHITE, C_AMBER, "ALERTA ALTA", "Stock ≤ ROP\n(Reorden Recomendado)", size=18)

# Flechas a severidad
arrow_pts([[950, DY+130], [805, DY+130], [805, AY_CRIT]], C_RED)
arrow_pts([[950, DY+130], [1085, DY+130], [1085, AY_CRIT]], C_AMBER)


# ── Leyenda ─────────────────────────────────────────────────────────────────
text_node(40, AY_CRIT + 200, 1300, 30, "Fuente: Elaboración propia (2026). Arquitectura de decisión del módulo src/core/operations_research/reorder_point.py", C_SLATE, size=16)

diagram = {
    "type": "excalidraw", "version": 2, "source": "casserisissima-thesis",
    "elements": elements,
    "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}
}
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(diagram, f, ensure_ascii=False, indent=2)
print("Diagrama Flujo ROP Evolutivo (V2 Mejorado) generado.")
