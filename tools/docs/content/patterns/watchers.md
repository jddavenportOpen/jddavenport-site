---
title: "Watchers: condition until it fires"
description: "A watcher checks one condition on a cadence, pings once when it is true, then stops. Expiry is mandatory. Here's how to build one."
section: patterns
group: "Loops and schedules"
order: 100
updated: 2026-10-05
sources: ["learn/tier-2/07-watchers.mdx"]
---

A watcher answers one question on a schedule: is this true yet? When the answer turns yes, it sends one message and stops. It never pings twice for the same trigger, and it never runs forever. That's the whole primitive, and it fills the gap between cron (durable but dumb) and a session loop (smart but dies with the session).

I built mine in June 2026 because agents kept writing "I'll watch for the reply" into chat, and a chat can't watch anything.

## What you'll learn

- The five check kinds that cover almost every "wait for X"
- A minimal watcher you can build in an afternoon
- The direction check, the expiry rule, and how a watcher pairs with a ledger of promises

## The anatomy

Every watcher has the same parts:

| Field | What it is |
|---|---|
| `title` | A human label. It shows up in the alert. |
| `kind` | Which check to run (see below). |
| `config` | The check's arguments: a search query, a path, a command, a date. |
| `cadence_minutes` | How often to check. |
| `escalate` | The message to send when it fires. Write the next action into it. |
| `expires_at` | Mandatory. When the watcher gives up even if it never fired. |
| `status` | `active`, `triggered` or `expired`. Only `active` ones get checked. |
| `linked_loop` | Optional. The promise in your ledger this watcher is checking. |

Stored as JSON, one entry looks like this:

```json
{
  "id": "w-4f2a",
  "title": "Vendor quote reply",
  "kind": "mail_search",
  "config": { "query": "from:sales@vendor.example subject:quote" },
  "cadence_minutes": 30,
  "escalate": "Vendor replied with the quote. Compare against the budget sheet and answer by Friday.",
  "created_at": "2026-10-01T16:00:00Z",
  "expires_at": "2026-10-31T16:00:00Z",
  "status": "active",
  "next_check_at": "2026-10-01T16:30:00Z"
}
```

## Five check kinds

Mine shipped with four and gained a fifth the same day. These five cover nearly everything I've needed:

| Kind | True when | Typical use |
|---|---|---|
| `mail_search` | A mail search returns something newer than the watcher | Waiting on a reply |
| `file_exists` | A path appears (or disappears) | One script hands off to another |
| `file_mtime` | A file changed, or went stale | A nightly export stopped updating |
| `shell` | An allowlisted command exits 0 or its output matches | A health URL comes back up |
| `date_reached` | Now is past a date, minus a lead time | Token expiries, renewals, due dates |

`date_reached` is the one people forget. The clock is a sensor. "This login token expires in 30 days" is the most common obligation there is, and without a date kind it's inexpressible. Mine got one a few hours after the first version shipped, for exactly that reason: token expiries, renewals and due dates had no way in. Set the lead time so the alert lands while there's still time to act, and put the re-auth command in the alert.

For `shell`, keep an allowlist of command prefixes. A watcher registry is a file, and anything that reads a file and runs what's in it is a code-execution hole if you let it run arbitrary commands.

## A minimal implementation

One sweep function, run by a single cron job every 15 minutes, does all of it:

