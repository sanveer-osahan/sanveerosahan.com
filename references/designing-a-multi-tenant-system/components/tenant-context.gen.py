# Generates the Tenant Context diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the Onboarding and
# the Identity diagrams draw with, and the drawing keeps that look: one dotted
# box, boxes, arrows and Comic Shanns labels.
#
# One request, one tenant:
#   User -make_request(tenant="Workspace 1")-> Product -routed to-> Workspace 1
#                                                      -  -  -  -  > Workspace 2
# The solid arrow is the tenant the context names. The dotted arrow is the other
# tenant the same user belongs to, which this request never reaches.
import io, math, os

from rough import *

W, H = 1080, 340   # one box holds the whole drawing

BOX_H, WS_H = 70, 90

# Three columns: the user, the product it calls, the workspace the product
# routes the call to.
X_USER, W_USER = 40, 150
CX_PROD, RX_PROD, RY_PROD = 560, 72, 54
X_WS, W_WS = 850, 200

ROW1, ROW2 = 120, 260   # Workspace 1 sits on the request line, Workspace 2 below it

# The call breaks over two lines, so the label stays narrow.
REQ = ("make_request", '(tenant="Workspace 1")')

def box(x, y, w, h, s, size=17):
    return rect(x, y, w, h) + text(x + w / 2, y + h / 2 + 6, s, size, "middle")

def edge(cy, y, side):
    """The point on the product ellipse at the given height, left or right."""
    sin = (y - cy) / RY_PROD
    cos = math.sqrt(max(0.0, 1 - sin * sin))
    return CX_PROD + side * (RX_PROD * cos + 7)

def diagram():
    p = [frame(W, H)]
    p.append(box(X_USER, ROW1 - BOX_H / 2, W_USER, BOX_H, "User"))
    p.append(ellipse(CX_PROD, ROW1, RX_PROD, RY_PROD))
    p.append(text(CX_PROD, ROW1 + 6, "Product", 17, "middle"))
    p.append(box(X_WS, ROW1 - WS_H / 2, W_WS, WS_H, "Workspace 1"))
    p.append(box(X_WS, ROW2 - WS_H / 2, W_WS, WS_H, "Workspace 2"))
    # The request carries the tenant identifier.
    x0, x1 = X_USER + W_USER + 2, edge(ROW1, ROW1, -1)
    p.append(arrow(x0, ROW1, x1, ROW1))
    p.append(label(x0, ROW1, x1, ROW1, REQ[0], size=14, off=34))
    p.append(label(x0, ROW1, x1, ROW1, REQ[1], size=14, off=16))
    # The product routes it to that tenant, and to that tenant only.
    x0, x1 = edge(ROW1, ROW1, 1), X_WS - 8
    p.append(arrow(x0, ROW1, x1, ROW1))
    p.append(label(x0, ROW1, x1, ROW1, "routed to", size=14, off=16))
    x0, y0 = edge(ROW1, ROW1 + 34, 1), ROW1 + 34
    p.append(arrow(x0, y0, X_WS - 8, ROW2, dash="1 7"))
    return "".join(p)

ALT = ("Tenant Context. The user calls the product with a make_request that names the tenant "
       "Workspace 1. The product routes the request to Workspace 1. A dotted arrow runs "
       "to Workspace 2, the other tenant, which this request never reaches.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  tenant-context — one request, one tenant, in the Excalidraw stroke style.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/tenant-context.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-tenant-context">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-tenant-context{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-tenant-context svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "tenant-context.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
