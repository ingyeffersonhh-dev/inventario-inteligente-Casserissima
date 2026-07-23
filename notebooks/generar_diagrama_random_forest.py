import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Create folders if they don't exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, '..', 'docs', 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

# Academic Blue-and-Grey Palette
C_NAVY_DARK  = "#1e3a8a"  # Azul Marino Oscuro
C_BLUE_MED   = "#2b6cb0"  # Azul Académico Medio
C_SLATE_MED  = "#475569"  # Gris Pizarra
C_GREY_COOL  = "#94a3b8"  # Gris Frío
C_GREY_LIGHT = "#e2e8f0"  # Gris Muy Claro
C_CHARCOAL   = "#334155"  # Gris Carbón
C_TEXT       = "#0f172a"  # Color de texto

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')

# Font settings
font_title = {'fontsize': 16, 'fontweight': 'bold', 'color': C_TEXT, 'family': 'sans-serif'}
font_box = {'fontsize': 12, 'fontweight': 'bold', 'color': 'white', 'family': 'sans-serif'}
font_tree = {'fontsize': 12, 'fontweight': 'bold', 'color': C_CHARCOAL, 'family': 'sans-serif'}

# 1. Test Sample Input
ax.text(6, 9.2, "Test Sample Input", ha='center', va='center', fontdict=font_title)

# Tree positions
tree_x = [2, 6, 10]
tree_y_top = 7.5

# Arrows from Input to Trees
for x in tree_x:
    # Use ax.annotate for arrows
    ax.annotate("",
                xy=(x, tree_y_top + 0.3), xycoords='data',
                xytext=(6, 8.9), textcoords='data',
                arrowprops=dict(arrowstyle="->", color=C_SLATE_MED, lw=1.5))

# The "..." in the middle
ax.text(8, 7.5, "( . . . )", ha='center', va='center', fontsize=14, color=C_SLATE_MED, fontweight='bold')
ax.text(8, 4.5, "( . . . )", ha='center', va='center', fontsize=14, color=C_SLATE_MED, fontweight='bold')

# Arrow for "..."
ax.annotate("",
            xy=(8, 5.0), xycoords='data',
            xytext=(8, 7.0), textcoords='data',
            arrowprops=dict(arrowstyle="->", color=C_SLATE_MED, lw=1.5))

def draw_tree(ax, x_center, y_top, title, path):
    """
    path: list of indices (0: root, 1: left, 2: right, 3: ll, 4: lr, 5: rl, 6: rr)
    to highlight
    """
    ax.text(x_center - 0.8, y_top, title, ha='right', va='center', fontdict=font_tree)
    
    # Node coordinates
    nodes = {
        0: (x_center, y_top),
        1: (x_center - 0.5, y_top - 0.8),
        2: (x_center + 0.5, y_top - 0.8),
        3: (x_center - 0.8, y_top - 1.6),
        4: (x_center - 0.2, y_top - 1.6),
        5: (x_center + 0.2, y_top - 1.6),
        6: (x_center + 0.8, y_top - 1.6),
    }
    
    # Edges
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
    
    # Draw edges
    for u, v in edges:
        color = C_NAVY_DARK if (u in path and v in path) else C_GREY_COOL
        lw = 2.5 if (u in path and v in path) else 1.5
        zorder = 1 if (u in path and v in path) else 0
        ax.plot([nodes[u][0], nodes[v][0]], [nodes[u][1], nodes[v][1]], color=color, lw=lw, zorder=zorder)
    
    # Draw nodes
    for i, (nx, ny) in nodes.items():
        color = C_NAVY_DARK if i in path else C_GREY_COOL
        circle = patches.Circle((nx, ny), radius=0.15, facecolor=color, edgecolor='white', lw=1.5, zorder=2)
        ax.add_patch(circle)
        
    return nodes[path[-1]] # Return the leaf node coordinates

