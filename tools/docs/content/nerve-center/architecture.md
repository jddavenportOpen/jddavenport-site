---
title: "The architecture in one page"
description: "Operator, cockpit, bridge, Claude Code sessions, memory, Postgres, watchdogs and one send gate: the Nerve Center on one page."
section: nerve-center
group: "Overview"
order: 10
updated: 2026-10-05
sources: []
---

The Nerve Center is my production AI organization, and the whole thing fits in one sentence: a supervising service owns long-lived Claude Code sessions, a bus routes work between them and me, a shared memory gives them recall, Postgres holds durable state, and a watchdog layer assumes everything above it will eventually fail. It has run every day since April 10, 2026, with 30+ agents in daily production and 100+ built over time.

This page is the map. Every other article in this section zooms in on one box.

## The picture

```text
                 me: phone, desktop, chat apps
                              |
        +---------------------+----------------------+
        |                     |                      |
     cockpit             Telegram              iMessage
  (web + iPhone app)   (journaled transport)  (assistant channel)
        |                     |                      |
        +----------+----------+----------------------+
                   |
             the bridge: supervising service
             owns the long-lived Claude Code sessions as children
                   |
   +---------------+----------------+-------------------+
   |               |                |                   |
 CEO agent    domain agents    build workers       expert agents
 (talks to me) (one per area)  (worktree fleets)   (route by topic)
   |               |                |                   |
   +-------+-------+--------+-------+---------+---------+
           |                |                 |
      agent bus        memory layer       Postgres
   (durable messages)  (graph + vectors   (250+ tables:
                        + keyword index)   runs, ledgers,
                                           approval queues)
           |
     watchdog layer: liveness = work completed, not uptime
           |
     send gate: the only door to the outside world
```

## The pieces

| Piece | What it does | Read more |
|---|---|---|
| Operator surfaces | The cockpit in a browser or the iPhone app, Telegram, and an iMessage channel for the assistant | [The cockpit](/docs/nerve-center/the-cockpit/), [Talking to it from your phone](/docs/nerve-center/phone-and-messaging/) |
| The bridge | One Python service that starts, owns and streams the long-lived agent sessions | [The bridge](/docs/nerve-center/the-bridge/) |
| Sessions | Every agent is a Claude Code process. The CEO agent talks to me; domain agents own areas; workers build; experts answer | [The CEO agent](/docs/nerve-center/the-ceo-agent/) |
| The spine | A separate Python backend behind the cockpit: a durable workflow runner, queue drainers, and a relay outbox for outbound messages | [Durable state](/docs/safety-and-operations/durable-state/) |
| Agent bus | Agent-to-agent messages, persisted before delivery, dead-lettered loudly | [The agent bus](/docs/nerve-center/the-agent-bus/) |
| Memory | A graph store plus a vector store plus a keyword index, queried together | [Memory](/docs/nerve-center/memory-graph/) |
| Postgres | The system of record. If it matters, it lives in a table, not a context window | [Durable state](/docs/safety-and-operations/durable-state/) |
| Watchdogs | Detectors that ask "did you do work?" instead of "are you running?" | [Watchdogs](/docs/safety-and-operations/watchdogs/) |
| Send gate | Every outbound message passes one chokepoint and needs my yes | [The send gate](/docs/safety-and-operations/the-send-gate/) |

The stack under all of it is boring on purpose: Python daemons for orchestration, a TypeScript and Next.js cockpit on Vercel, Postgres on Supabase, a vector store and a graph store for memory, a small local model for rote jobs, and macOS launchd keeping it all alive on always-on hardware.

## The runtime is Claude Code

I didn't write an agent runtime. Every session in the diagram is a Claude Code process, and everything I built sits around it: files that tell it the rules, servers that give it tools, hooks that stop it, and a supervisor that keeps it alive. [How the system got built](/docs/nerve-center/the-story/) covers why.

That choice has a cost. When the CLI changes, everything changes. So the CLI has exactly one owner: a pipeline that tests a new release against the places my code depends on its behavior, swaps it in atomically, rolls back on its own if something breaks, and waits for my approval on a major version. No running session updates itself.

## One message, end to end

Say I text "what's due this week?" from Telegram while walking to class.

1. The Telegram transport writes the message to a journal on disk *before* it tells Telegram it got it. If the process dies one millisecond later, Telegram redelivers and the journal dedupes it.
2. A dispatcher hands it to the CEO agent as a headless Claude Code turn.
3. The CEO agent either answers from shared state or asks the school domain agent over the bus.
4. The answer goes back out. It counts as answered only when Telegram confirms the send. Receipts, or it didn't happen.
5. If the reply is long and voice mode is on, a spoken version follows as a voice note.

Nothing in that path leaves the system for a third party, so no gate fires. If I'd said "email my professor that I'll be late", the CEO agent would draft it, and the draft would wait at the send gate until I approved that exact text.

## Where the guardrails live

Every guardrail in the system lands in one of four places. This is the most useful idea on the page, so here it is plainly.

| Place | What it controls | Example |
|---|---|---|
| MCP servers | Capability. An agent can only do what a server exposes | A send-only reply server that can post to me and nothing else |
| PreToolUse hooks | Policy, checked before a command runs, no matter what the model believes | A raw restart of the bridge is blocked outright |
| Sub-agents | Blast radius. Fan-out work runs with its own tool grants | A build worker gets a worktree and repo access, not my inbox |
| The send gate | The outside world. One chokepoint for every outbound message | Approval tokens bound to a hash of the exact recipients, subject and body |

Honest read: the four places are not equally strong. In early September I audited the policy hook and found tens of thousands of "allow" decisions and zero blocks over the same stretch. It wasn't broken. Real sends happen inside Python code, where a hook that watches tool calls can't see them. The chokepoint in the code path had recorded hundreds of denials. The lesson: put enforcement where the action actually happens, then audit that it fires.

> **Note:** "Prose rules do not survive contact with autonomous agents. Machine enforcement does." Every rule that matters gets a hook, a gate or a detector. A sentence in a CLAUDE.md file is documentation.

## What is in motion

Two things are being built as of October 2026:

- Moving the database and cockpit hosting onto my own always-on hardware. In progress, not cut over.
- Nerve Center v7, a phone-first rebuild of the cockpit. Its first pages (today, work, school, what needs me) went live inside the current cockpit on October 3 and 4. The rest, including anything that sends, is on branches behind feature flags. The cockpit I actually live in is still Nerve Center v6.

## Five rules if you build one

From the [production teardown](https://jddavenport.com/teardown), which has the three failures behind them:

1. State outlives sessions. Anything that matters goes to a table or a file.
2. Sync intent, not state. The moment two writers exist, blob sync is a time machine.
3. Liveness is work completed. Uptime checks are blind to the wedged state.
4. Enforce with machines. Every rule gets a hook, a gate or a detector.
5. Gate the sends. One door out, with a freeze switch you can hit from your phone.

The system also publishes its own census. The [live capabilities page](https://nerve-center-showcase.vercel.app) regenerates from live state every day, so its numbers come from a generator, not from me typing them.

**Next:** [How the system got built](/docs/nerve-center/the-story/)
