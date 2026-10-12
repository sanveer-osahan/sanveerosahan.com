# Single-instance limits: research notes

Working notes for the section "Starting with a Simple Monolith" in
`src/content/articles/designing-a-multi-tenant-system.md`. The design: one application server (a monolith)
and one PostgreSQL instance. The instance holds `common_db` (Users, Workspaces, Memberships) plus one
database per tenant (`tenant_1_db`, `tenant_2_db`, ...). A PostgreSQL connection can reach only one
database (see `databases-per-instance-research.md`, §3), so the server keeps a connection pool per tenant
database. A request looks up the Membership in `common_db`, then queries the tenant's database.

The question, in the author's words: as tenants × users grow, which limit hits first, and why?

1. Compute (CPU/memory) on the application server
2. Number of connections Postgres can hold
3. Compute (CPU/memory/IO) on the database
4. Storage (the author believes this hits last)
5. Anything missed?

Sources are primary only: the PostgreSQL docs (current, 18) and source, posts by PostgreSQL core
developers, PgBouncer's docs, the managed-service vendors' own docs, and AWS/Azure SaaS guidance. Source
links below use the same pinned commit as the sibling note: `PG@` stands for
`https://github.com/postgres/postgres/blob/3c6135f839d03ef96a7313bca09ba4c1ec8dd161/`.

---

## Short answer

The ranked order for this design, with one line on why:

1. **Postgres connections hit first.** Every tenant database needs its own pool, so connections grow as
   app instances × tenant databases × pool size, against a server-wide `max_connections` that defaults to
   100 and that managed services cap by memory. This is a hard error (`FATAL: sorry, too many clients
   already`), and it arrives with tens of tenants, long before CPU or disk is busy.
2. **Database compute comes next.** All tenants share one CPU, one buffer cache (`shared_buffers`), one
   WAL and one disk. A heavy tenant slows everyone (noisy neighbor). Many open connections also cost DB
   throughput even when idle, so wall 1 feeds wall 2.
3. **App server compute is real but the cheapest to fix.** The app tier is stateless and scales out
   independently of the databases. The catch: each new app instance brings its own full set of per-tenant
   pools, so scaling the app tier makes wall 1 worse.
4. **Storage comes last.** The author is right. Managed PostgreSQL goes to 64 TiB per instance (RDS, Cloud
   SQL), and disk can be grown online. Storage turns into a problem through operations (backup and restore
   time, autovacuum), not through running out of bytes.
5. **What the question missed:** per-database operations that grow with tenant count (autovacuum visiting
   every database, wraparound freezing of idle tenants, schema migrations once per database, onboarding
   via `CREATE DATABASE`), whole-cluster backup and PITR, and the single instance being a single point of
   failure for every tenant.

The order of 2 and 3 is my reasoning, not a sourced ranking. On a single small app server, app CPU can
saturate first. No primary source ranks them. What the sources do support is that connections are a hard
cap that the per-database design multiplies, and that the usual fix for app CPU (more app instances)
multiplies it further.

---

## 1. Postgres connections (the first wall)

