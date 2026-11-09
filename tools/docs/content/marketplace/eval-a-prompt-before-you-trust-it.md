---
title: "Eval a prompt before you trust it"
description: "Measure an agent or a prompt with real cases and negative controls, then change one thing at a time. Built on foundry-evals and agent-evals-starter."
section: marketplace
group: "Workflows"
order: 60
updated: 2026-11-09
sources: ["https://github.com/ai-foundry-byu/foundry-marketplace/tree/main/plugins/foundry-evals", "https://github.com/jddavenportOpen/agent-evals-starter"]
---

"It worked when I tried it" is one sample. An eval is the same question asked on purpose, many times, with a grader you trust. Without one, every prompt change is a guess.

## What you install

```
claude plugin marketplace add ai-foundry-byu/foundry-marketplace
claude plugin install foundry-evals@ai-foundry
```

New to evals? Run [agent-evals-starter](https://github.com/jddavenportOpen/agent-evals-starter) first. It runs offline and shows every part on a small support agent.

## The steps

1. **Scaffold a suite.** `new-eval` writes cases, a runner, code graders, a yes-or-no judge and negative controls.
2. **Add controls.** A do-nothing agent and a pushover agent should both score badly. If they don't, your graders are broken, not your agent.
3. **Run it and read it.** `run-eval` reports the score with a confidence interval and compares it with the last run.
4. **Audit it.** The `eval-auditor` agent looks for problems that make a score meaningless, like a judge that agrees with everything.
5. **Hill-climb one change at a time.** `hillclimb` changes one thing, re-runs, and keeps the change only if it beats noise.

## Check your work

The do-nothing control fails. Your score has an interval, not just a number. You can name the one change that moved it.

## Limits

A suite's score is not held-out accuracy unless you keep a test split and score it separately. `new-eval` is labeled beta. The full skill series starts at [Agent evals](/docs/ai-core-skills/agent-evals/).
