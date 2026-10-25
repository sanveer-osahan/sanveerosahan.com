---
title: "Testing Postgres Max Connections"
description: ""
publishDate: 2026-10-19
draft: true
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
<!--
  connection-limits: 150 requests, a pool of 12 and a database that allows 100.
  SINGLE SOURCE: references/testing-postgres-max-connections/components/connection-limits.gen.py
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-connection-limits">
<style>
@font-face{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,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) format("woff2");
}
.diagram-connection-limits{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}
.diagram-connection-limits svg{display:block;width:100%;height:auto;color:inherit}
</style>
<svg viewBox="0 0 1080 650" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="150 requests reach the server. 12 requests each use one of the 12 connections, conn 1 to conn 12, in the pool. The 12 connections end in a small box inside a large box in the database. The large box shows the 100 connections the database allows. The small box holds the 12 taken by the pool. The other 138 requests, Request 13 to Request 150, wait in a queue for a free connection. A request that waits more than 10 seconds times out with a context deadline exceeded error.">
  <text x="40" y="40" font-size="18" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">150 requests</text><path d="M40.52,120.58 C66.67,121.84 91.02,120.63 169.47,122.6 M39.88,121.49 C84.65,120.27 131.76,120.03 169.74,121.94 M170.01,121.98 C169.53,134.46 171.55,147.08 171.97,157.11 M170.31,122.21 C169.28,134.63 169.39,148.77 170.15,158.02 M171.14,159.76 C121.69,156.48 72.61,156.02 39.63,157.51 M169.97,158.66 C128.18,158.81 86.04,159.56 40.78,157.75 M38.99,157.26 C40.58,151.41 39.27,141.3 39.18,120.38 M40.42,158.03 C39.47,148.92 40.47,138.46 40.33,122.59" stroke-width="1.8" opacity="1.0"/><text x="105" y="146" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 1</text><path d="M174.68,140.25 C209.9,141.66 250.66,140.74 284.23,139.16 M173.9,139.87 C197.42,140.04 219.54,139.6 285.9,139.77 M285.02,139.89 C284.11,137.54 280.1,138.47 274.48,133.82 M285.88,139.76 C281.05,138.01 276.72,136.05 274.39,134.06 M285.43,138.86 C281.48,141.47 279.72,144.63 275.31,145.73 M285.78,140.34 C284.1,140.62 280.93,142.15 274.76,146.14" stroke-width="1.8" opacity="1.0"/><path d="M288.77,121.95 C321.35,120.26 352.53,121.57 400.53,123.87 M290.41,123.78 C334.63,121.87 377.13,123.07 400.94,122.05 M401.35,121.31 C398.5,133.41 399.82,142.03 401.64,158.49 M399.82,123.91 C399.35,135.17 400.35,145.86 400.34,156.77 M398.77,158.88 C370.62,156.44 341.63,154.7 289.03,157.03 M399.45,156.35 C368.36,155.61 335.18,155.88 290.26,156.3 M289.2,157.88 C289.93,149.69 288.1,143.34 290.66,124.22 M289.1,156.77 C290.24,146.56 289.48,135.13 290.25,123.43" stroke-width="1.6" opacity="1.0"/><text x="345" y="145" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">conn 1</text><path d="M402.67,140.4 C527.83,141.28 653.85,142.29 730.42,140.3 M403.66,140.23 C498.55,138.12 593.24,137.84 731.17,140.5 M731.47,138.85 C727.13,137.63 725.09,136.35 718.49,135.54 M731.4,139.71 C726.58,137.51 722.42,135.6 719.36,134.78 M731.74,140.88 C725.94,142.24 723.18,144.13 719.36,144.68 M730.62,140.55 C727.22,141.92 723.69,143.78 719.88,144.9" stroke-width="1.8" opacity="1.0"/><path d="M38.98,177.9 C82.47,179.3 121.09,176.93 169.91,176.25 M39.14,177.92 C90.1,175.55 139.07,175.8 170.65,177.21 M171.05,178.43 C169.75,187.33 170.62,201.78 171.41,211.69 M170.76,177.01 C170.27,186.67 169.97,196.14 169.59,213.19 M170.26,211.54 C137.59,213.21 106.74,211.81 40.72,212.51 M169.85,212.14 C119.26,213.6 69.24,214.71 39.58,213.37 M40.2,212.91 C40.85,200.26 41.3,191.85 38.43,177.55 M39.64,213.14 C39.67,202.02 40.4,190.08 39.04,177.5" stroke-width="1.8" opacity="1.0"/><text x="105" y="201" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 2</text><path d="M172.54,196.96 C210.65,195.62 247.79,194.94 284.14,196.24 M174.41,194.95 C203.59,194.9 234.27,194.68 285.81,194.37 M286.8,195.25 C284.48,194.91 280.23,193.31 274.59,190.67 M286.1,195.43 C281.52,192.64 277.96,190.93 273.75,189.26 M286.87,195.38 C283.69,195.63 280.45,198.67 274.31,201.62 M285.67,194.82 C283.08,196.75 280.56,197.59 274.78,201.06" stroke-width="1.8" opacity="1.0"/><path d="M289.73,179.26 C332.78,180.5 375.07,180.3 398.26,176.78 M290.09,178.62 C331.26,178.82 371.32,178.36 400.03,177.93 M399.8,178.48 C402.28,187.69 399.66,194.78 400.36,213.23 M399.69,177.59 C400.26,188.57 400.04,198.51 400.38,211.82 M401.29,211.93 C376.13,211.33 353.07,210.2 290.34,210.67 M399.91,211.97 C371.53,210.97 344.12,211.55 290.76,211.85 M290.14,210.61 C291.27,202.46 288.81,191.78 289.12,176.68 M289.06,211.74 C289.87,200.52 290.16,190.65 289.84,178.42" stroke-width="1.6" opacity="1.0"/><text x="345" y="200" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">conn 2</text><path d="M404.13,194.19 C508.85,192.37 615.92,192.94 729.84,194.39 M403.69,194.91 C494.93,194.91 585.75,194.29 731.47,194.51 M730.38,194.91 C727.9,193.08 723.2,192.79 718.59,189.96 M731.15,195.01 C726.28,192.29 721.94,190.05 719.73,189.36 M732.28,196.11 C727.56,197.37 722.85,197.52 719.64,201.07 M731.15,194.59 C728.23,196.22 725.13,197.89 718.7,200.26" stroke-width="1.8" opacity="1.0"/><path d="M38.04,232.01 C79.99,231.77 117.08,232.11 171.63,230.48 M39.32,231.23 C84.6,232.64 130.68,231.75 170.19,231.4 M170.91,231.71 C171.65,243.12 169.33,252.63 170.7,269.58 M169.8,231.23 C170.91,242.13 170.78,250.61 170.18,267.49 M168.28,268.23 C120.89,269.55 72.03,269.68 38.74,266.08 M170.14,267.47 C135.53,267.91 99.98,267.92 39.5,267.45 M39.82,268.62 C40.11,256.35 39.09,242.81 38.44,232.08 M40.05,267.76 C40.71,259.75 39.35,252.83 40.34,233" stroke-width="1.8" opacity="1.0"/><text x="105" y="256" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 3</text><path d="M174.68,250.94 C208.23,249.52 245.67,250.47 284.09,250.71 M173.24,250.51 C206.33,248.44 238.58,249.25 286.01,249.72 M285.1,249.82 C281.77,248.35 280.46,246.6 273.24,244.72 M286.61,250.35 C283.3,248.16 280.47,247.66 273.66,244.93 M285.49,249.78 C282.94,250.71 277.5,253.03 273.82,256.46 M286.5,250.59 C281.83,251.62 276.86,254.68 274.85,254.93" stroke-width="1.8" opacity="1.0"/><path d="M288.47,231.61 C321.67,232.89 354.69,235.32 401.58,234.48 M290.4,232.46 C315.42,234.12 339.46,232.9 400.12,233.24 M401.53,231.05 C399.19,239.56 399.69,246.16 398.13,268.46 M400.91,232.99 C400.03,244.22 400.64,253.57 400.17,267.02 M401.86,266.36 C362.76,268.91 327.63,268.08 288.03,266.23 M400.27,266.99 C377.83,268.02 353.2,267.89 290.81,266.78 M290.49,266.06 C288.63,256.59 288.38,250.08 288.71,233.36 M290.38,266.04 C290.32,256.71 290.31,247.43 290.29,233.49" stroke-width="1.6" opacity="1.0"/><text x="345" y="255" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">conn 3</text><path d="M403.68,250.04 C492.83,253.34 583.65,251.22 730.75,248.81 M404.45,249.77 C497.4,247.95 590.94,248.44 730.89,249.46 M730.98,251.13 C725.98,249.12 723.17,246.27 720.48,243.69 M731.26,249.53 C726.78,247.54 722.7,245.38 719.53,244.04 M730.21,249.69 C727.46,251.6 725.72,251.09 719.53,256.12 M730.4,249.76 C727.09,251.85 723.25,253.83 718.69,255.76" stroke-width="1.8" opacity="1.0"/><path d="M39.17,326.47 C69.52,325.93 103.93,327.32 169.02,327.8 M39.46,327.36 C71.12,325.64 100.79,326.79 170.82,326.84 M171.49,325.24 C169.03,334.38 169.6,344.86 171.6,363.3 M169.94,327 C169.58,339.19 170.31,352.7 169.86,362.23 M170.39,362.77 C131.56,360.24 91.12,362.21 39.9,361.06 M169.85,363.94 C122.32,362.22 74.63,363.27 39.34,363.76 M40.11,363.29 C40.92,355.33 41.34,344.58 39.71,326.94 M39.74,362.03 C40.32,353.51 40.23,345.56 39,326" stroke-width="1.8" opacity="1.0"/><text x="105" y="351" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 12</text><path d="M175.32,344.82 C196.79,345.1 221.38,345.39 286.19,346.36 M173.87,345.85 C203.53,345.97 231.96,345.01 286.63,345.18 M285.19,345.73 C283.92,342.36 280.51,341.31 275.47,340.26 M285.75,344.83 C283.18,344.21 280.51,342.87 274.55,339.19 M285.67,343.94 C281.88,345.63 279.86,348.78 273.74,350.73 M285.79,345.2 C282.69,347.25 279.25,348.02 273.89,350.01" stroke-width="1.8" opacity="1.0"/><path d="M290.57,328.97 C325.63,326.97 362.74,327.09 400.19,329.14 M290.22,327.57 C325.54,329.85 360.27,327.98 400.94,327.63 M400.15,329.76 C399.23,340.66 401.9,350.31 398.94,361.6 M399.12,328.39 C399.93,336.86 399.81,344.82 400.77,361.48 M400.43,362.88 C372.66,361.41 342.37,361.85 291.39,361.06 M399.69,361.55 C358.95,360.28 315.75,361.12 289.49,361.34 M288.8,361.41 C290.94,347.72 289.41,336.11 290.54,326.17 M290.99,361.32 C289.26,351.2 290.17,339.58 289.3,327.14" stroke-width="1.6" opacity="1.0"/><text x="345" y="350" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">conn 12</text><path d="M404.1,343.63 C508.14,343.4 611.13,344.38 731.44,343.97 M404.19,345.59 C479.89,342.83 554.27,343.5 730.7,344.5 M729.83,345.52 C728.11,342.39 723.19,343.08 720.04,340.13 M730.92,345.56 C727.63,343.44 725.04,342.37 719.07,338.88 M730.75,345.2 C727.88,345.36 725.32,349.18 720.17,350.23 M730.49,344.85 C727.01,346.81 722.05,348.72 719.3,350.4" stroke-width="1.8" opacity="1.0"/><text x="105" y="302" font-size="22" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">...</text><text x="345" y="302" font-size="22" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">...</text><path d="M249.09,74.28 C335.27,73.76 419.09,74.28 629.1,74.89 M250.52,75.29 C383.59,75.37 518.74,75.56 630.53,74.68 M629.96,76.11 C628.81,154.04 627.89,231.91 629.6,395.38 M630.3,74.33 C630.69,140.6 631.46,206.35 630.45,395.44 M629.62,394.09 C513.8,395.62 398.1,396.78 250.33,395.94 M630.4,395.52 C528.25,393.81 425.22,393.68 250.29,394.78 M251.14,393.71 C249.34,297.29 249.87,202.64 249.32,75.87 M249.38,395.65 C251.15,297.78 251,201.77 249.48,75.32" stroke-width="1.8" opacity="0.5" stroke-dasharray="1 8"/><text x="440" y="100" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Pool: 12 connections</text><text x="885" y="40" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Database</text><path d="M967.9,51.1 C1004.63,53.73 1041.46,60.22 1058.13,65.2 C1074.8,70.19 1078.86,75.83 1067.93,81.03 C1057,86.24 1026.25,93.35 992.55,96.44 C958.85,99.53 906.4,100.09 865.74,99.56 C825.08,99.02 776.94,96.88 748.6,93.24 C720.27,89.59 698.77,83.34 695.71,77.68 C692.65,72.02 706.37,63.9 730.26,59.29 C754.15,54.68 815.54,51.66 839.05,50.03 C862.57,48.41 860.66,49.58 871.36,49.54 C882.07,49.5 903.2,49.3 903.27,49.79 M837.76,49.46 C874.74,47.71 931.17,48.48 967.9,51.1 C1004.63,53.73 1041.46,60.22 1058.13,65.2 C1074.8,70.19 1078.86,75.83 1067.93,81.03 C1057,86.24 1026.25,93.35 992.55,96.44 C958.85,99.53 906.4,100.09 865.74,99.56 C825.08,99.02 776.94,96.88 748.6,93.24 C720.27,89.59 698.77,83.34 695.71,77.68 C692.65,72.02 706.37,63.9 730.26,59.29" stroke-width="1.8" opacity="1.0"/><path d="M694.69,75.25 C697.64,160.21 695.82,244.12 696.05,404.21 M694.54,75.53 C696.31,187.9 696.44,301.43 694.81,405.09 M1073.93,75.05 C1074.78,160.16 1073.98,244.85 1073.89,404.29 M1074.57,75.09 C1073.51,181.99 1073.25,288.69 1075.04,404.77" stroke-width="1.8" opacity="1.0"/><path d="M1074.68,404.35 C1073.6,405.57 1072.48,409.48 1068.24,411.68 C1064,413.88 1057.53,415.49 1049.24,417.53 C1040.94,419.57 1029.96,422.38 1018.48,423.94 C1007,425.49 994.5,425.76 980.37,426.85 C966.24,427.95 949.73,429.82 933.71,430.5 C917.69,431.18 900.55,431.06 884.26,430.91 C867.97,430.76 851.61,430.26 835.95,429.62 C820.29,428.99 804.47,428.24 790.29,427.11 C776.1,425.98 762.64,424.35 750.84,422.83 C739.04,421.31 727.62,419.71 719.5,417.99 C711.37,416.27 706.34,414.78 702.11,412.49 C697.88,410.2 695.46,405.61 694.13,404.24 M1074.82,405.14 C1073.78,406.23 1072.94,409.44 1068.58,411.66 C1064.23,413.89 1057.02,416.68 1048.69,418.51 C1040.36,420.34 1030.05,421.01 1018.61,422.64 C1007.16,424.28 994.24,427.23 980.03,428.32 C965.83,429.41 949.32,428.71 933.37,429.18 C917.43,429.65 900.61,431.12 884.37,431.14 C868.12,431.17 851.72,429.79 835.92,429.3 C820.12,428.81 803.87,429.04 789.55,428.2 C775.23,427.37 761.54,425.92 750,424.28 C738.46,422.65 728.32,420.35 720.31,418.4 C712.31,416.44 706.07,414.69 701.97,412.57 C697.88,410.45 696.79,406.83 695.75,405.68" stroke-width="1.8" opacity="1.0"/><path d="M715.92,106.26 C810.4,105.39 905.36,104.4 1053.91,106.24 M714.45,104.76 C841.56,104.89 968.4,104.52 1054.42,104.5 M1056.06,104.33 C1057.14,167.68 1055.89,232.87 1055.67,380.57 M1054.49,104.61 C1056.23,189.45 1056.22,273.05 1055.44,380.24 M1056,381.01 C931.88,378.17 807.44,377.82 716.2,378.9 M1054.43,379.57 C958.54,381.86 862.44,381.62 715.1,380.26 M715.11,379.52 C714.24,311.95 713.72,243.97 713.79,106.01 M714.51,379.38 C715,319.41 716.12,257.64 715.62,105.31" stroke-width="1.8" opacity="1.0" stroke-dasharray="1 8"/><text x="962" y="148" font-size="14" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">max_connections: 100</text><path d="M735.76,124.55 C785.51,125.01 839.77,127.5 865.76,124.89 M735.06,125.37 C765.74,124.23 794.7,123.46 864.33,124.55 M865.48,124.15 C865.05,186.18 865.62,245.58 864.18,365.91 M865.13,124.25 C867.44,178.98 866.8,233.43 865.02,365.67 M865.82,363.23 C828.85,368.07 792.49,366.36 734.27,366.92 M865.05,365.03 C817.88,365.74 773.14,365.97 734.36,364.23 M734.37,366.02 C735.13,282.85 734.02,201.79 734.07,126.21 M735.82,364.55 C736.13,310.82 735.9,256.93 734.6,124.19" stroke-width="1.8" opacity="1.0" stroke-dasharray="1 8"/><text x="800" y="240" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">12 taken</text><text x="800" y="262" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">by the pool</text><text x="480" y="438" font-size="16" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Queue</text><path d="M40.03,450.74 C209.57,449.79 378.65,451.17 569.28,450.37 M39.82,450.38 C199.98,448.92 359.02,448.57 570.05,450.03 M569.54,451.34 C570.76,467.29 569.61,487.11 568.94,504.75 M570.26,449.9 C570.56,468.54 570.55,487.93 569.14,505.71 M570.56,505.49 C360.21,506.07 150.09,506.02 39.83,506.75 M570.34,505.86 C453.34,505.2 337.2,504.72 39.64,505.96 M40.19,506.12 C39.65,490.09 40.92,474.28 40.89,451.2 M39.45,505.77 C41,489.47 41.32,472.68 40.79,450.49" stroke-width="1.8" opacity="1.0"/><path d="M49.54,457.21 C78.98,456.25 105.84,457.98 148.83,459.65 M49.63,458.36 C72.1,458.72 92.02,458.9 149.26,457.9 M148.31,456.67 C148.33,473.79 149.26,487.19 148.73,498.62 M149.35,457.18 C150.58,471.2 149.65,483.71 149.8,497.19 M149.63,497.57 C118.82,498.76 89.25,495.4 51.09,499.11 M149.58,497.46 C123.69,498.02 94.5,497.44 49.75,497.05 M48.33,498.77 C47.96,487.6 49.46,473.24 48.43,457.52 M49.57,497.03 C49.71,483.79 49.17,468.94 50.42,457.36" stroke-width="1.6" opacity="1.0"/><text x="100" y="483" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 13</text><path d="M159.95,459.95 C187.09,456.05 212.25,456.56 260.54,457.73 M159.42,458.63 C192.91,458.64 225.87,459.41 260.82,457.62 M259.94,458.9 C260.3,469.82 261.65,481.14 258,498.9 M260.57,457.24 C259.7,470.18 260.42,482.75 259.89,497.48 M261.72,497.47 C235.67,499.24 213.02,500.09 159.3,498.21 M260.85,498.45 C220.26,498.64 180.48,499.29 160.38,498.66 M158.14,496 C159.6,483.27 160.34,471.26 161.96,456.78 M160.72,498.48 C159.38,482.09 159.78,467.18 159.53,457.62" stroke-width="1.6" opacity="1.0"/><text x="210" y="483" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 14</text><path d="M269.25,457.83 C302.55,457.57 339.98,459.48 370.46,459.91 M270.09,458.06 C301.33,457.7 333.28,458.08 370.63,457.05 M368.91,458.95 C371.25,467.39 370.03,473.96 368.96,496.94 M369.86,458.77 C370.01,468.32 369.77,478.78 369.54,497.16 M370.35,496.64 C333.33,497.68 297.74,498.22 269.73,498 M370.31,498.71 C333.91,498.62 299.11,497.19 270.57,498.05 M271.81,498.42 C268.18,483.88 270.76,469.27 270.76,456.81 M269.08,498.3 C269.27,486.07 270.09,473.5 269.17,458.41" stroke-width="1.6" opacity="1.0"/><text x="320" y="483" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 15</text><path d="M441.94,459.74 C473.96,458.05 504.3,455.29 559.16,457.73 M439.75,457.41 C479.05,457.27 516.07,456.45 560.3,457.12 M558.83,456.91 C560.47,465.33 558.4,476.02 561.64,499.27 M559.46,458.34 C560.69,471.33 560.68,485.57 560.58,498.11 M559.76,496.19 C517.32,497.79 475.68,498.48 440.18,499.09 M560.68,497.2 C517.38,498.52 473.74,498.89 439.58,498.17 M441.8,499.12 C441.34,481.13 438.98,468.75 439.11,458.36 M440.91,497.72 C439.26,485.05 440.25,473.19 439.78,457.5" stroke-width="1.6" opacity="1.0"/><text x="500" y="483" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Request 150</text><text x="405" y="488" font-size="22" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">...</text><path d="M100.32,450.57 C144.17,438.69 188.03,425.47 289.23,398.37 M100.16,449.2 C165.11,431.77 230.55,413.93 290.49,397.51 M290.85,398.21 C285.13,396.64 279.65,396.74 276.49,395.71 M289.87,397.87 C287.18,397.37 284.79,396.42 277.31,395.16 M290.19,397.42 C286.85,401.1 283.21,401.92 279.93,407.31 M290.22,397.69 C287.87,399.6 284.77,402.05 280.15,406.6" stroke-width="1.8" opacity="1.0"/><text x="240" y="440" font-size="16" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">wait</text><path stroke="#e03131" d="M231.75,508.04 C231.33,534.64 230.93,560.41 228.78,575.7 M229.75,510.52 C230.62,529.39 229.4,547.42 229.23,577 M230.2,575.81 C231.27,572.75 233.49,567.44 235.71,564.76 M230.6,575.84 C232.41,570.71 234.67,566.4 235.72,564.78 M230.95,576.26 C229.62,573.01 226.43,570.08 223.97,563.24 M229.88,575.88 C228.72,573.9 228.17,571.53 225.01,563.86" stroke-width="1.8" opacity="1.0"/><text x="246" y="550" font-size="16" text-anchor="start" font-family="var(--dg-font-hand)" fill="#e03131" stroke="none">wait &gt; 10s</text><path stroke="#e03131" d="M40.99,579.97 C155.57,580.09 270.35,581.09 418.88,581.06 M40.02,580.12 C174.07,581.47 309,582.09 419.47,579.96 M419.98,580.25 C418.93,597.92 418.27,618.89 420.89,628.26 M420.09,579.51 C420.38,600.24 420.34,619.62 419.95,629.41 M419.09,631.03 C307.86,629.02 194.35,630.01 40.27,630.07 M419.85,629.67 C268.73,630.08 116.44,630.85 39.94,630.11 M40.63,629.78 C40.48,615.36 40.16,602.19 38.31,580.3 M39.81,630.21 C39.81,616.91 40.87,604.7 39.5,579.59" stroke-width="1.8" opacity="1.0"/><text x="230" y="611" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="#e03131" stroke="none">timed out: context deadline exceeded</text>
