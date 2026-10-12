# Generates the Rate Limiting diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Read left to right: Tenant A with two users and Tenant B with one user send
# requests to one server. User 1 is a script, so it has a thick box and a thick
# arrow. Inside the server, each request passes the user limit, then the tenant
# limit, then goes to the database. A request over either limit gets 429 with a
# Retry-After header.
import io, os

from rough import *

W, H = 1080, 430

X_GRP, W_GRP = 30, 200
X_USR, W_USR = 50, 160
TENANTS = (("Tenant A", 40, 200, (("User 1 (script)", 120, 3.2), ("User 2", 190, 1.8))),
           ("Tenant B", 270, 130, (("User 3", 345, 1.8),)))
SRV = (300, 40, 540, 360)                # x, y, w, h
CHECK_Y, CHECK_W, CHECK_H = 175, 160, 70
CHECKS = (("user limit", 345), ("tenant limit", 625))
PG_CX, PG_RX, PG_RY, PG_TOP, PG_BOT = 975, 75, 16, 150, 270

def diagram():
    p = [frame(W, H)]
    cy = CHECK_Y + CHECK_H / 2
    for name, top, h, users in TENANTS:
        p.append(rect(X_GRP, top, W_GRP, h, sw=1.8, op=0.5, dash="1 8")
                 + text(X_GRP + 14, top + 26, name, 16))
        for label, uy, sw in users:
            p.append(rect(X_USR, uy - 24, W_USR, 48, sw=sw)
                     + text(X_USR + W_USR / 2, uy + 6, label, 15, "middle"))
            p.append(arrow(X_USR + W_USR + 4, uy, CHECKS[0][1] - 8, cy, sw=sw))
    sx, sy, sw_, sh = SRV
    p.append(rect(sx, sy, sw_, sh) + text(sx + 20, sy + 32, "Server", 18))
    for i, (name, x) in enumerate(CHECKS):
        p.append(rect(x, CHECK_Y, CHECK_W, CHECK_H)
                 + text(x + CHECK_W / 2, cy + 6, name, 16, "middle"))
        mx = x + CHECK_W / 2
        p.append(arrow(mx, CHECK_Y + CHECK_H + 4, mx, 318))
        p.append(text(mx, 344, "429", 16, "middle")
                 + text(mx, 368, "Retry-After", 15, "middle"))
        nxt = CHECKS[i + 1][1] - 8 if i + 1 < len(CHECKS) else PG_CX - PG_RX - 8
        p.append(arrow(x + CHECK_W + 4, cy, nxt, cy))
    p.append(cylinder(PG_CX, PG_TOP, PG_BOT, PG_RX, PG_RY))
    p.append(text(PG_CX, PG_TOP + PG_RY + 52, "Database", 18, "middle"))
    return "".join(p)

ALT = ("Tenant A has two users, User 1 and User 2, and Tenant B has one user, User 3. "
       "User 1 is a script, drawn with a thick box and a thick arrow. All three users send "
       "requests to the Server. Inside the Server, each request passes the user limit, then "
       "the tenant limit, then goes to the database. A request over either limit gets 429 with "
       "a Retry-After header.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  rate-limit — the server checks the user limit, then the tenant limit.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/rate-limit.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-rate-limit">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-rate-limit{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-rate-limit svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "rate-limit.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
