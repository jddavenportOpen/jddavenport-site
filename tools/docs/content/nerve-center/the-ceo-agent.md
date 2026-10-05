---
title: "The CEO agent"
description: "The orchestrator I talk to: how it routes work to domain agents and specialists, and what it may never do alone."
section: nerve-center
group: "Orchestration"
order: 30
updated: 2026-10-05
sources: ["learn/tier-3/b1-ceo-orchestrator-agent.mdx", "architecture/ceo-agent.mdx"]
---

The CEO agent is the one I talk to. It holds the cross-domain picture, decides who should do a piece of work, checks the result, and is the only agent whose job is to talk to me. It can build, research and delegate on its own. It can't send anything to anyone, move money, or do anything irreversible without my yes.

"CEO" is a job title, not a corporate org chart. There is no COO, CTO or CMO agent, and there never was. The old docs described a C-suite that existed only as a diagram. What exists is one orchestrator above persistent [domain agents](/docs/nerve-center/domain-agents/) and a bench of specialists.

## What you'll learn

- The three shapes the CEO agent runs in, and why
- How it decides what to handle and what to hand off
- The hard walls, and where they're enforced in code
- The bugs that taught me each wall

## One profile, three lifecycles

The CEO is a profile (identity, cross-domain authority, rules) that runs in three places:

| Lifecycle | Where | Why it exists |
|---|---|---|
| The persistent seat | Behind Telegram, as headless Claude Code turns that resume one long session | It's the seat of record: always on, reachable from my phone, owns standing loops |
| CEO worker panes | Live sessions in the cockpit I open for a big piece of work | Long interactive jobs where I want to watch and steer |
| Ephemeral fan-out | A sub-agent that wears the CEO profile for one scoped task, then exits | Cross-domain judgment inside a larger workflow |

The persistent seat runs on Opus 5.5, the current interactive default. When its context fills to about 90%, it writes a carryover summary to a running-state file, starts a fresh session, and seeds the new one with that summary. So the conversation survives a rotation, and the facts that matter live in a file, not in a context window.

I reach it from the cockpit (web or the iPhone app) and from Telegram. Same orchestrator, same rules. The iMessage channel is a different door: it goes to the [executive assistant](/docs/nerve-center/executive-assistant/), not to the CEO agent.

### One context assembler, not three hand-kept lists

Every CEO lifecycle gets its starting context from one shared helper. It assembles the agent's identity file, three of my [personal context files](/docs/nerve-center/personal-context/) (who I am, how I decide, my hard rules), a generated summary of the org's charter, a one-line status per domain, and a live snapshot of P0 and P1 open loops, each with its own character budget and the whole thing capped at about 16,000 characters. When it drafts as me, the file on how I write gets added.

That helper exists because of a quiet bug. Three places used to build CEO context by hand, and all three were wrong in different ways. The worst: the preload for agent-to-agent CEO questions claimed to load three files. In practice it loaded a truncated identity file and silently skipped the other two, because their paths had a doubled folder name and an existence check quietly passed over them. Every answer looked fine. It just knew less than it claimed to. One assembler, one list, a test on what it actually loads, and the bug class goes away.

## How it routes work

The routing rule is short: handle it inline only if it's quick and needs no domain expertise. Everything else goes to whoever owns it.

| Request | Where it goes | How |
|---|---|---|
| Status lookup, quick read, a decision across domains | Handled inline | Reads shared state and files |
| "What's due in school this week?" | The school domain agent | A durable message over the [agent bus](/docs/nerve-center/the-agent-bus/) |
| A tax deadline, a training question, a course concept | An expert agent | Topic routing, [never answered from its own head](/docs/nerve-center/expert-agents/) |
| "Build X", "fix Y" | Build workers in isolated worktrees | Sub-agents or the [fleet](/docs/nerve-center/fleets/) |
| Email, message, post | Drafted, then held | The [send gate](/docs/safety-and-operations/the-send-gate/) waits for my yes |

Two habits are written into its rules because I kept watching agents skip them:

- **Inventory before spawning.** Before building a new agent for a task, check whether one exists. A surprising amount of my early sprawl was duplicate agents.
- **Runbook first.** Before hand-writing a report or a draft for a project, look for that project's existing generator and run it.

Delegation only counts if it's verified. A sub-agent that says "done" hasn't proven anything. The CEO agent checks the work against something real: a test that went from red to green, a URL serving the merged commit, a row in a table. For anything with a user interface, "done" means a done gate passed against prod: the live URL serves the exact merged commit, and a browser run of the user journey passes.

## The hard walls

| The CEO agent will never, on its own | Enforced by |
|---|---|
| Send anything to a third party as me | The send gate: single-use approval tokens bound to a hash of the exact recipients, subject and body |
| Move money | The same gate, plus a denylist in the work gate |
| Do anything irreversible | A blast-radius classifier on queued work, PreToolUse hooks on commands |
| Push to someone else's GitHub repo unchecked | A GitHub governor that judges anything outside my own repos |

Pushing to my own repos is allowed and expected. Agents ship code without asking me; I review the product in prod, not the diff.

The personality rule matters as much as the walls: push back when I'm wrong, with receipts, and concede fast when I push back with better ones. I don't want an orchestrator that agrees with me. That rule gets copied into the prompt of every agent it spawns.

## The work queue, and the bug in its safety gate

From June, the CEO layer had a bounded executor: every two hours it pulled one approved item from a ledger, classified its blast radius, dispatched a build agent in a worktree for anything safe, verified the result, and retried with backoff up to a cap before parking the item and telling me once.

The classifier is conservative on purpose. It returns one of three verdicts:

- **ALLOW:** clearly a reversible build. Dispatch.
- **DENY:** reads as external send, money, deploy or anything irreversible. Surface to me.
- **ESCALATE:** can't tell. Treated like DENY.

A false block costs me one message. A false allow could send an email as me. So the denylist runs first, and any irreversible signal wins.

Then it over-corrected. In late July I measured the backlog and found the gate was refusing legitimate builds because the proposal *descriptions* quoted things like a dollar figure or the word "deploy" while explaining a problem. The single biggest refusal class was a proposal quoting a cost while describing a bug. The gate couldn't tell "this proposal describes a deploy problem" from "this build will deploy." The fix scores the instruction with the full denylist and the diagnostic prose with a narrow one that only reacts to the catastrophic classes (a send as me, money movement, destructive data, credential rotation, force-push).

> **Note:** As of October 2026 the scheduled work-queue run is paused, along with a batch of other scheduled pushes I paused in mid-September. The gate and the executor still exist. I'd rather run fewer autonomous loops that I trust than many I don't read.

## If you build one

1. Give the orchestrator one persistent seat and write its running state to a file, so a context rotation isn't amnesia.
2. Build its starting context with one function, and test what that function actually loads.
3. Route by ownership. The orchestrator that does everything itself is the one that knows nothing deeply.
4. Put the walls in code, and score instructions separately from descriptions.
5. Expect to turn things off. Pausing a loop is a decision, not a failure.

**Next:** [Domain agents](/docs/nerve-center/domain-agents/)
