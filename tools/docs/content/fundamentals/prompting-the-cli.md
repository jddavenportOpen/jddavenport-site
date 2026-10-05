---
title: "Prompting Claude Code well"
description: "Goals, not steps. Surgical scope. The context to hand over, and the requests that reliably produce a mess."
section: fundamentals
group: "How it works"
order: 50
updated: 2026-10-05
sources: ["learn/tier-1/05-prompting-well.mdx"]
---

A good request to Claude Code names the problem, the boundary and the proof. What's wrong, what must not change, and what evidence you'll accept as done. Get those three right and you get a small diff you can trust. Leave them out and you get a large diff, a confident "done," and an hour of review.

## Goals, not steps

The most common mistake is writing a procedure instead of an outcome.

**Before:**
> Open `webhook.py`. Find `build_shipment`. Change `order.billing_address` to `order.shipping_address`. Then run the tests.

**After:**
> Orders are shipping to the billing address instead of the shipping address. The bug is somewhere in `webhook.py`. Fix it and show me the tests passing.

The second version is shorter and better. You stated the symptom and the success condition. The agent finds the cause. If your guess about the fix was wrong (maybe the address is set correctly and overwritten later), the first prompt walks the agent into your mistake. The second lets it find the real one.

You also don't get faster by writing the steps. You just did the thinking you were trying to hand off.

## Say what must not change

Agents are eager. Ask for a bug fix in a messy file and you may get the fix, three renamed variables, a new helper and a reformatted import block. Each change is defensible. Together they make a diff you can't review.

Pair every goal with a boundary:

> Fix the address bug in `webhook.py`. Don't refactor. Don't change any function signatures. Leave the other handlers alone.

My own instructions carry a standing version of this: surgical changes, minimal and targeted, and if you want a refactor, ask for a refactor as its own task. A one-line diff is a good diff.

## Ask for the evidence you'll accept

"Done" is the most dangerous word an agent says. Agents will declare victory after writing a file, not after proving it works. So say what proof you want, up front:

- "Run the failing test before and after, and paste both outputs."
- "Show me the query returning the right row."
- "Deploy, then load the page and confirm the new button is there."

In my system "done" for anything user-facing has a machine definition: the production URL is serving the exact commit that was merged, and a browser test walks the real user journey against production and passes. If either check fails or comes back inconclusive, nobody gets to say "it's live." You don't need that machinery to use the idea. You just need to name the evidence in the prompt.

## Point at files instead of pasting

You don't need to paste 200 lines of code into the prompt. The agent can read.

> The retry logic in `scripts/notify.sh` sends duplicate alerts for the same job within 12 hours. Read it and fix the suppression.

"Read it and" saves you the paste and gives the agent the real file instead of your summary of it. Same for logs, configs and docs: name the path.

## Plan first when it spans files

For anything that touches several files or where the approach isn't obvious, separate exploring from editing. Plan mode does exactly that: the agent reads, asks questions and proposes a plan, but makes no edits until you approve it.

```bash
claude --permission-mode plan
```

Or press `Shift+Tab` mid-session until the status bar shows plan mode. Approve the plan, and then the agent builds against it.

Plan mode has overhead, and the official best-practices page says so. For a one-line fix, skip it. For a change where a wrong approach costs an afternoon, it's the cheapest insurance you can buy.

## Tell it to push back

Most people prompt for agreement without meaning to. If you only ever say "do X," you'll get X, even when X is a bad idea.

In May 2026 I put it in my standing instructions in plain words: "I don't want yes-men agents. I want agents that take ownership and push back against me when I'm wrong." The rule that goes with it: if a request will cost time, money, trust or scope, name the cost and propose the better path before executing. Disagree with receipts (a file path, a log line, a number), and concede fast when I push back with a better argument.

You can do this per prompt:

> Add a cache in front of the pricing API. If you think a cache is the wrong fix for slow checkout, say so first and show me why.

And when you spawn other agents, pass the trait along in their prompts. An agent you delegate to will happily build your bad design unless you've told it not to.

## Requests that reliably make a mess

| Request | What you get | Ask instead |
|---|---|---|
| "Clean this up" | Unlimited scope | "Rename these two variables and fix the indentation" |
| "Fix the bug, add tests, update the README, and check for other issues" | Four half-finished tasks in one diff | Four prompts, in order |
| "Can you help me think through how to fix X?" | A plan, no fix | "Fix X" (or plan mode, on purpose) |
| "Make it better" | Whatever the model thinks "better" means | The specific property you want, and how you'll measure it |
| "Done?" | "Yes" | "Show me the output that proves it" |

## When the session goes sideways

If you've corrected the agent twice on the same thing and it's still circling, stop correcting. The context is now full of failed attempts and it keeps tripping on them. Run `/clear`, then write one better prompt that includes what you learned: the real cause, the constraint it kept missing, the evidence you want. A clean session with a sharper prompt almost always beats a long one with a pile of corrections.

> **Tip:** For anything irreversible (a migration, a deploy, a message to a real person), build the pause into the prompt: "Show me the SQL before you run it." One extra round trip is cheap. Undoing a dropped column isn't.

**Next:** [MCP: giving the agent new senses](/docs/fundamentals/mcp/)
