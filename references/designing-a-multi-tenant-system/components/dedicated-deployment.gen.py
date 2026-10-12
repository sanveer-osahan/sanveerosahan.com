# Generates the Dedicated Deployment diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Two rows, each read left to right: requests, the load balancer, the servers,
# the database instances. The top row is the shared deployment for tenants 2,
# 3 and 4. The bottom row is tenant 1's dedicated deployment, a full copy of
# the system with its own common_db, in the region the customer chooses.
# Nothing connects the two rows.
import io, os

from rough import *

W, H = 1080, 650

X_REQ, W_REQ, H_REQ = 50, 130, 50
X_LB, W_LB, H_LB = 230, 140, 80
X_SRV, W_SRV, H_SRV = 440, 150, 60
PG_CX, PG_RX, PG_RY = 880, 115, 18

# Each deployment: its label, its frame top and bottom, the requests label,
# the centre of the row, the servers, and the instances.
DEPLOYMENTS = (
    ("shared deployment", 20, 360, "tenants 2, 3, 4", 190,
     (("Server 1", 100), ("Server 2", 190), ("Server 3", 280)),
     (("Database 1", ("common_db", "tenant_2_db"), 45, 160),
      ("Database 2", ("tenant_3_db", "tenant_4_db"), 215, 330))),
    ("tenant 1 deployment, in its own region", 390, 630, "tenant 1", 515,
     (("Server 4", 470), ("Server 5", 560)),
     (("Database 3", ("common_db", "tenant_1_db"), 445, 575),)),
)

def diagram():
    p = [frame(W, H)]
    for name, top, bot, who, cy, servers, instances in DEPLOYMENTS:
        p.append(rect(20, top, W - 40, bot - top, sw=1.8, op=0.5, dash="1 8")
                 + text(36, top + 26, name, 15))
        p.append(rect(X_REQ, cy - H_REQ / 2, W_REQ, H_REQ)
                 + text(X_REQ + W_REQ / 2, cy + 6, "Requests", 16, "middle")
                 + text(X_REQ + W_REQ / 2, cy + H_REQ / 2 + 24, who, 14, "middle"))
        p.append(rect(X_LB, cy - H_LB / 2, W_LB, H_LB)
                 + text(X_LB + W_LB / 2, cy - 6, "Load", 16, "middle")
                 + text(X_LB + W_LB / 2, cy + 18, "balancer", 16, "middle"))
        p.append(arrow(X_REQ + W_REQ + 4, cy, X_LB - 8, cy))
        for iname, dbs, itop, ibot in instances:
            p.append(cylinder(PG_CX, itop, ibot, PG_RX, PG_RY))
            p.append(text(PG_CX, itop + PG_RY + 28, iname, 18, "middle"))
            for i, db in enumerate(dbs):
                p.append(text(PG_CX, itop + PG_RY + 58 + 24 * i, db, 15, "middle"))
        for sname, sy in servers:
            p.append(rect(X_SRV, sy - H_SRV / 2, W_SRV, H_SRV)
                     + text(X_SRV + W_SRV / 2, sy + 6, sname, 16, "middle"))
            p.append(arrow(X_LB + W_LB + 4, cy, X_SRV - 8, sy))
            for *_, itop, ibot in instances:
                p.append(arrow(X_SRV + W_SRV + 4, sy, PG_CX - PG_RX - 8, (itop + ibot) / 2, sw=1.2))
    return "".join(p)

ALT = ("Two separate deployments of the same system. The shared deployment serves tenants "
       "2, 3 and 4: Requests reach its Load balancer, which sends them to Server 1, Server 2 "
       "and Server 3. These connect to Database 1, which holds common_db and tenant_2_db, and "
       "to Database 2, which holds tenant_3_db and tenant_4_db. Tenant 1's deployment runs in "
       "its own region: Requests reach its own Load balancer, which sends them to Server 4 "
       "and Server 5. These connect to Database 3, which holds its own common_db and "
       "tenant_1_db. Nothing connects the two deployments.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  dedicated-deployment — a full, separate copy of the system for one tenant.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/dedicated-deployment.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-dedicated-deployment">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-dedicated-deployment{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-dedicated-deployment svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "dedicated-deployment.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
