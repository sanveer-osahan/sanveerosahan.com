# Generates the Onboarding diagram component (single source of truth).
#
# The strokes come from rough.py, the Rough.js algorithm that Excalidraw itself
# draws with, so this drawing matches the B2C / B2B pair in the same article.
# The labels use Comic Shanns, inlined as a data URI, so the drawing carries its
# own font everywhere it is used.
#
# The diagram holds two flows, one under the other:
#   User 1 -1. signs-up-> Product -2. new workspace-> Workspace 1
#                                      -3. provision-> Tenant Resources
#   User 2 -4. signs-up-> Product -5. join workspace-> Workspace 1
# Each flow repeats the Product and the Workspace, so each one reads on its own.
import io, math, os

from rough import *

W, H = 1080, 336   # one box holds the whole drawing

MID1, MID2 = 84, 252   # the line each flow sits on
BOX_H = 64
WS_H = 80
ELL_RX, ELL_RY = 60, 46

# The four columns. Both flows put their nodes on the same columns, so the
# repeated Product and Workspace line up under each other.
X_USER, W_USER = 40, 110
X_PROD = 290                      # the left edge of the product ellipse
CX_PROD = X_PROD + ELL_RX
X_WS, W_WS = 580, 160
X_TR, W_TR = 870, 170

def box(x, y, w, h, s, size=17):
    return rect(x, y, w, h) + text(x + w / 2, y + h / 2 + 6, s, size, "middle")

def node_user(mid, s):
    return box(X_USER, mid - BOX_H / 2, W_USER, BOX_H, s)

def node_product(mid):
    return (ellipse(CX_PROD, mid, ELL_RX, ELL_RY)
            + text(CX_PROD, mid + 6, "Product", 17, "middle"))

def hflow(mid, pairs):
    """The horizontal arrows of one flow, each with its numbered label."""
    out = []
    for x0, x1, s in pairs:
        out.append(arrow(x0, mid, x1, mid))
        out.append(label(x0, mid, x1, mid, s, size=14, off=16))
    return out

def flow_one():
    p = [node_user(MID1, "User 1"), node_product(MID1)]
    p.append(box(X_WS, MID1 - WS_H / 2, W_WS, WS_H, "Workspace 1"))
    p.append(box(X_TR, MID1 - WS_H / 2, W_TR, WS_H, "Tenant Resources"))
    p += hflow(MID1, [
        (X_USER + W_USER + 2, X_PROD - 8, "1. signs-up"),
        (CX_PROD + ELL_RX + 8, X_WS - 8, "2. new workspace"),
        (X_WS + W_WS + 8, X_TR - 8, "3. provision"),
    ])
    return "".join(p)

def flow_two():
    p = [node_user(MID2, "User 2"), node_product(MID2)]
    p.append(box(X_WS, MID2 - WS_H / 2, W_WS, WS_H, "Workspace 1"))
    p += hflow(MID2, [
        (X_USER + W_USER + 2, X_PROD - 8, "4. signs-up"),
        (CX_PROD + ELL_RX + 8, X_WS - 8, "5. join workspace"),
    ])
    return "".join(p)

ALT = ("Onboarding, in two flows. First flow: User 1 signs up to the product, the "
       "sign-up creates Workspace 1, and Workspace 1 provisions the tenant resources. "
       "Second flow: User 2 signs up to the same product and joins Workspace 1.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  onboarding — the sign-up flow, drawn in the Excalidraw stroke style.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/onboarding.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-onboarding">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-onboarding{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-onboarding svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {frame(W, H)}
  {flow_one()}
  {flow_two()}
</svg>
</figure>
'''

out = os.path.join(HERE, "onboarding.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
