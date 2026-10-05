---
title: "Open-source index"
description: "Every public repo behind these docs, one line each, with the article that explains it."
section: reference
order: 30
updated: 2026-10-05
sources: ["resources.mdx"]
---

Every public repo that relates to these docs, one line each, with the article that explains it. All of them live under [github.com/jddavenportOpen](https://github.com/jddavenportOpen), and each one was checked with a logged-out request on October 5, 2026. My private system stays private because it runs my actual life and work. These are the parts that generalize.

Most are MIT licensed; check each repo's license file before you reuse code. Where a repo's own README quotes an agent count, it was true when that README was written; the durable phrasing is 30+ agents in daily production, 100+ built over time.

## Production core

The safety, governance and orchestration pieces, extracted from the system that runs every day.

| Repo | What it is | Read |
|---|---|---|
| [warden](https://github.com/jddavenportOpen/warden) | A governor for autonomous agents: autonomy admitted by reversibility, not confidence. Zero dependencies, offline tests | [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/) |
| [claude-bug-squash](https://github.com/jddavenportOpen/claude-bug-squash) | Point Claude Code at a repo and a bug: it fixes in an isolated worktree, proves red to green, gates the fix, and never merges out of the box | [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/) |
| [ethos-gate](https://github.com/jddavenportOpen/ethos-gate) | PreToolUse and Stop hooks that block irreversible or outward-facing actions unless a human approved them | [Hooks](/docs/fundamentals/hooks/) |
| [claude-deploy-kit](https://github.com/jddavenportOpen/claude-deploy-kit) | Enterprise controls for Claude agents: a policy chokepoint, a destructive-command deny hook, an eval gate, a redacting audit log, pluggable secrets | [One door out: the send gate](/docs/safety-and-operations/the-send-gate/) |
| [orchestra-agents](https://github.com/jddavenportOpen/orchestra-agents) | A small Python library for driving many Claude agents in parallel with guardrails and evals: fan-out, a durable bus, circuit breakers | [Orchestration: delegate down, verify up](/docs/patterns/orchestration/) |
| [clawd-agent-os](https://github.com/jddavenportOpen/clawd-agent-os) | Tiered agent hierarchies with worktree-isolated fleets, a durable agent bus and one model registry as the source of truth | [Fleets: parallel build agents](/docs/nerve-center/fleets/) |
| [hub-watchdog](https://github.com/jddavenportOpen/hub-watchdog) | A two-strike uptime watchdog that runs on GitHub Actions, so it keeps working when the machine it watches is down | [Watchdogs](/docs/safety-and-operations/watchdogs/) |
| [agent-safety-case-study](https://github.com/jddavenportOpen/agent-safety-case-study) | A capability-versus-risk case study of running an AI organization in production: each capability, its risk, the control, an incident | [The architecture in one page](/docs/nerve-center/architecture/) |
| [claude-code-behavior-specs](https://github.com/jddavenportOpen/claude-code-behavior-specs) | Target-behavior specs for the Claude Code CLI written from production incidents, each with a reproduction and the workaround that shipped | [Lessons from running agents every day](/docs/field-notes/lessons-from-running-agents/) |
| [nerve-center-showcase](https://github.com/jddavenportOpen/nerve-center-showcase) | The capabilities page my system regenerates from live state every day ([live page](https://nerve-center-showcase.vercel.app)) | [The system documents itself](/docs/safety-and-operations/ground-truth/) |

## Agent tooling

Things you can drop into your own Claude Code setup.

| Repo | What it is | Read |
|---|---|---|
| [agent-evals-starter](https://github.com/jddavenportOpen/agent-evals-starter) | Learn agent evals by running them: a support agent, 24 tasks, code graders, an LLM judge, controls. Runs offline | [Agent evals](/docs/ai-core-skills/agent-evals/) |
| [mcp-judge](https://github.com/jddavenportOpen/mcp-judge) | A calibrated multi-persona LLM judge as an MCP server, with an eval harness that proves the calibration | [How to validate your agent eval](/docs/ai-core-skills/agent-evals-validate/) |
| [context-kit](https://github.com/jddavenportOpen/context-kit) | Four personal-context templates plus five Claude Code skills, so an agent starts with real context about you. One-command install | [Personal context files](/docs/nerve-center/personal-context/) |
| [harnessview](https://github.com/jddavenportOpen/harnessview) | Scan a project's Claude Code setup and see it as one live graph that flags broken wiring | [harnessview](/docs/builds/harnessview/) |
| [deep-research-agent](https://github.com/jddavenportOpen/deep-research-agent) | Iterative, multi-source research with a knowledge-gap loop, a devil's-advocate pass and per-claim verification | [The deep-research agent](/docs/builds/deep-research-agent/) |
| [mastery-engine](https://github.com/jddavenportOpen/mastery-engine) | Point it at a codebase and get a curriculum about your actual code, with every claim verified against disk | No article yet |

## Personal AI OS

| Repo | What it is | Read |
|---|---|---|
| [clawdling](https://github.com/jddavenportOpen/clawdling) | The open, bring-your-own-key personal AI OS engine: chat that acts, a multi-pane Claude Code cockpit, headless workers. AGPL-3.0 | [Clawdling: the open engine](/docs/builds/clawdling/) |
| [fleetwright](https://github.com/jddavenportOpen/fleetwright) | A self-hosted agent operations OS: a persistent chief of staff that commands a fleet of agents | [The CEO agent](/docs/nerve-center/the-ceo-agent/) |
| [openplaud](https://github.com/jddavenportOpen/openplaud) | A free, self-hosted manager for Plaud voice recordings, with your own transcription keys or local Whisper | [Voice notes into the second brain](/docs/builds/plaud-voice-notes/) |

## Apps

| Repo | What it is | Read |
|---|---|---|
| [resume-grader](https://github.com/jddavenportOpen/resume-grader) | One Claude call scores any resume against any job on a six-dimension rubric | [Build your own resume grader](/docs/builds/resume-grader/) |
| [vc-job-board](https://github.com/jddavenportOpen/vc-job-board) | The job board behind the BYU AI Foundry jobs page: venture portfolio roles, twice-daily ingest, resume matching | [The BYU AI Foundry](/docs/builds/byu-ai-foundry/) |
| [recruit-copilot](https://github.com/jddavenportOpen/recruit-copilot) | A job search as a verification problem: one experience bank, tailored resumes proven machine-readable, no auto-apply | [recruit-copilot](/docs/builds/recruit-copilot/) |
| [openbudget](https://github.com/jddavenportOpen/openbudget) | Self-hosted envelope budgeting with read-only bank sync through SimpleFIN | [OpenBudget](/docs/builds/openbudget/) |
| [voiceclaw](https://github.com/jddavenportOpen/voiceclaw) | A voice agent you call by phone, on Vapi, Claude and Deepgram. Archived | [VoiceClaw: a phone agent](/docs/builds/voiceclaw/) |
| [bookjd](https://github.com/jddavenportOpen/bookjd) | A self-hosted booking app, your own Calendly: real calendar availability, optional payment, both calendars updated | No article yet |
| [jddavenport-site](https://github.com/jddavenportOpen/jddavenport-site) | Source for jddavenport.com | [About these docs](/docs/reference/about-these-docs/) |

## Not listed here

A few public repos are older experiments or side projects that these docs don't cover. Browse the [full list on GitHub](https://github.com/jddavenportOpen?tab=repositories) if you're curious. Anything not on that page isn't public, whatever an older page may have linked.

**Next:** [About these docs](/docs/reference/about-these-docs/)
