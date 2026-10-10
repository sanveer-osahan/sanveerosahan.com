# Databases per instance: research notes

Working notes for the section "Starting with a Simple Monolith" in
`src/content/articles/designing-a-multi-tenant-system.md`. That section proposes one database instance
holding a `common_db` (Workspaces, Users, Memberships) plus one database per tenant
(`tenant_1_db`, `tenant_2_db`, ...). It says a separate database on a shared instance gives logical isolation.

The questions, in the author's words:

1. How many databases can be created in such single instance DBs?
2. How does the data storage work internally when data is stored per database?
3. A single connection lets you connect to only one database. Why?

Sources are primary only: each vendor's own docs and limits pages, and the PostgreSQL source tree.
PostgreSQL docs are the current (18) docs. PostgreSQL source links are pinned to the `REL_18_STABLE` commit
`3c6135f839d03ef96a7313bca09ba4c1ec8dd161`, so line numbers stay valid. Below, `PG@` stands for
`https://github.com/postgres/postgres/blob/3c6135f839d03ef96a7313bca09ba4c1ec8dd161/`.

---

## Short answers

**1. How many databases?** Each engine's hard limit is far beyond anything a startup will reach.
PostgreSQL documents 4,294,950,911 databases per cluster. SQL Server documents 32,767 per instance.
MySQL documents no limit apart from the file system's limit on directories. What runs out first is
operations, not the hard limit. In PostgreSQL every database is a full copy of the system catalogs, every
pooled connection is pinned to one database, and autovacuum has to visit every database in turn. All of
them share one WAL, one buffer pool, one transaction-ID counter and one `max_connections`. No first-party
source gives a tenant count at which database-per-tenant stops working.

**2. How is storage laid out?** It depends on the engine, and the difference matters.
- **PostgreSQL:** each database is a directory, `base/<database OID>/`, that holds its own system catalogs
  and table files. The WAL, the commit log (`pg_xact`), shared memory, the roles and the list of databases
  are shared by the whole cluster. As a result, `pg_dump` works per database, but physical backup and
  point-in-time recovery (PITR) restore only the whole cluster.
- **MySQL/InnoDB:** a "database" is a schema, meaning a directory of per-table `.ibd` files. The data
  dictionary, system tablespace, undo tablespaces, redo log and binary log are instance-wide.
- **SQL Server:** each database owns its own data (`.mdf`/`.ndf`) and log (`.ldf`) files, and you can back
  up and restore one database, including to a point in time.

**3. Why one database per connection?** This is a PostgreSQL property. MySQL and SQL Server don't have
it. In PostgreSQL the client names the database in the startup packet. The postmaster starts one backend
process for that connection. `InitPostgres()` binds that process to one database: it sets `MyDatabaseId`,
sets the process's database path (once; the code asserts it is never set twice), and loads that
database's catalogs into the per-process relation cache. Nothing in the backend can undo this, so
switching databases means a new backend, which means a new connection. psql's `\c` opens a new connection
and closes the old one. `dblink` and `postgres_fdw` reach other databases by opening their own extra
connections. MySQL's `USE` and SQL Server's `USE` and three-part names switch databases or cross between
them inside one connection, because in those engines a database is a namespace on the same server
session.

---

## 1. How many databases one instance can hold

### PostgreSQL

**Documented hard limit**

- The limits appendix lists "number of databases: 4,294,950,911" and "relations per database:
  1,431,650,303". <https://www.postgresql.org/docs/current/limits.html>
- Where the number comes from: database OIDs are assigned from the ordinary OID space.
  `CREATE DATABASE` gets the new OID from `GetNewOidWithIndex(pg_database_rel, DatabaseOidIndexId, ...)`
  (`PG@src/backend/commands/dbcommands.c#L1444`). User OIDs start at `FirstNormalObjectId = 16384`
  (`PG@src/include/access/transam.h#L197`). 2³² − 16,384 − 1 = 4,294,950,911, which matches the documented
  figure. (The arithmetic is mine. The docs state the number without deriving it.)

**Operational limits** (these are not documented as limits; they are costs that grow with the number of
databases)

