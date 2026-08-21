---
title: "Databricks End to End: From Raw Data to an AI Chatbot"
description: "The story of one problem is scattered across 4 systems. Pulling it into Databricks, then serving both the counting questions and the meaning questions from it."
publishDate: 2026-08-21
draft: false
tags: ["databricks", "data-engineering", "ai", "rag"]
---

## The problem

4xData connects to data sources of every shape: SQL databases, warehouses, NoSQL stores and object storage. Customers build automations on top of those connections to pull data out of each source and feed it into whatever sits downstream.

The Connector team builds and maintains those source connectors, and writes the business logic that extracts the data.

Every source brings its own set of problems, and the Connector team absorbs all of them. They carry the highest number of support tickets in the company.

That number climbs with the roadmap. Each new connector adds a source to support. Each increase in depth on an existing connector covers more of a source's surface, and more surface means more of that source's problems reach us.

Growth pushes from the other side too. 4xData is winning high end customers who bring high revenue growth, and those customers arrive with a security posture. They apply the principle of least privilege and grant a connector the narrowest access their policy allows. That is the right call on their side and a steady stream of tickets on ours, because a connector that cannot reach what it needs fails in ways that take time to trace back to a missing permission.

The ticket count rises, in other words, because the company is succeeding. That is what makes it a business threat rather than a support inconvenience. Engineering hours spent closing tickets are hours taken from the connectors that win the next set of customers.

## What we need to know

7 questions, each one aimed at a decision somebody has to make.

- **The patterns worth closing.** Ranked by the number of tickets each one produces and by whether that number is growing. A pattern with 100 tickets that peaked in May matters less than one with 30 that started in July and is still climbing. Grouping is by cause rather than by connector, so a permission failure that shows up on Postgres, Snowflake and MongoDB counts once at its real size instead of 3 times at a third of it.

- **The connectors to prioritise.** Raw ticket volume favours whichever connector has the most customers. The ranking has to account for how much each connector's tickets cost to service.

- **Root cause fix or patch.** For every ticket that shipped a fix, whether the engineer closed the cause or worked around the symptom. A connector with a high patch ratio is holding debt that comes back as next quarter's tickets.

- **Time to resolution.** How long tickets take to close, split by connector, severity and account tier. Slow resolution on the accounts paying the most is the number that reaches leadership before it reaches us.

- **Engineering hours per pattern.** The third signal in that ranking, rebuilt from the timestamps on comments and pull requests. Volume tells us how often a problem happens. Hours tell us what it costs, and cost is what justifies pulling an engineer off the roadmap to fix it.

- **Related tickets for a given ticket id.** An engineer picking up a new ticket sees the ones that describe the same failure, along with how each was resolved, instead of starting from the description.

- **The docs that are missing.** Tickets an engineer closed with an explanation and no code change. Every cluster of those is a page that should exist, and every ticket in it is one the customer could have answered without us.

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/architecture.png" alt="Pipeline diagram. On the left, a Support Tickets box holding Issue, Comments, Slack thread and GitHub PR. An extract arrow leads into a Databricks box containing a Unity Catalog Volume, a Medallion Architecture box with bronze for raw data, silver for denormalized data and gold for serving the business use case, an AI Search Index fed from silver, and an AI Chatbot fed from both the index and gold." />
</figure>

## Why the interface is a chatbot

A dashboard would answer those 7 questions and stop there. Every answer ends in a follow-up it cannot take: which customers, on which connector, and what did we do about it last time.

Has anyone seen a timeout on Oracle when the customer reads from a standby? What did we do the last time a warehouse started returning partial result sets? Which customers hit the schema drift bug in June, and did the fix hold for all of them?

Today those get asked in Slack, and the answer depends on whether the person who solved it 3 months ago is online and remembers. When nobody answers, the engineer either rediscovers the fix or escalates to someone who should be building a connector.

The answers already exist. They sit in ticket comments, Slack threads and pull request descriptions, written as prose, which is why no query reaches them. A chatbot over that archive turns 3 months of resolved work into something the team can interrogate.

