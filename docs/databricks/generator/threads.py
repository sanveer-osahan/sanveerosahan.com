"""Comment threads and analyst reasoning, written by Claude, one call per ticket.

Results append to out/threads.jsonl as they land, so a crash or an interrupt
costs only the calls in flight. Re-running skips issue_ids already written.
"""

from __future__ import annotations
import argparse, json, os, pathlib, random, sys, threading
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal

from anthropic import Anthropic
from pydantic import BaseModel

import reference as ref
from tickets import build_tickets

MODEL = "claude-sonnet-5"
OUT = pathlib.Path(__file__).parent / "out"
JSONL = OUT / "threads.jsonl"

_write_lock = threading.Lock()


class Comment(BaseModel):
    author_role: Literal["support_engineer", "developer", "manager"]
    channel: Literal["ticket", "slack", "github"]
    visibility: Literal["customer", "internal"]
    text: str


class Thread(BaseModel):
    comments: list[Comment]
    pattern_reasoning: str
    fix_type_reasoning: str


SYSTEM = """You write realistic support ticket threads for 4xData, a data movement \
platform. Customers connect a source (databases, warehouses, NoSQL stores, object \
storage, SaaS apps) and 4xData syncs their data downstream on a schedule.

You are writing internal history, not marketing copy. Every comment reads like a \
working engineer typed it into a ticket, a Slack thread, or a GitHub pull request \
while busy. Specifics over adjectives: error strings, table and column names, row \
counts, grant names, config keys, endpoint names. No pleasantries beyond what a real \
thread carries. Nobody signs their name.

Channel and visibility rules:
- channel "ticket": the support ticket itself. visibility "customer" when the comment \
is written to the customer, "internal" for a note between staff.
- channel "slack": always visibility "internal". Debugging, thinking out loud, short \
messages, fragments, occasional dead ends.
- channel "github": always visibility "internal". Pull request description, review \
comments, or a fix summary. Written about code.

Thread choreography, in order:
1. A support_engineer records their own first analysis of what the customer reported.
2. A developer triages it, usually in slack, and works out what is going on.
3. The developer states the root cause, and on github describes the fix.
4. The developer reports back with a time estimate and a read on how hard it is.
5. The support_engineer writes what goes to the customer, both during the work and \
once it is resolved.
Steps overlap and interleave. A manager appears only on high and critical tickets, \
briefly, asking about impact or timing.

Reasoning fields: an analyst read the whole thread afterwards and wrote down why this \
ticket carries the pattern label it does, and why the fix counts as a patch or a root \
cause fix. Cite what in the thread supports it. Two to four sentences each."""


def build_prompt(t, pattern_row, customer, dev_name, support_name, mgr_name) -> str:
    hours = (t["resolved_datetime"] - t["start_datetime"]).total_seconds() / 3600
    fix = t["fix_type"]
    lines = [
        f"Connector: {t['connector']}",
        f"Customer: {customer['customer_name']} ({customer['account_tier']} tier, {customer['region']})",
        f"Severity: {t['severity']}",
        f"Time to resolution: {hours:.1f} hours",
        "",
        f"Pattern (the cause): {t['pattern']}",
        f"What that means: {pattern_row['pattern_description']}",
        f"The durable fix for this class of problem: {pattern_row['root_cause_fix']}",
        "",
    ]
    if fix is None:
        lines += [
            "No code shipped for this ticket. It was answered, routed to the roadmap, or "
            "closed as working as designed. Do not include any github comments.",
            "Keep the thread short: support records the question, a developer confirms the "
            "behaviour, support writes the answer back to the customer.",
        ]
    elif fix == "patch":
        lines += [
            "The fix that shipped was a PATCH. The developer worked around the immediate "
            "symptom for this customer rather than fixing the cause. Someone should note, "
            "in passing, that the real fix is bigger and has not been done.",
        ]
    else:
        lines += [
            "The fix that shipped was a ROOT CAUSE fix, along the lines of the durable fix "
            "above. It took longer and touched shared code.",
        ]
    lines += [
        "",
        f"Cast: support engineer {support_name}, developer {dev_name}"
        + (f", engineering manager {mgr_name}" if t["severity"] in ("high", "critical") else ""),
        f"Write exactly {t['_thread_len']} comments.",
    ]
    if t["_ambiguous"]:
        lines += [
            "",
            "Make this one genuinely ambiguous early on. The customer's report and the first "
            "few comments should point at a plausible wrong cause, and the real cause should "
            "only become clear when the developer states the root cause.",
        ]
    return "\n".join(lines)


