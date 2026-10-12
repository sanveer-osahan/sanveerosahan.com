# Generates the Load Balancer diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Read left to right: requests, the load balancer, three servers, one database.
# Each server opens its own connections, so every new server adds more
# connections to the same database.
import io, os

from rough import *

W, H = 1080, 500

REQ = (40, 225, 130, 50)                 # x, y, w, h
LB = (230, 210, 170, 80)
X_SRV, W_SRV, H_SRV = 500, 160, 100
ROWS = (95, 250, 405)                    # the centre of each server
PG_CX, PG_RX, PG_RY, PG_TOP, PG_BOT = 920, 90, 18, 165, 335

def diagram():
    p = [frame(W, H)]
    rx, ry, rw, rh = REQ
    p.append(rect(rx, ry, rw, rh) + text(rx + rw / 2, ry + rh / 2 + 6, "Requests", 16, "middle"))
    lx, ly, lw, lh = LB
    p.append(rect(lx, ly, lw, lh) + text(lx + lw / 2, ly + 34, "Load", 16, "middle")
             + text(lx + lw / 2, ly + 58, "balancer", 16, "middle"))
    p.append(arrow(rx + rw + 4, ry + rh / 2, lx - 8, ly + lh / 2))
    p.append(cylinder(PG_CX, PG_TOP, PG_BOT, PG_RX, PG_RY)
             + text(PG_CX, (PG_TOP + PG_BOT) / 2 + 12, "Database", 18, "middle"))
    for n, cy in enumerate(ROWS, 1):
        p.append(rect(X_SRV, cy - H_SRV / 2, W_SRV, H_SRV)
                 + text(X_SRV + W_SRV / 2, cy + 6, f"Server {n}", 16, "middle"))
        p.append(arrow(lx + lw + 4, ly + lh / 2, X_SRV - 8, cy))
        ty = (PG_TOP + PG_BOT) / 2 + (cy - ROWS[1]) * 0.45
        p.append(arrow(X_SRV + W_SRV + 4, cy, PG_CX - PG_RX - 8, ty))
    return "".join(p)

ALT = ("Requests reach a Load balancer, which sends each request to one of three servers: "
       "Server 1, Server 2 and Server 3. All three servers connect to the same database.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  load-balancer — a load balancer in front of three servers.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/load-balancer.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-load-balancer">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-load-balancer{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-load-balancer svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "load-balancer.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
