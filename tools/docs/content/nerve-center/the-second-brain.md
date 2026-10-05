---
title: "The second brain: logs, rollups, journals"
description: "The system's memory of its own work: per-project logs, a daily rollup, a project registry and a compiled daily journal."
section: nerve-center
group: "Memory and context"
order: 100
updated: 2026-10-05
sources: ["learn/tier-3/a3-file-based-second-brain.mdx", "building-ai-os/arch-eod-compiler.mdx"]
---

A system with 30+ agents in daily production, many sessions in parallel and sessions that rotate when their context fills can only answer "what did we ship this week?" if every ship writes a line to a file. Chat history isn't a record. It rotates, it's split across parallel sessions, and the session that did the work is usually gone by the time you ask. So my system keeps a file-based record of its own work, and every agent is required to write to it.

This article is the structure of that record: what's hand-written, what's generated, and the one rule that keeps the generated parts honest.

## What you'll learn

- The five layers: project folders, the ship log, the master changelog, the project registry, the daily journal
- Which files a human writes and which a script writes
- Why generated files carry a "do not hand-edit" header
- What broke, and which layer I actually trust

## The problem, concretely

Three things happen in any multi-agent system, reliably:

1. An agent ships something material and nobody records it.
2. A session hits its context limit, rotates, and the new session has no idea what the old one did.
3. I ask "what shipped this week?" and the honest answer requires reading a dozen logs by hand.

The fix is boring convention. One command to log a ship. One generated file that rolls everything up. A rule that says the next session answers from the file, not from memory.

## The five layers

| Layer | What it is | Written by |
|---|---|---|
| Project folder | `README.md`, `WORKPLAN.md`, `CHANGELOG.md`, `LINKS.md` per project | Scaffolded by a script; README, WORKPLAN and LINKS edited by humans and agents |
| Ship log | One timestamped line appended to that project's `CHANGELOG.md` | A logging script, called by whoever shipped |
| Master changelog | Every project's log merged into one file, newest day first | Regenerated every morning. Never hand-edited |
| Project registry | One YAML entry per project: status, phase, next milestone, links, owner | Scaffold script on create; agents update status and phase |
| Daily journal | An activity log appended through the day, an end-of-day summary at night | Activity logger, session-end digests, a nightly compiler |

### The ship log

Every agent that changes system state calls one script when it's done:

```bash
clawd-log.sh inbox-triage "Fixed the retry loop that re-sent the same digest every tick"
clawd-log.sh inbox-triage "M3.2 shipped: change-gated digest" --completes M3.2
```

The first form appends a timestamped bullet under today's date heading in that project's changelog, creating the heading if it's missing. The second form also flips the matching `- [ ] M3.2` checkbox in the project's workplan to `- [x]`. One call logs the ship and closes the milestone. Ship equals flip plus log.

"Material" is defined in the instruction file every agent loads: a script written, a file edited, a migration run, a bug patched, a config changed, a decision made. Pure research and one-line trivial edits don't count. Everything else does. If an agent wrote code or changed state and didn't log it, the work is invisible to the next session, which is the same as not having done it.

### Project folders and the registry

A new project is one command, which creates the four files and the registry entry together:

```bash
clawd-new-project.sh inbox-triage --name "Inbox triage" --domain life-ops --status planning
```

The registry is what lets an agent answer "what's active right now?" without walking the disk. Each entry carries the project's status, current phase, next milestone, blockers and links. It's a cache of facts that live in the folders, which means it can drift; I'll come back to that.

There's a distinction the registry enforces: **a project has an end state and produces an artifact** (code, a deal, a doc, a launch). A chore doesn't. "Register the car" is a domain to-do, not a project. When in doubt, it's a to-do. Scaffolding a project for a chore is how you end up with a registry full of ghosts.

### The master changelog

A scheduled job rebuilds the master changelog every morning at 4:40 from every project's log. Its header says, in so many words:

```text
SOURCE OF TRUTH for "what did we do" / "what's been built." Newest day at top.
Auto-aggregated from every per-project log.
Do NOT hand-edit. Regenerate with daily-rollup.sh --master.
```

That file is the first thing a fresh session reads when I ask what happened. The instruction file says it plainly: answer from the changelog, not from chat history. A late-night run also saves a short daily rollup: what shipped today across all projects, what's due in the next 72 hours, and the top open loops.

### The daily journal

The journal is the most automatic layer and the least trustworthy, so I'll be specific about each piece:

- An activity logger appends a line whenever something notable happens (a merge, a deploy, a commit with a message).
- When a Claude Code session ends, a hook writes a digest of that session and drops a snippet for the journal. The next session can read the newest digest to pick up where the last one stopped.
- At 9:57 every night a compiler reads the day's journal, counts activities by category, writes an end-of-day summary and refreshes the dashboards. If it fails twice it files a ticket and pages me with the path to the failure artifact, instead of quietly writing nothing.

Until September an LLM pass also wrote a narrative version of each day, and a morning job pre-built the day's file. I paused both on September 13, along with a batch of other scheduled jobs. The activity log and the end-of-day summary still run.

## Generated vs hand-written

The rule is simple: **if a script writes it, nobody edits it by hand.** Fix the source and regenerate.

| File | Hand-edit? | If it's wrong |
|---|---|---|
| Project `README.md`, `WORKPLAN.md`, `LINKS.md` | Yes | Edit it |
| Project `CHANGELOG.md` | Append only, through the script | Log a correction as a new line |
| Master changelog | Never | Fix the project log, regenerate |
| Daily rollup and journal summary | Never | Fix the input, rerun |
| Project registry | Through the scaffold and status updates | Fix the entry, then find out why it drifted |

Why so strict? Because the next regeneration overwrites a hand edit, silently. You fix a typo in the master file at 3pm, the 4:40 job puts it back, and now two people remember different histories. Every generated file in my system says "do not hand-edit" in its header for exactly this reason.

## What broke

**The log is honor-system at the point of entry.** Nothing forces an agent to call the logging script. Agents built in a hurry skip it, and their work is invisible until someone notices. The only mitigation is the rule itself, repeated in every agent's instructions and in the prompt of every agent I spawn. It's not airtight, and I don't yet have a check that catches a skipped log. If you build this, that check is the first thing I'd add.

**Duplicates.** A ship logged under two project slugs shows up twice in the master changelog, by design. The journal is worse: on October 4 the same pull request appears five times in the activity log, at five different times of day. Honest read: the journal is noisy, and the master changelog is the layer I trust. If you build this, make the changelog the source of truth and treat the journal as a convenience.

**The registry drifts.** It's a hand-kept list of facts that live elsewhere, so it's always a little stale. In April a cleanup pass found dozens of ghost projects still listed as live and reclassified them as archived, ideas or superseded. The general fix for that class of bug is to render from what exists instead of from a list, which is its own article: [The system documents itself](/docs/safety-and-operations/ground-truth/).

## Copy this

You don't need the whole thing. Start with three pieces:

1. One `CHANGELOG.md` per project and one command that appends a timestamped line to it.
2. A generated rollup that merges them, with "do not hand-edit" in the header.
3. One line in your agent instructions: "After shipping anything material, log it. Answer 'what did we do' from the rollup, not from chat history."

That's an afternoon of work, and it turns "what happened last week?" from an archaeology project into one file read.

**Next:** [Memory: graph plus vectors plus keywords](/docs/nerve-center/memory-graph/)
