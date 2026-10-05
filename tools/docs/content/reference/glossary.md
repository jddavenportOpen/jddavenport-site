---
title: "Glossary"
description: "Plain definitions for the terms these docs use, from harness and hook to send gate, blast radius and dead letter."
section: reference
order: 10
updated: 2026-10-05
sources: ["glossary.mdx"]
---

Plain definitions for the words these docs use, each linked to the article that teaches it. Alphabetical within four groups: Claude Code itself, building agents, running an AI organization, and safety and quality.

## Claude Code and the harness

**Agent.** A model in a loop with tools: it reads the situation, decides what to do, does it, looks at the result, and goes again until the job is done or it needs you. A chatbot answers. An agent acts. See [Anatomy of an agent](/docs/patterns/anatomy-of-an-agent/).

**CLAUDE.md.** A Markdown file of standing instructions that Claude Code loads at the start of a session: your rules, conventions and commands. It sits in context for the whole session, so every line has a cost; keep it short and move history somewhere else. See [CLAUDE.md: teaching the agent your rules](/docs/fundamentals/claude-md/).

**Compaction.** When a session's context fills up, Claude Code summarizes the older parts to make room. Anything not written to a file can lose detail in the summary, which is why state belongs on disk. See [Sessions and context windows](/docs/fundamentals/sessions-and-context/).

**Context window.** Everything the model can see at once: instructions, files it read, tool results and the conversation so far. Bigger isn't free; a fuller window is slower and costs more per turn.

**Effort.** A dial for how much the model thinks before it answers, separate from which model you pick. Higher effort is slower and more thorough. See [Cost and model choice](/docs/fundamentals/cost-and-model-choice/).

**Harness.** Everything wrapped around the model that lets it act: the loop, the tools, file access, settings, hooks and permission prompts. Claude Code is a harness. See [What Claude Code is, and what a harness is](/docs/start-here/what-is-claude-code/).

**Hook.** A command that Claude Code runs automatically at a fixed point, such as before a tool call or when a turn ends. A hook can block an action outright, which makes it the place for rules the model must not forget. See [Hooks: rules the model cannot forget](/docs/fundamentals/hooks/).

**MCP server.** A program that gives the agent new tools or data over the Model Context Protocol, an open standard. Calendar access, a database, a search engine: each can be an MCP server. See [MCP: giving the agent new senses](/docs/fundamentals/mcp/).

**Permission mode.** How much Claude Code may do without asking you first: from asking before every edit or command to running freely inside rules you set. See [Permissions and safety basics](/docs/start-here/permissions-and-safety/).

**Session.** One running conversation with Claude Code, with its own context window. Sessions end; files don't.

**Skill.** A packaged piece of know-how (instructions, and sometimes scripts) that the agent loads only when the task calls for it, so it doesn't sit in every prompt. See [Skills](/docs/fundamentals/skills/).

**Sub-agent.** A separate agent the main one starts for a focused job. It works in its own context and hands back a result, which keeps the main conversation clean. See [Sub-agents and delegation](/docs/patterns/sub-agents-and-delegation/).

**Token.** The unit models read and write, roughly three quarters of a word in English. Context size and usage are counted in tokens.

**Worktree.** A second working folder for the same git repository, on its own branch. Parallel agents each get one so they can't overwrite each other's files or switch the branch out from under each other. See [Worktree isolation: the hard lesson](/docs/patterns/worktree-isolation/).

## Building agents

**Domain agent.** A long-lived agent that owns one area of life or work, such as school, health or a program I run, and keeps its own state and status report. See [Domain agents](/docs/nerve-center/domain-agents/).

