---
title: "Where to go next: learning paths"
description: "Pick a path by goal: first week, one agent to many, how a production AI org runs, or a PM's path. Ordered reading lists."
section: start-here
order: 80
updated: 2026-10-05
sources: ["learn/tier-0/08-learning-path-map.mdx", "getting-started.mdx", "best-of.mdx"]
---

You can install Claude Code, sign in on the right billing, run a session, review an edit, and read what the agent is doing. That's the whole of Start here. This page is the map for everything after: four reading paths, each in order, picked by what you're trying to do.

These docs moved from docs.agenttree.army to jddavenport.com/docs in October 2026, and every article was rewritten for the move: current facts, current commands, and the parts that were wrong taken out. If you followed a link from the old site, you're in the right place.

## How the docs are organized

| Section | What it covers |
|---|---|
| Start here | Using Claude Code at all. You just finished it. |
| Fundamentals | The working parts: context, files as state, CLAUDE.md, tools, MCP, skills, hooks, settings, git, logging, cost. Ends with your first agent. |
| Patterns | What holds up when many agents run for months: delegation, isolation, orchestration, routing, memory, loops, shipping. |
| Inside the Nerve Center | How my production AI organization works today, piece by piece. |
| Safety and operations | What makes it safe to hand an AI system real authority. |
| Builds | Case studies of specific things I built, with repos where they're public. |
| Field notes | Opinions from running agents every day, labeled as opinions. |
| AI Core Skills | One in-demand AI skill at a time, with a kit you can use tonight. |
| Product management | Breaking into PM, the MBA path, and the AI product builder role. |
| Reference | Glossary, FAQ, open-source index. |

You don't have to finish a section before peeking ahead. The prerequisites are real, though: Patterns assumes you know what a tool, a hook and a CLAUDE.md are.

## Path 1: your first week with Claude Code

For: you just installed it and want to use it well on your own projects. Read in order, and do something small with each one before moving on.

1. [Sessions and context windows](/docs/fundamentals/sessions-and-context/)
2. [Files as state, not chat memory](/docs/fundamentals/files-as-state/)
3. [CLAUDE.md: teaching the agent your rules](/docs/fundamentals/claude-md/)
4. [Tools 101](/docs/fundamentals/tools/)
5. [Prompting Claude Code well](/docs/fundamentals/prompting-the-cli/)
6. [Git discipline for agents](/docs/fundamentals/git-for-agents/)
7. [settings.json and permissions config](/docs/fundamentals/settings-and-permissions/)
8. [Cost and model choice](/docs/fundamentals/cost-and-model-choice/)
9. [Build your first agent](/docs/fundamentals/build-your-first-agent/)

By the end you'll have a small agent that runs on a schedule, keeps its memory in a file, and follows one safety rule: it drafts, it doesn't send.

## Path 2: from one agent to many

For: you've got one useful agent and want several working together without stepping on each other. This is where most of the hard lessons live.

1. [MCP: giving the agent new senses](/docs/fundamentals/mcp/)
2. [Skills](/docs/fundamentals/skills/)
3. [Hooks: rules the model cannot forget](/docs/fundamentals/hooks/)
4. [Anatomy of an agent](/docs/patterns/anatomy-of-an-agent/)
5. [Write the spec before the code](/docs/patterns/specs-before-code/)
6. [Sub-agents and delegation](/docs/patterns/sub-agents-and-delegation/)
7. [Worktree isolation: the hard lesson](/docs/patterns/worktree-isolation/)
8. [Orchestration: delegate down, verify up](/docs/patterns/orchestration/)
9. [Model routing](/docs/patterns/model-routing/)
10. [Agent memory you own](/docs/patterns/agent-memory/)
11. [The loops doctrine](/docs/patterns/loops-doctrine/), then [Schedules as a heartbeat](/docs/patterns/heartbeats/) and [Watchers](/docs/patterns/watchers/)
12. [Root cause first](/docs/patterns/root-cause-first/)
13. [Ship to prod](/docs/patterns/ship-to-prod/)

If you only read three: worktree isolation, hooks, and ship to prod. Those three prevent most of the damage I've seen agents do.

## Path 3: how a production AI organization runs

For: you want to see the whole thing working. This is my own system, the Nerve Center: 30+ agents in daily production since April 2026, with the failures left in.

1. [The architecture in one page](/docs/nerve-center/architecture/)
2. [How the system got built](/docs/nerve-center/the-story/)
3. [The CEO agent](/docs/nerve-center/the-ceo-agent/) and [Domain agents](/docs/nerve-center/domain-agents/)
4. [The agent bus](/docs/nerve-center/the-agent-bus/)
5. [Fleets: parallel build agents](/docs/nerve-center/fleets/)
6. [The second brain](/docs/nerve-center/the-second-brain/) and [Open loops](/docs/nerve-center/open-loops/)
7. [The cockpit](/docs/nerve-center/the-cockpit/) and [The bridge](/docs/nerve-center/the-bridge/)
8. [One door out: the send gate](/docs/safety-and-operations/the-send-gate/)
9. [QA: user stories, Playwright and synthetic users](/docs/safety-and-operations/qa-and-synthetic-users/)
10. [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/)
11. [Watchdogs: liveness is work completed](/docs/safety-and-operations/watchdogs/)
12. [Durable state](/docs/safety-and-operations/durable-state/)

For the short version first, read the [production teardown](https://jddavenport.com/teardown) on my site. The system also publishes its own census daily on the [live capabilities page](https://nerve-center-showcase.vercel.app).

## Path 4: for PMs and leaders

For: you're deciding what AI means for your role or your team, and you'd rather learn from a running system than a slide.

1. [The AI product builder](/docs/product-management/the-ai-product-builder/)
2. [Agent evals](/docs/ai-core-skills/agent-evals/), the first AI Core Skill, and the one I'd learn first
3. [One door out: the send gate](/docs/safety-and-operations/the-send-gate/)
4. [The system documents itself](/docs/safety-and-operations/ground-truth/)
5. [Lessons from running agents every day](/docs/field-notes/lessons-from-running-agents/)
6. [Why agents will eat a lot of SaaS](/docs/field-notes/agents-vs-saas/)
7. [Building in public without fooling anyone](/docs/field-notes/building-in-public/)
8. [How to break into product management](/docs/product-management/how-to-break-into-pm/) and [The MBA path](/docs/product-management/the-mba-path-to-pm/), if you're making the move yourself

## Browsing instead

Not every reader wants a path. The [Builds](/docs/builds/agenttree-merch/) section is case studies you can read in any order, and [Open-source index](/docs/reference/open-source/) lists every public repo behind these docs. New term? The [Glossary](/docs/reference/glossary/) defines it.

## The honest expectation

This isn't a "10x overnight" track. Getting from one session to a system of agents you trust is real work, and the parts of my system that look impressive are also the parts that broke most often. The paths exist so that when you hit an advanced article, you have the ideas underneath it.

Take them in order. Build small things as you go. Come back here when you're not sure what's next.

**Next:** [Sessions and context windows](/docs/fundamentals/sessions-and-context/)
