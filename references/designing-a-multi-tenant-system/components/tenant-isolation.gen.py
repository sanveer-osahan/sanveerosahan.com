# Generates the Tenant Isolation diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with, and the drawing keeps that look: no border,
# boxes, arrows and Comic Shanns labels.
#
# Who may reach which tenant:
#   User 1 -owner--> Workspace 1
#   User 2 -viewer-> Workspace 1
#   User 2 -owner--> Workspace 2
#   User 1 -  X  -> Workspace 2
# The last arrow is dotted and carries a cross. Nothing but the application
# logic stops that call, which is the point the section makes.
import io, math, os

from rough import *

W, H = 1080, 400   # one box holds the whole drawing

BOX_H = 80

# Two columns: the users on the left, the tenants they reach on the right.
X_USER, W_USER = 80, 200
X_WS, W_WS = 720, 280

ROW1, ROW2 = 115, 295   # one row per user, one row per workspace

X0 = X_USER + W_USER + 2   # every arrow leaves the right edge of a user box
X1 = X_WS - 8              # and stops short of the left edge of a workspace box

def box(x, mid, w, s, size=18):
    y = mid - BOX_H / 2
    return rect(x, y, w, BOX_H) + text(x + w / 2, mid + 6, s, size, "middle")

def cross(x, y, r=11):
    """The cross that marks a call the system must refuse."""
    return path(dline(x - r, y - r, x + r, y + r)
                + " " + dline(x + r, y - r, x - r, y + r), sw=2.2)

def diagram():
    p = [frame(W, H)]
    p.append(box(X_USER, ROW1, W_USER, "User 1"))
    p.append(box(X_USER, ROW2, W_USER, "User 2"))
    p.append(box(X_WS, ROW1, W_WS, "Workspace 1"))
    p.append(box(X_WS, ROW2, W_WS, "Workspace 2"))
    # User 1 owns Workspace 1.
    p.append(arrow(X0, ROW1, X1, ROW1))
    p.append(label(X0, ROW1, X1, ROW1, "owner", size=15, off=16))
    # User 2 reads the same workspace, and owns one of its own.
    ax0, ay0, ax1, ay1 = X0, ROW2 - 22, X1, ROW1 + 20
    p.append(arrow(ax0, ay0, ax1, ay1))
    # The midpoint of this arrow is where the two diagonals cross, so the label
    # rides the far half of it instead.
    p.append(label(ax0 + (ax1 - ax0) * 0.45, ay0 + (ay1 - ay0) * 0.45,
                   ax1, ay1, "viewer", size=15, off=16))
    p.append(arrow(X0, ROW2, X1, ROW2))
    p.append(label(X0, ROW2, X1, ROW2, "owner", size=15, off=16))
    # User 1 reaches for Workspace 2. The system must refuse this call.
    y0, y1 = ROW1 + 22, ROW2 - 20
    p.append(arrow(X0, y0, X1, y1, dash="1 7"))
    p.append(cross(X0 + (X1 - X0) * 0.3, y0 + (y1 - y0) * 0.3))
    return "".join(p)

ALT = ("Tenant Isolation. User 1 is the owner of Workspace 1. User 2 is a viewer of "
       "Workspace 1 and the owner of Workspace 2. A dotted arrow runs from User 1 to "
       "Workspace 2 and carries a cross: User 1 must not reach the data of Workspace 2.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  tenant-isolation — who may reach which tenant, in the Excalidraw stroke style.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/tenant-isolation.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-tenant-isolation">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-tenant-isolation{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-tenant-isolation svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "tenant-isolation.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
