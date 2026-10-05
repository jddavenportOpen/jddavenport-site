---
title: "Agent memory you own"
description: "Three layers of memory in plain files, the read, write, synthesize habit, and when to graduate to a database."
section: patterns
group: "Agents"
order: 70
updated: 2026-10-05
sources: ["articles/memory-systems.mdx", "tutorials/agent-memory-system.mdx"]
---

Every session starts with amnesia. The model doesn't remember yesterday, your preferences, or the approach that already failed. Memory is files the agent reads at the start, writes as it goes, and tidies at the end. Plain Markdown gets you most of the way, and you own every byte of it.

This is a tutorial. By the end you'll have a three-layer memory in a folder, an instruction that makes the agent use it, and a clear sense of when you've outgrown files.

## What you'll learn

- The three layers: daily log, entity files, a short curated summary
- The habit that makes it work: read, write as you go, synthesize
- Two rules that keep memory trustworthy
- When to graduate to a vector and graph store

## Why not one big file

The obvious move is one giant memory file loaded every session. It breaks fast: the window fills, old context drowns new context, and the agent weighs a decision from March the same as one from this morning. You want different stores for different jobs, loaded selectively.

```text
memory/
  MEMORY.md                    layer 3: curated summary, always loaded
  entities/
    people/dana-reyes.md       layer 2: one file per person, project, company
    projects/harbor-pilot.md
  2026-10-04.md                layer 1: daily logs, append as you go
  2026-10-05.md
state/
  current.md                   the bridge between sessions
```

Every name in these examples is made up. Use your own.

## Step 1: the daily log

One file per day. Decisions, not just actions. "Decided X because Y" is useful in three weeks; "looked up prices" isn't.

```markdown
# 2026-10-05

## Harbor Coffee pilot
- Compared three POS integrations. Picked the one with a webhook API.
- **Decision:** start with webhooks, revisit polling only if they drop events.
- **Follow-up:** confirm webhook retry policy with their docs by 10-08.

## Preferences learned
- Prefers tables over prose for comparisons.
```

Rules for a good log:

- Write it during the session, not reconstructed at the end.
- Mark follow-ups explicitly so a later session can find them.
- Skip noise: routine reads, failed first attempts that taught nothing.
- Never edit an old day. Append a correction to today's file instead.

The log is your ground truth. It's cheap to keep and it's the only layer you can't rebuild from the others.

## Step 2: entity files

Logs are narrative. Entity files are state: one Markdown file per person, project or company, so the agent can open exactly the thing it needs.

The trick is splitting each file into two sections with different write rules:

```markdown
# Dana Reyes

## Status
- role: operations lead, Harbor Coffee
- prefers: async updates, no surprise calls
- last_contact: 2026-10-03

## Log
- 2026-09-28: kickoff call. Wants weekly written updates.
- 2026-10-03: approved the webhook approach.
```

**Status** holds current facts. Update them in place: when Dana's role changes, rewrite the line. **Log** holds real events, appended, never edited.

That split exists because I got it wrong. My CRM files once had machine-generated facts ("12 days since last touch", "draft ready to send") appended into the event timeline every time a job ran. The timelines filled with noise that looked like history. Now machine facts go to Status, only real human events go to Log, and a weekly check fails if status lines leak into a timeline.

When a fact changes, the old value doesn't need to be preserved in Status; the Log already holds the history of what happened and when. If you want an explicit trail, add a dated line to the Log: "2026-10-03: role changed from analyst to operations lead."

## Step 3: the curated summary

`MEMORY.md` is the only layer loaded every session, so it has a budget. Mine are short: who the agent works for, active projects in a line each, decisions not to re-litigate, and lessons that change future behavior.

