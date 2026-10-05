---
title: "The loops doctrine"
description: "Every future obligation becomes a machine loop with an off switch: cron, watcher, session loop or a dated one-shot."
section: patterns
group: "Loops and schedules"
order: 90
updated: 2026-10-05
sources: ["learn/tier-2/06-the-loops-doctrine.mdx"]
---

"I'll check back on that" is a promise a chat reply can't keep. The session ends, the context rotates, and nobody checks back. So the rule in my system is simple: the moment an agent creates a future obligation, it wires that obligation to a machine loop. A promise that lives only in prose is a dropped promise.

I made this a standing rule on June 7, 2026, after one too many "I'll keep an eye on it" replies that nobody kept an eye on. My words to the system: "I want loops automatically used in our system where it makes sense without me needing to ask."

## What you'll learn

- The four loop shapes and how to pick one
- The two guardrails that keep loops from becoming noise
- Why an "off" has to stick, and why a pause must never silence its own monitor

## Four shapes, four primitives

Every future obligation has a shape. Match the shape and the primitive picks itself.

| Shape of the obligation | Primitive | Examples |
|---|---|---|
| Runs on a fixed cadence, forever | **cron** (or a LaunchAgent) | Daily backup, nightly sync, weekly review |
| Wait until a condition is true, then act once | **watcher** | "When the vendor replies", "when the export file appears", "when this URL returns 200" |
| In-flight work in this session | **session loop** | Waiting on CI, a deploy, a long build |
| Happens on a specific date | **durable one-shot** | "Remind me on the 13th", "the API token expires in 30 days" |

In Claude Code terms: a session loop is `/loop` or a background task the session watches. A durable one-shot can be a Desktop scheduled task, a routine, or a watcher whose condition is the date. Cron and LaunchAgents are covered in [Schedules as a heartbeat](/docs/patterns/heartbeats/). Watchers get [their own article](/docs/patterns/watchers/) next.

The most common mistake is using the wrong one. "Check every four hours whether anything changed and tell me" is not a cron job. It's a watcher with a change condition. A cron job runs whether or not anything changed, which is exactly the problem.

## The habit

When you finish a piece of work and there's a "we should follow up on..." at the end, stop and ask what shape it is:

1. Needs to happen on a schedule? Add the schedule.
2. Needs to fire when something changes? Register a watcher.
3. Needs to happen on a date? Register a dated one-shot.
4. Only matters for this session? A session loop is fine, and it dies with the session.

That pause takes a minute. It's the whole doctrine.

The same habit has to reach agents you spawn. Any agent that can create pending work either registers the loop itself or prints the exact registration command in its report. If the doctrine isn't in the agent's prompt, the agent will write "I'll monitor this" and mean nothing by it.

## Guardrail 1: every loop names its off condition

A loop with no end is noise waiting to happen. So every loop says when it stops:

| Primitive | Off condition |
|---|---|
| Watcher | Fires once, or hits its expiry. My default expiry is 30 days, and a watcher can't be set past a year. |
| Dated one-shot | Fires once. |
| Session loop | The session ends. (Claude Code's `/loop` tasks also expire after seven days.) |
| Cron | An explicit owner who decides when it dies. |

The 30-day default exists because most "wait for X" conditions either resolve or stop mattering within a month. If yours genuinely needs longer, set it on purpose.

Cron is the dangerous one because it has no natural end. In June 2026 I found a cron line that had been failing every hour with `ModuleNotFoundError`, pointing at a module that no longer existed. Nobody noticed because nobody read its log. Delete the schedule in the same change that deletes the code, and if you can, run a daily check that every scheduled job still points at something real. Mine started the same day.

## Guardrail 2: alerts are change-gated

A loop that pings you with the same content twice is broken. My worst offender was the open-loops digest that re-sent the same unchanged list six times a day. Within a week I was skimming past it, which means it would have hidden the one day the list actually changed.

The fix is mechanical: hash what you're about to send, compare it with what you sent last, and stay quiet on a match. Or make the loop trigger-once, which is what a watcher is.

A related trap: check which direction the signal is coming from. My first "wait for the vendor's reply" watch fired on its very first sweep, on my own outgoing email, because the search matched the thread and I had written the first message. Pin the sender (`from:vendor.com`).

## Off has to stick

Turning a loop off is also a promise, and it breaks the same way. On September 11, 2026 I found an autonomous job running that I had switched off. A resume script, written to restart jobs paused during a usage crunch, had dutifully restarted it that morning. It didn't know the difference between "paused by a script" and "killed by me."

The fix was a kill ledger. Every path that can re-arm a job now asks one question first: did a human kill this? As of late September, nine separate re-arm paths consult it, and a weekly check reports any kill that came back to life.

If you build anything that restarts things, give it a way to know what it must never restart.

## The healer-exempt rule

One more trap, and it's subtle. In July 2026 I paused an area of the system to audit a failure. The pause gated everything in that package, including a monitor that watched for an expiring login token. So the pause meant to investigate a problem also silenced the alarm that would have reported the next one.

The rule since July 21: a pause must never gate its own monitor or healer. Monitors are read-only and alert-only, and they always run. If a monitor lives inside something that can be paused, move the monitor somewhere that can't be, rather than carving out an exception in the pause logic.

## Pair promises with checks

Some obligations are human promises ("I'll send the deck Friday"). Some are conditions a machine can check ("the reply arrived"). I keep a ledger of open promises, covered in [Open loops](/docs/nerve-center/open-loops/), and any entry that's machine-checkable gets a watcher linked to it. The ledger holds the promise. The watcher does the checking, and when it fires it notes the result on the ledger entry.

Not everything is checkable. "Decide which framework to use" is a judgment. "The token expires on the 14th" is a date. Telling those apart is most of the skill.

## The receipt that sold me

My school's learning system caps API tokens at 90 days. One expired in June 2026 and nobody noticed for 12 weeks, because nothing checked it. Everything downstream just quietly stopped seeing coursework. A dated one-shot set when the token was minted would have caught it on day 89. Now a weekly job renews the token and a health check pages if renewal ever stops.

Every silent failure I've had looks like that: an obligation everyone assumed someone else was watching.

**Next:** [Watchers: condition until it fires](/docs/patterns/watchers/)