It has to handle 2 kinds of question, and they need different machinery. "What went wrong with the Oracle connector for this customer" is a retrieval question, answered by finding the relevant threads. "How many P1 tickets did we get last month" is a query, answered by counting rows. A retrieval-only chatbot answers the second kind with confidence and gets it wrong. Giving it a search tool and a SQL tool, and letting it pick, keeps both kinds honest.

The same interface serves 2 more groups. A new engineer asks it how the team has handled a class of failure before, instead of spending their first month learning it from Slack. A support engineer answering a customer finds the prior fix without pulling a connector engineer off their work.

## What we have

We pulled 3 months of resolved tickets, April to June 2026, out of the systems where the work happened. Each issue brings its description and its comments, the Slack thread the developers debugged it in, and the GitHub pull request behind the fix: description, review comments, and the summary of what changed in the code.

All of it carries an author and a timestamp. Ordering it turns an issue into one thread that reads top to bottom, and that thread is the unit we embed and store in a vector database.

Then we read them. We assigned each issue a cause pattern and a fix type by hand, and wrote down why we called each one the way we did. Those labels and that reasoning are what the model trains on.

6 tables came out of that pass.

### `support_tickets`

| Column | Description |
|---|---|
| `issue_id` | The ticket key. Joins to every other table here. |
| `customer` | The account that raised it. Joins to `customers`. |
| `connector` | Which connector the ticket is about, 1 of 15. |
| `pattern` | The cause, assigned by hand from the frozen list in `patterns`. |
| `fix_type` | `patch` or `root_cause`. Null when the ticket shipped no code. |
| `severity` | `low`, `medium`, `high`, `critical`. The business uses P numbers for priority, so severity keeps clear of them. |
| `assignee` | The developer who owns that connector. Joins to `employees`. |
| `start_datetime` | When the customer raised it. |
| `resolved_datetime` | When it closed. Every ticket in the set is resolved. |

### `ticket_content`

One row per comment. Order them by `timestamp` and you have the thread.

| Column | Description |
|---|---|
| `issue_id` | The ticket the comment belongs to. |
| `text` | The comment itself. |
| `timestamp` | When someone wrote it. |
| `commentor` | Who wrote it. Joins to `employees`. |
| `channel` | `ticket`, `slack`, or `github`. 3 places the same problem gets discussed. |
| `visibility` | `customer` or `internal`. Slack and GitHub are always internal, and that is where the complexity estimates and the blunt assessments live. |

### `reasoning`

| Column | Description |
|---|---|
| `issue_id` | One row per ticket. |
| `pattern_reasoning` | Why the analyst picked that pattern, citing what in the thread supports it. |
| `fix_type_reasoning` | Why the fix counts as a patch or as a root cause fix. |

Nothing else in the dataset explains a label, so `reasoning` is where 2 engineers settle a disagreement about one.

### `patterns`

| Column | Description |
|---|---|
| `pattern_name` | The label. 13 of them, and the list does not grow without a review. |
| `pattern_description` | What the pattern covers, written so that 2 people reading the same thread pick the same label. |
| `root_cause_fix` | The durable fix for that class of problem, stated as a single sentence. |

### `customers`

| Column | Description |
|---|---|
| `customer_id` | Account key. |
| `customer_name` | The account. |
| `account_tier` | `enterprise`, `growth`, or `startup`. |
| `region` | Where the account runs. |

### `employees`

| Column | Description |
|---|---|
| `employee_id` | Person key. |
| `name` | The person. |
| `role` | `support_engineer`, `developer`, or `manager`. Role drives the order of a thread: support records the report, a developer works the cause, support writes back to the customer. |

## What we build in Databricks

- **Analytics.** SQL over the 3 months, answering the 7 questions.

- **A chatbot.** One tool that searches the threads, one that queries the tables. It picks which to use.

- **A classifier.** Trained on the hand-assigned labels and the reasoning behind them. From July it labels each week's closed tickets, and nobody spends a day doing it by hand.

## Loading the files into Databricks

Databricks names everything in 3 parts: catalog, schema, table. If you have used Postgres or Snowflake, it is the shape you know with one level added on top.

A **volume** is the part with no warehouse equivalent. It holds files rather than tables: parquet, CSV, JSON, images. Files land in a volume first and become tables after. Keeping the raw file means a wrong parse costs a re-read rather than a re-export.

