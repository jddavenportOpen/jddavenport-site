---
title: "The system documents itself"
description: "Render from what exists, not from a hand-kept list. The org chart lesson, the daily capabilities page, and the counting rule."
section: safety-and-operations
group: "Guardrails"
order: 40
updated: 2026-10-05
sources: ["learn/tier-3/d6-org-chart-ground-truth.mdx"]
---

Anything a human has to remember to update will eventually lie. My org chart did, my registry did, and for a while my own public numbers disagreed with each other on the same day. The fix every time was the same: render from what exists, generate every derived view from one source, and let only generators state exact numbers.

## What you'll learn

- How a hand-kept org chart drifted, and what replaced it
- Why "read from disk" is harder than it sounds when the UI runs in the cloud
- How the public capabilities page builds itself, and the loop bug it had
- The counting rule I use for every public number

## The org chart that lied

The cockpit's first org chart read a hand-curated YAML file: a list of agents, their domains, their connections. Add an agent, update the list. Rename one, update the list. Nobody did. By late May the chart showed agents that had been archived, missed ones that had been added, and disagreed with itself about how many MCP servers existed.

The May 31 audit put numbers on it: the registry oversold the real roster by about two to one, with a pile of named "specialists" that had no code behind them. Pages in the same app reported different counts for the same thing. In the audit's phrase, the product disagreed with itself.

## Render from what exists

The obvious fix is "read the filesystem." The catch: the cockpit runs on Vercel, and Vercel can't read my Mac. The first version that tried reading files directly worked in local development and, in production, quietly degraded to a handful of nodes built from heartbeats, with a "no such file or directory" error nobody saw.

What works:

1. **A sync job on the Mac** walks the real sources every seven minutes (the MCP server config, the domain folders, the project registry, the agent roster) and upserts them into tables, pruning rows that no longer exist.
2. **The cockpit reads the tables.** If a source fails, the response records the error and returns what it can, instead of failing the whole page.
3. **A weekly drift guard** compares every view against the source. The canonical roster against the code directories, the scheduled jobs and the service definitions. The generated registries against a fresh regeneration. The cockpit's table slug for slug. And the live production org endpoint, signed in as a QA identity, to check that the number a user actually sees matches the source.

One honest exception. The agent roster is still one file a human edits, because "what counts as an agent" is a decision, not a fact on disk. What changed is that it's *one* file. Every other registry, the cockpit roster and the generated agent definitions come from it, and the drift guard fails if any of them disagree.

That last part exists because of a real miss. After a new model shipped in late July and the registry was repointed, most agent definitions stayed on the old model for three weeks, because the `model:` line in each definition file was typed by hand. Now that line is stamped by a script from a policy file, and the weekly guard fails if anyone hand-edits it.

> **Note:** A guard that can't see is a failure, not a pass. If the drift guard's sign-in has expired or a fetch fails, it pages. "Checked zero things, found zero problems" is the most dangerous green in any monitoring system.

## The capabilities page builds itself

The public [capabilities page](https://nerve-center-showcase.vercel.app) is the same idea pointed outward. A generator introspects live state and writes two files: a machine-readable JSON feed and a self-contained HTML page. Its contract:

- **Every count and every name is computed from live state on every run.** The only hand-written inputs are a short list of dated milestones and the template prose.
- **Allowlist first.** Only named fields are ever emitted. A new internal field never leaks by accident.
- **Idempotent.** Same state, byte-identical output, so a content hash can tell "nothing changed" from "something changed."
- **Leak scan, fail closed.** Before publish, a scanner checks the output for secrets, personal data and internal topology. Any hit blocks the publish and alerts me.

It regenerates daily, and also whenever a project logs a ship. This site's home page reads the same feed through a small server-side endpoint with its own allowlist, so the stat strip and telemetry numbers on [jddavenport.com](https://jddavenport.com/) are generated, not typed.

### The loop that re-armed itself

The near-real-time trigger was a file watcher: logging a ship touches a flag file, and the watcher fires the regeneration. The regeneration then deleted the flag. The watcher counted the delete as a change. So from July until September 27, every run re-armed the next one ten minutes later. In one 30-day window, 519 of 811 deploys started exactly one throttle interval after the previous one. Nobody noticed, because each run was individually correct.

Two fixes: the script never deletes the flag (only the watcher reads it), and a deploy policy now separates kinds of change. A changed capability deploys immediately. A change only in the counters that move on every logged ship deploys at most once every 20 hours.

## The counting rule

At one point four different public agent counts for my system were live at once: one on this site, one baked into the link-preview image, one on the capabilities page, and one in a case study. The highest was about double the lowest. A reader who sees two of them in one sitting discounts all of them, on pages whose whole argument is real numbers.

The rule now splits by provenance:

| Where the number appears | What it says |
|---|---|
| Static copy (prose, meta descriptions, the link-preview image, this docs site) | A durable floor: **30+ agents in daily production, 100+ built over time** |
| Generated surfaces (the home page stat strip and telemetry, the capabilities page) | Exact numbers, produced by a generator from live state, with their date |

The link-preview image is the strictest case. Every platform that ever rendered a link caches its card, so a number baked there outlives any correction. Mine kept showing a stale count after every page had been fixed.

The same thinking applies to any metric. The May audit found a sync dashboard proudly reporting every run "succeeded." Succeeded meant "didn't throw an exception," not "wrote rows," and several runs had been silent no-ops. Measure the output, not the absence of an error.

## Copy this

1. Pick one canonical source per fact. Generate every other view from it.
2. If the UI can't read the source directly, sync it into tables on a short schedule and prune what disappeared.
3. Run a drift check against the view the user actually sees, and page when the check is blind.
4. Let generators state exact numbers. Let prose state floors.

**Next:** [Watchdogs: liveness is work completed](/docs/safety-and-operations/watchdogs/)
