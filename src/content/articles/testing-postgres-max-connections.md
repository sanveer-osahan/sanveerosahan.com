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