### 1. Create the catalog, the schemas and the volume

```sql
CREATE CATALOG IF NOT EXISTS support_analytics;

CREATE SCHEMA IF NOT EXISTS support_analytics.bronze;
CREATE SCHEMA IF NOT EXISTS support_analytics.silver;
CREATE SCHEMA IF NOT EXISTS support_analytics.gold;

CREATE VOLUME IF NOT EXISTS support_analytics.bronze.raw;
```

Bronze holds the tables as they arrive, silver the cleaned and joined versions, gold what the analytics read. Those 3 names are a convention the industry settled on. Databricks enforces none of it, and you could call them anything.

Run this in the SQL editor. On Free Edition you get 1 warehouse at `2X-Small`, which is far more than 2,700 comment rows need.

### 2. Upload the files

In the sidebar, click **New**, then **Add or upload data**, then **Upload files to a volume**. Drag the 6 parquet files into the drop zone and pick `support_analytics.bronze.raw` as the destination.

```
batch_support_tickets.parquet
batch_ticket_content.parquet
batch_reasoning.parquet
patterns.parquet
customers.parquet
employees.parquet
```

The drop zone takes many files at once and no folders. There is a **Download directory** button in the volume browser with no upload counterpart, so a nested export means creating each directory by hand and uploading into it one at a time. Export flat and none of that comes up.

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/volume-upload.png" alt="Databricks Catalog Explorer showing the raw volume under support_analytics.bronze, listing the 6 uploaded parquet files with their sizes, and an upload summary panel confirming 6 files uploaded." />
<figcaption>The 6 files landed in <code>support_analytics.bronze.raw</code>. Bronze, silver and gold sit alongside each other in the catalog tree on the left.</figcaption>
</figure>

### 3. Check what landed

```sql
LIST '/Volumes/support_analytics/bronze/raw';

SELECT * FROM read_files(
  '/Volumes/support_analytics/bronze/raw/batch_support_tickets.parquet'
) LIMIT 5;
```

`read_files` reads a file without creating a table. Look at what you have before you commit to a schema.

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/read-files-result.png" alt="Databricks SQL editor showing a read_files query against batch_support_tickets.parquet, with a result grid of 5 ticket rows listing issue_id, assignee, connector, fix_type, severity, start and resolved timestamps, and pattern." />
<figcaption>5 rows straight out of the volume. No table exists yet.</figcaption>
</figure>

## Landing the files as tables

`read_files` parses the parquet on every run. A table stores it once as Delta, which gives you a name other queries can join to, column statistics the planner uses, and a history you can roll back. Bronze is where the files arrive with their shape unchanged.

Each file becomes a table with the same query you just ran, plus `CREATE TABLE` in front.

```sql
CREATE TABLE support_analytics.bronze.support_tickets AS
SELECT * FROM read_files(
  '/Volumes/support_analytics/bronze/raw/batch_support_tickets.parquet');

CREATE TABLE support_analytics.bronze.ticket_content AS
SELECT * FROM read_files(
  '/Volumes/support_analytics/bronze/raw/batch_ticket_content.parquet');

CREATE TABLE support_analytics.bronze.reasoning AS
SELECT * FROM read_files(
  '/Volumes/support_analytics/bronze/raw/batch_reasoning.parquet');

CREATE TABLE support_analytics.bronze.patterns AS
SELECT * FROM read_files(
  '/Volumes/support_analytics/bronze/raw/patterns.parquet');

CREATE TABLE support_analytics.bronze.customers AS
SELECT * FROM read_files(
  '/Volumes/support_analytics/bronze/raw/customers.parquet');

CREATE TABLE support_analytics.bronze.employees AS
SELECT * FROM read_files(
  '/Volumes/support_analytics/bronze/raw/employees.parquet');
```

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/bronze-tables.png" alt="Databricks Catalog Explorer tree showing the support_analytics catalog, the bronze schema, and Tables (6): customers, employees, patterns, reasoning, support_tickets and ticket_content." />
<figcaption>6 files in, 6 tables out.</figcaption>
</figure>