- **Each database is a full set of catalogs.** "Most system catalogs are copied from the template database
  during database creation and are thereafter database-specific."
  <https://www.postgresql.org/docs/current/catalogs-overview.html>. By default the new database is a clone
  of `template1`. <https://www.postgresql.org/docs/current/sql-createdatabase.html>. Each new database
  therefore adds a copy of `pg_class`, `pg_attribute`, `pg_proc` and the rest, together with their files
  and indexes. No first-party page gives the size of an empty database. Measure it on your own build.
- **Creating a database writes the template to the WAL.** With the default `WAL_LOG` strategy, "the
  database will be copied block by block and each block will be separately written to the write-ahead
  log". With `FILE_COPY`, the server must "perform a checkpoint both before and after the creation of the
  new database". <https://www.postgresql.org/docs/current/sql-createdatabase.html>. Onboarding a tenant is
  therefore a cluster-wide event, not a cheap insert.
- **Autovacuum visits databases one at a time.** "The launcher will distribute the work across time,
  attempting to start one worker within each database every autovacuum_naptime seconds. (Therefore, if the
  installation has N databases, a new worker will be launched every autovacuum_naptime/N seconds.) A
  maximum of autovacuum_max_workers worker processes are allowed to run at the same time."
  <https://www.postgresql.org/docs/current/routine-vacuuming.html#AUTOVACUUM>
  - In the source, the launcher spaces databases `millis_increment = 1000.0 * autovacuum_naptime / nelems`
    apart. If that comes out below `MIN_AUTOVAC_SLEEPTIME` (100 ms), the launcher "silently use[s] a larger
    naptime". (`PG@src/backend/postmaster/autovacuum.c#L1032-L1041`; constant at
    `PG@src/backend/postmaster/autovacuum.c#L139`.) Derived from those two lines: with the default
    `autovacuum_naptime` of one minute
    (<https://www.postgresql.org/docs/current/runtime-config-vacuum.html#GUC-AUTOVACUUM-NAPTIME>), beyond
    about 600 databases the launcher can no longer get around all of them once per naptime. A full round
    then takes about N × 110 ms. This is a reading of the code, not a documented threshold.
  - A worker serves one database: workers "connect to a database as determined in the launcher, and once
    connected they examine the catalogs to select the tables to vacuum" (`PG@src/backend/postmaster/autovacuum.c#L7-L13`).
- **Wraparound protection covers every database, including idle tenants.** "It is necessary to vacuum
  every table in every database at least once every two billion transactions."
  <https://www.postgresql.org/docs/current/routine-vacuuming.html#VACUUM-FOR-WRAPAROUND>. The XID counter
  that drives this is one counter in shared memory for the whole cluster: `TransamVariablesData.nextXid`,
  with `oldestXid` commented as the "cluster-wide minimum datfrozenxid" and `oldestXidDB` as the "database
  with minimum datfrozenxid" (`PG@src/include/access/transam.h#L209-L227`). A busy tenant consumes XIDs,
  and every quiet tenant's database then has to be frozen to keep pace.
- **Connections are pinned to a database, so pools multiply.** `max_connections` "Determines the maximum
  number of concurrent connections to the database server. The default is typically 100 ... This parameter
  can only be set at server start." <https://www.postgresql.org/docs/current/runtime-config-connection.html#GUC-MAX-CONNECTIONS>.
  Because a connection cannot change database (§3), a pool cannot be shared across tenant databases.
  PgBouncer's own docs size pools "per user/database pair" (`default_pool_size`, default 20).
  <https://www.pgbouncer.org/config.html>. My arithmetic: 50 tenant databases × 20 = 1,000 potential server
  connections, against a default `max_connections` of 100.
- **Open files per backend.** `max_files_per_process` "Sets the maximum number of open files each server
  subprocess is allowed to open simultaneously ... The default is one thousand files."
  <https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-MAX-FILES-PER-PROCESS>. A
  backend only opens files of the database it is bound to. Pinned pools mean more backends overall, each
  with its own file and cache footprint.
- **Shared buffers are one pool.** `shared_buffers` "Sets the amount of memory the database server uses
  for shared memory buffers" (<https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-SHARED-BUFFERS>).
  A buffer's identity includes the database OID (`BufferTag { spcOid, dbOid, relNumber, forkNum, blockNum }`,
  `PG@src/include/storage/buf_internals.h#L106-L113`). Every tenant database competes for the same cache,
  so a noisy tenant pushes out the others' pages.
