# Generates the APIs sequence diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Three dotted bands hold the three levels of security: Unsecured, User scoped
# and Tenant scoped. One actor lifeline stands on the left, and the three
# journeys run one after another down the page:
#   User 1  signs up, then creates the workspace
#   User 2  signs up, then joins the same workspace
#   User 1  signs in, gets the workspace token, then lists the resources
# Every call draws the endpoint it reaches as a box in its own band. A solid
# arrow carries the request keys. A dotted arrow back carries the response keys.
import io, os

from rough import *

W = 1080

# --- columns ---------------------------------------------------------------

ACTOR = 110                    # the one lifeline every journey draws on
HEAD_W, HEAD_H = 120, 42

BANDS = (                      # (title, band left, band width)
    ("Unsecured", 360, 220),
    ("User scoped", 600, 220),
    ("Tenant scoped", 840, 220),
)
UNS, USR, TNT = (i for i in range(3))

EP_W, EP_H = 210, 44           # one endpoint box
BAND_TOP = 24
TITLE_Y = 50
FIRST_HEAD = 76                # the top of the first journey header

GAP_HEAD = 42                  # header bottom to the first call of a journey
STEP = 92                      # one call to the next
GAP_JOURNEY = 56               # the last call of a journey to the next header

# --- the journeys ----------------------------------------------------------
# (actor, [(band, endpoint, request keys, response keys)])

JOURNEYS = (
    ("User 1", (
        (UNS, "sign_up", "email, password", "user, identity_token"),
        (USR, "create_workspace", "identity_token, name, slug", "workspace, workspace_token"),
    )),
    ("User 2", (
        (UNS, "sign_up", "email, password", "user, identity_token"),
        (USR, "join_workspace", "identity_token, workspace_slug", "workspace, workspace_token"),
    )),
    ("User 1", (
        (UNS, "sign_in", "email, password", "user, identity_token"),
        (USR, "get_workspace_token", "identity_token, workspace_id", "workspace, workspace_token"),
        (TNT, "list_resources", "workspace_token", "resources"),
    )),
)

def layout():
    """The y of every header and every call, and the height the drawing needs."""
    y, rows = FIRST_HEAD, []
    for name, calls in JOURNEYS:
        head_y = y
        cy = head_y + HEAD_H + GAP_HEAD + EP_H / 2
        ys = [cy + i * STEP for i in range(len(calls))]
        rows.append((name, head_y, ys))
        y = ys[-1] + EP_H / 2 + GAP_JOURNEY
    return rows, int(y - GAP_JOURNEY + 46)

ROWS, H = layout()

def box(cx, cy, w, h, s, size=16):
    # One pass per edge. A doubled edge this wide reads as a shadow.
    return srect(cx - w / 2, cy - h / 2, w, h) + text(cx, cy + 6, s, size, "middle")

def call(n, band, name, req, res, y):
    """One call: the endpoint box, the request arrow and the response arrow."""
    _, bx, bw = BANDS[band]
    cx = bx + bw / 2
    p = [box(cx, y, EP_W, EP_H, f"{n}. {name}", 15)]
    x0, x1 = ACTOR + 7, cx - EP_W / 2 - 8
    # One pass per shaft. Over a span this long the two passes of a doubled
    # stroke drift apart, and the line reads as a blurred pair.
    p.append(sarrow(x0, y - 17, x1, y - 17))
    p.append(text((x0 + x1) / 2, y - 26, req, 13, "middle"))
    p.append(sarrow(x1, y + 21, x0, y + 21, sw=1.5, dash="1 6"))
    p.append(text((x0 + x1) / 2, y + 12, res, 13, "middle"))
    return "".join(p)

def diagram():
    p = []
    for title, bx, bw in BANDS:
        p.append(srect(bx, BAND_TOP, bw, H - 2 * BAND_TOP, sw=1.5, op=0.45, dash="1 8"))
        p.append(text(bx + bw / 2, TITLE_Y, title, 17, "middle"))
    n = 0
    for j, (name, head_y, ys) in enumerate(ROWS):
        if j:
            # One hairline between two journeys, so the three read apart.
            p.append(path(rline(40, head_y - 26, W - 40, head_y - 26), sw=1.2, op=0.35, dash="1 9"))
        p.append(box(ACTOR, head_y + HEAD_H / 2, HEAD_W, HEAD_H, name, 16))
        p.append(path(rline(ACTOR, head_y + HEAD_H, ACTOR, ys[-1] + EP_H / 2 + 14),
                      sw=1.4, op=0.5, dash="1 7"))
        for (band, ep, req, res), y in zip(JOURNEYS[j][1], ys):
            n += 1
            p.append(call(n, band, ep, req, res, y))
    return "".join(p)

ALT = ("The APIs as a sequence. Three dotted bands hold the three levels of security: "
       "Unsecured, User scoped and Tenant scoped, and every endpoint sits in the band that "
       "guards it. The three journeys run one after another. User 1 calls sign_up and then "
       "create_workspace. User 2 calls sign_up and then join_workspace. User 1 then calls "
       "sign_in, get_workspace_token and list_resources. A solid arrow carries the request "
       "keys and a dotted arrow back carries the response keys.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  api-sequence — the API calls of the example, in the Excalidraw stroke style.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/api-sequence.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-api-sequence">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-api-sequence{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-api-sequence svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "api-sequence.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes", "H =", H)
