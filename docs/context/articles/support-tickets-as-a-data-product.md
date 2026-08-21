# Context: Support Tickets as a Data Product

Article-local context for `src/content/articles/support-tickets-as-a-data-product.md`.
Site-wide vocabulary and voice live in the root `CONTEXT.md`.

## Status

In progress. Written alongside the Databricks build, so this file leads the
article: decisions land here first, then the prose follows.

Written so far: the opening, the problem statement, the weekly review, the
extracted data, and the nine questions.

## Post type

Explainer at the spine, with a how-to running through it. The spine is the
architecture idea (do the language work once at write time, then everything is
a query). The how-to is the Databricks implementation that proves it. An opinion
lands near the end. One format, explainer, with the build as the supporting
section. Do not switch format mid-article.

## Audience

Anyone who lands on the site, matching the site-wide rule from `CONTEXT.md` and
the precedent set by the coding-agent article: **pitch every explanation at the
reader who knows less.**

A reader who has never administered a database has to follow the problem
statement without stopping. That means no vendor grant syntax, no config flags,
no acronyms on first use. Say "ask for a table you have no permission to see and
the database tells you the table does not exist" rather than naming the
Snowflake privilege that causes it.

An engineer reading the same paragraph still recognises the failure. Writing it
plainly costs that reader nothing.

Deep technical detail is allowed later, once the Databricks build starts and the
reader has opted in. It is banned from the opening and from "Why the queue
grows".

## The worked example

Everything runs against one fictional company, introduced in the opening.

- **4xData**: the company. Sells continuous data movement. A customer points it
  at a source (Postgres, Snowflake, MongoDB, S3), picks tables and cadence, and
  the rows land downstream on schedule with no pipeline code to write.
  **4xData does not sell connectors.** The product is working data movement. A
  connector is how that keeps working for one source, which is why a connector
  bug reads to the customer as the whole product failing.
- **The Connector team**: builds and maintains the source connectors and writes
  the extraction logic. Files more support tickets than any other team.
- **Source**: what the customer connects. Always "source", never "system" or
  "database", because the product word is source.
- **Connector**: the thing the Connector team ships, one per source type. An
  implementation detail to the customer, and the whole job to the team.
- **Sync**: one scheduled run of a connector against a customer's source.

4xData is invented. Do not attach it to a real vendor, and do not invent
revenue figures or customer names for it. The pressure in the story comes from
shape, not from numbers.

## Why the tickets rise (the three drivers)

Keep all three, in this order. Each one is a sign of a healthy company, which is
what makes the problem interesting rather than a story about a bad team.

1. **Breadth**: every new connector is new surface.
2. **Depth**: tables, then views, then CDC, then schema drift. Each layer is a
   requested feature and a new way to fail.
3. **Enterprise security**: least privilege is correct policy, and it is also
   the reason a connector fails on a table it cannot see. The ticket is real,
   the permission is deliberate, the fix differs every time.

## The stakes

Support load crosses a line and becomes a roadmap problem. Hours spent on
tickets are hours not spent on the next connector, and the tickets skew towards
enterprise accounts, so the highest paying customers wait the longest. The
question is not "close tickets faster". It is "which small set of fixes removes
the largest share of future tickets".

## The data

Three months. Four streams, all timestamped, all shaped as "who said what,
when": the issue and its state history, the comments, the linked Slack thread,
and the linked GitHub pull request with its fix summary.

The framing line to reuse: none of this is a document, all of it is a stream of
events, and the first job is folding those streams into one record per ticket.

## The nine questions in scope

Grouped as **Counting**, **Judgement**, **Leverage** in the article.

1. MTTR by connector, severity, customer tier.
2. Top patterns by volume, from a frozen label set.
3. Rising patterns over time.
4. Auto-assign the pattern label.
5. Patch fix or root cause fix.
6. Recurrence after a patch.
7. Cost of a pattern in engineering hours, which ranks connectors to fix.
8. Related tickets for a given ticket.
9. Docs gaps, from tickets closed with an explanation instead of a code change.

Question 7 is the payoff. The article says so out loud at the end of the problem
statement, so the reader knows what the other eight are for.

The chatbot rides along as the interface over questions 1 to 9 rather than as a
tenth question.

## Deliberately out of scope

**Intake-time use cases.** Auto-routing, duplicate detection at creation,
deflection, and escalation prediction all belong to a forward-looking system.
They are a stronger business case and a different article. Mentioning them in
passing at the end is allowed. Building them here is not.

Also out: release regression correlation and generating knowledge base drafts.
Both are reachable from the same pipeline. Neither earns its length here.

## The central claim

RAG is the right tool for two of the nine questions. The rest are ordinary data
work. The leverage sits in the layer nobody puts in the diagram: extraction into
one canonical ticket record, and derived fields written once by a model at
ingest so that read time stays SQL.

## Framing decisions

- **The correction that earns the article**: a pure retrieval chatbot answers
  "what went wrong with the Snowflake connector" well and "how many P1 tickets
  last month" confidently wrong. Give the chatbot a retrieval tool and a query
  tool and let the model choose. This is tool use, not retrieval.
- **Write time versus read time** is the phrase the article turns on. Introduce
  it early and reuse it verbatim.
- **Taxonomy before classifier**. Discovery runs once by clustering. Production
  classifies against a frozen label set. Free-form labels drift and break the
  dashboard. This is a section, not an aside.
- **Open on 4xData, not on the architecture.** The reader recognises the
  weekly review. Nobody recognises a medallion diagram.

## Terms local to this article

- **Ticket record**: the one canonical row per ticket. Issue, ordered comments,
  Slack thread, pull request, and state history. Not "document", not "chunk".
- **Derived field**: a column written by a model at ingest, not at read.
  Examples: fix type, pattern label, affected connector, root cause summary.
- **Pattern**: a label from the frozen taxonomy. Always a label from that set,
  never a free-form phrase the model invented for one ticket.
- **The weekly review**: the manual process being replaced. Use this phrase
  every time, so the before and after stay legible.

## Voice rules for this article

The `write-content` skill governs the prose. Beyond its rules, two habits are
banned here because the first draft was full of them:

- **Three-item lists.** Use two, or four, or restructure. Real technical lists
  of three (connector, severity, account tier) are fine. Rhetorical ones are not.
- **Punchy one-line paragraph endings.** Every section landing on a mic drop is
  the loudest AI tell in the piece.
- **Spelled-out numbers.** Numerals, every time. "6 tables", not "six tables".
  "3 months", not "three months". The pronoun "one" stays a word ("each one",
  "one of them"), because it counts nothing.
- **Databricks vocabulary in the problem statement.** Unity Catalog, AI
  functions, Delta and the rest belong in the build section, once the reader has
  opted in. Naming them earlier loses anyone who has never opened Databricks,
  which contradicts the audience rule above.

Credibility comes from named failure modes, not atmosphere. The draft earns its
keep with `USAGE` on the Snowflake schema, `DBMS_LOGMNR` grants, replication
slots filling a disk, and change streams needing a replica set. Invented detail
like "at three in the morning under load" is banned. Add a failure mode only if
it is true of the real product.

## Open questions

- How much of the Databricks build ships as runnable SQL versus as shape.
- Whether the Databricks concepts get a primer section or get named inline.
- Sanveer to supply real 4xData-equivalent failure modes from his own work, to
  replace or extend the four currently in the draft.