- **Backup and restore time.** See §2. Physical backup and PITR are cluster-wide, so restoring one tenant's
  data from a physical backup means restoring the whole cluster.

**No first-party number for "too many databases".** Neither the PostgreSQL docs nor the source state a
tenant count at which database-per-tenant becomes impractical.

### MySQL / InnoDB

- **Documented hard limit: none.** "MySQL has no limit on the number of databases. The underlying file
  system may have a limit on the number of directories." InnoDB "permits up to 4 billion tables."
  <https://dev.mysql.com/doc/refman/8.4/en/database-count-limit.html>
- **Operational limits:** the main bound is the file system: one directory per database, and by default
  one `.ibd` file per table (§2). The InnoDB buffer pool, redo log and connection limit are shared across
  all databases (§2). Because a connection can switch database (§3), MySQL doesn't have PostgreSQL's
  one-pool-per-database problem.

### SQL Server

- **Documented hard limit:** "Databases per instance of SQL Server: 32,767". The same table lists
  "User connections: 32,767" and "Files per database: 32,767".
  <https://learn.microsoft.com/en-us/sql/sql-server/maximum-capacity-specifications-for-sql-server>
- **Operational limits:** every database has at least one data file and one log file (§2), so file and log
  management grows linearly with tenants. `tempdb` is "a global resource available to all users connected
  to a Database Engine instance", so all tenants share it.
  <https://learn.microsoft.com/en-us/sql/relational-databases/databases/tempdb-database>

### MongoDB (short note)

MongoDB's limits page documents no limit on the number of databases. It says: "While there is no hard
limit on the number of collections in a single MongoDB Atlas cluster, the performance of a cluster might
degrade if it serves a large number of collections and indexes". For Atlas it recommends a maximum number
of collections plus indexes by tier (5,000 on M10, 10,000 on M20/M30, 100,000 on M40 and up).
<https://www.mongodb.com/docs/manual/reference/limits/>. The page does not describe a per-database storage
model, so these notes cover MongoDB no further.

---

## 2. How storage works per database

### PostgreSQL

**Cluster, databases, schemas.** "A PostgreSQL database cluster contains one or more named databases.
Roles and a few other object types are shared across the entire cluster. A client connection to the server
can only access data in a single database, the one specified in the connection request."
<https://www.postgresql.org/docs/current/ddl-schemas.html>. "A small number of objects, like role, database,
and tablespace names, are defined at the cluster level and stored in the pg_global tablespace."
<https://www.postgresql.org/docs/current/manage-ag-overview.html>

**Data directory layout.** <https://www.postgresql.org/docs/current/storage-file-layout.html>
- `base/`: "Subdirectory containing per-database subdirectories". "For each database in the cluster there
  is a subdirectory within PGDATA/base, named after the database's OID in pg_database. This subdirectory is
  the default location for the database's files; in particular, its system catalogs are stored there."
- `global/`: "Subdirectory containing cluster-wide tables, such as pg_database".
- `pg_wal/`: "Subdirectory containing WAL (Write Ahead Log) files".
- `pg_tblspc/`: symbolic links to tablespaces, each "named after the tablespace's OID".
- Table and index files "are named after the table or index's filenode number, which can be found in
  pg_class.relfilenode". Files over 1 GB are split into `filenode.1`, `filenode.2` and so on. Each relation
  also has a `_fsm` (free space map) fork, and tables have a `_vm` (visibility map) fork.
