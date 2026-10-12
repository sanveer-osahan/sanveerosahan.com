# Generates the Connection Pool diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Two rows, each read left to right: requests, the server, the database.
#
# Without a pool: the server opens a new connection for each request, so each
# request has its own dotted arrow to the database.
#
# With a pool: the server keeps three connections open to the database. Requests 1
# to 3 each borrow one, and Request 4 waits for one to come back.
import io, os

from rough import *

W, H = 1080, 630

X_REQ, W_REQ, H_REQ = 40, 130, 40
PG_CX, PG_RX, PG_RY = 880, 90, 18

# Without a pool.
A_TITLE = 50
A_ROWS = (105, 165, 225)                 # the centre of each request
A_SRV = (250, 75, 150, 180)              # x, y, w, h
A_PG = (95, 235)                         # cylinder top, bottom

# With a pool.
B_TITLE = 330
B_ROWS = (425, 475, 525)                 # each request and the connection it borrows
B_WAIT = 585                             # the request that waits
B_SRV = (250, 350, 400, 220)
B_POOL = (420, 362, 210, 196)
X_CONN, W_CONN, H_CONN = 455, 140, 34
B_PG = (405, 545)

def request(cy, n):
    return (rect(X_REQ, cy - H_REQ / 2, W_REQ, H_REQ)
            + text(X_REQ + W_REQ / 2, cy + 6, f"Request {n}", 16, "middle"))

def postgres(top, bot):
    return (cylinder(PG_CX, top, bot, PG_RX, PG_RY)
            + text(PG_CX, (top + bot) / 2 + 12, "Database", 18, "middle"))

def diagram():
    p = [frame(W, H)]
    xr = X_REQ + W_REQ + 4
    xp = PG_CX - PG_RX - 8

    # Without a pool: one new connection per request.
    p.append(text(X_REQ, A_TITLE, "Without a pool", 18))
    sx, sy, sw_, sh = A_SRV
    p.append(rect(sx, sy, sw_, sh) + text(sx + sw_ / 2, sy + sh / 2 + 6, "Server", 18, "middle"))
    p.append(postgres(*A_PG))
    for n, cy in enumerate(A_ROWS, 1):
        p.append(request(cy, n))
        p.append(arrow(xr, cy, sx - 8, cy))
        p.append(arrow(sx + sw_ + 4, cy, xp, cy, sw=1.5, dash="1 6"))
    mid = A_ROWS[1]
    p.append(label(sx + sw_ + 4, mid, xp, mid, "new connection"))

    # With a pool: three connections stay open; Request 4 waits.
    p.append(text(X_REQ, B_TITLE, "With a pool", 18))
    sx, sy, sw_, sh = B_SRV
    p.append(rect(sx, sy, sw_, sh) + text(sx + 20, sy + 28, "Server", 18))
    px, py, pw, ph = B_POOL
    p.append(rect(px, py, pw, ph, sw=1.8, op=0.5, dash="1 8"))
    p.append(text(px + pw / 2, py + 26, "Connection pool", 16, "middle"))
    p.append(postgres(*B_PG))
    for n, cy in enumerate(B_ROWS, 1):
        p.append(request(cy, n))
        p.append(arrow(xr, cy, X_CONN - 8, cy))
        p.append(rect(X_CONN, cy - H_CONN / 2, W_CONN, H_CONN, sw=1.6)
                 + text(X_CONN + W_CONN / 2, cy + 5, "in use", 15, "middle"))
        p.append(path(dline(X_CONN + W_CONN + 4, cy, PG_CX - PG_RX - 4, cy), 1.8))
    top = B_ROWS[0]
    p.append(label(X_CONN + W_CONN + 4, top, PG_CX - PG_RX - 4, top, "kept open"))
    p.append(request(B_WAIT, 4))
    p.append(text(xr + 12, B_WAIT + 6, "waits", 16))
    return "".join(p)

ALT = ("How the server connects to the database, in two rows. Without a pool: Requests 1, 2 and 3 "
       "reach the Server, and the Server opens a new connection to the database for each one. "
       "With a pool: inside the Server, a dotted Connection pool box holds three connections "
       "that stay open to the database. Requests 1, 2 and 3 each use one of them, and Request 4 "
       "waits.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  connection-pool — requests without a pool and with one.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/connection-pool.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-connection-pool">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-connection-pool{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-connection-pool svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "connection-pool.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
