# max_connections by memory size: research notes

Working notes for the section "Starting with a Simple Monolith" in
`src/content/articles/designing-a-multi-tenant-system.md`. The sibling note
`single-instance-limits-research.md` (§1) concludes that Postgres connections are the first wall for a
database-per-tenant design. This note answers the follow-up question:

> What is a sensible `max_connections` value for a PostgreSQL instance at each memory size?

Sources are primary only: the PostgreSQL docs (current, 18), posts by PostgreSQL core developer Andres
Freund, and the managed-service vendors' own docs. The PostgreSQL wiki is cited once and marked as
community content. No PostgreSQL source code is cited here, so no `PG@` pinned links are needed.

---

## Short answer

- **No official "optimal" value exists.** The PostgreSQL docs give only the default ("typically 100")
  and warn that raising it costs shared memory. No PostgreSQL doc, and none of the three vendors, publishes
  a recommended `max_connections` for a given memory size. Andres Freund's benchmarks show that the
  answer depends on workload and latency, not on memory alone.
- **The practical reference is what managed services set by default.** All three scale it with memory.
  RDS uses `LEAST({DBInstanceClassMemory/9531392}, 5000)`, about one connection per 9.1 MiB of usable
  memory. Azure's table is close to that and also caps at 5,000. Cloud SQL is far more conservative and
  tops out at 1,000.