- In the source, `GetRelationPath()` builds exactly `global/<relfilenode>` for shared relations and
  `base/<dbOid>/<relfilenode>` for everything else (`PG@src/common/relpath.c#L143-L182`). The physical
  address of any relation is `RelFileLocator { spcOid, dbOid, relNumber }`, and "relNumber is only unique
  within a database in a particular tablespace" (`PG@src/include/storage/relfilelocator.h#L33-L63`).

So on disk, tenant 1's tables live in `base/<oid of tenant_1_db>/...` and tenant 2's in
`base/<oid of tenant_2_db>/...`.

**Shared vs per-database catalogs.** "Most system catalogs are copied from the template database during
database creation and are thereafter database-specific. A few catalogs are physically shared across all
databases in a cluster." <https://www.postgresql.org/docs/current/catalogs-overview.html>. The catalogs
marked `BKI_SHARED_RELATION` in `src/include/catalog/` (PG 18) are: `pg_authid`, `pg_auth_members`,
`pg_database`, `pg_db_role_setting`, `pg_tablespace`, `pg_shdepend`, `pg_shdescription`, `pg_shseclabel`,
`pg_replication_origin`, `pg_subscription` and `pg_parameter_acl` (e.g. `PG@src/include/catalog/pg_database.h`,
`PG@src/include/catalog/pg_authid.h`). Everything else, including `pg_class`, `pg_attribute`, `pg_namespace`
and `pg_proc`, exists once per database.

**What is shared by every database in the cluster:**
- **One WAL.** "WAL files are stored in the directory pg_wal under the data directory." Positions are one
  monotonically increasing LSN. <https://www.postgresql.org/docs/current/wal-internals.html>. Every WAL record
  addresses pages by `RelFileLocator`, which carries the `dbOid` (above). One stream therefore holds every
  database's changes.
- **One commit log.** Table files "are not usable without the commit log files, pg_xact/*, which contain
  the commit status of all transactions." <https://www.postgresql.org/docs/current/backup-file.html>
- **One XID counter and one OID counter** in shared memory (`TransamVariablesData.nextXid`, `.nextOid`,
  `PG@src/include/access/transam.h#L209-L222`).
- **One buffer pool** (`shared_buffers`), keyed by a `BufferTag` that includes `dbOid` (§1).
- **Roles.** `pg_authid` is shared, so "there cannot be different roles named, say, joe in two databases
  in the same cluster". <https://www.postgresql.org/docs/current/ddl-schemas.html>

**Backup and PITR.**
- Logical, per database: "pg_dump only dumps a single database. To export an entire cluster, or to export
  global objects that are common to all databases in a cluster (such as roles and tablespaces), use
  pg_dumpall." <https://www.postgresql.org/docs/current/app-pgdump.html>
- Physical, whole cluster only: "file system backups only work for complete backup and restoration of an
  entire database cluster", because of `pg_xact`. <https://www.postgresql.org/docs/current/backup-file.html>
- PITR, whole cluster only: "As with the plain file-system-backup technique, this method can only support
  restoration of an entire database cluster, not a subset."
  <https://www.postgresql.org/docs/current/continuous-archiving.html>

The practical consequence: rolling one tenant back to 10:42 yesterday means restoring the whole cluster to
a scratch server and then using `pg_dump` to copy that tenant's database back out.

### MySQL / InnoDB

- A database is a directory, and a schema is the same thing. "CREATE SCHEMA is a synonym for CREATE
  DATABASE." The statement "creates only a directory under the MySQL data directory."
  <https://dev.mysql.com/doc/refman/8.4/en/create-database.html>. "MySQL represents each database as a
  directory in the data directory." <https://dev.mysql.com/doc/refman/8.4/en/identifier-mapping.html>
- Tables are files: "InnoDB creates tables in file-per-table tablespaces by default", stored as
  `table_name.ibd` "in a schema directory under the MySQL data directory".
  <https://dev.mysql.com/doc/refman/8.4/en/innodb-file-per-table-tablespaces.html>
