# Generates the Connection Limits diagram for the max_connections article.
#
# It reuses rough.py and the Comic Shanns font from the multi-tenant components,
# so the strokes match the diagrams in that article.
#
# 150 requests reach a pool of 12 connections. 12 requests hold a connection, the
# rest wait in a queue, and a request that waits more than 10s times out. The 12
# pooled connections use 12 of the 100 connections that the database allows.
import io, os, sys

SHARED = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "../../designing-a-multi-tenant-system/components")
sys.path.insert(0, SHARED)
from rough import *
import rough

W, H = 1080, 650
RED = "#e03131"

def red(s):
    return s.replace('fill="currentColor"', f'fill="{RED}"').replace("<path ", f'<path stroke="{RED}" ')

LANES = ((140, "conn 1"), (195, "conn 2"), (250, "conn 3"), (345, "conn 12"))

def diagram():
    p = []
    p.append(text(40, 40, "150 requests", 18))

    # The 12 requests that hold a connection, one lane each.
    for cy, name in LANES:
        n = name.split()[1]
        p.append(rect(40, cy - 18, 130, 36) + text(105, cy + 6, f"Request {n}", 16, "middle"))
        p.append(arrow(174, cy, 286, cy))
        p.append(rect(290, cy - 17, 110, 34, sw=1.6) + text(345, cy + 5, name, 15, "middle"))
        p.append(arrow(404, cy, 731, cy))
    p.append(text(105, 302, "...", 22, "middle"))
    p.append(text(345, 302, "...", 22, "middle"))

    # The pool, a channel of 12 lanes.
    p.append(rect(250, 75, 380, 320, sw=1.8, op=0.5, dash="1 8"))
    p.append(text(440, 100, "Pool: 12 connections", 16, "middle"))

    # The database: a cylinder. The large box allows 100, the small box is what the pool takes.
    p.append(text(885, 40, "Database", 18, "middle"))
    p.append(cylinder(885, 75, 405, 190, 26))
    p.append(rect(715, 105, 340, 275, sw=1.8, dash="1 8"))
    p.append(text(962, 148, "max_connections: 100", 14, "middle"))
    p.append(rect(735, 125, 130, 240, sw=1.8, dash="1 8"))
    p.append(text(800, 240, "12 taken", 15, "middle"))
    p.append(text(800, 262, "by the pool", 15, "middle"))

    # The queue: Request 13 is at the head, Request 150 at the tail.
    p.append(text(480, 438, "Queue", 16))
    p.append(rect(40, 450, 530, 56))
    for x, w, label_ in ((50, 100, "Request 13"), (160, 100, "Request 14"), (270, 100, "Request 15"), (440, 120, "Request 150")):
        p.append(rect(x, 458, w, 40, sw=1.6) + text(x + w / 2, 483, label_, 15, "middle"))
    p.append(text(405, 488, "...", 22, "middle"))
    p.append(arrow(100, 450, 290, 398))
    p.append(text(240, 440, "wait", 16))

    # The timeout.
    p.append(red(arrow(230, 510, 230, 576)))
    p.append(red(text(246, 550, "wait &gt; 10s", 16)))
    p.append(red(rect(40, 580, 380, 50) + text(230, 611, "timed out: context deadline exceeded", 15, "middle")))
    return "".join(p)

ALT = ("150 requests reach the server. 12 requests each use one of the 12 connections, conn 1 to "
       "conn 12, in the pool. The 12 connections end in a small box inside a large box in the database. "
       "The large box shows the 100 connections the database allows. The small box holds the 12 taken by the "
       "pool. The other 138 requests, Request 13 to Request 150, wait in a queue for a "
       "free connection. A request that waits more than 10 seconds times out with a context "
       "deadline exceeded error.")

FONT_B64 = io.open(os.path.join(rough.HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  connection-limits: 150 requests, a pool of 12 and a database that allows 100.
  SINGLE SOURCE: references/testing-postgres-max-connections/components/connection-limits.gen.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-connection-limits">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-connection-limits{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-connection-limits svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "connection-limits.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
