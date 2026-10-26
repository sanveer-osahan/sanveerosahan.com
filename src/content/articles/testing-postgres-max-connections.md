---
title: "Understanding Database Connection Limits"
description: ""
publishDate: 2026-10-19
draft: false
tags: ["postgres", "multi-tenancy", "b2b"]
sources:
  - title: "PostgreSQL Documentation: How Connections Are Established"
    author: "The PostgreSQL Global Development Group"
    url: "https://www.postgresql.org/docs/current/connect-estab.html"
  - title: "PostgreSQL Documentation: Message Flow"
    author: "The PostgreSQL Global Development Group"
    url: "https://www.postgresql.org/docs/current/protocol-flow.html"
  - title: "PostgreSQL Documentation: The pg_hba.conf File"
    author: "The PostgreSQL Global Development Group"
    url: "https://www.postgresql.org/docs/current/auth-pg-hba-conf.html"
  - title: "PostgreSQL Documentation: Connections and Authentication"
    author: "The PostgreSQL Global Development Group"
    url: "https://www.postgresql.org/docs/current/runtime-config-connection.html"
  - title: "PostgreSQL 14 Internals"
    author: "Egor Rogov"
    url: "https://edu.postgrespro.com/postgresql_internals-14_en.pdf"
  - title: "RFC 9293: Transmission Control Protocol (TCP)"
    author: "Wesley Eddy"
    url: "https://www.rfc-editor.org/rfc/rfc9293"
  - title: "RFC 6056: Recommendations for Transport-Protocol Port Randomization"
    author: "Michael Larsen, Fernando Gont"
    url: "https://www.rfc-editor.org/rfc/rfc6056"
  - title: "POSIX: listen()"
    author: "The Open Group"
    url: "https://pubs.opengroup.org/onlinepubs/9799919799/functions/listen.html"
  - title: "POSIX: connect()"
    author: "The Open Group"
    url: "https://pubs.opengroup.org/onlinepubs/9799919799/functions/connect.html"
  - title: "POSIX: accept()"
    author: "The Open Group"
    url: "https://pubs.opengroup.org/onlinepubs/9799919799/functions/accept.html"
  - title: "POSIX: fork()"
    author: "The Open Group"
    url: "https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html"
  - title: "What Is Database Connection Pooling? Definition and Examples"
    author: "Sami Ahmed Siddiqui"
    url: "https://www.yugabyte.com/key-concepts/what-is-database-connection-pooling-definition-and-examples/"
---
## Introduction

There were multiple outages in the last year and there have been some in the last decade where the story is something like this:  

Your application is expecting traffic during a Black Friday Sale.
You are confident that the services will be able to handle the traffic due to the follwing:  

- Autoscaling of application servers is configured
- Redis cache layer present
- Load testing showed stable CPU and memory usage, 200ms response time

In production, everything is working fine for the first 20 minutes.  
Then responses for some requests slowed down - taking 2 to 3 seconds.  

- The CPU and Memory usage was still stable. 
- Application Servers were scaling correctly as configured. 
- Database Server had no downtime.

Yet there was an outage.  
Why?  
Let's understand few concepts before doing deep dive into the incidents.

## Connecting to a Database

Let's take an example of connecting your Application to a Postgres Instance.  

We have the following actors in the entire process:

1. Application Server : Where your Application's business logic runs. A machine on which the OS kernel can sen/recieve TCP packets.
2. Database Client : Application Server uses the Database Client like psql to connect to the Database.
3. Database Server : Hosts the Database with memory and storage. Another machine on which the OS kernel can sen/recieve TCP packets.
4. Postmaster : The main Postgres process known as the supervisor process


### Phase 1 : Set up the Database Server

There are various ways to set up a DBMS like Postgres:

- Locally using OS Native installtions (Ubuntu/MacOS/Windows)
- Using Docker 
- On an EC2 machine
- Using Amzon RDS
- Using Backend-as-a-Service (BaaS) like Supabase

The idea is that Postrgres operates on a host server machine as a multi-process background server.

When you start Postgres on a server, it launches a supervisor background process known as postmaster.

This process listens on a specific network port (defaulting to 5432) for incoming network connections.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/postmaster-listen.light.png" alt="On the Database Server, the postmaster calls listen() on port 5432." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/postmaster-listen.dark.png" alt="On the Database Server, the postmaster calls listen() on port 5432." />
</figure>

Pull the Postgres Docker image:

```bash
docker pull postgres:17
```

Start a Postgres instance on port 5432 with 512MB memory:

