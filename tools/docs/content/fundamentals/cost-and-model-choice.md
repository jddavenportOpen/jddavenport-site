---
title: "Cost and model choice"
description: "Subscription vs API billing, tiering models by work type, and how to read cost without fooling yourself."
section: fundamentals
group: "Working habits"
order: 120
updated: 2026-10-05
sources: ["learn/tier-1/12-cost-and-model-routing.mdx", "articles/cost-of-ai-agents.mdx"]
---

"AI is expensive" and "AI is cheap" are both lazy. The real answer depends on how you pay, which model you point at which job, and whether you can read your own numbers. This article covers the two ways to pay for Claude Code, how I tier models by the kind of work, and the measurement mistakes that will fool you if you let them.

## What you'll learn

- Subscription vs API billing, and which one fits which work
- Real numbers from my system, labeled for what they are
- How to tier models (and effort) by what the work can break
- Why silence in a config defaults to the most expensive option
- The two different measurements people confuse, and the bad call it caused me

## Two ways to pay

| | Subscription (Pro, Max, Team, Enterprise) | API key (Claude Console) |
|---|---|---|
| You pay | A flat monthly price per seat | Per token, input and output, at each model's rate |
| The limit | Usage windows (a session window and a weekly window) | Your budget and rate limits |
| Good for | You at a keyboard, interactive work | Automation, CI, products you ship to others |
| What a dollar figure in `/usage` means | Not your bill. It's list price, computed locally. | Close to your bill |

Prices change, so I won't print them here. Check [claude.com/pricing](https://claude.com/pricing) on the day you decide.

The thing people get wrong: having a subscription doesn't give you free API calls for your own code. The subscription covers Claude Code sessions signed in with your account. An app you build that calls the API directly is billed to an API key.

When you hit a subscription window, switching models doesn't help: the window is shared across models. You wait for the reset, or turn on usage credits if your plan has them.

## Real numbers

From my published teardown, measured on my own system, as list-price equivalents:

- A heavy build session runs about $30 to $35. Two examples: $34.67 across 201 model calls, and $32.13 across 188.
- A five-reviewer audit panel is roughly 300K tokens.
- A rote heartbeat that formats a status report costs pennies on a small model.

For a broader reference point, Anthropic's own cost docs (as of October 2026) say enterprise deployments average around $13 per developer per active day and $150 to $250 per developer per month, with 90% of users under $30 per active day.

I say "list-price equivalent" on purpose. I run on subscriptions. Those dollar figures are what the same token volume would cost at API list price. They measure work volume. They are not a bill.

## Tier models by work type

Not every job needs the biggest model. Early on, every task in my system went to the top model: research, commit messages, checking whether a file exists. That's the most expensive way to be lazy.

The tiers I run as of October 2026:

| Tier | Model | Used for |
|---|---|---|
| Interactive and review | Opus 5.5 | Chat sessions, planning, code review, judges |
| Build | Sonnet 5 | Writing code, most autonomous work |
| Bulk | Haiku 4.5 | Rote classification, formatting, cheap status jobs |
| Local | A small open model on my own hardware | Bulk extraction where privacy and latency beat quality |
| Flagship | Fable 5.1 | Only when I explicitly ask for it |

Three rules keep that table honest:

1. **One file names the model for each tier.** Everything else (agent definitions, scripts, the cockpit's model picker) is generated from it. "Sonnet" once meant three different models in three places in my system. Now a model change is one line.
2. **The most expensive tier is explicit-only.** Since September 5, 2026, nothing routes to the flagship automatically. A person has to pick it.
3. **New models get adopted behind gates.** Same family, never a downgrade, a live test call, a quality check, and automatic rollback if anything fails.

## Effort is the second dial

Recent models let you set how hard the model thinks: low, medium, high, xhigh, max. Higher effort reasons longer and uses more tokens. It's a separate dial from the model, and it matters just as much.

On July 31, 2026 I measured where my work volume went. One model did over 90% of it, at top effort, because every workflow lane ran build, review and fix at the highest settings regardless of what the lane touched. A lane fixing a typo in a doc got the same adversarial review as a lane changing a safety gate.

The rule now: **review effort scales with blast radius.**

| What the change can break | Review |
|---|---|
| Autonomy, safety gates, credentials, anything that sends externally or moves money, anything irreversible, a shared rail every producer rides | Top effort, independent reviewers |
| Normal engineering: a new module, a schema change, a live loop's behavior | High |
| Mechanical edits, config, cadence changes, test-only work | Medium |
| Doc text, comment fixes, log paths | No review agent. The builder checks its own work. |

Cost isn't a cap in my system (I removed budget caps in May 2026; cost is tracked for visibility). Tiering isn't about saving money for its own sake. A second top-tier reviewer on a doc fix buys nothing, and it makes everything slower and uses plan capacity that real work needs.

## Silence is the most expensive setting

When you fan work out to many agents and don't say which model or effort each one should use, they inherit the default. In my setup that default is the top model at a very high effort level. So an unlabeled lane gets the priciest option by accident, multiplied by however many lanes you launched.

The fix is a habit: name the tier on every fan-out lane, even when the answer is the top tier. A linter in my system flags lanes that leave it out. Saying "opus" on purpose is fine. Saying nothing is the bug.

## Context is cost, and it's speed

Every turn, the model processes the whole context window. A session carrying 400K tokens of history pays for that on every message, in tokens and in seconds. My October 2026 chat-speed audit found model time was about 85 to 90% of the wait in my cockpit, driven by top effort on every pane and very large contexts. The cheapest optimizations are the boring ones from [sessions and context](/docs/fundamentals/sessions-and-context/): `/clear` between tasks, subagents for big investigations so their file reads stay out of your main window, and compacting before long work.

## Read your numbers without fooling yourself

I made this mistake myself.

My daily cost readout shows two numbers. One is yesterday's dollar figure: every model call from my local session transcripts, repriced at API list price. The other is plan consumption: the percentage of each subscription's weekly window used. They look related. They measure different things.

The dollar figure is work volume. The quota percentage is how close a plan is to its limit. One morning a large dollar figure got read as "this plan is exhausted, move the work to another plan." The plan wasn't close to its limit. The conclusion came from the wrong number.

So:

- Never infer plan exhaustion from a dollar figure. Check the quota.
- Never call list-price figures "what it cost" on a subscription. Say "work volume, list-price equivalent."
- In Claude Code, `/usage` shows both, and the docs say plainly that for subscribers the session dollar figure isn't relevant for billing.

> **Tip:** Start with one agent on a small model doing a repetitive job you hate. Measure the time it saves and the volume it uses. Then move it up a tier only if the output is measurably worse. Most rote jobs never need to move.

For how routing evolved in my system, including the dead ends, see [model routing in practice](/docs/nerve-center/model-routing-in-practice/). The pattern itself is in [model routing](/docs/patterns/model-routing/).

**Next:** [Build your first agent](/docs/fundamentals/build-your-first-agent/)
