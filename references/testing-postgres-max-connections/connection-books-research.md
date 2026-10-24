# Books and sources on how a PostgreSQL connection works

Research for the "Testing Postgres max_connections" video and article. Checked on 2026-10-22.

How I checked: each O'Reilly book was looked up by ISBN in O'Reilly's own catalog API
(`learning.oreilly.com/api/v2/epubs/urn:orm:book:<ISBN>/` and its `table-of-contents/`), which
returns the title, release date, and the full table of contents. Chapter and section names below
are copied from that table of contents [S1]. I read the table of contents only, not the chapters,
except for *PostgreSQL 14 Internals*, which is a free PDF and which I read.

## Short answer

**No book on O'Reilly explains the PostgreSQL wire protocol in depth.** The best explanation is free:
the PostgreSQL docs plus a free book (*PostgreSQL 14 Internals*) that is not on O'Reilly. On O'Reilly,
the books cover the practical side: too many connections, idle connections, pooling, pg_hba.conf, SSL.

### Top 3 books on O'Reilly

1. **PostgreSQL Mistakes and How to Avoid Them**, Jimmy Angelakos (Manning, 2025) [S1][S2]
   - 6.2 Improper memory allocation
   - 6.3 Having too many connections
   - 6.4 Having idle connections (6.4.2 The problem with idle connections)
   - 8.3 trust-ing in pg_hba.conf
2. **Learn PostgreSQL, Second Edition**, Luca Ferrari and Enrico Pirozzi (Packt, 2023, PostgreSQL 16) [S1][S3]
   - Ch 2 Getting to Know Your Cluster: "PostgreSQL processes", "Connecting to the cluster",
     "Introducing the connection string", "Solving common connection problems"
   - Ch 3 Managing Users and Connections: "Role passwords, connections, and availability",
     "Managing incoming connections at the role level" (pg_hba.conf)
   - Ch 10 Users, Roles, and Database Security: "SSL connections"
3. **PostgreSQL 16 Administration Cookbook**, Gianni Ciolli, Boriss Mejías, Jimmy Angelakos, Vibhor Kumar, Simon Riggs (Packt, 2023) [S1][S4]
   - Ch 1 First Steps: "Connecting to the PostgreSQL server", "Troubleshooting a failed connection"
   - Ch 4 Server Control: "Preventing new connections", "Restricting users to only one session each",
     "Setting up a connection pool", "Running multiple PgBouncer on the same port to leverage multiple cores"
   - Ch 6 Security: "Connecting using encryption (SSL / GSSAPI)"
   - Ch 8 Monitoring and Diagnosis: "Checking whether a user is connected", "Killing a specific session"

**Best free book (not on O'Reilly):** *PostgreSQL 14 Internals*, Egor Rogov (Postgres Professional,
free PDF) [S5]. Read 1.2 "Processes and Memory" and 1.3 "Clients and the Client-Server Protocol"
(pages 33–35). It explains, in three pages, that postmaster spawns one backend per client, why many
connections cost memory and CPU, and why poolers exist. Later, 16.2 "Simple Query Protocol" and
16.3 "Extended Query Protocol" show what the backend does with a query [S5].

### Reading order (smallest set, about 2 hours)

1. Docs 51.2 "How Connections Are Established" — one page. Process-per-connection model. [S6]
2. *PostgreSQL 14 Internals* 1.2 and 1.3 — three pages. Why each connection costs memory and time. [S5]
3. Docs 54.2.1 "Start-up" and 54.2.2 "Simple Query" — the startup message, authentication, query flow. Skim 54.2.3 "Extended Query". [S7]
4. Docs 19.3 — `max_connections`, `reserved_connections`, `superuser_reserved_connections`. [S8]
5. *PostgreSQL Mistakes and How to Avoid Them* 6.3 and 6.4 — too many and idle connections. [S2]
6. PgBouncer "Features" page — session, transaction, and statement pooling. [S11]

Optional, only if the video needs it: *High Performance Browser Networking* ch 2 "Three-Way Handshake"
and ch 4 "TLS Handshake" for the TCP/TLS cost [S1][S14]; the source files in the table at the end of
section 2 to show the real code.

## 1. All books checked

