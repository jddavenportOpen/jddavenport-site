---
title: "Write the rules down, then enforce them"
description: "A charter for a multi-agent system, and why every rule that matters eventually needs a hook, a gate or a detector."
section: patterns
group: "Running the org"
order: 160
updated: 2026-10-05
sources: ["frameworks/organizational-charter.mdx", "learn/tier-3/b3-organization-charter.mdx"]
---

Write the rules down so every session starts from the same ones. Then expect the important ones to drift anyway, and give each a hook, a gate or a detector. Prose rules do not survive contact with autonomous agents. Machine enforcement does.

A charter is the document every agent in a multi-agent system is bound by: who reports to whom, who owns what, what needs a human. Mine was ratified on March 27, 2026, before most of the system existed. Writing it early was right. Trusting it alone was not.

## What you'll learn

- What goes in a charter for a multi-agent system
- What I removed, and why
- Four receipts showing prose rules drifting
- How each rule that matters got machine enforcement
- Rules about combinations, not single actions

## What goes in a charter

Keep it short enough that agents actually load it. Mine covers these, and I'd start with the same list:

1. **A mission that works as a filter.** Mine, in short: run the administrative weight of my life so completely that I never have to think about it. It's a test, not a slogan. Work that adds overhead for me is out of scope, however impressive it is.
2. **Hierarchy.** Every agent has one owner. Results flow up one chain, so a failure always has one place to land.
3. **Domain ownership.** Each area has one owning agent. Two agents acting in the same area produce conflicting edits and "who owns this?" arguments.
4. **Verify before surfacing.** I never see broken work. If an agent can't verify it, it doesn't surface it.
5. **A human for irreversible actions.** Sending anything as me, moving money, deleting data, identity and IP decisions: always my yes, no exceptions written in.
6. **Artifacts over conversations.** The deliverable is a file, a commit or a URL, not a chat message about one. "I'll remember" is banned.
7. **Git discipline.** Branch first, focused commits, and everything that matters lives in a repo.
8. **Model routing.** The tier follows the work, and the work's blast radius sets the tier. ([Model routing](/docs/patterns/model-routing/) has the framework.)
9. **Reuse before rebuild.** Check for an existing agent before building a new one.

Here's how one reads in practice. Short, with a stated violation, so there's no arguing about what breaking it looks like:

```markdown
### Verify before surfacing

Before delivering anything to me: run it, open it, load it.
If broken: fix it, don't report it. If unfixable: escalate with a diagnosis.

Violation: delivering an unverified result, a broken link or a
"should work" to me.
```

## What I removed

A charter that never loses a rule is a charter nobody is maintaining.

- **The budget cap and quiet hours** came out on May 25, 2026. Cost is still tracked for visibility, but nothing blocks an agent or pages me over a daily dollar figure. A cap was making quality decisions by clock.
- **The corporate org chart.** The original charter drew a CEO over COO, CTO, CMO and CIO agents. Those were never built as code; their folders held personas and a few stray scripts, and nothing ran them. What runs is organized by area of life and type of work. A note in the charter now says to trust the generated roster, not the old diagram.

## Prose drifts: four receipts

Every one of these was a written rule that agents had loaded.

1. **The worktree rule.** "Background agents that may run git get their own worktree" was in every relevant instruction. Agents still trampled a shared checkout three times in May and again in June, including one `git reset --hard` that wiped another agent's uncommitted work.
2. **The inventory rule.** "Run the list-agents script before spawning a generic agent" was marked non-negotiable on April 30. The script didn't exist until a June 1 audit noticed. For a month, the rule pointed at nothing.
3. **The model table.** My charter has a table of which model each tier uses. As I write this it names a model two generations old. The registry a machine actually reads is current. The prose copy rotted silently, in two places in the same file.
4. **The policy hook.** A safety hook in front of tool calls logged tens of thousands of "allow" decisions and zero blocks in early September 2026. It wasn't broken. Real sends happen inside Python code, out of the hook's sight. The layer actually enforcing was one level down.

The pattern: a rule can be loaded, agreed with, and still not hold, because the agent's context is full of other things, or the rule names something that doesn't exist, or the rule watches the wrong layer.

## The enforcement ladder

For each rule that matters, I ask what makes it hold when nobody remembers it. The answers so far:

| Rule | What enforces it |
|---|---|
| A human yes for anything sent as me | One send gate for every outbound message. Approval tokens are single-use and bound to a hash of the exact recipients, subject and body; change the body and the token dies. A CI check fails the build if any code path sends outside the gate. On its first run, June 30, 2026, it caught five email senders that manual audits had missed. |
| Never raw-restart the session supervisor | A hook blocks the command. Reload scripts refuse while sessions are live and print the casualty list if forced. A detector pages on any cluster of session deaths and names the command that caused it. One raw restart in July killed every live session at once. |
| Worktrees for parallel agents | A pre-commit hook refuses commits on the shared checkout; a watchdog restores it every five minutes. |
| Model choice for agents | The `model:` line is generated from a policy file, with a weekly check. |
| Verify before surfacing | A done gate: production must serve the exact merged commit, and a browser journey must pass against it. |
| Push back, don't be a yes-man | A script injects the posture into every agent definition, so new agents inherit it. |
| Keep instructions small | A pre-commit check caps the main instruction file's size and how much one commit may grow it. History moves to an archive. |

Not everything needs this. A style preference can stay prose. But if breaking a rule costs money, trust or an irreversible action, ask what stops it at 3am when no session remembers it. If the answer is "the charter says so," you don't have a rule yet. The send gate is the clearest case: an autonomous system is only as trustworthy as what stops it.

## Rules about combinations

Some risks don't come from any single action. An agent that holds three things at once (access to private data, exposure to untrusted content, and a channel to send to third parties) can leak data without breaking a single rule. Each leg is allowed; the combination is the problem. This is often called the lethal trifecta.

Per-action guards can't see a combination, so since August 23, 2026 a weekly audit walks every agent definition and its code, classifies each of the three legs, and grades the result against a reviewed ledger. Three details make it hold up:

- **The ledger is a list of mitigations, not an allowlist.** Each accepted case names its controls, and each control has a machine probe that's re-checked every run. If someone deletes or renames the control that made a case acceptable, the audit fails. An allowlist would stay green in exactly that case.
- **You can't regenerate your way to green.** Writing a fresh baseline produces rows with empty controls, and empty controls fail.
- **Blind is a failure.** If the audit can't read the definitions or the ledger, it exits with its own error code and pages, never a quiet skip.

A send to me doesn't count as the third leg. I own my own data; counting messages to me would flag every agent that can page me.

## Where a rule lives decides who obeys it

Instruction files load by location. A rule written in one project's CLAUDE.md never reaches an agent started from another directory. I've had agents in one area of the system refuse things that agents in another area had been doing for weeks, because the rule lived in a file only one of them loaded. So rules every agent needs live in the user-level file, with a line explaining why they're there and not in the project file. [CLAUDE.md](/docs/fundamentals/claude-md/) covers how loading works.

## Where to start

If you're writing your first charter, three rules first:

1. **Hierarchy.** Know who reports to whom.
2. **Verify before surfacing.** A quality gate from day one.
3. **A human for irreversible actions.** Approval for anything that leaves the building.

Add domain ownership, context limits and artifacts when you have more than a couple of agents. Then, for each rule, write down what would enforce it. Build that enforcement the first time a rule gets broken, not the third.

**Next:** [The architecture in one page](/docs/nerve-center/architecture/)
