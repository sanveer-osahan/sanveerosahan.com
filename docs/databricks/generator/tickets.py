"""Ticket metadata generation. Deterministic given a seed; no model calls here."""

from __future__ import annotations
import datetime as dt
import numpy as np
import pandas as pd
import reference as ref

SEED = 20260421

# Tickets per load. April/May/June are one batch; July ships as weekly files.
# The climb ends at roughly 6 tickets per working day in July, so the batch
# months are sized to land under that: 2.5, 3.8 and 5.0 per working day.
MONTH_VOLUMES = {
    "2026-04": 55,
    "2026-05": 80,
    "2026-06": 110,
}
# Sized at roughly 6 tickets per working day. Week 1 is short (Wed to Sun, so
# three working days); the rest carry five each.
JULY_WEEKS = [  # (label, first_day, last_day, ticket_count)
    ("2026-07-05", dt.date(2026, 7, 1), dt.date(2026, 7, 5), 18),
    ("2026-07-12", dt.date(2026, 7, 6), dt.date(2026, 7, 12), 30),
    ("2026-07-19", dt.date(2026, 7, 13), dt.date(2026, 7, 19), 30),
    ("2026-07-26", dt.date(2026, 7, 20), dt.date(2026, 7, 26), 30),
    ("2026-07-31", dt.date(2026, 7, 27), dt.date(2026, 7, 31), 30),
]

# Weekends carry a quarter of a working day's volume, so a per-day rate means
# something.
WEEKEND_WEIGHT = 0.25

# Two planted trends. Multipliers apply to the base pattern weight, then
# everything is renormalised, so the shape moves without the total drifting.
PATTERN_TRENDS = {
    "Schema drift unhandled":    {"2026-04": 0.40, "2026-05": 0.70, "2026-06": 1.30, "2026-07": 1.90},
    "Private Link setup failed": {"2026-04": 0.50, "2026-05": 0.60, "2026-06": 1.60, "2026-07": 1.70},
}

AMBIGUITY_RATE = 0.15  # threads where the pattern only resolves in the dev's root cause


def _rng() -> np.random.Generator:
    return np.random.default_rng(SEED)


def build_reference_frames(rng) -> dict[str, pd.DataFrame]:
    patterns = pd.DataFrame(ref.PATTERNS)

    rows = []
    for tier, names in (
        ("enterprise", ref.ENTERPRISE_NAMES),
        ("growth", ref.GROWTH_NAMES),
        ("startup", ref.STARTUP_NAMES),
    ):
        for name in names:
            rows.append({"customer_name": name, "account_tier": tier})
    rng.shuffle(rows)
    customers = pd.DataFrame(rows)
    customers.insert(0, "customer_id", [f"CUST-{i:03d}" for i in range(1, len(customers) + 1)])
    customers["region"] = rng.choice(ref.REGIONS, size=len(customers))

    emp = []
    for d in ref.DEVELOPERS:
        emp.append({"name": d["name"], "role": "developer"})
    for n in ref.SUPPORT_ENGINEERS:
        emp.append({"name": n, "role": "support_engineer"})
    for n in ref.MANAGERS:
        emp.append({"name": n, "role": "manager"})
    employees = pd.DataFrame(emp)
    employees.insert(0, "employee_id", [f"EMP-{i:03d}" for i in range(1, len(employees) + 1)])

    return {"patterns": patterns, "customers": customers, "employees": employees}


def _connector_weights() -> np.ndarray:
    """Heavy five carry 65%, light ten carry 35%, with variance inside each group."""
    heavy = np.array([1.35, 1.15, 1.00, 0.90, 0.80])
    heavy = heavy / heavy.sum() * 0.65
    light = np.array([1.30, 1.20, 1.10, 1.05, 1.00, 0.95, 0.90, 0.85, 0.75, 0.65])
    light = light / light.sum() * 0.35
    return np.concatenate([heavy, light])


def _pattern_weights(month: str) -> np.ndarray:
    """Heavy four carry 65% at baseline, then the planted trends bend the shape."""
    w = np.array([0.1700 if n in ref.HEAVY_PATTERNS else 0.0389 for n in ref.PATTERN_NAMES])
    for name, by_month in PATTERN_TRENDS.items():
        w[ref.PATTERN_NAMES.index(name)] *= by_month[month]
    return w / w.sum()


def _customer_weights(customers: pd.DataFrame) -> np.ndarray:
    w = customers["account_tier"].map(ref.TIER_WEIGHTS).to_numpy(dtype=float)
    return w / w.sum()


def _start_datetime(rng, day: dt.date) -> dt.datetime:
    """Business hours weighted, with a tail into evenings and nights."""
    if rng.random() < 0.82:
        hour = int(rng.integers(8, 19))
    else:
        hour = int(rng.choice([0, 1, 2, 3, 4, 5, 6, 7, 19, 20, 21, 22, 23]))
    return dt.datetime(day.year, day.month, day.day, hour,
                       int(rng.integers(0, 60)), int(rng.integers(0, 60)))


