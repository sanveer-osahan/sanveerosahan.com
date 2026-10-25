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


