#!/usr/bin/env python3
"""Marketplace catalog for jddavenport.com/docs/marketplace/. Python 3 stdlib only.

build.py imports this module and calls catalog_html() for the marketplace section page
and search_entries() for docs/search-index.json, so the docs build stays one command:

    python3 tools/docs/build.py                 # builds docs, including the marketplace
    python3 tools/docs/marketplace.py --refresh # re-vendor the Foundry catalog, then build

Inputs (both vendored, so the build is deterministic and offline):
    tools/docs/marketplace-source.json  snapshot of ai-foundry-byu/foundry-marketplace
                                        site/catalog-index.json (refreshed with --refresh)
    tools/docs/marketplace-local.json   public jddavenportOpen and ai-foundry-byu items,
                                        each repo and install line checked by hand

Rules the cards keep:
  - a maturity label is read from the source evidence, never upgraded here
  - an install line is shown only when a stranger can run it as written
  - AGPL and a missing license are flagged in plain words
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "marketplace-source.json"
LOCAL = HERE / "marketplace-local.json"
UPSTREAM = "ai-foundry-byu/foundry-marketplace"

E = lambda s: html.escape(str(s), quote=True)  # noqa: E731

CATEGORIES = [  # (id, heading, one line)
    ("plugin", "Plugins", "Install a whole set in one command. Updates come with it."),
    ("skill", "Skills", "One folder your agent loads when the task matches."),
    ("agent", "Agents", "Workers you hand a job to: research, phone calls, judging, orchestration."),
    ("hook", "Hooks", "Rules that hold on every tool call, not just when the agent remembers."),
    ("harness", "Harnesses and tools", "The machinery around the agents: orgs, fleets, governors, traces."),
    ("template", "Templates and specs", "Starting points your agent builds out in your own stack."),
    ("guide", "Guides", "Learn by running it."),
    ("workflow", "Workflows", "Several of the items above chained into one job, with a check at the end."),
]
CAT_IDS = {c[0] for c in CATEGORIES}

LABELS = {
    "verified": "Passed a live end-to-end run of its main path in a real Claude Code session.",
    "beta": "Partly live-tested or unit-tested, with known gaps.",
    "new": "Little or no live testing yet. Try it on something low stakes first.",
    "unrated": "Not part of the Foundry's recorded test runs. Its README states its own limits.",
}

# Quoted (lightly shortened) from the Known limits section of the foundry-marketplace README.
FOUNDRY_LIMITS = {
    "foundry-sdlc": ["Projects scaffolded before this release keep an old tools/gen_stories.py; run gen_stories.py --refresh-tools if the stage readout sticks at 4.",
                     "Parallel lanes are protected only as subagents with worktree isolation."],
    "foundry-guardrails": ["A seatbelt, not a vault. The hooks match file names and command shapes, so an unusual command such as an archive round trip can still get past them."],
    "foundry-qa": ["Signed-in QA needs a test-only sign-in route that is off in production.",
                   "The full stage 6 check is heavy: each verifier and persona runs its own Chromium."],
    "foundry-design": ["ui-reviewer and design-system are beta: their latest fixes have not been re-run live."],
    "foundry-devices": ["The Android, iOS Simulator, macOS and Windows commands pass on CI runners but have not run on a student's own app yet.",
                        "macOS automation needs the Accessibility permission for your terminal."],
    "foundry-iphone-mirror": ["It has never driven a real phone. Treat it as experimental."],
    "foundry-evals": ["A suite's score is not held-out accuracy unless you keep a test split and score it separately."],
    "foundry-builder-kit": ["add-auth, scheduled-agents and tmux-agents produce code that is unit-tested but not run end to end. Build and run it yourself before you trust it."],
}
ALL_FOUNDRY_LIMIT = "On smaller models, call a skill by name. Triggering is tuned for Sonnet and Opus."


def load():
    src = json.loads(SOURCE.read_text(encoding="utf-8"))
    local = json.loads(LOCAL.read_text(encoding="utf-8"))
    return src, local


def _maturity_mix(items):
    counts = {}
    for i in items:
        counts[i["maturity"]] = counts.get(i["maturity"], 0) + 1
    order = [m for m in ("verified", "beta", "new") if m in counts]
    if len(order) == 1:
        return order[0], f"All {counts[order[0]]} items {order[0]}."
    # never round up: a mixed plugin is labeled by its weakest item
    weakest = order[-1]
    return weakest, ", ".join(f"{counts[m]} {m}" for m in order) + "."


def foundry_cards(src):
    mk = src["marketplace"]
    cards = []
    for p in src["plugins"]:
        if p.get("external"):
            continue  # recruit is listed once, from its own repo, in the local items
        items = [i for i in src["items"] if i["plugin"] == p["name"]]
        label, mix = _maturity_mix(items)
        kinds = {}
        for i in items:
            kinds[i["type"]] = kinds.get(i["type"], 0) + 1
        inside = [{"name": i["name"], "type": i["type"], "maturity": i["maturity"], "url": i["page_url"]}
                  for i in sorted(items, key=lambda i: (i["type"], i["name"]))]
        cards.append({
            "id": p["name"], "name": p["name"], "category": "plugin", "owner": "AI Foundry",
            "repo": f"https://github.com/{mk['repo']}/tree/main/plugins/{p['name']}",
            "license": "MIT", "maturity": label, "maturity_note": f"Labeled by its weakest item. {mix}",
            "summary": p["description"], "starter": bool(p.get("starter")),
            "install": f"claude plugin marketplace add {mk['repo']} && claude plugin install {p['name']}@{mk['name']}",
            "limits": FOUNDRY_LIMITS.get(p["name"], []) + [ALL_FOUNDRY_LIMIT],
            "inside": inside, "kinds": kinds, "site": mk["site_url"],
        })
    return cards


def all_cards():
    src, local = load()
    cards = foundry_cards(src) + local["items"]
    for c in cards:
        assert c["category"] in CAT_IDS, f"{c['id']}: unknown category {c['category']!r}"
        assert c["maturity"] in LABELS, f"{c['id']}: unknown maturity {c['maturity']!r}"
        assert c["repo"].startswith(("https://github.com/jddavenportOpen/", "https://github.com/ai-foundry-byu/")), c["id"]
    return cards


def _license_html(lic):
    if lic == "AGPL-3.0":
        return '<span class="mk-lic mk-flag" title="Copyleft">AGPL-3.0 · share changes if you run it as a service</span>'
    if lic == "none":
        return '<span class="mk-lic mk-flag">No license file yet · ask before reuse</span>'
    return f'<span class="mk-lic">{E(lic)}</span>'


def card_html(c):
    tag = "Starter set · " if c.get("starter") else ""
    install = ""
    if c.get("install"):
        kind = c.get("install_kind", "Terminal")
        install = (f'<div class="mk-install"><p class="mk-install-k">{E(kind)}</p>'
                   f'<div class="mk-cmd"><code>{E(c["install"])}</code>'
                   f'<button type="button" class="mk-copy" data-copy="{E(c["install"])}" aria-label="Copy install line for {E(c["name"])}">Copy</button></div></div>')
    elif c.get("install_note"):
        install = f'<p class="mk-noinstall">{E(c["install_note"])}</p>'
    limits = "".join(f"<li>{E(x)}</li>" for x in c.get("limits", []))
    limits = f'<details class="mk-limits"><summary>Known limits</summary><ul>{limits}</ul></details>' if limits else ""
    inside = ""
    if c.get("inside"):
        rows = "".join(
            f'<li><a href="{E(i["url"])}" target="_blank" rel="noopener">{E(i["name"])}</a>'
            f'<span class="mk-it">{E(i["type"])}</span><span class="mk-m mk-m-{E(i["maturity"])}">{E(i["maturity"])}</span></li>'
            for i in c["inside"])
        kinds = ", ".join(f"{n} {k}{'s' if n != 1 else ''}" for k, n in sorted(c["kinds"].items()))
        inside = f'<details class="mk-inside"><summary>What is inside: {E(kinds)}</summary><ul>{rows}</ul></details>'
    links = [f'<a href="{E(c["repo"])}" target="_blank" rel="noopener">Source</a>']
    if c.get("docs"):
        links.append(f'<a href="{E(c["docs"])}">Write-up</a>')
    if c.get("site"):
        links.append(f'<a href="{E(c["site"])}" target="_blank" rel="noopener">Item pages</a>')
    note = c.get("maturity_note") or LABELS[c["maturity"]]
    return f"""<li class="mk-card" id="item-{E(c['id'])}">
  <p class="mk-meta"><span class="mk-m mk-m-{E(c['maturity'])}" title="{E(LABELS[c['maturity']])}">{E(c['maturity'])}</span><span>{E(tag)}{E(c['owner'])}</span>{_license_html(c['license'])}</p>
  <h3 class="mk-name">{E(c['name'])}</h3>
  <p class="mk-sum">{E(c['summary'])}</p>
  <p class="mk-note">{E(note)}</p>
  {install}
  {limits}
  {inside}
  <p class="mk-links">{' · '.join(links)}</p>
