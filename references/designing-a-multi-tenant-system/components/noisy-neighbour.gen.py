# Generates the Noisy Neighbour diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Read left to right: six tenants, the load balancer, three servers, two
# database instances. Tenants A and B have high usage: thick boxes and thick
# arrows. Tenants C to F have low usage: thin boxes and dotted arrows.
#
# Each server shows a row of CPU slots, and each database instance a row of
# connection slots. The letters say which tenant holds each slot. A and B hold
# almost all of them, so D and F wait.
import io, os

from rough import *

W, H = 1080, 500

X_TEN, W_TEN = 30, 120
HIGH = (("A", 95), ("B", 160))           # each high-usage tenant and its centre
LOW = (("C", 255), ("D", 305), ("E", 355), ("F", 405))
LB = (205, 205, 110, 80)                 # x, y, w, h
X_SRV, W_SRV, H_SRV = 380, 250, 90
SERVERS = ((110, "AABABC"), (245, "BABBAA"), (380, "ABADBA"))
CELL_W, CELL_H = 34, 32
PG_CX, PG_RX, PG_RY = 870, 170, 18
INSTANCES = (("Database 1", 50, "AAAAC", "holds A, C, D", "D waits"),
             ("Database 2", 280, "BBBBE", "holds B, E, F", "F waits"))
PG_HEIGHT = 180

def slots(x, y, letters):
    return "".join(rect(x + i * CELL_W, y, CELL_W, CELL_H, sw=1.4)
                   + text(x + i * CELL_W + CELL_W / 2, y + 22, c, 15, "middle")
                   for i, c in enumerate(letters))

def diagram():
    p = [frame(W, H)]
    lx, ly, lw, lh = LB
    lcy = ly + lh / 2
    p.append(text(X_TEN, HIGH[0][1] - 38, "high usage", 14))
    for t, cy in HIGH:
        p.append(rect(X_TEN, cy - 25, W_TEN, 50, sw=3.2)
                 + text(X_TEN + W_TEN / 2, cy + 6, f"Tenant {t}", 16, "middle"))
        p.append(arrow(X_TEN + W_TEN + 4, cy, lx - 8, lcy - 12, sw=3.2))
    p.append(text(X_TEN, LOW[0][1] - 30, "low usage", 14))
    for t, cy in LOW:
        p.append(rect(X_TEN, cy - 18, W_TEN, 36, sw=1.4)
                 + text(X_TEN + W_TEN / 2, cy + 5, f"Tenant {t}", 15, "middle"))
        p.append(arrow(X_TEN + W_TEN + 4, cy, lx - 8, lcy + 12, sw=1.5, dash="1 6"))
    p.append(rect(lx, ly, lw, lh) + text(lx + lw / 2, ly + 34, "Load", 16, "middle")
             + text(lx + lw / 2, ly + 58, "balancer", 16, "middle"))
    for n, (cy, letters) in enumerate(SERVERS, 1):
        y = cy - H_SRV / 2
        p.append(rect(X_SRV, y, W_SRV, H_SRV) + text(X_SRV + 16, y + 24, f"Server {n}", 16))
        p.append(text(X_SRV + W_SRV - 16, y + 24, "CPU", 13, "end"))
        p.append(slots(X_SRV + (W_SRV - 6 * CELL_W) / 2, y + 40, letters))
        p.append(arrow(lx + lw + 4, lcy, X_SRV - 8, cy))
        for name, top, *_ in INSTANCES:
            ty = top + PG_HEIGHT / 2
            p.append(arrow(X_SRV + W_SRV + 4, cy, PG_CX - PG_RX - 8, ty, sw=1.2))
    for name, top, letters, holds, waits in INSTANCES:
        bot = top + PG_HEIGHT
        p.append(cylinder(PG_CX, top, bot, PG_RX, PG_RY))
        p.append(text(PG_CX, top + PG_RY + 26, name, 18, "middle"))
        p.append(text(PG_CX + 5 * CELL_W / 2 - 33, top + PG_RY + 64, "connections", 13))
        p.append(slots(PG_CX - 5 * CELL_W / 2 - 45, top + PG_RY + 42, letters))
        p.append(text(PG_CX, top + PG_RY + 104, holds, 15, "middle"))
        p.append(text(PG_CX, top + PG_RY + 130, waits, 15, "middle"))
    return "".join(p)

ALT = ("Six tenants send requests through a Load balancer to three servers, and every "
       "server connects to two database instances. Tenants A and B have high usage, drawn "
       "with thick boxes and arrows; Tenants C, D, E and F have low usage, drawn with thin "
       "boxes and dotted arrows. Each server has six CPU slots, almost all held by A and B. "
       "Database 1 holds A, C and D: A holds four of its five connections and D waits. "
       "Database 2 holds B, E and F: B holds four of its five connections and F waits.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  noisy-neighbour — two big tenants fill the slots, the small ones wait.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/noisy-neighbour.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-noisy-neighbour">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-noisy-neighbour{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-noisy-neighbour svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "noisy-neighbour.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
