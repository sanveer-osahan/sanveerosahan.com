# Generates the Request Timeline diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Time runs left to right. Three requests start 10 ms apart. Each one uses the
# CPU for 10 ms, waits 100 ms for the database and 80 ms for other things, then
# uses the CPU for 10 ms more. The bottom row is the one core: it runs the CPU
# parts of all three requests, and it is free while they wait.
import io, os

from rough import *

W, H = 1080, 350

X0, PX = 180, 3.9                        # where 0 ms is, pixels per ms
H_BAR = 38
ROWS = (70, 135, 200)                    # the centre of each request row
CORE = 295                               # the centre of the core row
CPU_MS = 10
PARTS = ((CPU_MS, "CPU", False), (100, "database 100 ms", True),
         (80, "other waits 80 ms", True), (CPU_MS, "CPU", False))

def x(ms):
    return X0 + ms * PX

def block(ms0, ms1, cy, s, dotted, size=14):
    x0, x1 = x(ms0), x(ms1)
    r = (rect(x0, cy - H_BAR / 2, x1 - x0, H_BAR, sw=1.8, op=0.5, dash="1 8") if dotted
         else rect(x0, cy - H_BAR / 2, x1 - x0, H_BAR, sw=1.8))
    return r + text((x0 + x1) / 2, cy + 5, s, size, "middle")

def diagram():
    p = [frame(W, H)]
    for n, cy in enumerate(ROWS, 1):
        p.append(text(40, cy + 6, f"Request {n}", 16))
        t = (n - 1) * CPU_MS
        for ms, s, dotted in PARTS:
            p.append(block(t, t + ms, cy, s, dotted, 12 if s == "CPU" else 14))
            t += ms
    p.append(text(40, CORE + 6, "One core", 16))
    for n in range(3):
        p.append(block(n * CPU_MS, (n + 1) * CPU_MS, CORE, str(n + 1), False, 14))
        p.append(block(190 + n * CPU_MS, 200 + n * CPU_MS, CORE, str(n + 1), False, 14))
    p.append(block(3 * CPU_MS, 190, CORE, "free for other requests", True))
    return "".join(p)

ALT = ("Three requests over time, each starting 10 ms after the one before. Each request "
       "uses the CPU for 10 ms, waits 100 ms for the database and 80 ms for other things, "
       "then uses the CPU for 10 ms. The bottom row is one core: it runs the first CPU part "
       "of Requests 1, 2 and 3, is free for other requests while they wait, then runs their "
       "last CPU part.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  request-timeline — one core and three requests over time.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/request-timeline.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-request-timeline">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-request-timeline{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-request-timeline svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "request-timeline.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