Nothing is cleaned, renamed or joined here. A bronze table that edits its source removes your ability to tell a bad transformation from a bad file.

Check the counts before moving on.

```sql
SELECT 'support_tickets' AS t, count(*) FROM support_analytics.bronze.support_tickets
UNION ALL SELECT 'ticket_content', count(*) FROM support_analytics.bronze.ticket_content
UNION ALL SELECT 'reasoning',      count(*) FROM support_analytics.bronze.reasoning
UNION ALL SELECT 'patterns',       count(*) FROM support_analytics.bronze.patterns
UNION ALL SELECT 'customers',      count(*) FROM support_analytics.bronze.customers
UNION ALL SELECT 'employees',      count(*) FROM support_analytics.bronze.employees;
```

| Table | Rows |
|---|---|
| `support_tickets` | 245 |
| `ticket_content` | 1,816 |
| `reasoning` | 245 |
| `patterns` | 13 |
| `customers` | 40 |
| `employees` | 9 |

245 tickets and 245 reasoning rows should match, because every ticket in the 3 months carries an analyst's note. A gap there means a file arrived short.

## Next: one row per ticket

Bronze holds comments as rows. Everything after this reads a ticket rather than a comment. The search index embeds a ticket, and the classifier reads a ticket to decide its pattern.

So the next table turns those 1,816 comment rows into 245 tickets, each carrying its whole conversation as one block of text in time order, with the ticket metadata, the customer and the analyst's reasoning alongside it.

```sql
CREATE TABLE support_analytics.silver.ticket_record
TBLPROPERTIES (
  delta.enableChangeDataFeed         = true,               -- the search index needs this
  delta.deletedFileRetentionDuration = 'interval 30 days'  -- so weekly syncs do not fail
)
AS
WITH lines AS (
  SELECT
    c.issue_id,
    c.timestamp,
    c.visibility,
    concat('[', date_format(c.timestamp, 'yyyy-MM-dd HH:mm'), ' | ',
           e.name, ' (', e.role, ') | ', c.channel, ']\n', c.text) AS line
  FROM support_analytics.bronze.ticket_content c
  JOIN support_analytics.bronze.employees e ON e.employee_id = c.commentor
),
threads AS (
  SELECT
    issue_id,
    count(*) AS comment_count,
    -- collect_list returns no particular order, so sort on the timestamp
    concat_ws('\n\n',
      transform(array_sort(collect_list(struct(timestamp, line))), x -> x.line)
    ) AS thread_text,
    concat_ws('\n\n',
      transform(array_sort(collect_list(
        CASE WHEN visibility = 'customer' THEN struct(timestamp, line) END
      )), x -> x.line)
    ) AS thread_text_customer
  FROM lines
  GROUP BY issue_id
)
SELECT
  t.issue_id, t.connector, t.severity, t.pattern, t.fix_type,
  'human' AS label_source,          -- a person assigned these, not a model
  -- the search index stores timestamp and double, but not the timestamp_ntz
  -- that untimezoned parquet produces, nor the decimal that dividing produces
  CAST(t.start_datetime    AS TIMESTAMP) AS start_datetime,
  CAST(t.resolved_datetime AS TIMESTAMP) AS resolved_datetime,
  CAST(timestampdiff(MINUTE, t.start_datetime, t.resolved_datetime) / 60.0
       AS DOUBLE) AS hours_to_resolve,
  cu.customer_name, cu.account_tier, cu.region,
  e.name AS assignee_name,
  r.pattern_reasoning, r.fix_type_reasoning,
  th.comment_count, th.thread_text, th.thread_text_customer
FROM support_analytics.bronze.support_tickets t
JOIN threads th                            ON th.issue_id    = t.issue_id
JOIN support_analytics.bronze.customers cu ON cu.customer_id = t.customer
JOIN support_analytics.bronze.employees e  ON e.employee_id  = t.assignee
LEFT JOIN support_analytics.bronze.reasoning r ON r.issue_id = t.issue_id;
```

Then check it.

```sql
SELECT count(*) AS tickets,
       sum(comment_count) AS comments,
       count(pattern_reasoning) AS with_reasoning
FROM support_analytics.silver.ticket_record;
```

