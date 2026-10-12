# Generates the Two Database Instances diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Read left to right: requests, the server, two database instances.
#
# The server finds the instance of each workspace in common_db, then uses the
# pool for that instance. Database 1 holds common_db and the databases of
# tenants 1 and 2; Database 2 holds the databases of tenants 3 and 4.
import io, os

from rough import *

W, H = 1080, 490

REQ = (40, 220, 130, 50)                 # x, y, w, h
SRV = (250, 30, 360, 430)
X_POOL, W_POOL, H_POOL = 400, 170, 70
PG_CX, PG_RX, PG_RY = 880, 110, 18

# Each instance: its name, its databases, its cylinder top and bottom, the arrow label.
INSTANCES = (
    ("Database 1", ("common_db", "tenant_1_db", "tenant_2_db"), 60, 230, "tenants 1, 2"),
    ("Database 2", ("tenant_3_db", "tenant_4_db"), 280, 450, "tenants 3, 4"),
)

def diagram():
    p = [frame(W, H)]
    rx, ry, rw, rh = REQ
    p.append(rect(rx, ry, rw, rh) + text(rx + rw / 2, ry + rh / 2 + 6, "Requests", 16, "middle"))
    sx, sy, sw_, sh = SRV
    p.append(rect(sx, sy, sw_, sh) + text(sx + 20, sy + 32, "Server", 18))
    p.append(text(sx + 20, sy + 58, "finds the instance in common_db", 14))
    for n, (name, dbs, top, bot, lab) in enumerate(INSTANCES, 1):
        cy = (top + bot) / 2
        p.append(rect(X_POOL, cy - H_POOL / 2, W_POOL, H_POOL, sw=1.8, op=0.5, dash="1 8")
                 + text(X_POOL + W_POOL / 2, cy + 6, f"Pool {n}", 16, "middle"))
        p.append(arrow(rx + rw + 4, ry + rh / 2, X_POOL - 8, cy))
        p.append(cylinder(PG_CX, top, bot, PG_RX, PG_RY))
        p.append(text(PG_CX, top + PG_RY + 28, name, 18, "middle"))
        for i, db in enumerate(dbs):
            p.append(text(PG_CX, top + PG_RY + 58 + 24 * i, db, 15, "middle"))
        x0, x1 = X_POOL + W_POOL + 4, PG_CX - PG_RX - 8
        p.append(arrow(x0, cy, x1, cy))
        p.append(label(x0, cy, x1, cy, lab))
    return "".join(p)

ALT = ("Requests reach the Server. The Server finds the instance of each workspace in "
       "common_db, and keeps one connection pool for each database instance. Pool 1 connects "
       "to Database 1, which holds common_db, tenant_1_db and tenant_2_db. Pool 2 connects to "
       "Database 2, which holds tenant_3_db and tenant_4_db.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  two-instances — the server and two database instances.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/two-instances.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-two-instances">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-two-instances{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-two-instances svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "two-instances.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
