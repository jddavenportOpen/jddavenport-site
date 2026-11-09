#!/usr/bin/env python3
"""Refresh the dated fallback snapshot in brain.html and showcase.html.

    python3 tools/metrics/refresh_snapshot.py             # fetch live, rewrite both pages
    python3 tools/metrics/refresh_snapshot.py --dry-run   # fetch and validate, write nothing

Both pages upgrade their numbers from /api/metrics on load. What this script
owns is what a visitor sees when that request fails: the baked numbers, the
"Snapshot" chip, the fine-print date and the inline SNAP / live data. deploy.sh
runs it on every deploy so the fallback cannot sit stale again.

It rewrites those blocks in place. The pages are the source of truth now: the
old one-shot generators (~/clawd/projects/jd-portfolio/showcase/build_*.py) are
behind them on copy, so re-running those would regress the pages.

Failure policy: anything wrong (network, bad JSON, a missing field, a block the
page no longer has, a guard tripping) keeps the old snapshot in BOTH pages,
prints a warning and exits 0. A deploy never fails over a fallback number.

Guards, all fatal to the refresh and never to the deploy:
  - the snapshot is built from an explicit allowlist, so no dollar field can
    arrive from upstream, and the result is scanned for one anyway
  - static prose keeps the counting rule (30+ / 100+): a precise agent count
    outside a data-k element refuses the write
  - a feed older than the snapshot already baked in is ignored

Python 3 standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS_URL = "https://jddavenport.com/api/metrics"
TIMEOUT_S = 15

# Same order, colors and labels as the CAT table in brain.html.
CATS = [
    ("self-heal / watchdog", "#69B27A", "Self-healing watchdogs"),
    ("routing / infra", "#7CB4CF", "Routing and infrastructure"),
    ("delivery", "#F5A623", "Delivery"),
    ("capture", "#F8C384", "Capture"),
    ("memory", "#B8A4DC", "Memory"),
    ("backup / storage", "#827F7C", "Backup and storage"),
    ("other", "#5E5B58", "General background jobs"),
]
WATCHDOG = "self-heal / watchdog"


class Keep(Exception):
    """Keep the old snapshot. The message says why."""


def _count(v, what):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise Keep(f"{what} is not a count: {v!r}")
    return v


def _counts(d, what):
    if not isinstance(d, dict) or not d:
        raise Keep(f"{what} missing")
    return {str(k): _count(v, f"{what}.{k}") for k, v in d.items()}


def snapshot(feed: dict) -> dict:
    """Reduce the feed to exactly the fields the pages render. Allowlist only."""
    if not isinstance(feed, dict):
        raise Keep("feed is not an object")
    as_of = feed.get("as_of")
    if not (isinstance(as_of, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of)):
        raise Keep(f"bad as_of: {as_of!r}")
    stats = feed.get("stats") or {}
    metrics = feed.get("metrics") or {}
    structure = feed.get("structure") or {}
    kinds = _counts(structure.get("agents_by_kind"), "agents_by_kind")
    jobs = _counts(structure.get("jobs_by_category"), "jobs_by_category")
    scopes = _counts(structure.get("skills_by_scope"), "skills_by_scope")
    if WATCHDOG not in jobs:
        raise Keep("no watchdog count")

    ships_per_day = structure.get("ships_per_day")
    if not (isinstance(ships_per_day, list) and ships_per_day):
        raise Keep("ships_per_day missing")
    ships_per_day = [_count(v, "ships_per_day") for v in ships_per_day]

    tokens = metrics.get("tokens_30d_sparkline")
    if not (isinstance(tokens, list) and tokens):
        raise Keep("tokens_30d_sparkline missing")
    tokens = [{"d": str(p["d"])[:10], "total": _count(p["total"], "sparkline.total")}
              for p in tokens if isinstance(p, dict) and "d" in p and "total" in p]
    if not tokens:
        raise Keep("tokens_30d_sparkline has no usable points")

    snap = {
        "as_of": as_of,
        "stats": {k: _count(stats.get(k), f"stats.{k}")
                  for k in ("agents", "skills", "automations", "ships_last_30d")},
        "metrics": {
            "turns_yesterday": _count(metrics.get("turns_yesterday"), "turns_yesterday"),
            "tokens_30d_sparkline": tokens,
        },
        "structure": {
            "agents_by_kind": kinds,
            "skills_by_scope": scopes,
            "jobs_by_category": jobs,
            "ships_per_day": ships_per_day,
        },
    }
    if snap["stats"]["agents"] == 0 or snap["stats"]["automations"] == 0:
        raise Keep("feed reports zero agents or jobs, refusing to bake that in")
    return snap


def _bars_brain(values):
    m = max(values) or 1
    w = 120 / len(values)
    out = []
    for i, v in enumerate(values):
        h = max(1.5, 26 * v / m)
        out.append(f'<rect x="{i * w:.2f}" y="{28 - h:.1f}" width="{w * 0.75:.2f}" height="{h:.1f}" rx="1"/>')
    return "".join(out)


def _bars_showcase(values):
    m = max(values) or 1
    out = []
    for i, v in enumerate(values):
        h = max(1.5, 26 * v / m)
        out.append(f'<rect x="{i * 4}" y="{28 - h:.1f}" width="3" height="{h:.1f}" rx="1"/>')
    return "".join(out)


def _sub(page, pattern, repl, what, flags=0):
    new, n = re.subn(pattern, lambda m: m.group(1) + repl + (m.group(2) if m.re.groups > 1 else ""), page, flags=flags)
    if n == 0:
        raise Keep(f"block not found: {what}")
    return new


def _shared(page, as_of):
    page = _sub(page, r'(<span id="chip-text">Snapshot · )[^<]*(</span>)', as_of, "chip date")
    return _sub(page, r"(the snapshot from )\d{4}-\d{2}-\d{2}()", as_of, "fine-print date")


def _num(page, key, value):
    return _sub(page, rf'(<b data-k="{key}">)[^<]*(</b>)', f"{value:,}", f"data-k {key}")


def _spark(page, sid, bars):
    return _sub(page, rf'(<svg [^>]*id="{sid}"[^>]*>).*?(</svg>)', bars, f"spark {sid}", re.S)


def render_brain(page: str, snap: dict) -> str:
    st, s = snap["structure"], snap["stats"]
    a = st["agents_by_kind"]
    spec = sum(n for k, n in a.items() if k not in ("orchestrator", "domain"))
    page = _shared(page, snap["as_of"])
    for key, value in (
        ("orch", a.get("orchestrator", 1)),
        ("dom", a.get("domain", 0)),
        ("spec", spec),
        ("skills", sum(st["skills_by_scope"].values())),
        ("jobs", sum(st["jobs_by_category"].values())),
        ("turns", snap["metrics"]["turns_yesterday"]),
        ("ships", s["ships_last_30d"]),
    ):
        page = _num(page, key, value)
    cats = "".join(
        f'<li><span class="sw" style="background:{col}"></span><span>{label}</span><b>{st["jobs_by_category"][key]:,}</b></li>'
        for key, col, label in CATS if st["jobs_by_category"].get(key))
    page = _sub(page, r'(<ul class="cats" id="cats">).*?(</ul>)', cats, "job categories", re.S)
    page = _spark(page, "spark-tok", _bars_brain([p["total"] for p in snap["metrics"]["tokens_30d_sparkline"]]))
    page = _spark(page, "spark-ship", _bars_brain(st["ships_per_day"]))
    return _sub(page, r"^( var SNAP=).*?(;)$", json.dumps(snap), "SNAP", re.M)


def render_showcase(page: str, snap: dict) -> str:
    st, s = snap["structure"], snap["stats"]
    live = {
        "agents": s["agents"],
        "automations": s["automations"],
        "watchdogs": st["jobs_by_category"][WATCHDOG],
        "ships": s["ships_last_30d"],
    }
    page = _shared(page, snap["as_of"])
    for key, value in live.items():
        # The headline agent count follows the counting rule in static copy
        # (30+ / 100+), so showcase has no data-k="agents" element any more.
        if key == "agents" and f'data-k="{key}"' not in page:
            continue
        page = _num(page, key, value)
    page = _spark(page, "spark", _bars_showcase(st["ships_per_day"]))
    return _sub(page, r"(, live=)\{[^}]*\}(;)", json.dumps(live), "live defaults")


def check_guards(page: str, name: str) -> None:
    if re.search(r"\$\s?\d", page) or re.search(r"usd|\$70M", page, re.I):
        raise Keep(f"{name}: dollar figure in page")
    # Counting rule: outside a generator-fed data-k element, no precise agent
    # count. "30+ agents" passes, "48 agents" does not.
    prose = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    prose = re.sub(r'<b data-k="[^"]*">[^<]*</b>', " ", prose)
    prose = re.sub(r"<[^>]*?(?:content|aria-label)=\"([^\"]*)\"[^>]*>", r" \1 ", prose)
    prose = re.sub(r"<[^>]+>", " ", prose)
    hit = re.search(r"\b\d[\d,]*\s+(?:[a-z]+\s+)?agents?\b", prose)
    if hit:
        raise Keep(f"{name}: precise agent count in static prose: {hit.group(0)!r}")


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "jddavenport-site-deploy/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return json.loads(r.read().decode("utf-8"))


def _write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(tmp, path.stat().st_mode & 0o777)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def refresh(feed: dict, root: Path = ROOT, dry_run: bool = False) -> str:
    """Compute both pages in memory, then write both. Raises Keep to change nothing."""
    snap = snapshot(feed)
    brain_path, showcase_path = root / "brain.html", root / "showcase.html"
    brain, showcase = brain_path.read_text("utf-8"), showcase_path.read_text("utf-8")

    baked = re.search(r'<span id="chip-text">Snapshot · (\d{4}-\d{2}-\d{2})</span>', brain)
    if baked and snap["as_of"] < baked.group(1):
        raise Keep(f"feed as_of {snap['as_of']} is older than the baked {baked.group(1)}")

    new_brain, new_showcase = render_brain(brain, snap), render_showcase(showcase, snap)
    check_guards(new_brain, "brain.html")
    check_guards(new_showcase, "showcase.html")
    if new_brain == brain and new_showcase == showcase:
        return f"snapshot already current ({snap['as_of']})"
    if dry_run:
        return f"dry run: would bake snapshot {snap['as_of']}"
    _write(brain_path, new_brain)
    _write(showcase_path, new_showcase)
    return f"baked snapshot {snap['as_of']}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    url = os.environ.get("SNAPSHOT_METRICS_URL", METRICS_URL)
    try:
        print("refresh_snapshot:", refresh(fetch(url), dry_run=a.dry_run))
    except Exception as e:  # noqa: BLE001  (the contract: never fail the deploy)
        print(f"refresh_snapshot: WARNING, keeping the old snapshot: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
