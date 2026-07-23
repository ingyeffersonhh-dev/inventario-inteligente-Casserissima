import json
import os

def create_rect(id, x, y, w, h, fill, stroke, text_id):
    return {
        "type": "rectangle",
        "id": id,
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke,
        "backgroundColor": fill,
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id+text_id) % 100000,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": [{"id": text_id, "type": "text"}],
        "link": None,
        "locked": False,
        "roundness": {"type": 3}
    }

def create_text(id, text, x, y, w, h, container_id, color, size):
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
        "angle": 0,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id+text) % 100000,
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
        "versionNonce": hash(id+"arrow") % 100000,
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

def create_free_text(id, text, x, y, color, size):
    return {
        "type": "text",
        "id": id,
        "x": x, "y": y,
        "width": len(text)*size*0.6, "height": size*1.25,
        "text": text,
        "originalText": text,
        "fontSize": size,
        "fontFamily": 3,
        "textAlign": "left",
        "verticalAlign": "top",
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": hash(id) % 100000,
        "version": 1,
        "versionNonce": hash(id+"freetext") % 100000,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
        "containerId": None,
        "lineHeight": 1.25
    }

elements = []

# Constants
W = 260
H = 120
GAP_X = 100
START_X = 100
MAIN_Y = 200
ERR_Y = 380

# Colors (Academic Blue-and-Grey Palette)
C_PRIM_F = "#eff6ff"  # Ice Blue
C_PRIM_S = "#1e3a8a"  # Navy Blue
C_START_F = "#eff6ff" # Soft Ice Blue
C_START_S = "#1e3a8a" # Navy Blue
C_END_F = "#ecfdf5"   # Mint Tint
C_END_S = "#047857"   # Deep Green
C_WARN_F = "#fffbeb"  # Amber Tint
C_WARN_S = "#b45309"  # Amber Stroke
C_ERR_F = "#fef2f2"   # Red Tint
C_ERR_S = "#991b1b"   # Dark Red
C_TITLE = "#1e3a8a"   # Navy Title

TEXT_LIGHT = "#1e293b" # Dark Slate
TEXT_DARK = "#1e293b"  # Dark Slate (since primary fills are now light)

# Title
elements.append(create_free_text("title", "Diagrama de Flujo del Inventario Actual (AS-IS) - Pastelería Casserissima", START_X, MAIN_Y - 120, C_TITLE, 36))

steps = [
    ("recepcion", "Recepción\nde Insumos", "Sin control\ncuantitativo", C_START_F, C_START_S, TEXT_LIGHT),
    ("almacen", "Almacenamiento\nEmpírico", "Sin política\nFIFO", C_PRIM_F, C_PRIM_S, TEXT_DARK),
    ("despacho", "Despacho a\nProducción", "Despacho\nintuitivo", C_PRIM_F, C_PRIM_S, TEXT_DARK),
    ("produccion", "Producción\nDiaria", "Sobreproducción\ndefensiva", C_PRIM_F, C_PRIM_S, TEXT_DARK)
]

prev_id = None
curr_x = START_X

for i, (sid, name, err, fill, stroke, tcolor) in enumerate(steps):
    rect_id = f"rect_{sid}"
    text_id = f"txt_{sid}"
    err_rect_id = f"erect_{sid}"
    err_txt_id = f"etxt_{sid}"
    arr_id = f"arr_{sid}"
    err_arr_id = f"earr_{sid}"
    
    # Main Box
    elements.append(create_rect(rect_id, curr_x, MAIN_Y, W, H, fill, stroke, text_id))
    elements.append(create_text(text_id, name, curr_x+10, MAIN_Y+10, W-20, H-20, rect_id, tcolor, 28))
    
    # Error Box
    elements.append(create_rect(err_rect_id, curr_x, ERR_Y, W, 90, C_ERR_F, C_ERR_S, err_txt_id))
    elements.append(create_text(err_txt_id, err, curr_x+10, ERR_Y+10, W-20, 70, err_rect_id, TEXT_LIGHT, 20))
    
    # Error Arrow
    elements.append(create_arrow(err_arr_id, curr_x + W/2, MAIN_Y + H, 0, ERR_Y - (MAIN_Y + H), rect_id, err_rect_id, C_ERR_S, "dashed"))
    
    # Connection Arrow
    if prev_id:
        elements.append(create_arrow(arr_id, curr_x - GAP_X, MAIN_Y + H/2, GAP_X, 0, prev_id, rect_id, C_PRIM_S))
    
    prev_id = rect_id
    curr_x += W + GAP_X

# Branch to Venta / Merma
venta_x = curr_x
venta_y = MAIN_Y - 80
merma_y = MAIN_Y + 120

# Venta Box
v_rect = "rect_venta"
v_txt = "txt_venta"
elements.append(create_rect(v_rect, venta_x, venta_y, W, 100, C_END_F, C_END_S, v_txt))
elements.append(create_text(v_txt, "Venta", venta_x+10, venta_y+10, W-20, 80, v_rect, TEXT_LIGHT, 28))

# Arrow to Venta
elements.append(create_arrow("arr_venta", curr_x - GAP_X, MAIN_Y + H/2, GAP_X, venta_y + 50 - (MAIN_Y + H/2), prev_id, v_rect, C_PRIM_S))

# Merma Box
m_rect = "rect_merma"
m_txt = "txt_merma"
elements.append(create_rect(m_rect, venta_x, merma_y, W, 100, C_WARN_F, C_WARN_S, m_txt))
elements.append(create_text(m_txt, "Merma\n(Pérdidas)", venta_x+10, merma_y+10, W-20, 80, m_rect, TEXT_LIGHT, 28))

# Arrow to Merma
elements.append(create_arrow("arr_merma", curr_x - GAP_X, MAIN_Y + H/2, GAP_X, merma_y + 50 - (MAIN_Y + H/2), prev_id, m_rect, C_PRIM_S))

# Merma Error
me_rect = "erect_merma"
me_txt = "etxt_merma"
me_err_y = merma_y + 160
elements.append(create_rect(me_rect, venta_x, me_err_y, W, 90, C_ERR_F, C_ERR_S, me_txt))
elements.append(create_text(me_txt, "Registro irregular\nde pérdidas", venta_x+10, me_err_y+10, W-20, 70, me_rect, TEXT_LIGHT, 20))

# Arrow to Merma Error
elements.append(create_arrow("earr_merma", venta_x + W/2, merma_y + 100, 0, 60, m_rect, me_rect, C_ERR_S, "dashed"))

# Wrapper
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

os.makedirs("../docs/images", exist_ok=True)
with open("../docs/images/diagrama_flujo_inventario.excalidraw", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("Excalidraw diagram generated.")
