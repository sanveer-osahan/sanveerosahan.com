# Generates the Simple Monolith diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Left to right: the users, the one server they call, and the one database
# instance the server reads and writes. A dotted box beside the instance holds
# the databases it serves: one common database for Workspaces, Users and
# Memberships, then one database per tenant. A dotted arrow runs from the
# instance to each of them.
import io, os

from rough import *

W, H = 1080, 410

MID = 205                      # the row the three main shapes stand on
BOX_H = 76

X_USER, W_USER = 40, 140
X_SRV, W_SRV = 265, 150
DB_CX, DB_TOP, DB_BOT, DB_RX, DB_RY = 570, 150, 252, 80, 18

# The dotted box of databases the one instance serves.
BOX_X, BOX_Y, BOX_W, BOX_H2 = 715, 40, 345, 330
SMALL_CX, SMALL_RX, SMALL_RY, SMALL_HALF = 760, 24, 7, 16
DBS = (                        # (name, row centre, note under the name)
    ("common_db", 100, "Workspaces, Users, Memberships"),
    ("tenant_1_db", 185, None),
    ("tenant_2_db", 260, None),
)
MORE_Y = 325                   # the row that says there are more

def box(x, w, s, size=18):
    return rect(x, MID - BOX_H / 2, w, BOX_H) + text(x + w / 2, MID + 6, s, size, "middle")

def small_db(name, cy, note):
    p = [cylinder(SMALL_CX, cy - SMALL_HALF, cy + SMALL_HALF, SMALL_RX, SMALL_RY, sw=1.6)]
    lx = SMALL_CX + SMALL_RX + 16
    if note:
        p.append(text(lx, cy - 2, name, 16))
        p.append(text(lx, cy + 18, note, 13))
    else:
        p.append(text(lx, cy + 6, name, 16))
    return "".join(p)

def diagram():
    p = [frame(W, H)]
    p.append(box(X_USER, W_USER, "Users"))
    p.append(box(X_SRV, W_SRV, "Server"))
    p.append(cylinder(DB_CX, DB_TOP, DB_BOT, DB_RX, DB_RY))
    p.append(text(DB_CX, MID + 6, "Database", 18, "middle"))
    p.append(arrow(X_USER + W_USER + 4, MID, X_SRV - 8, MID))
    p.append(arrow(X_SRV + W_SRV + 4, MID, DB_CX - DB_RX - 8, MID))
    # The databases the one instance serves.
    p.append(rect(BOX_X, BOX_Y, BOX_W, BOX_H2, sw=1.8, op=0.5, dash="1 8"))
    for name, cy, note in DBS:
        p.append(small_db(name, cy, note))
        p.append(arrow(DB_CX + DB_RX + 6, MID + (cy - MID) * 0.25,
                       SMALL_CX - SMALL_RX - 8, cy, sw=1.5, dash="1 6"))
    p.append(text(SMALL_CX, MORE_Y + 6, "...", 18, "middle"))
    return "".join(p)

ALT = ("Starting with a simple monolith. Users call one Server, and the Server calls one "
       "Database instance. Beside the instance, a dotted box holds the databases it serves: "
       "common_db, which stores Workspaces, Users and Memberships, then tenant_1_db, "
       "tenant_2_db, and more.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  simple-monolith — the users, one server, one database instance and the databases it serves.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/simple-monolith.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-simple-monolith">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-simple-monolith{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-simple-monolith svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "simple-monolith.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
