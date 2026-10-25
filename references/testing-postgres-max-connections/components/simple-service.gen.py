# Generates the simple service diagram: users, one server, one database instance.
# Same drawing as the multi-tenant simple-service, without the box of databases.
import io, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'designing-a-multi-tenant-system', 'components'))

from rough import *

W, H = 700, 200

MID = 100                      # the row the three main shapes stand on
BOX_H = 76

X_USER, W_USER = 40, 140
X_SRV, W_SRV = 265, 150
DB_CX, DB_TOP, DB_BOT, DB_RX, DB_RY = 570, 45, 147, 80, 18

def box(x, w, s, size=18):
    return rect(x, MID - BOX_H / 2, w, BOX_H) + text(x + w / 2, MID + 6, s, size, "middle")

def diagram():
    p = [frame(W, H)]
    p.append(box(X_USER, W_USER, "Users"))
    p.append(box(X_SRV, W_SRV, "Server"))
    p.append(cylinder(DB_CX, DB_TOP, DB_BOT, DB_RX, DB_RY))
    p.append(text(DB_CX, MID + 6, "Database", 18, "middle"))
    p.append(arrow(X_USER + W_USER + 4, MID, X_SRV - 8, MID))
    p.append(arrow(X_SRV + W_SRV + 4, MID, DB_CX - DB_RX - 8, MID))
    return "".join(p)

ALT = "A simple service. Users call one Server, and the Server calls one Database instance."

FONT_B64 = io.open(os.path.join(HERE, "..", "..", "designing-a-multi-tenant-system", "components", "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  simple-service — the users, one server and one database instance.
  SINGLE SOURCE: references/testing-postgres-max-connections/components/simple-service.gen.py
  Do not edit the copy. Edit the generator and run it.
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-simple-service">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-simple-service{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-simple-service svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple-service.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
