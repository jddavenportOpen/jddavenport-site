---
title: "Lessons from running agents every day"
description: "What survived six months of production: prompt discipline, memory when you need it, schedules as infrastructure, machines over memos."
section: field-notes
order: 10
updated: 2026-10-05
sources: ["articles/the-54-agent-stack.mdx"]
---

I've run a production AI organization every day since April 10, 2026: 30+ agents in daily production, 100+ built over time, on always-on hardware with Claude Code as the runtime. These are the lessons that survived contact with real work. Most of them came from something breaking.

## 1. Agents fail on instructions before they fail on code

The first thing that kills an agent is rarely a bug. It's an agent that doesn't know what it owns, what it must never do, or what "done" looks like. Mine trampled each other's git state, drifted into work nobody asked for, and answered questions from their own heads when an expert agent existed for exactly that topic.

What fixed it was boring and written down:

- **A definition per agent.** One file per agent with its scope, its tools, and its hard limits. Formal definitions didn't exist in my system before July 2026. Before that, agents were folders and good intentions.
- **Shared context files.** Four files every drafting or deciding agent reads first: who I am, how I decide, how I write, and the rules I never break. There's a public starter version at [context-kit](https://github.com/jddavenportOpen/context-kit).
- **Routing tables.** For certain topics the main agent must call the specialist instead of answering. It works from a table of trigger phrases, so routing doesn't depend on it remembering a paragraph.

The catch I didn't see coming: a rule only works where the agent can read it. An agent started from one project folder never loads the rules file in another. I had routing rules that reached the top-level agent and none of the domain agents, which start in their own folders. Some rules now live in the user-level file on purpose, because that's the only one every session loads. And the main rules file is size-capped by a pre-commit check, because every live session rereads it whenever it changes.

## 2. Memory is a feature you add when you need it

Every tutorial shows you one call to a model. Almost none show you how the second call remembers the first.

Mine went in stages. First, nothing: fine for one-shot tasks, useless for anything about people. Then files: a changelog per project, a work plan, a one-line ship log per change, rolled up daily. That carried the system for its first two months, and it's still the backbone. In late June memory became a graph plus a vector store, so an agent could ask "what do I know about this person" and get connected facts instead of keyword matches.

Honest read: start with files. A database is a graduation, not a starting point.

The lesson that cost the most: memory needs provenance. In September I found that a hook meant to look up names in my CRM had been reading text the system itself injects into prompts (recalled memories, context carried over from earlier sessions) as if I had typed it. It minted fake "people" from that text, and the fakes flowed into memory. The fix was to strip injected text before extraction, refuse to trust anything the hook had written, quarantine the bad entries, and add a weekly check. If you can't say where a memory came from, you can't trust it.

## 3. Orchestration is harder than agents

A sub-agent doesn't know what its parent knew. Without an explicit hand-off you get agents that re-ask settled questions, reverse decisions, and build things that conflict with the architecture. Every delegation now carries the task, the context, the success criteria, which files to read first, and which model tier to run on.

The plumbing between agents is where the subtle failures hide. My first agent-to-agent call was synchronous, and when it timed out it returned an empty string. An empty string looks exactly like a real empty answer. The calling agent carried on, confidently, with nothing. The replacement is a durable bus: every message is saved before delivery, a transient empty is retried, and a real failure is dead-lettered, alerts me, and raises an error. It can no longer fail quietly. Honest limit: durable means it survives a crash or a timeout, not the whole machine going offline.

Fleets have their own version. A September audit found headless workers still running at top effort after the agent that started them had timed out and moved on. Orphans, still burning quota.

## 4. Schedules are production infrastructure

Scheduled jobs are the system's heartbeat. When they stop, agents stop being proactive and the whole thing goes quiet.

What I learned running them:

- **Every future obligation becomes a machine loop.** Cron for forever, a watcher for "until this happens," a session loop for work in flight, a one-shot for a date. A promise that only lives in a chat reply is a dropped promise.
- **Every loop names its off switch.** Watchers expire after 30 days by default. No immortal loops.
- **Alert on change, not on schedule.** A four-hourly re-send of the same unchanged list was my single biggest noise complaint. Content-hash it or don't send it.
- **Know your scheduler's limits.** On macOS, cron can't access the login Keychain, so jobs that need credentials there have to be LaunchAgents.
- **Measure work, not uptime.** A session once sat on a confirmation dialog nobody could see for four and a half hours. Nothing crashed, so nothing alerted. Liveness checks now ask "did you do work?" instead of "are you running?"

## 5. Enforce with machines, not memos

This is the lesson I'd tattoo on a new builder. Prose rules don't survive contact with autonomous agents.

In July one agent restarted the service that owns every session with a raw command instead of the safe script, and every live session died in two seconds. The safe script existed, but using it was on the honor system. A pre-execution hook now blocks the raw command outright.

When I built one gate for every outbound message, its CI check found five email senders that skipped it on day one. Manual audits had missed all five.

The counterexample matters too. I also had a policy hook watching tool calls for risky sends. In early September an audit showed it had logged tens of thousands of "allow" decisions and zero blocks, because the real sends happened inside Python code the hook never saw. The gate in the code path is what actually enforces. A guard has to sit where the action happens, not where it's convenient to look.

## 6. Pick the model by what the work can break

At the end of July I measured my own work volume and found one model doing over 90% of it at top effort, including doc fixes. The rule now: effort scales with blast radius. Top effort for safety gates, credentials, anything that can send externally or move money, anything irreversible. Normal engineering gets high. Mechanical edits get medium. A doc fix doesn't get a reviewer at all.

Related: one setting should have one writer. Two of my scripts wrote different effort values into the same settings file and fought each other 30 to 70 times a day for almost a month before I noticed. Both now read one registry key.

## What I'd do differently

**Fewer repos, more depth, sooner.** From February to July I created roughly 28 repositories a month. In August that fell to 16 and in September to 10, while merges into the main system climbed from 6 in May to 332 in August. The system got better when I stopped starting things.

**Build the stop conditions first.** The send gate landed in the same fortnight my merge rate jumped from single digits to dozens. Honest read: that's not a coincidence. You can't run autonomous work at that pace unless there's exactly one door out.

**Build monitoring before the agents that depend on it.** I did it backwards, and paid for it in silent failures.

The system is live. It breaks. I fix the process that let it break, and it gets better. That's the whole method.

**Next:** [Building in public without fooling anyone](/docs/field-notes/building-in-public/)