# Draw trees and get leaf positions
leaf1 = draw_tree(ax, 2, tree_y_top, "Tree 1", path=[0, 2, 6])
leaf2 = draw_tree(ax, 6, tree_y_top, "Tree 2", path=[0, 1, 4])
leaf3 = draw_tree(ax, 10, tree_y_top, "Tree 600", path=[0, 2, 5])

# Draw Prediction Boxes
pred_y = 4.5
pred_width = 2.4
pred_height = 0.6

for i, x in enumerate(tree_x):
    # Box
    rect = patches.Rectangle((x - pred_width/2, pred_y - pred_height/2), pred_width, pred_height, 
                             facecolor=C_GREY_LIGHT, edgecolor=C_SLATE_MED, lw=1.5)
    ax.add_patch(rect)
    # Text
    label = f"Prediction {i+1}" if i < 2 else "Prediction 600"
    ax.text(x, pred_y, label, ha='center', va='center', fontsize=11, fontweight='bold', color=C_TEXT)

# Arrows from leaves to predictions
ax.annotate("", xy=(tree_x[0], pred_y + pred_height/2), xycoords='data', xytext=(leaf1[0], leaf1[1] - 0.15), textcoords='data',
            arrowprops=dict(arrowstyle="-|>", color=C_NAVY_DARK, lw=2, mutation_scale=15))
ax.annotate("", xy=(tree_x[1], pred_y + pred_height/2), xycoords='data', xytext=(leaf2[0], leaf2[1] - 0.15), textcoords='data',
            arrowprops=dict(arrowstyle="-|>", color=C_NAVY_DARK, lw=2, mutation_scale=15))
ax.annotate("", xy=(tree_x[2], pred_y + pred_height/2), xycoords='data', xytext=(leaf3[0], leaf3[1] - 0.15), textcoords='data',
            arrowprops=dict(arrowstyle="-|>", color=C_NAVY_DARK, lw=2, mutation_scale=15))

# Average Box
avg_x = 6
avg_y = 2.5
avg_width = 4.5
avg_height = 0.8

rect_avg = patches.Rectangle((avg_x - avg_width/2, avg_y - avg_height/2), avg_width, avg_height, 
                             facecolor=C_GREY_LIGHT, edgecolor=C_SLATE_MED, lw=1.5)
ax.add_patch(rect_avg)
ax.text(avg_x, avg_y, "Average All Predictions", ha='center', va='center', fontsize=12, fontweight='bold', color=C_TEXT)

# Arrows from predictions to Average
for x in tree_x:
    ax.annotate("", xy=(avg_x, avg_y + avg_height/2), xycoords='data', xytext=(x, pred_y - pred_height/2), textcoords='data',
                arrowprops=dict(arrowstyle="->", color=C_SLATE_MED, lw=1.5))

# Final Prediction Box
final_y = 1.0
final_width = 3.5
final_height = 0.8

rect_final = patches.Rectangle((avg_x - final_width/2, final_y - final_height/2), final_width, final_height, 
                               facecolor=C_GREY_LIGHT, edgecolor=C_SLATE_MED, lw=1.5)
ax.add_patch(rect_final)
ax.text(avg_x, final_y + 0.15, "Random Forest", ha='center', va='center', fontsize=12, fontweight='bold', color=C_TEXT)
ax.text(avg_x, final_y - 0.2, "Prediction", ha='center', va='center', fontsize=12, fontweight='bold', color=C_TEXT)

# Arrow from Average to Final
ax.annotate("", xy=(avg_x, final_y + final_height/2), xycoords='data', xytext=(avg_x, avg_y - avg_height/2), textcoords='data',
            arrowprops=dict(arrowstyle="-|>", color=C_NAVY_DARK, lw=2, mutation_scale=15))

plt.tight_layout()
output_path = os.path.join(IMAGES_DIR, 'arquitectura_random_forest.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Diagram saved to {output_path}")