245 tickets, 1,816 comments, 245 with reasoning. The comment count matching bronze is the part worth checking: a join that drops rows shows up here and nowhere else.

## Making the embeddings

### The problem embeddings solve

A database can tell you whether two pieces of text match. It cannot tell you whether they mean the same thing.

Take 2 tickets from the pile:

> Sync started failing after the customer's security team tightened the role.

> Connector cannot see the orders table since their access review last week.

Same problem. Barely a word in common. Search one and you will not find the other, because `LIKE '%tightened the role%'` matches characters, and nothing in the second ticket has those characters in it.

### What an embedding is

An embedding turns a piece of text into a list of numbers. You hand a model some text, it hands back roughly a thousand numbers.

The useful part is how the model was trained: text that means similar things comes back with similar numbers. Those 2 tickets above land close together, even with no shared words. A ticket about a Salesforce API limit lands far away from both.

So comparing 2 tickets stops being a string problem and becomes arithmetic on 2 lists of numbers. A computer does that fast, and it does not care how the sentence was worded.

That is the whole idea. Text in, numbers out, close meaning gives close numbers.

The model doing this is not a chat model. `databricks-qwen3-embedding-0-6b` has one job and cannot hold a conversation. It reads text and returns numbers.

### What the index is for

You could store those numbers in a column and compare them yourself. With 245 tickets that works.

At 50,000 tickets, every search reads all 50,000 rows and does the arithmetic on each. That gets slow, and it gets slow on every single query.

A **search index** is a copy of those numbers arranged so that "find the closest ones" is fast without reading everything. You give it a question, it gives you back the nearest tickets. This is the thing people mean by a vector database.

### Why the index goes stale

The index holds a copy. Add a ticket to the table and the index knows nothing about it until it is told.

Being told is called a **sync**. 2 ways to run it:

- **Continuous.** Databricks watches the table and updates the index by itself. It holds compute open to do that watching.
- **Triggered.** Nothing happens until you ask for a sync. You run it after each load.

Continuous sounds better and is wrong here. Free Edition gives you a compute quota, and when you exceed it your workspace shuts down for the rest of the day. Something holding compute open around the clock will find that limit. Use Triggered.

Either way, Databricks needs to know which rows changed since last time. That is what `delta.enableChangeDataFeed` was for on the silver table. Delta keeps a log of row-level changes, and the sync reads that log rather than re-reading 245 tickets to find the 3 that moved.

### Why hybrid, and not just vectors

Embeddings are good at meaning and bad at exact strings.

Your tickets are full of things where the exact string is the point: `DBMS_LOGMNR`, `wal_level`, `restricted.googleapis.com`, an error code. Turn `DBMS_LOGMNR` into a thousand numbers and it blurs into "something Oracle, something permissions". Search for it and you get Oracle permission tickets, some of which never mention it.

Old-fashioned keyword search has the opposite problem. It finds `DBMS_LOGMNR` and misses every ticket that describes the same failure without naming it.

**Hybrid** runs both and merges the results. You want both, so pick Hybrid.

### 1. Create the endpoint

An **endpoint** is the compute that serves the index. The index is the data, the endpoint is the machine answering questions about it.

Left sidebar, **Compute**, then the **AI Search** tab, then **Create endpoint**. Name it `support_search`, pick **Standard**, confirm. It takes a few minutes to come online.

Free Edition allows 1 endpoint, so this is the only one you get. Every index you build later shares it.

### 2. Create the index

Open **Catalog**, find `support_analytics.silver.ticket_record`, then **Create**, then **AI Search index**.

Databricks renamed this feature from Vector Search to AI Search, and the rename reached the UI before it reached everything else. The menu says AI Search, the SQL function is still `vector_search`, and the Python package is `databricks-ai-search`. Expect to see both names.

