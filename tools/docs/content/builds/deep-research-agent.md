---
title: "The deep-research agent"
description: "A knowledge-gap loop over parallel sources with a devil's-advocate pass and per-claim verification. Public and clonable."
section: builds
group: "Research and content"
order: 50
updated: 2026-10-05
sources: ["learn/tier-3/f1-deep-research-agent.mdx"]
---

My research agent treats a question as a loop with a stopping condition and treats its own draft as a hypothesis to attack. It keeps searching until it can't name a gap, argues against itself, then tries to refute every factual claim in the final report before it hands it over. The code is public at [jddavenportOpen/deep-research-agent](https://github.com/jddavenportOpen/deep-research-agent).

It's also the agent behind two of my more embarrassing failures, which are further down and worth more than the architecture.

## Why not just search and summarize

One round of search plus a summary gives you a confident paragraph built on whatever ranked first. Three things go wrong: it stops too early on hard questions, nothing checks it against itself, and you can't tell the solid claims from the guesses. Each piece below fixes one of those.

## The loop

```text
question
  -> 1. Knowledge gap: what don't we know yet? (or COMPLETE)
  -> 2. Tool selector: which sources, which query, per gap
  -> 3. Parallel search across sources, then scrape the best pages
  -> 4. Observations: what did the sources actually say?
  -> back to 1 until COMPLETE or the budget runs out
  -> 5. Devil's advocate: attack the findings; critique becomes new gaps
  -> 6. Writer: cited report with a confidence score
  -> 7. Verify: try to refute every claim, flag what doesn't survive
  -> 8. Save
```

**The gap step is the engine.** Each pass asks what's still missing and returns specific sub-questions. When nothing material is missing it says `COMPLETE`. Easy questions stop after a couple of passes. Hard ones get more.

**Sources run in parallel.** The public version fans out to nine: web search (Brave), GitHub, Reddit, arXiv, Hacker News, Semantic Scholar, Stack Overflow, Wikipedia and X. Search snippets are thin, so the top web results get scraped to full text and fed back into the same pass. The tool selector picks sources by question type: social questions go to X and Reddit, academic claims to arXiv and Semantic Scholar, code questions to GitHub and Stack Overflow.

**Supporting pieces** keep a deep run usable: multi-hop decomposition (a "compare A and B on X, Y and Z" gap becomes parallel sub-queries), one hop of citation-graph expansion through Semantic Scholar, source credibility scoring, and relevance-based compression so a run with hundreds of sources still fits the writer's context.

## Attacking its own work

Two stages exist to make the report less sure of itself.

**The devil's advocate** reads the accumulated findings and looks for what's weak, contradicted or missing. Its critique doesn't go into a footnote. It goes back into the loop as new gaps, so the agent researches its own blind spots.

**Per-claim verification** runs after the writer. It pulls the falsifiable claims out of the draft and hands each one to independent skeptical voters. Each voter runs a fresh search trying to prove the claim wrong.

| Verdict | Rule |
|---|---|
| REFUTED | At least 2 of 3 voters find contradicting evidence |
| VERIFIED | Survives the vote and a voter produced a real supporting source URL |
| UNVERIFIED | Survives, but nobody found a source. The skeptical default. |

The report ships with a claim verification table and inline flags, so a reader sees which sentences are solid at a glance. The README credits where the vote-per-claim pattern came from. The gap loop, the source fan-out and the rest are original.

The report also carries a 0 to 100 confidence score, and the agent is allowed to say it's low. An August 2026 run of mine over 478 sources came back at 47, labeled LOW. The run worked fine. The agent was telling me the evidence is thin, which is the one thing I most need it to say.

## Depth and cost

The public repo ships three presets:

| Depth | Passes | Claim verification | Pages scraped per pass |
|---|---|---|---|
| shallow | 2 | off | 1 |
| standard | 5 | light (1 vote, up to 12 claims) | 3 |
| deep | 10 | full (3 votes, up to 25 claims) | 5 |

```bash
git clone https://github.com/jddavenportOpen/deep-research-agent.git
cd deep-research-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # add the keys you have; only an LLM route is required
python -m deep_research.main "state of autonomous agents" --depth deep --resume
```

It runs on two model profiles: a cheap one (cloud models through OpenRouter plus a local Ollama step) and a premium one that routes every role through Claude. Every call is cost-tracked and the total goes into the report's front matter. For scale: a deep run in June 2026 over 370 sources logged $7.78, list-price equivalent.

State is checkpointed after every pass. In August two of my deep runs were killed partway through by a tool timeout. Both resumed from their last checkpoint instead of starting over. `--resume` is not a nice-to-have on a ten-pass run.

The version I run internally has one extra, opt-in source: a single call that lets Claude use its own web search and fetch tools and return a cited mini-report, which gets ingested alongside the other sources.

## Two failures worth more than the diagram

Both came from the same place: a scheduled research sweep inside my self-improvement loop, which runs the researcher on a timer and turns findings into improvement proposals.

**Zero sources for 24 days.** The sweep ran on the cheap profile. When I turned off the paid router that profile depended on, every call fell through to the Claude CLI, which rejected the non-Claude model names. The tool selector died first, so no search ever ran. From July 5 to July 29, 2026, every run reported `Sources: 0`, exited 0, and looked healthy. The fix pinned the sweep to a profile that routes to models the machine can actually call, plus a test that goes red if anyone points it at an unroutable provider again.

**The same report 27 times.** The sweep rotates through five evergreen themes, one per run, so every query comes back around every few days. Nothing checked whether the new report said anything the last one hadn't. From June 7 to September 1, 2026 one query alone (multi-agent orchestration patterns) saved 27 near-identical reports, about half a megabyte of the same output. The proposals it generated were deduplicated, so the downstream backlog looked clean. The reports weren't, and nobody read them closely enough to notice. A September audit found it; the last logged run had produced a 748-character report from zero sources. The fix lives at the save step: it compares the new report's body with the newest prior report on the same topic and replaces it in place when they say the same thing. It compares the body only, because the front matter carries a date and a cost that change every run, so hashing the whole file would never match and the check would silently do nothing.

Honest read: both are the same bug class. A scheduled job that exits 0 is not a job that works. Check the output, not the exit code, and make "nothing new" a loud result instead of a quiet one.

## Correcting the record

An earlier version of these docs said this agent started life inside an earlier OpenClaw codebase. It didn't. That claim came from a mislabeled internal file. This is my own code, built on Claude and my own scaffolding.

**Next:** [AI decks that don't look like AI](/docs/builds/decks/)
