# Generates the Dedicated Database Instance diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Read left to right: requests, the load balancer, three servers, three database
# instances. Databases 1 and 2 are the shared instances from the sharding
# diagram. Database 3 is new and dedicated: it holds only tenant_1_db, the
# database of the heavy tenant, which moved there from Database 1. Every server
# connects to all three instances.
import io, os

from rough import *

W, H = 1080, 640

REQ = (40, 290, 130, 50)                 # x, y, w, h
LB = (220, 275, 150, 80)
X_SRV, W_SRV, H_SRV = 450, 150, 90
ROWS = (155, 315, 475)                   # the centre of each server
PG_CX, PG_RX, PG_RY = 880, 120, 18

# Each instance: its name, its tag, its databases, its cylinder top and bottom.
INSTANCES = (
    ("Database 1", "shared", ("common_db", "tenant_2_db"), 30, 195),
    ("Database 2", "shared", ("tenant_3_db", "tenant_4_db"), 240, 405),
    ("Database 3", "dedicated to tenant 1", ("tenant_1_db",), 450, 600),
)

def diagram():
    p = [frame(W, H)]
    rx, ry, rw, rh = REQ
    p.append(rect(rx, ry, rw, rh) + text(rx + rw / 2, ry + rh / 2 + 6, "Requests", 16, "middle"))
    lx, ly, lw, lh = LB
    p.append(rect(lx, ly, lw, lh) + text(lx + lw / 2, ly + 34, "Load", 16, "middle")
             + text(lx + lw / 2, ly + 58, "balancer", 16, "middle"))
    p.append(arrow(rx + rw + 4, ry + rh / 2, lx - 8, ly + lh / 2))
    for name, tag, dbs, top, bot in INSTANCES:
        p.append(cylinder(PG_CX, top, bot, PG_RX, PG_RY))
        p.append(text(PG_CX, top + PG_RY + 30, name, 18, "middle"))
        p.append(text(PG_CX, top + PG_RY + 54, tag, 14, "middle"))
        for i, db in enumerate(dbs):
            p.append(text(PG_CX, top + PG_RY + 90 + 24 * i, db, 15, "middle"))
    for n, cy in enumerate(ROWS, 1):
        p.append(rect(X_SRV, cy - H_SRV / 2, W_SRV, H_SRV)
                 + text(X_SRV + W_SRV / 2, cy + 6, f"Server {n}", 16, "middle"))
        p.append(arrow(lx + lw + 4, ly + lh / 2, X_SRV - 8, cy))
        for *_, top, bot in INSTANCES:
            p.append(arrow(X_SRV + W_SRV + 4, cy, PG_CX - PG_RX - 8, (top + bot) / 2, sw=1.2))
    return "".join(p)

ALT = ("Requests reach a Load balancer, which sends each request to one of three servers. "
       "Every server connects to three database instances. Database 1 is shared: it holds "
       "common_db and tenant_2_db. Database 2 is shared: it holds tenant_3_db and "
       "tenant_4_db. Database 3 is new and dedicated to tenant 1: it holds only tenant_1_db.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  dedicated-instance — the heavy tenant moves to its own database instance.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/dedicated-instance.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-dedicated-instance">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-dedicated-instance{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-dedicated-instance svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "dedicated-instance.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
