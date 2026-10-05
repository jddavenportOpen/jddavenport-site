---
title: "FAQ"
description: "Short answers to what people ask most: do I need to code, what it costs, is it safe, what agents can't do, and where to start."
section: reference
order: 20
updated: 2026-10-05
sources: ["faq.mdx"]
---

The questions people actually ask me about running agents, with short answers and a link to the longer one.

## Do I need to know how to code?

To start, no. To go far, it helps a lot.

Claude Code takes plain-English instructions and writes, runs and fixes the code itself, so you can get real work done on day one without writing a line. Where coding knowledge pays off is in knowing when a fix is a bandaid, and in writing the rules and checks that keep agents honest. My background is product management, not engineering. What I had to learn wasn't syntax. It was how to specify work, how to verify it, and where to put the guardrails.

Start with [What Claude Code is](/docs/start-here/what-is-claude-code/), work through the Start here section in order, then pick a route in [Where to go next: learning paths](/docs/start-here/learning-paths/).

## What does it cost to run?

Less than people fear for small things, more than people expect for heavy ones. Real numbers from my system:

| Kind of work | Rough cost |
|---|---|
| A rote heartbeat that formats a status report, on a cheaper model | pennies |
| A heavy build session | about $30 to $35 in API-equivalent cost (two examples: $34.67 over 201 model calls, $32.13 over 188) |
| A five-reviewer audit panel | roughly 300k tokens |

Most of my daily work runs on Claude subscription plans rather than per-token API billing, and I track usage as work volume at list-price equivalent so I can see where it goes. The biggest lever isn't the plan. It's matching the model and effort to what the work can break: small models for rote jobs, top models only for review and risky decisions. One audit found a single model doing over 90% of the work volume at top effort, which is the most expensive way to be lazy. See [Cost and model choice](/docs/fundamentals/cost-and-model-choice/). Current prices are at [claude.com/pricing](https://claude.com/pricing).

## Is it safe to let agents act for me?

Only with gates, and the gates have to be machines, not instructions.

My rule: the system can draft anything and send nothing without my yes. Every outbound message goes through one chokepoint, and approval is bound to the exact recipients and text, so a changed message needs a new approval. When I switched that gate on, a build check immediately found five email senders that had been going around it. Prose rules don't survive contact with autonomous agents. Machine enforcement does.

Money, sending as me, identity and anything irreversible always need a human. See [One door out: the send gate](/docs/safety-and-operations/the-send-gate/) and [Permissions and safety basics](/docs/start-here/permissions-and-safety/).

## What can't agents do?

Plenty, and the list is more useful than the hype:

- **They can't tell plausible from correct without a check.** A model answering a stats question without running the numbers produces a confident paragraph and a wrong answer. See [The analytics suite](/docs/builds/analytics-suite/).
- **They don't notice their own environment.** An agent once published a false "blocked by an upstream bug" caveat for 70 days because every test it ran was in the same misconfigured shell. See [Clawdling](/docs/builds/clawdling/).
- **They don't remember.** Anything not written to a file is gone when the session ends. See [Files as state](/docs/fundamentals/files-as-state/).
- **They don't own outcomes.** They'll report "done" on work that isn't live. That's why "done" in my system means production serves the merged commit and a real browser test passes. See [Ship to prod](/docs/patterns/ship-to-prod/).
- **They shouldn't do the trust parts.** Relationships, commitments, judgment calls with someone else's money. Agents draft. People decide.

## Is your system open source?

Parts of it. The full system runs my actual life and work, so it stays private. The pieces that generalize are public on GitHub under [jddavenportOpen](https://github.com/jddavenportOpen): the governance engine for autonomous fixes, the orchestration core, an open personal AI engine, eval starters, and more. The full list, each with the article that explains it, is the [open-source index](/docs/reference/open-source/).

For the shape of the private system, there's a public teardown at [jddavenport.com/teardown](https://jddavenport.com/teardown) and a capabilities page the system regenerates from live state every day at [nerve-center-showcase.vercel.app](https://nerve-center-showcase.vercel.app).

## Why Claude Code?

Because it's a harness, not a chat window. It gives the model a loop, tools, files, a permission system, hooks that can block an action, MCP for new capabilities, and sub-agents for delegation. Those are exactly the parts you need to run agents for months instead of minutes.

Every agent session in my system is a Claude Code process. I tried other setups early on, including OpenClaw in early 2026, and settled on Claude Code plus my own scaffolding: the harness does the hard parts well, and the parts I care about most (policy, durability, sends) I can enforce with hooks and code around it.

## Why does a five-minute fix take you thirty?

Because I fix the process, not the symptom. The bandaid is five minutes and it recurs. The root-cause fix is thirty and it doesn't: diagnose, fix whatever produced the bug, clean up the other instances, add a guard so it can't come back, then patch what I first noticed. See [Root cause first, never bandaids](/docs/patterns/root-cause-first/).

## How many agents do you run?

30+ agents in daily production, 100+ built over time, running every day since April 10, 2026. I don't quote an exact number in static pages, because the roster moves and a typed number goes stale. The capabilities page above shows the live count.

## Where do I start?

1. Install Claude Code and run a first session: [Install Claude Code](/docs/start-here/install-claude-code/).
2. Learn the working parts: [Fundamentals](/docs/fundamentals/sessions-and-context/).
3. Build one agent that does one real job for you: [Build your first agent](/docs/fundamentals/build-your-first-agent/).
4. Then read the patterns that hold up at scale, starting with [Anatomy of an agent](/docs/patterns/anatomy-of-an-agent/).

Pick a job you actually do every week. A toy agent teaches you the tool. A real one teaches you everything else.

## How do I reach you?

Email me@jddavenport.com, connect on [LinkedIn](https://www.linkedin.com/in/jd-davenport/), or book time at [book.jddavenport.com](https://book.jddavenport.com). If you find a mistake in these docs, email is fastest. See [About these docs](/docs/reference/about-these-docs/).

**Next:** [Open-source index](/docs/reference/open-source/)
