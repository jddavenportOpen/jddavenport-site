---
title: "Files as state, not chat memory"
description: "Anything that must outlive a session goes in a file. The layout that lets an agent system remember its own work."
section: fundamentals
group: "How it works"
order: 20
updated: 2026-10-05
sources: ["learn/tier-1/02-files-as-state.mdx"]
---

Chat memory is not state. When a session ends, everything the agent "knew" from the conversation is gone, and compaction can drop it even sooner. If it matters tomorrow, it goes in a file. This is the one doctrine everything else in my system rests on, and it's the cheapest one to adopt: you need a folder and the discipline to write things down.

## The test

Pretend you kill the session right now. What's lost?

Whatever you just thought of is the stuff that wasn't written down. A research summary that only exists in a reply. A decision you made in turn 40. The note that the staging database is stale. A promise to check something on Friday. All of it is gone the moment the terminal closes.

Now ask the agent to write the research to `notes/research.md`, the decision to the changelog, and the Friday check to a ledger. Kill the session again. Nothing is lost. A new session reads three files and picks up where the old one stopped, even three days and two reboots later.

## What belongs in files

| Kind of state | Where it lives | Example |
|---|---|---|
| Rules and standing instructions | `CLAUDE.md` | "Run the tests before committing" |
| What the project is | `README.md` | One paragraph: goal, status, owner |
| What's planned | `WORKPLAN.md` | Milestones as a checklist |
| What shipped | `CHANGELOG.md` | Dated, append-only lines |
| Where things are | `LINKS.md` | Repo, prod URL, dashboards, docs |
| Ongoing facts about an area of life or work | A small YAML or Markdown state file per area | Current status, open issues, pending decisions |
| Research and notes | A notes folder | Findings with sources |
| Promises still owed | An open loops ledger | "Check the deploy Friday" |
| Things code queries | A database table | Workflow runs, approval queues, cost records |

What doesn't need a file: scratch work, intermediate reasoning, anything you won't care about once the task is done.

The last row matters once you have more than a few agents. Files are great for things people and agents read. Tables are better for things code queries, counts or locks. My system keeps runs, task ledgers, approval queues and cost records in Postgres, 250+ tables of it. The teardown puts it in one line: if it matters, it lives in a table, not in a context window.

## The project file set

Every project in my system gets the same four files:

```text
projects/<slug>/
  README.md      what this is, in one paragraph
  WORKPLAN.md    milestones as a checklist
  CHANGELOG.md   append-only, newest day first
  LINKS.md       repo, prod URL, dashboards
```

One command scaffolds a new project with all four. Another appends to the changelog. That second one is the habit that makes the whole thing work, so here's a minimal version you can copy:

```bash
#!/usr/bin/env bash
# ship-log: append a dated line to a project's CHANGELOG.md
# usage: ship-log <slug> "what shipped"
set -euo pipefail
slug="$1"; msg="$2"
file="$HOME/projects/$slug/CHANGELOG.md"
[ -f "$file" ] || { echo "no project: $slug" >&2; exit 1; }
today="## $(date +%F)"
line="- $(date +%H:%M): $msg"
if grep -qx "$today" "$file"; then
  # today's heading exists: add the line right under it
  awk -v h="$today" -v l="$line" '{print} $0==h{print l}' "$file" > "$file.tmp"
else
  # new day: put the heading above the newest existing day
  awk -v h="$today" -v l="$line" '
    /^## / && !done {print h; print l; print ""; done=1}
    {print}
    END {if (!done) {print ""; print h; print l}}' "$file" > "$file.tmp"
fi
mv "$file.tmp" "$file"
```

Newest day on top, newest line on top within the day. That's the whole tool.

My real version also takes a `--completes M3.2` flag that ticks the matching checkbox in `WORKPLAN.md`, so shipping a milestone and recording it are one command. The rule that goes with it lives in my instructions: after anything material (code written, config changed, bug fixed, decision made), log it. Pure reading and research don't need a line.

## The master changelog

Per-project logs are useful on their own. The aggregate is where the value is.

Every night a rollup job reads every project's `CHANGELOG.md` and writes one master changelog, newest day first, grouped by project. Its header says, in so many words, do not hand-edit this file, regenerate it. When a new session needs to know what happened across everything this week, it reads the top of one file. When I want to know what got built, I read the same file instead of scrolling through chats.

The master is a derived artifact. If it looks wrong, you fix the source log and regenerate. You never patch the derived copy, because a patched copy drifts from its source and then you have two truths.

## Append-only logs can't quietly rewrite history

The changelog is append-only by convention. Nothing gets edited after the fact, and that matters more than it sounds.

On June 9, 2026 my merch store took its first live order (my own test purchase). The log for that day says the fulfillment code shipped, and then it says the first real order exposed three bugs: it tried to expand Stripe fields that can't be expanded, it used the billing address instead of the shipping address, and it sent a confirm flag in the request body instead of the query string. Every one of those lines is still there.

If I'd been allowed to tidy the log, it would say "shipped fulfillment" and look clean. Instead it says what happened. Three "fixed X" lines in a row for the same module tell you that module needs a harder look. A cleaned-up log can't tell you that.

## Why this makes the system inspectable

The side effect I didn't expect: files make an agent system legible to a human. I can open a project folder and see what it is, what's planned, what shipped and where it lives, without asking an agent and without trusting its summary. Any tool can read a text file. Any agent can too.

It also changes what "memory" means. My system has a real memory layer (a graph plus a vector store, covered later in these docs), but the backbone is boring Markdown on disk. When in doubt, the file wins.

## Promises are state too

State gets lost to a sentence more often than to a crash: "I'll check on that after the deploy." It sounds like a commitment, but nothing will ever remind anyone, so it's dropped the moment it's said.

In my system, a future obligation has to become a machine loop the moment it's made: a scheduled job, a watcher that fires when a condition is met, or an entry in the open loops ledger that the morning standup surfaces. Prose is not a reminder. That idea gets its own article: [the loops doctrine](/docs/patterns/loops-doctrine/).

> **Tip:** Start small. One project folder, the four files, and a one-line log after each change. In a week you'll have something no chat history can give you: a record you trust.

**Next:** [CLAUDE.md: teaching the agent your rules](/docs/fundamentals/claude-md/)
