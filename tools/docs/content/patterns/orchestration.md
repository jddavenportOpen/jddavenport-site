---
title: "Orchestration: delegate down, verify up"
description: "One agent talks to the human, specialists do the work, and nothing reaches the human until it has been checked."
section: patterns
group: "Agents"
order: 50
updated: 2026-10-05
sources: ["learn/tier-2/04-orchestration.mdx", "articles/agent-orchestration.mdx", "tutorials/multi-agent-orchestration.mdx", "frameworks/agent-tree-architecture.mdx"]
---

One agent talks to the human. Specialists do the work. Every result gets checked on its way back up, and nothing reaches the human until it has been. That's orchestration: delegate down, verify up. Without the verify half, it's just a relay with extra steps.

One agent doing everything works until its context fills with five unrelated jobs and it starts confusing them. A tree of agents fixes that, and introduces a new way to fail: confident output from a context nobody checked.

## What you'll learn

- The shape of my agent tree today
- When the orchestrator acts directly and when it delegates
- The verification loop, and what "verified" means in practice
- Parallel work, and how agents talk to each other
- The anti-patterns that cost me the most

## My tree, October 2026

```text
me  (phone, cockpit, chat apps)
 |
 CEO agent        talks to me, routes work, holds the hard walls
 |
 +-- domain agents    long-lived sessions that own an area:
 |                    school, growth, AI Foundry, work, life-ops, a few private ones
 +-- specialists      researcher, QA agent, deck designers, ...
 +-- expert agents    routed by topic: course experts, a certification coach, ...
 +-- fleet workers    short-lived build agents, each in its own worktree
```

The CEO agent is my default point of contact. I can open any domain agent's session directly when I want to, but most requests start with the CEO. It decides what to handle, what to hand to a domain, and what to spin up. Domain agents are persistent Claude Code sessions that know their area deeply and nothing else. Specialists each do one job (see [Anatomy of an agent](/docs/patterns/anatomy-of-an-agent/)). Expert agents answer questions in a narrow field from a real knowledge base, and the CEO must call them instead of answering from its own head. Fleet workers exist for one task and are gone when it's done.

The [Inside the Nerve Center](/docs/nerve-center/the-ceo-agent/) section covers each of these in detail. This page is the pattern.

### What I dropped

My earliest charter drew this as a corporate org chart: a COO agent, a CTO agent, a CMO agent. None of those were ever built as code. The folders held personas and a few stray scripts, and nothing ran them. What actually runs is the tree above, organized by area of life and type of work, not by job title. If you're designing your own, organize by what each agent needs to know, not by what a company would call it.

## Act directly or delegate

The orchestrator isn't too important to do work. It should do small things itself, because spawning costs more than doing. Reading a file, checking a status, looking up a decision: just do it.

It delegates when a task needs many steps, reads a lot, or needs a specialist's tools. It runs pieces in parallel when they don't depend on each other. [Sub-agents and delegation](/docs/patterns/sub-agents-and-delegation/) has the full decision table and what goes in the prompt.

The one thing the orchestrator never delegates is the judgment at the end: is this good enough to show the human?

## The verification loop

```text
orchestrator delegates a task with a "done means" line
  -> worker returns a result and a claim ("tests pass")
  -> orchestrator checks the claim itself: runs the tests, opens the file, loads the URL
  -> fails?  send the failure back to the same worker, with the evidence
  -> passes? report it, with the receipt
```

Two details matter. Send the failure back to the same worker when you can, because it knows what it already tried and a fresh one will repeat the mistake. And report with a receipt (a test output, a commit, a URL), not an adjective.

Here's what "verified" means in my system for a code change:

1. **Adversarial review.** Three separate review agents with different instructions, one told to try to reject the change.
2. **CI gates.** QA, architecture rules, unit tests. Any production bug gets a test that reproduces the exact failure before the fix lands.
3. **The done gate.** The production URL must serve the exact commit that was merged, and a browser journey must pass against it. Inconclusive is not done.

Only then does the orchestrator tell me, and what it tells me is what to click. I review the product in production, not the diff. Agents review the pull requests. ([Ship to prod](/docs/patterns/ship-to-prod/) covers that flow.)

## Parallel work

When pieces are independent, run them at once and integrate at the end. A real one from June 7, 2026: I approved a batch of improvement proposals by voice. The CEO agent dispatched one build agent per proposal, each in its own git worktree with its own objective, plus a QA agent to exercise the results. Each worked on its own branch, so none of them could see, or break, the others' half-finished work. One message from me turned into a parallel wave of builds, and my only job was the approval at the start.

The unit never changes: one agent, one worktree, one goal, one branch. What scales is how many of those run at once, and that's bounded by memory, not ambition.

## How agents talk to each other

Any agent can ask any other by name. The first version was a synchronous call over the supervising service's stream. It had a bad failure mode: when a heavy agent took longer than the timeout, the call returned an empty string, which looked exactly like a real empty answer. The caller carried on with nothing.

The replacement is a durable bus. Every message is written to Postgres before delivery, a transient empty answer is retried, and a real failure dead-letters the message, alerts me, and raises an error instead of returning blank. One-way reports are drained by a resident daemon, and a daily probe sends a canary through the whole path. Honest caveat: durable here means it survives a crash, a dropped connection or a timeout, not a full outage of the machine. [The agent bus](/docs/nerve-center/the-agent-bus/) has the details.

## The hard walls

Orchestration decides who does the work. It doesn't decide what's allowed. Some actions need my yes no matter how confident any agent is: sending anything as me, moving money, and identity or IP decisions. Every outbound message goes through one chokepoint, [the send gate](/docs/safety-and-operations/the-send-gate/), and the orchestrator can't route around it, because whether something leaves the building was never the orchestrator's call.

## Anti-patterns

- **Over-delegation.** Spawning an agent to read one file. The overhead is bigger than the task.
- **Relaying.** Forwarding a worker's output without checking it. "The sub-agent said it worked" is a claim, not verification.
- **No timeout, or a timeout that only stops waiting.** In September 2026 timed-out calls left headless children running at top effort, delivering answers to nobody.
- **Context dumping.** Passing your memory file to a worker that needs three file paths. It's slower, and it leaks.
- **Silent model choice.** A lane with no model named inherits the most expensive one. See [Model routing](/docs/patterns/model-routing/).
- **Too many hands on one checkout.** Parallel agents without worktrees. See [Worktree isolation](/docs/patterns/worktree-isolation/).

## Start small

You don't need a tree to start. One orchestrating session, one specialist it calls, and a verification step you never skip will teach you most of this. Add domains when one context can't hold an area anymore. Add parallelism when you have independent work and the isolation to support it.

**Next:** [Model routing: the right model for the work](/docs/patterns/model-routing/)
