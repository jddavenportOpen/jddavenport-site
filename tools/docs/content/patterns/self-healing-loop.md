---
title: "The self-healing loop"
description: "A scout reads the system's own failures and ranks fixes, a human approves, and isolated agents ship them with a failing test first."
section: patterns
group: "Shipping"
order: 140
updated: 2026-10-05
sources: ["learn/tier-2/13-self-healing-loop.mdx"]
---

A system that runs all day produces a steady stream of evidence about what's broken: error logs, failed jobs, red tests, retries. A self-healing loop reads that evidence, proposes fixes, gets a human yes, and ships the fixes through the same gates as any other change. It's four narrow jobs wired together with a human approval in the middle, and that approval is what keeps it honest.

## The weekend it worked

In June 2026 I posted that my agent system had found seven bugs in itself over a weekend, I had approved the fixes, and seven build agents were shipping them. That was true. The changelog from June 7 and 8 shows the proposals, the approvals and the fixes, each with a regression guard. The fixes ranged from plumbing to real gaps: retries and a 72-hour aging alert for voice-note processing that could fail quietly, a circuit breaker on an auth path, a reaper for stale open loops, a digest that stopped sending when there was nothing to say, and a migration of hand-rolled API calls that had no fallback (one was failing live that weekend).

That weekend is history now, and what came after is more useful than the weekend itself. It's in [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/). This page is the pattern.

## The four jobs

### 1. The scout

A scheduled job reads the system's own logs, failed-job records and test output, groups recurring failures, and writes ranked proposals. Each proposal has:

- the root cause, stated as a process gap, not a symptom
- the proposed fix
- how confident the scout is
- the risk: is it reversible, and what's the blast radius?

The scout never builds anything. It observes and proposes.

Run it twice a day, not continuously. The human review is the bottleneck by design, and a scout that writes proposals every ten minutes buries the reviewer.

### 2. The human gate

I read the proposals and approve or reject each one. Approving "add a test and fix the log format" takes seconds. A proposal that changes a schema or the behavior of something live gets real scrutiny.

This step is not optional. The scout can be right about the bug and wrong about the fix, and a fix that quietly changes a contract other code depends on looks fine in isolation. Catching that is the reviewer's job.

### 3. Isolated build agents

Each approved proposal becomes a task for its own build agent, in its own git worktree, on its own branch. Approvals fan out to parallel agents that don't step on each other. See [Worktree isolation](/docs/patterns/worktree-isolation/) for why the isolation has to be enforced, not requested.

The order inside each agent matters: **write the failing test first.** Reproduce the bug as a test that goes red, then make it go green. A fix without a reproduction is a guess.

### 4. Gates decide what merges

The build agent doesn't decide it's done. The same machinery that gates every other change does: review by separate agents, the merge gate, and for anything user-facing, the done gate against prod. A fix that can't pass the gates doesn't land, however confident its author was.

## What a guard looks like

Every fix ships with something that fails if the bug comes back. That's what makes the loop self-healing instead of self-patching. A guard is one of:

- a test that reproduces the original failure
- a check in the merge gate that blocks the pattern (for example, a scan that refuses any new hand-rolled API call)
- a scheduled sweep that alerts if the bug class reappears
- a new assertion in an existing test

A fix with no guard is half a fix. The bug is one bad edit away from coming back.

## What went wrong later

Two lessons from the months after that weekend, because the loop did not just keep humming:

- **Proposal quality decays.** On July 31, 2026 I had five reviewer agents read every open proposal against the live system. There were 403. They recommended 23, a signal rate under 6%. Two finds were alarming: one proposal to adopt a new model was built entirely from strings in a test fixture that had leaked into the live queue, and another's whole body was an approval in my name ("JD approved: build it") that referred to nothing. A scout reading noisy logs proposes noise, and a queue nobody prunes starts holding things that look like authority. The standalone scout has been paused since September 13, 2026, and I killed its backlog sweep. Failures now become tickets in the gated bug-squash pipeline instead.
- **Gates on paper aren't gates.** On August 1, 2026 a safety review found the automated fixer's review quorum passed with one approval out of three, and one merge path ignored shadow mode entirely. It went back to shadow mode that day. The details are in [Auto bug-squash and the Warden](/docs/safety-and-operations/bug-squash-and-warden/).

Honest read: the human approval step was never the weak link. The weak links were every place I assumed a machine check was running when it wasn't.

## A version you can build this weekend

You don't need any of my infrastructure. Three pieces:

**1. A log reader that writes proposals.** Group the last day of errors by a normalized signature and write anything that recurred to a file:

```python
from collections import Counter
from json import dumps
from pathlib import Path
from re import sub

def signature(line: str) -> str:
    # strip numbers, ids and paths so the same error groups together
    line = sub(r"\b[0-9a-f]{8,}\b", "<id>", line)
    line = sub(r"\d+", "<n>", line)
    return sub(r"(/[\w.-]+)+", "<path>", line)[:200]

def scout(log_files, out=Path("proposals.json"), min_count=3):
    counts = Counter()
    examples = {}
    for f in log_files:
        for line in Path(f).read_text(errors="ignore").splitlines():
            if "ERROR" in line or "Traceback" in line:
                sig = signature(line)
                counts[sig] += 1
                examples.setdefault(sig, line)
    proposals = [
        {"signature": s, "count": n, "example": examples[s], "status": "proposed"}
        for s, n in counts.most_common() if n >= min_count
    ]
    out.write_text(dumps(proposals, indent=2))
    return proposals
```

**2. A human review step.** Read `proposals.json`, set `status` to `approved` or `rejected`. Thirty seconds for a handful of items. Don't skip it.

**3. A build prompt that demands a test.** For each approved item, run Claude Code in a fresh worktree with something like:

```text
Approved bug: <signature and example line>.
Work in this worktree only. First write a test that reproduces the failure and confirm it fails.
Then fix the root cause, not the symptom. Confirm the test passes and the full suite stays green.
Report: root cause, the fix, the test you added, and anything you could not verify.
Do not merge. Open a PR.
```

Then you merge after your gates pass. Once you have a few weeks of proposals and outcomes, add the extras: confidence scores you can calibrate against what actually got approved, a cap on files per fix, and a list of paths automated fixes may never touch.

**Next:** [Projects vs. todos](/docs/patterns/projects-vs-todos/)
