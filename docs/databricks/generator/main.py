"""Join ticket metadata with the generated threads and write the parquet loads.

Reads:
  out/batches/batch_*.json   ticket specs (also the per-ticket cast)
  out/threads/batch_*.jsonl  one thread per ticket, written by the agents

Writes a FLAT folder, so the whole thing uploads to a Unity Catalog volume in
one drag and drop. The volume UI takes many files at once but will not take a
folder, so the week lives in the filename rather than in a directory:

  out/parquet/batch_<table>.parquet                     April to June, fully labelled
  out/parquet/weekly_<table>_YYYY-MM-DD.parquet         July, pattern and fix_type null
  out/parquet/{patterns,customers,employees}.parquet    reference data
  out/july_labels.parquet                               held aside, never part of a load
"""
from __future__ import annotations
import datetime as dt
import json, pathlib, random, sys
import pandas as pd
from tickets import build_tickets, JULY_WEEKS

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
PARQUET = OUT / "parquet"

TICKET_COLS = ["issue_id", "assignee", "connector", "fix_type", "severity",
               "start_datetime", "resolved_datetime", "pattern", "customer"]
CONTENT_COLS = ["issue_id", "text", "timestamp", "commentor", "channel", "visibility"]


def load_specs() -> dict[str, dict]:
    specs = {}
    for f in sorted((OUT / "batches").glob("batch_*.json")):
        for spec in json.loads(f.read_text()):
            specs[spec["issue_id"]] = spec
    return specs


def load_threads() -> dict[str, dict]:
    threads, bad = {}, 0
    for f in sorted((OUT / "threads").glob("batch_*.jsonl")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                threads[rec["issue_id"]] = rec
            except (json.JSONDecodeError, KeyError):
                bad += 1
                print(f"  unparseable: {f.name}:{i}", file=sys.stderr)
    if bad:
        print(f"  {bad} bad lines skipped", file=sys.stderr)
    return threads


def comment_times(start, end, n: int, rng: random.Random) -> list[dt.datetime]:
    """Monotonic across the ticket's own window, front-loaded: most of the
    talking happens early, then a gap, then the closing update."""
    span = (end - start).total_seconds()
    fracs = sorted(min(0.97, ((i + 1) / (n + 1)) ** 0.85 * rng.uniform(0.85, 1.15))
                   for i in range(n))
    return [start + dt.timedelta(seconds=span * f) for f in fracs]


def build() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    tickets, refs = build_tickets()
    specs, threads = load_specs(), load_threads()

    missing = [t for t in tickets["issue_id"] if t not in threads]
    if missing:
        print(f"WARNING: {len(missing)} tickets have no thread yet "
              f"(first: {missing[:3]}). They are dropped from this build.", file=sys.stderr)

    emp_id = dict(zip(refs["employees"]["name"], refs["employees"]["employee_id"]))

    content_rows, reasoning_rows = [], []
    for _, t in tickets.iterrows():
        rec = threads.get(t["issue_id"])
        if rec is None:
            continue
        spec = specs[t["issue_id"]]
        cast = {"support_engineer": spec["support_engineer"],
                "developer": spec["developer"],
                "manager": spec.get("manager") or spec["developer"]}
        comments = rec["comments"]
        rng = random.Random(hash(t["issue_id"]) & 0xFFFF)
        for c, ts in zip(comments, comment_times(t["start_datetime"], t["resolved_datetime"],
                                                 len(comments), rng)):
            channel = c["channel"]
            content_rows.append({
                "issue_id": t["issue_id"],
                "text": c["text"],
                "timestamp": ts,
                "commentor": emp_id.get(cast.get(c["author_role"], ""), None),
                "channel": channel,
                # slack and github are internal by construction, whatever the model said
                "visibility": "internal" if channel in ("slack", "github") else c["visibility"],
            })
        reasoning_rows.append({
            "issue_id": t["issue_id"],
            "pattern_reasoning": rec["pattern_reasoning"],
            "fix_type_reasoning": rec["fix_type_reasoning"],
        })

    have = set(threads)
    tickets = tickets[tickets["issue_id"].isin(have)].copy()
    return (tickets, pd.DataFrame(content_rows), pd.DataFrame(reasoning_rows), refs)


def write(df: pd.DataFrame, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # pandas writes datetimes as TIMESTAMP(NANOS) by default. Spark cannot read
    # that and fails with PARQUET_TYPE_ILLEGAL, so coerce to microseconds.
    df.to_parquet(path, index=False,
                  coerce_timestamps="us", allow_truncated_timestamps=True)
    print(f"  {path.relative_to(OUT)}  {len(df)} rows")


def main() -> None:
    tickets, content, reasoning, refs = build()
    if tickets.empty:
        sys.exit("no threads found in out/threads/; run the writers first")

    batch = tickets[tickets["_load"] == "batch"]
    print(f"\nbatch load ({len(batch)} tickets)")
    write(batch[TICKET_COLS], PARQUET / "batch_support_tickets.parquet")
    write(content[content["issue_id"].isin(batch["issue_id"])][CONTENT_COLS],
          PARQUET / "batch_ticket_content.parquet")
    write(reasoning[reasoning["issue_id"].isin(batch["issue_id"])],
          PARQUET / "batch_reasoning.parquet")
    for name in ("patterns", "customers", "employees"):
        write(refs[name], PARQUET / f"{name}.parquet")

    print("\nweekly loads (pattern and fix_type held back)")
    july = []
    for label, *_ in JULY_WEEKS:
        wk = tickets[tickets["_load"] == f"weekly:{label}"]
        if wk.empty:
            continue
        july.append(wk[["issue_id", "pattern", "fix_type"]])
        blind = wk[TICKET_COLS].copy()
        blind["pattern"] = None
        blind["fix_type"] = None
        write(blind, PARQUET / f"weekly_support_tickets_{label}.parquet")
        write(content[content["issue_id"].isin(wk["issue_id"])][CONTENT_COLS],
              PARQUET / f"weekly_ticket_content_{label}.parquet")

    if july:
        print("\nheld aside, not part of any load")
        write(pd.concat(july), OUT / "july_labels.parquet")


if __name__ == "__main__":
    main()
