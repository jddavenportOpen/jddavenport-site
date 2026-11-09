---
title: "Bug report to merged fix"
description: "Turn a user's bug report into a failing test, a fix in its own worktree, and a merge that is gated on proof. Root cause first, not a patch on the symptom."
section: marketplace
group: "Workflows"
order: 40
updated: 2026-11-09
sources: ["https://github.com/ai-foundry-byu/app-feedback-loop", "https://github.com/jddavenportOpen/claude-bug-squash"]
---

Most bug fixes by agents patch the symptom the user saw. The bug comes back in a new shape a week later. This workflow refuses a fix until there is a test that fails while the bug is present and passes once it is gone.

## What you install

```
claude plugin marketplace add jddavenportOpen/claude-bug-squash && claude plugin install claude-bug-squash@claude-bug-squash
claude plugin marketplace add ai-foundry-byu/foundry-marketplace && claude plugin install foundry-sdlc@ai-foundry
```

For the intake side, have your agent build [app-feedback-loop](https://github.com/ai-foundry-byu/app-feedback-loop) into your app. It is a spec, not a library.

## The steps

1. **Capture.** The in-app feedback button sends a screenshot plus context: the page, recent errors, console and network.
2. **Write it down in the reporter's words.** `bug-to-story` gives the report an id and adds it to the PRD as a story criterion.
3. **Reproduce.** Write the repro as a command that fails now. If you cannot reproduce it, the report stays open with a question, not a guess.
4. **Ask why five times.** Fix the cause that produced this bug, not the line where it showed up.
5. **Fix in a worktree.** claude-bug-squash fixes in an isolated worktree, proves red to green, and puts the fix through a three-seat review before it can merge.
6. **Close the loop.** The fix commit tells the reporter it is fixed.

## Check your work

The repro command failed before the fix and passes after it, on the merged commit. The new test stays in the suite so the bug cannot quietly return.

## Limits

claude-bug-squash will not auto-merge without a repro command, and by default it merges at most one fix a day. The habit behind this is in [Root cause first](/docs/patterns/root-cause-first/).
