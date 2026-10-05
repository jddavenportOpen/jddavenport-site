---
title: "Anatomy of an agent"
description: "What a specialist agent is on disk: a definition, a package with a CLI, a registry row, state it doesn't own, and one clear scope."
section: patterns
group: "Agents"
order: 10
updated: 2026-10-05
sources: ["learn/tier-2/01-anatomy-of-an-agent.mdx"]
---

A specialist agent in my system is four things on disk: a definition file that tells Claude Code when to use it, a package with a command-line entry point, a registry row that says who it is and who may call it, and state that lives somewhere else. If you can't say what it does in one sentence, it isn't one agent yet.

"Agent" gets used for everything from a shell one-liner to a fleet. This page pins down the version that holds up when you run 30+ agents in daily production and have built 100+ over time: small, scoped, replaceable without touching its neighbors.

## What you'll learn

- The on-disk shape every specialist follows
- Why the model line in an agent definition is generated, never typed
- Why the command line is the agent's real API
- The inventory rule: look before you build

## The shape

Here's the deep-research agent, trimmed to what matters:

```text
.claude/agents/researcher.md       the definition Claude Code reads
agents/researcher/
  main.py                          entry point: importable and a CLI
  core/  tools/                    the research loop and its sources
  tests/                           tests live inside the package
  README.md
  CAPABILITY-CARD.md               what it can actually do, verified
registry row                       id, role, tier, who may call it
```

The directory name is the agent's identity. The registry slug, the message-bus target and the scheduled jobs all key off it. Rename the folder and you've changed its address everywhere, which is a good reason not to.

## The definition file

Claude Code reads custom sub-agents from Markdown files in `.claude/agents/`. Front matter on top, the agent's instructions below. A trimmed version of mine:

```markdown
---
name: researcher
description: Multi-depth deep research with an iterative knowledge-gap loop,
  a devil's-advocate pass and cited Markdown output. Delegate here for any
  web or deep research task instead of ad-hoc web search.
tools: Bash, Read, Grep, Glob, Write, Edit, WebSearch, WebFetch
model: claude-opus-5-5
---

You are the researcher agent. Run the Python implementation; never
fabricate sources. Push back if the query is underspecified.
```

The `description` does the routing. The main session reads it to decide whether to delegate, so write it like a job posting: what it's for, and what it replaces ("instead of ad-hoc web search").

Formal definition files are newer than you'd think. Before July 2026 none of my agents had one; they existed as folders and conventions. Writing them down is what made them callable by name.

### The model line is generated

When Opus 5 shipped on July 24, 2026, I made it the default for every chat session the same day. Three weeks later I found that about two-thirds of my agent definitions still said `model: sonnet`, a tier below the default I'd chosen. Nobody had swept the `model:` lines, because they were hand-typed literals with no owner.

The fix: a policy file maps each agent to a tier ("review", "build", "bulk"), a model registry maps each tier to one model id, and a script stamps the `model:` line into every definition from those two inputs. A weekly check fails if any definition disagrees. A new agent inherits the default tier without anyone remembering to set it.

> **Tip:** If more than one file says which model an agent uses, they will disagree. Pick one source and generate the rest.

## The CLI is the contract

Every specialist runs as `python3.12 -m agents.<name>`:

```bash
python3.12 -m agents.researcher.main "state of print-on-demand margins in 2026" --depth standard
```

That one entry point serves everyone: me at a terminal, a scheduled job, another agent over the message bus, a cockpit button. If the CLI works, every caller works. If it only works when a particular chat session drives it by hand, what you have is a prompt.

Depth flags are part of the contract too. The researcher's `shallow`, `standard` and `deep` presets dial iterations and how hard it verifies its own claims, so a caller picks a cost and rigor level without knowing the internals.

## The capability card answers "can it do X?" once

I kept asking the same questions about the researcher: does it have live X data, does it really use the Reddit API? Each time, a session re-investigated from scratch. Now the answer lives in `CAPABILITY-CARD.md`, verified against the code, with a date.

The useful part is what it admits. The card says Reddit is "PARTLY": the app-only search endpoint was returning 403, so the tool falls back to site search and gets lower-fidelity results. An honest card stops an agent from promising something the code can't deliver.

## State lives outside the package

An agent reads and writes state; it doesn't own it. Reports land in the vault, domain state lives in that domain's folder, durable records go to Postgres. Delete the package and recreate it, and nothing that mattered is lost.

This is [files as state](/docs/fundamentals/files-as-state/) applied one level down. The package is code. The record of what it did belongs to the system.

## Tests live with the package

`agents/researcher/tests/` sits next to the code it tests, so `pytest agents/researcher/` covers that agent's contract without running the whole estate. The researcher's tests read like a list of past failures: confidence fails closed, the curator fails closed, citations get fetched and checked. Each one is a bug that shipped once.

## Inventory before you build

The rule: before spawning a general-purpose agent for a task, check whether a specialist already does it.

```bash
bash scripts/list-agents.sh qa      # search the registry by keyword
ls agents/                          # see what's actually on disk
```

It exists because of April 30, 2026. A session spun up ad-hoc Playwright agents to QA a new feature while a full QA agent already sat on disk: PRD parsing, multi-browser runs, accessibility audits, visual baselines. The ad-hoc run's results never reached the QA agent's baseline store, so the next regression check had nothing to compare against.

The rule went into my instructions as non-negotiable. Then a June 1 audit found the script it told every agent to run didn't exist. For a month, the "non-negotiable" step pointed at nothing. Somebody wrote the script that day.

> **Note:** A rule that names a tool is only as real as the tool. When you write "always run X," check that X runs.

If nothing matches and the gap is real, write the gap into the registry first. The next session should never rediscover it.

## A new-agent checklist

1. One sentence of scope. If it needs "and," consider two agents.
2. A definition file with a description written for the router, not for you.
3. A package with a CLI entry point and tests inside it.
4. A registry row: id, role, tier, who may call it.
5. State written outside the package.
6. A capability card once anyone asks "can it do X?" twice.
7. The model tier set in policy, never typed into the definition.

**Next:** [Write the spec before the code](/docs/patterns/specs-before-code/)
