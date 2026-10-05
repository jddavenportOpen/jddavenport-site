---
title: "The one-shot pipeline"
description: "Scaffold, lock intent, brief with ground truth, build in isolation, verify against stories, ship, log. Which steps machines enforce and which are still prose."
section: patterns
group: "Shipping"
order: 130
updated: 2026-10-05
sources: ["frameworks/one-shot-methodology.mdx"]
---

Agents build things right the first time when they work inside a pipeline with gates they can't talk their way past. The same model, prompted ad hoc, gives you the coin-flip quality everyone complains about. Put it inside scaffolding, written intent, isolation, verification and a ship log, and the hit rate changes.

I first wrote this up in June 2026. This version is the October re-audit: every step checked against what actually runs today, and one claim cut. The June version said we "ship working applications daily." I can't back that as a rate, so it's gone. What I can show: merges into my agent repo went from 6 in May to 78 in June, 166 in July and 332 in August 2026, while the number of new repos I was creating fell. Fewer new things, more work landing per thing.

## The first law

> Anything that must happen every time gets a hook, a gate, a schedule or a check. Prose rules are for judgment calls.

Rules written into an instruction file get followed until the context fills up with task work and the rule loses its grip. My main instruction file still has a rule marked NON-NEGOTIABLE in capitals, followed by a paragraph listing exactly when agents tend to forget it. That paragraph exists because the capitals didn't work. The spoken-summary rule had the same problem until May 2026, when I moved it into a hook that fires at the end of every turn. Since then it doesn't depend on the model remembering anything. Everything below follows from that.

## The seven steps

### 1. Scaffold: projects exist as files

One command creates a project folder with a README, a workplan, a changelog and a links file, and registers it in a machine-readable project registry. Nothing starts life as "a conversation we had." If the project has a runbook, agents read it first and use its existing generators instead of hand-writing output.

Prevents: lost context between sessions, reinvented requirements, no record of decisions.

### 2. Lock intent: written requirements before code

Significant changes have to trace to written intent: a PRD, user stories, or at least a commit message that states the story. In my cockpit repo, a gate on the commit message checks for that intent before a significant change can land. It's a deterministic script, not a model call, and it fails open on its own errors so a broken gate never wedges a commit.

The most useful part of any PRD is its acceptance tests: user-visible, falsifiable behavior. Not "chat should work well" but "clicking any live agent in any section opens its pane." Those become the QA journeys in step 5. More on that in [Write the spec before the code](/docs/patterns/specs-before-code/).

### 3. Brief: ground truth before interpretation

A build session should read the facts before it reads the request. In my system that means the instruction files, the project's own state files, and a digest of the previous session that hooks write at compaction and at session end, so a new session starts from a file instead of a memory. Agents that draft or decide for me also load four personal context files (who I am, how I decide, how I write, my hard rules).

Prevents: an agent confidently building on a stale picture of the codebase.

### 4. Build under isolation

- **Worktrees are mandatory** for any agent that may touch git. A preflight refuses to guess which repo it's in. A pre-commit hook on the shared cockpit checkout refuses commits outright, and a watchdog restores a shared checkout that has drifted off its branch. I adopted this after parallel agents switched branches under each other more than once. The full story is in [Worktree isolation](/docs/patterns/worktree-isolation/).
- **Inventory before spawning.** Before an orchestrator spins up a generic agent, it checks whether a specialist already exists. Re-implementing the QA runner from scratch is a violation, not a style choice.
- **Name the model on every fan-out lane.** A lane that doesn't say which model to use inherits the most expensive one. Mechanical stages get a small model, normal building gets the build tier, and the top tier is reserved for work that needs it. See [Model routing](/docs/patterns/model-routing/).

### 5. Verify: never by the builder

Two checks, neither done by the agent that wrote the code:

- **Review by separate agents**, with effort scaled to blast radius, and one reviewer told to try to reject. For cockpit changes there's also an architect sign-off at commit time. Products outside the cockpit don't get the architect, because its assumptions don't apply to them. They get industry-standard QA instead.
- **QA against the spec.** A QA agent turns user stories into Playwright journeys and runs them against the deployed app, at phone and desktop widths, with accessibility and visual checks. It tests what the PRD promised, never what the builder claimed. "I fixed it" isn't evidence. A green run is.

Details in [QA: user stories, Playwright and synthetic users](/docs/safety-and-operations/qa-and-synthetic-users/).

### 6. Ship: the human reviews the product

The building session merges through the merge gate, deploys, restarts whatever runs the code, and runs the done gate: the prod URL must serve the merged commit and a browser journey must pass against prod. Only then does it tell me what to click. Pushes to my own repos go straight through. Anything that touches someone else's repo (a fork, a PR, a comment) goes past a GitHub governor that judges reputation risk. The flow is in [Ship to prod](/docs/patterns/ship-to-prod/).

### 7. Log: every ship leaves a record

One command appends a dated line to the project's changelog and ticks the matching workplan item. A master changelog is regenerated daily from every project's log. When I ask "what did we build this week," the answer comes from that file, not from chat history, which is gone at the next session rotation.

## Machine-enforced vs prose, re-verified

I re-checked every row against the live system on October 5, 2026. The June table had rows that no longer matched reality (a session-start briefing hook and a stop-hook intent check that aren't wired globally today), so this table is shorter and true.

| Mechanism | How it's enforced | Kind |
|---|---|---|
| No commits from the shared cockpit checkout | Pre-commit hook plus drift watchdog | Machine |
| An agent in a worktree can't edit files in a shared checkout | Pre-edit path guard hook | Machine |
| No raw restarts of the session supervisor | Pre-tool-use hook | Machine |
| Every outbound send through one gate | Chokepoint plus a daily scan for bypasses | Machine |
| No new test failures on push | Local merge gate, new-failure ratchet | Machine |
| Written intent for significant cockpit changes | Commit-message gate (fails open on its own errors) | Machine |
| Instruction file stays small | Pre-commit size budget | Machine |
| Actions on other people's GitHub repos | Governor hook, with an explicit human override | Machine |
| "Done" means the right SHA and a passing journey | Done gate, which the shipping agent must run | Hybrid |
| Reuse a specialist before building a new one | Rule plus a registry lookup script | Hybrid |
| Review effort scales with blast radius | Rule plus an advisory lint (it warns, doesn't block) | Hybrid |
| Root cause before bandaid | Rule, with worked examples | Judgment |
| Push back with receipts, concede fast | Rule, copied into every spawned agent's prompt | Judgment |

The split is deliberate. Mechanical invariants get mechanical enforcement. Judgment calls stay prose because no script can make them, but the prose carries the incident that created each rule. A rule with a story attached sticks better than a rule alone.

## If you adopt only three

1. **No unverified work reaches the human.** QA against the acceptance tests, against the deployed thing, every time.
2. **Isolation for parallel agents, enforced by a hook.** Collisions are the most expensive bug class I've had.
3. **File-based state and a ship log.** Sessions are disposable. The record isn't.

None of this makes the model smarter. It removes the failure modes that have nothing to do with intelligence: lost context, drifted intent, unverified claims, parallel collisions, recurring bugs, invisible work. What's left is the model doing what it's good at, writing code against a clear spec, with verification waiting at the exit.

**Next:** [The self-healing loop](/docs/patterns/self-healing-loop/)