</li>"""


def workflow_card(a):
    return f"""<li class="mk-card mk-wf" id="item-{E(a.slug)}">
  <p class="mk-meta"><span>Workflow</span></p>
  <h3 class="mk-name"><a href="{a.url}">{E(a.title)}</a></h3>
  <p class="mk-sum">{E(a.description)}</p>
  <p class="mk-links"><a href="{a.url}">Read the steps</a> · {a.minutes} min</p>
</li>"""


def catalog_html(workflows) -> str:
    """HTML for the marketplace section page. workflows: the section's Article objects."""
    cards = all_cards()
    src, _ = load()
    mk = src["marketplace"]
    counts = {cid: sum(1 for c in cards if c["category"] == cid) for cid, _, _ in CATEGORIES}
    counts["workflow"] = len(workflows)
    nav = "".join(f'<li><a href="#cat-{cid}">{E(h)} <span class="mono">{counts[cid]}</span></a></li>'
                  for cid, h, _ in CATEGORIES if counts[cid])
    blocks = []
    for cid, h, line in CATEGORIES:
        if not counts[cid]:
            continue
        if cid == "workflow":
            body = "".join(workflow_card(a) for a in workflows)
        else:
            body = "".join(card_html(c) for c in cards if c["category"] == cid)
        blocks.append(f'<section class="mk-cat" aria-labelledby="cat-{cid}"><h2 id="cat-{cid}" class="group-title">{E(h)}</h2>'
                      f'<p class="mk-cat-line">{E(line)}</p><ol class="mk-grid">{body}</ol></section>')
    labels = "".join(f'<li><span class="mk-m mk-m-{k}">{k}</span> {E(v)}</li>' for k, v in LABELS.items())
    total = len(cards) + len(workflows)
    one_cmd = f"claude plugin marketplace add {mk['repo']}"
    return f"""<div class="mk">
  <p class="mk-total mono">{total} free items · {len(workflows)} workflows · {sum(len(c.get('inside', [])) for c in cards)} individual skills, agents and hooks inside the Foundry plugins</p>
  <div class="mk-start">
    <p class="mk-start-t">Add the AI Foundry marketplace once</p>
    <div class="mk-cmd"><code>{E(one_cmd)}</code><button type="button" class="mk-copy" data-copy="{E(one_cmd)}" aria-label="Copy the marketplace add command">Copy</button></div>
    <p class="mk-start-s">Then install any Foundry plugin by name, or type <code>/plugin</code> inside Claude Code to browse. The Foundry's own item pages are at <a href="{E(mk['site_url'])}" target="_blank" rel="noopener">its marketplace site</a>.</p>
  </div>
  <details class="mk-labels"><summary>What the labels mean</summary><ul>{labels}</ul></details>
  <nav class="mk-nav" aria-label="Marketplace categories"><ul>{nav}</ul></nav>
  {''.join(blocks)}
</div>"""


def search_entries():
    out = []
    for c in all_cards():
        heading = dict((cid, h) for cid, h, _ in CATEGORIES)[c["category"]]
        out.append({"title": c["name"], "description": c["summary"], "section": "Marketplace", "group": heading,
                    "url": f"/docs/marketplace/#item-{c['id']}", "headings": [i["name"] for i in c.get("inside", [])],
                    "text": f"{c['maturity']} {c['license']} {c['owner']} " + " ".join(c.get("limits", []))[:300]})
    return out


def refresh() -> None:
    raw = subprocess.run(["gh", "api", f"repos/{UPSTREAM}/contents/site/catalog-index.json",
                          "-H", "Accept: application/vnd.github.raw"], check=True, capture_output=True, text=True).stdout
    json.loads(raw)  # must parse before it replaces the vendored copy
    SOURCE.write_text(raw if raw.endswith("\n") else raw + "\n", encoding="utf-8")
    print(f"refreshed {SOURCE.name} from {UPSTREAM}")


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh()
    sys.path.insert(0, str(HERE))
    import build  # noqa: E402
    sys.exit(build.build(build.DEFAULT_SECTIONS, build.DEFAULT_CONTENT))
