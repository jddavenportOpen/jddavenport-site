---
title: "0 to 1 product build"
description: "Go from an idea to a shipped app with agents, one stage at a time, with a judge at each gate. Built on foundry-sdlc."
section: marketplace
group: "Workflows"
order: 10
updated: 2026-11-09
sources: ["https://github.com/ai-foundry-byu/foundry-marketplace/blob/main/SDLC.md"]
---

Agents build fast. They also build the wrong thing fast. This workflow makes them write down what "right" means first, then checks the build against it. It is the Foundry SDLC, the same eight stages our student builders run on client work.

## What you install

```
claude plugin marketplace add ai-foundry-byu/foundry-marketplace
claude plugin install foundry-sdlc@ai-foundry
claude plugin install foundry-guardrails@ai-foundry
claude plugin install foundry-qa@ai-foundry
```

## The steps

1. **Scaffold.** Say "start a new project". The `new-project` skill writes the standard files: README, REQUIREMENTS, DECISIONS, PRD, WORKPLAN.
2. **Requirements.** Paste every ask as the client said it. `gather-requirements` gives each one an id (R-01) and keeps the client's words.
3. **PRD and stories.** `write-prd` turns requirements into user stories with numbered, checkable criteria. Then the `prd-critic` agent reviews it cold. Fix what it finds before you go on.
4. **Workplan.** `write-workplan` turns stories into a task table with owners and dependencies.
5. **Build.** `parallel-lanes` runs independent tasks as separate agents, one git worktree each. See [Parallel lanes with worktrees](/docs/marketplace/parallel-lanes-with-worktrees/).
6. **Code QA, then visual QA.** Tests first. Then the `story-verifier` agent checks each story on the running app, as a user would.
7. **Ship.** The `ship` skill re-runs every gate on the commit you are shipping. See [Ship with a done gate](/docs/marketplace/ship-with-a-done-gate/).
8. **Feedback.** Every bug report goes through `bug-to-story`, so it becomes a story criterion and a failing test before anyone fixes it.

Lost? Ask "where are we on this project?" The `sdlc` skill reads your files and names the stage you are in.

## Check your work

You are done when every story in PRD.md has a story-verifier PASS on the commit you shipped. A green test suite alone is not done.

## Limits

`ship` is labeled beta. Projects scaffolded before the current release keep an old helper script; the marketplace README says how to refresh it. The long version of why specs come first is in [Specs before code](/docs/patterns/specs-before-code/).
