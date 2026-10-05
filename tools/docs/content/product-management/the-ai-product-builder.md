---
title: "The AI product builder"
description: "When one person can orchestrate agents across research, design and engineering, the PM role changes. The skills that matter now."
section: product-management
order: 30
updated: 2026-10-05
sources: ["product-management/ai-pm-builder.mdx"]
---

"Will AI replace PMs?" is the wrong question. The useful one is: what happens to the role when one person can direct agents that do first drafts of research, analysis, design and code? My answer, from running a production AI organization every day since April 2026: the PM becomes the person who decides what's worth building, specifies it precisely enough for an agent to build, and proves it works. Less coordination, more judgment.

## The role is absorbing its neighbors, partly

A product team used to need separate people for research synthesis, prototypes, analysis, status tracking and documentation. A PM who can direct agents now does a first pass of each.

| Work | What an agent does well | What the PM still owns |
|---|---|---|
| Research synthesis | Clusters interview transcripts, pulls themes, finds quotes | Deciding which problem matters, and reading enough raw transcripts to know if the summary is right |
| Prototyping | A working prototype in hours, not a sprint | Taste: which of three versions is right, and what to cut |
| Analysis | Writes the query, runs it, charts it | Choosing the metric, and noticing when the number is measuring something else |
| Tracking | Status reports, follow-ups, commitments | Calling the tradeoff when two commitments collide |
| Writing | Drafts PRDs, release notes, updates | The decision the document records |

That's why the heading says "partly." Agents produce a strong first draft. Specialists still matter for depth: a senior researcher, designer or engineer catches things a first draft won't. What changes is the ratio. More first passes come from agents, and specialists put their time where depth pays.

## A worked example: how I build with agents

My own system is the clearest example I can give. I talk to one top-level agent. It routes work to specialist agents, and 30+ of them run in daily production. Here's how a feature actually moves:

1. **Spec first.** Builds start from a written spec with user stories and acceptance tests, and QA later runs against those same stories. Agents build the wrong thing confidently when the spec is vague, so the spec is where my time goes.
2. **Build in isolation.** Parallel build agents each work in their own git workspace, so parallel agents can't overwrite each other.
3. **Adversarial review.** Every substantive change gets reviewed by three separate agents with different instructions, one of them told to try to reject it. Then automated tests and checks.
4. **Ship, then I review the product.** I don't read diffs or review pull requests. The agent that built it merges, deploys, and tells me what to click. I judge it by using it.
5. **"Done" is a machine check.** For user-facing work, the live site has to report the exact commit that was merged, and a browser test has to pass the real user journey on the live site. No pass, no "done."
6. **Anything that leaves the system needs my yes.** Agents can draft any message. Nothing gets sent, and no money moves, without my approval.

Notice where my effort sits: the spec at the start, the product at the end, and the approvals on anything risky. That's the PM's job in miniature. The middle is delegated, with machines checking it.

## The skills that matter now

### 1. Orchestration

Delegating to an agent is delegating to a very fast new hire with no context. The skill is the hand-off: the goal, the context, what "done" means, which files to read first, and what not to touch. A vague brief to an agent doesn't produce a question. It produces a confident wrong answer, fast.

### 2. Systems thinking

Once agents do the work, you're designing a system: inputs, outputs, loops and failure modes. Where does work get stuck? What happens when a step fails quietly? Who notices? Some of my hardest problems were system problems: two scripts writing different values to the same setting and fighting each other dozens of times a day, or a call between agents that failed by returning an empty answer that looked real.

### 3. Judgment and taste

When generating options is nearly free, the value moves to choosing. Which problem is worth solving. Which solution is simple enough. Which metric actually matters. An agent will happily give you ten options. Picking the right one, and killing the other nine, is the job.

### 4. Technical fluency

You don't need to write production code. You need to understand APIs, data models, how agents use tools, and how models fail, well enough to know what's easy, what's hard, and what's a bad idea. The fastest way to get there is to build one small agent yourself. The [Start here](/docs/start-here/what-is-claude-code/) section is designed for exactly that.

### 5. Evals

This is the skill I'd put first if I could only pick one. An eval is a test for an AI system's behavior: a set of tasks, a definition of good, and graders that check it. Without evals, "the agent works" is a feeling. With them, it's a number you can watch move. Writing good evals is product work: you're defining quality precisely enough that a machine can check it. The [AI Core Skills](/docs/ai-core-skills/agent-evals/) series teaches it end to end, with a starter repo you can run tonight.

### 6. Knowing where the human stays

Every system I trust has explicit points where a person approves: money, sending as you, identity, anything irreversible. Deciding where those gates go, and enforcing them in code instead of hoping, is a product decision. It's also the one that determines whether anyone can trust what you built.

## The honest limits

- **Agents make the build cheaper, not the decision.** The bottleneck moves from "can we build it" to "should we." That makes PMs more important, not less, but only PMs who can make that call well.
- **First drafts need checking.** Every claim an agent makes about the world has to be checkable. My docs, including this one, follow a rule that every fact about my system is verified against the live system before it's published, because agents write confident prose about things that aren't true.
- **One-person systems are fragile.** Mine runs because I hold it to strict process rules and fix root causes, not symptoms. It still breaks. A team adopting this needs someone who owns that reliability work.

## How to start

1. **Build one small agent** that does a real task for you. Follow [Start here](/docs/start-here/what-is-claude-code/), then [Build your first agent](/docs/fundamentals/build-your-first-agent/).
2. **Write evals for it** before you trust it. Start with [Agent evals](/docs/ai-core-skills/agent-evals/).
3. **Write down what you learned**, including what broke. That record is your portfolio.
4. **Talk about decisions, not tools.** In interviews and on your resume, describe what you chose, how you checked it, and where you kept a human in the loop.

The PM role is becoming the job of turning cheap output into the right product. Start building with agents now, and keep receipts.

**Next:** [Glossary](/docs/reference/glossary/)
