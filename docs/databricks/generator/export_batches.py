"""Split the 383 tickets into batch spec files for the thread writers."""
from __future__ import annotations
import json, pathlib, random
import reference as ref
from tickets import build_tickets

BATCH_SIZE = 24
OUT = pathlib.Path(__file__).parent / "out"

STYLE = """# How to write a 4xData support thread

4xData is a data movement platform. A customer connects a source (Postgres,
Salesforce, Snowflake, MongoDB, S3, and so on) and 4xData syncs their data
downstream on a schedule. The Connector team builds and owns the connectors.

You are writing internal history, not marketing copy. Every comment reads like a
working engineer typed it while busy.

## Hard rules

- Specifics over adjectives. Error strings, table and column names, row counts,
  grant names, config keys, endpoint names, version numbers.
- Nobody signs their name. No "Hi team". No "Hope this helps".
- Vary length hard. Some Slack messages are four words. Some ticket replies to a
  customer run five sentences.
- No em dashes anywhere.
- Never name the pattern label in the text. The thread shows the problem; the
  label is a judgement made afterwards.

## Channels

- `ticket` : the support ticket. `visibility` is `customer` when written to the
  customer, `internal` for a staff-only note on the ticket.
- `slack`  : always `internal`. Debugging out loud. Fragments, dead ends,
  thinking, short lines.
- `github` : always `internal`. Pull request description, review comment, or fix
  summary. Written about code.

## Who talks, in roughly this order

1. `support_engineer` records their first read of what the customer reported.
2. `developer` triages, usually in slack, and works out what is happening.
3. `developer` states the root cause and describes the fix on github.
4. `developer` reports back with a time estimate and how hard it was.
5. `support_engineer` writes what goes to the customer, during and after.

These interleave. A `manager` appears only on high and critical tickets, briefly,
asking about customer impact or timing.

## The two reasoning fields

An analyst read the whole thread afterwards. `pattern_reasoning` says why this
ticket carries its pattern label, citing what in the thread supports it.
`fix_type_reasoning` says why the fix counts as a patch or a root cause fix. Two
to four sentences each. Reference concrete details from the thread.

## Output

One JSON object per ticket, one per line, in the order given:

{"issue_id":"4XD-1001","comments":[{"author_role":"support_engineer","channel":"ticket","visibility":"customer","text":"..."}],"pattern_reasoning":"...","fix_type_reasoning":"..."}

Exactly `comment_count` comments per ticket. No markdown fences, no commentary.
"""


def main() -> None:
    tickets, refs = build_tickets()
    patterns = {r["pattern_name"]: r for r in refs["patterns"].to_dict("records")}
    customers = {r["customer_id"]: r for r in refs["customers"].to_dict("records")}

    specs = []
    for _, t in tickets.iterrows():
        rng = random.Random(hash(t["issue_id"]) & 0xFFFF)
        dev = next(d["name"] for d in ref.DEVELOPERS if t["connector"] in d["owns"])
        cust = customers[t["customer"]]
        pat = patterns[t["pattern"]]
        hours = (t["resolved_datetime"] - t["start_datetime"]).total_seconds() / 3600
        spec = {
            "issue_id": t["issue_id"],
            "connector": t["connector"],
            "customer": f'{cust["customer_name"]} ({cust["account_tier"]} tier, {cust["region"]})',
            "severity": t["severity"],
            "hours_to_resolve": round(hours, 1),
            "pattern": t["pattern"],
            "pattern_means": pat["pattern_description"],
            "durable_fix_for_this_pattern": pat["root_cause_fix"],
            "fix_type": t["fix_type"],
            "comment_count": int(t["_thread_len"]),
            "support_engineer": rng.choice(ref.SUPPORT_ENGINEERS),
            "developer": dev,
            "manager": ref.MANAGERS[0] if t["severity"] in ("high", "critical") else None,
            "ambiguous_early": bool(t["_ambiguous"]),
        }
        if t["fix_type"] is None:
            spec["note"] = ("No code shipped. Answered, routed to the roadmap, or closed as "
                            "working as designed. No github comments at all. Keep it short.")
        elif t["fix_type"] == "patch":
            spec["note"] = ("The fix was a PATCH: worked around the symptom for this customer. "
                            "Someone should note in passing that the real fix is bigger and "
                            "has not been done.")
        else:
            spec["note"] = ("The fix was a ROOT CAUSE fix, along the lines of the durable fix. "
                            "It took longer and touched shared code.")
        if spec["ambiguous_early"]:
            spec["note"] += (" Make this one ambiguous early: the first few comments point at a "
                             "plausible wrong cause, and the real cause only lands when the "
                             "developer states the root cause.")
        specs.append(spec)

    bdir = OUT / "batches"
    bdir.mkdir(parents=True, exist_ok=True)
    (bdir / "STYLE.md").write_text(STYLE)
    (OUT / "threads").mkdir(parents=True, exist_ok=True)

    n = 0
    for i in range(0, len(specs), BATCH_SIZE):
        n += 1
        (bdir / f"batch_{n:02d}.json").write_text(json.dumps(specs[i:i + BATCH_SIZE], indent=1))
    print(f"{len(specs)} tickets -> {n} batches of up to {BATCH_SIZE} in {bdir}")


if __name__ == "__main__":
    main()
