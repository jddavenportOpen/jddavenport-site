---
title: "How to validate your agent eval"
description: "Eight gates that prove your eval measures what you think it measures, with real results."
section: ai-core-skills
group: "#1 Agent evals"
order: 50
updated: 2026-10-05
sources: ["ai-roles-skills-series/day-01-agent-evals"]
---

An eval is a measuring instrument. Before you trust a reading, you check the instrument. The pass bars below are mine, assembled from the practices in Part 2. No source publishes a standard set. Every famous eval failure in Part 2 (the 38% empty agent, the 42% that was really 95%, the 100% exploit agent) was an instrument nobody checked this way.

## The eight validation gates

Don't call your suite done until each of these has a result. The skill in the kit runs them and reports them as this table.

| Gate | How | Pass bar |
|---|---|---|
| Reference solutions | Replay every task's known-good answer through the graders | 100%. Anything less is a broken task or grader, not a bad agent. |
| Do-nothing control | An agent that says "Sorry, I can't help" and calls no tools | Inspect every task it passes. Passing a "nothing changed" database check is expected. Passing the whole task usually means it needs a check on what the agent says. |
| Pushover control | An agent that does whatever the user asks, instantly | Fails every task where obeying breaks the rules. Inspect any pass: either the task allows it or the graders are too loose. |
| Cheating control | Ask AI for the cheapest way to pass each grader without doing the work. Try a few. | No shortcut passes. |
| Judge validation | Your labels vs the judge, on a held-out split | A bar you set before looking (I use 0.8 for both), reported with the test counts |
| Task audit | Could two experts disagree? Is the reference right? Is a grader too strict or too loose? | No task flagged "broken" |
| Human read | You read every failing transcript from the first real run | Every failure seems fair: clear what the agent did wrong |
| Zero-percent check | Any task at 0% across all trials | Read the transcript. Anthropic's rule of thumb is that 0% across many trials (they cite around 100) usually means a broken task. At 3 trials, it's a reason to look, not a verdict. |

## Gate results from the repo

Real output from the repo, 24 tasks x 3 trials each, LLM judges off:

| Agent | pass@1 | Act tasks (do, escalate) | Hold tasks (refuse, ask) |
|---|---|---|---|
| Reference (replays the known-good solution) | 100% | 100% | 100% |
| Do-nothing agent ("Sorry, I can't help with that.") | 25% | 0% | 43% |
| Pushover agent (does whatever it's told, instantly) | 4% | 10% | 0% |
| Claude | Run it: `python -m evals run --agent claude --trials 3` | | |

The number that matters most: the do-nothing agent **passes the database check on 16 of 24 tasks**. That's by design: on every hold task (and two read-only tasks) the right end state is "nothing changed," and a database check can't tell a good refusal from a non-answer. What catches it is the second check on what the agent *said*. The first time I ran these controls, the do-nothing and pushover agents scored 29% and 12%. Reading their passing transcripts found two tasks where only an LLM judge could catch a flat "Yes, we can do that," and judges are skipped offline. I added code checks. That's this gate doing its job.

How to read it:
- **The reference agent must score 100%.** If it doesn't, a task or grader is broken. Anthropic calls this writing a reference solution "that passes all graders."
- **The do-nothing agent** scores zero on act tasks and passes 6 of 14 hold tasks. That's why the suite needs both kinds of task, and why hold tasks need a check on what the agent says, not just on the database.
- **The pushover** fails almost everything, including the happy path, because it refunds before the customer says yes. Together the two controls bracket your suite.
- **Error bars.** With 50 tasks at 70%, the 95% interval is roughly plus or minus 13 points; at 24 tasks it's about 18. So don't read much into a few points between two headline numbers. To compare two versions, compare them task by task on the same tasks (paired differences), and treat repeated trials of one task as related, not independent. That's Anthropic's statistics advice.

## Validating a judge, step by step

A judge is a model. You validate it like one.

1. Hand-label 100 to 200 conversations Pass or Fail for this one criterion. Aim for at least 30 to 50 of each in the test split. (The repo ships 40 labels, about 10 per class in test: enough to learn the workflow, not to trust a judge.)
2. Split: 10 to 20% as few-shot examples in the prompt, 40% dev (tune the prompt), 40% test (touch once).
3. On the test set, treat Fail as the positive class (the judge's job is catching failures) and report two numbers separately, plus how many it answered Unknown:
   - **True positive rate:** of the replies a human marked Fail, how many did the judge catch?
   - **True negative rate:** of the replies a human marked Pass, how many did the judge pass?

Why separately? Because a judge can look 90% accurate while missing most failures. Research on factual-consistency judges found over 95% precision on good summaries but only 30 to 60% recall on bad ones. Shopify's bar was to get close to how often two humans agree (kappa 0.61 vs 0.69).

## Signs you did it wrong

- You never ran a do-nothing agent, so you don't know how many tasks it passes.
- You tune your prompt against the same tasks every day and never hold any back. Your suite has quietly become a validation set.
- The agent can read the grader, the answer key, or earlier trials.
- The judge is the same model as the agent, and nobody checked for self-preference.
- Your judge rates things 1 to 10.
- One judge grades five things at once.
- Nobody on the team has read a transcript this week.
- The judge's labels were written by a model.
- You're celebrating a 3-point gain on 24 tasks.
- Every task is a "should do it" task.
- Trials share an environment, so one run can see the last one's work.
