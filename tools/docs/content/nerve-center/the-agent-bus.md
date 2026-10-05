---
title: "The agent bus: how agents talk"
description: "From a synchronous ask that could silently return nothing to a durable bus that persists, retries and dead-letters loudly."
section: nerve-center
group: "Orchestration"
order: 50
updated: 2026-10-05
sources: ["learn/tier-3/b4-ask-agent.mdx"]
---

Agents need to ask each other things. My first way of doing that could lie by saying nothing: a timeout came back as an empty string, and an empty string looks exactly like an agent that had nothing to say. The durable bus fixed that by writing every message to Postgres before delivering it, so a message can succeed, fail loudly, or sit visibly pending. It can't vanish.

## Version one: ask_agent

The first interface was one function. Name a target, ask a question, get text back.

```python
from agents.shared.ask_agent import ask

answer = ask("school", "Anything due in the next 48 hours?")
answer = ask("ceo", "Review this plan and tell me what's missing.")
```

Under the hood it opened a fresh context for the target, loaded that agent's identity and state files, ran one turn through the bridge, and streamed the answer back. It deliberately did *not* share the target's live session history. Two agents reading and writing one session at once is the same race that forced worktree isolation for git.

The flaw was in the transport. The call was synchronous and kept no record. If the stream ended early (a timeout, a bridge restart, a busy session), it returned `""`. On July 11, two of those empties in a row looked like a dead bus. The bus wasn't dead. Complex questions to heavy agents were running past the timeout, and the caller couldn't tell "no answer" from "the agent said nothing."

The quick fixes landed the same day: a longer default timeout (240 seconds) and a CLI that fails loud on an empty answer. The real fix was a different transport.

## Version two: the durable bus

The pattern was fine. The transport had no durability guarantee. So the bus moved onto the Postgres database the system already ran on.

| Primitive | Use it for | What it guarantees |
|---|---|---|
| `ask_durable(target, question)` | A question you block on | Persisted before delivery; a transient empty is retried; a real failure is dead-lettered, alerted and *raised*. It never returns `""` |
| `post_message(target, text)` | A one-way send | The row exists before the call returns; you get a correlation id |
| `post_artifact(target, kind=..., title=..., body=...)` | Reports, completions, escalations | A structured envelope the drain can route by kind |

Every row moves through one status machine:

```text
pending -> processing -> done
                      -> failed (retryable)
                      -> dead   (dead-lettered, alert sent)
```

Rule of thumb I give every agent: `ask_durable` for anything you'd be upset to lose, `post_artifact` for durable one-way reports. Plain `ask` is fine for a throwaway question where an empty answer costs nothing.

## The drain: who actually delivers

Producers were built first. For about a week, nothing consumed the general inbox, so rows sat pending forever. That's the classic gap: everyone builds the send side.

The drain is a resident daemon that wakes every 30 seconds and works the inbox:

- **It checks the target is real** before anything else. An unknown name dead-letters immediately and alerts me. It never makes up context for an agent that doesn't exist.
- **It routes by kind.** Interactive kinds (tasks, escalations) go to the target's live session if one is open, otherwise into one batched turn per target. Informational kinds (reports, receipts) go to a live session if there is one, otherwise they wait and flush as one batched turn per target per day. Never one spawn per message.
- **Pending can't mean forever.** Three real delivery failures on a row, or a row older than a day, means dead plus an alert. A separate alerter pages me if a task or escalation sits pending more than two hours, which covers the case where the drain itself is dead.

When it went live on July 17, a message path that had been a black hole a day earlier delivered a worker's report to a live session in about 45 seconds.

## Three bugs that shaped the drain

**An outage recorded as a delivery.** When a batched turn hit an account or quota wall, the turn's output was the error text, and the drain recorded that text as the answer. Over 72 hours in August, ten rows were marked "delivered" with an outage message as their receipt. Now the answer is checked first: an error-shaped or empty reply is a delivery failure, not a receipt.

**A rate limit that burned every retry.** In early September the bridge returned "rate limit, retry in about 17 minutes" to several targets at once. At a 30-second tick, three strikes went by in 90 seconds and the rows dead-lettered. Now a transient rail failure is recorded as a deferral and doesn't use up a strike. Deferrals stay visible to the stale-row reaper, so a rail that never comes back still dies loud.

**A child that kept running.** A September audit found that when the synchronous call timed out, it stopped listening but never killed the headless Claude Code process it had started. The orphan kept running at top effort after its caller had given up, and three timeouts meant a dead letter *and* a still-running orphan. Now a timed-out call tells the bridge to kill the turn, and headless spawns go through a shared helper that kills the whole process group. A lint in the merge gate refuses new code that skips it. That class of bug also fed a kernel-panic loop, covered in [Fleets](/docs/nerve-center/fleets/).

## Holds, bounces and the probe

- **Off domains hold, they don't drop.** If I've switched a domain off, a blocking question to it fails fast. A one-way message is persisted but held, untouched by the drain, until the domain is back on.
- **No rail means an instant bounce.** If a name resolves but nothing can receive under it, the message dead-letters on the first attempt and a bounce goes back to the sender, so nobody waits on silence.
- **A round-trip probe checks the whole path.** On a schedule, a canary is posted and the probe asserts it reaches `done` with its nonce echoed back within five minutes. It started daily and runs weekly now.

## The honest caveat

"Durable" here means the message survives a process crash, a bridge blip or a timeout. It does *not* mean it survives the whole machine being offline. Rows already in Postgres are safe, but nothing on the box produces or drains while it's down. A local spool that would cover a full outage is planned, not built.

## Build your own

You don't need my stack to get this right. The minimum:

1. Write the message to durable storage before you try to deliver it.
2. Give every message a status, and make "dead" a real status with an alert attached.
3. Never let a timeout return a value that looks like a real answer. Raise instead.
4. Check the receipt. An error message is not an answer.
5. Kill what you spawn when you stop waiting for it.

[clawd-agent-os](https://github.com/jddavenportOpen/clawd-agent-os) has a public version of this bus (`ask_durable`, `post_message`) alongside the fleet and drainer patterns. [orchestra-agents](https://github.com/jddavenportOpen/orchestra-agents) has a self-contained, bring-your-own-key bus with the same status machine on SQLite.

**Next:** [Fleets: parallel build agents](/docs/nerve-center/fleets/)