```bash
docker run -d \
  --name test-pg-conns \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  --memory=512m \
  --memory-swap=512m \
  postgres:17
```

### Phase 2 : Application <-> Database TCP Handshake

The Application has to use the Database to persist the data and querying it to serve the business logic.
The Application Server uses a Database Client which does these operations.

First the client establishes a connection with the Database server by connecting to the port 5432 where the postmaster is listening.

The client picks a free port, for eg - 5123 and sends SYN to the Database Server on port 5432.
The Database Server replies wirh SYN-ACK.
The client then sends ACK and the TCP handshake is complete thus establishing the connection between the Database client and the Database Server

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/tcp-handshake.light.png" alt="The Database Client connects to port 5432 on the Database Server. The TCP handshake runs between client port 5123 and server port 5432." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/tcp-handshake.dark.png" alt="The Database Client connects to port 5432 on the Database Server. The TCP handshake runs between client port 5123 and server port 5432." />
</figure>

Install Go:

<div class="tabset">
<input class="tabr" type="radio" name="go-os" id="go-mac" checked>
<input class="tabr" type="radio" name="go-os" id="go-win">
<input class="tabr" type="radio" name="go-os" id="go-lin">
<div class="tabnav">
<label for="go-mac">macOS</label>
<label for="go-win">Windows</label>
<label for="go-lin">Linux</label>
</div>
<div class="tabpanes">
<div class="pane pane-go-mac">
<pre><code>brew install go</code></pre></div>
<div class="pane pane-go-win">
<pre><code>winget install GoLang.Go</code></pre></div>
<div class="pane pane-go-lin">
<pre><code>sudo snap install go --classic</code></pre></div>
</div>
</div>

Create a Go program that connects to the Postgres instance we started:

```bash
mkdir connect && cd connect
go mod init connect
go get github.com/jackc/pgx/v5
```

```go
package main

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5"
)

func main() {
	ctx := context.Background()

	conn, err := pgx.Connect(ctx, "postgres://postgres:password@localhost:5432/postgres")
	if err != nil {
		fmt.Println("connect:", err)
		return
	}
	defer conn.Close(ctx)

	fmt.Println("connected")
}
```

Run it:

```bash
go run main.go
```

Output:

```
connected
```

Now change the port in the connection string from `5432` to `5433` and run it again:

```
connect: failed to connect to `user=postgres database=postgres`: 127.0.0.1:5433 (localhost): dial error: dial tcp 127.0.0.1:5433: connect: connection refused
```

Nothing is listening on port 5433, so the TCP handshake fails. Change the port back to `5432`.

### Phase 3 : Postmaster accepts the connection

Postmaster accepts the connection after the TCP handshake and forks a new child process.
These child processes are backend processes which gets the connection and they can communicate with each other using semaphores and shared memory to maintain the data integrity throughout the concurrent data access.

Once a connection is established, the client can now send a query in plain text form to the Database backend process and the backend process parses the query, creates a plan, and returns the results over the connection.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/postmaster-accept.light.png" alt="The postmaster accepts the connection on port 5432 and forks a child process. The Database Client on port 5123 and the child process then exchange the query and the query results." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/postmaster-accept.dark.png" alt="The postmaster accepts the connection on port 5432 and forks a child process. The Database Client on port 5123 and the child process then exchange the query and the query results." />
</figure>

Update the program to execute a query on the connection:

```go
package main

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5"
)

func main() {
	ctx := context.Background()

	conn, err := pgx.Connect(ctx, "postgres://postgres:password@localhost:5432/postgres")
	if err != nil {
		fmt.Println("connect:", err)
		return
	}
	defer conn.Close(ctx)

	var pid int
	err = conn.QueryRow(ctx, "SELECT pg_backend_pid()").Scan(&pid)
	if err != nil {
		fmt.Println("query:", err)
		return
	}
	fmt.Println("backend pid:", pid)
}
```

Run it:

```bash
go run main.go
```

Output:

```
backend pid: 87
```

The query execution was successful over the connection.

## What is Connection Pooling?

Postgres uses a multi-process architecture where one process is allowed per connection.
So one connection cannot run 2 queries at the same time. Try it with the connection code from Phase 2. Run 2 queries in parallel on the same connection:

