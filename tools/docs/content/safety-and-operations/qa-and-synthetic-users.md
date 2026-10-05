---
title: "QA: user stories, Playwright and synthetic users"
description: "QA driven by user stories: browser journeys, accessibility, visual baselines, synthetic users, and a persona tester that never sends."
section: safety-and-operations
group: "Guardrails"
order: 20
updated: 2026-10-05
sources: ["learn/tier-3/h1-qa-agent-self-test.mdx", "learn/tier-3/h3-synthetic-users.mdx"]
---

QA in my system tests what the spec promised, never what the builder claimed. "I fixed it" is a sentence. A green browser run against the acceptance tests, on the deployed product, is evidence. Everything on this page exists to produce the second thing and to keep test traffic from touching anything real.

## What you'll learn

- How user stories become browser journeys
- What the QA agent checks besides "does the page load"
- The bounded fix loop, and where it's not allowed to run
- Synthetic users, and the persona tester I built in October 2026
- The rules that keep tests away from real conversations and real sends

## Stories first

Every product has a list of user stories with acceptance tests: concrete, user-visible behavior that can fail. "Clicking any live agent in any section opens its pane." "The page has no horizontal scroll at phone width." Not "chat should feel fast."

Those stories are the test plan. In June 2026 I wrote 79 of them for the cockpit across 11 categories and tested every one against prod. All the routes rendered. Most acceptance checks passed. Three real bugs came out, and two of them were the same kind: two pages showing different numbers for the same thing because they read from different sources. Neither would have shown up in a unit test. Both were obvious the moment someone looked at the product the way a user would.

If you take one thing from this page: write the stories before you write the tests, and write them in the user's words. See [Write the spec before the code](/docs/patterns/specs-before-code/).

## What the QA agent does

My QA agent turns a product's stories into checks and runs them with Playwright against a preview or production URL. Each project has a small config file listing its routes, its stories and its thresholds. Beyond "the page renders," it covers:

| Check | Catches |
|---|---|
| Browser journeys from stories | Flows that break end to end even though every page loads |
| Phone and desktop viewports | Layouts that only break at one width |
| Accessibility audit | Missing labels, contrast failures, keyboard traps |
| Visual baselines | A grid that silently collapses from four columns to two |
| API contract tests | An endpoint that changed shape under a page that depends on it |
| Flaky-test detection | Tests that pass and fail on the same code, so a red means something |
| Regression history | Whether this failure is new or an old friend |

Checks on what actually renders catch the bugs nobody can describe in advance. In June 2026 a CSS ordering change made a four-column grid render as two, on very wide screens only. The production bundle emitted the two-column rule after the four-column one at equal specificity, so the later rule won. A class-name assertion said the right classes were present and missed it. What caught it was asserting the computed style in a stylesheet built in the same order as production. Test what renders, not what the code says.

Two calibration rules for baselines: capture them from a state you've confirmed is correct, and set the diff threshold per page. Static UI gets a tight threshold. Pages with live data get a looser one, or they fail on every run.

## The bounded fix loop

When a QA run fails, a small loop can try to fix it:

```text
test -> fix -> retest -> (repeat, max 3) -> escalate to a human
```

The cap is the point. Three attempts, then it stops and tells me, instead of grinding on a failure that needs a person. It's meant for preview environments, where a bad fix can be thrown away. Against a live production target it refuses to run the repair half unless that project has explicitly opted in, because a fix agent rewriting code while QA hammers prod is how you get two problems.

## Two kinds of product, two kinds of QA

My system has an architect agent that gates changes to the cockpit and the products built around it: it checks written intent and signs off on architecture. It fires only for those products. Its assumptions (how the cockpit is wired, its conventions) are wrong for anything else, and early on it wrongly gated outside products.

Everything else gets industry-standard QA: Playwright journeys against the stories, visual checks, accessibility. Every build agent working on an outside product gets this in its prompt: don't invoke the architect, QA to industry standard against the user stories.

## Tests never touch real conversations

On June 2, 2026, QA agents doing smoke tests sent test messages into my real CEO session. You can't unsend a message into a conversation. They're still there.

The rules since then, in every build and QA agent's prompt:

- Never spawn, message or post to a live session to test something.
- Read-only checks are fine: load the page, inspect the DOM, call GET endpoints.
- If you must test sending, create a disposable session labeled as one, use it, delete it.

A second fix came later. The QA browser used to sign in with a copy of my own session. In September 2026 it moved to its own QA identity, and the cleanup job that closes test sessions refuses to touch anything not stamped with that identity. Tests can't impersonate me by accident anymore, and a cleanup job can't close one of my real sessions by mistake.

## Synthetic users

A route test asks "does this page work?" A synthetic user asks "can a person get done what they came for?" It's an agent with a persona (a goal, a device, how comfortable they are with tech) that walks a flow the way that person would and reports where it got stuck, not just what errored.

Here's the case for them, from my own store. The first live order was my own test purchase on June 9, 2026. It exposed three bugs in the checkout-to-fulfillment path: a request that asked to expand fields that can't be expanded, the billing address used where the shipping address belonged, and a confirmation flag sent in the wrong part of the request. Then the order failed at the print vendor because no payment method was on file there, while the card had already been charged. Every unit test had passed. The bugs only appeared when someone actually tried to buy something.

That someone was me. Best guess: a synthetic buyer walking the full flow on a test configuration would have found the first three before a real card was involved. That's the job: be the first customer so the first customer doesn't have to be.

Rules I'd give anyone building them:

- **Name the persona specifically.** "First-time buyer on a phone who skims" finds different bugs than "user."
- **Report friction, not just failures.** A page that loads but confuses is a finding.
- **Never let a synthetic user do anything real in production.** No real orders, messages or reviews.
- **Every real-user failure becomes a new persona variant.** The billing-address bug is exactly the kind of scenario a buyer persona should walk every time.

## The persona tester (October 2026)

The newest piece is a tester that uses the product the way I do. Built on October 4, 2026 for the next version of the cockpit, it runs every user story at phone, tablet and desktop widths, plus inside the phone app's shell, against live data. It records what it would have done and never sends a write. Four separate layers make sure of that, and a ledger diff before and after each run proves nothing changed.

Its first run found a real bug: a horizontal overflow on the home screen at every width. The first full round passed 51 of 80 stories. After fixes, the second round passed 59 of 80, with 8 previously failing stories fixed and none regressed. The scoreboard is the point. A story either works at every width or it doesn't, and the number goes up only when the product gets better.

Status, stated plainly: its code reached the main branch on October 5, 2026. Its nightly schedule is written but not switched on, and the cockpit version it tests is still behind flags.

## Where QA ends

QA tells you the product does what the stories say. It doesn't tell you whether an AI feature's answers are any good. That's evaluation, a different discipline with its own method: read real transcripts, build a failure taxonomy, write graders, validate the judges. Start with [Agent evals](/docs/ai-core-skills/agent-evals/).

And QA isn't the last gate. The done gate runs a journey against production after deploy and refuses to call anything done on an inconclusive run. That's covered in [Ship to prod](/docs/patterns/ship-to-prod/).

**Next:** [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/)
