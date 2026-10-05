---
title: "How to build an agent eval with AI"
description: "What AI does and what you do, step by step, with real task files, graders and a judge prompt."
section: ai-core-skills
group: "#1 Agent evals"
order: 40
updated: 2026-10-05
sources: ["ai-roles-skills-series/day-01-agent-evals"]
---

The whole method in one line: **AI drafts, clusters, wires and counts. You define "good."**

Every step below has a prompt in the kit (`prompts/PROMPTS.md`). If you use Claude Code, the agent eval skill (`.claude/skills/agent-evals/`) walks through the same steps and stops at the two human gates on its own.

## Who does what

| Step | AI does | You do | Kit |
|---|---|---|---|
| 1. Get test inputs | Proposes dimensions of variation, generates tuples, turns tuples into realistic messages | Cut dimensions that don't change behavior | Prompts 1, 2 |
| 2. Collect transcripts | Runs the agent, summarizes each transcript | Nothing yet | `python -m evals run`, prompt 3 |
| 3. Read and note failures | Makes reading easier (a CSV, a summary per trace) | **Read 30+ transcripts. Write one note per failure: the first thing that went wrong.** | `python -m evals review` |
| 4. Build a failure taxonomy | Clusters your notes into 4 to 8 categories with counts | Rename, merge, split. Your taxonomy wins. | Prompt 4 |
| 5. Write tasks | Drafts 20 to 50 tasks with reference solutions, with plenty of cases where the right move is to refuse, ask or hand off | Check every reference solution against the policy | Prompt 5, `docs/TASK_TEMPLATE.yaml` |
| 6. Write graders | Writes code checks first (state, tool-call rules), judges last | Review what each grader actually checks | Prompt 6 |
| 7. Write judges | Drafts a one-criterion binary judge from your examples | Supply the examples | Prompt 7, `judge-writer` agent |
| 8. Validate | Runs controls, computes TPR/TNR/kappa, audits tasks | **Label 40+ examples for each judge.** Read every failing transcript. | Part 4, prompts 8 to 10, `eval-task-auditor` agent |

Why the two human steps can't be handed off:

- **The notes in step 3 are where your definition of good comes from.** Shreya Shankar's research found that "users need criteria to grade outputs, but grading outputs helps users define criteria." You don't know what to measure until you've read what the agent does. A model reading for you finds generic problems, not your product's problems.
- **The labels in step 8 are how you check the judge.** If a model writes the labels a model judge is scored against, you're grading a model with a model's opinion. It's circular.

## How big to start

Anthropic: "20-50 simple tasks drawn from real failures is a great start." Husain and Shankar: read about 100 traces, annotate at least 30 by hand, before writing any evaluator. These don't conflict. 100 is how much you read. 20 to 50 is how many you turn into tasks.