```go
package main

import (
	"context"
	"fmt"
	"sync"

	"github.com/jackc/pgx/v5"
)

func main() {
	ctx := context.Background()

	conn, err := pgx.Connect(ctx, "postgres://postgres:password@localhost:5432/postgres")
	if err != nil {
		fmt.Println("connect:", err)
		return
	}
	defer conn.Close(ctx)

	var wg sync.WaitGroup
	for i := 1; i <= 2; i++ {
		wg.Go(func() {
			var pid int
			err := conn.QueryRow(ctx, "SELECT pg_backend_pid() FROM pg_sleep(1)").Scan(&pid)
			fmt.Println("query", i, "pid:", pid, "error:", err)
		})
	}
	wg.Wait()
}
```

```bash
go run main.go
```

Output:

```
query 2 pid: 0 error: conn busy
query 1 pid: 87 error: <nil>
```

The connection serves one query at a time. The second query fails because the first query still uses the connection.

The Application Server handles multiple requests at a given time.

For handling multiple requests that expect to run queries on the database, establishing a new connection for each process every time using the TCP handshake is considered as a heavy tax before a single byte of actual data is allowed.

Connection Pooling is used to solve this exact bottleneck.
A Connection Pooler maintains a fixed set of pre-established Database connections which are reused across the Application Server requests.

The Connection Pool acts as a cache of already established connections which the Application process borrows, executes the query, and then releases the connection back to the cache when done. The connection then is ready to be picked by other processes.



If there are no connections available in the pool, then the request is queued and have to wait for one to be released.
A timeout is configured on how much the request is allowed to wait in the queue. If the wait time is exceeded, the query is marked as failed.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/connection-pool.light.png" alt="The Application Server holds a Connection Pool with 3 open connections to the Database. Requests 1 to 3 borrow a connection and release it. Request 4 waits in a queue until a connection is free." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/connection-pool.dark.png" alt="The Application Server holds a Connection Pool with 3 open connections to the Database. Requests 1 to 3 borrow a connection and release it. Request 4 waits in a queue until a connection is free." />
</figure>

Install the pool package:

```bash
go get github.com/jackc/pgx/v5/pgxpool@v5.11.0
```

Update the program to use a connection pool and run the same 2 queries in parallel:

```go
package main

import (
	"context"
	"fmt"
	"sync"

	"github.com/jackc/pgx/v5/pgxpool"
)

func main() {
	ctx := context.Background()

	pool, err := pgxpool.New(ctx, "postgres://postgres:password@localhost:5432/postgres")
	if err != nil {
		fmt.Println("pool:", err)
		return
	}
	defer pool.Close()

	var wg sync.WaitGroup
	for i := 1; i <= 2; i++ {
		wg.Go(func() {
			var pid int
			err := pool.QueryRow(ctx, "SELECT pg_backend_pid() FROM pg_sleep(1)").Scan(&pid)
			fmt.Println("query", i, "pid:", pid, "error:", err)
		})
	}
	wg.Wait()
}
```

Run it:

```bash
go run main.go
```

Output:

```
query 2 pid: 88 error: <nil>
query 1 pid: 87 error: <nil>
```

Both queries succeed. The pool opened a second connection, so each query ran on a different backend process.

## Understanding Connection Limits

Your Application Server and the User API  requests are not the only services served by the Database instance concurrently.

At a given time, it can also serve:
- ETL jobs
- Admin Operations
- Scheduled cleanup jobs

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/database-clients.light.png" alt="The Database serves App Servers, ETL Jobs, Admin Ops, and Scheduled Cleanup Jobs at the same time." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/database-clients.dark.png" alt="The Database serves App Servers, ETL Jobs, Admin Ops, and Scheduled Cleanup Jobs at the same time." />
</figure>

So there are 2 places where connection limits are set and configured:

### 1. Max Connections

Defines the maximumn number of concurrent connections the Database instance can handle for all the jobs it's serving.

For Postgres, the default value is 100 for setting named `max_connections`.

```go
package main

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5"
)

func main() {
	ctx := context.Background()
	url := "postgres://postgres:password@localhost:5432/postgres"

	conn, err := pgx.Connect(ctx, url)
	if err != nil {
		fmt.Println("connect:", err)
		return
	}
	defer conn.Close(ctx)

	var maxConnections string
	err = conn.QueryRow(ctx, "SHOW max_connections").Scan(&maxConnections)
	if err != nil {
		fmt.Println("query:", err)
		return
	}
	fmt.Println("max_connections:", maxConnections)

	for i := 2; ; i++ {
		c, err := pgx.Connect(ctx, url)
		if err != nil {
			fmt.Println("connection", i, "failed:", err)
			return
		}
		defer c.Close(ctx)
	}
}
```

```bash
go run main.go
```

Output:

