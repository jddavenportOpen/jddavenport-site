---
title: "Open loops: tracking every promise"
description: "A ledger of what the system promised to do, surfaced at every session start and checked by watchers where a machine can check it."
section: nerve-center
group: "Memory and context"
order: 140
updated: 2026-10-05
sources: ["learn/tier-3/b8-tracker.mdx"]
---

The changelog tells you what shipped. The open-loops ledger tells you what was promised. The gap between the two is where trust leaks out of an agent system, so every commitment my agents or I make becomes a row in one ledger, and it stays there until something closes it.

The ledger is the easy part. Keeping it precise, so the one loop that matters isn't buried under a hundred that don't, took most of the work.

## What you'll learn

- What a loop is and how loops get opened
- How loops reach me, and the rule for what agents do with them
- When a loop gets a watcher instead of a reminder
- Three precision failures and the fixes, which are the useful part

## What a loop is

A loop is a commitment with an owner. "I'll send the deck Friday." "Check the deploy after the merge." "Waiting on the vendor's reply." Each row carries:

| Field | Values |
|---|---|
| Status | open, in progress, blocked, completed, cancelled |
| Priority | P0 (drop everything) to P3 (best effort) |
| Owner | me, an agent, or an external party |
| Due | optional date |
| Provenance | who or what created it |

The command-line interface is small on purpose:

```bash
open_loops add "Send the pilot one-pager to Northwind" --priority p1 --owner jd --due 2026-10-09
open_loops list                      # P0 to P3, open and blocked
open_loops update 3f2a91c0 --status completed --notes "sent 10/08"
open_loops stale                     # no update in 3+ days
open_loops sla --emit                # ratcheted escalation (see below)
```

Since June 11, 2026, loops live in one table. Before that, nine different stores each held part of my backlog (a loops table, an assistant database, a couple of Markdown lists, a JSON file of recurring tasks) and they disagreed with each other. The migration moved every row into one unified backlog and checked that every row going in was accounted for coming out, merges included. The command-line verbs didn't change, so nothing that called them had to.

## How loops get opened

- **From conversations.** When an agent agrees to do something later, it opens a loop in the same breath. The rule in every agent's instructions: a promise that lives only in a chat reply is a dropped promise.
- **From meetings and voice notes.** Recorded conversations are transcribed and action items are extracted into the backlog.
- **From messages and email.** The assistant's inbox triage turns things people are waiting on into rows.
- **From the agents themselves.** A build agent that needs to verify a deploy tomorrow opens a loop instead of hoping someone remembers.

The ledger itself dates to April. The first automatic commitment extractor, built in late April, was a dedicated tracker agent that scanned my chat and sent mail for commitment-shaped language. A cheap regex threw out most messages before any model saw them, then a small model pulled the counterparty, due date and quote, with a confidence floor. I retired it in July; the inbox and voice-note pipelines, which already have the text, do the extraction now. The pre-filter is still worth stealing: a high-recall regex in front of a model call cuts the model's work to a fraction.

## How loops reach me

Two places today:

1. **Session start.** Every new session lists open loops and surfaces any P0 or P1 by name in its first line ("2 P0s pending: X, Y. Say go."). The rule is triage and surface only. A session doesn't start working a loop just because it saw one at boot. It acts on my word or on a machine trigger, never on its own boredom.
2. **The cockpit.** An open-loops page, and since early October a phone view that ranks what's blocked on me.

Until September a 7 a.m. standup message carried the top of the ledger too. I killed it on September 11 because I never read it. Then it kept arriving for ten more mornings, because a liveness check saw no standup receipt and helpfully re-sent it. Turning a job off now means one entry in one off-switch file, and a weekly check confirms nothing else can restart it.

## Watchers: when a machine can check it

Some loops are really conditions. "When the reply lands." "When the file appears." "When this page changes." A reminder to check is the wrong tool for those. A watcher is the right one:

