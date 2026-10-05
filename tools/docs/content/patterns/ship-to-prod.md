---
title: "Ship to prod: review the product, not the diff"
description: "PR, gates, merge, deploy, smoke test prod, then tell the human what to click. Plus the gate that decides when 'done' is actually true."
section: patterns
group: "Shipping"
order: 120
updated: 2026-10-05
sources: ["learn/tier-2/12-ship-to-prod.mdx"]
---

I don't review pull requests. I review the product, in production, by using it. Agents write the code, other agents review it, machines gate it, and the session that built it ships it and tells me what to click. That's been the rule since May 23, 2026, after one too many messages asking me to merge pull requests in order.

This only works if the gates are real and "done" means something a machine can check. Most of this page is about those two things.

## The flow

1. **Branch** off main, in an isolated worktree (see [Worktree isolation](/docs/patterns/worktree-isolation/)).
2. **Open the PR** with what changed and why.
3. **Review by agents**, scaled to what the change can break.
4. **Pass the merge gate.** Red means fix it, not ask me.
5. **Merge.**
6. **Deploy**, and restart anything that runs the merged code.
7. **Prove it's live** with the done gate: the right commit is serving, and a browser journey passes against prod.
8. **Tell me** the URL and one line on what to try.

The orchestrating session owns every step. Merge conflicts, a failing check, a broken build, a deploy that didn't take: all of it gets debugged by the agent, not handed back. The test is simple. Could I say "ship this," walk away, and come back to find it live? If any step waits on me, that step is a gap.

## Who reviews, and how hard

"Agents review PRs" doesn't mean one agent glances at the diff. Every substantive change gets adversarial review from separate agents with different instructions, and one of them is told to try to reject it. A builder never reviews its own work.

But not every change deserves that. On July 31, 2026 I measured where the work volume went and found that every lane ran top-effort review no matter what it touched: a typo fix in a plan document got the same scrutiny as a change to a safety gate. Now review effort scales with blast radius:

| What the change can break | Review |
|---|---|
| Autonomy, safety gates, credentials, anything that sends externally or costs money, anything irreversible, shared rails | Top effort, independent reviewers |
| Normal engineering: a new module, a schema change | High effort |
| Mechanical edits, config, test-only work | Medium |
| Docs, plans, comments | No reviewer. The builder self-checks. |

Honest read: maximum review on everything felt thorough and mostly bought rubber stamps on typo fixes. Match the review to the risk.

## The merge gate

My agent repo doesn't use hosted CI. I turned GitHub Actions off in July 2026 (my words: "you run everything"), and branch protection on a private repo needs a paid GitHub plan, so the gate runs locally on every push: deterministic static checks, the tests for the files that changed, an architecture ratchet, and a migration probe. It grades a fresh checkout of the exact commit being pushed, not whatever happens to be lying around in the working tree.

The gate taught me something the hard way. On July 28, 2026 I flipped it from advisory to blocking. Within hours there were three bypasses, because the test stage failed on any red test, and the tree carried dozens of pre-existing failures owned by other sessions. Every branch was hostage to someone else's debt, and the gate was training agents to turn it off.

So it became a ratchet. Known failures live in a frozen baseline. A new red blocks. A baselined red warns with a count. A baselined test that turns green gets reported for pruning. The gate stays honest without punishing the wrong person.

Two more details that matter:

- **A docs-only push skips the heavy stages.** If every changed file is prose, it exits almost instantly. Don't run a 40-minute test slice for a three-line doc fix.
- **Every bypass is logged in one place, and counted by a command.** The day the ratchet landed, a status note claimed "zero bypasses since the rescope." Two days later an audit found three in the log, one on a commit already in main. Nobody had read the log; the claim came from memory. Now a bypass census reads the log and exits non-zero if it finds any, so the number is counted, never asserted. A gate you can skip silently isn't a gate.

## "Done" is a machine check

"Deployed" is not "working," and "the CI passed" is not "it works in prod." So nothing is called done until a gate says so. The done gate checks two things:

1. **The deployed commit matches.** The prod URL reports the git SHA it's serving, and it has to equal the SHA that was merged.
2. **A real user journey passes.** A Playwright browser runs the journey written for that feature against the live URL and passes.

The exit codes are the contract:

| Exit | Meaning | What the agent does |
|---|---|---|
| 0 | Done. Right SHA, journey passed. | Tell me it's live. |
| 2 | Wrong SHA is serving. | Find the deploy or alias drift. |
| 3 | The journey failed in prod. | Fix it and rerun. |
| 4 | Couldn't discover the SHA. | Fix the probe. |
| 6 | Inconclusive: the test browser was refused a session or rate-limited, so nothing was checked. | Retry. Never report done on this. |

Exit 6 exists because of a specific lie: a run that never got past sign-in "passes" every assertion it never made. Inconclusive is not done.

## Merged is not live

Code reaching main is not the same as code running. If a long-running process loaded the old version, the old version is what's live. During the September kernel-panic fix, the corrected memory breaker landed on main at 18:07, but the running breaker had started at 15:41. For a few hours the fix existed and wasn't running. The last step of shipping is restarting whatever consumes the code, then checking the new behavior in its logs.

## Never test on a live conversation

On June 2, 2026, build and QA agents doing "prod smoke tests" sent test messages into my real CEO session. They're still there. You can't unsend a message into a conversation.

The rule every build and QA agent gets in its prompt: never spawn, message or post to a live session to test something. Read-only checks are fine (load the page, inspect it, call GET endpoints). If you really need to test sending, create a clearly labeled disposable session, use it, and delete it.

## When prod breaks

Fix first, announce second. If the smoke test finds a regression: roll back or hotfix, pass the gates, redeploy, rerun the done gate, then tell me. "Deployed, there's a known issue, working on it" puts me in the position of knowing prod is broken with no timeline. I'd rather hear nothing until it works.

## What I touch

Nothing between "ship this" and the URL. I click around the live product and decide whether it's right. If it isn't, that's a new request, and the loop starts again.

**Next:** [The one-shot pipeline](/docs/patterns/one-shot-pipeline/)