def generate_one(client, t, pattern_row, customer, rng: random.Random) -> dict:
    dev = next(d["name"] for d in ref.DEVELOPERS if t["connector"] in d["owns"])
    support = rng.choice(ref.SUPPORT_ENGINEERS)
    mgr = ref.MANAGERS[0]

    msg = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM,
        output_format=Thread,              # the SDK folds this into output_config.format
        output_config={"effort": "low"},   # generation, not reasoning: keep it cheap
        messages=[{"role": "user", "content": build_prompt(t, pattern_row, customer, dev, support, mgr)}],
    )
    # parsed_output hangs off the text block. Adaptive thinking puts a thinking
    # block first, so content[0] is not safe to index.
    thread: Thread = next(b.parsed_output for b in msg.content if b.type == "text")

    # Timestamps are assigned here, not by the model: monotonic across the ticket's
    # own window, front-loaded so most of the talking happens early.
    start, end = t["start_datetime"], t["resolved_datetime"]
    span = (end - start).total_seconds()
    n = len(thread.comments)
    fracs = sorted(min(0.97, (i + 1) / (n + 1) ** 0.85 * rng.uniform(0.85, 1.15)) for i in range(n))
    names = {"support_engineer": support, "developer": dev, "manager": mgr}

    comments = []
    for c, f in zip(thread.comments, fracs):
        vis = "internal" if c.channel in ("slack", "github") else c.visibility
        comments.append({
            "text": c.text,
            "timestamp": (start + dt.timedelta(seconds=span * f)).isoformat(),
            "commentor": names[c.author_role],
            "channel": c.channel,
            "visibility": vis,
        })
    return {
        "issue_id": t["issue_id"],
        "comments": comments,
        "pattern_reasoning": thread.pattern_reasoning,
        "fix_type_reasoning": thread.fix_type_reasoning,
    }


def _load_dotenv() -> None:
    """Read KEY=value lines from .env beside this file, without adding a dependency."""
    env = pathlib.Path(__file__).parent / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="generate only the first N tickets")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    _load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "No ANTHROPIC_API_KEY. Put it in docs/databricks/generator/.env as\n"
            "  ANTHROPIC_API_KEY=sk-ant-...\n"
            "or export it in your shell."
        )

    tickets, refs = build_tickets()
    patterns = {r["pattern_name"]: r for r in refs["patterns"].to_dict("records")}
    customers = {r["customer_id"]: r for r in refs["customers"].to_dict("records")}

    OUT.mkdir(exist_ok=True)
    done = set()
    if JSONL.exists():
        done = {json.loads(l)["issue_id"] for l in JSONL.read_text().splitlines() if l.strip()}

    todo = [t for _, t in tickets.iterrows() if t["issue_id"] not in done]
    if args.limit:
        todo = todo[: args.limit]
    if not todo:
        print(f"nothing to do; {len(done)} threads already written")
        return
    print(f"{len(done)} already written, generating {len(todo)} with {args.workers} workers")

    client = Anthropic()
    ok = err = 0
    with JSONL.open("a") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(generate_one, client, t, patterns[t["pattern"]],
                        customers[t["customer"]], random.Random(hash(t["issue_id"]) & 0xFFFF)): t
            for t in todo
        }
        for fut in as_completed(futures):
            issue = futures[fut]["issue_id"]
            try:
                rec = fut.result()
            except Exception as e:  # keep going; rerun picks up what failed
                err += 1
                print(f"  {issue} failed: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            with _write_lock:
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
            ok += 1
            if ok % 25 == 0:
                print(f"  {ok}/{len(todo)}")
    print(f"done: {ok} written, {err} failed")


if __name__ == "__main__":
    main()
