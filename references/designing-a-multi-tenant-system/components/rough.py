# The Rough.js stroke primitives that Excalidraw itself draws with.
#
# Every straight edge is a cubic bezier whose two control points and two end
# points move by a small random offset, and every edge is drawn twice. The
# shapes stay in place; only the ink is sloppy.
#
# Both diagram generators in this folder import this module. One seed serves
# them all, so a drawing looks the same every time the generator runs.
import math, random, io, os

R = random.Random(20260924)

HERE = os.path.dirname(os.path.abspath(__file__))

def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")

# --- Rough.js stroke primitives -------------------------------------------

ROUGHNESS = 1.0
BOWING = 1.0
MAXOFF = 2.0

def _off(lo, hi, gain):
    return ROUGHNESS * gain * (R.random() * (hi - lo) + lo)

def _off_sym(a, gain):
    return _off(-a, a, gain)

def rline(x1, y1, x2, y2, overlay=False, move=True):
    """One Rough.js line: a bowed cubic with jittered ends and controls."""
    lensq = (x1 - x2) ** 2 + (y1 - y2) ** 2
    ln = math.sqrt(lensq)
    if ln < 200:
        gain = 1.0
    elif ln > 500:
        gain = 0.4
    else:
        gain = -0.0016668 * ln + 1.233334
    offset = MAXOFF
    if offset * offset * 100 > lensq:
        offset = ln / 10
    if overlay:
        offset = offset / 2
    diverge = 0.2 + R.random() * 0.2
    mdx = _off_sym(BOWING * MAXOFF * (y2 - y1) / 200, gain)
    mdy = _off_sym(BOWING * MAXOFF * (x1 - x2) / 200, gain)
    r = lambda: _off_sym(offset, gain)
    d = f"M{f(x1 + r())},{f(y1 + r())} " if move else ""
    d += ("C%s,%s %s,%s %s,%s" % (
        f(mdx + x1 + (x2 - x1) * diverge + r()), f(mdy + y1 + (y2 - y1) * diverge + r()),
        f(mdx + x1 + 2 * (x2 - x1) * diverge + r()), f(mdy + y1 + 2 * (y2 - y1) * diverge + r()),
        f(x2 + r()), f(y2 + r())))
    return d

def dline(x1, y1, x2, y2):
    """A line drawn twice, the way Excalidraw draws every edge."""
    return rline(x1, y1, x2, y2) + " " + rline(x1, y1, x2, y2, overlay=True)

def path(d, sw=1.8, op=1.0, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" stroke-width="{sw}" opacity="{op}"{da}/>'

def rect(x, y, w, h, sw=1.8, op=1.0, dash=None):
    d = " ".join([
        dline(x, y, x + w, y),
        dline(x + w, y, x + w, y + h),
        dline(x + w, y + h, x, y + h),
        dline(x, y + h, x, y),
    ])
    return path(d, sw, op, dash)

def _curve(pts):
    """Rough.js _curve with curveTightness 0."""
    if len(pts) < 4:
        return ""
    d = f"M{f(pts[1][0])},{f(pts[1][1])}"
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] + (p1[0] - p3[0]) / 6, p2[1] + (p1[1] - p3[1]) / 6)
        d += " C%s,%s %s,%s %s,%s" % (f(c1[0]), f(c1[1]), f(c2[0]), f(c2[1]), f(p2[0]), f(p2[1]))
    return d

def _ellipse_points(inc, cx, cy, rx, ry, overlap):
    core, allp = [], []
    rad = _off_sym(0.5, 1.0) - math.pi / 2
    o = lambda: _off_sym(1.0, 1.0)
    core.append((o() + cx + 0.9 * rx * math.cos(rad - inc), o() + cy + 0.9 * ry * math.sin(rad - inc)))
    a = rad
    while a < rad + 2 * math.pi + inc - 0.01:
        p = (o() + cx + rx * math.cos(a), o() + cy + ry * math.sin(a))
        allp.append(p)
        core.append(p)
        a += inc
    allp.append((o() + cx + rx * math.cos(rad + 2 * math.pi + overlap * 0.5),
                 o() + cy + ry * math.sin(rad + 2 * math.pi + overlap * 0.5)))
    allp.append((o() + cx + 0.98 * rx * math.cos(rad + overlap),
                 o() + cy + 0.98 * ry * math.sin(rad + overlap)))
    allp.append((o() + cx + 0.9 * rx * math.cos(rad + overlap * 0.5),
                 o() + cy + 0.9 * ry * math.sin(rad + overlap * 0.5)))
    return allp, core