| Field | Value | Why |
|---|---|---|
| Name | `support_analytics.silver.ticket_record_index` | |
| Primary key | `issue_id` | How a hit points back at a row |
| Embedding source | Compute embeddings | Databricks makes the numbers, you do not |
| Embedding source column | `thread_text` | The column that gets turned into numbers |
| Embedding model | `databricks-qwen3-embedding-0-6b` | The model that does the turning |
| Index type | Hybrid | Meaning and exact strings, both |
| Sync mode | Triggered | Protects the Free Edition quota |

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/create-ai-search-index.png" alt="The Create AI Search index dialog in Databricks, showing issue_id as the primary key, Compute embeddings selected, thread_text as the embedding source column, the support_search endpoint, Triggered index update mode, and databricks-qwen3-embedding-0-6b as the embedding model." />
<figcaption>Compute embeddings, <code>thread_text</code> as the source column, Triggered updates.</figcaption>
</figure>

Note what happens with **Compute embeddings**: you never write an embedding step, and there is no vector column in your table. Databricks reads `thread_text`, calls the model on every row, stores the numbers in the index, and repeats for new rows on each sync. Your table stays readable text.

**Save computed embeddings** stays off. Turning it on writes the numbers to a Delta table as well, which is worth doing when you plan to build a second index over the same text and would rather not pay to compute them twice. 1 index, leave it off.

The same thing from a notebook:

```python
%pip install databricks-ai-search
dbutils.library.restartPython()

from databricks.ai_search.client import AISearchClient

client = AISearchClient()
client.create_endpoint(name="support_search", endpoint_type="STANDARD")

index = client.create_delta_sync_index(
    endpoint_name="support_search",
    source_table_name="support_analytics.silver.ticket_record",
    index_name="support_analytics.silver.ticket_record_index",
    primary_key="issue_id",
    embedding_source_column="thread_text",
    embedding_model_endpoint_name="databricks-qwen3-embedding-0-6b",
    pipeline_type="TRIGGERED",
    columns_to_sync=["issue_id", "thread_text", "connector", "pattern",
                     "fix_type", "severity", "account_tier", "label_source"],
)
```

`columns_to_sync` decides what comes back with each hit. Without it you get an id and the text. With it you get the connector, the pattern and the tier too, and you can narrow a search to one connector or to tickets a human labelled. The classifier needs that second one later.

### 3. Ask it something

```sql
SELECT issue_id, connector, pattern, fix_type
FROM vector_search(
  index => 'support_analytics.silver.ticket_record_index',
  query_text => 'sync fails after the customer tightened the connector role',
  query_type => 'HYBRID',
  num_results => 5
);
```

Every argument is passed by name, with `=>` rather than `=`. That sentence appears in no ticket. The index turns it into numbers, finds the 5 tickets whose numbers sit closest, and returns them.

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/vector-search-result.png" alt="A vector_search query in the Databricks SQL editor returning 5 tickets: a PostgreSQL API rate limit ticket, a NetSuite asking-broader-permissions ticket, Snowflake and SQL Server missing-permissions tickets, and an Amazon S3 credential expiry ticket." />
<figcaption>4 of the 5 are permission problems, across 4 different connectors. None of them contain the words in the query.</figcaption>
</figure>

## The gold layer

Gold is where the questions get answered. Silver has 1 row per ticket; gold has 1 row per thing somebody makes a decision about, which is a pattern, a connector, or a segment of customers.

These are 5 views, not tables. The data is small, and a view is always current, so there is no refresh job to build or forget.

### Cost needs a definition

Ticket count says what happens most. It does not say what to fix, because 6 tickets that each drag on for 2 weeks cost more than 16 that close the same afternoon.

Real engineer hours would be the number to rank on, and nothing records them. A ticket tracker holds timestamps, not effort, and a proxy built from comment counts tracks ticket count too well to reorder anything.

Use time open instead. Sum `hours_to_resolve` across a pattern and you get the total hours that tickets of that kind sat unresolved. That is a real measurement rather than a guess, and it is the cost the customer feels, which is the one the account manager hears about.

### Patterns worth closing

Volume, trend, cost and fix quality in 1 row per pattern.

