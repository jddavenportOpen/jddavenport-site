---
title: "Open-source index"
description: "Every public repo behind these docs, one line each, with the article that explains it."
section: reference
order: 30
updated: 2026-10-05
sources: ["resources.mdx"]
---

Every public repo that relates to these docs, one line each, with the article that explains it. All of them live under [github.com/jddavenportOpen](https://github.com/jddavenportOpen), and each one was checked with a logged-out request on November 22, 2026. My private system stays private because it runs my actual life and work. These are the parts that generalize.

Most are MIT licensed; check each repo's license file before you reuse code. Where a repo's own README quotes an agent count, it was true when that README was written; the durable phrasing is 100+ agents built.

## Production core

The safety, governance and orchestration pieces, extracted from the system that runs every day.

| Repo | What it is | Read |
|---|---|---|
| [warden](https://github.com/jddavenportOpen/warden) | A governor for autonomous agents: autonomy admitted by reversibility, not confidence. Zero dependencies, offline tests | [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/) |
| [claude-bug-squash](https://github.com/jddavenportOpen/claude-bug-squash) | Point Claude Code at a repo and a bug: it fixes in an isolated worktree, proves red to green, gates the fix, and never merges out of the box | [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/) |
| [ethos-gate](https://github.com/jddavenportOpen/ethos-gate) | PreToolUse and Stop hooks that block irreversible or outward-facing actions unless a human approved them | [Hooks](/docs/fundamentals/hooks/) |
| [agent-safety-case-study](https://github.com/jddavenportOpen/agent-safety-case-study) | A capability-versus-risk case study of running an AI organization in production: each capability, its risk, the control, an incident | [The architecture in one page](/docs/nerve-center/architecture/) |
| [claude-code-behavior-specs](https://github.com/jddavenportOpen/claude-code-behavior-specs) | Target-behavior specs for the Claude Code CLI written from production incidents, each with a reproduction and the workaround that shipped | [Lessons from running agents every day](/docs/field-notes/lessons-from-running-agents/) |

## Agent tooling

Things you can drop into your own Claude Code setup.

| Repo | What it is | Read |
|---|---|---|
| [agent-evals-starter](https://github.com/jddavenportOpen/agent-evals-starter) | Learn agent evals by running them: a support agent, 24 tasks, code graders, an LLM judge, controls. Runs offline | [Agent evals](/docs/ai-core-skills/agent-evals/) |
| [mcp-judge](https://github.com/jddavenportOpen/mcp-judge) | An LLM judge that runs as an MCP server, with an eval harness. Results not published | [How to validate your agent eval](/docs/ai-core-skills/agent-evals-validate/) |
| [harnessview](https://github.com/jddavenportOpen/harnessview) | Scan a project's Claude Code setup and see it as one live graph that flags broken wiring | [harnessview](/docs/builds/harnessview/) |
| [deep-research-agent](https://github.com/jddavenportOpen/deep-research-agent) | Iterative, multi-source research with a knowledge-gap loop, a devil's-advocate pass and per-claim verification | [The deep-research agent](/docs/builds/deep-research-agent/) |

## Personal AI OS

| Repo | What it is | Read |
|---|---|---|
| [clawdling](https://github.com/jddavenportOpen/clawdling) | The open, bring-your-own-key personal AI OS engine: chat that acts, a multi-pane Claude Code cockpit, headless workers. AGPL-3.0 | [Clawdling: the open engine](/docs/builds/clawdling/) |
| [openplaud](https://github.com/jddavenportOpen/openplaud) | A free, self-hosted manager for Plaud voice recordings, with your own transcription keys or local Whisper | [Voice notes into the second brain](/docs/builds/plaud-voice-notes/) |

## Apps

| Repo | What it is | Read |
|---|---|---|
| [resume-grader](https://github.com/jddavenportOpen/resume-grader) | One Claude call scores any resume against any job on a six-dimension rubric | [Build your own resume grader](/docs/builds/resume-grader/) |
| [vc-job-board](https://github.com/jddavenportOpen/vc-job-board) | The job board behind the BYU AI Foundry jobs page: venture portfolio roles, twice-daily ingest, resume matching | [The BYU AI Foundry](/docs/builds/byu-ai-foundry/) |
| [recruit-copilot](https://github.com/jddavenportOpen/recruit-copilot) | A job search as a verification problem: one experience bank, tailored resumes proven machine-readable, no auto-apply | [recruit-copilot](/docs/builds/recruit-copilot/) |
| [openbudget](https://github.com/jddavenportOpen/openbudget) | Self-hosted envelope budgeting with read-only bank sync through SimpleFIN | [OpenBudget](/docs/builds/openbudget/) |
| [bookjd](https://github.com/jddavenportOpen/bookjd) | A self-hosted booking app, your own Calendly: real calendar availability, optional payment, both calendars updated | No article yet |
| [jddavenport-site](https://github.com/jddavenportOpen/jddavenport-site) | Source for jddavenport.com | [About these docs](/docs/reference/about-these-docs/) |

## Not listed here

A few public repos are older experiments or side projects that these docs don't cover. Browse the [full list on GitHub](https://github.com/jddavenportOpen?tab=repositories) if you're curious. Anything not on that page isn't public, whatever an older page may have linked.

**Next:** [About these docs](/docs/reference/about-these-docs/)