def ellipse(cx, cy, rx, ry, sw=1.8, op=1.0):
    inc = (2 * math.pi) / 9
    rx = rx + _off_sym(rx * 0.05, 1.0)
    ry = ry + _off_sym(ry * 0.05, 1.0)
    overlap = inc * _off(0.1, _off(0.4, 1.0, 1.0), 1.0)
    allp, core = _ellipse_points(inc, cx, cy, rx, ry, overlap)
    return path(_curve(allp) + " " + _curve(core), sw, op)

def arrow(x0, y0, x1, y1, sw=1.8, dash=None):
    """A straight Rough.js shaft with a two-stroke head.

    A dash pattern applies to the shaft alone, so a dotted arrow keeps a solid
    head, the way Excalidraw draws one.
    """
    ang = math.atan2(y1 - y0, x1 - x0)
    d = [dline(x0, y0, x1, y1)]
    for s in (+1, -1):
        a = ang + s * 0.44
        hl = 13
        d.append(dline(x1, y1, x1 - math.cos(a) * hl, y1 - math.sin(a) * hl))
    if dash:
        return path(d[0], sw, dash=dash) + path(" ".join(d[1:]), sw)
    return path(" ".join(d), sw)

def text(x, y, s, size=16, anchor="start"):
    return (f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" text-anchor="{anchor}" '
            f'font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">{s}</text>')

def label(x0, y0, x1, y1, s, size=15, off=16):
    """A label that follows a connector, offset to one side of it.

    A positive offset puts the text on the upper side of a line drawn left to
    right, a negative offset on the lower side. The text turns with the line,
    so a label on a diagonal connector never crosses the ink it names.
    """
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1.0
    px, py = mx + (dy / ln) * off, my + (-dx / ln) * off
    ang = math.degrees(math.atan2(dy, dx))
    return (f'<text x="{f(px)}" y="{f(py)}" font-size="{size}" text-anchor="middle" '
            f'transform="rotate({f(ang)},{f(px)},{f(py)})" '
            f'font-family="var(--dg-font-hand)" fill="currentColor" stroke="none" '
            f'opacity="0.85">{s}</text>')

def frame(w, h, pad=9):
    """The panel border. The diagrams draw no border, so it is empty."""
    return ""

def _arc_pts(cx, cy, rx, ry, a0, a1, n=12):
    """Jittered points along one arc of an ellipse."""
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((cx + rx * math.cos(a) + _off_sym(1.0, 1.0),
                    cy + ry * math.sin(a) + _off_sym(1.0, 1.0)))
    return pts

def cylinder(cx, top, bottom, rx, ry, sw=1.8):
    """The drum that a diagram draws a database with.

    A full ellipse for the top cap, two walls, and the front half of the bottom
    cap. The hidden half of the bottom cap stays out, so the drum reads as a
    solid body. Every stroke is drawn twice, the way Excalidraw draws one.
    """
    p = [ellipse(cx, top, rx, ry, sw)]
    p.append(path(dline(cx - rx, top, cx - rx, bottom)
                  + " " + dline(cx + rx, top, cx + rx, bottom), sw))
    d = []
    for _ in range(2):
        pts = _arc_pts(cx, bottom, rx, ry, 0.0, math.pi)
        d.append(_curve([pts[0]] + pts + [pts[-1]]))
    p.append(path(" ".join(d), sw))
    return "".join(p)

def sarrow(x0, y0, x1, y1, sw=1.8, dash=None):
    """A straight arrow whose shaft is drawn once.

    Excalidraw draws every edge twice, but over a long span the two passes
    drift apart and the line reads as blurred. A long connector draws its
    shaft once, and keeps the two-stroke head.
    """
    ang = math.atan2(y1 - y0, x1 - x0)
    head = []
    for s in (+1, -1):
        a = ang + s * 0.44
        head.append(dline(x1, y1, x1 - math.cos(a) * 13, y1 - math.sin(a) * 13))
    shaft = rline(x0, y0, x1, y1)
    if dash:
        return path(shaft, sw, dash=dash) + path(" ".join(head), sw)
    return path(shaft + " " + " ".join(head), sw)

def srect(x, y, w, h, sw=1.8, op=1.0, dash=None):
    """A rectangle whose four edges are drawn once.

    A tall or wide dotted box drawn twice shows two dot rows that read as
    blur, so a band or a panel border draws its edges once.
    """
    d = " ".join([
        rline(x, y, x + w, y),
        rline(x + w, y, x + w, y + h),
        rline(x + w, y + h, x, y + h),
        rline(x, y + h, x, y),
    ])
    return path(d, sw, op, dash)