```markdown
# Memory

## Active
- Harbor Coffee pilot: webhook integration, target 10-20. See entities/projects/harbor-pilot.md
- Docs rebuild: rewriting every article. See projects/docs/WORKPLAN.md

## Decisions (don't re-litigate)
- Webhooks over polling for POS events (2026-10-05)

## Lessons
- Verify a vendor's retry policy before trusting webhooks.
- Lead with the answer; detail after.
```

Point to detail; don't paste it. Rewrite this file weekly from the logs and entity files. It's a view of the other layers, not the source of truth.

Claude Code now ships its own version of this layer. Its auto memory keeps a `MEMORY.md` index plus one file per topic, and loads the first 200 lines or 25 KB of the index at the start of every conversation, whichever comes first ([docs](https://code.claude.com/docs/en/memory)). The design choice is the same one I landed on: a small index that points to detail, because anything past the budget never loads.

## Step 4: make the agent use it

Memory nobody reads is a diary. Put the habit in your CLAUDE.md, where every session sees it:

```markdown
## Memory

At session start:
1. Read state/current.md: what was I doing?
2. Read today's and yesterday's daily log.
3. Read memory/MEMORY.md.
4. List any follow-ups marked in the last 3 days.

During the session:
- Decision made or preference learned: append it to today's log now.
- A fact about a person or project changed: update its Status section.

At session end:
- Rewrite state/current.md: status, next step, what I'm waiting on.
- If something changes future behavior, add it to MEMORY.md.
```

`state/current.md` is the bridge. When a long session compacts its context or ends, this file is what the next one starts from:

```markdown
# Current state (2026-10-05 16:40)

Working on: Harbor pilot webhook handler, draft in src/webhooks/pos.ts
Waiting on: retry policy answer from vendor docs
Next: write the idempotency test before the handler
```

## Step 5: find things without reading everything

Search first, then read the one file that matters:

```bash
rg -n -i "webhook" memory/          # every mention, with file and line
rg -l "harbor" memory/entities/     # which entity files mention it
```

Plain text search over a few hundred files is fast and exact. It's also the right tool longer than people think.

## Two rules that keep memory trustworthy

**Memory stays out of sub-agents.** Your summary file holds personal context. A coding sub-agent needs three file paths, not your life. Pass the task, never the memory file. An agent can't leak what it never received.

**Know where every fact came from.** Anything that writes to memory automatically must record its source and must not trust text it didn't produce. In September 2026 a prompt hook in my system was minting fake "people" into the CRM and memory from text that had been injected into prompts, not from anyone I'd actually met. The fix was to strip injected regions before extracting anything, check provenance before writing, prune the bad entries, and add a weekly guard. A memory you can't trust is worse than none, because the agent believes it.

> **Warning:** Automated memory writers are an injection surface. Treat anything they read as untrusted input.

## When to graduate from files

Files carry you a long way. Graduate when you hit one of these:

- Keyword search returns too much and you need "things like this," not "things containing this word."
- Your questions are about relationships: who introduced whom, which projects share a person.
- Several agents write memory at once and you need one writer with readers behind it.

Mine runs three layers together as of October 2026: a graph database for relationships, a vector store for semantic search with embeddings from a small model running locally, and a keyword index of decisions. A query combines semantic hits with a one-hop walk of the graph. Two lessons from running it: a single-writer graph needs a read replica so readers don't block the nightly ingest, and an older embedded vector store had to be frozen when the server version took over, so nothing read stale data by accident. [Memory: graph plus vectors plus keywords](/docs/nerve-center/memory-graph/) has the details.

The files didn't go away when I added the database. The daily logs, project logs and person files are still the record. The database is an index over them.

## A starter kit

If you'd rather not start from a blank folder, [context-kit](https://github.com/jddavenportOpen/context-kit) is my public starter: four personal context templates (who you are, how you decide, how you write, your hard rules) and five Claude Code skills, including open loops and an end-of-session digest. It installs with one command and it's MIT licensed.

**Next:** [Schedules as a heartbeat](/docs/patterns/heartbeats/)
