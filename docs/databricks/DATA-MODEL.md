# Synthetic support ticket dataset

Domain model for the generated dataset behind the article
`src/content/articles/support-tickets-as-a-data-product.md`.

## Purpose

Three months of tickets (April, May, June 2026) carry human-assigned `pattern`
and `fix_type`, plus the analyst's written reasoning for both. That is the
training set. July 2026 arrives as weekly loads with neither label. A model
trained on the three months predicts them.

The reasoning columns exist because a human analysed the ticket. They are the
record of that judgement, not prompt scaffolding.

## Settled terms

- **Pattern**: the cause of a ticket, from a frozen list in `patterns`. Causes
  only. An earlier round split this into cause and effect columns; that was
  reversed. "Connector not scalable" is a cause, not a symptom.
- **Fix type**: `patch` or `root_cause`. Nullable, because a feature request
  and a works-as-designed ticket ship neither.
- **Reasoning**: the human analyst's written justification for the pattern and
  the fix type on one ticket. April to June only. Never present for July.
- **Channel**: the surface a comment was written on. `ticket`, `slack`, or
  `github`.
- **Visibility**: whether a comment reached the customer. `customer` or
  `internal`. Slack and GitHub are always internal. Ticket comments are either.
- **Severity**: `low`, `medium`, `high`, `critical`. Priority uses P-numbers
  elsewhere in the business, so severity avoids them.
- **Employee**: whoever is assigned to a ticket or comments on it. Carries a
  role, because role drives the order of the thread.

## Settled decisions

| Decision | Outcome |
|---|---|
| Volume | ~400 tickets across April, May, June, rising month over month |
| Concentration | 35 / 65 rather than a strict 20 / 80 Pareto |
| Ticket status | Resolved only. Analysis runs on resolved tickets. |
| `Missing right permissions` vs `Asking broader permissions` | Stay separate. Different fixes. Needs a hard rule in `pattern_description` so labelling stays consistent. |
| `Lack of Documentation` | Stays a pattern. A human labelled it, so the model predicts it on July rather than discovering it. |
| Comment text | LLM-generated per ticket, whole thread in one call |
| `reasoning` for July | None |
| Roles | `support_engineer`, `developer`, `manager` |
| Volume | April 55, May 80, June 110 (batch), July 138 across five weekly files |
| Rate | The climb ends at ~6 tickets per working day in July. Weekends carry a quarter of a working day. |
| Patterns | 13, causes only. Heavy four carry 65%. |
| Connectors | 15. Heavy five carry 65%. |
| Planted trends | `Schema drift unhandled` climbs Apr to Jul. `Private Link setup failed` steps up in June and holds. |
| Team size | Sized from ownership: one developer owns one high-volume connector plus two low-volume ones |
| Thread length | 4 to 16 comments, median 7, scaled by severity and fix type |

## Thread choreography

Every ticket follows the same shape, driven by role:

1. Support writes their own analysis first.
2. Dev triages, fixes, and writes the root cause.
3. Dev communicates the issue and the fix back, with timeline estimates and a
   read on complexity.
4. Support writes what goes to the customer, both while dev works and after
   resolution.

## Tables

`support_tickets`, `ticket_content`, `patterns`, `reasoning`, `customers`,
`employees`. Column lists land here once round 2 settles.

## Databricks naming

Catalog `support_analytics`, schemas `bronze` / `silver` / `gold`, volume
`support_analytics.bronze.raw`.

Not named after the company. Unity Catalog names cannot start with a digit, so
`4xData` needs a workaround spelling, and naming a catalog after the company
adds nothing when the whole workspace is that company. The catalog says what it
holds instead.

Volume layout mirrors `out/parquet/`:

```
/Volumes/support_analytics/bronze/raw/batch/<table>.parquet
/Volumes/support_analytics/bronze/raw/weekly/week=2026-07-05/<table>.parquet
```

`week=` is load-bearing. Databricks reads it as a partition column, so the load
date arrives as data without a column in any file.

## Generated dataset, as built

383 tickets. 245 labelled (April to June), 138 unlabelled (July, 5 weekly
loads). 2,886 comments. Written by 16 background agents against
`out/batches/STYLE.md`, validated by `validate.py`, assembled by `main.py`.

`out/july_labels.parquet` holds the true July labels and sits outside both load
folders.

## Open

Nothing from the grilling session. Next work is the Databricks build itself.
