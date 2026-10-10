# Generates the Identity diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the Onboarding
# diagram draws with, and the drawing keeps that look: boxes,
# arrows and Comic Shanns labels.
#
# The sequence runs left to right, User -> Product -> Workspace, and each user
# gets its own row with its own Product, the way the Onboarding rows do:
#   User 1 -signs-up-> Product -1. creates / owner--> Workspace 1
#   User 2 -signs-up-> Product -2. joins / member---> Workspace 1
#                              -3. creates / owner-> Workspace 2
# Workspace 1 is drawn once, because the point of the drawing is that both users
# belong to the same workspace, in two different roles. The number is the step.
# The word under the arrow is the role the step grants.
import io, math, os

from rough import *

W, H = 1080, 386   # one box holds the whole drawing

BOX_H, WS_H = 70, 90

# Three columns: the user, the product it signs up on, the workspace the product
# binds it to.
X_USER, W_USER = 40, 170
CX_PROD, RX_PROD, RY_PROD = 470, 72, 54
X_WS, W_WS = 800, 240

ROW1, ROW2 = 95, 300   # one row per user
MID_W2 = ROW2          # the workspace User 2 creates sits on its own row

def box(x, y, w, h, s, size=17):
    return rect(x, y, w, h) + text(x + w / 2, y + h / 2 + 6, s, size, "middle")

def edge(cy, y, side):
    """The point on a product ellipse at the given height, left or right."""
    sin = (y - cy) / RY_PROD
    cos = math.sqrt(max(0.0, 1 - sin * sin))
    return CX_PROD + side * (RX_PROD * cos + 7)

def node_user(mid, s):
    return box(X_USER, mid - BOX_H / 2, W_USER, BOX_H, s)

def node_product(mid):
    return (ellipse(CX_PROD, mid, RX_PROD, RY_PROD)
            + text(CX_PROD, mid + 6, "Product", 17, "middle"))

def node_ws(mid, s):
    return box(X_WS, mid - WS_H / 2, W_WS, WS_H, s)

def signup(mid):
    x0, x1 = X_USER + W_USER + 2, edge(mid, mid, -1)
    return arrow(x0, mid, x1, mid) + label(x0, mid, x1, mid, "signs-up", size=14, off=16)

def bind(cy, y0, y1, step, role):
    """One arrow from a product to a workspace, with the step and the role."""
    x0, x1 = edge(cy, y0, 1), X_WS - 8
    return (arrow(x0, y0, x1, y1)
            + label(x0, y0, x1, y1, step, size=14, off=16)
            + label(x0, y0, x1, y1, role, size=14, off=-26))

def diagram():
    p = [frame(W, H)]
    # Row 1: User 1 creates the workspace and owns it.
    p.append(node_user(ROW1, "User 1"))
    p.append(node_product(ROW1))
    p.append(node_ws(ROW1, "Workspace 1"))
    p.append(signup(ROW1))
    p.append(bind(ROW1, ROW1, ROW1, "1. creates", "owner"))
    # Row 2: User 2 joins the same workspace, and creates one of its own.
    p.append(node_user(ROW2, "User 2"))
    p.append(node_product(ROW2))
    p.append(node_ws(MID_W2, "Workspace 2"))
    p.append(signup(ROW2))
    p.append(bind(ROW2, ROW2 - 25, ROW1 + 30, "2. joins", "member"))
    p.append(bind(ROW2, ROW2, MID_W2, "3. creates", "owner"))
    return "".join(p)

ALT = ("Identity. User 1 signs up on the product, creates Workspace 1 and owns it. "
       "User 2 signs up on the same product, joins the same Workspace 1 as a member, "
       "and creates Workspace 2, which User 2 owns.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  identity — one user, many tenants, one role in each, in the Excalidraw stroke style.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/identity.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-identity">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-identity{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-identity svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "identity.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