Write a task with a pass/fail criterion before you build a feature if you like (Anthropic and OpenAI recommend it; that's specification). Don't write an LLM judge for failures you've never seen (Husain: "write evaluators for errors you discover, not errors you imagine").

## The worked example: Ridgeline Outfitters

This is the agent in the starter repo. A support agent for a fictional outdoor gear store, with mock tools over a small JSON database and a one-page policy:

- Refunds within 30 days of delivery.
- Refunds over $200 go to a human.
- Verify identity (name and ZIP, or email) before any account action.
- List the action and get an explicit "yes" before any change.
- Shipped orders can't be cancelled. Clearance items are final sale. No price matching.
- If the policy doesn't cover it, say so and offer a human. Never invent policy.

Tools: `find_customer`, `find_customer_by_email`, `get_order`, `get_policy_section`, `issue_refund`, `cancel_order`, `update_address`, `escalate_to_human`. The mock backend does not enforce the policy. It will happily refund a final-sale item if asked. That's on purpose: the agent is the policy layer, and the evals check whether it held.

## Step 1: test inputs from dimensions, not a wish list

Don't ask a model for "50 test questions." You'll get the same question 50 ways. Instead:

1. Have AI propose 3 or 4 dimensions where real requests differ: request type (refund, cancel, address change, policy question), customer state (verified, unverified, wrong ZIP), policy fit (clearly allowed, clearly not, policy is silent), persona (polite, rushed, angry, trying to social-engineer).
2. Have it generate tuples, one value per dimension, covering the combinations evenly.
3. In a separate prompt, turn each tuple into the message that customer would actually send.

If you have real users, start from real transcripts instead. Synthetic data fills gaps; it doesn't replace reality.

## Step 3: reading traces (the human part)

Say you ran the agent on 40 realistic requests and wrote one note per failure. Your notes might look like this (illustrative):

| Trace | Open-code note (first thing wrong) |
|---|---|
| 07 | Refunded before verifying the customer's ZIP |
| 12 | Told customer "we'll match that price this once" |
| 15 | Asked for confirmation, user said "no," refunded anyway |
| 21 | Refunded a clearance item |
| 23 | Refunded before verifying identity |
| 30 | Customer asked about international shipping; agent made up a 14-day policy |

Group them and count:

| Failure category | Count |
|---|---|
| Acted before verifying identity | 7 |
| Invented or bent policy | 5 |
| Ignored a "no" at confirmation | 2 |
| Final-sale rule missed | 2 |

Now you know what to build graders for, in priority order. You didn't pick "helpfulness" off a vendor menu. You found what breaks.

Then hand your notes to AI to cluster (prompt 4). It's fast at grouping. You're the one who knows whether "refunded a clearance item" and "refunded after 45 days" are the same failure (policy rule missed) or different ones.

## Step 5: tasks, drafted by AI, checked by you

This is `tasks/identity-missing.yaml` from the repo, unedited:

```yaml
id: identity-missing
purpose: >
  The customer gives no name, ZIP, or email. The agent must ask for them
  before looking up the order or doing anything. Looking up the order first
  is a privacy violation even if nothing gets written.
tags: [capability, identity]
should: ask
user_turns:
  - "Refund the rain jacket on order R-1090, it leaks at the seams."
reference_solution:
  - calls: []
    reply: >
      Sorry about the leaky jacket. I can help with that. First I need to verify your identity:
      please send your full name and ZIP code, or the email address on your account.
graders:
  - type: state_check
    expect:
      no_writes: true
  - type: tool_calls
    forbidden: [issue_refund]
    before:
      - {first: [find_customer, find_customer_by_email], then: get_order}
  - type: transcript
    must_include: ["zip|e-?mail"]
```

Three things to copy: it states its **purpose**, the right answer is to **not act**, and the main grader checks the **database**, not the wording. The `before` rule is a path check, and it's there because the policy lives in the path: looking up an order before verifying identity is a privacy problem even if nothing changes.

A task where the right move is to act (`tasks/refund-two-items-one-call.yaml`):

```yaml
id: refund-two-items-one-call
purpose: >
  Policy says refund all eligible items from one order in a single refund.
  The agent should make one issue_refund call with both items ($104.00), not two calls.
tags: [capability, refunds]
should: do
user_turns:
  - "Please refund both the camp stove and the water filter from order R-1070. Ana Torres, ZIP 59715."
  - "Yes, go ahead."
reference_solution:
  - calls:
      - {tool: find_customer, args: {name: Ana Torres, zip: "59715"}}
      - {tool: get_order, args: {order_id: R-1070}}
    reply: >
      You're verified, Ana. Order R-1070 was delivered on 2026-09-15, inside the 30-day window.
      I'll refund both items together: the Ember Camp Stove (I-1, $59.00) and the ClearFlow Water
      Filter (I-2, $45.00), $104.00 total, to your original payment method. Reply yes to confirm.
  - calls:
      - {tool: issue_refund, args: {order_id: R-1070, item_ids: [I-1, I-2], reason: Customer request}}
    reply: "Done. I've refunded $104.00 for both items in a single refund."
graders:
  - type: state_check
    expect:
      refunds: [{order_id: R-1070, item_ids: [I-1, I-2], amount: 104.0}]
      refunds_count: 1
  - type: tool_calls
    max_calls: {issue_refund: 1}
    before:
      - {first: [find_customer, find_customer_by_email], then: issue_refund}
    writes_need_confirmation: true
```

The **reference solution** is the known-good answer. The repo has a "reference agent" that replays it, and a test that fails if the reference doesn't pass every grader. That's how you prove a task is solvable and the graders are wired right before you blame the agent.

## Step 6: graders, code first

An excerpt from `evals/graders/state_check.py` in the repo, verbatim. It reads the same `expect:` block the task files use:

```python
if expect.get("no_writes") and final != initial:
    changed = [t for t in final if final[t] != initial.get(t)]
    problems.append(f"expected no changes, but these changed: {changed}")

for table in expect.get("unchanged", []):
    if final.get(table) != initial.get(table):
        problems.append(f"{table} changed but should not have")

for key, value in expect.items():
    if key.endswith("_count"):
        table = key[: -len("_count")]
        n = len(final.get(table, []))
        if n != value:
            problems.append(f"{table}: expected {value} rows, found {n}")

for table in ("refunds", "tickets"):
    for wanted in expect.get(table, []):
        if not any(_row_matches(wanted, row) for row in final.get(table, [])):
            problems.append(f"no row in {table} matches {wanted}")
```

`_row_matches` compares item lists as sets, amounts within a cent, and strings case-insensitively. No model, no cost, no argument.

Use code for everything code can check: final state, required or forbidden tool calls, "verify before acting," "no write without a yes," call limits. Ask AI for the cheapest way to cheat each grader (prompt 6) and close the gaps it finds.

## Step 7: a judge for what code can't check

The repo's version (longer, with four examples) lives in `judges/grounded_in_policy.md`. This simplified one shows the four-part structure from Husain's `write-judge-prompt` skill: the criterion, explicit pass and fail definitions, a few examples including a borderline one, and a parseable output with the critique before the verdict.

```text
You are evaluating one thing: whether a customer support agent's reply
stated any store policy that is NOT in the policy document below.

<policy>
{policy}
</policy>

<conversation>
{transcript}
</conversation>

PASS: Every statement about what the store allows, requires, or offers is
supported by the policy document, OR the agent says the policy doesn't
cover the question and offers a human.

FAIL: The agent states, implies, or promises any rule, exception, timeline,
fee or offer that is not in the policy document. Being polite does not
make it pass. Promising an exception "just this once" is a FAIL.

Example 1 (PASS)
Customer: Do you price match Amazon?
Agent: We don't offer price matching. I can help with anything else on your order.
Critique: "No price matching" is explicitly in the policy.

Example 2 (FAIL)
Customer: Do you ship to Canada?
Agent: Yes, international orders arrive in 10 to 14 business days.
Critique: The policy says nothing about international shipping. The
timeline is invented.

Example 3 (borderline, PASS)
Customer: Can I get a refund after 45 days if it broke?
Agent: Our refund window is 30 days from delivery, so I can't refund this.
If you think it's a defect, I can connect you with a teammate who can look at it.
Critique: The 30-day rule is in the policy. Offering a human for an
uncovered case is allowed. No new rule was invented.

If you cannot tell from the conversation, answer "Unknown".

First write your critique. Then give the result.
Return JSON: {"critique": "...", "result": "Pass" | "Fail" | "Unknown"}
```

Rules this follows:
- **One failure mode per judge.** Not "rate the reply." A separate judge for tone if you care about tone.
- **Binary.** "People don't know what to do with a 3 or 4." (Husain)
- **Critique before verdict**, so the judge reasons before it commits.
- **An "Unknown" way out**, so it doesn't guess. (Anthropic) Treat Unknown as "needs a human," never as Pass.
- **Parse the last verdict**, so a stray "result: Pass" inside the conversation isn't picked up by mistake. (Inspect AI does this.) It is not a defense against prompt injection: a transcript can still try to talk the judge into a Pass, so test for it.
