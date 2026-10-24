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

### Phase 3 : Postmaster accepts the connection

Postmaster accepts the connection after the TCP handshake and forks a new child process.
These child processes are backend processes which gets the connection and they can communicate with each other using semaphores and shared memory to maintain the data integrity throughout the concurrent data access.

Once a connection is established, the client can now send a query in plain text form to the Database backend process and the backend process parses the query, creates a plan, and returns the results over the connection.

<figure class="diagram">
<img class="theme-light-only" src="/images/posts/testing-postgres-max-connections/postmaster-accept.light.png" alt="The postmaster accepts the connection on port 5432 and forks a child process. The Database Client on port 5123 and the child process then exchange the query and the query results." />
<img class="theme-dark-only" src="/images/posts/testing-postgres-max-connections/postmaster-accept.dark.png" alt="The postmaster accepts the connection on port 5432 and forks a child process. The Database Client on port 5123 and the child process then exchange the query and the query results." />
</figure>

## What is Connection Pooling?

Postgres uses a multi-process architecture where one process is allowed per connection.
So when the Application Server which is handling multiple requests at a given time uses multiple connections to the Postgres Database Server.

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
