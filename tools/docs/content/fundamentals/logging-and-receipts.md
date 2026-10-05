---
title: "Logging and receipts: making agent work inspectable"
description: "No artifact, no accountability. One-line ship logs, daily rollups, run ledgers and receipts that say what really happened."
section: fundamentals
group: "Working habits"
order: 110
updated: 2026-10-05
sources: ["learn/tier-1/11-logging.mdx", "frameworks/accountability-artifacts.mdx"]
---

When you run one agent, you watch it work. When you run many, some of them on schedules you set up weeks ago, you can't watch anything. You read what they left behind. So the rule in my system is short: no artifact, no accountability. Every material action leaves a file or a row, and every claim of "sent" or "done" is backed by a receipt that says what actually happened, including when what happened was nothing.

## What you'll learn

- The four kinds of artifacts I rely on, from a one-line log to a delivery receipt
- How a daily rollup turns scattered logs into one readable history
- What a run ledger records and why it lives in a database
- The honesty rule for receipts, with two failures that taught it
- How to tell "healthy" from "nobody checked"

## Four layers of artifacts

| Layer | What it records | Where it lives | Who reads it |
|---|---|---|---|
| Ship log | One line per material change, per project | Each project's `CHANGELOG.md` | The next session, me, the daily rollup |
| Master changelog | Every project's log, merged by day | One generated file | Me, any session that needs the big picture |
| Run ledger | Each automated run: what started it, inputs, outcome, cost | Postgres tables | Dashboards, watchdogs, audits |
| Receipt | Proof an outbound action happened, from the system that did it | A field on the action's row | The sender, the alarm, me when something didn't arrive |

Each layer answers a different question. The ship log answers "what changed in this project." The master answers "what happened this week, everywhere." The ledger answers "did the 7 AM job run, and what did it do." The receipt answers "did that message actually reach anyone."

## Layer 1: the ship log

After anything material (code written, config changed, bug fixed, migration run, decision made) the agent appends one line to the project's changelog:

```text
## 2026-06-09
- 13:34: Fulfillment drainer live. First real order exposed three bugs; all fixed.
- 09:16: Store switched to live orders for a test purchase.
```

It's append-only. Nothing gets edited after the fact. If something shipped broken, the log says it shipped, then says it was fixed. Three "fixed X" lines in a row for the same module tell you where to look next. A tidied log can't.

Pure reading and research don't need a line. If the agent wrote code or changed state, it logs. My instructions say it bluntly: skipping the log makes the work invisible to the next session and to me. The [files as state](/docs/fundamentals/files-as-state/) article has a tiny script you can copy for this.

## Layer 2: the daily rollup

Every night a job reads every project's changelog and regenerates one master changelog: newest day first, grouped by project. The header tells humans and agents not to edit it, because it's derived. If it looks wrong, you fix the source log and regenerate.

That one file is how a new session catches up on a week in a minute, and how I answer "what got built?" without trusting anyone's memory, including mine.

## Layer 3: the run ledger

Scheduled and autonomous work needs more structure than a Markdown line. In my system, workflow runs, task queues, approval queues and cost records live in Postgres, 250+ tables of durable state. A run row records what triggered it, when it started and ended, its outcome, and its cost.

Two rules make a ledger useful instead of decorative:

- **Liveness is work completed, not uptime.** A daemon that's "running" but hasn't finished a task in six hours is dead. Watch the ledger for completed work, not the process list for a PID.
- **Stale is not green.** My health check treats any status file older than twice its writer's schedule as UNKNOWN, and UNKNOWN is never grounds to say the system is healthy. A missing heartbeat looks exactly like a quiet day unless you make it look different.

## Layer 4: receipts

Agents in my system can draft anything and send nothing on their own. Outbound messages go into an outbox. A separate relay process holds the send credentials, drains the outbox, and writes the provider's receipt back onto the row. The contract is one line: no receipt, not sent.

The row moves through states: queued, sending, sent with a receipt attached, or failed and retried with backoff. Each row carries an idempotency key, so a retry after a crash can't send twice. After repeated failures a row is dead-lettered (held, never retried automatically) and an alarm fires. That alarm lives outside the relay on purpose. You never put the alarm for a system inside the system it's watching.

## The honesty rule

A receipt says what happened, not what was supposed to happen. Two failures taught me why that needs saying.

**Exit code 0 is not delivery.** In June 2026 an agent sent an important text through a script that drove the Messages app. The script exited 0. Three times. It had queued nothing. A macOS quirk with an idle conversation meant the send silently no-op'd. The fix worked only because the agent stopped trusting the exit code and checked the delivery record in the Messages database, which showed sent and delivered for exactly one copy. The script now opens the conversation before sending, and "sent" means the delivery record says so.

**"Sent, not confirmed" is a valid answer.** When my cockpit switches a chat pane to a different model, it sends a command to the session and watches for confirmation. Sometimes the confirmation doesn't come back in time. In September 2026 the UI was changed to say exactly that, "Sent, not confirmed," instead of rounding up to success or down to failure. The honest middle state is more useful than a confident wrong one.

So when you design a receipt, give it room for every true answer:

| State | Means |
|---|---|
| Delivered | The receiving system confirmed it |
| Sent, not confirmed | We handed it off; no confirmation yet |
| Failed | We know it didn't go, and why |
| Unknown | We can't tell. Treat as not delivered. |

## Designing artifacts that hold up

- **Timestamp everything.** Freshness checks need a time to compare against.
- **Predictable paths.** Dated names (`2026-10-05.md`) give you a free archive and make globbing trivial.
- **Numbers in fields, not prose.** A count buried in a sentence can't be charted or alarmed on.
- **Name the producer.** Which job, which run, which commit wrote this?
- **Derive, don't hand-maintain.** Anything you can generate from source, generate. My public [capabilities showcase](https://nerve-center-showcase.vercel.app) regenerates daily from the live system. Hand-kept numbers drift. At one point four different public counts of my agents were live at the same time, which is why the site now says "30+ agents in daily production, 100+ built over time" and leaves exact figures to the generator.

## What it buys you

Logging feels like overhead right up until the morning a scheduled job has been failing for two days and you need to know if it broke suddenly or slowly, and what changed near that time. With a ledger and a changelog you read two files and know in a minute. Without them you reconstruct it from memory and diffs, and often never find the cause.

> **Tip:** Start with the ship log and one receipt rule. Log every material change in one line, and never let any code you write call something "sent" on an exit code alone. Those two habits catch most of what goes wrong.

**Next:** [Cost and model choice](/docs/fundamentals/cost-and-model-choice/)
