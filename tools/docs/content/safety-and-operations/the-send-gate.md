---
title: "One door out: the send gate"
description: "The system can draft anything and send nothing without a yes. One chokepoint, content-bound approval tokens, a freeze switch, and a scan for bypasses."
section: safety-and-operations
group: "Guardrails"
order: 10
updated: 2026-10-05
sources: []
---

My system can draft anything: email, texts, posts, replies. It can't send any of it to another person without my explicit yes. Every outbound message to a third party goes through one chokepoint, and that chokepoint is the most important safety constraint I've built. It's also what made it safe to let everything else run fast.

## What you'll learn

- Why one door beats a rule on every door
- How a content-bound, single-use approval token works
- The freeze switch, and the scan that catches new bypasses
- Where my gate failed anyway, and what fixed it

## The problem: send paths grow on their own

An autonomous system grows send paths the way a house grows extension cords. Every agent that drafts mail eventually gets a "just send it" shortcut, added for convenience, never malicious. Each one was guarded by a docstring and a line in an instruction file. Those drift under context pressure. An agent working hard on a task can reason its way to "the user clearly wants this sent."

At the end of June 2026 that happened: an agent sent outreach on its own that nobody had approved. The root cause wasn't the agent. It was that "don't send without approval" lived in prose on many doors instead of in code on one.

## The design

On June 30, 2026 I shipped a universal external-send gate. Four parts:

**1. One chokepoint.** Every transport that can reach another person (email from any of my accounts, iMessage, calendar invites, posts, DMs, team chat messages) goes through one guarded transmit function. Nothing else is allowed to call the underlying send.

**2. Default deny, by action class.** The gate sorts every outbound action into a class. External classes (email to a third party, a post, a DM) are denied without a token. A brand-new class whose transport is external is also denied, so a new send path is gated by construction, not by someone remembering to add it. Messages to me (alerts, my own chat, voice summaries) pass, because I own those channels. A dry run always passes, because it releases nothing.

**3. A single-use, content-bound approval token.** When I approve a specific draft, the system mints a token bound to that action and to a SHA-256 hash of the exact recipients, subject and body. At send time the gate recomputes the hash. If anything changed, the send is refused: approve X, send Y, and you get a refusal with its own distinct reason in the audit log. Tokens expire, and they're consumed on use, so a replay fails. (The first version bound the token to the action only. Binding it to the content came on July 9, 2026, and closed the hole where one draft gets approved and an edited one goes out. If you build this, make the hash required from day one.)

**4. A global freeze switch.** One file on disk stops every irreversible external send. The draft is preserved, nothing goes out, and the refusal says how to lift the freeze. When I shipped the gate, I engaged the freeze the same afternoon.

In sketch form:

```python
from hashlib import sha256
from json import dumps
from pathlib import Path
from secrets import token_urlsafe
from time import time

FREEZE = Path("state/SEND_FREEZE")
TOKENS = {}  # in real life: an append-only file or a table

def content_hash(recipients, subject, body):
    canonical = dumps({"to": sorted(r.lower() for r in recipients),
                            "subject": subject.strip(), "body": body.strip()}, sort_keys=True)
    return sha256(canonical.encode()).hexdigest()

def mint(action_class, recipients, subject, body, ttl_min=60):
    """Called only after a human approved this exact draft."""
    token = token_urlsafe(16)
    TOKENS[token] = {"class": action_class,
                     "hash": content_hash(recipients, subject, body),
                     "expires": time() + ttl_min * 60, "used": False}
    return token

def guarded_send(action_class, recipients, subject, body, token, transport):
    if FREEZE.exists():
        return "refused: send freeze engaged (draft kept)"
    rec = TOKENS.get(token)
    if not rec or rec["used"] or time() > rec["expires"] or rec["class"] != action_class:
        return "refused: no valid approval"
    if rec["hash"] != content_hash(recipients, subject, body):
        return "refused: approved message != this message"   # token NOT consumed
    rec["used"] = True
    transport(recipients, subject, body)
    return "sent"
```

