---
title: "The cockpit"
description: "A web app with a live pane for every agent session, an iPhone app around it, and a design system shared with this site."
section: nerve-center
group: "The cockpit"
order: 150
updated: 2026-10-05
sources: ["learn/tier-3/d1-nerve-center.mdx", "building-ai-os/arch-nerve-center.mdx", "building-ai-os/story-nerve-center.mdx"]
---

The cockpit is where I talk to the system. It's a Next.js web app on Vercel with a live chat pane for every agent session, an iPhone app that wraps it, and a set of pages that show real state: open loops, people, projects, memory, runs, the org chart. Internally it's Nerve Center v6. It doesn't run the system. The system runs whether or not a cockpit tab is open. The cockpit is a window and a keyboard.

## What you'll learn

- What's in the cockpit and how it connects to the agents
- The session model: one live brain per domain, parked when idle
- How the cockpit proves which build is live, and the two incidents behind that
- What the first version got wrong, and the audit that said so

## What's in it

| Surface | What it does |
|---|---|
| Chat | A pane per session: the CEO agent, each domain agent, build workers. Clean chat bubbles by default, a raw terminal one tap away. Answerable question cards, a model and effort picker per pane, a read-aloud button on every reply |
| Org chart | A live graph of agents, domains, MCP servers and skills, rendered from what exists on disk |
| Open loops, CRM, projects | Views over the ledgers described in the previous articles |
| Memory, journal, runs | Views over the memory layer, the daily journal, and timelines of headless runs |
| Governance | The Warden's queue, usage, the system page |

The stack today: Next.js and React on Vercel, Postgres on Supabase behind it, and a Python service on my always-on Mac (the bridge) that fronts the actual Claude Code processes, which live in separate worker processes it manages. Vercel can't reach into my Mac's filesystem or processes, so everything live goes through the bridge, and everything the cockpit needs to show when the Mac is busy lives in Postgres. [The bridge](/docs/nerve-center/the-bridge/) covers that half.

### The design

The cockpit and this site share one design system, Warm Graphite: a warm near-black canvas, an amber accent, Geist for UI text and Geist Mono for telemetry, almost no motion. If this page looks familiar, that's why. The first cockpit, in April, was neon glassmorphism with a particle field that shifted color by time of day. It looked great in screenshots. The rebuild killed the spins, pulses and sweeps and kept state legible through color and text instead. Honest read: a cockpit you use for hours a day should be calm.

### The iPhone app

The phone app is a thin native shell around the cockpit's chat page: a full-screen web view with device-pair sign-in and native push notifications. The cockpit reaches the phone the moment it deploys, with no app store release, and new builds of the shell itself install from a private over-the-air page. An older fully native UI is kept only as a one-launch fallback if the web view can't load.

## The session model

In early June the Mac was running 24 live agent sessions at once: every domain brain kept warm around the clock, plus a fresh session every time I opened a domain chat in the cockpit. Load average hit 133, the tunnel to the cockpit flapped, and chat went down everywhere.

My rule after that, verbatim: *"We should have ONE domain agent live at a time, never many spawned versions, and only spawn when I chat with them, otherwise they are dormant."*

A reaper enforces it every few minutes:

1. One live session per domain. Duplicates are parked, keeping the newest.
2. Idle sessions are parked after a set number of minutes.
3. A session that's mid-response is never parked.

"Parked" means the process stops but the conversation doesn't. Opening the pane again resumes the same Claude Code session from its transcript, so the agent picks up mid-thought instead of starting blank. The live session count stays bounded and nothing is lost.

## Proving which build is live

The cockpit answers one question about itself: which commit am I running? A version endpoint returns the deployed git SHA, and it returns an error, not a cheerful 200, if a build has no SHA baked in. The endpoint came out of one incident, and a second one showed why it isn't enough on its own.

**July 30.** A raw deploy from a checkout that was five commits behind silently rolled back a merged fix. Every watcher stayed green. The drift guard that was supposed to catch exactly this had been logging "could not read versions" hundreds of times for a week, because it scraped a service-worker URL instead of asking the app. So the app learned to say its own SHA, and the deploy script became the only sanctioned way to ship (a pre-execution hook now blocks a raw production deploy).

**September 20.** A verified deploy was undone six minutes later by a guard that thought it was helping. Two different guards were writing the same production alias from two different sources of truth. The fix was one writer per thing, plus a test that fails if a third writer ever appears.

That SHA is also the first half of my definition of done for any UI change: prod serves the exact merged SHA, and a browser journey passes against prod. If either fails, it isn't done, whatever the agent says.

## What the first version got wrong

On May 31 I ran a five-agent audit of the cockpit. Its one-line verdict: *"The architecture is excellent. The content and focus are the problem. It's a beautiful cathedral with mostly-empty rooms."* It scored the cockpit about 4 out of 10 on actually serving its purpose. The findings that stung:

- Most domain areas were hollow. Their hourly heartbeats narrated their own emptiness.
- The agent registry oversold itself about two to one: many named "specialists" had no code behind them.
- A budget page showed April numbers as current, badged "On Track."
- Pages contradicted each other on the same metric. In the audit's words, the product disagreed with itself.
- A dashboard with 127 commits in 14 days had gone unopened.
- The vector store behind memory had been frozen for 32 days and nobody noticed.

The meta-finding was worse: about 95% of my messages to the system were me building the system, not using it. The audit's instruction: strip the cathedral to the butler. The lasting lesson is the one on the org chart: anything a human has to remember to update will lie, so render from what exists. [The system documents itself](/docs/safety-and-operations/ground-truth/) is that lesson in full.

## What's next

A rebuild, Nerve Center v7, is rolling out inside the same app. An early phone-first view went live on October 3 and 4, 2026: today, week, to-dos, notes and what needs me, mostly read-only. Most of the rest is built on branches behind feature flags. The chat panes are still the v6 surface, and the v7 screen that can send messages is built but switched off.

**Next:** [What the cockpit rebuilds taught me](/docs/nerve-center/cockpit-rebuilds/)
