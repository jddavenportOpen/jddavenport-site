---
title: "Auto bug-squash and the Warden"
description: "Gated self-repair: fixes in isolated worktrees with red-to-green proof, and a governor that admits autonomy by reversibility, not confidence."
section: safety-and-operations
group: "Guardrails"
order: 30
updated: 2026-10-05
sources: ["learn/tier-3/h2-self-healer-evolution.mdx"]
---

The [self-healing loop](/docs/patterns/self-healing-loop/) from June 2026 grew into two things: a gated bug-squash pipeline that fixes code, and a governor called the Warden that decides what any autonomous agent may do unattended. Both are built on one idea: a model's confidence is not permission. Proof is, and reversibility is.

This page is mostly about what went wrong on the way, because that's where the design came from.

## The bug-squash pipeline

A bug comes in as a ticket, from a detector or a report. From there, every layer re-checks the actual diff, never the fixing agent's description of it:

1. **Triage.** Classify severity, try to reproduce, locate the files, assign a risk tier. Anything touching a never-touch path is never automatic.
2. **Fix in an isolated worktree.** A scoped agent edits a throwaway checkout, never the real one.
3. **Red-to-green proof.** A reproduction must fail before the fix and pass after. No proof, no automatic path.
4. **Blast-radius caps.** A small number of files and lines, no new dependencies, no schema changes, no CI or infrastructure edits.
5. **Never-touch list.** Auth, secrets, payments, migrations, deploys and the safety rails themselves. A hit is a hard stop and goes to a human.
6. **Three-seat adversarial review.** Product, safety and architecture reviewers, each read-only. Any one of them can veto with a cited reason.
7. **Shadow mode.** Even after all that, it records what it would merge and stops.
8. **A daily rate limit**, so one misclassified ticket can't fan out into a string of bad merges.
9. **An explicit arm switch** before any real merge happens.

The public version is [claude-bug-squash](https://github.com/jddavenportOpen/claude-bug-squash). Out of the box it proposes and gates, but it never merges. You turn merging on deliberately, after you trust what you've seen.

## What went wrong on the way

### The safety layers were partly theater

On August 1, 2026 a safety review of my internal pipeline found that its layers looked better on paper than in code. One merge path, driven by a scheduled job, ignored shadow mode entirely. The "three of three reviewers approved" quorum passed with one approval. The receipt that said "(3/3 approved)" was a hardcoded string. The fixer agent ran with my full environment, so production credentials were one `cat` away from an agent that could merge unattended. Thirteen audit rows recorded things that hadn't happened.

I stepped the whole rail back to shadow mode that day, gave the fixer an allowlisted environment with the credentials withheld, put the CI scripts and agent config on the never-merge list, fixed the quorum and the verdict parser, and added a lint that flags any field in the outcome log that never changes value. That last one matters most, and the next section is why.

### The gates were there and empty

In mid-August I traced why almost nothing was eligible for automatic fixing. Out of 410 tickets, exactly one had qualified. The chain was simple once I looked: tickets didn't carry the failing test, so reproduction was never attempted, so 65 of the 65 most recent tickets had no reproduction result at all, so everything fell through to "needs a human."

Flipping the autonomy switch would have changed nothing. The fix was to make detectors attest what they observed and where to re-read it, and to have triage re-verify against live state and form its own verdict. A reproduction the fixer reports about itself is a fabricated receipt with extra steps.

An audit two weeks earlier had already said the same thing about the review side: three of the five signals the outcome log tracked never changed. The reviewer-approval field was always empty, the veto field was always empty, and the re-verify step never reopened anything. They existed in code and never fired. The pipeline stayed in shadow mode until August 18, when the reproduction chain was fixed and I turned merging back on. The daily merge cap is small, and its expiry is a step down, not a cliff: an earlier version would have jumped from one merge a day to eight at midnight on a calendar date, with no approval and nothing in any log. An autonomy increase should never be triggered by the calendar.

### The scoreboard counted the weather

By early September the ledger showed 123 tickets marked production-verified, and I was ready to quote "more than a hundred fixes." Before I did, a review split them by how they were actually resolved:

| Resolution | Count |
|---|---|
| Real fixes | 88 (70 shipped as a PR) |
| Condition cleared on its own (a job that recovered by itself) | 28 |
| No resolution recorded | 6 |
| False alarm | 1 |

A job that comes back on its own isn't a bug fix. The weekly report now counts what was built separately from what merely cleared. When the split went in, the previous seven days showed nine closes and zero real fixes. That's a worse number and a truer one.

Honest read: if I hadn't split that metric, I'd have published it. Measure what you built, not what went away.

## The Warden

The Warden is a governor for autonomous agents. Its rule: **autonomy is admitted by reversibility, not by confidence.** An agent may act unattended only if the action can be undone and its success can be observed. Otherwise a human decides.

The public library is [warden](https://github.com/jddavenportOpen/warden). Its gates run in a fixed order, deterministic ones first:

| Order | Gate | Can a model override it? |
|---|---|---|
| 1 | Protected targets are excluded | No |
| 2 | The action must have an executable undo | No |
| 3 | Has this type of fix been demoted for failing before? | No, it fails closed |
| 4 | A judge scores it against your written constitution | It can only veto |
| 5 | Execute, then watch the original alert signal | |
| 6 | If the signal never goes green, the undo runs by itself | |

Three choices worth copying:

- **The judge can only downgrade.** There's no path where a model talks an action past the first three gates. If a model can say yes, the model is on the critical path for safety.
- **Undo is a function, not a sentence.** A rollback plan you can't execute is a promise.
- **Success is the original signal going green**, not "the command returned 200." If a fix type gets rolled back twice on the same target, it demotes itself to human approval and stops asking.

The README is honest about its limits, and I'd point you there: it checks that an undo exists, not that it works, and it governs actions, not prompts.

### What the Warden did in my system

- **August 15, 2026:** it started adopting new models automatically, behind gates: same family only, never a downgrade, a live probe, a quality benchmark, and automatic rollback. That still runs nightly.
- **August 16:** its first fully autonomous build landed on main after passing the merge gate.
- **Early September:** it refused its own authority on a blast-radius check and handed the call to a human instead of acting. That's the behavior you want from a governor: when in doubt, it shrinks its own authority.
- **September 11:** I turned the continuous Warden lanes off. By its own metric, it had landed two unattended changes in the previous week, which wasn't worth the work volume the lanes consumed around the clock. A resume script had also quietly switched it back on after a pause. That second problem led to the kill ledger described in [The loops doctrine](/docs/patterns/loops-doctrine/).

What runs now is a weekly Warden pass: a resumable job that works through a ranked queue, ships what passes the gates through independent review, and delivers a weekly brief. Plus the nightly model adoption.

Honest read: the always-on Warden's problem was yield, not safety. Two unattended landings a week didn't justify running around the clock against a system that mostly didn't need fixing. Weekly fits the actual rate of real work.

## If you build one

- Start in shadow mode and stay there until you've read a few weeks of "would have merged."
- Make every gate prove it fires. A field that never changes value is decoration.
- Count fixes by what was built, never by what closed.
- Put the deterministic checks before the model, and never let the model approve.
- Give every autonomous action an executable undo, and watch the signal that started it.

**Next:** [The system documents itself](/docs/safety-and-operations/ground-truth/)