- Instance-wide pieces:
  - Data dictionary: "Data dictionary tables are created in a single InnoDB tablespace named mysql.ibd,
    which resides in the MySQL data directory."
    <https://dev.mysql.com/doc/refman/8.4/en/data-dictionary-transactional-storage.html>
  - System tablespace `ibdata1`, "the storage area for the change buffer".
    <https://dev.mysql.com/doc/refman/8.4/en/innodb-system-tablespace.html>
  - Undo tablespaces: "Two default undo tablespaces are created when the MySQL instance is initialized."
    <https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-tablespaces.html>
  - Redo log: "Redo log files reside in the #innodb_redo directory in the data directory".
    <https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html>
  - Buffer pool: "an area in main memory where InnoDB caches table and index data".
    <https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html>
- Per-database recovery is possible with tools. `mysqlbinlog --database=db_name` filters the binary log to
  one database's changes (for row-based logging, "only entries that change tables belonging to db_name").
  <https://dev.mysql.com/doc/refman/8.4/en/mysqlbinlog.html>. A file-per-table table can also be imported
  from another instance (same file-per-table page).

### SQL Server

- "At a minimum, every SQL Server database has two operating system files: a data file and a log file."
  Primary data file `.mdf`, optional secondary `.ndf`, transaction log `.ldf`, with "at least one log file
  for each database". "A file or filegroup can't be used by more than one database."
  <https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-files-and-filegroups>
- Each database therefore has its own transaction log, and backup and restore are per database. That
  includes point-in-time restore under the full recovery model ("Restore a SQL Server database to a point
  in time (full recovery model)").
  <https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/back-up-and-restore-of-sql-server-databases>
- Shared: `tempdb` (above), plus the instance's memory and connection limit.

---

## 3. Why one PostgreSQL connection binds to exactly one database

**The docs state the rule.** "When connecting to the database server, a client must specify the database
name in its connection request. It is not possible to access more than one database per connection.
However, clients can open multiple connections to the same database, or different databases."
<https://www.postgresql.org/docs/current/manage-ag-overview.html>

**Step 1: the startup packet names the database.** The protocol's StartupMessage carries `user` ("Required;
there is no default") and `database` ("The database to connect to. Defaults to the user name.").
<https://www.postgresql.org/docs/current/protocol-message-formats.html>. The server parses it in
`ProcessStartupPacket()`: `if (strcmp(nameptr, "database") == 0) port->database_name = pstrdup(valptr);`
(`PG@src/backend/tcop/backend_startup.c#L770-L771`). It falls back to the user name when the field is
empty (`#L857-L858`). No protocol message exists to change the database later.

**Step 2: one backend process per connection.** "PostgreSQL implements a 'process per user' client/server
model. In this model, every client process connects to exactly one backend process ... [the postmaster]
spawns a new backend process every time a connection is requested."
<https://www.postgresql.org/docs/current/connect-estab.html>. In the source: `BackendStartup()` → `postmaster_child_launch()`
(`PG@src/backend/postmaster/postmaster.c#L3531`, `#L3582`). The new backend runs `PostgresMain()`, which
calls `InitPostgres(dbname, InvalidOid, username, ...)` with the comment `/* database to connect to */`
(`PG@src/backend/tcop/postgres.c#L4293`).

**Step 3: `InitPostgres()` binds the process to that database** (`PG@src/backend/utils/init/postinit.c#L712`).
In order:
1. It loads relcache entries for the shared catalogs only, which are the ones it can read before it knows
   the database: "Load relcache entries for the shared system catalogs. This must create at least entries
   for pg_database and catalogs used for authentication." (`#L814-L818`, `RelationCacheInitializePhase2()`)
2. It looks the name up in the shared `pg_database` catalog (`GetDatabaseTuple`), failing with `database
   "%s" does not exist` (`#L1012-L1016`).
3. It takes a lock on that database so that `DROP DATABASE` cannot remove it mid-session:
   `LockSharedObject(DatabaseRelationId, dboid, 0, RowExclusiveLock)` (`#L1058`). It then advertises itself
   in the ProcArray as "in" that database. `DROP DATABASE` checks the ProcArray for exactly this.
4. It fixes the identity: `MyDatabaseId = dboid;` and `MyProc->databaseId = MyDatabaseId;`
   (`#L1116`, `#L1130`). The comment notes it only reacts to cache-invalidation messages "for unshared
   catalogs" once `MyDatabaseId` is set (`#L1132-L1138`).
5. It points all file access at that database's directory: `fullpath = GetDatabasePath(MyDatabaseId, ...)`,
   then `SetDatabasePath(fullpath)` (`#L1144`, `#L1167`). `SetDatabasePath()` is one-shot by design:
   `/* This should happen only once per process */ Assert(!DatabasePath);`
   (`PG@src/backend/utils/init/miscinit.c#L334-L338`).
6. It loads that database's catalogs into the per-process caches: "It's now possible to do real access to
   the system catalogs. Load relcache entries for the system catalogs." (`RelationCacheInitializePhase3()`,
   `#L1170-L1176`). The relcache init file it reads and writes is per database, `DatabasePath/pg_internal.init`
   (`PG@src/backend/utils/cache/relcache.c#L6183-L6187`).

