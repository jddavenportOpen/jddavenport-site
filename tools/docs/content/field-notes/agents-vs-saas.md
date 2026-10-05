---
title: "Why agents will eat a lot of SaaS"
description: "SaaS gives you a better interface for doing work. Agents do the work. An opinion, with where it holds and where it doesn't."
section: field-notes
order: 30
updated: 2026-10-05
sources: ["articles/why-ai-agents-will-replace-saas.mdx"]
---

This is an opinion, and I'll label it as one: a lot of SaaS sells a better interface for doing work, and agents do the work. When the work itself gets done, the interface matters less. I've run an AI organization every day since April 2026, and that experience both supports the thesis and puts real limits on it. Both halves are below.

## The thesis

Look at what most business software promises. A CRM gives you a better screen for managing contacts. A project tool gives you a better screen for tracking tasks. Chat gives you a better screen for messages. None of them promise to do the work. You still type the call notes in, move the card across the board, and read every thread.

SaaS moved work from paper to screens. Agents move work from people to machines, with people approving the parts that matter.

## What it looks like in my own system

Three things I don't do by hand anymore:

**The CRM.** My CRM is a folder of Markdown files, one per person, written by agents from my mail, calendar, messages, meetings and voice notes. Each file separates machine facts (last contact, status) from real human events (a conversation, a meeting), and a weekly check fails if a machine fact leaks into the timeline. I never open a CRM screen to log a call. There isn't one.

**Meeting notes into work.** I carry a voice recorder. Recordings are transcribed every day and turned into tasks and CRM notes. The meeting becomes follow-ups without me retyping anything.

**The morning.** An executive-assistant agent works from my inbox, calendar and open commitments, flags threads I've left unanswered, and drafts replies. Drafts, not sends. More on that below.

The common thread: none of these needed a better interface. They needed the work done and a place to check it.

## Where the thesis holds

Honest read: the software most exposed is per-seat software whose main value is a screen where a person moves data between systems. Logging, updating, copying, summarizing, reformatting, chasing. That work is exactly what an agent with tool access does well, and it's a large share of what a lot of seats are paying for.

It also holds for glue work between tools. Before agents, the integration between two products was a person with two browser tabs open. An agent with access to both does it without the tabs.

## Where it doesn't hold

Six months of running agents taught me the limits, and they're real.

### 1. Money, identity and irreversible actions stay human

My system can draft anything and send nothing on its own. Every outbound message goes through one gate, and approvals are bound to the exact recipients, subject and body, so changing a word invalidates the approval. When I turned that gate on in June, its first check found five email senders that skipped it. None were malicious. They were code paths written before the gate existed.

So "agents do the work" needs an asterisk: agents do the work up to the point where a mistake costs money, reputation or something you can't undo. Past that point a person says yes. The interface for that yes still matters.

### 2. Reliability is real engineering, and someone pays for it

A SaaS vendor does the boring reliability work for you. Run your own agents and it's yours. I've had a restart kill every live session at once, a hidden confirmation dialog freeze the system for four and a half hours, and an agent-to-agent call that failed by returning an empty answer that looked like a real one. Each fix was a piece of infrastructure: guards, watchdogs, a durable message bus.

The cost doesn't vanish when you drop the license. It moves into engineering. For a team without that skill, the SaaS is still cheaper.

### 3. The system of record survives

Agents still need somewhere durable to keep the truth. My system's state lives in Postgres, 250+ tables of workflow runs, task ledgers, approval queues and cost records. "If it matters, it lives in a table, not in a context window." What agents eat is the screen on top of the database, not the database.

### 4. The API becomes the product

My agent-run merch store runs on Stripe and a print-on-demand vendor. My cockpit runs on Vercel and Supabase. I didn't replace any of them. My agents call them. Software whose API is the product becomes a tool agents use, and it does fine. Software whose screen is the product is the one under pressure.

### 5. Shared views for people still matter

When several humans need to look at the same thing and argue about it, a shared interface earns its keep. My own system still has a cockpit, a web app with a live pane for every agent session, because I need to see what's happening and step in. Agents reduce how much of the work happens in the interface. They don't remove the need to look.

## What I'd tell a team deciding today

- **Audit seats by verb.** For each tool, ask whether people mostly *decide* in it or *move data* in it. The second kind is your candidate list.
- **Keep your system of record.** Point agents at it. Don't let a migration to agents become a migration off your data.
- **Put the human gate in before the agents.** One door out for anything that sends, pays or deletes. Build it first; it's what makes running fast safe.
- **Price the reliability work honestly.** If nobody on the team can own watchdogs and incident fixes, buy the SaaS a while longer.

Best guess on timing: the shift is uneven and slower than the hype, because the limits above are real. But the direction is clear to me. The products that survive will be the ones agents can call, not the ones people have to click through.

**Next:** [How to break into product management](/docs/product-management/how-to-break-into-pm/)
