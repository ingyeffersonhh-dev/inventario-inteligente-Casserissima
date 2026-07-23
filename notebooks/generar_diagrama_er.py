"""
CASSERISISSIMA 2.0 — Diagrama Entidad-Relación (ER)
Tamaño maximizado para lectura en Word.
Se ajustan las flechas para evitar superposiciones (rutas ortogonales).
"""
import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE_DIR, '..', 'docs', 'images', 'diagrama_er.excalidraw')
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

C_NAVY       = "#1e3a8a"
C_BLUE       = "#2b6cb0"
C_SLATE      = "#475569"
C_GREY_LIGHT = "#f1f5f9"
C_GREEN      = "#166534"
C_AMBER      = "#92400e"
C_CHARCOAL   = "#1e293b"
C_WHITE      = "#ffffff"

elements = []
_id = 0

def nid():
    global _id
    _id += 1
    return f"er_{_id:04d}"

def table_box(x, y, title, fields, fill, stroke, text_color=None, title_fill=None):
    tc = text_color or C_WHITE
    tf = title_fill or stroke
    ROW_H = 40
    HDR_H = 50
    w = 420
    total_h = HDR_H + len(fields) * ROW_H

    outer_id = nid()
    outer = {
        "type": "rectangle", "id": outer_id,
        "x": x, "y": y, "width": w, "height": total_h,
        "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(outer_id)) % 99999, "version": 1,
        "versionNonce": abs(hash(outer_id+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "link": None, "locked": False,
        "boundElements": [], "roundness": {"type": 2}
    }
    elements.append(outer)

    hdr_id = nid()
    hdr_tid = nid()
    hdr = {
        "type": "rectangle", "id": hdr_id,
        "x": x, "y": y, "width": w, "height": HDR_H,
        "strokeColor": stroke, "backgroundColor": tf,
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(hdr_id)) % 99999, "version": 1,
        "versionNonce": abs(hash(hdr_id+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "link": None, "locked": False,
        "boundElements": [{"id": hdr_tid, "type": "text"}],
        "roundness": {"type": 2}
    }
    elements.append(hdr)

    hdr_text = {
        "type": "text", "id": hdr_tid,
        "x": x, "y": y, "width": w, "height": HDR_H,
        "text": title, "originalText": title,
        "fontSize": 22, "fontFamily": 3,
        "textAlign": "center", "verticalAlign": "middle",
        "strokeColor": C_WHITE, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(hdr_tid)) % 99999, "version": 1,
        "versionNonce": abs(hash(hdr_tid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "link": None, "locked": False,
        "containerId": hdr_id, "lineHeight": 1.25, "fontWeight": 700
    }
    elements.append(hdr_text)

    for i, (fname, ftype, pk_fk) in enumerate(fields):
        ry = y + HDR_H + i * ROW_H
        prefix = "🔑 " if pk_fk == "PK" else ("🔗 " if pk_fk == "FK" else "   ")
        row_label = f"{prefix}{fname}  :  {ftype}"

        row_id = nid()
        row_tid = nid()
        row_fill = C_GREY_LIGHT if i % 2 == 0 else C_WHITE
        row = {
            "type": "rectangle", "id": row_id,
            "x": x + 1, "y": ry, "width": w - 2, "height": ROW_H,
            "strokeColor": stroke, "backgroundColor": row_fill,
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "angle": 0,
            "seed": abs(hash(row_id)) % 99999, "version": 1,
            "versionNonce": abs(hash(row_id+"v")) % 99999,
            "isDeleted": False, "groupIds": [], "link": None, "locked": False,
            "boundElements": [{"id": row_tid, "type": "text"}],
            "roundness": None
        }
        elements.append(row)

        row_text = {
            "type": "text", "id": row_tid,
            "x": x + 15, "y": ry, "width": w - 30, "height": ROW_H,
            "text": row_label, "originalText": row_label,
            "fontSize": 16, "fontFamily": 3,
            "textAlign": "left", "verticalAlign": "middle",
            "strokeColor": C_CHARCOAL, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "angle": 0,
            "seed": abs(hash(row_tid)) % 99999, "version": 1,
            "versionNonce": abs(hash(row_tid+"v")) % 99999,
            "isDeleted": False, "groupIds": [], "link": None, "locked": False,
            "containerId": row_id, "lineHeight": 1.25, "fontWeight": 400
        }
        elements.append(row_text)

    return outer_id

def rel_line_points(x, y, points, label="", color=C_SLATE):
    # points = array de offsets relativos a [x, y], ej: [[0,0], [100,0], [100,50]]
    aid = nid()
    
    # Calcular width/height base bounds (para Excalidraw format)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    
    a = {
        "type": "arrow", "id": aid,
        "x": x, "y": y,
        "width": abs(w) if w != 0 else 1, "height": abs(h) if h != 0 else 1,
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(aid)) % 99999, "version": 1,
        "versionNonce": abs(hash(aid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "link": None, "locked": False,
        "points": points,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None, "endArrowhead": "arrow",
        "boundElements": []
    }
    elements.append(a)

def free_text(x, y, w, h, text, color, size=16, bold=False):
    tid = nid()
    t = {
        "type": "text", "id": tid,
        "x": x, "y": y, "width": w, "height": h,
        "text": text, "originalText": text,
        "fontSize": size, "fontFamily": 3,
        "textAlign": "center", "verticalAlign": "middle",
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(tid)) % 99999, "version": 1,
        "versionNonce": abs(hash(tid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "link": None, "locked": False,
        "containerId": None, "lineHeight": 1.25,
        "fontWeight": 700 if bold else 400
    }
    elements.append(t)

# ── Título ──────────────────────────────────────────────────────────────────
free_text(40, 20, 1400, 40,
    "Figura N. Diagrama Entidad-Relación — Base de Datos CASSERIISSIMA 2.0",
    C_CHARCOAL, size=26, bold=True)

# ── ENTIDADES ───────────────────────────────────────────────────────────────
COL1 = 40
COL2 = 540
COL3 = 1040

# products (Altura = 50 + 9*40 = 410)
# Caja Y: 120 -> Bottom: 530
table_box(COL1, 120, "products", [
    ("id",               "VARCHAR(50)",  "PK"),
    ("sku",              "VARCHAR(20)",  ""),
    ("name",             "VARCHAR(100)", ""),
    ("category",         "VARCHAR(50)",  ""),
    ("selling_price",    "FLOAT",        ""),
    ("unit_cost",        "FLOAT",        ""),
    ("shelf_life_days",  "INTEGER",      ""),
    ("lead_time_days",   "INTEGER",      ""),
    ("is_active",        "BOOLEAN",      ""),
], fill=C_WHITE, stroke=C_NAVY, text_color=C_NAVY, title_fill=C_NAVY)

# ingredients
table_box(COL1, 600, "ingredients", [
    ("id",               "INTEGER",      "PK"),
    ("name",             "VARCHAR(100)", ""),
    ("unit",             "VARCHAR(20)",  ""),
    ("current_stock",    "FLOAT",        ""),
    ("alert_threshold",  "FLOAT",        ""),
    ("updated_at",       "DATETIME",     ""),
], fill=C_WHITE, stroke=C_GREEN, text_color=C_GREEN, title_fill=C_GREEN)

# sales_transactions
table_box(COL2, 120, "sales_transactions", [
    ("id",               "INTEGER",      "PK"),
    ("product_id",       "VARCHAR(50)",  "FK"),
    ("scenario_id",      "INTEGER",      ""),
    ("sale_date",        "DATE",         ""),
    ("quantity_sold",    "FLOAT",        ""),
    ("revenue",          "FLOAT",        ""),
    ("day_of_week",      "INTEGER",      ""),
    ("is_holiday",       "BOOLEAN",      ""),
    ("is_payday",        "BOOLEAN",      ""),
], fill=C_WHITE, stroke=C_BLUE, text_color=C_BLUE, title_fill=C_BLUE)

# scenario_config
table_box(COL2, 600, "scenario_config", [
    ("id",               "INTEGER",      "PK"),
    ("active_scenario",  "INTEGER",      ""),
    ("updated_at",       "DATETIME",     ""),
], fill=C_WHITE, stroke=C_BLUE, text_color=C_BLUE, title_fill=C_BLUE)

# demand_forecasts
table_box(COL3, 120, "demand_forecasts", [
    ("id",               "INTEGER",      "PK"),
    ("product_id",       "VARCHAR(50)",  "FK"),
    ("model_version",    "VARCHAR(50)",  ""),
    ("forecast_date",    "DATE",         ""),
    ("predicted_demand", "FLOAT",        ""),
    ("lower_bound_90",   "FLOAT",        ""),
    ("upper_bound_90",   "FLOAT",        ""),
    ("mape",             "FLOAT",        ""),
    ("rmse",             "FLOAT",        ""),
    ("generated_at",     "DATETIME",     ""),
], fill=C_WHITE, stroke=C_AMBER, text_color=C_AMBER, title_fill=C_AMBER)

# model_registry
table_box(COL3, 600, "model_registry", [
    ("id",               "INTEGER",      "PK"),
    ("product_id",       "VARCHAR(50)",  "FK"),
    ("version_tag",      "VARCHAR(80)",  ""),
    ("mape_val",         "FLOAT",        ""),
    ("rmse_val",         "FLOAT",        ""),
    ("mae_val",          "FLOAT",        ""),
    ("hyperparameters",  "TEXT (JSON)",  ""),
    ("is_active",        "BOOLEAN",      ""),
    ("trained_at",       "DATETIME",     ""),
], fill=C_WHITE, stroke=C_AMBER, text_color=C_AMBER, title_fill=C_AMBER)

# ── RELACIONES (Rutas ortogonales) ──────────────────────────────────────────

# products → sales_transactions (1:N)
# Sale del borde derecho de products hacia borde izquierdo de sales
px1 = COL1 + 420
py1 = 120 + 50 + 40 + 20 # product_id fk pos en sales_trans: índice 1 -> 50 + 1*40 + 20 = 110. En products, id es idx 0 -> 50 + 20 = 70
# Conectemos pk de products con fk de sales
py1_pk = 120 + 50 + 20  # centro de 'id' en products
py1_fk = 120 + 50 + 40 + 20 # centro de 'product_id' en sales
rel_line_points(px1, py1_pk, [
    [0, 0], 
    [40, 0], 
    [40, py1_fk - py1_pk], 
    [COL2 - px1, py1_fk - py1_pk]
], color=C_NAVY)
free_text(px1 + 5, py1_pk - 25, 60, 20, "1 : N", C_NAVY, size=16, bold=True)

# products → demand_forecasts (1:N)
# Sale de la base de products hacia la base de demand_forecasts
px2 = COL1 + 210  # centro bottom products
py2 = 120 + 410   # bottom edge products
py2_fk = 120 + 50 + 40 + 20 # product_id en demand_forecasts
# Vamos hacia abajo, derecha hasta debajo de demand_forecasts, y subimos
rel_line_points(px2, py2, [
    [0, 0],
    [0, 30], # bajamos 30 px
    [COL3 - 20 - px2, 30], # vamos derecha hasta antes de demand_forecasts
    [COL3 - 20 - px2, py2_fk - py2], # subimos
    [COL3 - px2, py2_fk - py2] # entramos al borde izquierdo de demand_forecasts
], color=C_AMBER)
free_text(COL3 - 80, py2_fk - 30, 60, 20, "1 : N", C_AMBER, size=16, bold=True)

# products → model_registry (1:N)
# Sale de la base de products hacia borde izquierdo de model_registry
px3 = COL1 + 300 # un poco mas a la derecha en el bottom
py3 = 120 + 410  # bottom edge products
py3_fk = 600 + 50 + 40 + 20 # product_id en model_registry
rel_line_points(px3, py3, [
    [0, 0],
    [0, py3_fk - py3], # bajamos directo hasta la altura de FK
    [COL3 - px3, py3_fk - py3] # derecha hasta entrar a la caja
], color=C_AMBER)
free_text(COL3 - 80, py3_fk - 30, 60, 20, "1 : N", C_AMBER, size=16, bold=True)

# ── Leyenda ─────────────────────────────────────────────────────────────────
free_text(40, 1050, 1400, 30,
    "Fuente: Elaboración propia (2026).   🔑 PK = Clave Primaria   🔗 FK = Clave Foránea   1:N = Relación uno a muchos",
    C_SLATE, size=16)

diagram = {
    "type": "excalidraw", "version": 2, "source": "casserisissima-thesis",
    "elements": elements,
    "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}
}
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(diagram, f, ensure_ascii=False, indent=2)
print("Diagrama ER (Rutas Ortogonales) generado.")
