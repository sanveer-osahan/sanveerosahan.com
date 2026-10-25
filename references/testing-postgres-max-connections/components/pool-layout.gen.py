# Generates the pool layout diagram: 3 servers of 8 cores, 2 databases, one pool per pair.
import io, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'designing-a-multi-tenant-system', 'components'))

from rough import *

W, H = 1080, 820

POOL = 14                      # connections in each pool: 8 cores need 14
X_SRV, W_SRV, H_SRV = 40, 230, 100
SRV_CY = (150, 410, 670)
DB_CX, DB_RX, DB_RY = 930, 130, 26
DB_TOP_BOT = ((50, 365), (475, 790))   # (top, bottom) of each cylinder
STUB = 150                     # the flat start of an arrow, where the pool label sits
BOX_W, BOX_H, BOX_GAP = 56, 44, 12

def database(j, top, bot):
    p = [cylinder(DB_CX, top, bot, DB_RX, DB_RY)]
    p.append(text(DB_CX, top + 86, f"Database {j}", 20, "middle"))
    p.append(text(DB_CX, top + 110, "2 GiB RAM", 16, "middle"))
    by = top + 126                                   # dotted box: max_connections
    p.append(rect(DB_CX - 112, by, 224, 148, 1.8, 1.0, "1 8"))
    p.append(text(DB_CX, by + 24, "max_connections: 100", 15, "middle"))
    x = DB_CX - (3 * BOX_W + 2 * BOX_GAP) / 2
    for _ in range(3):                               # one box per server pool
        p.append(rect(x, by + 38, BOX_W, BOX_H))
        p.append(text(x + BOX_W / 2, by + 38 + BOX_H / 2 + 6, str(POOL), 18, "middle"))
        x += BOX_W + BOX_GAP
    p.append(text(DB_CX, by + 112, f"{POOL * 3} in use", 16, "middle"))
    p.append(text(DB_CX, by + 132, "by the pools", 15, "middle"))
    return "".join(p)

def diagram():
    p = [frame(W, H)]
    for i, cy in enumerate(SRV_CY, 1):
        p.append(rect(X_SRV, cy - H_SRV / 2, W_SRV, H_SRV))
        p.append(text(X_SRV + W_SRV / 2, cy - 4, f"Server {i}", 20, "middle"))
        p.append(text(X_SRV + W_SRV / 2, cy + 24, "8 cores", 16, "middle"))
    for j, (top, bot) in enumerate(DB_TOP_BOT, 1):
        p.append(database(j, top, bot))
    end = DB_CX - DB_RX - 10
    x0 = X_SRV + W_SRV + 4
    for i, cy in enumerate(SRV_CY):
        for j, (top, bot) in enumerate(DB_TOP_BOT):
            y0 = cy + (-30 if j == 0 else 30)
            y1 = (top + bot) / 2 + (i - 1) * 40
            p.append(path(dline(x0, y0, x0 + STUB, y0), 1.8))
            p.append(arrow(x0 + STUB, y0, end, y1))
            p.append(text(x0 + 14, y0 - 12, f"pool: {POOL}", 15))
    return "".join(p)

ALT = ("Three application servers with 8 cores each and two database instances with 2 GiB of RAM "
       "and max_connections 100 each. Every server has one connection pool to each database, "
       "6 pools in all, and each pool holds 14 connections. Inside each database, a dotted box shows max_connections 100 and holds three boxes of 14, one per server pool. The pools use 42 connections in all.")

FONT_B64 = io.open(os.path.join(HERE, "..", "..", "designing-a-multi-tenant-system", "components", "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  pool-layout — 3 servers of 8 cores, 2 database instances and one pool for each pair.
  SINGLE SOURCE: references/testing-postgres-max-connections/components/pool-layout.gen.py
  Do not edit the copy. Edit the generator and run it.
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-pool-layout">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-pool-layout{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-pool-layout svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pool-layout.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
