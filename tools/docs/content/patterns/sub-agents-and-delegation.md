---
title: "Sub-agents and delegation"
description: "When to delegate, foreground vs background, what the prompt must carry, timeouts that actually kill, and naming the model tier on every lane."
section: patterns
group: "Agents"
order: 30
updated: 2026-10-05
sources: ["learn/tier-2/02-spawning-sub-agents.mdx", "frameworks/delegation-framework.mdx"]
---

Delegate work that needs judgment and would flood your own context. Do quick things yourself. Call a CLI when the job is a command. And when you do delegate, the prompt is the whole world the sub-agent gets, so it has to carry everything: the goal, the output, the boundaries and the model tier.

A sub-agent in Claude Code is a separate agent with its own context window, its own tools and its own instructions. It works, then hands back a result. That separation is the point: the parent stays focused, and the child can read fifty files without filling the parent's window.

## What you'll learn

- A quick test for delegate, do it yourself, or run a command
- How foreground and background work in Claude Code today
- The six things every sub-agent prompt carries
- Why the model tier must be named on every lane
- Timeouts that kill, and concurrency sized to the machine

## Delegate, do it yourself, or run a command

| The task | Do this | Why |
|---|---|---|
| Read a file, check git status, look up a value | Do it yourself | Spawning costs more than doing |
| A known command with a known output (`pytest`, a CLI agent) | Run it with Bash | No judgment needed, so no agent needed |
| Many steps, needs judgment, or reads a lot | Delegate | Keeps your context for decisions |
| Several independent pieces | Delegate in parallel | Wall-clock time drops to the slowest piece |
| An existing specialist covers it | Call the specialist | See [inventory before you build](/docs/patterns/anatomy-of-an-agent/) |

A heuristic that holds up: if you'd have to write a paragraph of instructions, use a sub-agent. If the instruction is "run this and tell me the output," use Bash. Spawning an agent to run `python3.12 -m agents.researcher.main "query"` is paying a manager to press a button.

## Foreground and background

Claude Code runs sub-agents two ways. A foreground sub-agent blocks the parent until it finishes. A background sub-agent runs while the parent keeps working, and its result arrives later as a notification.

Which one you get has changed over time, so check the [sub-agents docs](https://code.claude.com/docs/en/sub-agents) for your version. As of October 2026, an interactive session runs spawned sub-agents in the background by default (Claude Code calls this fork mode). With fork mode off, Claude runs them in the background unless it needs the result before its next step. A definition can force background with `background: true` in its front matter.

The decision rule for your own designs is the same either way: does the parent need this result before its next action? If yes, it's a dependency, so wait for it. If no, let it run and verify when it lands.

Two practical differences. Background sub-agents get a smaller built-in tool set. And their permission prompts surface in your main session, so a background agent that needs approval is waiting on you, not stuck.

## What every sub-agent prompt carries

The child starts with none of your conversation. Six things go in every prompt I write:

1. **The goal, specific.** Not "help with the PR." "Implement `formatDate` in `src/lib/utils.ts` per the spec below, run `npm test`, report pass or fail."
2. **The output contract.** A file path, a JSON shape, a verdict line. If you don't say what comes back, you'll get an essay.
3. **The minimum context.** File paths, constraints, acceptance criteria. Not your memory file, not your calendar, not the last hour of chat. A coding agent doesn't need to know about your week, and an agent can't leak what it never received.
4. **The worktree line,** when it may touch git: "You are in a worktree. Confirm with `pwd`. Don't touch other branches in the parent checkout." See [Worktree isolation](/docs/patterns/worktree-isolation/).
5. **The no-live-sessions line,** when it may touch anything persistent: "Do not spawn or post to any live session. Use read-only checks or a disposable session you delete after." In June 2026 build and QA agents smoke-tested features by sending "[QA smoke]" messages into my real CEO chat. Those messages are still there. Chat history doesn't have an undo.
6. **The push-back line.** "If this design is wrong, say so with evidence before building it." I don't want sub-agents that execute a bad plan politely. In my system this is injected into every agent definition by a script, so it doesn't depend on me remembering.

Here's a compact prompt with all six:

```text
Goal: add rate limiting to POST /api/login: 5 attempts per IP per minute.
Files: src/app/api/login/route.ts, src/lib/ratelimit.ts (create it).
Done means: npm test passes, including 3 new tests (under limit, at limit,
window reset). Return: the files changed, the test output, any blockers.
You are in a worktree; confirm with pwd and stay in it.
Do not post to any live session. Read-only checks only.
If rate limiting belongs somewhere other than this route, say so first.
```

## Name the model tier on every lane

Every sub-agent runs on some model at some effort. If you don't choose, something chooses for you. In Claude Code the per-invocation `model` wins, then the definition's `model` front matter, then an environment override, then the main conversation's model. Silence usually means "same as the parent," and the parent is usually the most expensive thing you run.

That's not hypothetical. In July 2026 I measured one model doing over 90% of my work volume (list-price equivalent) at top effort, because every lane inherited it. In September, fan-out children alone were about half of all work volume. Nobody chose that. Silence chose it.

So tier both dials by what the work can break:

| Blast radius | Model and effort |
|---|---|
| Autonomy, safety gates, credentials, anything that moves money or sends externally, anything irreversible, a rail every producer rides | Top tier, top effort, plus an independent reviewer |
| Normal engineering: a new module, a schema change | Build tier, high effort |
| Mechanical edits, config, formatting, test-only work | Smaller model, medium or low effort |
| Doc fixes and receipt text | No reviewer agent at all; the builder self-checks |

A deliberate `model: opus` on a lane that needs it is fine. What I lint for is the lane with no tier named, because that one inherits the most expensive answer by accident. [Model routing](/docs/patterns/model-routing/) covers the framework.

## Timeouts must kill, not just stop waiting

Every delegated job needs a deadline, and the deadline has to end the work, not just the wait.

The September 2026 audit found this the hard way. My message bus gave a synchronous call 240 seconds, then gave up. Giving up meant the caller stopped listening. It did not stop the headless child, which kept running at top effort, finished, and delivered an answer to nobody. Three timeouts dead-lettered the message while the orphans kept going.

The rules that came out of it:

- A timeout cancels the child, and the cancel escalates to a hard kill. The child also carries its own wall-clock budget, so it dies on schedule even if the cancel gets lost.
- A timed-out result is a failure, loudly, never an empty string that looks like a real empty answer.
- Retry with a smaller task or better instructions, not the same prompt with a longer clock.

## Concurrency is a memory budget

The old advice was "cap at five concurrent agents." A fixed number is wrong in both directions. My fleet's queue drainer sizes its worker count from the memory actually available on the machine it runs on, and falls back to a small default only if it can't measure. A machine with headroom runs more; a tight one throttles itself.

I learned why the hard way in September, when browser swarms plus a large local model drove a run of kernel panics. Parallelism isn't free. It's paid for in RAM, and the machine doesn't negotiate.

## Verify what comes back

"The sub-agent said it worked" isn't verification. Run the tests. Open the file. Check the URL. The sub-agent's summary is a claim, and claims from a context you can't see are exactly where plausible-but-wrong work hides. [Orchestration](/docs/patterns/orchestration/) covers the verification loop in full.

**Next:** [Worktree isolation: the hard lesson](/docs/patterns/worktree-isolation/)