```sql
CREATE OR REPLACE VIEW support_analytics.gold.pattern_summary AS
SELECT
  t.pattern,
  count(*)                                                      AS tickets,
  round(100.0 * count(*) / sum(count(*)) OVER (), 1)            AS pct_of_all,
  count_if(date_format(t.start_datetime, 'yyyy-MM') = '2026-04') AS apr,
  count_if(date_format(t.start_datetime, 'yyyy-MM') = '2026-05') AS may,
  count_if(date_format(t.start_datetime, 'yyyy-MM') = '2026-06') AS jun,
  round(sum(t.hours_to_resolve))                                AS open_hours,
  round(avg(t.hours_to_resolve), 1)                             AS avg_hours_open,
  round(100.0 * count_if(t.fix_type = 'patch')
        / nullif(count_if(t.fix_type IS NOT NULL), 0), 0)        AS patch_pct
FROM support_analytics.silver.ticket_record t
GROUP BY t.pattern
ORDER BY open_hours DESC;
```

Order by `open_hours`, not by `tickets`, and the list changes. CDC log retention sits 11th by ticket count and 5th by hours, because its 8 tickets average 381 hours each. Asking broader permissions moves the same way. Both are slow for the same reason: someone at the customer has to agree to something before anyone can close them.

`apr`, `may` and `jun` beside each other make the trend readable without a chart. A pattern rising across those 3 columns deserves attention that its total does not yet justify.

### Connectors to prioritise

The same numbers rolled up to the unit the roadmap plans in.

```sql
CREATE OR REPLACE VIEW support_analytics.gold.connector_priority AS
SELECT
  t.connector,
  count(*)                            AS tickets,
  round(sum(t.hours_to_resolve))      AS open_hours,
  round(avg(t.hours_to_resolve), 1)   AS avg_hours_open,
  count_if(t.account_tier = 'enterprise') AS enterprise_tickets,
  mode(t.pattern)                     AS top_pattern
FROM support_analytics.silver.ticket_record t
GROUP BY t.connector
ORDER BY open_hours DESC;
```

`top_pattern` is what makes this actionable. A connector at the top of the list with no dominant pattern needs investigation. One whose tickets are 60% a single cause needs a fix, and `pattern_summary` already says what that fix looks like.

### Time to resolution

Sliced 3 ways, because the average across everything hides the thing you want to see.

```sql
CREATE OR REPLACE VIEW support_analytics.gold.resolution_time AS
SELECT
  connector,
  severity,
  account_tier,
  count(*)                                        AS tickets,
  round(avg(hours_to_resolve), 1)                 AS avg_hours,
  round(percentile(hours_to_resolve, 0.5), 1)     AS median_hours,
  round(percentile(hours_to_resolve, 0.9), 1)     AS p90_hours
FROM support_analytics.silver.ticket_record
GROUP BY connector, severity, account_tier;
```

Median and p90 sit next to the average on purpose. One ticket that stayed open 3 weeks drags an average and changes nothing about the typical experience. The median says what a normal ticket looks like, and p90 says how bad the tail gets.

### Patch debt

Which connectors are accumulating problems that will come back.

```sql
CREATE OR REPLACE VIEW support_analytics.gold.patch_debt AS
SELECT
  connector,
  count_if(fix_type = 'patch')      AS patches,
  count_if(fix_type = 'root_cause') AS root_causes,
  round(100.0 * count_if(fix_type = 'patch')
        / nullif(count_if(fix_type IS NOT NULL), 0), 0) AS patch_pct
FROM support_analytics.silver.ticket_record
GROUP BY connector
HAVING count_if(fix_type IS NOT NULL) > 0
ORDER BY patch_pct DESC;
```

A high patch rate is a forecast. Every patched ticket is a cause still sitting in the code, and the next customer to hit it files the next ticket.

### Documentation gaps

Tickets an engineer answered rather than fixed.

```sql
CREATE OR REPLACE VIEW support_analytics.gold.docs_gaps AS
SELECT
  connector,
  count(*)                        AS tickets,
  round(sum(t.hours_to_resolve))  AS open_hours,
  count_if(t.account_tier = 'enterprise') AS enterprise_tickets
FROM support_analytics.silver.ticket_record t
WHERE t.pattern = 'Lack of documentation'
GROUP BY connector
ORDER BY open_hours DESC;
```

Every hour in `open_hours` here was a customer waiting for an answer a page would have given them. That is the cheapest fix on the whole list and it needs no code change.

### Look at them