**Why it can't switch afterwards.** Everything a backend knows about tables, such as `pg_class`, types,
functions, cached plans and the relcache and catcache, came from one database's private copy of the
catalogs. A table OID or relfilenode means nothing outside that database, since relNumber "is only unique
within a database" (`PG@src/include/storage/relfilelocator.h#L38-L39`). The process also holds a lock on
its database and is registered in shared memory under that database's OID. Switching would mean flushing
every cache, releasing and retaking those locks, and re-registering. That amounts to a new backend
process, and the server provides no path for doing it in place. The source never states this rationale in
one sentence. It follows from the one-shot `SetDatabasePath()` assert and the order of `InitPostgres()`
above.

**Why psql's `\c` is a new connection.** The docs say: "Establishes a new connection to a PostgreSQL server
... If the new connection is successfully made, the previous connection is closed."
<https://www.postgresql.org/docs/current/app-psql.html>. In the source, `do_connect()` calls
`PQconnectStartParams()` for a fresh connection and then `PQfinish(o_conn)` on the old one
(`PG@src/bin/psql/command.c#L3930`, `#L4234`, `#L4314`). The server sees a disconnect and a new backend.

**How cross-database access works anyway: a second connection.**
- `dblink`: "supports connections to other PostgreSQL databases from within a database session";
  `dblink_connect` "opens a persistent connection to a remote database".
  <https://www.postgresql.org/docs/current/dblink.html>
- `postgres_fdw`: "establishes a connection to a foreign server during the first query that uses a foreign
  table associated with the foreign server ... a connection is established for each user mapping."
  <https://www.postgresql.org/docs/current/postgres-fdw.html>. The docs list both as the way objects
  "within one database [can] act as proxies for objects in other database or clusters".
  <https://www.postgresql.org/docs/current/manage-ag-overview.html>

In both cases your backend becomes a client and opens a second connection, which gets a second backend
bound to the other database. A join between `common_db.memberships` and `tenant_7_db.projects` is
therefore a distributed query, not a local one.

**Contrast: MySQL.** "The USE statement tells MySQL to use the named database as the default (current)
database for subsequent statements ... Making a particular database the default by means of the USE
statement does not preclude accessing tables in other databases", for example
`SELECT author_name,editor_name FROM author,db2.editor WHERE ...`.
<https://dev.mysql.com/doc/refman/8.4/en/use.html>. A MySQL database is a namespace (a synonym for schema)
over one shared data dictionary (§2), so one session can name tables in any database it has privileges on.

**Contrast: SQL Server.** `USE` "Changes the database context to the specified database or database
snapshot" and "takes effect immediately". <https://learn.microsoft.com/en-us/sql/t-sql/language-elements/use-transact-sql>.
Object names can be `<database_name>.<schema_name>.<object_name>`, where `database_name` "Specifies the name
of a SQL Server database when the object resides in a local instance of SQL Server".
<https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transact-sql-syntax-conventions-transact-sql>.
One exception: in **Azure SQL Database**, "the USE statement doesn't switch between databases, and error
code 40508 is returned. To change databases, you must directly connect to the database." (same `USE` page).
That behaves like PostgreSQL.

---