- **Memory is not what limits useful connections.** An idle connection costs about 1.3 MiB with huge
  pages and about 7.6 MiB without them (Freund's measurement). The real limit is CPU. Throughput of
  *active* connections peaks at a small multiple of the core count: in Freund's benchmark, around 48
  clients on a 20-core machine. Many idle connections also slow down the active ones.
- **Do not read the table as "raise it freely".** Azure explicitly advises against going above its
  default, and suggests a PgBouncer pool of 2 to 5 × vCores instead. That figure is the only number in a
  primary source that resembles a "recommended" value, and it is a pool size, not a `max_connections`
  value.

---

## The table

Memory is in GiB. All values are default `max_connections` (total, including reserved slots).

| Memory | AWS RDS (formula, upper bound) | Azure Flexible Server (SKU) | Google Cloud SQL | Note |
| --- | --- | --- | --- | --- |
| 1 GiB | ≤ 112 | No 1 GiB SKU | No 1 GiB tier (0.6 GB → 25, 1.7 GB → 50) | Smallest sizes: OS overhead eats most of the memory |
| 2 GiB | ≤ 225 | 50 (B1ms, 1 vCore) | No 2 GiB tier (1.7 GB → 50) | Azure reserves 15, leaving 35 for users |
| 4 GiB | ≤ 450 | 429 (B2s, 2 vCores) | 100 (3.75 to < 6 GB) | |
| 8 GiB | ≤ 901 | 859 (B2ms / D2s, 2 vCores) | 400 (7.5 to < 15 GB) | Typical "first production" size |
| 16 GiB | ≤ 1,802 | 1,718 (D4s 4 vCores / E2s 2 vCores) | 500 (15 to < 30 GB) | |
| 32 GiB | ≤ 3,604 | 3,437 (D8s 8 vCores / E4s 4 vCores) | 600 (30 to < 60 GB) | |
| 64 GiB | 5,000 (cap) | 5,000 (cap) | 800 (60 to < 120 GB) | Both RDS and Azure hit their 5,000 cap |
| 128 GiB | 5,000 (cap) | 5,000 (cap) | 1,000 (≥ 120 GB) | |
| 256 GiB | 5,000 (cap) | 5,000 (cap) | 1,000 (≥ 120 GB) | More memory buys no more default slots |

How to read each column:

- **RDS:** my arithmetic, `floor(GiB × 1,073,741,824 / 9,531,392)`, capped at 5,000. It is an **upper
  bound**. `DBInstanceClassMemory` is the instance's memory *minus* what the OS and RDS management
  processes reserve, so the real default is lower. AWS's own MySQL example on an 8 GiB class shows the
  effect: 683 from the nominal memory, "approximately 630" after the reservation (about 8% lower). AWS
  gives no PostgreSQL example, so the exact PostgreSQL value per class is unconfirmed. Check it with
  `SHOW max_connections;`.
- **Azure:** copied from the published per-SKU table. Azure reserves 15 of these slots, so user
  connections are the value minus 15. Burstable SKUs (B-series) do not get the built-in PgBouncer.
- **Cloud SQL:** copied from the published table. The table is in "GB", by memory of the largest instance
  in the replication chain. The binary sizes in the first column map into these buckets (4 GiB = 4.29 GB,
  8 GiB = 8.59 GB, and so on). Cloud SQL's shared-core machines (about 0.6 GB and 1.7 GB) are the only
  tiers below 3.75 GB, so 1 GiB and 2 GiB have no exact row.

**A recommended practical value:** no primary source gives one per memory size, so the table has no such
column. The closest is Azure's guidance for a PgBouncer pool of "2 to 5" × vCores (§4), which depends on
CPU, not memory. For Azure's General Purpose D-series (4 GiB per vCore) that is 4 to 10 pooled connections
at 8 GiB, 16 to 40 at 32 GiB and 128 to 320 at 256 GiB (my arithmetic).

---

## 1. What PostgreSQL itself says

**The default and its cost.** `max_connections` "Determines the maximum number of concurrent connections
to the database server. The default is typically 100 connections ... This parameter can only be set at
server start." Raising it allocates more memory up front: "PostgreSQL sizes certain resources based
directly on the value of max_connections. Increasing its value leads to higher allocation of those
resources, including shared memory."
<https://www.postgresql.org/docs/current/runtime-config-connection.html#GUC-MAX-CONNECTIONS>. The docs do
not say how much shared memory each slot costs. (Unconfirmed: I found no doc figure for the per-slot
shared-memory size.)

**The kernel side.** With System V semaphores, "PostgreSQL uses one semaphore per allowed connection
(max_connections) ... in sets of 16."
<https://www.postgresql.org/docs/current/kernel-resources.html>. The same chapter warns that on Linux "the
kernel might terminate the PostgreSQL postmaster ... if the memory demands of either PostgreSQL or another
process cause the system to run out of virtual memory", and recommends strict overcommit
(`vm.overcommit_memory=2`). Too many busy connections on too little memory therefore end in the OOM killer,
not in a polite error.
<https://www.postgresql.org/docs/current/kernel-resources.html#LINUX-MEMORY-OVERCOMMIT>

**No recommended value.** The docs give no rule that ties `max_connections` to RAM. The memory guidance
they do give is for `shared_buffers`: "a reasonable starting value for shared_buffers is 25% of the memory
in your system", and "it is unlikely that an allocation of more than 40% of RAM to shared_buffers will
work better than a smaller amount."
<https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-SHARED-BUFFERS>. Per-connection
memory has to fit into what is left after that.

---

## 2. Managed-service defaults (primary sources)

**AWS RDS for PostgreSQL.** Default `LEAST({DBInstanceClassMemory/9531392}, 5000)`, allowed range
6–262143. "Database connections consume memory. Setting one of these parameters too high can cause a low
memory condition that might cause a DB instance to be placed in the incompatible-parameters status." AWS
recommends RDS Proxy "If your applications frequently open and close connections, or keep a large number
of long-lived connections open".
<https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html#RDS_Limits.MaxConnections>

`DBInstanceClassMemory` "Returns an integer for the number of bytes of memory available to the database
process ... the calculation subtracts memory reserved for the operating system and the RDS processes that
manage the instance. Therefore, the number is always somewhat lower than the memory figures shown in the
instance class tables ... The exact value depends on a combination of factors." Division truncates
("Decimals in the quotient are truncated, not rounded").
<https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ParamValuesRef.html#USER_FormulaVariables>

If `max_connections` or `shared_buffers` is set too high, "your RDS for PostgreSQL DB instance won't
start", with `FATAL: could not map anonymous shared memory`.
<https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.Parameters.html>

**Azure Database for PostgreSQL flexible server.** A published table of "*default* maximum number of
connections for each pricing tier and vCore configuration" (values in the table above), capped at 5,000.
"An Azure Database for PostgreSQL flexible server reserves 15 connections for physical replication and
monitoring." The default is computed at provisioning and does not change if you later change the SKU, so
Azure says to "adjust the value for the max_connections parameter according to the values in the
preceding table."
<https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-limits>

An observation, not stated by Azure: Azure's values track the RDS formula closely (859 at 8 GiB vs. RDS's
≤ 901; 1,718 at 16 GiB vs. ≤ 1,802), so both behave like "about one connection per 9–10 MB of memory".
B1ms (2 GiB, 50) is the exception.

**Google Cloud SQL for PostgreSQL.** "The default value depends on the amount of memory of the largest
instance in the chain of primaries": tiny (~0.5 GB) 25, small (~1.7 GB) 50, 3.75 to < 6 GB 100, 6 to
< 7.5 GB 200, 7.5 to < 15 GB 400, 15 to < 30 GB 500, 30 to < 60 GB 600, 60 to < 120 GB 800, ≥ 120 GB
1,000. Minimum 14; the sum of `max_connections`, `autovacuum_max_workers` and `max_worker_processes` cannot
exceed 262142. Changing it requires a restart.
<https://docs.cloud.google.com/sql/docs/postgres/flags>

