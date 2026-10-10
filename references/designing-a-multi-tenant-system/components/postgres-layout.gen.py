# Generates the Postgres data directory diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# On the left, the server. On the right, the data directory of one Postgres
# instance: global/ and pg_wal/ along the top, shared by every database, and
# base/ below, with one directory per database, named by the database OID.
# Each database directory holds the files of its own tables: the data file,
# named by the table's filenode number, and its free space map (_fsm) and
# visibility map (_vm). The server opens one connection to each database.
#
# The OIDs are examples. The OID counter is cluster wide, so no two databases
# and no two tables in this drawing share a number.
import io, os

from rough import *

W, H = 1080, 660

SRV_X, SRV_W, SRV_CY, SRV_H = 40, 150, 380, 84

INST = (320, 30, 730, 595)         # the data directory: x, y, w, h
TOP_Y, TOP_H = 92, 70              # global/ and pg_wal/
BASE = (345, 190, 680, 415)        # base/: x, y, w, h

DB_X, DB_W, DB_H = 370, 630, 106
DB_YS = (232, 358, 484)
FILE_X0, FILE_W, FILE_H, FILE_GAP = 560, 112, 36, 14

DBS = (                            # (oid, name, table file, table)
    ("16384/", "common_db", "16390", "users"),
    ("16400/", "tenant_1_db", "16410", "resources"),
    ("16420/", "tenant_2_db", "16430", "resources"),
)

def dir_box(x, y, w, h, title, note, size=17):
    return (rect(x, y, w, h) + text(x + 18, y + 30, title, size)
            + text(x + 18, y + 54, note, 13))

def database(y, oid, name, node, table):
    p = [srect(DB_X, y, DB_W, DB_H)]
    p.append(text(DB_X + 22, y + 46, oid, 18))
    p.append(text(DB_X + 22, y + 72, name, 15))
    fy = y + 22
    for i, s in enumerate((node, node + "_fsm", node + "_vm")):
        fx = FILE_X0 + i * (FILE_W + FILE_GAP)
        p.append(rect(fx, fy, FILE_W, FILE_H, sw=1.5))
        p.append(text(fx + FILE_W / 2, fy + 24, s, 14, "middle"))
    p.append(text(FILE_X0 + 3 * (FILE_W + FILE_GAP) + 6, fy + 24, "...", 16))
    p.append(text(FILE_X0, y + DB_H - 16, f"the {table} table: data, free space map, visibility map", 13))
    return "".join(p)

def diagram():
    p = [frame(W, H)]
    p.append(rect(SRV_X, SRV_CY - SRV_H / 2, SRV_W, SRV_H)
             + text(SRV_X + SRV_W / 2, SRV_CY + 6, "Server", 18, "middle"))
    ix, iy, iw, ih = INST
    p.append(srect(ix, iy, iw, ih, sw=1.8, op=0.5, dash="1 8"))
    # Shared by every database in the instance.
    p.append(dir_box(345, TOP_Y, 320, TOP_H, "global/", "pg_database, pg_authid, ..."))
    p.append(dir_box(690, TOP_Y, 335, TOP_H, "pg_wal/", "one WAL for every database"))
    bx, by, bw, bh = BASE
    p.append(srect(bx, by, bw, bh, sw=1.6, op=0.7))
    p.append(text(bx + 22, by + 30, "base/", 17))
    for y, (oid, name, node, table) in zip(DB_YS, DBS):
        p.append(database(y, oid, name, node, table))
    # One connection per database.
    for i, y in enumerate(DB_YS):
        sy = SRV_CY - 24 + i * 24
        ey = y + DB_H / 2
        p.append(sarrow(SRV_X + SRV_W + 4, sy, DB_X - 8, ey))
        # The label rides the first two thirds of the shaft, clear of the dotted border.
        x0, x1 = SRV_X + SRV_W + 4, DB_X - 8
        p.append(label(x0, sy, x0 + (x1 - x0) * 0.66, sy + (ey - sy) * 0.66,
                       f"connection {i + 1}", size=13, off=11))
    return "".join(p)

ALT = ("The data directory of one Postgres instance. Along the top, global/ holds the cluster wide "
       "tables such as pg_database and pg_authid, and pg_wal/ holds one WAL for every database. "
       "Below, base/ holds one directory per database, named by its OID: 16384/ for common_db, "
       "16400/ for tenant_1_db and 16420/ for tenant_2_db. Each one holds its own table files: "
       "the data file named by the table filenode, and its _fsm and _vm files. The Server on the "
       "left opens one connection to each database.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  postgres-layout — one Postgres data directory, one directory per database, one connection per database.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/postgres-layout.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-postgres-layout">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-postgres-layout{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-postgres-layout svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "postgres-layout.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