## 4. What this means for the article's design

**What "a separate database on a shared instance" gives, by engine:**

| | PostgreSQL | MySQL/InnoDB | SQL Server |
| --- | --- | --- | --- |
| Separate catalog / namespace | Yes, own copy of most catalogs | Namespace only; one shared data dictionary | Yes |
| One connection can read another tenant's database | No, needs `dblink`/`postgres_fdw` (a second connection) | **Yes**, `db2.table`, if privileges allow | **Yes**, `db.schema.table`, if permissions allow (not on Azure SQL Database) |
| Who can connect by default | **`PUBLIC` has `CONNECT` on every new database** ([ddl-priv](https://www.postgresql.org/docs/current/ddl-priv.html)); revoke it per tenant DB | Per-database `GRANT` | Needs a database user / `CONNECT` |
| Roles / logins | Cluster-wide (`pg_authid` shared) | Instance-wide | Logins instance-wide, users per database |
| Log / recovery | One WAL; PITR is whole-cluster only | One redo log; binlog filterable per database | **Per-database log; per-database PITR** |
| Shared resources (noisy neighbour) | WAL, `shared_buffers`, XID counter, `max_connections`, autovacuum workers | Buffer pool, redo, undo, connections | `tempdb`, memory, connections |

Points that follow from the sources:

- **In PostgreSQL the isolation is real at the query level, and the connection is what enforces it.** A
  query that forgets a tenant filter cannot reach another tenant's database, because the backend cannot see
  it (§3). That is stronger than `WHERE tenant_id = ?`. Two caveats: new databases grant `CONNECT` to
  `PUBLIC` by default, so a connection that names the wrong database still gets in unless you revoke
  that grant and give each tenant its own role. Also, roles are shared across the cluster.
- **In MySQL a "database per tenant" is a schema per tenant.** One connection can join across tenants
  (`USE` docs above). The isolation comes from `GRANT`s, not from the database boundary. A single
  application user with access to every tenant database is close to the shared-table risk the article
  warns about.
- **In SQL Server the database is a storage and recovery unit** (own files, own log, per-database restore),
  but one connection can still cross databases with three-part names.
- **The `common_db` + `tenant_N_db` split costs PostgreSQL something extra:** you cannot `JOIN`
  Memberships (in `common_db`) to tenant tables in one query, and every request that touches both needs
  two connections, from two pools.
- **Operational costs grow with the tenant count in PostgreSQL:** one connection pool per tenant database
  against one server-wide `max_connections`; a full catalog copy per database; autovacuum cycling through
  every database, and freezing every database against one cluster-wide XID counter; a WAL-logged copy of
  `template1` per onboarding; and no per-tenant PITR.
- **At what tenant count does it stop being practical? No first-party source states one.** The PostgreSQL
  docs give only the hard limit (4,294,950,911). The source gives one mechanical threshold: with the
  default one-minute `autovacuum_naptime`, beyond about 600 databases the launcher can no longer visit
  every database once per naptime (§1). That is a reading of `autovacuum.c`, not a documented limit or a
  recommendation. Any other figure would have to come from your own measurements.

### Where this contradicts or qualifies the article as written

1. "There are modern databases that support multiple databases in a single instance." This is true, but
   "database" means different things. In MySQL it is a schema (`CREATE SCHEMA` is a synonym), in SQL
   Server it is a set of files with its own log, and in PostgreSQL it is a separate catalog that a
   connection is bound to. The isolation you get varies accordingly.
2. "A separate database on a shared instance gives you logical isolation." In PostgreSQL this holds at the
   query level, but not by default at the access level, since `PUBLIC` gets `CONNECT`. It also gives no
   resource isolation and no per-tenant point-in-time restore. In MySQL and SQL Server, one connection can
   read across databases, so isolation depends entirely on privileges. That is the same "one mistake
   leaks data" class of risk the article attributes only to shared tables.
3. The diagram and design put Memberships in `common_db` and tenant data in `tenant_N_db` on the same
   instance. In PostgreSQL that means no cross-database joins and two connections per request. The article
   doesn't mention this yet.