</svg>
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

<!-- component:simple-service start -->
<!--
  simple-service — the users, one server and one database instance.
  SINGLE SOURCE: references/testing-postgres-max-connections/components/simple-service.gen.py
  Do not edit the copy. Edit the generator and run it.
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-simple-service">
<style>
@font-face{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,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) format("woff2");
}
.diagram-simple-service{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}
.diagram-simple-service svg{display:block;width:100%;height:auto;color:inherit}
</style>
<svg viewBox="0 0 700 200" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="A simple service. Users call one Server, and the Server calls one Database instance.">
  <path d="M40.52,60.58 C68.7,61.75 95.08,60.55 179.47,62.6 M39.88,61.49 C88.16,60.18 138.76,59.94 179.74,61.94 M180.01,61.98 C179.19,88.51 181.21,115.19 181.97,137.11 M180.31,62.21 C179.32,89.16 179.43,117.83 180.15,138.02 M181.14,139.76 C128,136.47 75.23,136.02 39.63,137.51 M179.97,138.66 C134.92,138.89 89.51,139.65 40.78,137.75 M38.99,137.26 C40.34,123.24 39.03,104.98 39.18,60.38 M40.42,138.03 C39.71,118.59 40.7,97.8 40.33,62.59" stroke-width="1.8" opacity="1.0"/><text x="110" y="106" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Users</text><path d="M265.68,62.25 C313.61,63.88 367.1,62.96 413.23,61.16 M264.9,61.87 C296.11,62.13 325.91,61.69 414.9,61.77 M413.5,61.84 C417.4,79.18 415.71,101.52 415.38,137.02 M414.82,61.63 C413.93,90.12 413.92,118.2 415.23,137.38 M414.12,136.25 C366.29,138.43 321.8,140.59 266.65,138.3 M414.66,138.53 C383.92,136.66 350.85,137.19 265.8,138.93 M263.77,136.95 C264.5,114.76 264.48,94.51 265.53,62.87 M265.41,138.78 C265.69,106.76 264.29,77.62 265.94,61.05" stroke-width="1.8" opacity="1.0"/><text x="340" y="106" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Server</text><path d="M592.62,28.2 C609.24,29.4 627.23,31.67 636.73,34.75 C646.23,37.82 651.29,42.88 649.63,46.66 C647.97,50.44 639.01,54.61 626.78,57.42 C614.56,60.23 593.67,63.08 576.28,63.53 C558.89,63.98 536.48,62.53 522.45,60.13 C508.42,57.72 496.08,53.03 492.09,49.1 C488.1,45.16 491.09,39.82 498.5,36.52 C505.9,33.22 527.05,30.88 536.53,29.31 C546,27.74 549.02,27.58 555.34,27.08 C561.67,26.58 574.27,26.02 574.47,26.32 M537.01,27.57 C551.73,25.96 576,27 592.62,28.2 C609.24,29.4 627.23,31.67 636.73,34.75 C646.23,37.82 651.29,42.88 649.63,46.66 C647.97,50.44 639.01,54.61 626.78,57.42 C614.56,60.23 593.67,63.08 576.28,63.53 C558.89,63.98 536.48,62.53 522.45,60.13 C508.42,57.72 496.08,53.03 492.09,49.1 C488.1,45.16 491.09,39.82 498.5,36.52" stroke-width="1.8" opacity="1.0"/><path d="M488.9,43.7 C490.9,73.18 489.26,103.74 490.52,145.59 M489.6,45.44 C489.8,66.56 488.88,88.6 490.33,147.61 M648.2,44.54 C650.05,79.61 648.54,112.21 650.5,147.86 M649.03,45.29 C648.72,84.12 649.75,123.73 649.58,147.22" stroke-width="1.8" opacity="1.0"/><path d="M649.9,146.96 C649.58,147.66 649.65,149.76 647.93,151.17 C646.22,152.58 643.27,154.13 639.61,155.39 C635.95,156.66 631.09,157.49 625.99,158.73 C620.89,159.97 614.76,161.9 609,162.84 C603.24,163.77 598,163.99 591.43,164.35 C584.86,164.71 576.54,165.15 569.58,165.01 C562.61,164.87 556.31,164 549.66,163.51 C543.01,163.01 535.59,162.7 529.69,162.03 C523.79,161.35 519.16,160.31 514.23,159.45 C509.31,158.58 503.67,158.19 500.15,156.83 C496.62,155.47 494.96,152.81 493.11,151.28 C491.25,149.74 489.69,148.23 489.01,147.61 M649.55,146.29 C649.05,147.02 648.35,149.01 646.51,150.66 C644.66,152.31 641.7,154.62 638.46,156.19 C635.22,157.75 631.83,158.97 627.05,160.05 C622.28,161.13 615.76,161.83 609.79,162.66 C603.83,163.5 598.05,164.62 591.28,165.06 C584.5,165.5 576.12,165.36 569.13,165.3 C562.13,165.25 555.81,165.29 549.3,164.72 C542.8,164.16 536.01,162.67 530.1,161.93 C524.18,161.19 518.84,161.38 513.83,160.29 C508.82,159.21 503.43,156.81 500.05,155.42 C496.68,154.02 495.22,153.18 493.58,151.94 C491.93,150.7 490.74,148.65 490.18,148" stroke-width="1.8" opacity="1.0"/><text x="570" y="106" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Database</text><path d="M184.34,100.05 C205.23,99.7 230.78,101.96 258.19,98.65 M184.81,100.2 C202.21,99.41 220.11,100.81 256.34,99.94 M257.39,100.9 C254.32,99.27 251.78,96.82 244.22,94.71 M256.73,99.38 C253.48,98.48 248.72,96.44 245.46,94.67 M256.34,99.8 C252.56,102.11 247.86,103.88 245.59,106.58 M257.57,99.41 C254.37,101.3 250.41,102.59 245.14,105.54" stroke-width="1.8" opacity="1.0"/><path d="M419.41,100.93 C442.61,99.97 468.82,100.78 480.8,101.47 M419.18,100.92 C443.31,99.47 469.13,99.83 482.46,100.74 M482.44,100.96 C479.3,97.47 476.34,96.28 471.05,93.8 M481.77,100.06 C478.6,98.52 474.28,96.36 470.64,95.05 M480.76,100.66 C479.28,102.61 474.25,104.6 471.16,104.6 M482.17,100.57 C477.46,102.06 474.56,103.21 469.79,105.21" stroke-width="1.8" opacity="1.0"/>