---

## 3. The memory math

**An idle connection: about 1.3 MiB with huge pages, about 7.6 MiB without.** Andres Freund, "Measuring
the memory overhead of a Postgres connection" (7 Oct 2020). Measuring with `ps` RSS overstates it, because
RSS charges every backend for the shared buffers it has touched. Freund instead adds `Pss_Anon` (private
memory) and `VmPTE` (page tables): a connection "running a very simplistic read-only OLTP workload ... has
an overhead of about 7.6MiB with huge_pages=off and of 1.3MiB huge_pages=on". Most of the difference is
page tables: `VmPTE` was 6,480 kB without huge pages and 132 kB with them (test cluster:
`shared_buffers` = 16 GB). His conclusion: "the overhead of a connection is less than 2MiB."
<https://blog.anarazel.de/2020/10/07/measuring-the-memory-overhead-of-a-postgres-connection/>.
He repeats it in the connection-scalability post: "with the right configuration—most importantly, using
huge_pages—the memory overhead of each connection is below 2 MiB", and "memory is not the primary issue
around connection scalability."
<https://techcommunity.microsoft.com/blog/adforpostgresql/analyzing-the-limits-of-connection-scalability-in-postgres/1757266>

The page-table cost scales with how much shared memory a backend maps, so the 7.6 MiB figure depends on
the 16 GB `shared_buffers` used in the test. It is not a constant. (My reading of the numbers, not a
stated result.) `huge_pages` defaults to `try` in PostgreSQL
(<https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-HUGE-PAGES>), so whether you
pay 1.3 or 7.6 MiB depends on whether the OS has huge pages set up. Whether each managed service turns
huge pages on for PostgreSQL is unconfirmed here.

**An idle connection grows over time.** Catalog and relation caches are per backend. In Freund's
scalability post, a backend's `CacheMemoryContext` grew from 512 kB to 593 MB after touching 100k tables,
a problem with "long-lived connections combined with schema-based multi-tenancy" (same post as above).

**An active connection: work_mem × operations, with hash operations doubled.**

- `work_mem` (default 4 MB) is per operation, not per query: "a complex query might perform several sort
  and hash operations at the same time, with each operation generally being allowed to use as much memory
  as this value specifies ... Also, several running sessions could be doing such operations concurrently.
  Therefore, the total memory used could be many times the value of work_mem."
  <https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-WORK-MEM>
- Hash operations get more: "The final limit is determined by multiplying work_mem by
  hash_mem_multiplier. The default value is 2.0".
  <https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-HASH-MEM-MULTIPLIER>
- Sessions using temporary tables also get `temp_buffers` (default 8 MB per session), and maintenance
  (`maintenance_work_mem`, default 64 MB) applies per `VACUUM`/`CREATE INDEX` and per autovacuum worker.
  Same page.
- Freund: "a query can end up requiring work_mem several times over ... With larger work_mem settings,
  practically required for analytics workloads, one can't reasonably use a huge number of concurrent
  connections and expect to never hit memory exhaustion related issues (i.e. errors or the OOM killer)."
  (scalability post above).

A rough upper bound per active query, my arithmetic with defaults: a query with two sorts and one hash
join can use 4 + 4 + (4 × 2) = 16 MB beyond the idle overhead. There is no fixed ceiling per connection.

**Worked example, my arithmetic.** An 8 GiB instance with 25% (2 GiB) in `shared_buffers` and the RDS
default of about 900 connections:

| Scenario | Per connection | × 900 | Fits in the ~6 GiB left? |
| --- | --- | --- | --- |
| All idle, huge pages on | 1.3 MiB | ~1.1 GiB | Yes |
| All idle, huge pages off | 7.6 MiB | ~6.7 GiB | No (and 7.6 MiB was measured with a larger `shared_buffers`) |
| All active, 16 MB of work_mem each | ~17 MiB | ~15 GiB | No |

The managed defaults are sized so that most connections are idle at any one time. They do not leave room
for every slot to be busy with sorts or hashes at once.

---

## 4. More connections is not more throughput

**Active-connection throughput peaks near a small multiple of CPU cores.** Freund's pgbench run
(memory-resident, read-only, on "20/40 CPU cores/threads"): "The non-delayed pgbench peaks around 48
clients, the delayed run around 3000 connections." With a 1 ms network delay and 1 ms processing delay,
each connection sits idle most of the time, so more of them are needed to keep the CPU busy. Moving from
local to a 10GbE network "moves the peak from around 48 connections closer to 500 connections."
(scalability post above). So the number of connections that do useful work at once is close to the core
count. The number of open connections needed to keep that many busy depends on how idle each one is.

