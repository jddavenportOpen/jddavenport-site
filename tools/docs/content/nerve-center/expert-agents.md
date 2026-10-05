---
title: "Expert agents: route by topic"
description: "A knowledge base plus a routing table, so the main agent calls the expert instead of answering from its own head."
section: nerve-center
group: "Orchestration"
order: 80
updated: 2026-10-05
sources: ["learn/tier-3/g3-health-stack.mdx", "learn/tier-3/g5-tax-and-finance.mdx"]
---

An expert agent is a narrow agent with its own knowledge base, and a routing rule that forces the main agent to call it. The routing rule is the important half. A general model asked about a filing deadline or a training block will give you a confident, plausible, generic answer. An expert grounded in the right sources and my context gives a specific one, with the source attached. The work is making sure the specific one gets asked.

## The experts I run

By category:

| Expert | Grounded in | Typical question |
|---|---|---|
| Course experts, one per course, plus a TA seat | That course's real slides, readings and syllabus | "Explain the concept from week 4 and how it shows up on the exam" |
| Fitness and training | A research knowledge base with labeled evidence, plus my goals | "Should I swap this lift, and what does the evidence say?" |
| Tax rules and deadlines | Tax law research plus my own tax context | "What's the deadline to amend, and which rule sets it?" |
| Claude certification study | The exam's task statements and a drill bank | "Quiz me on the parts I keep missing" |
| Case-competition coach | Judging criteria, sources and past decks | "Score this deck the way a judge would" |

There are others I don't list publicly. The pattern is the same for all of them.

## The routing table

The rule lives in the instruction file every main session reads: when a message hits one of these topics, call the expert and reply with its answer. Don't answer from your own head. I don't have to name the agent or type a slash command; a partial match on the topic is enough.

A trimmed version of the shape:

```text
Topic triggers                                  -> Expert
"the course prof", "ask the <course> prof"      -> course expert for that course
progressive overload, deload, program design    -> fitness and training expert
amend, missed deduction, refund deadline        -> tax expert
the cert, practice exam, study plan (cert ctx)  -> certification mentor
"judge our deck", the case comp                 -> case-competition coach
```

Each expert is also a target on the [agent bus](/docs/nerve-center/the-agent-bus/), so a domain agent or the CEO agent can ask one directly. Most also take attachments: a slide, a PDF, a screenshot of a problem.

> **Warning:** Write the routing table where every session will read it. A domain session only loads its own folder's rules plus my user-level file. A routing rule that lives only in the main project file reaches the CEO seat and nobody else, and the domain agent will cheerfully answer from its own head.

## Anatomy of an expert

They're all built the same way, and it's deliberately small:

1. **A persona prompt, kept verbatim.** Who the expert is, what it owns, how it answers, what it refuses. The tax expert, for example, leads with the exact deadline and names the rule that sets it.
2. **Always-loaded context.** A master synthesis of the knowledge base, plus a profile file of my relevant context, injected on every call.
3. **Retrieved on relevance.** The top few topic files, scored against the question.
4. **One `ask()` function and a CLI.** Same interface for every expert, so callers don't care which one they're talking to.

Retrieval depends on size. The tax expert's knowledge base is a handful of Markdown files, so it uses keyword scoring and no vector database at all. The course experts crawl the course site, download the slides and readings, parse them, embed them, and answer with a citation to the slide. Use the simplest retrieval that finds the right page.

## Label the evidence

The fitness expert weighs three kinds of evidence and tags every claim with one of them: a peer-reviewed human study, an animal study, or community practice (coaches, forums, anecdote). It takes all three seriously and never presents an anecdote as trial data.

That one rule does more for trust than any amount of retrieval tuning. When an answer says *community* next to a claim, I know how much weight to put on it.

## Keep the knowledge current

A knowledge base built once goes stale quietly. The fitness expert runs a weekly currency loop: a research agent refreshes one core area every week plus two rotating ones, so every area gets touched within about three weeks, and it appends a dated digest to that area's log. A staleness watchdog flags any area that falls behind.

The loop only researches and files. It doesn't change my program; that still goes through the expert and me.

## Ownership: the expert owns its domain

In June I watched the main agent start editing my training program itself, because the request came in through the main chat. That's the failure this pattern exists to prevent. The rule I wrote: the fitness expert owns program design. The main agent briefs it with the full request and relays the answer. It doesn't draft the change on its own.

The same goes for the case-competition coach, with an extra constraint. The competition bans AI-generated final work and requires disclosing AI use. So the coach critiques, finds sources and scores. The team writes the slides. Before submission it runs a check for leaks that would disqualify a deck, like a school name sitting in the file's metadata.

## Keep the grounding private

The experts that help most are grounded in personal documents: your records, your goals, your history. That's also what makes them unpublishable, so I share the pattern and keep the knowledge bases private. If you build one, ground it in your own documents and check that its first real answer is concrete and verifiable. If it isn't, the grounding is too thin.

## Build your own

1. Pick a topic where a wrong confident answer costs you something.
2. Write the persona prompt and a one-page synthesis before you collect sources.
3. Start with keyword retrieval over Markdown. Add embeddings only when it misses.
4. Label evidence quality in the answer itself.
5. Put the routing rule where every session reads it, and say "never answer from your own head" out loud.

[Course-expert agents](/docs/builds/course-expert-agents/) walks through building the course version end to end.

**Next:** [The executive assistant](/docs/nerve-center/executive-assistant/)
