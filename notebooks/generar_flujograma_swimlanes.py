import json
import os

def create_rect(id, x, y, w, h, fill, stroke, text_id=None, stroke_style="solid", roundness=3):
    bound_elements = [{"id": text_id, "type": "text"}] if text_id else []
    return {
        "type": "rectangle",
        "id": id,
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke,
        "backgroundColor": fill,
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": stroke_style,
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id + (text_id or "")) % 100000,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": bound_elements,
        "link": None,
        "locked": False,
        "roundness": {"type": roundness} if roundness else None
    }

def create_text(id, text, x, y, w, h, container_id, color, size, angle=0):
    return {
        "type": "text",
        "id": id,
        "x": x, "y": y,
        "width": w, "height": h,
        "text": text,
        "originalText": text,
        "fontSize": size,
        "fontFamily": 3,
        "textAlign": "center",
        "verticalAlign": "middle",
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": angle,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id + text) % 100000,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
        "containerId": container_id,
        "lineHeight": 1.25
    }

def create_arrow(id, x, y, dx, dy, start_id, end_id, color, style="solid"):
    return {
        "type": "arrow",
        "id": id,
        "x": x, "y": y, "width": abs(dx), "height": abs(dy),
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": style,
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id + "arrow") % 100000,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
        "points": [[0, 0], [dx, dy]],
        "startBinding": {"elementId": start_id, "focus": 0, "gap": 2} if start_id else None,
        "endBinding": {"elementId": end_id, "focus": 0, "gap": 2} if end_id else None,
        "startArrowhead": None,
        "endArrowhead": "arrow"
    }

def create_line(id, x, y, dx, dy, color, style="dashed"):
    return {
        "type": "line",
        "id": id,
        "x": x, "y": y, "width": abs(dx), "height": abs(dy),
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": style,
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id + "line") % 100000,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
        "points": [[0, 0], [dx, dy]]
    }

def create_free_text(id, text, x, y, color, size, angle=0, w=None, h=None):
    width = w if w is not None else len(text) * size * 0.6
    height = h if h is not None else size * 1.25
    return {
        "type": "text",
        "id": id,
        "x": x, "y": y,
        "width": width, "height": height,
        "text": text,
        "originalText": text,
        "fontSize": size,
        "fontFamily": 3,
        "textAlign": "center" if angle != 0 else "left",
        "verticalAlign": "middle" if angle != 0 else "top",
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": angle,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id + "freetext") % 100000,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
        "containerId": None,
        "lineHeight": 1.25
    }

# Build the elements
elements = []

# Title
elements.append(
    create_free_text(
        "main_title",
        "Flujograma de Gestión de Inventario Actual (AS-IS) con Carriles y Puntos Críticos",
        150, 45, "#1e3a8a", 24
    )
)

# Geometry
LANE_X = 50
LANE_W = 1150
HEADER_W = 70
CONTENT_W = LANE_W - HEADER_W
CONTENT_X = LANE_X + HEADER_W

Y_LANE1 = 110
H_LANE1 = 200

Y_LANE2 = 310
H_LANE2 = 200

Y_LANE3 = 510
H_LANE3 = 250

# Colors (Academic Blue-and-Grey Palette)
C_HEADER_BG = "#f1f5f9"      # Light grey for headers
C_LANE1_BG = "#ffffff"       # White background for lane 1
C_LANE2_BG = "#f8fafc"       # Very light grey for lane 2 (alternating)
C_LANE3_BG = "#ffffff"       # White background for lane 3
C_STROKE_LANE = "#cbd5e1"    # Border for lanes

C_BOX_BG = "#eff6ff"         # Ice blue for normal steps
C_BOX_STROKE = "#1e3a8a"     # Navy blue for normal steps
C_TEXT_COLOR = "#1e293b"     # Dark Slate for text

C_BRECHA_BG = "#fef2f2"      # Soft red tint for Brechas
C_BRECHA_STROKE = "#991b1b"  # Dark red for Brechas
C_BRECHA_TEXT = "#991b1b"    # Red text

# Draw Lane Backgrounds & Headers
# Lane 1 (PROVEEDORES)
elements.append(create_rect("lane1_hdr", LANE_X, Y_LANE1, HEADER_W, H_LANE1, C_HEADER_BG, C_STROKE_LANE, roundness=0))
elements.append(create_rect("lane1_content", CONTENT_X, Y_LANE1, CONTENT_W, H_LANE1, C_LANE1_BG, C_STROKE_LANE, roundness=0))
# Text rotated 270 degrees (reads bottom to top)
# Center of header block: cx = 50 + 35 = 85, cy = 110 + 100 = 210
# For rotated text, width is the "height" of the text on screen, height is the "width" of the text.
elements.append(create_free_text("lane1_lbl", "PROVEEDORES", 85 - 15, 210 - 75, "#475569", 16, angle=-1.5707963267948966, w=150, h=30))

# Lane 2 (ENCARGADA DE ALMACÉN)
elements.append(create_rect("lane2_hdr", LANE_X, Y_LANE2, HEADER_W, H_LANE2, C_HEADER_BG, C_STROKE_LANE, roundness=0))
elements.append(create_rect("lane2_content", CONTENT_X, Y_LANE2, CONTENT_W, H_LANE2, C_LANE2_BG, C_STROKE_LANE, roundness=0))
# Center: cx = 85, cy = 310 + 100 = 410
elements.append(create_free_text("lane2_lbl", "ENCARGADA DE ALMACÉN", 85 - 15, 410 - 90, "#475569", 16, angle=-1.5707963267948966, w=180, h=30))