def _resolution_hours(rng, severity: str, tier: str, pattern: str) -> float:
    median = ref.SEVERITY_MEDIAN_HOURS[severity]
    hours = median * float(np.exp(0.75 * rng.standard_normal()))
    if tier == "enterprise":
        # Enterprise environments take longer to resolve, and the permission and
        # network patterns are where that shows up most.
        hours *= 1.60 if pattern in {
            "Missing right permissions", "Asking broader permissions", "Private Link setup failed"
        } else 1.25
    return max(hours, 0.5)


def _fix_type(rng, pattern: str) -> str | None:
    if pattern in ref.NO_FIX_PATTERNS:
        return None
    p_patch = 0.72 if pattern in ref.PATCH_LEANING else 0.55
    return "patch" if rng.random() < p_patch else "root_cause"


def _thread_length(rng, severity: str, fix_type: str | None) -> int:
    if fix_type is None:
        return int(rng.integers(3, 7))
    base = {"low": 4, "medium": 6, "high": 8, "critical": 10}[severity]
    if fix_type == "root_cause":
        base += 3
    return int(np.clip(base + rng.integers(-1, 3), 4, 16))


def _pick_day(rng, days: list[dt.date]) -> dt.date:
    """Weekdays carry four times the volume of weekend days."""
    w = np.array([WEEKEND_WEIGHT if d.weekday() >= 5 else 1.0 for d in days])
    return days[int(rng.choice(len(days), p=w / w.sum()))]


def _days_in(month: str) -> list[dt.date]:
    y, m = int(month[:4]), int(month[5:])
    last = (dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1)).day
    return [dt.date(y, m, d) for d in range(1, last + 1)]


def build_tickets() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rng = _rng()
    refs = build_reference_frames(rng)
    customers, employees = refs["customers"], refs["employees"]

    owner = {c: d["name"] for d in ref.DEVELOPERS for c in d["owns"]}
    emp_id = dict(zip(employees["name"], employees["employee_id"]))
    conn_w = _connector_weights()
    cust_w = _customer_weights(customers)

    loads: list[tuple[str, str, list[dt.date], int]] = []
    for month, n in MONTH_VOLUMES.items():
        loads.append(("batch", month, _days_in(month), n))
    for label, first, last, n in JULY_WEEKS:
        days = [first + dt.timedelta(days=i) for i in range((last - first).days + 1)]
        loads.append((f"weekly:{label}", "2026-07", days, n))

    rows, seq = [], 1000
    for load, month, days, n in loads:
        pat_w = _pattern_weights(month)
        for _ in range(n):
            seq += 1
            connector = str(rng.choice(ref.CONNECTORS, p=conn_w))
            pattern = str(rng.choice(ref.PATTERN_NAMES, p=pat_w))
            cust = customers.iloc[int(rng.choice(len(customers), p=cust_w))]
            severity = str(rng.choice(ref.SEVERITIES, p=ref.SEVERITY_WEIGHTS))
            fix_type = _fix_type(rng, pattern)
            start = _start_datetime(rng, _pick_day(rng, days))
            hours = _resolution_hours(rng, severity, cust["account_tier"], pattern)
            rows.append({
                "issue_id": f"4XD-{seq}",
                "customer": cust["customer_id"],
                "connector": connector,
                "pattern": pattern,
                "fix_type": fix_type,
                "severity": severity,
                "assignee": emp_id[owner[connector]],
                "start_datetime": start,
                "resolved_datetime": start + dt.timedelta(hours=float(hours)),
                # Generation-only columns, dropped before the parquet write.
                "_load": load,
                "_thread_len": _thread_length(rng, severity, fix_type),
                "_ambiguous": bool(rng.random() < AMBIGUITY_RATE),
            })

    tickets = pd.DataFrame(rows).sort_values("start_datetime").reset_index(drop=True)
    return tickets, refs


if __name__ == "__main__":
    t, refs = build_tickets()
    print(f"tickets: {len(t)}")
    print("\nper load:\n", t.groupby("_load").size().to_string())
    print("\ntop connectors (share):\n",
          (t["connector"].value_counts(normalize=True).head(5) * 100).round(1).to_string())
    print(f"\nheavy-5 connector share: {t['connector'].isin(ref.HEAVY_CONNECTORS).mean()*100:.1f}%")
    print(f"heavy-4 pattern share:   {t['pattern'].isin(ref.HEAVY_PATTERNS).mean()*100:.1f}%")
    m = t.assign(month=t["start_datetime"].dt.strftime("%Y-%m"))
    print("\nvolume per month and per working day:")
    for month, grp in m.groupby("month"):
        wd = len([d for d in _days_in(month) if d.weekday() < 5])
        print(f"  {month}  {len(grp):>4} tickets   {len(grp)/wd:.1f} per working day")
    print("\nplanted trends (% of month):")
    for p in PATTERN_TRENDS:
        s = m[m["pattern"] == p].groupby("month").size() / m.groupby("month").size() * 100
        print(f"  {p:<28}", s.round(1).to_dict())
    print("\nmedian hours to resolve, enterprise vs rest:")
    j = t.merge(refs["customers"], left_on="customer", right_on="customer_id")
    j["hrs"] = (j["resolved_datetime"] - j["start_datetime"]).dt.total_seconds() / 3600
    print(j.groupby("account_tier")["hrs"].median().round(1).to_string())
