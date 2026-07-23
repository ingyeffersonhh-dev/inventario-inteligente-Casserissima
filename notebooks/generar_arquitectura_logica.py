"""
CASSERISISSIMA 2.0 — Diagrama de Arquitectura Lógica (Three-Tier, Tamaño Word)
Paleta Académica oficial y tipografía grande para legibilidad en el documento.
"""
import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE_DIR, '..', 'docs', 'images', 'arquitectura_logica.excalidraw')
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# ── Paleta Académica (Oficial de la Tesis) ────────────────────────────────────
C_NAVY       = "#1e3a8a"   # Presentación (Next.js)
C_BLUE       = "#2b6cb0"   # Aplicación (FastAPI)
C_SLATE      = "#475569"   # Textos secundarios
C_GREY_LIGHT = "#f1f5f9"   # Fondos de caja
C_GREEN      = "#166534"   # Datos (SQLite)
C_AMBER      = "#92400e"   # Motores (ML / OR)
C_CHARCOAL   = "#1e293b"   # Textos principales
C_WHITE      = "#ffffff"

elements = []
_id = 0

def nid():
    global _id
    _id += 1
    return f"el_{_id:04d}"

def draw_box(x, y, w, h, bg, stroke, label="", sublabel="", font_size=20, roundness=3, dashed=False, stroke_w=2, text_color=C_CHARCOAL):
    rid = nid()
    r = {
        "type": "rectangle", "id": rid,
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": "solid", "strokeWidth": stroke_w,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(rid)) % 99999, "version": 1,
        "versionNonce": abs(hash(rid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "link": None, "locked": False,
        "boundElements": [], "roundness": {"type": roundness}
    }
    elements.append(r)
    
    if label:
        tid = nid()
        # Ajuste vertical dependiendo de si hay sublabel o no
        y_label = y + 15 if sublabel else y + (h/2 - font_size/2)
        t = {
            "type": "text", "id": tid,
            "x": x + 15, "y": y_label,
            "width": w - 30, "height": font_size * 1.5,
            "text": label, "originalText": label,
            "fontSize": font_size, "fontFamily": 3, # Tipografía Académica (3)
            "textAlign": "center" if not sublabel else "left",
            "verticalAlign": "middle",
            "strokeColor": text_color, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "angle": 0,
            "seed": abs(hash(tid)) % 99999, "version": 1,
            "versionNonce": abs(hash(tid+"v")) % 99999,
            "isDeleted": False, "groupIds": [], "link": None, "locked": False,
            "containerId": None, "lineHeight": 1.2, "fontWeight": 700
        }
        elements.append(t)
        
    if sublabel:
        sid = nid()
        s = {
            "type": "text", "id": sid,
            "x": x + 15, "y": y + 15 + font_size + 10,
            "width": w - 30, "height": (font_size-4) * 1.5,
            "text": sublabel, "originalText": sublabel,
            "fontSize": font_size - 4, "fontFamily": 3,
            "textAlign": "left", "verticalAlign": "middle",
            "strokeColor": text_color, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "angle": 0,
            "seed": abs(hash(sid)) % 99999, "version": 1,
            "versionNonce": abs(hash(sid+"v")) % 99999,
            "isDeleted": False, "groupIds": [], "link": None, "locked": False,
            "containerId": None, "lineHeight": 1.2, "fontWeight": 400
        }
        elements.append(s)
        
    return rid

def arrow(x1, y1, x2, y2, label="", dashed=False, bi=False):
    aid = nid()
    a = {
        "type": "arrow", "id": aid,
        "x": x1, "y": y1,
        "width": abs(x2-x1), "height": abs(y2-y1),
        "strokeColor": C_SLATE, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": abs(hash(aid)) % 99999, "version": 1,
        "versionNonce": abs(hash(aid+"v")) % 99999,
        "isDeleted": False, "groupIds": [], "link": None, "locked": False,
        "points": [[0, 0], [x2-x1, y2-y1]],
        "startBinding": None, "endBinding": None,
        "startArrowhead": "arrow" if bi else None, 
        "endArrowhead": "arrow",
        "boundElements": []
    }
    elements.append(a)
    
    if label:
        tid = nid()
        cx = x1 + (x2-x1)/2
        cy = y1 + (y2-y1)/2
        t = {
            "type": "text", "id": tid,
            "x": cx - 80, "y": cy - 15, "width": 160, "height": 30,
            "text": label, "originalText": label,
            "fontSize": 18, "fontFamily": 3,
            "textAlign": "center", "verticalAlign": "middle",
            "strokeColor": C_SLATE, "backgroundColor": C_WHITE,
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "angle": 0,
            "seed": abs(hash(tid)) % 99999, "version": 1,
            "versionNonce": abs(hash(tid+"v")) % 99999,
            "isDeleted": False, "groupIds": [], "link": None, "locked": False,
            "containerId": None, "lineHeight": 1.2, "fontWeight": 600
        }
        elements.append(t)


# ── TÍTULO ────────────────────────────────────────────────────────────────────
draw_box(40, 20, 1000, 40, "transparent", "transparent", 
         label="Figura N. Arquitectura Lógica de 3 Capas (Three-Tier Architecture)", 
         font_size=26, stroke_w=0)


# ── CAPA 1: PRESENTACIÓN ──────────────────────────────────────────────────────
y1 = 120
draw_box(40, y1, 1000, 180, C_GREY_LIGHT, C_NAVY, dashed=True)
draw_box(60, y1 - 20, 300, 40, C_GREY_LIGHT, C_NAVY, label="CAPA DE PRESENTACIÓN", font_size=18, text_color=C_NAVY)

fw = 250
draw_box(70, y1 + 50, fw, 90, C_WHITE, C_NAVY, label="Dashboard", sublabel="KPIs y Alertas", font_size=20)
draw_box(70 + fw + 30, y1 + 50, fw, 90, C_WHITE, C_NAVY, label="Predicciones", sublabel="Gráficas por producto", font_size=20)
draw_box(70 + (fw + 30)*2, y1 + 50, fw, 90, C_WHITE, C_NAVY, label="Operaciones", sublabel="Ingresos / Cierres", font_size=20)

# Badge Next.js
draw_box(890, y1 + 65, 130, 60, C_NAVY, C_NAVY, label="Next.js 15\nReact/TS", font_size=16, text_color=C_WHITE)

# Flecha HTTP/REST
arrow(540, y1 + 180, 540, 400, label="REST API (JSON)", bi=True, dashed=True)


# ── CAPA 2: APLICACIÓN / NEGOCIO ──────────────────────────────────────────────
y2 = 400
draw_box(40, y2, 1000, 400, C_GREY_LIGHT, C_BLUE, dashed=True)
draw_box(60, y2 - 20, 300, 40, C_GREY_LIGHT, C_BLUE, label="CAPA DE APLICACIÓN", font_size=18, text_color=C_BLUE)

# Badge FastAPI
draw_box(890, y2 + 20, 130, 60, C_BLUE, C_BLUE, label="FastAPI\nPython", font_size=16, text_color=C_WHITE)

# Routers (API Gateway interno)
draw_box(70, y2 + 60, 300, 310, C_WHITE, C_BLUE)
draw_box(80, y2 + 80, 280, 30, "transparent", "transparent", label="API Routers (Controladores)", font_size=18, text_color=C_BLUE)

draw_box(90, y2 + 130, 260, 40, C_GREY_LIGHT, C_BLUE, label="routers/dashboard.py", font_size=16)
draw_box(90, y2 + 180, 260, 40, C_GREY_LIGHT, C_BLUE, label="routers/predictions.py", font_size=16)
draw_box(90, y2 + 230, 260, 40, C_GREY_LIGHT, C_BLUE, label="routers/inventory.py", font_size=16)
draw_box(90, y2 + 280, 260, 40, C_GREY_LIGHT, C_BLUE, label="routers/sales.py", font_size=16)

# Motores Core
draw_box(450, y2 + 60, 560, 310, C_WHITE, C_AMBER)
draw_box(460, y2 + 80, 540, 30, "transparent", "transparent", label="Motores Core (Lógica de Negocio)", font_size=18, text_color=C_AMBER)

# ML Engine
draw_box(470, y2 + 130, 250, 220, C_GREY_LIGHT, C_AMBER, label="Motor Predictivo (ML)\n\n• Feature Eng.\n• Pipeline (RF)\n• Model Registry", font_size=18, text_color=C_CHARCOAL)

# Operations Research
draw_box(740, y2 + 130, 250, 220, C_GREY_LIGHT, C_AMBER, label="Inves. Operativa\n\n• ROP Evolutivo\n• Safety Stock\n• Newsvendor", font_size=18, text_color=C_CHARCOAL)

# Flechas internas Backend
arrow(370, y2 + 200, 450, y2 + 200, label="Servicios", bi=True)


# ── CAPA 3: DATOS / PERSISTENCIA ──────────────────────────────────────────────
y3 = 900
draw_box(40, y3, 1000, 180, C_GREY_LIGHT, C_GREEN, dashed=True)
draw_box(60, y3 - 20, 300, 40, C_GREY_LIGHT, C_GREEN, label="CAPA DE PERSISTENCIA", font_size=18, text_color=C_GREEN)

# Badge SQLite
draw_box(890, y3 + 50, 130, 60, C_GREEN, C_GREEN, label="SQLite 3", font_size=16, text_color=C_WHITE)

# ORM & Tables
draw_box(70, y3 + 50, 280, 100, C_WHITE, C_GREEN, label="SQLAlchemy ORM", sublabel="Mapeo Objeto-Relacional", font_size=20)
draw_box(450, y3 + 50, 420, 100, C_WHITE, C_GREEN, label="Base de Datos Relacional", sublabel="products, sales, forecasts, models", font_size=20)

# Flechas a BD
arrow(350, y3 + 100, 450, y3 + 100, bi=True)
arrow(210, y2 + 400, 210, y3, label="Consultas DB", bi=True, dashed=True)
arrow(730, y2 + 400, 730, y3, label="Persistencia", bi=True, dashed=True)

# ── LEYENDA ───────────────────────────────────────────────────────────────────
draw_box(40, 1150, 1000, 40, "transparent", "transparent", 
         label="Fuente: Elaboración propia (2026). Arquitectura Cliente-Servidor Desacoplada.", 
         font_size=16, stroke_w=0, text_color=C_SLATE)

# ─────────────────────────────────────────────────────────────────────────────
diagram = {
    "type": "excalidraw", "version": 2,
    "source": "casserisissima-thesis",
    "elements": elements,
    "appState": {"viewBackgroundColor": C_WHITE, "gridSize": None},
    "files": {}
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(diagram, f, ensure_ascii=False, indent=2)

print("Diagrama de Arquitectura Logica (Version Word) guardado con exito.")