# Lane 3 (PRODUCCIÓN Y VENTAS)
elements.append(create_rect("lane3_hdr", LANE_X, Y_LANE3, HEADER_W, H_LANE3, C_HEADER_BG, C_STROKE_LANE, roundness=0))
elements.append(create_rect("lane3_content", CONTENT_X, Y_LANE3, CONTENT_W, H_LANE3, C_LANE3_BG, C_STROKE_LANE, roundness=0))
# Center: cx = 85, cy = 510 + 125 = 635
elements.append(create_free_text("lane3_lbl", "PRODUCCIÓN Y VENTAS", 85 - 15, 635 - 90, "#475569", 16, angle=-1.5707963267948966, w=180, h=30))

# Step Boxes
step_boxes = [
    # (id, name, lane_num, cx, cy)
    ("envio", "Envío de Insumos\n(Materias primas)", 1, 300, 210),
    ("recepcion", "1. Recepción de Insumos\n(Ingreso físico)", 2, 300, 410),
    ("almacen", "2. Almacenamiento\nEmpírico", 2, 590, 410),
    ("despacho", "3. Despacho a Producción\n(Visual e informal)", 3, 590, 610),
    ("produccion", "4. Planificación y\nProducción Diaria", 3, 880, 610),
    ("ventas", "5. Ventas y Disposición\nde Insumos Caducados", 1, 880, 210)
]

BOX_W = 240
BOX_H = 75

for bid, name, lane, cx, cy in step_boxes:
    rx = cx - BOX_W / 2
    ry = cy - BOX_H / 2
    elements.append(create_rect(f"box_{bid}", rx, ry, BOX_W, BOX_H, C_BOX_BG, C_BOX_STROKE, f"txt_{bid}", roundness=3))
    elements.append(create_text(f"txt_{bid}", name, rx + 10, ry + 10, BOX_W - 20, BOX_H - 20, f"box_{bid}", C_TEXT_COLOR, 15))

# Brecha Boxes (Critiques)
brechas = [
    # (id, text, target_box_id, cx, cy, line_start, line_end)
    ("b1", "Brecha 1: Sin verificación cuantitativa\nni registro de vencimientos.", "box_recepcion", 300, 500, (300, 410 + BOX_H/2), (300, 500 - 25)),
    ("b2", "Brecha 2: Sin políticas FIFO ni\nsegmentación por vida útil.", "box_almacen", 590, 310, (590, 410 - BOX_H/2), (590, 310 + 25)),
    ("b3", "Brecha 3: Extracción sin registro\nni control de pesaje/cantidades.", "box_despacho", 590, 715, (590, 610 + BOX_H/2), (590, 715 - 25)),
    ("b4", "Brecha 4: Sobreproducción defensiva\npara evitar quiebres de stock.", "box_produccion", 880, 715, (880, 610 + BOX_H/2), (880, 715 - 25)),
    ("b5", "Brecha 5: Mermas elevadas (~12%)\ny descarte sin registro regular.", "box_ventas", 880, 105, (880, 210 - BOX_H/2), (880, 105 + 25))
]

BRECHA_W = 320
BRECHA_H = 50

for bid, text, target, cx, cy, start_pt, end_pt in brechas:
    rx = cx - BRECHA_W / 2
    ry = cy - BRECHA_H / 2
    elements.append(create_rect(f"box_{bid}", rx, ry, BRECHA_W, BRECHA_H, C_BRECHA_BG, C_BRECHA_STROKE, f"txt_{bid}", stroke_style="solid", roundness=3))
    elements.append(create_text(f"txt_{bid}", text, rx + 10, ry + 5, BRECHA_W - 20, BRECHA_H - 10, f"box_{bid}", C_BRECHA_TEXT, 13))
    # Red connector line
    elements.append(create_line(f"line_{bid}", start_pt[0], start_pt[1], end_pt[0] - start_pt[0], end_pt[1] - start_pt[1], C_BRECHA_STROKE, style="dashed"))

# Arrows connecting steps
arrows = [
    # (id, start_box, end_box, sx, sy, dx, dy)
    ("envio_recep", "box_envio", "box_recepcion", 300, 210 + BOX_H/2, 0, (410 - BOX_H/2) - (210 + BOX_H/2)),
    ("recep_alma", "box_recepcion", "box_almacen", 300 + BOX_W/2, 410, (590 - BOX_W/2) - (300 + BOX_W/2), 0),
    ("alma_desp", "box_almacen", "box_despacho", 590, 410 + BOX_H/2, 0, (610 - BOX_H/2) - (410 + BOX_H/2)),
    ("desp_prod", "box_despacho", "box_produccion", 590 + BOX_W/2, 610, (880 - BOX_W/2) - (590 + BOX_W/2), 0),
    ("prod_vent", "box_produccion", "box_ventas", 880, 610 - BOX_H/2, 0, (210 + BOX_H/2) - (610 - BOX_H/2))
]

for aid, start_b, end_b, sx, sy, dx, dy in arrows:
    elements.append(create_arrow(f"arr_{aid}", sx, sy, dx, dy, start_b, end_b, C_BOX_STROKE))

# Final output dictionary
output = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elements,
    "appState": {
        "viewBackgroundColor": "#ffffff",
        "gridSize": 20
    },
    "files": {}
}

# Write file
os.makedirs("docs/images", exist_ok=True)
with open("docs/images/diagrama_flujo_inventario.excalidraw", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("diagrama_flujo_inventario.excalidraw generated successfully!")