```
max_connections: 100
connection 101 failed: failed to connect to `user=postgres database=postgres`: 127.0.0.1:5432 (localhost): server error: FATAL: sorry, too many clients already (SQLSTATE 53300)
```

The value of `max_connections` depends on the memory size of the instance.
One connection uses about 12 MiB of memory.

Best case scenario:

max_connections ≈ 50% of memory / 12 MiB

So around 2 GiB memory for 100 connections.

Configure the `max_connections` value accordingly.  
4 GiB -> 200 max_connections  
8 Gib -> 400 max_connections

Configuring a higher value of `max_connections` than what is recommended for memory size will cause Out of Memory (OOM) Database crashes.

### 2. Max Pool Size

In the last section we discussed about the connection limits on a Database.
But each of the service that is using the Database uses a Connection Pool and the Pool sets their own connection limits.  

The Connection Pool is a shared resource used by multiple process but there is a limit on the number of connections that the Pool can maintain.  

The value for max_pool_size should always be configured to be less than max_connections.  

Checking the max pool size of `pgxpool` and running 150 requests in parallel:

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

func main() {
	ctx := context.Background()

	pool, err := pgxpool.New(ctx, "postgres://postgres:password@localhost:5432/postgres")
	if err != nil {
		fmt.Println("pool:", err)
		return
	}
	defer pool.Close()

	fmt.Println("max pool size:", pool.Config().MaxConns)

	var wg sync.WaitGroup
	for i := 1; i <= 150; i++ {
		wg.Go(func() {
			start := time.Now()
			reqCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
			defer cancel()

			var pid int
			err := pool.QueryRow(reqCtx, "SELECT pg_backend_pid() FROM pg_sleep(1)").Scan(&pid)
			if err != nil {
				fmt.Println("request", i, "error:", err, "time:", time.Since(start).Round(time.Millisecond))
				return
			}
			fmt.Println("request", i, "pid:", pid, "time:", time.Since(start).Round(time.Millisecond))
		})
	}
	wg.Wait()
}
```

```bash
go run main.go
```

Output:

```
max pool size: 12
request 7 pid: 91 time: 1.015s
request 3 pid: 87 time: 1.016s
request 12 pid: 94 time: 1.017s
...
request 31 pid: 91 time: 3.032s
...
request 118 pid: 88 time: 9.061s
...
request 139 error: context deadline exceeded time: 10.001s
request 150 error: context deadline exceeded time: 10.001s
```

Here there are total 12 max connections in the Pool.  
The wait time for each request is configured to be 10 seconds.  
There are 150 requests trying to use the 12 connections at the same time.
As one conbection can be only used by one request at a time, some of the requests have to wait for the connection to released.  
Few connections had to wait beyond the allowed wait time of 10 seconds and they failed with a timeout error.  

This is what's happening here:
<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/connection-limits.light.png" alt="150 requests reach the server. 12 requests each use one of the 12 connections, conn 1 to conn 12, in the pool. The 12 connections end in a small box inside a large box in the database. The large box shows the 100 connections the database allows. The small box holds the 12 taken by the pool. The other 138 requests, Request 13 to Request 150, wait in a queue for a free connection. A request that waits more than 10 seconds times out with a context deadline exceeded error." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/connection-limits.dark.png" alt="150 requests reach the server. 12 requests each use one of the 12 connections, conn 1 to conn 12, in the pool. The 12 connections end in a small box inside a large box in the database. The large box shows the 100 connections the database allows. The small box holds the 12 taken by the pool. The other 138 requests, Request 13 to Request 150, wait in a queue for a free connection. A request that waits more than 10 seconds times out with a context deadline exceeded error." />
</figure>

## Incident Deep Dives

The [Black Friday Outage](https://medium.com/@aniruddhasonawane/the-black-friday-outage-that-wasnt-about-cpu-memory-or-traffic-it-was-a-database-connection-bccc1c57499c) incident explains that the default Max Pool Size set was too low for the Connection Pool to handle the traffic.  
There was nothing wrong with how the Application Server scaled and no bottlenecks on the Database side.  
But due to the limited pool size, the high traffic requests were waiting for the connections to be released by the Pool and were timing out.

Another [post](https://www.linkedin.com/posts/absar0920_databaseoptimization-postgresql-systemdesign-share-7503603400136159232-8KLI/) here explains that multiple Application Servers scaled up used their own Connection Pools.   
An outage was caused because together the total number of connections by the Pools exceeded the max_connections limit on the Database.  

Configuring the Max Pool Size used by the Services and Max Connections on the Database is all about tuning the right values such that:  

- The Connection Pool Size is able to serve the traffic of requests asking for the connections.
- The total connections opened by the Connection Pools across the Services is always less than the Max Connections value on the Database Instance being accessed by the services.  

These are examples of other such incidents caused due to misconfigurations of the connection limits:

- [Resend, 2026-02-15](https://www.resend.com/blog/incident-report-for-february-15-2026): a service went from about 60 to over 330 connections because the max pool size was too high. The database hit its connection limit.
- [Buttondown, 2026-03-31](https://buttondown.com/blog/incident-0024): the `max_connections` value was set a long time ago and never revisited as traffic grew.
- [Honeycomb, 2018-05-03](https://web.archive.org/web/2019/https://www.honeycomb.io/blog/rds-performance-degradation-postmortem/): slow queries made the Go MySQL pool open more connections. They exceeded `max_connections` (Error 1040).
- [Alpaca, 2021-11-09](https://status.alpaca.markets/incidents/68rj5kdbpcxd): connections stayed "idle in transaction" while the service pool counted them as in use.
- [Val Town, 2024-12-31](https://blog.val.town/blog/post-mortem-exhausted-host-connection-pool): deadlocked queries had no timeout, so they held pool connections forever.
- [Python Discord, 2020-12-11](https://docs.pydis.wtf/post-mortems/2020/12/11/postgres-connection-surge.html): Postgres reached 100 clients and returned `sorry, too many clients already`. The authors suspect connections were not closed.
- [ImprovMX, 2025-09-24](https://improvmx.com/blog/2025-09-23-post-mortem): connections spiked about 30 times and overloaded the SQL connection pool.
- [GitLab.com, 2022-05-26](https://gitlab.com/gitlab-com/gl-infra/production/-/issues/7139): a config change doubled the connections to the replicas. An alert caught it and customers saw no impact.

## Tuning the Connection Limit Values

We start with one server, one connection pool and one database instance.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/simple-service.light.png" alt="A simple service. Users call one Server, and the Server calls one Database instance." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/simple-service.dark.png" alt="A simple service. Users call one Server, and the Server calls one Database instance." />
</figure>

Assume:

- A request takes 100 ms:
  - 20 ms of server CPU.
  - 50 ms in the database.
  - 30 ms of other waits: network and calls to other services.
- The server has 1 core.
- The database has 2 GiB of memory and `max_connections` set to 100.

### Requests per second the server can handle

One core runs one thing at a time. A request uses 20 ms of CPU.

1 / 0.02 = 50 requests in each second. This is the absolute maximum.

Waits start to grow at about 70% busy, because requests arrive in bursts.

70% of 50 = 35 requests in each second.

### Requests per second the database can handle

The database spends 50 ms on a request, so one connection serves 1 / 0.05 = 20 requests in each second.

100 connections × 20 = 2,000 requests in each second. This is the absolute maximum.

70% of 2,000 = 1,400 requests in each second.

### Ideal connection pool size

Connections in use = requests per second × the time a request holds a connection.

35 × 0.05 s = 1.75 connections. We round up to 2.

The ideal max pool size is 2.

With more cores on the server and more memory on the database:

| Server cores | Database memory | max_connections | Requests/sec | Ideal pool size |
| --- | --- | --- | --- | --- |
| 1 | 2 GiB | 100 | 35 | 2 |
| 2 | 4 GiB | 200 | 70 | 4 |
| 4 | 8 GiB | 400 | 140 | 7 |
| 8 | 16 GiB | 800 | 280 | 14 |
| 16 | 32 GiB | 1,600 | 560 | 28 |
| 32 | 64 GiB | 3,200 | 1,120 | 56 |

These calculations are considering only single Application Server and a single Database instance.  
When an Application Service is scaled horizontally, the Connection Pool Size multiples by the number of instances added.  
When a Database instance is scaled horizontally, the Max Connections is multiplied by the number of instances added.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/pool-layout.light.png" alt="Three application servers with 8 cores each and two database instances with 2 GiB of RAM and max_connections 100 each. Every server has one connection pool to each database, 6 pools in all, and each pool holds 14 connections. Inside each database, a dotted box shows max_connections 100 and holds three boxes of 14, one per server pool. The pools use 42 connections in all." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/pool-layout.dark.png" alt="Three application servers with 8 cores each and two database instances with 2 GiB of RAM and max_connections 100 each. Every server has one connection pool to each database, 6 pools in all, and each pool holds 14 connections. Inside each database, a dotted box shows max_connections 100 and holds three boxes of 14, one per server pool. The pools use 42 connections in all." />
</figure>
