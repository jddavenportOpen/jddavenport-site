---
title: "Agent tracing and evals: a deep dive for aspiring AI PMs"
description: "How to see what an agent did, how to judge whether it was good, and the eval habits Anthropic, Arize and WorkOS shared at AI Engineer New York."
section: ai-core-skills
group: "#2 Agent tracing"
order: 10
updated: 2026-10-13
sources: ["aie-nyc-2026-10-12"]
---

Part of my AI Core Skills series. It builds on [#1 Agent evals](/docs/ai-core-skills/agent-evals/), and if you want posts like this in your inbox, [join the newsletter](https://jddavenport.com/newsletter).

*By JD Davenport. I'm an MBA student at BYU and the founder of AI Foundry, and I run my own multi-agent system, which means I keep finding out where it breaks.*

On October 12, 2026 I spent a day at AI Engineer in New York. Four sessions there, taken together, made the best crash course on agent quality I have found:

- **Lance Martin (Anthropic):** eval design, hill climbing, and cost.
- **SallyAnn DeLucia (Arize AI):** "AI Evaluation 101," a hands-on workshop on LLM-as-judge and on turning traces into datasets.
- **Nick Nisi and Zack Proser (WorkOS):** verification loops for coding agents.
- **CJ Avilla and Harrison Stall (Anthropic):** Claude Managed Agents and Flows, including the ways single agents fail.

This guide is my synthesis. My recordings were rough, so I paraphrase the speakers rather than quote them. Where I could not tell what someone said, I left the point out.

---

## 1. Why this is a PM topic

**The eval is the spec.** In normal software, the PRD says what the product should do and tests check it. With an agent, behavior comes from a model you do not control. So the most precise statement of "what good looks like" is the eval: the cases, the criteria, and the pass bar. Whoever writes that owns the product's definition of quality.

SallyAnn made two points I keep coming back to:

1. **Metrics tell you something might be broken. Evals tell you what the failure is.** A drop in thumbs-up rate is a metric. "The agent ignores the budget on multi-day trips" is an eval finding. You need both.
2. **Every stakeholder helps define success.** Product, engineering, support, domain experts, security. It is not one role's job.

Lance described how his colleagues now work: much more time designing evals and specifying tasks, then letting Claude climb against them. As agents do more of the building, the human job moves toward defining "good" precisely. That is product work.

---

## 2. Tracing: how you see what an agent did

You cannot read an agent's logic the way you read code. The logic is a chain of model decisions made at runtime: which tool to call, what to search for, when to stop. The only place it shows up is in the record of what happened afterward. That record is a trace.

### Trace and span

- A **trace** is the record of one run, from the user's request to the final answer.
- A **span** is one unit of work inside it: an LLM call, a tool call, a retrieval, a sub-agent.
- Spans nest. The top one is the **root span** (in the Arize workshop: the span with no parent). It usually holds the user's input and the final output.

In SallyAnn's demo, a travel-planning agent got a request like "3 days, less touristy, here is my budget." The trace showed a research sub-agent, a tool span that fetched destination data, one LLM span that chose the tool, and a second that summarized its output. Sometimes you have to walk down the tree and back up to understand one decision.

### What to capture on every span

| Field | Why a PM cares |
|---|---|
| Inputs and outputs | You cannot judge quality without them |
| Span type (LLM, tool, retrieval, agent) | Shows where a failure started |
| Model and effort or thinking setting | Lets you compare configurations |
| Prompt or skill version | Ties a regression to a change |
| Tokens, including cache reads | Cost, and whether caching works |
| Latency | User experience |
| Errors and stop reason | Separates "model was wrong" from "system broke" |
| Session ID | Follows multi-turn behavior |

On caching: Lance noted that agents resend most of their context every turn, and the prompt cache only matches an exact prefix, so one small early change breaks it. Anthropic's docs price cache reads at 0.1x base input for most models. Track your cache hit rate. You can only see it if your traces record cache reads.

### Standards and tools

The emerging standard is the **OpenTelemetry GenAI semantic conventions**. They define spans for model calls, agents (`invoke_agent`), and tools (`execute_tool`), with attributes like `gen_ai.request.model` and `gen_ai.usage.input_tokens`. The spec is still marked "development," so expect changes.

Tools you will hear about, in no particular order: Arize (its Phoenix project is open source and built on OpenTelemetry), LangSmith, Braintrust, Langfuse, and the Anthropic Console, which Lance said shows prompt cache hit rate for API apps. His other point: at small scale you do not need a fancy system. Claude can build you a custom data viewer cheaply.

### The loop that matters

1. **Instrument** the agent so every run produces a trace.
2. **Look at the data.** Read real traces. What did users ask? Which tools ran? Would you accept the answer?
3. **Name the failure modes.** Patterns, not single bad runs.
4. **Promote cases into a dataset.** In Arize, that means filtering spans (root spans to judge the final answer, tool spans to judge a tool call) and saving them.
5. **Write an eval** against that dataset, and keep running it.

Lance mentioned feedback from Hamel Husain on Anthropic's eval-building skill: it should walk the user through the raw data first. Lance agreed. Claude is good at scanning logs and flagging likely failures, he said, but the human still has a real role in looking at the data.

CJ and Harrison added one more use. Managed Agents keeps a durable log of every event, so you can hand a week of sessions to a reviewer agent and ask whether any agent did something unexpected or called tools it should not have. Traces are an audit trail, not just a debugger.

---

## 3. Types of evals, and when to use each

| Type | What it is | Use it when |
|---|---|---|
| **Code / deterministic** | A script checks the output: valid JSON, a required field, a passing test | The criterion is objective |
| **LLM-as-judge** | A second model grades against a rubric, returning a label and an explanation | The criterion needs judgment |
| **Pairwise** | A judge picks the better of two outputs | Quality is squishy and absolute scores are noisy |
| **Human review** | People label outputs | Setting the gold standard and checking judges |
| **Agent-as-judge** | A full agent investigates the result with tools | Success is complex, like "did this PR fix the bug" |
| **Small classifier judges** | A fast model returns only a label or probability | High-volume checks where you do not need reasoning |
| **User feedback, business metrics** | Thumbs, retention, resolution rate | Production signals |

Rules that came up across sessions:

- **Use deterministic checks when you can.** Lance said this directly.
- **Explanations matter.** A judge's reasoning shows you why it gave a label, so you are not trusting it blindly.
- **One quality per LLM judge.** SallyAnn's guidance: build several small judges rather than one that checks everything.
- **Start small, grow with usage.** Her own product's agent began with a few evals and now runs 32. A generic template beats no eval, but replace it with specific ones as real data shows what matters.

---

## 4. What makes an eval good

### Lance's four properties

1. **Scales with model.** A stronger model scores higher.
2. **Scales with thinking.** More reasoning effort scores higher.
3. **Headroom at the frontier.** The best model is not already maxed out.
4. **Low run-to-run variance.** Two runs give about the same score.

### The fake headroom trap

Lance sees this constantly, even in popular public benchmarks. Some cases are ambiguous or mislabeled, so no model can pass them. The eval looks like it has 20% left to gain, but nobody can get it, and you burn tokens climbing an eval that is already saturated. His blog post offers a test: you should be able to say why a task is hard before you include it.

### Write criteria a coworker could grade

| Vague | Concrete (travel agent) |
|---|---|
| "Helpful" | Answers the follow-up questions the user asked |
| "Accurate" | Plan matches the requested number of days |
| "Good" | Totals stay within the stated budget |

SallyAnn's framing: describe success the way you would to a coworker, because you are about to describe it to an LLM.

### Grading rules

- **Binary beats 1-10.** Lance called "rate this from 1 to 10" the worst option because it is so noisy. For several dimensions, use several binary checks. Hamel Husain makes the same case in his LLM-as-judge guide.
- **Test the rubric across models.** If 2 or 3 different models grading with it all disagree, the rubric is the problem.
- **Run replicates.** Grade the same outputs several times and check the scores hold.
- **Use smaller, cheaper graders** where they work.
- **Use pairwise for squishy outputs.** It is easier to say why one web page beats another than to score one page from 0 to 5.

### Build the case set carefully

- **Match production.** Lance's overfitting example: one benchmark task needs OCR, so the harness gains an OCR tool that production never needed.
- **Do not build the set from one model's failures.** Intelligence is jagged. A set made only of what a mid-size model fails may be trivial for a stronger one. Choose cases that are hard from first principles and from production data.
- **Start modest.** SallyAnn suggested about 20 traces, 1 dimension, 1 judge. Anthropic's agent-evals post suggests 20 to 50 realistic tasks from real failures.
- **Check the judge against humans.** SallyAnn calls this alignment: label the dataset yourself, run the eval, compare. Then run it online against live traces.

Two terms from Anthropic's post worth knowing: **pass@k** is the chance of at least one success in k tries. **pass^k** is the chance all k succeed. Users who expect it to work every time care about the second.

---

## 5. Hill climbing

With a good eval, you can hand Claude the thing to improve (a prompt, a skill file) and let it iterate: read failures, edit, rerun, keep what helps. Anthropic ships this in Claude Code, described in Lance's September 2026 post.

**How it guards against overfitting.** The eval is split into train and test. The climber only reads train failures and never sees test cases. Both scores are reported every round. **Train rising while test stays flat is the classic overfitting signal.** Lance warned that prompts overfit easily: Claude is very good at wiggling a prompt into a shape that scores well on your eval but not in production.

**What to climb.** Text surfaces like prompts and skills are the best start because they clearly drive the behavior you measure. Harness code works too, but diffs are larger and harder to interpret. Lance's example: a skill that teaches Claude Code about Anthropic's API started at 68% on a docs-based eval, and an autonomous loop improved it substantially by comparing failures to the docs.

**Climbing on cost.** Tell the climber to hold quality and cut cost, and it searches model, effort, and prompt. In the customer-support example in Lance's post, a prompt audit plus model selection cut cost from 4.6 cents to 1 cent per ticket while accuracy on the search tickets rose from 74.4% to 98.9%. Two takeaways:

- A saturated eval is still useful for cost work: fix quality, burn down cost.
- A bigger model at low effort is often cheaper than a smaller model at high effort, because it needs fewer tokens. Lance offered this as a broad pattern his team sees, not a law. Test it on your own eval.

He also said older prompting habits, like "double-check your work" rituals, can add cost on frontier models, and contradictory rules confuse newer models more than older ones. A prompt audit is often the cheapest first win.

**When the climb gets stuck.** It is **not guaranteed to converge**. When it stalls, the cause is usually the eval: ambiguous instructions, bad labels, faulty grader examples. Anthropic's climber now clusters remaining failures by root cause after a few stuck rounds. In Lance's own run, that step found ambiguous cases and rewrote them. **A stuck climb means audit the eval.**

---

## 6. Verification: proof over claims

Evals measure a system across many cases. Verification asks a narrower question on each run: did the agent actually do what it says?

### Receipts

Nick and Zack's core idea: status comes from records, not from the model's description of its own work. "It passes" is a claim. A test result, a screenshot, a recording of the flow, or an API check that the PR exists with passing merge checks is a receipt. Two warnings from them:

- **A screenshot can lie.** It may show a state reached by a path no user could take. Proof should run start to finish.
- **Receipts go stale.** In their demo, the latest receipt said "fail," but it was for code that no longer existed.

Keep receipts from every run anyway. They become your future eval dataset.

### Verifier CLIs

Their top recommendation: build an app-specific verifier CLI. Their demo tool could check health (`doctor`), drive the app (`join`, `reload`), inspect state (`storage`, `snapshot`, `screenshot`), run a deterministic proof (`prove`), and use a fast, cheap model as a `judge` for near misses, like a confirmation message worded differently but meaning the same thing.

The PM translation: **a command that tells an agent "you are done when this returns pass" is a spec an agent can execute.** Give it the outcome and the check, not a step-by-step path. Write detailed error messages, because an agent can recover from a clear failure on its own. The cheapest start: tell agents, in the repo's agent instructions file, to run the verifier before opening a PR.

### Why an agent should not grade its own work

CJ and Harrison named three single-agent failure modes:

1. **Agentic laziness.** Asked to check 50 services in an outage, an agent that sees 35 healthy ones can talk itself out of checking the rest.
2. **Self-preferential bias.** Ask an agent to write a poem, then ask if it is good: it says yes. Same with code.
3. **Goal drift.** In a long, repeatedly compacted context, an early rule like "don't touch production" can get lost.

Their fixes: give each unit of work its own narrowly scoped agent so you know every item was checked, copy the goal into every sub-agent, and review with a separate agent in an isolated context. This is why you design separate judges and verifiers, and why I treat any agent's "done" as a claim until a receipt backs it.

---

## 7. How I do it in my own system

I built a small eval framework for my own agents. One suite is on the scoreboard today: a classifier that labels job postings.

- **64 labeled cases, split 23 train, 10 validation, 31 test.** Splits come from a hash of each case ID, so adding cases never moves old ones.
- **Deterministic grader**, because the labels are objective. When I use LLM judges, the framework only allows named binary criteria, never a 1-10 scale.
- **3 replicates per run.** Variation is low: about 0.015 standard deviation across reps, and 1 of 31 test cases flips between runs.
- **Grader self-test.** Every case has a known-good output that must pass, and an empty output must fail.
- **Errors are not zeros.** A timeout goes to an error log, not into the score as a wrong answer.
- **The hill climber reads train failures only.**

The honest part: the test score is about 82%, and the audit warns that with 31 cases and 3 reps, the **noise floor is about ±10 points**. A larger model scored about 87%. That looks better, but it sits inside the noise, so my eval cannot yet say whether the bigger model is better. The fix is more test cases, not a better story. **An eval has to be big enough to detect the change you care about before you trust it.**

---

## 8. Your first week: a checklist

Do this with any agent you can get your hands on, including one you build in a weekend.

1. **Instrument one agent.** Every span records input, output, model, tokens, latency, errors.
2. **Read 50 traces.** Write one line each: acceptable or not, and why.
3. **Name 3 to 5 failure modes** from those notes.
4. **Write 5 binary criteria** a coworker could grade without asking you questions.
5. **Build a 30-case set** from real traces, sampled to match real usage, with a train/test split.
6. **Hand-grade 10 cases** to check any LLM judge against.
7. **Run it on 2 models, 3 times each.** Does the bigger model score higher? Are scores stable? Is there headroom?
8. **Audit the eval.** Find cases that flip between runs or that every model fails. Fix or drop them.
9. **Try one improvement**, then compare train against test. Then try a cheaper configuration and see if quality holds.
10. **Write one page** on what you measured, found, and would do next. That page is an interview artifact.

---

## 9. Interview-ready talking points

1. **"The eval is the spec."** For an agent, the eval set and its pass criteria are the most precise definition of quality, and defining them is product work.
2. **Metrics vs evals.** Metrics say something moved. Evals say what failed and why.
3. **Traces and spans.** A trace is one run end to end; spans are its steps. You debug agents by reading traces, then promote failures into a dataset.
4. **Picking a grader.** Code for objective checks, binary LLM judges for judgment, pairwise for squishy quality, humans to set the standard and check the judges.
5. **Trustworthy evals.** They scale with model and thinking, have headroom, have low variance, and contain no ambiguous cases faking headroom.
6. **Overfitting.** Train/test split. The warning sign is train up, test flat.
7. **Cost is an eval dimension.** Hold quality, search model, effort, and prompt for something cheaper. Watch cache hit rate.
8. **Proof over claims.** Agents return receipts, not assertions, and do not grade their own work because of self-preferential bias.

---

## Further reading

- Anthropic Engineering, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (January 2026). Grader types, transcripts, pass@k and pass^k.
- Lance Martin, [Automating eval design and hillclimbing with Claude](https://claude.dev/blog/automating-eval-design-and-hillclimbing/) (September 2026). Eval properties, train/test split, the cost example above.
- Lance Martin, Gabe Cemaj, and Michael Cohen, [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) (April 2026).
- Hamel Husain, [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/).
- Hamel Husain, [Using LLM-as-a-Judge For Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/).
- Aman Khan (Arize AI), interviewed in [The AI Skill That Will Define Your PM Career](https://creatoreconomy.so/p/ai-skill-that-will-define-your-pm-career-aman-khan).
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai).
- [Arize Phoenix documentation](https://arize.com/docs/phoenix).
- Anthropic, [Prompt caching documentation](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching).

Hamel Husain and Aman Khan were the two names people in the room pointed me to for evals.

*If you're working on this too, I'd like to compare notes. Tell me what your first 50 traces showed you.*