```sql
SELECT * FROM support_analytics.gold.pattern_summary;
SELECT * FROM support_analytics.gold.connector_priority;
SELECT * FROM support_analytics.gold.patch_debt;
SELECT * FROM support_analytics.gold.docs_gaps;
```

That is the weekly review, as 4 queries that take a second.

## The chatbot

The gold views answer the questions you knew to ask. Somebody working a ticket has questions you did not.

Databricks ships a chat window called the **Playground**, and it will use your index with no code written. Attach the index as a tool and the model decides for itself when a question needs it. That decision is the whole difference between this and the `vector_search` query from earlier, where you chose to search and typed the search text yourself.

### Set it up

1. Left navigation, under **AI/ML**, open **Playground**.
2. Pick a model labelled **Tools enabled**. Models without the label cannot call anything.
3. **Tools**, then **+ Add tool**, then **AI Search**, then `support_analytics.silver.ticket_record_index`.

That is the setup.

### Ask it something a keyword search would miss

```
What usually goes wrong when a customer's security team gets involved?
```

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/playground-chatbot.png" alt="The Databricks Playground answering a question about customer security teams. It shows the model deciding to search, the tool call to ticket_record_index with a rewritten query, an answer about security teams pushing back on broad permission requests, and 4 cited ticket sources with timestamps and authors." />
<figcaption>Gemma 3 12B, 1 tool, 7 seconds, 4 tickets cited.</figcaption>
</figure>

Three things happened there.

The model **rewrote the question before searching**. It turned "what usually goes wrong when a customer's security team gets involved" into "what are common issues when the security team gets involved with customer tickets". Nobody asked it to. That rewrite is the model working out what to look for.

The answer names **`SELECT ON ALL TABLES`** as a point of contention. That string is nowhere in the question. It came out of the ticket threads, which means retrieval found the right tickets and the model read them rather than reciting what it already knows about security teams.

Every answer **cites the tickets it used**, with timestamps and authors. A wrong answer points at the ticket that misled it instead of leaving you to guess.

The model here is Gemma 3 12B, which is small. The retrieval is carrying the work, not the model, and that is the argument for spending your effort on the thread text and the index rather than on picking a bigger model.

### The other half: the numbers

The index holds ticket threads. Nothing in it knows how many tickets there were, so counting questions need the gold views, and reaching those in a chat window is a different Databricks feature.

**Genie** turns tables into a chat interface. Same idea as the Playground, different source: it writes SQL against tables you give it rather than searching text.

1. In the left navigation, open **Genie** and create a new space.
2. Add all 5 gold views as its data: `pattern_summary`, `connector_priority`, `resolution_time`, `patch_debt` and `docs_gaps`.

Add every one of them. Genie answers from what it can see, and a question about patch rates fails in a space that only holds `pattern_summary`. The views are small and cheap to include, and leaving one out produces a confident answer built from the wrong table rather than an error.

```
Which top 3 connectors should we prioritise fixing?
```

<figure class="diagram">
<img src="/images/posts/support-tickets-as-a-data-product/genie-connector-priority.png" alt="A Genie space answering which top 3 connectors to prioritise. It returns MongoDB, PostgreSQL and Salesforce in a table with total tickets, enterprise tickets and total open hours, followed by written analysis of MongoDB citing 9,347 open hours across 32 tickets, 12 enterprise customers and 67% patch debt." />
<figcaption>MongoDB first, on 32 tickets. PostgreSQL has 41 and comes second.</figcaption>
</figure>

That ordering is the thing to look at. PostgreSQL filed 9 more tickets than MongoDB and still ranks below it, because MongoDB's tickets sat open for 9,347 hours against PostgreSQL's 7,600. Genie was not told that hours matter more than counts. It read the columns the views expose and ranked on the one that measures cost.

The written half of the answer goes further than the table: 292 hours per ticket on MongoDB, the longest of any high-volume connector, 12 enterprise customers affected, and 67% of its fixes were patches rather than root cause fixes. Every one of those numbers comes from a different view, joined by a question nobody wrote SQL for.

Two tools now exist. The index answers what went wrong, Genie answers how much and how many, and an agent given both picks between them.
