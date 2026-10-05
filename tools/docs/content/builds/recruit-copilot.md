---
title: "recruit-copilot: a job search as a verification problem"
description: "One experience bank, roles scored against your goals, tailored resumes proven machine-readable, and no auto-apply by design."
section: builds
group: "Open source"
order: 180
updated: 2026-10-05
sources: []
---

Sending a job application is the easy part, and nobody needs a tool to send more of them. The part worth automating is the check before you hit send: is this role a real fit, can a machine read this resume, and would a hiring manager advance it. recruit-copilot is a Claude Code methodology built on that idea, public at [jddavenportOpen/recruit-copilot](https://github.com/jddavenportOpen/recruit-copilot), MIT licensed.

It does not apply for you. There is no submit path in the repo at all, for any employer, behind any flag. That's the point, not a missing feature.

## What you'll learn

- The eight-stage loop from old resumes to a recorded outcome
- The five checks that catch failures you'd otherwise never hear about
- Why the tool refuses to submit, and why I agree with it
- How to install it, fork it, or run it without Claude Code

## The loop

Point it at the resumes you already have. It merges them into one experience bank, scores open roles against goals you write, and for a posting you pick, builds a tailored single-column PDF. Then it checks that PDF harder than you would, applies a bar matched to the employer, and stops.

```text
01 intake -> 02 goals -> 03 scout -> 04 tailor -> 05 grade
                ^                                    |
                |                                    v
            08 outcome <- 07 apply <-------- 06 submit tier
```

| Stage | Decides |
|---|---|
| Intake | What is true about you, in one bank every resume draws from |
| Goals | What counts as a job worth your attention |
| Scout | Which open roles clear that bar, and why |
| Tailor | What goes on the page, and whether a machine can read the page |
| Grade | Whether three independent judges would advance it |
| Submit tier | What this employer costs to get wrong, and what bar that sets |
| Apply | The handoff to you, and a ledger row |
| Outcome | What actually happened, and what that should change |

Each stage is one Markdown file under `.claude/skills/recruit-copilot/`, written so a model with no other context can execute it and a human can read it before deciding to fork.

Two rules sit over all of it. **It cannot invent**: every line on a generated resume traces back to a bank entry you confirmed. And **your data stays on your machine**: the bank and every resume live in your home directory, outside the repo, and the only network calls go to public job boards.

## The five checks

Each one catches a failure that is silent. No error, no bounce, no reply. You never learn it happened, so you keep doing it.

| Check | The silent failure it catches |
|---|---|
| **Round trip.** Open the finished PDF, extract the text, diff it against what was laid out. Hard fail if your email didn't survive | A phone number swallowed by a header region, an employer lost to column interleaving, an export that came out as an image. Looks perfect on screen, arrives empty |
| **Layout.** Measure the rendered page from real glyph boxes | Overlapping text. It extracts as clean, correctly ordered text, so no parser can see it. Only the human reading it can |
| **Deterministic panel math.** Three judges score; a script does the arithmetic | LLM judges cluster in the 55 to 72 range and vote yes while scoring 72. The README's example: hand-averaging one real panel read 88.3 where the rule-based aggregator returned 80.1 |
| **Standard-library PDF stack.** About 850 lines, writer and reader | A common PDF library's encoding returns nothing to a simpler decoder, which looks exactly like a scanned image and sends you debugging the wrong thing |
| **Submit tier.** Never auto on the companies that matter | Spending your one read at the company you actually wanted while your resume was two revisions from ready |

The three judges are a recruiter's six-second skim, a hiring manager, and the applicant-tracking system itself. Same idea as [resume-grader](/docs/builds/resume-grader/), with two more seats and the math moved out of the model.

## Why it won't submit

The reasoning is a tier system. A standard employer is a repeatable event: apply, learn, apply again. A reach employer is close to one shot. The moment a tool can submit at the cheap end, the only thing between you and a bad submission at the expensive end is a config value and your judgment at 1am.

So the tool applies the bar that matches what this employer costs to get wrong: 90 for an employer you've marked as a reach, 70 for everyone else, 85 as the floor for the panel vote. Then it tells you no if you haven't cleared it, tells you where the file is, and you apply.

Those three numbers are judgments, and the repo says so. It has no funnel data yet and won't borrow anyone else's. The outcome stage exists to fix that: record what happened to an application and, if you want, contribute an anonymized record (tier, role family, panel score, result, month). Enough of those and a real question becomes answerable: does a panel score predict anything? If an 88 converts at the same rate as a 68, the bar is theater, and the repo commits to saying so.

Honest read: that last paragraph is the most important design choice in the repo. Every resume tool claims its score means something. Very few build the instrument that could prove it wrong.

## Install it

As a Claude Code plugin, from your terminal:

```bash
claude plugin marketplace add jddavenportOpen/recruit-copilot && claude plugin install recruit@recruit-copilot
```

Or inside a session, one command at a time (paste them together and the first reads the second as part of the repo name):

```text
/plugin marketplace add jddavenportOpen/recruit-copilot
```

```text
/plugin install recruit@recruit-copilot
```

Restart Claude Code or run `/reload-plugins`, then type `/recruit:` to see the commands: intake, goals, scout, tailor, grade, outcome, and a local dashboard whose Start Here tab walks setup in order.

It needs Python 3.9 or newer and Claude Code. Nothing to pip install, including the PDF work. Claude in your own session is the language runtime for intake, tailoring and grading, so there's no separate API key. Installing `pymupdf` is optional and switches the round-trip check to an independent text engine; the check reports which engine it used.

### Or fork it

The methodology is written to be taken. Four things in it are yours, not mine:

- **Your reach employers.** A 40-person startup you've wanted for three years is a reach for you. A famous logo you'd only take as a fallback isn't.
- **Your two pass bars.** Ideally set from your own outcome ledger.
- **The boards you scout.** Coverage is by company, not keyword.
- **Your search goals.** The scout refuses to run without them, rather than scoring your career against a stranger's defaults.

### Or run it without Claude Code

The two scripts that produce every number are plain Python with zero third-party imports, and the three judges are plain prompts any model can take. A smoke test builds a throwaway workspace, drives the real scripts, and checks the output with no network and no key:

```bash
git clone https://github.com/jddavenportOpen/recruit-copilot.git
cd recruit-copilot && python3 smoke_test.py
```

## Honest limits

From the repo, and worth repeating:

- The round-trip check proves the text is present and recoverable in reading order. It can't prove every commercial applicant-tracking system parses it, because those are closed. Don't let anyone call it "ATS-verified."
- Scanned, image-only resumes can't be read. There's no OCR.
- Scouting covers Greenhouse and Ashby. Lever, Workday and the rest aren't wired yet, which is the biggest open gap.
- No cover letters and no interview prep yet.
- Nothing here can tell whether a claim on your resume is true. Only you can.

**Next:** [VoiceClaw: a phone agent](/docs/builds/voiceclaw/)
