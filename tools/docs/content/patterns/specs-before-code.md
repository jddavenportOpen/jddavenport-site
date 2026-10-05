---
title: "Write the spec before the code"
description: "A short spec for a new agent, PRDs whose user stories become the test contract, and an intent gate that checks the build matches the ask."
section: patterns
group: "Agents"
order: 20
updated: 2026-10-05
sources: ["frameworks/agent-requirement-document.mdx", "learn/tier-3/b7-architect-agent.mdx"]
---

Write down what "done" means before an agent writes a line of code, in a form a machine can check. An agent will happily build something plausible that nobody asked for. The spec is how you catch that before it ships instead of after.

I use three layers, from cheapest to heaviest: a one-page spec when I create a new agent, a PRD with user stories for anything with users, and an intent gate that compares the finished diff against what was asked.

## What you'll learn

- A trimmed one-page spec for a new agent, and which parts earn their keep
- How user stories turn into the QA contract
- How an intent gate works, and why it's scoped to one product family
- The smallest version you can start with today

## Layer 1: a one-page spec for a new agent

In March 2026 I called this an Agent Requirement Document: identity, objective, capabilities, inputs and outputs, constraints, error handling, review cadence. Seven sections.

Honest read: I don't keep ARDs as separate files anymore. The content moved into the agent's definition file and its capability card (see [Anatomy of an agent](/docs/patterns/anatomy-of-an-agent/)). But writing one before the first commit is still the fastest way to find out you don't know what you're building. Here's the trimmed version, for a hypothetical agent that writes a weekly digest of what shipped:

```markdown
## Agent: weekly-digest

Objective: every Friday, a one-page summary of what shipped across all
projects, drafted for me to read. One metric: I read it and don't have
to open a changelog.

Inputs: the per-project changelogs for the last 7 days.
Output: one Markdown file. A notification that it exists.

Can:
- read changelogs and the project registry
- write one file to the digests folder

Cannot:
- send anything to anyone (drafts only; sends go through the send gate)
- edit a changelog, a WORKPLAN or the registry

Stop conditions:
- no changelog entries this week: write "nothing shipped" and stop
- a changelog fails to parse: name the file in the digest, keep going

Model tier: build tier. Mechanical summarization, nothing irreversible.
```

Two sections do almost all the work.

**The Cannot list.** Capabilities are a whitelist; if it isn't listed, the agent doesn't do it. Writing "cannot send" in the spec is what tells you, before you build, that this agent needs no outbound channel at all. That's a security decision made for free.

**Stop conditions.** Most agent failures I've debugged weren't wrong answers. They were agents that didn't know when to stop, or that "handled" a missing input by inventing one. Name the empty case and the broken case up front.

The objective line matters too. If you can't write one sentence and one metric, you aren't ready to build. Go back and figure out what you want.

## Layer 2: PRDs with user stories

For anything with users, including me, the spec is a PRD, and the part that matters is the user stories:

```text
As a <who>, I want <what>, so that <why>.
Acceptance: <what a test can observe>
```

A story isn't documentation. In my setup it's the test contract. The QA agent parses a PRD, extracts every user story, and generates a test spec for each one. Each project can carry an acceptance table where every row maps one-to-one to a story:

```yaml
tests:
  - id: QA-P2
    route: /directory
    expect: >
      cards only for profiles marked visible; no email or phone text;
      a hidden profile never appears.
  - id: QA-P2b
    route: /directory with filters
    expect: result count drops; visible cards match every filter.
```

That's adapted from a real project's table. Notice the second half of QA-P2: the story says what must not happen, not just what should. Privacy failures live there.

### The done journey

The last step is a browser journey against production. A change isn't done in my system until the production URL is serving the exact commit that was merged and a Playwright journey passes against it. An inconclusive run is not a pass. The journey is the user story, run for real. ([Ship to prod](/docs/patterns/ship-to-prod/) covers the gate.)

The best journey file I have opens with a comment explaining what it deliberately does not test. The feature's one write fires when a phone tab is opened, and the journey never opens it, because the done gate is read-only against production. The comment also admits the test runner can't do phone widths at all, so the phone tab is pinned by unit tests instead. A spec that names its own blind spot is worth more than one that pretends to cover everything.

> **Tip:** Write the "must not happen" half of every story. That's where the expensive bugs are.

## Layer 3: an intent gate

Specs drift from builds. An agent reads the PRD, builds for an hour, and ships something adjacent. So the cockpit repo has a gate that checks the finished change against the ask. It runs three checks, cheapest first:

| Check | Cost | What it does |
|---|---|---|
| Significance | free, no model | Classifies the diff. Docs, tests and code inside one module pass instantly. Shared contracts (APIs, schemas, migrations, dependencies, CI and deploy config, auth) are significant. |
| PRD gate | free, deterministic | A significant change must trace to written intent: a PRD in the diff, a user story in the commit or PR body, or a project PRD updated in the last 14 days. |
| Signoff and intent verify | one top-tier model call | Only for significant changes. An independent reviewer re-derives what was asked and checks the diff delivers it. |

Three design choices matter.

**The verifier is independent.** It gets the intent sources (the PRD, commit messages, the WORKPLAN milestone) and the diff. It never gets the builder's summary or the chat. It derives the intent first, then re-reads the code and checks the build. That catches the failures a builder can't see in its own work: work claimed in a commit message that isn't in the code, and requirements that quietly fell off. Extra scope nobody asked for gets a note, and only blocks when it replaces what was asked.

**The PRD has to be fresh.** The 14-day window exists because a months-old PRD would wave through every future change forever. The gate caught exactly that on the cockpit: an April PRD that would have satisfied it indefinitely.

**It fails open.** A timeout, a crash, a missing secret or an unparseable verdict degrades to a loud warning. Only a clearly parsed BLOCK or MISMATCH fails the change. Honest read: a gate that blocks on its own bugs teaches everyone to route around it.

### Why it only fires on one product family

Since June 6, 2026, this "architect" gate runs only for the cockpit and the products built around it. Its review loads a map of that system (the routes, the session model, how the chat renders) and checks the diff for coherence with it. Point that at an unrelated web app and it flags missing patterns that app never had. The reviewer would be right about the cockpit. It's reviewing the wrong system.

Everything else gets industry-standard QA instead: Playwright journeys against the PRD's user stories, plus visual checks. My standing rule is that every build or QA prompt for a non-cockpit product says this in plain words, so no agent wires the wrong gate in.

The gate still signs off on cockpit changes today. A bigger idea, a standing "architect" that governs product coherence across everything, is parked as its own project. I'd rather have the narrow gate that works than the broad one that's still a design doc.

## Start small

You don't need any of this machinery to get the benefit. Start here:

1. Before you ask an agent to build, write three user stories with acceptance lines, including one "must not."
2. Put the story in the commit body: `Story: as a <who>, I want <what>, so that <why>.`
3. After the build, ask a fresh session, with only the stories and the diff, whether the diff delivers them. Not the session that built it.

Step 3 is the whole intent gate in one prompt. The automation just makes sure nobody skips it.

**Next:** [Sub-agents and delegation](/docs/patterns/sub-agents-and-delegation/)
