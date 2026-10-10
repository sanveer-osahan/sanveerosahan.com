# Generates the Slack / Google Workspace component from the presentation.
#
# The presentation is the source of the two panels. This script lifts the panel
# markup, the brand sprite and the panel CSS out of it, scopes every rule under
# .diagram-worked, and writes a self-contained block the article can hold. The
# panels keep the look they have in the presentation.
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PRES = os.path.join(HERE, "..", "presentation.html")

src = io.open(PRES, encoding="utf-8").read()

# --- markup ---------------------------------------------------------------

def block(start, tag="div"):
    """The balanced element that begins at the given opening tag."""
    i = src.index(start)
    depth, j = 0, i
    for m in re.finditer(r"<(/?)%s\b" % tag, src[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            j = i + m.end()
            break
    return src[i:src.index(">", j) + 1]

sprite = block('<svg class="sprite"', "svg")
panel_slack = block('<div class="panel slack">')
panel_gws = block('<div class="panel gws">')

# One page may hold this component and the presentation's own sprite, so every
# id in the copy carries a prefix.
ids = set(re.findall(r'\sid="([^"]+)"', sprite))
for i in sorted(ids, key=len, reverse=True):
    sprite = sprite.replace('id="%s"' % i, 'id="we-%s"' % i)
    sprite = sprite.replace('url(#%s)' % i, 'url(#we-%s)' % i)
    sprite = sprite.replace('xlink:href="#%s"' % i, 'xlink:href="#we-%s"' % i)
markup = (sprite + panel_slack + panel_gws).replace('href="#mark-', 'href="#we-mark-')
panel_slack = panel_slack.replace('href="#mark-', 'href="#we-mark-')
panel_gws = panel_gws.replace('href="#mark-', 'href="#we-mark-')
sprite = sprite.replace('href="#we-we-', 'href="#we-')

# --- css ------------------------------------------------------------------

css = src[src.index("<style>", src.index("</title>")) + len("<style>"):]
css = css[:css.index("</style>")]

DROP = {"body", ".page", "h1", "p", "em", ".eyebrow", "section", "*", "img",
        "[hidden]", ".topbar", ".theme-switch", ".theme-switch button",
        ".theme-switch button:hover", ".theme-switch button[aria-pressed=\"true\"]",
        ".theme-switch button:focus-visible", ".diagram-tenancy"}

def scope_one(sel):
    sel = sel.strip()
    if sel.startswith(".diagram-tenancy"):
        return None
    if sel == ":root":
        return ".diagram-worked"
    for root in (':root:not([data-theme="light"])', ':root[data-theme="dark"]'):
        if sel.startswith(root):
            rest = sel[len(root):].strip()
            return f"{root} .diagram-worked" + (f" {rest}" if rest else "")
    if sel in DROP:
        return None
    return ".diagram-worked " + sel

def scope(chunk):
    out, i = [], 0
    while i < len(chunk):
        b = chunk.find("{", i)
        if b < 0:
            break
        sel = chunk[i:b].strip()
        if sel.startswith("@media"):
            depth, j = 0, b
            while True:
                if chunk[j] == "{":
                    depth += 1
                elif chunk[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = scope(chunk[b + 1:j])
            if inner.strip():
                out.append(sel + "{" + inner + "}")
            i = j + 1
            continue
        e = chunk.index("}", b)
        body = chunk[b + 1:e].strip()
        sels = [s for s in (scope_one(s) for s in sel.split(",")) if s]
        if sels and body:
            out.append(",".join(sels) + "{" + body + "}")
        i = e + 1
    return "".join(out)

css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
scoped = scope(css)

# Newsreader, Inter and JetBrains Mono are the three faces of the site. The
# rest are the faces the Slack and Google Workspace panels draw with.
FONTS = ("https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400"
         "&family=Inter:wght@400;500;600"
         "&family=JetBrains+Mono:wght@400;500"
         "&family=Lato:wght@400;700;900"
         "&family=Rubik:wght@400;500;600"
         "&family=Roboto:wght@300;400;500;700"
         "&family=Roboto+Mono:wght@400;500&display=swap")

COMPONENT = f'''<!--
  worked-examples — the Slack and Google Workspace panels, as the presentation draws them.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/presentation.html
  Do not edit this copy. Edit the presentation, then run:
    python3 references/designing-a-multi-tenant-system/components/worked-examples.gen.py
    python3 references/designing-a-multi-tenant-system/components/sync.py
-->
<figure class="diagram diagram-worked">
<style>
@import url("{FONTS}");
.diagram-worked{{margin:34px 0;display:flex;flex-direction:column;gap:28px;font-size:16px;line-height:1.55}}
.diagram-worked svg.sprite{{position:absolute;width:0;height:0;overflow:hidden}}
.diagram-worked .mark{{display:block;flex:none;width:auto;height:auto;margin:0}}
.diagram-worked .sec-head{{margin-bottom:20px}}
/* The article styles every h2 in the prose. These rules outrank it, so the
   brand mark and the name sit on one line the way the presentation draws them. */
.diagram-worked .sec-head .row{{display:flex;align-items:center;gap:12px}}
.diagram-worked .sec-head .row h2{{font-family:var(--font-display);letter-spacing:var(--display-tracking);font-size:clamp(22px,3vw,27px);line-height:1.2;color:var(--ink);margin:0;scroll-margin-top:0}}
{scoped}
</style>
{sprite}
{panel_slack}
{panel_gws}
</figure>
'''
COMPONENT = "\n".join(l for l in COMPONENT.split("\n") if l.strip()) + "\n"

out = os.path.join(HERE, "worked-examples.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
