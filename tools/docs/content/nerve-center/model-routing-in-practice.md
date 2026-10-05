---
title: "Model routing in practice"
description: "A budget router in April, one registry per tier, automatic model adoption, an explicit-only top tier, and a local model that crashed the box."
section: nerve-center
group: "Orchestration"
order: 70
updated: 2026-10-05
sources: ["building-ai-os/story-model-routing.mdx", "building-ai-os/arch-model-router.mdx", "learn/tier-3/h4-ollama-smart-router.mdx"]
---

My model routing wasn't designed. It was corrected, about once a month, by whatever had just gone wrong. Here's the sequence from April to October 2026, because each correction is a rule you can skip learning the hard way.

The framework version is in [Model routing](/docs/patterns/model-routing/). This is the history behind it.

## April: a router with a budget

The first router was a script that read a task's text, scored it for complexity keywords, and picked a tier: small model for lookups and formatting, mid model for most work, the big one for strategy. It tracked a daily dollar target of $15 and, past 80% of it, signaled agents to step down a tier.

It taught me the right instinct (most tasks don't need the biggest model) and two wrong mechanisms.

- **A budget cap fights the work.** On May 25, 2026 I removed the daily cap and quiet hours from my charter. Cost is still tracked for visibility. It no longer blocks anything or pages me. A downgrade at 4pm because of what ran at 9am is a quality decision made by a clock.
- **Keyword classifiers guess.** Routing is a design decision you make when you build an agent or a lane, not a runtime guess about a sentence.

By July the router was unwired. It still sits in the repo, labeled as not an authority for anything.

## July 3: "sonnet" meant three different models

An audit found that different parts of the system each had their own idea of which model a tier meant: the chat client, the fleet, the backend's role table, the cockpit's picker. The word "sonnet" resolved to three different model ids depending on which file you asked.

The fix was a single registry: one file, one model id per tier. Everything else is generated from it, including environment files, the cockpit's model picker and the daemon settings. Two nightly checks now guard it from both directions:

- A **death canary** probes every id in the registry, so a retired model pages me before it becomes an outage.
- A **birth watcher** looks for new model ids in the latest published Claude Code release, so a new model doesn't go unnoticed for weeks.

## July 24 and August 15: the definitions that didn't move

Opus 5 shipped on July 24 and I made it the default everywhere the same day. Or I thought so.

Three weeks later I found about two-thirds of my agent definitions still saying `model: sonnet`, a tier below the default I'd just chosen. Their `model:` lines were hand-typed, nothing swept them, and no check noticed. The chat sessions themselves were fine, because they inherit the default. The specialists those sessions spawned from definitions were a tier behind.

Since August 15, 2026, a policy file says which tier each agent belongs to, a script stamps the `model:` line into every definition from the policy plus the registry, and a weekly check fails on any disagreement. Nobody types a model id into an agent definition anymore.

## August 15: the Warden adopts new models itself

The same day, I asked for the newest model in each family to be adopted automatically. The Warden, my governor for autonomous changes, does it nightly behind gates. Any gate failing means no change, and it tries again tomorrow:

| Gate | Why |
|---|---|
| Same family only | Opus replaces Opus; nothing crosses families |
| Never a downgrade | A tier only moves forward |
| Published and routable | The installed CLI must know the id |
| Live probe | One real call must succeed. A quota error defers instead of condemning. |
| Quality bench | Candidate vs incumbent on a fixed set of deterministically-scored tasks, no model judging a model |
| Re-verify and roll back | After applying, regenerate everything and re-run the checks; any failure rolls back |

Rollback needs no git, no network and no working new model, by design. It has to work on the day things are broken.

Fable 5.1 was adopted by this path the night it shipped, September 1. Opus 5.5 is the more useful story. I asked for it on September 22, it went through the same gates, and the quality bench scored it level with the old Opus with no task regressed. Getting there exposed three defects that had been quietly breaking the nightly adopter. The worst: one unregistered agent definition made a generator refuse, so every nightly adoption had been rolling itself back. The rollback worked perfectly. Nobody had noticed it was firing. The outgoing model stays selectable, so anything pinned to it keeps working.

## The birth-model problem

A resumed Claude Code session keeps the model it was born with. So a registry change doesn't reach a long-lived chat pane; that pane is still running whatever it started on. An hourly drift guard now finds panes running a stale default and switches them through the cockpit's own live-switch path. It refuses to touch a pane mid-turn, and it never overrides a pin I chose on purpose.

That rule mattered sooner than I expected.

## July 31: one model, top effort, everything

In late July I measured where the work volume went (list-price equivalent). One model did over 90% of it, at top effort, because every workflow lane ran build on the top tier, review on the top tier at maximum effort, and fix on the top tier again. A one-line doc correction got the same adversarial review as a change to an autonomy gate.

The rule that came out of it: review effort scales with blast radius, not lane count. Autonomy, safety gates, credentials, external sends, money and irreversible changes get top tier, top effort and an independent reviewer. Normal engineering gets high. Mechanical edits get medium. Doc and receipt fixes get no review agent at all.

A follow-up in September found the other half of the leak. Fan-out children with no model named were about half of all work volume, because an unnamed lane inherits the most expensive tier. Now every fan-out lane names its tier, and a lint flags the ones that don't.

## August 8 to September 4: two writers, one setting

Two scripts each wrote an effort value into the same settings files. One wanted `xhigh`, the other restored `max`, each from its own hardcoded constant. They overwrote each other 30 to 70 times a day for almost a month.

The fix was one registry key that both read. A detail worth knowing: Claude Code's settings file doesn't accept `max` as a persisted effort. A file that says `max` is read as if the setting were absent. `max` exists only per session. So one of those writers had been fighting to write a value that did nothing.

## September 5: the top tier became explicit-only

From August 28 to September 2, I deliberately made Fable, the most capable and most expensive tier, my default chat model. Then I switched the default back.

The panes born during that window kept running Fable until they ended on their own, because of the birth-model rule above. On September 5 I made the tier explicit-only: nothing routes there automatically, including planning work that used to. It stays one deliberate click away in the cockpit.

Honest read on the cause: the usage I was worried about didn't come from automatic routing. The automatic planning route hadn't fired once in the 33 hours before the fix. It came from long-lived panes born in the deliberate window. So the change closed an exposure, not an active leak. An earlier claim that usage "spiked 7x on the directive day" came from comparing two adjacent days instead of the whole series, and was wrong.

## September 9: the local model that crashed the box

The local tier was supposed to be the free one. On September 9 I traced a run of ten watchdog kernel panics to memory. A 12 GB open-weight model was being loaded 90 to 250 times a day by a messaging pipeline, alongside browser and Node swarms, on a 36 GB machine. The memory gate trusted a "free memory" reading that said 87% free at 34 of 36 GB used.

The fixes, all on the same day:

- A memory-truth gauge in every admission gate, measuring what's really available instead of what the OS summary says.
- Heavy local models refused on that machine; light ones allowed under a memory budget.
- A compressor breaker that kills runaway work in verified process groups.
- A boot governor so a restart doesn't stampede.

An earlier fix that afternoon targeted a boot-time stampede of scheduled jobs. That was real, but it wasn't the whole story. The lesson from the pair: a reading taken at the wrong moment can say "not memory" with a straight face.

## October 2: effort for chat, separately

In a chat-speed audit on October 1, model time was about 85 to 90% of the wait in my cockpit: top effort on every pane plus very large contexts. Since October 2, interactive panes default to `high`, and fleet work keeps the top effort it was getting. I can still turn any single pane up to `max` from the cockpit.

That's a routing decision too. The right effort for a background build isn't the right effort for a conversation I'm waiting on.

## Where it stands

| What | Today |
|---|---|
| Source of truth | One registry, one model per tier; everything else generated |
| Agent definitions | Model line stamped from policy; weekly check |
| New models | Adopted nightly by the Warden behind gates, with rollback |
| Live sessions | Hourly drift guard; deliberate pins respected |
| Deepest tier | Explicit-only since September 5 |
| Effort | Tiered by blast radius; chat panes default `high` |
| Local models | Memory-gated; heavy ones refused on the main machine |

If I had to compress all of it into one rule: never let a default decide something expensive, because defaults outlive the reason you set them.

**Next:** [Expert agents: route by topic](/docs/nerve-center/expert-agents/)