```bash
watchers add --title "Vendor reply on the pilot" \
  --kind gmail_search --cadence 60 \
  --escalate "Northwind replied about the pilot"
```

A watcher checks on a cadence (in minutes), pings once when the condition fires, and then stops. Every watcher has a mandatory expiry (30 days by default), so nothing runs forever. A loop that's machine-checkable gets a paired watcher linked to it: the ledger holds the promise, the watcher does the checking.

One early lesson: direction-check email watches. My first watch for a vendor's reply fired on my own outbound email to the vendor, because I'd only searched for their address, not for mail *from* them.

## Three precision failures

### 1. The noisiest producer evicted the most urgent item

In August a ticket about clutter in the CEO agent's boot context led me to a worse bug. The boot context took the live P0 and P1 lines, oldest first, and cut the string at a fixed character budget. Of 60 lines, 12 survived. The other 48 were dropped silently, including a handful of urgent security chores. And a big share of the lines competing for that budget were auto-imported "Email from someone: subject" rows: mirrors of my inbox, not obligations anyone had stated.

The bug class, named: **a fixed-size budget filled in arrival order lets whichever producer is noisiest evict whichever item is most urgent.** Closing the email lane would have fixed that day and left the class intact. The fix made admission ranked (priority first, then authored obligations before inbox mirrors) and made omission loud: the context now ends with "N more live P0/P1 not shown" instead of nothing. When the intake classifier isn't sure, it calls the row authored, because wrongly hiding a real obligation is worse than one extra line.

### 2. Day 8 looked exactly like day 28

The only P0 in the ledger once sat open for 28 days with no progress. An escalation command existed, but it printed the identical warning on day 8 and day 28, in a digest next to hundreds of stale loops. Even when it ran, it looked like noise. The fix is an SLA with a ratchet:

| Priority | Breaches after | Then |
|---|---|---|
| P0 | 3 days | A new, louder escalation every 3 days it stays open |
| P1 | 7 days | Same ratchet at 7 |
| P2 | 21 days | Same ratchet at 21 |
| P3 | Never | Best effort |

Age is measured from creation, so touching a row doesn't reset the clock. A breached loop is re-surfaced at least weekly even if its level hasn't changed, and each new level is a distinct event, not the same line again.

Now the embarrassing half. The daily job that runs those checks had lost its crontab line in June. For two months it ran zero times, and nothing noticed an alerter that no scheduler called. A ledger check now lists alert scripts that are scheduled nowhere, and the weekly sweep pages when a new one appears. The original job still has no schedule as of October 2026; I found that while checking this article. Writing the watchdog is the easy part. Scheduling it, and proving it ran, is the part I keep relearning.

### 3. Extracted text dressed up as my to-dos

On October 4 I found that rows extracted automatically from messages, voice notes and scraped chat transcripts were landing straight into the "next up" state of my to-do list, presented as things I'd committed to. Hundreds of them. Each producer used a slightly different source name, and the gate that was supposed to hold them only knew some of the names. The fix was one provenance module that both the writers and the display use: an auto-captured row lands as "captured" and stays there until something triages it, and the new phone view labels where each item came from ("You said", "From Plaud", the voice recorder I use).

## Also: change-gate everything

The early ledger re-sent the same list to my phone every four hours, changed or not. It was my top noise complaint. The rule since: a loop alert carries a content hash and goes out only when the content changes. If your reminders don't change-gate, you'll stop reading them, and then the ledger is a list nobody reads.

## Copy this

1. One table, one CLI, one owner per row.
2. Open the loop in the same breath as the promise.
3. Conditions get watchers with expiries. Dates get one-shot reminders.
4. Rank what reaches the human, and say how much you left out.
5. Ratchet escalation, so time open makes a loop louder, not quieter. Then check that the job doing the ratcheting is actually scheduled.

**Next:** [The cockpit](/docs/nerve-center/the-cockpit/)
