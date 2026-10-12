# Generates the Dedicated Server Instance diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Read left to right: requests, the load balancer, two groups of servers, three
# database instances. The load balancer reads the workspace from each request.
# It sends tenant 1's requests to tenant 1's servers, and all the other
# requests to the shared servers. The shared servers connect to the shared
# Databases 1 and 2. Tenant 1's servers connect to Database 3, and to
# common_db on Database 1 (dotted).
import io, os

from rough import *

W, H = 1080, 700

REQ = (40, 330, 130, 50)                 # x, y, w, h
LB = (220, 310, 150, 90)
X_GRP, W_GRP = 450, 190
X_SRV, W_SRV, H_SRV = 470, 150, 70

# Each group: its label, its top and bottom, the server names and centres, the arrow label.
GROUPS = (
    ("shared", 30, 400, (("Server 1", 125), ("Server 2", 225), ("Server 3", 325)), "tenants 2, 3, 4"),
    ("tenant 1", 450, 670, (("Server 4", 545), ("Server 5", 625)), "tenant 1"),
)
PG_CX, PG_RX, PG_RY = 900, 120, 18
INSTANCES = (
    ("Database 1", "shared", ("common_db", "tenant_2_db"), 30, 195),
    ("Database 2", "shared", ("tenant_3_db", "tenant_4_db"), 240, 405),
    ("Database 3", "dedicated to tenant 1", ("tenant_1_db",), 490, 640),
)
LINKS = ((0, 0, None), (0, 1, None), (1, 2, None), (1, 0, "1 6"))  # group, instance, dash

def mid(top, bot):
    return (top + bot) / 2

def diagram():
    p = [frame(W, H)]
    rx, ry, rw, rh = REQ
    p.append(rect(rx, ry, rw, rh) + text(rx + rw / 2, ry + rh / 2 + 6, "Requests", 16, "middle"))
    lx, ly, lw, lh = LB
    p.append(rect(lx, ly, lw, lh) + text(lx + lw / 2, ly + 40, "Load", 16, "middle")
             + text(lx + lw / 2, ly + 64, "balancer", 16, "middle"))
    p.append(text(lx + lw / 2, ly + lh + 26, "routes by workspace", 14, "middle"))
    p.append(arrow(rx + rw + 4, ry + rh / 2, lx - 8, ly + lh / 2))
    for name, top, bot, servers, lab in GROUPS:
        p.append(rect(X_GRP, top, W_GRP, bot - top, sw=1.8, op=0.5, dash="1 8")
                 + text(X_GRP + 14, top + 24, name, 15))
        for sname, cy in servers:
            p.append(rect(X_SRV, cy - H_SRV / 2, W_SRV, H_SRV)
                     + text(X_SRV + W_SRV / 2, cy + 6, sname, 16, "middle"))
        up = mid(top, bot) < ly
        y0, y1 = (ly + 20, mid(top, bot)) if up else (ly + lh - 20, mid(top, bot))
        p.append(arrow(lx + lw + 4, y0, X_GRP - 8, y1))
        p.append(text(X_GRP - 12, y1 - 22 if up else y1 + 34, lab, 14, "end"))
    for name, tag, dbs, top, bot in INSTANCES:
        p.append(cylinder(PG_CX, top, bot, PG_RX, PG_RY))
        p.append(text(PG_CX, top + PG_RY + 30, name, 18, "middle"))
        p.append(text(PG_CX, top + PG_RY + 54, tag, 14, "middle"))
        for i, db in enumerate(dbs):
            p.append(text(PG_CX, top + PG_RY + 90 + 24 * i, db, 15, "middle"))
    for g, i, dash in LINKS:
        _, gtop, gbot, *_ = GROUPS[g]
        _, _, _, top, bot = INSTANCES[i]
        y0 = gtop + 60 if dash else mid(gtop, gbot)
        p.append(arrow(X_GRP + W_GRP + 4, y0, PG_CX - PG_RX - 8, mid(top, bot) + (25 if dash else 0),
                       sw=1.5 if dash else 1.8, dash=dash))
    return "".join(p)

ALT = ("Requests reach a Load balancer, which routes each request by its workspace. "
       "Requests for tenants 2, 3 and 4 go to the shared servers: Server 1, Server 2 and "
       "Server 3. Requests for tenant 1 go to tenant 1's own servers: Server 4 and Server 5. "
       "The shared servers connect to Database 1, which holds common_db and tenant_2_db, and "
       "to Database 2, which holds tenant_3_db and tenant_4_db. Tenant 1's servers connect to "
       "Database 3, which is dedicated to tenant 1 and holds tenant_1_db. A dotted arrow shows "
       "that tenant 1's servers still read common_db on Database 1.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  dedicated-servers — the heavy tenant gets its own servers too.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/dedicated-servers.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-dedicated-servers">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-dedicated-servers{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-dedicated-servers svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "dedicated-servers.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
