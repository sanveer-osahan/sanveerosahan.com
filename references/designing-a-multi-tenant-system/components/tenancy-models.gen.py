# Generates the B2C / B2B diagram component (single source of truth).
#
# The strokes come from rough.py, the Rough.js algorithm that Excalidraw itself
# draws with. The shapes stay in place; only the ink is sloppy. The labels use
# Comic Shanns, an Excalidraw font, subset to the characters this drawing
# needs and inlined as a data URI so the drawing carries its own font everywhere
# it is used.
import io, os

from rough import *

# --- The two panels -------------------------------------------------------
#
# The B2B panel holds three orgs of three users, so it needs more room than the
# B2C panel. Both panels share one height and one unit, and the row gives each
# cell a flex-grow equal to its own width. The two drawings therefore render at
# the same scale, and the B2B panel is simply wider.

H = 480
W_B2C, W_B2B = 440, 620

def panel_b2c():
    p = [frame(W_B2C, H), text(38, 62, "Business to Consumer (B2C)", 20)]
    cx, cy = 96, 272
    p.append(ellipse(cx, cy, 56, 44))
    p.append(text(cx, cy + 7, "Product", 19, "middle"))
    bx, bw, bh = 252, 156, 72
    for i, y in enumerate((116, 236, 356)):
        p.append(rect(bx, y, bw, bh))
        p.append(text(bx + bw / 2, y + bh / 2 + 7, f"User {i + 1}", 19, "middle"))
        p.append(arrow(cx + 58, cy - 2, bx - 14, y + bh / 2))
    return "".join(p)

def panel_b2b():
    p = [frame(W_B2B, H), text(38, 62, "Business to Business (B2B)", 20)]
    cx, cy = 100, 272
    p.append(ellipse(cx, cy, 58, 44))
    p.append(text(cx, cy + 7, "Product", 19, "middle"))
    bx, bw, bh = 252, 340, 96
    for i, y in enumerate((104, 224, 344)):
        p.append(rect(bx, y, bw, bh))
        p.append(text(bx + 18, y + 30, f"Org {i + 1}", 19))
        for j in range(3):
            ux, uy, uw, uh = bx + 12 + j * 112, y + 42, 92, 42
            p.append(rect(ux, uy, uw, uh, sw=1.3, op=0.78))
            p.append(text(ux + uw / 2, uy + uh / 2 + 6, f"User {j + 1}", 16, "middle"))
        p.append(arrow(cx + 60, cy - 2, bx - 14, y + bh / 2))
    return "".join(p)

def svg_attrs(w):
    return (f'viewBox="0 0 {w} {H}" role="img" fill="none" stroke="currentColor" '
            'stroke-linecap="round" stroke-linejoin="round"')

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  tenancy-models — the B2C / B2B pair, drawn in the Excalidraw stroke style.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/tenancy-models.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-tenancy">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-tenancy{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-tenancy .dg-row{{display:flex;gap:20px;align-items:flex-start}}
.diagram-tenancy .dg-cell{{min-width:0}}
.diagram-tenancy .dg-b2c{{flex:{W_B2C} 1 0}}
.diagram-tenancy .dg-b2b{{flex:{W_B2B} 1 0}}
.diagram-tenancy svg{{display:block;width:100%;height:auto;color:inherit}}
@media (max-width:760px){{
  .diagram-tenancy .dg-row{{display:block}}
  .diagram-tenancy .dg-cell + .dg-cell{{margin-top:20px}}
}}
</style>
<div class="dg-row">
  <div class="dg-cell dg-b2c">
    <svg {svg_attrs(W_B2C)} aria-label="Business to Consumer: one product draws an arrow straight to User 1, User 2 and User 3.">
      {panel_b2c()}
    </svg>
  </div>
  <div class="dg-cell dg-b2b">
    <svg {svg_attrs(W_B2B)} aria-label="Business to Business: one product draws an arrow to Org 1, Org 2 and Org 3, and each org holds User 1, User 2 and User 3.">
      {panel_b2b()}
    </svg>
  </div>
</div>
</figure>
'''

out = os.path.join(HERE, "tenancy-models.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