Fit: High = has named sections on connections, pooling, or connection limits. Medium = some.
Low = little or none. "On O'Reilly" was confirmed through the O'Reilly catalog API [S1].

| Book | Author | Publisher, year | On O'Reilly | Relevant chapters/sections (from the TOC) | Fit |
|---|---|---|---|---|---|
| PostgreSQL Mistakes and How to Avoid Them | Jimmy Angelakos | Manning, 2025 | Yes: [link](https://learning.oreilly.com/library/view/-/9781633436879/) | 6.2 Improper memory allocation; 6.3 Having too many connections; 6.4 Having idle connections; 8.3 trust-ing in pg_hba.conf | High |
| Learn PostgreSQL, 2nd ed. (PG 16) | Luca Ferrari, Enrico Pirozzi | Packt, 2023 | Yes: [link](https://learning.oreilly.com/library/view/-/9781837635641/) | Ch 2: PostgreSQL processes; Connecting to the cluster; Introducing the connection string; Solving common connection problems. Ch 3: Managing incoming connections at the role level. Ch 10: SSL connections. Ch 16: Information about running queries and sessions | High |
| PostgreSQL 16 Administration Cookbook | Ciolli, Mejías, Angelakos, Kumar, Riggs | Packt, 2023 | Yes: [link](https://learning.oreilly.com/library/view/-/9781835460580/) | Ch 1: Connecting to the PostgreSQL server; Troubleshooting a failed connection. Ch 4 Server Control: Preventing new connections; Restricting users to only one session each; Setting up a connection pool; PgBouncer recipes. Ch 6: Connecting using encryption (SSL / GSSAPI). Ch 8: Checking whether a user is connected; Killing a specific session | High |
| Mastering PostgreSQL 17, 6th ed. | Hans-Jürgen Schönig | Packt, 2024 | Yes: [link](https://learning.oreilly.com/library/view/-/9781836205975/) | Ch 8: Understanding bind addresses and connections; Managing the pg_hba.conf file. Ch 12: Inspecting pg_stat_activity; Checking for memory and I/O; Careless connection management | Medium |
| Mastering PostgreSQL 15, 5th ed. | Hans-Jürgen Schönig | Packt, 2023 | Yes: [link](https://learning.oreilly.com/library/view/-/9781803248349/) | Same two sections as the 17 edition (Ch 8, Ch 12). Prefer the 17 edition | Medium |
| PostgreSQL 14 Administration Cookbook | Simon Riggs, Gianni Ciolli | Packt, 2022 | Yes: [link](https://learning.oreilly.com/library/view/-/9781803248974/) | Older edition of the 16 cookbook. Prefer the 16 edition | Medium |
| PostgreSQL High Performance Cookbook | Dinesh Kumar, Chitij Chauhan | Packt, 2017 | Yes: [link](https://learning.oreilly.com/library/view/-/9781785284335/) | Ch 2: Tuning connection-related parameters. Ch 3: Understanding memory units (work_mem). Ch 5: Connection Pooling and Database Partitioning (pgpool-II, PgBouncer). Old (PG 9.x era) | Medium |
| Just Use Postgres! | Denis Magda | Manning, 2025 | Yes: [link](https://learning.oreilly.com/library/view/-/9781633435698/) | 1.4 Connecting with psql; Appendix A.3 Use connection pooling | Low |
| PostgreSQL: Up and Running, 3rd ed. | Regina Obe, Leo Hsu | O'Reilly, 2017 | Yes: [link](https://learning.oreilly.com/library/view/-/9781491963401/) | Ch 2: The pg_hba.conf File; Managing Connections. Old (PG 10) | Low |
| PostgreSQL: Up and Running, 4th ed. | Regina Obe, Leo Hsu | O'Reilly, early release (final date listed as Feb 2027) | Yes, early release: [link](https://learning.oreilly.com/library/view/-/9798341660885/) | Ch 2: pg_hba.conf. Ch 4: Connecting to a PostgreSQL Server. TOC says "Not Yet Final" | Low (for now) |
| PostgreSQL Query Optimization, 2nd ed. | Dombrovskaya, Novikov, Bailliekova | Apress, 2024 | Yes: [link](https://learning.oreilly.com/library/view/-/9798868800696/) | Chapter titles only in the TOC. Ch 10 "What About Configuration Parameters?" and Ch 11 "Application Development and Performance" may touch this. Not confirmed | Low |
| Designing Data-Intensive Applications, 2nd ed. | Martin Kleppmann, Chris Riccomini | O'Reilly, 2026 | Yes: [link](https://learning.oreilly.com/library/view/-/9781098119058/) | No connection or pooling section in the TOC. Ch 9 "Unreliable Networks" is general background only | Low |
| Database Reliability Engineering | Laine Campbell, Charity Majors | O'Reilly, 2017 | Yes: [link](https://learning.oreilly.com/library/view/-/9781491925935/) | Ch 4: Datastore Connection Layer (Utilization, Saturation, Errors). Monitoring view, not internals | Low |
| High Performance MySQL, 4th ed. (for contrast) | Silvia Botros, Jeremy Tinley | O'Reilly, 2021 | Yes: [link](https://learning.oreilly.com/library/view/-/9781492080503/) | Ch 1: Connection Management and Security. Ch 5: Per-Connection Memory Needs; The Thread Cache. Ch 8: The MySQL Client/Server Protocol. Good contrast: MySQL uses threads, not processes | Medium (contrast) |
| Efficient MySQL Performance (for contrast) | Daniel Nichter | O'Reilly, 2021 | Yes: [link](https://learning.oreilly.com/library/view/-/9781098105082/) | Ch 6: Threads and Connections | Low |
| High Performance Browser Networking | Ilya Grigorik | O'Reilly, 2013 | Yes: [link](https://learning.oreilly.com/library/view/-/9781449344757/). Also free at hpbn.co | Ch 2 Building Blocks of TCP: Three-Way Handshake. Ch 4 Transport Layer Security: TLS Handshake | Medium (TCP/TLS cost only) |
| TCP/IP Illustrated, Vol. 1, 2nd ed. | Kevin Fall, W. Richard Stevens | Addison-Wesley, 2011 | Yes: [link](https://learning.oreilly.com/library/view/-/9780132808200/) | Ch 13: TCP Connection Management. Long and deep; reference only | Low |
| PostgreSQL 14 Internals | Egor Rogov | Postgres Professional, 2022–2023 | **Not found on O'Reilly.** Free PDF | 1.2 Processes and Memory; 1.3 Clients and the Client-Server Protocol; 16.2 Simple Query Protocol; 16.3 Extended Query Protocol | High |
| The Art of PostgreSQL | Dimitri Fontaine | Self-published, 2019 | **Not found on O'Reilly** | Not checked (not on the platform) | — |

Notes:

- Authors and publishers come from the O'Reilly book description [S1] or the publisher page
  [S2][S3][S4]. Author names for *PostgreSQL High Performance Cookbook*, *Database Reliability
  Engineering*, *High Performance MySQL*, *Efficient MySQL Performance*, *Up and Running*, and
  *TCP/IP Illustrated* are from my own knowledge of these well-known books, and were not
  re-checked on a publisher page: **not confirmed** here.
- I found no *PostgreSQL 17* or *18 Administration Cookbook*. Not confirmed that one exists.
- I found no book on O'Reilly about HikariCP or client-side pools for PostgreSQL. Use the HikariCP wiki [S13].
- The `learning.oreilly.com/library/view/-/<ISBN>/` links use O'Reilly's short form (a dash in place
  of the title slug). The book behind each ISBN was confirmed through the catalog API [S1]. The link
  needs an O'Reilly login, so I could not open the page itself.

## 2. Free primary sources (read these with the books)

The current PostgreSQL release is 18. PostgreSQL 19 is at RC 1 (released 2026-10-15), so `/docs/current/`
links will soon point to 19 and the chapter numbers may change [S6].

### PostgreSQL docs (version 18)

| Topic | Page |
|---|---|
| Process-per-connection model, postmaster spawns a backend | [51.2 How Connections Are Established](https://www.postgresql.org/docs/current/connect-estab.html) [S6] |
| Big picture of a query | [51.1 The Path of a Query](https://www.postgresql.org/docs/current/query-path.html) |
| Wire protocol, overview | [Ch 54 Frontend/Backend Protocol](https://www.postgresql.org/docs/current/protocol.html), [54.1 Overview](https://www.postgresql.org/docs/current/protocol-overview.html) [S7] |
| Startup message, authentication, simple and extended query, termination | [54.2 Message Flow](https://www.postgresql.org/docs/current/protocol-flow.html): 54.2.1 Start-up, 54.2.2 Simple Query, 54.2.3 Extended Query, 54.2.9 Termination, plus SSL and GSSAPI session encryption [S7] |
| Byte-level message layout (for Wireshark demos) | [54.7 Message Formats](https://www.postgresql.org/docs/current/protocol-message-formats.html) |
| Password auth over the wire | [54.3 SASL Authentication](https://www.postgresql.org/docs/current/sasl-authentication.html) (SCRAM-SHA-256) |
| `max_connections`, `reserved_connections`, `superuser_reserved_connections` | [19.3 Connections and Authentication](https://www.postgresql.org/docs/current/runtime-config-connection.html) [S8] |
| `work_mem` and per-connection memory | [19.4 Resource Consumption](https://www.postgresql.org/docs/current/runtime-config-resource.html) [S9] |
| Shared memory and semaphores that grow with `max_connections` | [18.4 Managing Kernel Resources](https://www.postgresql.org/docs/current/kernel-resources.html) |
| Who may connect | [20.1 The pg_hba.conf File](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html) |
| TLS for connections | [18.9 Secure TCP/IP Connections with SSL](https://www.postgresql.org/docs/current/ssl-tcp.html) |
| Client side (libpq connection strings) | [32.1 Database Connection Control Functions](https://www.postgresql.org/docs/current/libpq-connect.html) |
| Seeing backend processes in `ps` | [27.1 Standard Unix Tools](https://www.postgresql.org/docs/current/monitoring-ps.html) |

Key facts from these pages, useful for the video:

- "PostgreSQL implements a 'process per user' client/server model." The postmaster listens on a
  TCP port and spawns a new backend process for each connection request [S6].
- The startup message carries the user name, the database name, and the protocol version. The server
  checks pg_hba.conf and then asks for authentication [S7].
- `max_connections` default is typically 100 and can only be set at server start. PostgreSQL sizes
  some resources, including shared memory, from it [S8].
- `superuser_reserved_connections` default is 3. `reserved_connections` default is 0; it reserves
  slots for roles with `pg_use_reserved_connections` [S8].
- `work_mem` default is 4MB, but it is per sort or hash operation, and many sessions can use it at
  once, so total memory can be many times `work_mem` [S9].

### Other free sources

- PgBouncer: [Features](https://www.pgbouncer.org/features.html) (session, transaction, and statement
  pooling) [S11], [Configuration](https://www.pgbouncer.org/config.html), [Usage](https://www.pgbouncer.org/usage.html).
- pgpool-II docs: <https://www.pgpool.net/docs/latest/en/html/> [S12].
- HikariCP wiki, [About Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing) — client-side pools and why small pools win [S13].
- PostgreSQL wiki, [Number Of Database Connections](https://wiki.postgresql.org/wiki/Number_Of_Database_Connections) [S10].
- *High Performance Browser Networking*, free online: [Building Blocks of TCP](https://hpbn.co/building-blocks-of-tcp/) and [Transport Layer Security](https://hpbn.co/transport-layer-security-tls/) [S14].

### PostgreSQL source code (REL_18_STABLE)

Checked on the GitHub mirror of the official repo [S15]. In PostgreSQL 17 the startup code moved out
of postmaster.c into a new file, `src/backend/tcop/backend_startup.c`. That file exists on
REL_17_STABLE, REL_18_STABLE, and master, but not on REL_16_STABLE [S15].

| Step | File | Function |
|---|---|---|
| Postmaster waits for connections | `src/backend/postmaster/postmaster.c` | `ServerLoop()` |
| Accept the TCP socket | `src/backend/libpq/pqcomm.c` | `AcceptConnection()` |
| Pick a child slot, too-many check, start the backend | `src/backend/postmaster/postmaster.c` | `BackendStartup()` |
| fork() the child | `src/backend/postmaster/launch_backend.c` | `postmaster_child_launch()` |
| SSL negotiation and startup packet | `src/backend/tcop/backend_startup.c` | `BackendMain()`, `BackendInitialize()`, `ProcessSSLStartup()`, `ProcessStartupPacket()` |
| Authentication (pg_hba.conf, password, SCRAM) | `src/backend/libpq/auth.c` | `ClientAuthentication()` |
| Take a PGPROC slot; "sorry, too many clients already" | `src/backend/storage/lmgr/proc.c` | `InitProcess()` |
| Reserved-slot check; "remaining connection slots are reserved..." | `src/backend/utils/init/postinit.c` | `InitPostgres()` |
| Main query loop of the backend | `src/backend/tcop/postgres.c` | `PostgresMain()`, `exec_simple_query()`, `exec_parse_message()`, `exec_bind_message()`, `exec_execute_message()` |
| Client side (libpq) connection state machine | `src/interfaces/libpq/fe-connect.c` | `PQconnectPoll()` |

The error "sorry, too many clients already" appears in two places: `backend_startup.c` (when the
postmaster already knows there are too many) and `proc.c` (when all PGPROC slots are taken) [S15].
That is the error the max_connections test will hit.

## Sources

- [S1] O'Reilly catalog API, metadata and table of contents per ISBN, e.g.
  `https://learning.oreilly.com/api/v2/epubs/urn:orm:book:9781633436879/table-of-contents/`.
  ISBNs checked: 9781633436879, 9781837635641, 9781835460580, 9781836205975, 9781803248349,
  9781803248974, 9781785284335, 9781633435698, 9781491963401, 9798341660885, 9798868800696,
  9781098119058, 9781491925935, 9781492080503, 9781098105082, 9781449344757, 9780132808200.
  Not found: 9785604597040 (PostgreSQL 14 Internals), 9781949950366 (The Art of PostgreSQL).
- [S2] Manning, PostgreSQL Mistakes and How to Avoid Them: <https://www.manning.com/books/postgresql-mistakes-and-how-to-avoid-them>
- [S3] Packt, Learn PostgreSQL, Second Edition: <https://www.packtpub.com/en-br/product/learn-postgresql-second-edition-9781837635641>
- [S4] Packt, PostgreSQL 16 Administration Cookbook: <https://www.packtpub.com/en-au/product/postgresql-16-administration-cookbook-9781835460580/chapter/server-control-4/section/setting-up-a-connection-pool-ch04lvl1sec58>
- [S5] Egor Rogov, *PostgreSQL 14 Internals*, Postgres Professional, ISBN 978-5-6045970-4-0. Book page: <https://postgrespro.com/community/books/internals>. PDF: <https://edu.postgrespro.com/postgresql_internals-14_en.pdf>
- [S6] PostgreSQL 18 docs, 51.2 How Connections Are Established: <https://www.postgresql.org/docs/current/connect-estab.html>
- [S7] PostgreSQL 18 docs, Ch 54 Frontend/Backend Protocol and 54.2 Message Flow: <https://www.postgresql.org/docs/current/protocol.html>, <https://www.postgresql.org/docs/current/protocol-flow.html>
- [S8] PostgreSQL 18 docs, 19.3 Connections and Authentication: <https://www.postgresql.org/docs/current/runtime-config-connection.html>
- [S9] PostgreSQL 18 docs, 19.4 Resource Consumption: <https://www.postgresql.org/docs/current/runtime-config-resource.html>
- [S10] PostgreSQL wiki, Number Of Database Connections: <https://wiki.postgresql.org/wiki/Number_Of_Database_Connections>
- [S11] PgBouncer features: <https://www.pgbouncer.org/features.html>
- [S12] pgpool-II documentation: <https://www.pgpool.net/docs/latest/en/html/>
- [S13] HikariCP wiki, About Pool Sizing: <https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing>
- [S14] Ilya Grigorik, High Performance Browser Networking (free online): <https://hpbn.co/building-blocks-of-tcp/>, <https://hpbn.co/transport-layer-security-tls/>
- [S15] PostgreSQL source, GitHub mirror of the official repo, branch REL_18_STABLE: <https://github.com/postgres/postgres/tree/REL_18_STABLE/src/backend> (files: `postmaster/postmaster.c`, `postmaster/launch_backend.c`, `tcop/backend_startup.c`, `tcop/postgres.c`, `libpq/pqcomm.c`, `libpq/auth.c`, `storage/lmgr/proc.c`, `utils/init/postinit.c`; `src/interfaces/libpq/fe-connect.c`)
