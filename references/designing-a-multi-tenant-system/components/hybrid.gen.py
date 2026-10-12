# Generates the Hybrid diagram component (single source of truth).
#
# The strokes come from rough.py, the same Rough.js algorithm the other diagrams
# in this folder draw with.
#
# Two deployments of the same three services. The shared deployment serves
# tenants 1, 2 and 3, and each service in it uses a different model:
# Service 1 is a single server on a single database, Service 2 has scaled
# servers on sharded databases, and Service 3 adds dedicated servers and a
# dedicated database for tenant 1. The Enterprise tenant has a dedicated deployment, where
# all three services share one database.
import io, os

from rough import *

W, H = 1080, 1050

X_TEN, W_TEN, H_TEN = 15, 170, 130
X_USR, W_USR, H_USR = 45, 110, 34
X_DEP = 200  # the left edge of the deployment frames
X_LB, W_LB, H_LB = 225, 110, 80
X_GRP = 370
X_SRV, W_SRV, H_SRV = 470, 140, 44
PG_CX, PG_RX, PG_RY = 880, 110, 14
H_PG = 70

# Each service group in the shared deployment: its name, its top and bottom,
# its servers (name, centre, tag), its instances (name, tag, top), and the
# instances that each server connects to.
SERVICES = (
    ("Service 1: single server, single database", 60, 180,
     (("Server", 125, None),),
     (("Database", None, 95),),
     ((0,),)),
    ("Service 2: scaled servers, scaled database", 210, 450,
     (("Server 1", 270, None), ("Server 2", 330, None), ("Server 3", 390, None)),
     (("Database 1", None, 250), ("Database 2", None, 360)),
     ((0, 1), (0, 1), (0, 1))),
    ("Service 3: scaled and dedicated", 480, 740,
     (("Server 1", 540, None), ("Server 2", 600, None), ("Server 3", 680, "tenant 1")),
     (("Database 1", "shared", 520), ("Database 2", "dedicated to tenant 1", 640)),
     ((0,), (0,), (1,))),
)

# The Enterprise tenant's dedicated deployment: one server for each service, one database.
DED_TOP, DED_BOT, DED_CY = 790, 1030, 920
DED_SERVERS = (("Service 1", 860), ("Service 2", 920), ("Service 3", 980))

def instance(name, tag, top):
    p = cylinder(PG_CX, top, top + H_PG, PG_RX, PG_RY)
    if tag:
        return p + text(PG_CX, top + 40, name, 16, "middle") + text(PG_CX, top + 61, tag, 13, "middle")
    return p + text(PG_CX, top + 48, name, 16, "middle")

def server(name, cy, x=X_SRV, w=W_SRV):
    return (rect(x, cy - H_SRV / 2, w, H_SRV)
            + text(x + w / 2, cy + 6, name, 15, "middle"))

# Each tenant: its name, its top, and its users. The users send the requests.
SHARED_TENANTS = (("Tenant 1", 175, ("User 1", "User 2")),
                  ("Tenant 2", 335, ("User 3", "User 4")),
                  ("Tenant 3", 495, ("User 5", "User 6")))
DED_TENANTS = (("Enterprise Tenant", 855, ("User 7", "User 8")),)

def entry(cy, tenants):
    p = (rect(X_LB, cy - H_LB / 2, W_LB, H_LB)
         + text(X_LB + W_LB / 2, cy - 6, "Load", 16, "middle")
         + text(X_LB + W_LB / 2, cy + 18, "balancer", 16, "middle"))
    for name, top, users in tenants:
        p += (rect(X_TEN, top, W_TEN, H_TEN, sw=1.8, op=0.5, dash="1 8")
              + text(X_TEN + 14, top + 24, name, 15))
        for i, user in enumerate(users):
            uy = top + 56 + 44 * i
            p += (rect(X_USR, uy - H_USR / 2, W_USR, H_USR)
                  + text(X_USR + W_USR / 2, uy + 5, user, 14, "middle")
                  + arrow(X_USR + W_USR + 4, uy, X_LB - 8, cy, sw=1.2))
    return p

def diagram():
    p = [frame(W, H)]
    # The shared deployment.
    p.append(rect(X_DEP, 20, W - 20 - X_DEP, 740, sw=1.8, op=0.5, dash="1 8")
             + text(X_DEP + 16, 46, "shared deployment", 15))
    cy = 400
    p.append(entry(cy, SHARED_TENANTS))
    for name, top, bot, servers, instances, links in SERVICES:
        p.append(rect(X_GRP, top, W - 40 - X_GRP, bot - top, sw=1.8, op=0.5, dash="1 8")
                 + text(X_GRP + 14, top + 24, name, 14))
        p.append(arrow(X_LB + W_LB + 4, cy, X_GRP - 8, (top + bot) / 2))
        for i in instances:
            p.append(instance(*i))
        for (sname, sy, tag), link in zip(servers, links):
            p.append(server(sname, sy))
            if tag:
                p.append(text(X_SRV - 12, sy + 5, tag, 13, "end"))
            for j in link:
                itop = instances[j][2]
                p.append(arrow(X_SRV + W_SRV + 4, sy, PG_CX - PG_RX - 8, itop + H_PG / 2, sw=1.2))
    # The Enterprise tenant's dedicated deployment.
    p.append(rect(X_DEP, DED_TOP, W - 20 - X_DEP, DED_BOT - DED_TOP, sw=1.8, op=0.5, dash="1 8")
             + text(X_DEP + 16, DED_TOP + 26, "enterprise tenant deployment", 15))
    p.append(entry(DED_CY, DED_TENANTS))
    p.append(instance("Database", "shared by all 3 services", DED_CY - H_PG / 2))
    for sname, sy in DED_SERVERS:
        p.append(server(sname, sy))
        p.append(arrow(X_LB + W_LB + 4, DED_CY, X_SRV - 8, sy))
        p.append(arrow(X_SRV + W_SRV + 4, sy, PG_CX - PG_RX - 8, DED_CY, sw=1.2))
    return "".join(p)

ALT = ("Two deployments of the same three services. The shared deployment serves tenants "
       "1, 2 and 3. Each of these tenants has two users, and the users' requests reach its Load balancer, which sends them to three services. "
       "Service 1 is a single server on a single Database. Service 2 has Server 1, Server 2 "
       "and Server 3, and each connects to Database 1 and Database 2. Service 3 has Server 1 "
       "and Server 2 on a shared Database 1, and Server 3 for tenant 1 on Database 2, which "
       "is dedicated to tenant 1. The Enterprise tenant has two users. Their requests reach the Enterprise tenant's deployment, which has its own Load balancer and one "
       "server each for Service 1, Service 2 and Service 3. All three connect to one "
       "Database that the three services share.")

FONT_B64 = io.open(os.path.join(HERE, "comicshanns.b64"), encoding="utf-8").read().strip()

COMPONENT = f'''<!--
  hybrid — each service uses the model that fits its scale and usage.
  SINGLE SOURCE: references/designing-a-multi-tenant-system/components/hybrid.gen.py
  Do not edit the copies. Edit the generator, run it, then run:
    python3 references/designing-a-multi-tenant-system/components/sync.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-hybrid">
<style>
@font-face{{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");
}}
.diagram-hybrid{{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}}
.diagram-hybrid svg{{display:block;width:100%;height:auto;color:inherit}}
</style>
<svg viewBox="0 0 {W} {H}" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="{ALT}">
  {diagram()}
</svg>
</figure>
'''

out = os.path.join(HERE, "hybrid.html")
io.open(out, "w", encoding="utf-8").write(COMPONENT)
print("wrote", out, len(COMPONENT), "bytes")