**The cap.** `max_connections` "Determines the maximum number of concurrent connections to the database
server. The default is typically 100 connections ... This parameter can only be set at server start."
Raising it costs memory up front: "PostgreSQL sizes certain resources based directly on the value of
max_connections. Increasing its value leads to higher allocation of those resources, including shared
memory." <https://www.postgresql.org/docs/current/runtime-config-connection.html#GUC-MAX-CONNECTIONS>.
Three of those slots are held back by default (`superuser_reserved_connections` "The default value is
three connections"; same page).

**Why each connection is expensive: one process per connection.** "PostgreSQL implements a 'process per
user' client/server model ... [the postmaster] spawns a new backend process every time a connection is
requested." <https://www.postgresql.org/docs/current/connect-estab.html>. Each backend then has its own
private memory for query work: `work_mem` (default 4 MB) applies per sort or hash operation, "a complex
query might perform several sort and hash operations at the same time ... Also, several running sessions
could be doing such operations concurrently. Therefore, the total memory used could be many times the
value of work_mem."
<https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-WORK-MEM>

**How much memory per connection, from a core developer.** Andres Freund (PostgreSQL committer, then at
Microsoft) measured it in "Analyzing the Limits of Connection Scalability in Postgres" (8 Oct 2020):
"with the right configuration—most importantly, using huge_pages—the memory overhead of each connection
is below 2 MiB", and concluded "memory is not the primary issue around connection scalability". The real
problem he found: "Postgres does not scale well to having a large number of established connections,
even if nearly all connections are idle", and "the achievable throughput of active connections decreases
significantly when the number of idle connections increases." The cause was snapshot computation, which
he fixed for PostgreSQL 14.
<https://techcommunity.microsoft.com/blog/adforpostgresql/analyzing-the-limits-of-connection-scalability-in-postgres/1757266>.
The PostgreSQL 14 release notes confirm it: "Improve the speed of computing MVCC visibility snapshots on
systems with many CPUs and high session counts (Andres Freund). This also improves performance when there
are many idle sessions." <https://www.postgresql.org/docs/release/14.0/>. Even after that fix the
vendors still treat connection count as a resource to ration (below).

**Managed-service defaults (the numbers you actually get).**

- **AWS RDS for PostgreSQL:** default `max_connections` is `LEAST({DBInstanceClassMemory/9531392}, 5000)`,
  allowed range 6–262143. "Database connections consume memory. Setting one of these parameters too high
  can cause a low memory condition." `DBInstanceClassMemory` is the instance's memory minus what the OS
  and RDS reserve. <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html#RDS_Limits.MaxConnections>.
  My arithmetic: an 8 GiB instance gives at most 8,589,934,592 / 9,531,392 ≈ 901, and less after the
  reservation.
- **Azure Database for PostgreSQL flexible server:** defaults by SKU, with 15 reserved, e.g. B1ms (2 GiB)
  50 total / 35 user; D2s (2 vCore, 8 GiB) 859 / 844; capped at 5,000. Azure advises against raising it:
  "As the number of connections increases, memory usage also rises ... a higher value for max_connections
  might be acceptable when most connections are idle, it can lead to significant performance problems
  after they become active", and "Each connection ... regardless of whether it's idle or active, consumes a
  significant amount of resources from your database." Over the cap you get `FATAL: sorry, too many
  clients already.` <https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-limits>
- **Google Cloud SQL for PostgreSQL:** default by memory, e.g. 25 (~0.5 GB), 50 (~1.7 GB), 100 (3.75 to
  < 6 GB), 400 (7.5 to < 15 GB), up to 1,000 (≥ 120 GB).
  <https://docs.cloud.google.com/sql/docs/postgres/flags>

**The multiplication in this design.** A pool cannot be shared across databases, because a connection is
bound to one database for life (sibling note, §3). Application pools also hold connections open while
idle: HikariCP, for example, defaults to `maximumPoolSize` 10 and `minimumIdle` "same as maximumPoolSize",
i.e. a fixed pool of 10 open connections. <https://github.com/brettwooldridge/HikariCP>. So the number of
server connections is roughly:

```
connections = app_instances × (tenant_databases + 1 for common_db) × pool_size
```

Worked example (my arithmetic, simple numbers):

| App instances | Tenant DBs | Pool size | Connections | Fits default 100? | Fits 8 GiB RDS (~900)? |
| --- | --- | --- | --- | --- | --- |
| 1 | 9 | 10 | 1 × 10 × 10 = 100 | Just (minus 3 reserved: no) | Yes |
| 1 | 50 | 10 | 1 × 51 × 10 = 510 | No | Yes |
| 2 | 50 | 10 | 2 × 51 × 10 = 1,020 | No | No |
| 3 | 100 | 10 | 3 × 101 × 10 = 3,030 | No | No |

With one shared database instead, the same 3 app instances would need 3 × 10 = 30 connections. The
database-per-tenant design turns the connection count from O(app instances) into O(app instances ×
tenants), which is why it is the first wall. It also arrives without any rise in users: 50 tenants with
one user each already need 510 connections.

**Does PgBouncer fix it? Less than usual.** PgBouncer's pools are per (user, database) pair:
`default_pool_size` is "The maximum number of server connections to allow per user/database pair"
(default 20), and a pool is "a specific database/user pair". The worst case it documents is
`max_client_conn + (max pool_size * total databases * total users)`.
<https://www.pgbouncer.org/config.html>. So PgBouncer still needs at least one server connection per
active tenant database. What it does help with:

- **It collapses app instances.** Many app instances share one PgBouncer pool per tenant database, so the
  `app_instances ×` factor goes away on the server side.
- **It shrinks idle pools.** `min_pool_size` defaults to 0 and `server_idle_timeout` (default 600 s)
  closes idle server connections (same page). Quiet tenants then hold zero or few server connections.
- **It caps the total.** `max_db_connections` caps server connections per database (default unlimited).
- **The cost:** to actually reduce server connections it must run in transaction mode (Andres Freund,
  post above: "To actually reduce the number of connections to the database server such poolers need to be
  used in transaction (or statement) pooling modes"). Transaction mode "breaks a few session-based features
  of PostgreSQL", including `SET/RESET`, `LISTEN`, `PREPARE / DEALLOCATE` and session-level advisory locks
  (PgBouncer marks these "Never" supported). <https://www.pgbouncer.org/features.html>. Azure recommends
  exactly this setup: "use PgBouncer ... Use it in transaction mode" (Azure limits page above).

The floor remains roughly `active tenant databases × a few connections`. With 1,000 tenants active at
once, even 2 per database is 2,000 server connections. That limit belongs to the design, not the pooler.

---

## 2. Database compute: CPU, memory, IO (the second wall)

**One instance, shared by every tenant.** All databases in a cluster share one buffer cache, one WAL and
one set of background workers (sibling note, §2):

- `shared_buffers` is a single pool ("the amount of memory the database server uses for shared memory
  buffers"; a "reasonable starting value ... is 25% of the memory in your system").
  <https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-SHARED-BUFFERS>. Buffers are keyed
  by `BufferTag { spcOid, dbOid, relNumber, forkNum, blockNum }` (`PG@src/include/storage/buf_internals.h#L106-L113`),
  so a heavy tenant's pages push out the others' pages.
- Per-query memory (`work_mem`, above) comes out of the same RAM as the cache and as every other tenant's
  backends.
- IO: RDS notes that throughput "is constrained by the resource that is consumed first. That resource
  might be network bandwidth, CPU, memory, or database internal resources", and that the instance class
  caps IOPS regardless of the volume ("the maximum IOPS is 40,000 rather than 256,000" in its example).
  <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html>

**Noisy neighbor: separate databases do not isolate resources.** AWS's SaaS Lens credits the silo model
with "No noisy neighbor concerns" only because it offers "a dedicated environment"
(<https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/silo-isolation.html>). Separate databases on
one shared instance are not dedicated: they share the CPU, cache, WAL and disk listed above. Azure's
database-per-tenant pattern gets "a high degree of performance isolation" from elastic pools and from
moving a database "between pools to provide reserved resources to a specific tenant"
(<https://learn.microsoft.com/en-us/azure/azure-sql/database/saas-tenancy-app-design-patterns?view=azuresql>).
Plain PostgreSQL has no per-database CPU or IO quota. (Unconfirmed by a single doc sentence: I found no
PostgreSQL doc page that says this outright. It follows from no such setting existing in the
resource-consumption chapter linked above.)

**Connections feed this wall.** Freund's benchmarks (§1) show idle connections reducing the throughput
of active ones, and Azure lists "high CPU utilization ... disk and lock contention" from large connection
counts (Azure limits page, §1). The connection explosion of wall 1 therefore also eats DB compute.

**Per-database overhead that lands on DB compute.**

- **Autovacuum visits databases one at a time.** "If the installation has N databases, a new worker will
  be launched every autovacuum_naptime/N seconds. A maximum of autovacuum_max_workers worker processes are
  allowed to run at the same time." <https://www.postgresql.org/docs/current/routine-vacuuming.html#AUTOVACUUM>.
  Defaults: `autovacuum_max_workers` 3, `autovacuum_naptime` 1 minute ("the minimum delay between autovacuum
  runs on any given database"). <https://www.postgresql.org/docs/current/runtime-config-vacuum.html>.
  Three workers serve every tenant database. Reading the launcher code, beyond about 600 databases it
  cannot visit each one once per minute (sibling note, §1; `PG@src/backend/postmaster/autovacuum.c#L1032-L1041`).
  That is a reading of the code, not a documented threshold.
- **Catalogs per database.** "Most system catalogs are copied from the template database during database
  creation and are thereafter database-specific."
  <https://www.postgresql.org/docs/current/catalogs-overview.html>
- **Catalog caches per backend.** Freund's post shows a backend's `CacheMemoryContext` growing from 512 kB
  to 593 MB after touching 100k tables, and names "long-lived connections combined with schema-based
  multi-tenancy" as the bad case. Database-per-tenant avoids the worst of it, because each backend is
  bound to one tenant's catalogs. What costs memory instead is the number of backends (§1). His
  workaround, recycling old pool connections, applies here too.
  (Same post as §1.)

---

## 3. App server compute (real, but the cheapest to fix)

- **The app tier scales independently.** In Azure's database-per-tenant pattern "The application tier is
  scaled up vertically by adding more resources per node. Or the app is scaled out horizontally by adding
  more nodes. The scaling is based on workload, and is independent of the number or scale of the
  individual databases." (Azure SaaS patterns page, §2.)
- **But scaling out multiplies connections.** Each new instance opens its own per-tenant pools (§1
  formula). Freund names this exact pattern as a source of connection pressure: "Often there are many
  servers running [web-]application code using one centralized database" (post in §1).
- **Per-tenant pools cost the app server too.** Each pool keeps sockets and threads or tasks open, and a
  server with hundreds of pools spends memory on them. Unconfirmed: I found no primary source that
  quantifies client-side memory per pooled connection. Treat this as minor next to the server-side cost.

A single app server can hit CPU before the database does, in a CPU-heavy app. The sources don't rank it,
and it is the limit with the easiest fix. The fix, though, makes wall 1 worse unless a shared pooler sits
in between.

---

## 4. Storage (last, as the author thought)

- **Hard caps are far away.** RDS: "You can create Db2, MySQL, MariaDB, and PostgreSQL RDS DB instances
  with up to 64 tebibytes (TiB) of storage." (RDS storage page, §2.) Cloud SQL: dedicated core "Up to 64
  TB", shared core "Up to 3 TB". <https://docs.cloud.google.com/sql/docs/postgres/quotas>. PostgreSQL itself
  allows 32 TB per table at the default block size. <https://www.postgresql.org/docs/current/limits.html>
- **Disk grows without a redesign.** RDS has storage autoscaling (RDS storage page); Azure has "storage
  autogrow". Azure caveats: growing storage "requires a server restart", grows "in 2x increments", can't
  shrink, and at 95% full the server switches "to read-only mode". (Azure limits page, §1.)
- **Each empty tenant database costs some disk** (its own catalog copy, above). No first-party page gives
  the size; measure it.
- **Where storage does bite: operations, not bytes.** Physical backup and PITR are whole-cluster only, so
  restore time grows with the total data of all tenants (§5).

---

## 5. What the question missed

- **Noisy neighbor** (§2). A shared instance gives data isolation but no resource isolation. One tenant's
  big report or bulk import slows every tenant.
- **Single point of failure.** One instance down means every tenant is down. The managed fix is a
  synchronous standby: RDS Multi-AZ "automatically provisions and maintains a synchronous standby replica
  in a different Availability Zone", but "You can't use a standby replica to serve read traffic", and
  commits can get slower.
  <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html>. The AWS SaaS
  Lens lists "Reduced scope of impact" as a pro of dedicated silos; a shared instance gives that up (silo
  page, §2).
- **Schema migrations fan out.** Every migration runs once per tenant database, and partial failure leaves
  tenants on different schema versions. Azure: "The application vendor must design procedures to carefully
  manage schema customizations at scale", and lists "Schema management" under operational complexity
  (Azure SaaS patterns page). No PostgreSQL feature runs DDL across databases in one transaction; a
  connection can't even reach another database (sibling note, §3).
- **Onboarding is a cluster-wide write.** `CREATE DATABASE` with the default `WAL_LOG` strategy copies the
  template "block by block and each block will be separately written to the write-ahead log"; `FILE_COPY`
  forces "a checkpoint both before and after".
  <https://www.postgresql.org/docs/current/sql-createdatabase.html>
- **Backup and restore are whole-cluster.** "file system backups only work for complete backup and
  restoration of an entire database cluster" (<https://www.postgresql.org/docs/current/backup-file.html>),
  and PITR "can only support restoration of an entire database cluster, not a subset"
  (<https://www.postgresql.org/docs/current/continuous-archiving.html>). Restoring one tenant means
  restoring everything to a scratch server and then using `pg_dump` (which "only dumps a single database",
  <https://www.postgresql.org/docs/current/app-pgdump.html>). Azure's flexible server PITR "creates the new
  server" (Azure limits page). Contrast Azure SQL, where restoring one tenant "only needs to restore the one
  single-tenant database" (Azure SaaS patterns page). That is a SQL Server property, not a PostgreSQL one.
- **Transaction ID wraparound covers idle tenants too.** "It is necessary to vacuum every table in every
  database at least once every two billion transactions."
  <https://www.postgresql.org/docs/current/routine-vacuuming.html#VACUUM-FOR-WRAPAROUND>. The XID counter is
  cluster-wide (`PG@src/include/access/transam.h#L209-L227`), so a busy tenant's writes force freezing work
  in every quiet tenant's database, and "the system will launch autovacuum processes to prevent wraparound
  even when autovacuum is otherwise disabled" (runtime-config-vacuum page, §2).
- **Monitoring gets coarse.** Cloud SQL collects PostgreSQL metrics "for up to 500 databases"; beyond that
  only the top 500 by transaction count are reported (Cloud SQL quotas page, §4).

**What no source gives:** a tenant count at which this design stops working. The thresholds above
(default 100 connections, ~600 databases per autovacuum minute, 500 databases for Cloud SQL metrics) are
documented defaults or readings of code, not recommendations.

---

## Sources

PostgreSQL
- max_connections, reserved connections: <https://www.postgresql.org/docs/current/runtime-config-connection.html>
- Process-per-connection: <https://www.postgresql.org/docs/current/connect-estab.html>
- work_mem, shared_buffers, maintenance_work_mem: <https://www.postgresql.org/docs/current/runtime-config-resource.html>
- Autovacuum settings: <https://www.postgresql.org/docs/current/runtime-config-vacuum.html>
- Autovacuum daemon, wraparound: <https://www.postgresql.org/docs/current/routine-vacuuming.html>
- Per-database catalogs: <https://www.postgresql.org/docs/current/catalogs-overview.html>
- CREATE DATABASE: <https://www.postgresql.org/docs/current/sql-createdatabase.html>
- Limits: <https://www.postgresql.org/docs/current/limits.html>
- File-system backup: <https://www.postgresql.org/docs/current/backup-file.html>
- PITR: <https://www.postgresql.org/docs/current/continuous-archiving.html>
- pg_dump: <https://www.postgresql.org/docs/current/app-pgdump.html>
- PostgreSQL 14 release notes: <https://www.postgresql.org/docs/release/14.0/>
- Source (pinned): `PG@src/include/storage/buf_internals.h`, `PG@src/backend/postmaster/autovacuum.c`,
  `PG@src/include/access/transam.h`

Core developer
- Andres Freund, "Analyzing the Limits of Connection Scalability in Postgres" (8 Oct 2020):
  <https://techcommunity.microsoft.com/blog/adforpostgresql/analyzing-the-limits-of-connection-scalability-in-postgres/1757266>

Poolers
- PgBouncer configuration: <https://www.pgbouncer.org/config.html>
- PgBouncer pooling modes: <https://www.pgbouncer.org/features.html>
- HikariCP defaults: <https://github.com/brettwooldridge/HikariCP>

Managed PostgreSQL
- AWS RDS quotas and max_connections: <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html>
- AWS RDS storage: <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html>
- AWS RDS Multi-AZ: <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html>
- Azure flexible server limits: <https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-limits>
- Cloud SQL flags (max_connections defaults): <https://docs.cloud.google.com/sql/docs/postgres/flags>
- Cloud SQL quotas: <https://docs.cloud.google.com/sql/docs/postgres/quotas>

SaaS guidance
- Azure SQL multitenant SaaS patterns: <https://learn.microsoft.com/en-us/azure/azure-sql/database/saas-tenancy-app-design-patterns?view=azuresql>
- AWS SaaS Lens, silo isolation: <https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/silo-isolation.html>
