---
title: "Fleets: parallel build agents"
description: "Many build agents at once: a worktree supervisor, a queue drainer, off-plan models for fleet work, and the orphan-process lesson."
section: nerve-center
group: "Orchestration"
order: 60
updated: 2026-10-05
sources: ["learn/tier-3/b5-fleet-of-claudes.mdx", "learn/tier-3/b6-infinity-fleet.mdx"]
---

A fleet is several Claude Code build agents working on the same codebase at the same time, each in its own git worktree, each on its own branch. Starting them is easy. The hard part is keeping them from trampling each other, keeping them on the right model, and making sure that when one stops, it actually stops.

## What you'll learn

- The worktree rule, and the incident that made it a rule
- How the fleet supervisor and the queue drainer split the work
- Why fleet work runs off the main plans by default
- The orphan-process bug, and why "kill the child" isn't enough

## The trampling problem

Two agents, one checkout. Agent A is editing a page on branch `org-chart-v2`. Agent B runs `git checkout chat-resume-fix` in the same folder. Agent A's next edit lands on Agent B's branch, and A has no idea.

That exact thing happened to me on May 22. Recovery took a cherry-pick, a dig through the reflog and about fifteen minutes. The same class came back in June. So it stopped being a convention and became a rule with machines behind it:

- **Any background agent that may touch git gets its own worktree.** No exceptions.
- **A preflight refuses to guess.** A worker's first action confirms which repo and worktree it's in, and exits with an error if it can't tell. Blind is a failure, never a pass.
- **Nested repos need their own worktrees.** My cockpit is a separate repo inside the agent repo. A worktree of the outer repo doesn't isolate the inner one, so cockpit work goes through a script that mints a per-agent worktree of the cockpit repo.
- **The shared checkout refuses commits.** A pre-commit hook blocks commits made directly in the shared folder, and a watchdog puts a drifted shared checkout back on its branch.

[Worktree isolation](/docs/patterns/worktree-isolation/) has the general pattern.

## The supervisor: one worktree, one tmux session, one branch

The fleet supervisor landed on April 29. For each task it:

1. **Spawns** a worker in a fresh worktree on a branch named for the run, inside a tmux session, with a plan file the agent re-reads every loop.
2. **Monitors** it by run id.
3. **Reaps** it when the session ends: reads the structured output, marks the task done or failed, cleans up the worktree.
4. **Reports** the batch result back to whoever asked.

It never merges. Workers land work on branches; whether a branch ships is the job of review and the merge gate.

Then it sat almost unused for two months. Only a handful of worktree-agent branches merged before June, when the fleet finally got used at scale. Building a capability and adopting it are different events. Plan for both.

## The drainer: a job board for workers

The supervisor needed an orchestrator session to drive it. The queue drainer, live from June 8, removed that:

```text
producer --enqueue--> task table (Postgres)
                          |
         drainer polls, claims one task (optimistic update:
         if another worker claimed it first, skip it)
                          |
         mint a run id -> spawn worker in a worktree
                          |
         reap -> done | failed -> retry with backoff
                                -> at the cap: park + tell me once
```

Each drainer has its own concurrency cap and idles on an empty queue. Capacity is the sum of attached workers, so another machine can join by running a worker. The old docs called this "infinity." It isn't. Each worker has a plan and a cap. There's just no central ceiling.

> **Warning:** A worker that claims tasks but can't run them is a black hole. In July a drainer on my second machine had broken Claude credentials. It kept claiming tasks and closing them instantly as phantom done or failed results, and a liveness job kept reviving it every time I killed it. Liveness is work completed, not "the process is up."

## Fleet work runs off the main plans

Build fleets are high volume and mostly mechanical, so by default they run on an offload tier (a Kimi coding model) instead of my Claude plans. Two things went wrong with that, and both were configuration, not code:

- **A pin that undid the default.** A July 26 audit found one config value on the drainer was forcing nearly all fleet tasks back onto the Claude plans. Removing one line moved the work back where it belonged.
- **A provider changed its error wording.** In September the offload provider's quota error text drifted, and the drainer stopped recognizing it, so tasks died instead of rerouting. Quota detection is now structural (the status code plus the provider), with tests that pin the real error text.

The rule I hold now: when a plan or provider is out of quota, it's closed. Nothing spins up on it until it's back; work rolls to another plan.

The same thinking applies to workflow fan-out inside a session. An unannotated fan-out lane inherits the most expensive model at top effort, so every lane has to name its tier out loud. More in [Model routing in practice](/docs/nerve-center/model-routing-in-practice/).

## The orphan lesson

This is the one I'd tattoo on a new builder.

A headless Claude Code run isn't one process. It starts helper processes too, like the MCP servers that give it tools. When a caller times out and kills only the direct child, the helpers get orphaned and keep running.

In late July an audit found a timed-out Telegram turn that had kept working after its caller gave up: about 9.5 million tokens of work volume (list-price equivalent) on an answer nobody would read. In September it got worse. A string of kernel panics on my main machine traced partly to thousands of orphaned helper processes from timed-out headless runs, piling up memory until the system's compressor filled and the watchdog panicked the kernel.

The first fix patched one call site. The machine panicked again eight hours later, because the shared client every agent used, and about twenty other call sites, had the same shape. The real fix:

1. A shared spawn helper that starts every headless run in its own process group and kills the whole group on timeout, on any exception, and after a clean exit too.
2. The shared client and the launch paths that mattered moved onto it.
3. A lint in the merge gate that refuses any new code that spawns Claude Code without it.

I wrote this one up as a public behavior spec with a runnable reproduction: [claude-code-behavior-specs](https://github.com/jddavenportOpen/claude-code-behavior-specs), SPEC-001.

The related bug: a long-running daemon that started before your fix is still running your bug. In September a fleet drainer on a second machine was found running code weeks behind its own fixes while every file-level check read green. Restart what you fix, and check the process start time against the code it loaded.

## If you build a fleet

1. Worktree per worker, enforced by a hook, not a reminder.
2. Never let a worker merge. Branches in, review and a gate out.
3. Make claim-without-spawn impossible to miss.
4. Put mechanical fleet work on the cheapest model that can do it, and audit the config that picks it.
5. Kill process groups, not processes.

Public versions: [clawd-agent-os](https://github.com/jddavenportOpen/clawd-agent-os) has the worktree-isolated fleet and a location-agnostic queue drainer; [orchestra-agents](https://github.com/jddavenportOpen/orchestra-agents) has a bounded-concurrency fleet with per-run cost tracking; [fleetwright](https://github.com/jddavenportOpen/fleetwright) packages a fleet engine with a cockpit.

**Next:** [Model routing in practice](/docs/nerve-center/model-routing-in-practice/)