</svg>
</figure>
<!-- component:simple-service end -->

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

<!-- component:pool-layout start -->
<!--
  pool-layout — 3 servers of 8 cores, 2 database instances and one pool for each pair.
  SINGLE SOURCE: references/testing-postgres-max-connections/components/pool-layout.gen.py
  Do not edit the copy. Edit the generator and run it.
  It draws in currentColor, so one drawing serves the light and the dark theme.
-->
<figure class="diagram diagram-pool-layout">
<style>
@font-face{
  font-family:"Comic Shanns";
  font-style:normal;
  font-weight:400;
  font-display:swap;
  src:url(data:font/woff2;base64,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) format("woff2");
}
.diagram-pool-layout{
  --dg-font-hand:"Comic Shanns","Comic Sans MS",monospace;
  color:hsl(var(--theme-text, 28deg 16% 13%));
  margin:34px 0;
}
.diagram-pool-layout svg{display:block;width:100%;height:auto;color:inherit}
</style>
<svg viewBox="0 0 1080 820" role="img" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-label="Three application servers with 8 cores each and two database instances with 2 GiB of RAM and max_connections 100 each. Every server has one connection pool to each database, 6 pools in all, and each pool holds 14 connections. Inside each database, a dotted box shows max_connections 100 and holds three boxes of 14, one per server pool. The pools use 42 connections in all.">
  <path d="M40.45,98.79 C86.94,99.16 131.9,98.13 269.55,100.51 M39.9,99.57 C119.82,97.78 201.71,97.58 269.78,99.95 M270.01,99.98 C268.99,134.94 271,170.05 271.97,199.11 M270.31,100.21 C269.35,135.88 269.46,173.27 270.15,200.02 M270.97,201.49 C184.84,198.68 99.02,198.3 39.69,199.58 M269.97,200.56 C195.45,201.39 120.63,202.03 40.66,199.79 M38.99,199.26 C40.2,180.34 38.89,157.18 39.18,98.38 M40.42,200.03 C39.84,174.39 40.84,147.41 40.33,100.59" stroke-width="1.8" opacity="1.0"/><text x="155" y="146" font-size="20" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Server 1</text><text x="155" y="174" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">8 cores</text><path d="M40.57,360.21 C115.62,361.98 195.39,361.2 268.49,359.28 M39.92,359.89 C87.16,360.28 133.22,359.9 269.92,359.81 M268.5,359.84 C272.64,383.11 270.95,411.4 270.38,459.02 M269.82,359.63 C268.89,396.95 268.89,433.86 270.23,459.38 M269.25,458.51 C196.13,460.81 125.85,462.65 41.41,460.26 M269.71,460.45 C221.67,458.62 171.65,459.07 40.68,460.79 M38.77,458.95 C39.29,429.95 39.28,402.9 40.53,360.87 M40.41,460.78 C40.67,419.18 39.27,380.46 40.94,359.05" stroke-width="1.8" opacity="1.0"/><text x="155" y="406" font-size="20" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Server 2</text><text x="155" y="434" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">8 cores</text><path d="M41.14,618.56 C108.4,619.37 179.26,617.94 271.39,621.27 M39.85,620.77 C119.1,620.51 199.59,619.59 270.29,619.8 M268.77,621.88 C270.1,646.25 269.94,670.73 269.03,720.03 M269.45,619.35 C270.19,648.51 269.37,678.2 270.26,719.3 M269.32,720.75 C221.17,721.18 170.87,721.9 40.56,721.04 M269.24,719.81 C195.07,719.54 119.36,719.25 40.21,720.36 M38.06,720.58 C39.58,682.4 41.63,645.77 39.16,620.44 M39.51,720.33 C39.43,690.38 39.05,660.92 40.25,620.72" stroke-width="1.8" opacity="1.0"/><text x="155" y="666" font-size="20" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Server 3</text><text x="155" y="694" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">8 cores</text><path d="M962.46,26.22 C989.28,27.59 1020.37,30.51 1036.36,34.93 C1052.34,39.35 1060.78,47.34 1058.35,52.72 C1055.91,58.1 1041.27,63.6 1021.73,67.2 C1002.19,70.8 968.87,73.7 941.12,74.35 C913.36,75 877.85,73.99 855.21,71.1 C832.57,68.21 812.49,62.3 805.28,57.02 C798.07,51.74 800.28,44.32 811.93,39.42 C823.59,34.53 861.28,29.94 875.2,27.66 C889.12,25.38 888.11,26.09 895.47,25.72 C902.83,25.36 918.64,25.24 919.36,25.49 M875.43,26.7 C898.57,24.43 935.64,24.85 962.46,26.22 C989.28,27.59 1020.37,30.51 1036.36,34.93 C1052.34,39.35 1060.78,47.34 1058.35,52.72 C1055.91,58.1 1041.27,63.6 1021.73,67.2 C1002.19,70.8 968.87,73.7 941.12,74.35 C913.36,75 877.85,73.99 855.21,71.1 C832.57,68.21 812.49,62.3 805.28,57.02 C798.07,51.74 800.28,44.32 811.93,39.42" stroke-width="1.8" opacity="1.0"/><path d="M799.17,51.2 C801.66,157.23 802.67,264.17 801.4,363.62 M799.64,50.32 C800.5,150.3 799.58,249.34 799.97,364.73 M1058.78,51.3 C1061.21,169.16 1060.37,289.62 1060.93,365.3 M1060.37,50.51 C1061.37,153.45 1061.68,258.36 1060.5,364.54" stroke-width="1.8" opacity="1.0"/><path d="M1059.59,364.04 C1059.09,365.45 1059.39,370.06 1056.56,372.49 C1053.73,374.92 1048.31,376.75 1042.6,378.62 C1036.88,380.48 1030.12,382.28 1022.27,383.7 C1014.41,385.11 1005.21,386.12 995.47,387.1 C985.73,388.09 974.78,389 963.84,389.61 C952.9,390.21 941.07,390.78 929.84,390.74 C918.62,390.7 907.29,389.87 896.48,389.38 C885.68,388.89 874.61,388.86 865.01,387.79 C855.41,386.72 846.75,384.63 838.88,382.96 C831.01,381.29 823.37,379.78 817.78,377.76 C812.18,375.73 808.17,372.98 805.31,370.83 C802.44,368.67 801.37,365.84 800.58,364.85 M1059.14,364.64 C1058.52,365.82 1058.02,369.58 1055.42,371.74 C1052.82,373.89 1049.07,375.6 1043.54,377.58 C1038.02,379.55 1030.31,382.05 1022.29,383.59 C1014.28,385.14 1005.22,385.77 995.47,386.85 C985.71,387.93 974.57,389.48 963.75,390.07 C952.92,390.66 941.62,390.23 930.51,390.4 C919.4,390.57 908.14,391.52 897.09,391.08 C886.04,390.65 874.02,388.92 864.21,387.79 C854.41,386.66 846.17,386 838.26,384.3 C830.34,382.61 822.35,379.74 816.73,377.64 C811.12,375.55 807.28,373.72 804.56,371.73 C801.85,369.75 801.15,366.74 800.46,365.74" stroke-width="1.8" opacity="1.0"/><text x="930" y="136" font-size="20" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Database 1</text><text x="930" y="160" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">2 GiB RAM</text><path d="M818.58,177.26 C885.47,173.79 952.67,174.39 1043.08,175.12 M817.7,176.08 C892.23,175.15 965.32,174.72 1042.53,176.77 M1040.09,177.01 C1043.7,227.49 1042.1,277.93 1043.42,322.56 M1042.26,176.88 C1041.45,225.73 1043.06,274.23 1041.31,323.49 M1041.29,324.09 C988.61,324.55 932.49,324.35 816.79,324.7 M1041.31,324.79 C963.34,325.16 883.54,325.09 818.63,323.59 M819.63,325.55 C815.26,277.33 818.03,232.02 819.67,177.15 M818.71,324.88 C818.55,268.85 819.91,213.98 818,175.75" stroke-width="1.8" opacity="1.0" stroke-dasharray="1 8"/><text x="930" y="200" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">max_connections: 100</text><path d="M832.71,215.82 C847.02,213.84 862.96,216.01 891.68,213.35 M833.9,213.79 C853.89,213.35 871.46,213.98 890.73,214.11 M888.41,212.39 C889.22,232.11 890.09,248.04 889.86,259.62 M889.55,213.63 C889.78,224.29 890.04,234.33 889.3,258.2 M890.37,257.17 C875.05,258.06 856.33,259.04 835.3,256.66 M890.1,258.36 C869.24,256.68 848.02,257.62 833.05,258.28 M834.47,259.85 C835.31,246.21 832.9,232.67 832.2,214.47 M833.77,257.14 C834.62,246.51 834.24,236.19 834.68,214.39" stroke-width="1.8" opacity="1.0"/><text x="862" y="242" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">14</text><path d="M901.98,215.79 C917.13,213.44 933.05,215.12 957.63,212.91 M902.98,213.8 C924.34,214.02 945.33,213.71 957.1,214.45 M958.6,213.28 C958.16,224.93 960.04,232.64 958.86,257.42 M957.59,213.78 C959.02,223.63 957.51,233.24 957.51,258.35 M957.87,259.33 C943.64,255.8 925.7,259.62 902.94,258.81 M958.46,257.87 C937.27,256.89 916.48,257.19 902.18,258.72 M902.08,259.24 C900.36,248.86 901.63,239.33 902.18,213.11 M901.55,258.63 C902.37,247.37 901.08,237.83 902.95,214.55" stroke-width="1.8" opacity="1.0"/><text x="930" y="242" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">14</text><path d="M971.52,213.86 C988.14,212.57 1006.59,214.09 1027.58,213.85 M969.68,213.96 C991.62,214.68 1012.63,214.97 1025.86,213.78 M1027.39,213.9 C1024.41,226.42 1026.4,239.29 1027.65,257.07 M1025.17,213.29 C1026.19,230.33 1025.42,247.01 1025.56,257.09 M1026.4,258.74 C1007.93,259.24 988.29,256.92 970.22,257.94 M1025.84,258.86 C1006.89,257.44 986.33,258.68 969.54,258.88 M969.51,257.91 C971.29,241.89 969.72,227.03 969.69,215.45 M969.58,257.95 C971.12,247.17 970.87,234.99 969.23,214.85" stroke-width="1.8" opacity="1.0"/><text x="998" y="242" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">14</text><text x="930" y="288" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">42 in use</text><text x="930" y="308" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">by the pools</text><path d="M998.36,453.72 C1022.91,456.26 1046.7,461.48 1056.3,466.62 C1065.91,471.77 1066.13,479.54 1056.01,484.58 C1045.89,489.63 1020.75,494.25 995.57,496.87 C970.4,499.49 933.27,501.44 904.94,500.29 C876.62,499.14 843.99,494.1 825.63,489.97 C807.27,485.84 794.11,480.87 794.8,475.5 C795.48,470.13 810.69,461.91 829.73,457.73 C848.78,453.55 890,451.79 909.07,450.42 C928.14,449.05 932.78,449.21 944.14,449.53 C955.51,449.85 977.47,451.69 977.25,452.35 M909.03,451.38 C935.61,450.35 973.82,451.18 998.36,453.72 C1022.91,456.26 1046.7,461.48 1056.3,466.62 C1065.91,471.77 1066.13,479.54 1056.01,484.58 C1045.89,489.63 1020.75,494.25 995.57,496.87 C970.4,499.49 933.27,501.44 904.94,500.29 C876.62,499.14 843.99,494.1 825.63,489.97 C807.27,485.84 794.11,480.87 794.8,475.5 C795.48,470.13 810.69,461.91 829.73,457.73" stroke-width="1.8" opacity="1.0"/><path d="M798.95,474.73 C800.86,599.21 801,723.08 800.6,789.57 M799.45,475.13 C800.61,544.74 799.58,613.08 799.65,789.87 M1060.19,475.77 C1057.65,539.98 1057.9,602.17 1060.8,790.64 M1060.15,474.73 C1060.66,547.01 1060.15,617.01 1060.53,789.36" stroke-width="1.8" opacity="1.0"/><path d="M1060.32,789.01 C1059.47,790.15 1058.1,793.37 1055.18,795.83 C1052.26,798.3 1048.31,801.73 1042.81,803.82 C1037.32,805.91 1030,806.9 1022.2,808.37 C1014.39,809.84 1005.82,811.51 995.98,812.63 C986.13,813.75 974,814.58 963.13,815.1 C952.27,815.63 941.99,815.78 930.81,815.78 C919.64,815.79 907.03,815.63 896.09,815.13 C885.15,814.62 874.91,814 865.16,812.76 C855.42,811.52 845.66,809.46 837.61,807.7 C829.55,805.94 822.25,804.13 816.86,802.19 C811.47,800.25 808.04,798.11 805.26,796.08 C802.48,794.05 801.03,791.02 800.18,790.01 M1060.06,789.6 C1059.38,790.63 1058.81,793.55 1055.95,795.77 C1053.1,797.99 1048.55,800.69 1042.93,802.94 C1037.31,805.19 1030.19,807.59 1022.25,809.27 C1014.31,810.95 1005.1,812.07 995.29,813.01 C985.48,813.94 974.44,814.43 963.39,814.89 C952.35,815.35 940.18,815.85 929.01,815.77 C917.84,815.68 906.92,814.92 896.38,814.38 C885.85,813.83 875.65,813.51 865.81,812.49 C855.97,811.46 845.55,809.81 837.34,808.21 C829.13,806.6 822.04,804.62 816.55,802.87 C811.06,801.11 807.06,799.89 804.41,797.68 C801.76,795.48 801.28,791 800.65,789.66" stroke-width="1.8" opacity="1.0"/><text x="930" y="561" font-size="20" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">Database 2</text><text x="930" y="585" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">2 GiB RAM</text><path d="M819.48,600.73 C871.38,603.55 926.13,604.24 1041.97,602.49 M818,601.82 C867.42,601.14 918.14,600.56 1042.35,600.37 M1040.08,601.89 C1039.68,644.61 1041,690.56 1040.79,748.52 M1041.03,601.23 C1042.97,634.35 1042.78,667.25 1041.07,748.64 M1042.98,747.54 C983.29,746.8 924.42,749.09 817.28,748.54 M1042.54,748.58 C991.84,750.3 940.9,751.24 817.53,749.31 M818.77,750.65 C818.82,697.83 819.07,650.05 819.49,599.24 M818,749.8 C819.3,712.18 819.42,675.17 817.94,601" stroke-width="1.8" opacity="1.0" stroke-dasharray="1 8"/><text x="930" y="625" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">max_connections: 100</text><path d="M835.06,638.72 C846.37,638.81 862.91,637.53 890.39,638.77 M834.05,638.95 C850.2,640.13 869.08,639.46 889.85,639.94 M890.63,637.69 C891.2,649.56 888.38,661.46 890.11,683.29 M889.32,638.85 C890.16,653.09 890.18,667.48 889.74,682.03 M889.35,681.01 C869.43,681.43 851.14,684.91 835.32,682.82 M890.69,683.1 C877.51,682.41 863.72,682.32 833.87,683.85 M832.99,684.26 C834.15,668.89 832.12,654.7 832.75,640.12 M833.51,683.95 C834.97,665.36 834.26,650.53 833.61,638.73" stroke-width="1.8" opacity="1.0"/><text x="862" y="667" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">14</text><path d="M902.16,639.96 C914.54,639.02 929.75,637.65 957.49,637.37 M902.66,638.62 C914.95,638.84 928.33,638.87 957.67,639.31 M957.23,637.93 C956.8,653.74 958.74,667.39 958.57,683.97 M957.63,639.09 C958.38,649.63 957.96,659.17 958.22,682.57 M956.21,684.88 C935.76,684.36 915.39,685.18 902.15,684.76 M957.47,682.47 C943.35,683.12 930.05,682.82 901.12,683.39 M900.14,684.54 C900.96,670.64 900.94,661.84 902.43,639.88 M901.44,683.69 C901.87,669 901.36,652.48 901.69,638.55" stroke-width="1.8" opacity="1.0"/><text x="930" y="667" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">14</text><path d="M970.28,637.98 C989.67,640.81 1010.29,640.99 1024.8,638.41 M969.7,639.27 C987.72,639.49 1007.82,639.5 1026.99,638.32 M1025.28,637.61 C1024.37,650.12 1025.13,661.56 1026.15,681.01 M1026.38,639.32 C1025.11,652.55 1025.61,668.3 1026.27,683.86 M1026.83,682.11 C1002.47,682.37 983.63,681.49 968.2,683.8 M1026.95,683.62 C1007.91,681.84 988.75,681.98 969.87,683.86 M970.16,682.48 C968.35,673.55 969.67,663.8 969.62,639.3 M970.77,683.71 C970.18,669.3 971.39,653.72 969.21,638.77" stroke-width="1.8" opacity="1.0"/><text x="998" y="667" font-size="18" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">14</text><text x="930" y="713" font-size="16" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">42 in use</text><text x="930" y="733" font-size="15" text-anchor="middle" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">by the pools</text><path d="M273.59,120.19 C321.96,119.89 372.37,121.68 422.48,118.79 M273.64,119.25 C327.07,120.71 379.78,120.11 424.86,120.49" stroke-width="1.8" opacity="1.0"/><path d="M424.82,121.09 C498.33,127.42 572.72,137.05 789.97,168.48 M424.47,119.82 C557.83,136.75 691.38,154.56 790.26,166.91 M790.43,168.33 C788.09,165.87 783.31,165.04 778.63,159.51 M790.06,167.68 C788.02,165.56 784.86,163.93 779.49,161.06 M788.75,168.13 C785,168.87 780.7,170.31 778.68,170.28 M790.6,167.19 C787.7,168.32 784.15,169.18 777.05,172.08" stroke-width="1.8" opacity="1.0"/><text x="288" y="108" font-size="15" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">pool: 14</text><path d="M273.9,178.52 C310.03,181.3 343.67,180.29 425.55,179.01 M273.3,180.18 C313.75,180.81 355.87,181.11 423.05,180.78" stroke-width="1.8" opacity="1.0"/><path d="M423.87,180.3 C542.89,315.9 661,448.56 790.51,592.4 M423.91,179.76 C548.93,320.66 673.6,461.07 789.91,592.57 M789.03,593.5 C787.84,588.27 787.84,583.59 785.47,581.04 M790.55,592.32 C788.9,588.17 787.53,584.99 785.83,580.05 M790.46,591.45 C785.66,591.18 781.83,589.07 777.23,587.54 M789.94,592.54 C786.23,590.72 782.48,589.23 778.02,587.18" stroke-width="1.8" opacity="1.0"/><text x="288" y="168" font-size="15" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">pool: 14</text><path d="M274.73,378.67 C311.01,379.94 348.4,378.99 424.25,379.02 M273.45,379.04 C323.3,380.35 373.37,378.84 423.24,379.82" stroke-width="1.8" opacity="1.0"/><path d="M423.05,380.57 C538.05,325.13 653.85,272.69 789.1,206.45 M423.55,379.75 C510.85,338.63 597.57,298.09 790.22,207.78 M789.75,208.09 C784.93,208.49 781.25,207.43 777.26,206.75 M790.47,207.77 C786.81,207.08 783.39,207.6 776.88,207.72 M789.13,208.29 C788.42,210.59 785.61,212.68 780.46,217.19 M790.04,207.76 C787.24,209.78 785.29,213.21 781.84,217.82" stroke-width="1.8" opacity="1.0"/><text x="288" y="368" font-size="15" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">pool: 14</text><path d="M275.28,440.33 C307.06,441.03 343.17,440.57 422.56,440.09 M273.83,439.85 C304.81,440.38 333.75,441 424.71,440.06" stroke-width="1.8" opacity="1.0"/><path d="M423.45,440.18 C547.2,503.84 669.29,568.04 790.3,631.86 M423.58,439.82 C555.28,507.71 686.48,576.92 790.5,632.79 M791.25,633.69 C786.59,629.61 784.47,625.05 781.69,623.26 M789.54,632.78 C787.32,628.52 784.13,625.04 782.18,622.12 M789.4,633.57 C786.74,632.68 783.53,630.94 777.25,631.12 M789.51,633.08 C787.46,632.54 783.44,632.81 776.94,631.93" stroke-width="1.8" opacity="1.0"/><text x="288" y="428" font-size="15" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">pool: 14</text><path d="M273.51,639.55 C325.81,639.62 372.15,638.47 425.87,639.13 M274.56,640.39 C320.59,638.61 366.36,637.7 424.18,640.66" stroke-width="1.8" opacity="1.0"/><path d="M424.32,639.75 C550.21,506.94 675.19,373.11 789.76,246.73 M423.7,639.93 C536.59,519.36 648.41,399.35 789.91,247.76 M790.25,246.86 C786.19,248.83 784.18,250.98 776.83,253.11 M790.01,247.15 C785.71,249.13 781.22,251.9 778.47,252.02 M790.56,246.59 C790.13,250.88 788.53,255.6 784.79,259.88 M790.19,247.22 C789.31,250.57 787.99,253.84 786.07,260.39" stroke-width="1.8" opacity="1.0"/><text x="288" y="628" font-size="15" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">pool: 14</text><path d="M275.93,698.99 C333.33,701.84 392.06,701.05 425.05,700.39 M273.2,700.18 C325.48,699.44 377.5,697.81 424.38,699.76" stroke-width="1.8" opacity="1.0"/><path d="M423.9,701 C502.8,694.39 582.26,688.4 790.28,673.35 M424.02,699.56 C552.66,688.63 680.83,679.69 790.29,673.07 M789.78,671.53 C785.6,670.56 780.53,669.6 776.77,667.38 M789.42,672.22 C786.41,670.96 782.91,670.42 778.38,667.71 M790.68,671.4 C785.68,673.94 780.08,676.72 779.79,678.64 M790.21,672.15 C785.55,674.36 781.47,677.55 778.64,678.82" stroke-width="1.8" opacity="1.0"/><text x="288" y="688" font-size="15" text-anchor="start" font-family="var(--dg-font-hand)" fill="currentColor" stroke="none">pool: 14</text>
</svg>
</figure>
<!-- component:pool-layout end -->
