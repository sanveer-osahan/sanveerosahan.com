# Generates the Core Entities diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with. The drawing joins the earlier drawings: two users, the
# product they call, two workspaces, and the store that holds the three core
# entities.
#
# The five steps, in order:
#   1. signs up          User 1 -> Product
#   2. creates workspace Product -> Workspace 1
#   3. signs up          User 2 -> Product
#   4. joins workspace   Product -> Workspace 1
#   5. creates workspace Product -> Workspace 2
# Two dotted arrows run from the workspaces into the store on the right. They
# carry no step number, because they are what the store keeps, not what a user
# does. Below the drawing, in a dotted box of its own, three small tables show the
# rows this very example puts in the store.
import io, math, os

from rough import *

W, H = 1080, 680   # one box holds the whole drawing

BOX_H = 76

# Four columns, left to right: the users, the product they call, the workspaces
# the product routes them to, and the store that holds the three core entities.
X_USER, W_USER = 40, 160
PROD_CX, PROD_CY, PROD_RX, PROD_RY = 360, 210, 72, 56
X_WS, W_WS = 640, 210
DB_CX, DB_TOP, DB_BOT, DB_RX, DB_RY = 975, 150, 280, 80, 18

ROW1, ROW2 = 140, 280

ENTITIES = ("Users", "Workspaces", "Memberships")

# The rows the store holds for this very example, below the drawing that makes
# them. Each table is (title, x, width, divider, rows).
SAMPLE_Y = 494
ROW_H = 44
SAMPLES = (
    ("Users", 80, 300, 90, (("U1", "User 1"), ("U2", "User 2"))),
    ("Workspaces", 430, 330, 90, (("W1", "Workspace 1"), ("W2", "Workspace 2"))),
    ("Memberships", 810, 220, 110, (("U1", "W1"), ("U2", "W1"), ("U2", "W2"))),
)

def box(x, mid, w, s, size=18):
    return rect(x, mid - BOX_H / 2, w, BOX_H) + text(x + w / 2, mid + 6, s, size, "middle")

def on_prod(tx, ty, pad=7):
    """The point on the product ellipse that faces the given point."""
    dx, dy = tx - PROD_CX, ty - PROD_CY
    t = 1.0 / math.hypot(dx / PROD_RX, dy / PROD_RY)
    n = math.hypot(dx, dy)
    return (PROD_CX + dx * t + dx / n * pad, PROD_CY + dy * t + dy / n * pad)

def table(title, x, w, div, rows):
    """One sample table: a title, a box, a row line per row and one column line."""
    h = ROW_H * len(rows)
    p = [text(x, SAMPLE_Y - 16, title, 17), rect(x, SAMPLE_Y, w, h)]
    for i in range(1, len(rows)):
        p.append(path(dline(x, SAMPLE_Y + ROW_H * i, x + w, SAMPLE_Y + ROW_H * i), 1.4))
    p.append(path(dline(x + div, SAMPLE_Y, x + div, SAMPLE_Y + h), 1.4))
    for i, (a, b) in enumerate(rows):
        cy = SAMPLE_Y + ROW_H * i + ROW_H / 2 + 6
        p.append(text(x + div / 2, cy, a, 15, "middle"))
        p.append(text(x + div + (w - div) / 2, cy, b, 15, "middle"))
    return "".join(p)

def step(x0, y0, x1, y1, s, off=16, size=14):
    """One numbered step: a solid arrow and the label that rides beside it."""
    return arrow(x0, y0, x1, y1) + label(x0, y0, x1, y1, s, size=size, off=off)

def diagram():
    p = [frame(W, H)]
    p.append(box(X_USER, ROW1, W_USER, "User 1"))
    p.append(box(X_USER, ROW2, W_USER, "User 2"))
    p.append(ellipse(PROD_CX, PROD_CY, PROD_RX, PROD_RY))
    p.append(text(PROD_CX, PROD_CY + 6, "Product", 18, "middle"))
    p.append(box(X_WS, ROW1, W_WS, "Workspace 1"))
    p.append(box(X_WS, ROW2, W_WS, "Workspace 2"))
    p.append(cylinder(DB_CX, DB_TOP, DB_BOT, DB_RX, DB_RY))
    for i, s in enumerate(ENTITIES):
        p.append(text(DB_CX, 190 + i * 28, s, 15, "middle"))
    xu, xw = X_USER + W_USER + 2, X_WS - 8
    # Both users sign up on the product.
    # The lower label sits under its shaft, clear of the User 2 box.
    for y, s, off in ((ROW1, "1. signs up", 16), (ROW2, "3. signs up", -16)):
        ex, ey = on_prod(xu, y)
        p.append(step(xu, y, ex, ey, s, off=off))
    # The product makes the first workspace, lets User 2 in, and makes a second.
    # Steps 4 and 5 run side by side. Each label holds a different stretch of
    # its own shaft, so the two never meet and neither one reaches an arrow head.
    for ty, s, off, t0, t1 in ((ROW1 - 28, "2. creates workspace", 16, 0.0, 1.0),
                               (ROW1 + 30, "4. joins workspace", -15, 0.3, 0.85),
                               (ROW2, "5. creates workspace", 15, 0.1, 0.7)):
        sx, sy = on_prod(xw, ty)
        p.append(arrow(sx, sy, xw, ty))
        p.append(label(sx + (xw - sx) * t0, sy + (ty - sy) * t0,
                       sx + (xw - sx) * t1, sy + (ty - sy) * t1, s, size=14, off=off))
    # What the store holds for each workspace.
    p.append(arrow(X_WS + W_WS + 2, ROW1 + 10, DB_CX - DB_RX - 4, 185, dash="1 7"))
    p.append(arrow(X_WS + W_WS + 2, ROW2 - 10, DB_CX - DB_RX - 4, 245, dash="1 7"))
    # The rows the store holds, in a dotted box of their own.
    p.append(arrow(DB_CX, DB_BOT + DB_RY + 4, DB_CX, 436, dash="1 7"))
    p.append(rect(40, 440, 1000, 200, sw=1.8, op=0.5, dash="1 8"))
    for t in SAMPLES:
        p.append(table(*t))
    return "".join(p)

ALT = ("Core Entities. User 1 and User 2 sign up on the Product. The Product creates "
       "Workspace 1, lets User 2 join it, and creates Workspace 2. A dotted arrow runs from "
       "each workspace into a database drum on the right that holds the three core entities: "
       "Users, Workspaces and Memberships. Below, three tables show the rows of this example: "
       "Users holds User 1 and User 2, Workspaces holds Workspace 1 and Workspace 2, and "
       "Memberships holds User 1 in Workspace 1, User 2 in Workspace 1, and User 2 in "
       "Workspace 2.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  core-entities — the two users, the two workspaces and the store that holds them.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/core-entities.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-core-entities">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-core-entities{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-core-entities svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "core-entities.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