**Expert agent.** An agent grounded in a specific body of knowledge (a course's materials, a rulebook) that the main agent must call instead of answering from its own head. See [Expert agents: route by topic](/docs/nerve-center/expert-agents/).

**Fan-out.** Splitting one job across many agents that run in parallel, then combining their results. Every lane should name its model, because an unnamed lane inherits the most expensive default. See [Fleets: parallel build agents](/docs/nerve-center/fleets/).

**Files as state.** The rule that anything an agent needs to remember goes in a file or a table, not in the conversation. Conversations end and get compacted. See [Files as state, not chat memory](/docs/fundamentals/files-as-state/).

**LLM judge.** A model used to grade another model's output against a written criterion. Useful only after you've checked how often it agrees with a human. See [Agent evals](/docs/ai-core-skills/agent-evals/).

**Model routing.** Picking the model per job by what the work can break, not by habit: a small model for rote classification, a top model for review of risky changes. See [Model routing](/docs/patterns/model-routing/).

**Orchestrator.** An agent whose job is to break work down, hand it to other agents and verify what comes back, rather than doing the work itself. In my system that's the CEO agent. See [The CEO agent](/docs/nerve-center/the-ceo-agent/).

**Personal context files.** A small set of files that tell an agent who you are, how you decide, how you write and what your hard rules are. Any agent that drafts or decides for you reads them first. See [Personal context files](/docs/nerve-center/personal-context/).

**Spec.** A written description of what to build and how you'll know it works, written before the code. Agents build to the letter of whatever you give them, so give them a good letter. See [Write the spec before the code](/docs/patterns/specs-before-code/).

## Running an AI organization

**Bridge.** The service in my system that owns every long-lived agent session. Sessions used to run as its child processes, which is why one careless restart once killed every session at once. See [The bridge](/docs/nerve-center/the-bridge/).

**Cockpit.** My web interface: a live pane for every agent session, on desktop and phone. Currently Nerve Center v6. See [The cockpit](/docs/nerve-center/the-cockpit/).

**Cron.** The classic Unix scheduler: run this command at this time, forever. Right for standing jobs with a fixed cadence. See [Schedules as a heartbeat](/docs/patterns/heartbeats/).

**Dead letter.** A message that couldn't be delivered after retries and is set aside, loudly, instead of being dropped. The point is that a failure becomes visible. See [The agent bus](/docs/nerve-center/the-agent-bus/).

**Durable bus.** How agents message each other in my system: every message is written to the database before delivery, retried if it comes back empty, and dead-lettered with an alert if it truly fails. It survives a crash or a timeout, not a full outage of the machine. See [The agent bus](/docs/nerve-center/the-agent-bus/).

**Heartbeat.** A scheduled check-in where an agent looks at its area and writes down what changed. Should cost pennies, so it runs on a cheaper model at low effort. See [Schedules as a heartbeat](/docs/patterns/heartbeats/).

**Loop.** Any future obligation turned into something a machine checks: a cron job, a watcher, a reminder on a date. A promise that lives only in a chat reply is a dropped promise. See [The loops doctrine](/docs/patterns/loops-doctrine/).

**Open loop.** An entry in a ledger of commitments: something promised, waiting on a reply, or due later. Surfaced at session start and in the cockpit. See [Open loops](/docs/nerve-center/open-loops/).

**Second brain.** The file system an AI organization writes to: per-project READMEs, plans and changelogs, a one-line log of every shipped change, and a master changelog generated from all of them. See [The second brain](/docs/nerve-center/the-second-brain/).

**Watcher.** A loop that checks a condition on a cadence ("has the reply arrived?") and fires once when it's true. Every watcher has an expiry so nothing runs forever. See [Watchers](/docs/patterns/watchers/).

## Safety and quality

**Blast radius.** What a change can break if it's wrong. It sets how hard a change gets reviewed: top effort for anything touching safety gates, credentials, money, outbound messages or irreversible actions; a light pass or none for doc fixes. See [Model routing in practice](/docs/nerve-center/model-routing-in-practice/).

**Done gate.** My rule for when a feature counts as shipped: production is serving the exact commit that was merged, and a browser test of the real user journey passes against production. An inconclusive run isn't done. See [Ship to prod](/docs/patterns/ship-to-prod/).

**Drift guard.** A scheduled check that compares what's running against what the source of truth says should be running, and repairs or reports the difference. Example: a running session keeps the model it was born with, so a guard catches sessions left on an old one. See [Model routing in practice](/docs/nerve-center/model-routing-in-practice/).

**Eval.** A repeatable test of an agent's behavior: a task, a definition of success, and a grader. See [Agent evals](/docs/ai-core-skills/agent-evals/).

**Lethal trifecta.** An agent that has private data, sees untrusted content and can send to third parties can leak data without breaking any single rule. My system audits for that combination weekly. See [One door out: the send gate](/docs/safety-and-operations/the-send-gate/).

**Root cause first.** Fix the process that produced a bug before patching the bug: diagnose, fix the process, backfill, add a regression guard, then fix the symptom. See [Root cause first, never bandaids](/docs/patterns/root-cause-first/).

**Send gate.** The single chokepoint every outbound message passes through. Agents can draft anything; nothing goes out without my approval, and the approval is bound to the exact recipients and text. See [One door out: the send gate](/docs/safety-and-operations/the-send-gate/).

**Warden.** The governor for autonomous changes in my system. Autonomy is admitted by how reversible an action is, not by how confident the agent sounds. See [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/).

**Watchdog.** A monitor that assumes everything above it will eventually fail. Measures liveness as work completed, not as a process being up. See [Watchdogs](/docs/safety-and-operations/watchdogs/).

## A note on older terms

The old version of these docs used vocabulary from OpenClaw, a public open-source agent project I tried in early 2026, such as `SOUL.md` and `USER.md` for identity and user-profile files. These docs don't use those terms. The closest thing in my setup is the personal context files above.

**Next:** [FAQ](/docs/reference/faq/)