```python
from json import dump, loads
from os import fdopen, replace
from tempfile import mkstemp
from datetime import datetime, timezone, timedelta
from pathlib import Path

REGISTRY = Path("state/watchers.json")
DEFAULT_EXPIRY = timedelta(days=30)

def now():
    return datetime.now(timezone.utc)

def ts(s):
    # treat a timestamp with no offset as UTC; see "The bug I shipped" below
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

def load():
    return loads(REGISTRY.read_text()) if REGISTRY.exists() else []

def save(watchers):
    # write atomically so a crash mid-write can't corrupt the registry
    fd, tmp = mkstemp(dir=REGISTRY.parent)
    with fdopen(fd, "w") as f:
        dump(watchers, f, indent=2)
    replace(tmp, REGISTRY)

CHECKS = {
    "file_exists": lambda c, w: Path(c["path"]).exists(),
    "date_reached": lambda c, w: now() >= ts(c["date"]) - timedelta(days=c.get("lead_days", 0)),
    # mail_search, file_mtime and shell plug in the same way
}

def sweep(notify):
    watchers, errors = load(), []
    for w in watchers:
        if w["status"] != "active":
            continue
        if now() >= ts(w["expires_at"]):
            w["status"] = "expired"           # expire first; never check a dead watcher
            continue
        if now() < ts(w["next_check_at"]):
            continue
        try:
            fired = CHECKS[w["kind"]](w["config"], w)
        except Exception as e:
            w["last_error"] = str(e)          # a failed check is not a "no"
            errors.append(f"{w['title']}: {e}")
            fired = False
        if fired:
            notify(f"{w['title']}: {w['escalate']}")
            w["status"] = "triggered"         # exactly one ping, then done
        else:
            w["next_check_at"] = (now() + timedelta(minutes=w["cadence_minutes"])).isoformat()
    save(watchers)
    if errors:                                # say so out loud, once per sweep
        notify("Watchers that could NOT be checked:\n" + "\n".join(errors))

if __name__ == "__main__":
    sweep(print)                              # swap print for your real notifier
```

Note what the sweep does before anything else: it expires. A past-due watcher is never checked again, so an expired condition can't wake up and page you about something you stopped caring about a month ago.

The cron line:

```bash
*/15 * * * * cd "$HOME/my-agents" && python3 watchers.py >> logs/watchers.log 2>&1
```

### The bug I shipped

My first version parsed timestamps with `fromisoformat` and nothing else. A date written without an offset, like `2026-07-25T08:00:00`, came back naive. Comparing a naive datetime with an aware one raises `TypeError`, the sweep swallowed per-watcher exceptions, and so the watcher never fired, never errored where anyone could see it, and would have expired quietly. Two of my date watchers were dead that way. I found out in July 2026 when a "remind me in a few days" watcher didn't remind me and I had to remember on my own, which is the exact failure watchers exist to prevent.

Two fixes, both in the sketch above: normalize every timestamp to UTC in one helper, and treat "the check threw" as news to report, never as "nothing found." My real sweep does the same for mail watches: if the mail login is broken, it names every watch it couldn't check instead of letting them all read as quiet.

### The sweep cadence is the floor

One consequence of a single sweep: the sweep cadence is the floor. A watcher set to check every 5 minutes still gets checked every 15 if that's how often the sweep runs. If you need faster, it probably deserves its own job.

## Mandatory expiry

Every watcher expires. Mine default to 30 days and refuse anything past a one-year cap, so a typo can't create an immortal one.

An immortal watcher is just a cron job you can't see in your crontab. Expiry forces a decision: if the condition hasn't fired in a month, either it was the wrong condition or you need to renew it on purpose.

## The direction check

My first real watcher was waiting on a vendor's reply about a warranty claim. The search matched the thread, and I had sent the first email in it, so on its very first sweep the watcher fired on my own outgoing message and told me the vendor had replied.

Any "wait for a reply" search has to be pinned to the sender: `from:` the person or domain you're waiting on. Check the direction of every mail watch before you register it.

## Pair it with a ledger

A watcher is an active sensor. A promise ledger is passive bookkeeping: what's owed, to whom, by when. They do different jobs, so keep them separate and link them.

- The ledger entry says "waiting on the vendor's quote, needed by Friday."
- The watcher checks the inbox every 30 minutes.
- When it fires, it pings once and appends a note to the ledger entry.

Not every promise is checkable. "Decide on the pricing model" needs a human. "The quote arrived" is a mail search. The skill is telling them apart, and wiring a watcher only to the second kind. My ledger is described in [Open loops](/docs/nerve-center/open-loops/).

## Write the alert for future you

The `escalate` text is read by someone who has forgotten why the watcher exists. "Condition met" is useless. "Vendor replied with the quote. Compare against the budget sheet and answer by Friday" is a task. Put the next action in the message, and the command to run if there is one.

**Next:** [Root cause first, never bandaids](/docs/patterns/root-cause-first/)
