---
title: "Ship with a done gate"
description: "Never call a feature done until production serves the commit you meant and a browser has walked the user's path on it. Built on foundry-qa."
section: marketplace
group: "Workflows"
order: 30
updated: 2026-11-09
sources: ["https://github.com/ai-foundry-byu/foundry-marketplace/tree/main/plugins/foundry-qa", "https://github.com/ai-foundry-byu/foundry-marketplace/tree/main/plugins/foundry-guardrails"]
---

"It's live" is the most expensive sentence an agent says. It is often wrong in one of two ways: production is serving an older build, or the build is right and the user's path through it is broken. A done gate checks both before anyone says the sentence.

## What you install

```
claude plugin marketplace add ai-foundry-byu/foundry-marketplace
claude plugin install foundry-qa@ai-foundry
claude plugin install foundry-guardrails@ai-foundry
```

You also need Playwright for the browser checks: `pip install playwright` then `python3 -m playwright install chromium`.

## The steps

1. **Write the journey.** One short file per feature: open this page, do this, expect that. Use the story's own acceptance criteria.
2. **Deploy.** Your normal way.
3. **Run the done gate.** The `done-gate` skill confirms the deployed build serves the commit you expect, then runs the journey in a real browser on desktop, phone and tablet sizes.
4. **Only then say done.** `verify-before-done` (a guardrails hook) blocks an agent from stopping after a code change with no test run since the change.
5. **Before a risky change,** run `regression-check` to list every consumer of what you changed.

## Check your work

The gate prints PASS for the commit you shipped. INCONCLUSIVE is not PASS: it means the browser never got to check anything, for example a sign-in wall.

## Limits

Signed-in pages need a test-only sign-in route that is off in production. Each browser check runs its own Chromium, so on a laptop run a few at a time. The reasoning is in [Ship to prod](/docs/patterns/ship-to-prod/).