**Idle connections cost the active ones.** "Postgres does not scale well to having a large number of
established connections, even if nearly all connections are idle", and "the achievable throughput of
active connections decreases significantly when the number of idle connections increases." Freund traced
the cause to `GetSnapshotData()` (same post). PostgreSQL 14 improved this: "Improve the speed of computing
MVCC visibility snapshots on systems with many CPUs and high session counts ... This also improves
performance when there are many idle sessions." <https://www.postgresql.org/docs/release/14.0/>

**Setting max_connections high, by itself, is cheap. Using the slots is not.** Freund: "Setting
max_connections to a very high value alone only leads at best (worst?) to a very small slowdown in itself,
and wastes some memory", with "no measurable performance difference for a read-only pgbench between
max_connections=100 and ... max_connections=100000 (for the same pgbench client count, 48 in this case)."
(same post). The cost comes from the connections actually opened.

**The vendors agree.** Azure: "Although it's possible to increase the value of max_connections beyond the
default setting, we advise against it ... Although a higher value for max_connections might be acceptable
when most connections are idle, it can lead to significant performance problems after they become active."
Instead: "use PgBouncer ... in transaction mode. To start, we recommend that you use conservative values by
multiplying the vCores within the range of 2 to 5."
<https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-limits>. AWS points to RDS
Proxy for the same problem (§2).

**The PostgreSQL wiki's rule of thumb (community content, not official docs).** "Number Of Database
Connections" gives `((core_count * 2) + effective_spindle_count)` as a starting point for *active*
connections, where "Core count should not include HT threads" and spindle count "is zero if the active data
set is fully cached". It warns that the formula predates 9.2 and that "There hasn't been any analysis so
far regarding how well the formula works with SSDs." Last edited 14 March 2014.
<https://wiki.postgresql.org/wiki/Number_Of_Database_Connections>. Azure's limits page links to it.
Freund's 48-client peak on 20 cores roughly agrees with it (about 2.4 × cores).

---

## 5. What this means for the article

- **Use the managed defaults as the reference numbers.** For an 8 GiB instance that is roughly 850–900
  (RDS, Azure) or 400 (Cloud SQL). A database-per-tenant design with a pool of 10 per tenant database per
  app instance uses that up at about 85–90 tenant databases on one app instance (see the sibling note's
  formula).
- **More memory buys slots only up to 64 GiB.** RDS and Azure both stop at 5,000; Cloud SQL stops at
  1,000 from 120 GB. Scaling the instance up is not a long-term fix for connection count.
- **The number worth tuning is active connections, not max_connections.** The useful count is a small
  multiple of vCores. A pooler (PgBouncer, RDS Proxy) holds that many server connections and lets many
  more clients share them.

**What no source gives:** an "optimal" `max_connections` per memory size. Every figure in the table is a
vendor default, and the RDS column is an upper bound from a formula whose exact input AWS does not publish.

---

## Sources

PostgreSQL
- max_connections, reserved connections: <https://www.postgresql.org/docs/current/runtime-config-connection.html>
- shared_buffers, work_mem, hash_mem_multiplier, huge_pages, temp_buffers, maintenance_work_mem:
  <https://www.postgresql.org/docs/current/runtime-config-resource.html>
- Kernel resources (semaphores, Linux overcommit): <https://www.postgresql.org/docs/current/kernel-resources.html>
- PostgreSQL 14 release notes (snapshot scalability): <https://www.postgresql.org/docs/release/14.0/>
- PostgreSQL wiki (community), "Number Of Database Connections":
  <https://wiki.postgresql.org/wiki/Number_Of_Database_Connections>

Core developer
- Andres Freund, "Measuring the memory overhead of a Postgres connection" (7 Oct 2020):
  <https://blog.anarazel.de/2020/10/07/measuring-the-memory-overhead-of-a-postgres-connection/>
- Andres Freund, "Analyzing the Limits of Connection Scalability in Postgres" (8 Oct 2020):
  <https://techcommunity.microsoft.com/blog/adforpostgresql/analyzing-the-limits-of-connection-scalability-in-postgres/1757266>

Managed PostgreSQL
- AWS RDS max_connections defaults: <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html>
- AWS RDS DBInstanceClassMemory definition: <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ParamValuesRef.html>
- AWS RDS for PostgreSQL parameters: <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.Parameters.html>
- Azure flexible server limits: <https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-limits>
- Cloud SQL flags (max_connections defaults): <https://docs.cloud.google.com/sql/docs/postgres/flags>