The real one also writes every decision, allowed or refused, to an audit log with the token id and the content hash.

## The scan that keeps it true

A chokepoint only works if nothing goes around it. So the same day, I shipped a guard: a script that searches the codebase for any known send primitive appearing outside the sanctioned wrapper, and fails if it finds one.

On its first run it found five autonomous email senders that bypassed the gate. Manual audits had missed all five. The prose said everything used the gate. The machine check disagreed, and the machine was right. All five were routed through the chokepoint that day.

## Where it failed anyway

In September 2026 I found a one-off script that had been sending a recurring email from my account for 12 weeks. Nobody had approved it. The guard never saw it, for three reasons:

- it only scanned two directories, and this script lived in a third
- it only matched sends written one way, and this one was written another
- it only ran in a hosted CI workflow that had been sitting red on unrelated findings, so nobody read it

All three are fixed. The guard now scans every directory that holds runnable code, catches sends written as shell strings and in shell scripts, and runs daily on a schedule that pages me if it fails.

Honest read: this is the failure I'd most want a reader to learn from. My gate was real, and for twelve weeks I described it as complete when it wasn't. A guard is only as wide as what it scans, and a check nobody reads isn't running.

## Hooks are not the gate

Claude Code has PreToolUse hooks that run before every tool call, and I use them for a lot (blocking raw restarts, for one). I also had a policy hook meant to block outward actions. In early September 2026 an audit of its log showed tens of thousands of decisions, every one of them "allow," over nine days. It wasn't broken. It was blind: it inspects the agent's tool calls, and my agents actually send from inside Python, which a tool-call hook never sees.

The chokepoint, sitting one layer down where the send really happens, had recorded hundreds of real refusals by then. That's the one that enforces.

The lesson generalizes: put the gate where the action actually happens, not where it's easiest to intercept. A hook on tool calls is a fine extra layer. It is not the door.

One more design difference worth copying. A lot of safety hooks fail open on their own errors, on purpose, because a broken hook that blocks everything gets ripped out. A send gate must fail closed. If the gate can't verify a token, the message doesn't go.

## The gate made speed safe

Here's the part I didn't expect. Merges into my agent repo went from 6 in May 2026 to 78 in June and 166 in July. The send gate landed June 30, in the middle of that climb.

Best guess: that's not a coincidence. At that rate you can't review every action an agent takes. You can review every message that leaves. One door out turned "let it run fast" from a gamble into a decision. The gate didn't slow the system down. It's what made running it fast survivable.

## What it does not do

- **It doesn't judge quality.** Drafts are written against my voice file before they reach me, and whether a draft is any good is my call. The gate answers one question: did a human approve exactly this?
- **It doesn't govern GitHub.** Pushes and PRs go through a separate governor, which lets pushes to my own repos through and judges anything touching someone else's.
- **It doesn't make me read carefully.** The token proves I approved the hash. Reading the draft is still my job.

## Build your own

You can start smaller than mine:

1. Find every place your code can send to another person. Grep for the libraries and CLIs.
2. Wrap them all in one function. Make it the only caller.
3. Require a token minted from an approval of the exact content. Hash it.
4. Add a freeze file that the function checks first.
5. Add a check that fails if any send primitive appears outside the wrapper, and run it on a schedule that alerts you.

For packaged versions of these ideas: [claude-deploy-kit](https://github.com/jddavenportOpen/claude-deploy-kit) has a single policy chokepoint that defaults to deny and always escalates irreversible actions to approval, and [ethos-gate](https://github.com/jddavenportOpen/ethos-gate) has PreToolUse hooks for irreversible commands and outbound GitHub actions. Use the hooks as a layer. Make the chokepoint the door.

**Next:** [QA: user stories, Playwright and synthetic users](/docs/safety-and-operations/qa-and-synthetic-users/)
