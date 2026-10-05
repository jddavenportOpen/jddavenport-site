---
title: "Model routing: the right model for the work"
description: "Route by work type and blast radius, not habit. Model tiers, effort as a second dial, and when to add an off-plan model."
section: patterns
group: "Agents"
order: 60
updated: 2026-10-05
sources: ["frameworks/llm-routing-strategy.mdx", "articles/smart-model-routing.mdx", "articles/kimi-k2-cost-optimization.mdx"]
---

Early on, every task went to the biggest model: research, commit messages, checking whether a file exists. That's the most expensive way to be lazy. Routing fixes it. Pick the model by what the work can break, not by habit, and write the choice down so silence doesn't default to the top tier.

This page is the framework. [Model routing in practice](/docs/nerve-center/model-routing-in-practice/) is the story of how my own routing got corrected, one incident at a time.

## What you'll learn

- The tiers I route between, and what each one is for
- Effort as a second dial, separate from the model
- The blast-radius rule for choosing both
- The rules that keep routing from rotting
- When to add a model from outside your main plan

## Two dials, not one

Every call has a model and an effort level. Claude Code exposes effort as `low`, `medium`, `high`, `xhigh` and `max`, per session or per sub-agent. A smaller model at high effort and a bigger model at low effort are different trade-offs, and most of the waste I've found came from turning both dials to the top by default.

## The tiers

Here's what I route between as of October 2026. Model names change every few months; the tier names don't.

| Tier | What runs there today | Use it for |
|---|---|---|
| Deepest | Fable 5.1 | Only when I explicitly ask for it |
| Review and chat | Opus 5.5 | My chat sessions, planning, code review, judges |
| Build | Sonnet 5 | Building code, most autonomous work |
| Bulk | Haiku 4.5 | Rote classification, formatting, cheap summaries |
| Offload | Kimi, on a separate flat subscription | Background fleet work kept off the main plans |
| Local | A small open model on my own hardware | Bulk extraction and embeddings, under a memory budget |

Two of those rows are worth explaining.

**The deepest tier is explicit-only.** Nothing routes there automatically. It's one deliberate click away when a hard problem earns it, and that's the only way in. The reason is in the in-practice article: a default that points at your most expensive model will be followed long after you stop meaning it.

**Local is capped by memory, not by ambition.** A local model is free per call and expensive in RAM. In September 2026 a 12 GB local model, loaded many times a day alongside browser automation, helped drive a run of kernel panics on my main machine. Heavy local models are now refused there; light ones run under a memory budget.

## Tier by blast radius

The rule that decides both dials: what's the worst thing this work can break?

| If the work touches | Model | Effort | Reviewer |
|---|---|---|---|
| Autonomy, safety gates, credentials, anything that moves money or sends externally, anything irreversible, a shared rail every producer rides | Review tier | Top | Independent reviewer required |
| Normal engineering: a new module, a schema change, a live loop's behavior | Build tier | High | Usually one |
| Mechanical edits, config, cadence changes, test-only work | Build or bulk | Medium | Rarely |
| Doc fixes, comment fixes, receipt text | Bulk or build | Low or medium | None; the builder checks its own work |

I don't run a budget cap, so this is about waste, not a ceiling. A top-tier, top-effort review of a typo fix buys nothing, and when everything gets the top tier you can no longer tell which work actually needed it. Honest read: uniform maximum effort isn't thoroughness. It's unmetered work volume.

Rote heartbeats cost pennies on a small model. A heavy build session runs about $30 to $35 in API-equivalent terms. Those numbers are the whole argument for routing: roughly three orders of magnitude between a heartbeat and a heavy build session. [Cost and model choice](/docs/fundamentals/cost-and-model-choice/) covers how to read those numbers honestly.

## Rules that keep routing honest

**One registry names one model per tier.** Code asks for a tier ("build"), never a model id. A single file maps tiers to ids, and everything else (agent definitions, environment files, the cockpit's model picker) is generated from it. I learned this when "sonnet" meant three different models in three different places at once.

**Name the tier on every lane.** A sub-agent or workflow lane with no model named inherits the parent's, which is usually the most expensive thing running. A deliberate choice of the top tier is fine. Silence is the bug.

**Route by task, not by agent.** The same agent might need a small model for a lookup and a big one for a judgment call. Assigning one model per agent forever is too rigid.

**Running sessions keep the model they were born with.** A resumed Claude Code session restores its original model, so changing your default doesn't reach anything already running. If you change a default, sweep the live sessions too, or wait for them to end.

**Benchmark on your own tasks.** Public leaderboards don't know your workload. My model adoption gate runs a small set of my own deterministically-scored tasks, candidate against incumbent, with no model judging another model.

> **Tip:** Never hardcode a model id in agent code. The id will be retired before the code is.

## Adding a model from outside your plan

Sometimes the right move is a different provider for a slice of work. Here's how that went for me, as a dated example rather than a recommendation.

- **April 2026:** I looked at Kimi as a cheaper option for structured coding and analysis work.
- **July 3, 2026:** it went live as the offload tier. Fleet tasks can opt in, and that work runs on a flat Kimi subscription instead of my main plans. It was verified end to end through the Claude Code CLI pointed at Kimi's endpoint.
- **July 16 to 17:** I flipped the tier to a newer Kimi model before its evaluation finished. The rule I'd agreed in advance said revert if it lost. On my own benchmark the older model passed 17 of 19 tasks and the newer one 14 of 19, with no task the newer one won alone. The tier went back the next day. The newer model stays selectable by hand.

What to copy from that:

1. Put the new model behind a tier, so adopting or dropping it is one line.
2. Make it opt-in per task before it's anyone's default.
3. Write the revert rule before you flip, and let the benchmark make the call.

## What I cut from the old version of this page

Old routing guides, mine included, were full of per-million-token price tables and benchmark scores. Prices change quarterly and most of those scores had no source I could check, so they're gone. If you need prices, get them from the provider's pricing page on the day you decide, and write the date next to them.

**Next:** [Agent memory you own](/docs/patterns/agent-memory/)
