"""Check generated thread batches against their specs."""
from __future__ import annotations
import json, pathlib, sys

OUT = pathlib.Path(__file__).parent / "out"
ROLES = {"support_engineer", "developer", "manager"}
CHANNELS = {"ticket", "slack", "github"}
KEYS = {"author_role", "channel", "visibility", "text"}


def check(n: int) -> list[str]:
    spec_f = OUT / "batches" / f"batch_{n:02d}.json"
    thr_f = OUT / "threads" / f"batch_{n:02d}.jsonl"
    if not thr_f.exists():
        return [f"batch_{n:02d}: no output file"]
    specs = {s["issue_id"]: s for s in json.loads(spec_f.read_text())}
    errs = []
    seen = set()
    for i, line in enumerate(thr_f.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            errs.append(f"batch_{n:02d}:{i} bad json: {e}")
            continue
        iid = r.get("issue_id")
        s = specs.get(iid)
        if s is None:
            errs.append(f"batch_{n:02d}:{i} unknown issue_id {iid}")
            continue
        seen.add(iid)
        for f in ("pattern_reasoning", "fix_type_reasoning"):
            if not str(r.get(f, "")).strip():
                errs.append(f"{iid}: empty {f}")
        cs = r.get("comments") or []
        if len(cs) != s["comment_count"]:
            errs.append(f"{iid}: {len(cs)} comments, spec says {s['comment_count']}")
        for c in cs:
            if set(c) != KEYS:
                errs.append(f"{iid}: comment keys {sorted(set(c) ^ KEYS)}")
                continue
            if c["author_role"] not in ROLES:
                errs.append(f"{iid}: bad role {c['author_role']}")
            if c["channel"] not in CHANNELS:
                errs.append(f"{iid}: bad channel {c['channel']}")
            if c["channel"] in ("slack", "github") and c["visibility"] != "internal":
                errs.append(f"{iid}: {c['channel']} marked {c['visibility']}")
            if c["author_role"] == "manager" and not s.get("manager"):
                errs.append(f"{iid}: manager speaks on a {s['severity']} ticket")
            if s["fix_type"] is None and c["channel"] == "github":
                errs.append(f"{iid}: github comment on a no-code ticket")
            if s["pattern"].lower() in c["text"].lower():
                errs.append(f"{iid}: pattern label leaked into comment text")
    for iid in set(specs) - seen:
        errs.append(f"{iid}: missing from output")
    return errs


# Batches whose agent has reported completion. Validating a file mid-write
# produces false failures, so only these are checked.
DONE = set(range(1, 17))

if __name__ == "__main__":
    total_err = 0
    for n in sorted(DONE):
        if not (OUT / "threads" / f"batch_{n:02d}.jsonl").exists():
            continue
        e = check(n)
        total_err += len(e)
        print(f"batch_{n:02d}: {'OK' if not e else str(len(e)) + ' problems'}")
        for x in e[:12]:
            print("   ", x)
    print(f"\n{total_err} problems total")
