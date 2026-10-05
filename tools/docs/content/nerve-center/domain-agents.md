---
title: "Domain agents"
description: "One persistent agent per area of life and work, each with its own folder, state, rules and live session."
section: nerve-center
group: "Orchestration"
order: 40
updated: 2026-10-05
sources: ["learn/tier-3/b2-eight-domain-agents.mdx", "building-ai-os/arch-domains.mdx"]
---

A domain agent owns one area of my life or work, and it's the agent that knows that area best. Each one has its own folder, its own rules file, its own state, and a long-lived Claude Code session I can open in the cockpit. The CEO agent coordinates them. It doesn't try to hold all of their context at once, because that's how you get an orchestrator that knows a little about everything and nothing about anything.

## The domains

The main ones, under the names the [live capabilities page](https://nerve-center-showcase.vercel.app) uses:

| Domain | What it owns |
|---|---|
| school | Coursework, grades, deadlines, syllabus tracking |
| ai-foundry | The BYU AI Foundry, the student builder program I co-founded |
| consulting | Proposals, deliverables, pipeline |
| growth | Content sourcing, drafting and the preview pipeline |
| health | Wearable sync into a table and a nightly summary |
| finance | Bank ingest, categorization, budget sync |
| family | Household calendar coordination and logistics |
| life-ops | Registrations, errands, bills, and keeping the machine itself healthy |

There are others, some of them private. The list moves: domains get added when an area earns one and archived when it stops earning one.

## What a domain is, on disk

A domain is a folder with a fixed shape. Here's the skeleton, with nothing personal in it:

```text
domains/<name>/
  CLAUDE.md        rules and identity for this domain's agent
  config.yaml      integrations, schedules, owner
  state/
    report.md      the current picture, with a "recent events" block
    tasks.yaml     single actions and chores for this area
    goals.yaml     what this area is trying to move
    events.jsonl   an append-only log of things that happened
```

When I open a domain's session, Claude Code starts in that folder. It reads the domain's own CLAUDE.md plus my user-level rules, and nothing else by default. That detail matters more than it looks; see the last section.

Tasks and projects stay separate. A single action ("renew the registration") is a domain task. Anything with a goal and an end state gets a project folder of its own, and a domain task can point at it. When in doubt, it's a task.

## How a domain's state moves

This changed twice, and the changes are the useful part.

**April: hourly heartbeats.** On April 16 every domain got an hourly heartbeat, staggered across the hour so they didn't all fire at once. Each heartbeat was an LLM run that read the domain's state, wrote a structured `report.md` (not questions, answers), and stopped. The CEO agent read the reports.

**July: event-driven pulses.** By July most heartbeat runs were no-ops behind a change check: an hourly model call to say nothing had changed. And the change check had a worse bug. It re-stamped the "last updated" time without a content change, which hid real staleness. On July 21 I retired the hourly LLM heartbeats and replaced them with pulses: when something real happens (a project log entry, a completed task, a message on the bus), one small function appends an event, refreshes the report's recent-events block, and stamps the freshness time. A pulse only re-stamps when it writes something.

**August: off.** On August 15 I turned off the rest of the heartbeat class. My note at the time was that I got no value out of any of them. The expensive half was already dead, so the savings were small. The cleanup wasn't. Reports with no producer went stale, and those reports were being fed into new sessions under a "live" header. The fix was to show the *median* snapshot age with a note that heartbeats are retired, instead of the newest. A few self-updating domains had been masking a lot of frozen ones.

> **Tip:** If a status file has no producer, the reader has to say so. A stale report presented as live is worse than no report.

## How a domain asks for a decision

A domain agent doesn't guess at cross-domain calls. It asks. The school agent can ask the CEO agent whether a deadline conflicts with a work commitment; the CEO agent can ask the health domain for this week's summary. Those questions go over the [durable agent bus](/docs/nerve-center/the-agent-bus/), so a timeout can't silently turn into an empty answer.

Domains can also be switched off. When a domain is off, a blocking question to it fails fast, and a one-way message to it is persisted but held, not delivered and not dead-lettered. Turn the domain back on and the held messages flow. Off means paused, not lost.

## The persistent-brain gotcha

A domain's session is long-lived. When the cockpit brings it back, it resumes the same Claude Code session. And a resumed session keeps the model it was *born* with.

That bit me in August. I'd switched the default model in the registry weeks earlier. Most of my live domain sessions were still on the previous model three weeks later, because no settings change reaches a process that's already running. Nothing errored. They were just quietly a model behind.

The fix has two halves:

1. Agent definition files carry a model line that's generated from a policy file, never typed by hand. Change the policy, re-run the stamp, and every definition updates.
2. An hourly drift guard compares every live session's model to the registry and switches drifted ones through the cockpit's own live-switch path. It refuses a session that's mid-turn, and it never overrides a model I picked on purpose.

## Where rules have to live

The domain session reads its own CLAUDE.md and my user-level file. It does *not* read the main agent-system CLAUDE.md, because it doesn't start in that folder. So a routing rule written only in the main project file reaches the CEO seat and nobody else.

I learned this the slow way: a domain session kept ignoring a rule that was clearly written down. It was written down in a file that session never loads. Now any rule every agent needs lives in the user-level file, with a line explaining why it's there.

## Keeping domains honest

- **A daily integrity check** catches half-built domains: a schedule that calls a module that doesn't exist, a folder with no state. Before it existed, one domain's scheduled job failed every hour in June, calling a module nobody had written, and nothing noticed.
- **Retirement is archive, not delete.** Retiring a domain snapshots its schedules, launch jobs and folder, and a tested restore puts it back byte for byte.
- **One domain list, written by the scaffold script.** Every cockpit surface reads the same list, and the script that creates a domain appends to it. In August a domain that had been set up by hand ran for weeks without appearing anywhere in the cockpit, because it never made the list. Create domains through the script or they don't exist where you look.

## If you build these

1. Start with two or three domains. Each one is surface you have to keep true.
2. Give each one a folder, a rules file and a state shape. Same shape everywhere.
3. Move state on events, not on a timer. Hourly "nothing changed" runs are noise.
4. Assume running sessions don't see config changes. Build the drift guard.
5. Put shared rules where every session actually reads them.

**Next:** [The agent bus: how agents talk](/docs/nerve-center/the-agent-bus/)
