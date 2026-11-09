---
title: "Parallel lanes with worktrees"
description: "Run several coding agents on one repo at once without them overwriting each other. One git worktree per lane, and a guard that keeps each lane in its own tree."
section: marketplace
group: "Workflows"
order: 20
updated: 2026-11-09
sources: ["https://github.com/ai-foundry-byu/foundry-marketplace/tree/main/plugins/foundry-sdlc", "https://github.com/ai-foundry-byu/foundry-marketplace/tree/main/plugins/foundry-guardrails"]
---

Two agents in one checkout will eventually wreck each other. One switches branches while the other is mid-edit, and the second agent's work lands on the wrong branch or vanishes. The fix is boring: give each agent its own git worktree.

## What you install

```
claude plugin marketplace add ai-foundry-byu/foundry-marketplace
claude plugin install foundry-sdlc@ai-foundry
claude plugin install foundry-guardrails@ai-foundry
```

`parallel-lanes` (in foundry-sdlc) plans and runs the lanes. `worktree-guard` (in foundry-guardrails) blocks a lane from editing the main checkout while lanes are active.

## The steps

1. **Start from a workplan.** Lanes need tasks with clear owners and no shared files. If two tasks touch the same file, they are one lane.
2. **Say "run the workplan in parallel lanes".** Each lane is a subagent with worktree isolation, on its own branch.
3. **Let each lane finish with its own tests.** A lane that cannot pass its own tests does not merge.
4. **Merge one lane at a time** into main, and re-run the tests after each merge. Conflicts surface here, one at a time, instead of all at once.

## Check your work

`git worktree list` shows one tree per lane while they run and only the main tree after. Every lane branch is merged or deliberately closed. Nothing is left half-merged.

## Limits

The guard protects lanes that run as subagents with worktree isolation. It does not stop a shell write, or one lane editing another lane's worktree. For running many agents on one app day to day, the Foundry's [agent-team-kit](https://github.com/ai-foundry-byu/agent-team-kit) adds port assignment and a schema lock (it has no license file yet). The pattern itself is in [Worktree isolation](/docs/patterns/worktree-isolation/).
