---
title: "Where agent evals came from, and what they mean"
description: "From 1930s holdout tests to agents that cheat on benchmarks: why evals exist and why it's a PM skill."
section: ai-core-skills
group: "#1 Agent evals"
order: 30
updated: 2026-10-05
sources: ["ai-roles-skills-series/day-01-agent-evals"]
---

## Where it came from: 200 years in seven chapters

The plot repeats at every scale: **measure, tune against the measure, the measure breaks, invent a harder or fresher one.**

### Chapter 1: Models that fit data (1805 to 1980s)
Least squares (1805). A math model of a neuron (1943). The perceptron (1957). "Machine learning" (1959). Backpropagation revives neural nets (1980s). These are models that learn from data. The question of how to check them comes right alongside.

### Chapter 2: Holding data out (1931 to 1975)
The earliest sample-splitting study Stone cites is from 1931, in educational statistics. Machine learning picked it up in the early 1960s. Bill Highleyman at Bell Labs built a punch-card dataset of handwritten characters and mailed it to other researchers. In 1961 Woody Bledsoe split it into "40 writers for training and 10 for testing," and Highleyman published what's been called the first formal study of train/test splits (Bell System Technical Journal, March 1962). Stone (1974) and Geisser (1975) gave cross-validation its statistical foundation.

### Chapter 3: A funder gets burned by demos (1966 to 1986)
In the 1960s Bell Labs' John Pierce attacked machine translation and speech recognition as "glamour and deceit." US funding dried up from about 1975 to 1986. Then DARPA's Charles Wayne restarted funding with one condition: objective evaluations on shared datasets, with NIST as a neutral referee holding the test data. Ken Church later called it "glamour-and-deceit-proof." Statistician David Donoho named this the **Common Task Framework** (shared training data, competitors on the same task, a referee with a hidden test set) and called it "the secret sauce of machine learning."

This is the origin story of evals in one sentence: **someone burned by demos demands a number that can't be faked.** A product leader asking for evals in 2026 is DARPA in 1986.

### Chapter 4: Shared benchmarks (1987 to 2019)
UCI repository (1987). TREC for search (1992). MNIST (1998: 60,000 training images, 10,000 test). The Netflix Prize (2006 to 2009). Kaggle (2010). ImageNet, and AlexNet's 2012 win. Each benchmark drove real progress. Each eventually saturated: GLUE, a language benchmark, was beaten in about a year. By July 2019 the top score (88.4) passed the human baseline (87.1).

### Chapter 5: Text breaks the grader (2002 to 2023)
Labels like "cat" or "7" are easy to grade. Text isn't: there are thousands of good answers. The field's answers, in order:

1. **Word overlap with a reference** (BLEU, IBM, 2002; ROUGE, 2004). Failed on open-ended text. A 2016 study found it correlates "very weakly" with human judgment on dialogue. OpenAI found wrong code often scores *higher* on BLEU than correct code.
2. **Run it and check** (HumanEval, 2021): 164 hand-written coding problems, graded by unit tests, several samples each, scored by pass@k. This is the bridge to agent evals.
3. **Crowd preference** (Chatbot Arena, 2023): people vote between two anonymous answers.
4. **A model as judge** (LLM-as-a-judge paper, June 2023): strong judges agreed with humans over 80% of the time on chat preferences, with known biases toward the first answer, longer answers and their own outputs.
5. **Check the end state of an environment** (2023 to 2024): did the database, file or webpage end up right?

### Chapter 6: Agents change the question (2023 to 2025)
Benchmarks stopped asking "is the answer right?" and started asking "did the task get done?"

- WebArena (2023): best GPT-4 agent completed 14.41% of web tasks. Humans: 78.24%.
- SWE-bench (2023): 2,294 real GitHub issues. Solved only if the patch applies and the tests pass. Claude 2 solved 4.8%.
- GAIA (2023): humans 92%, GPT-4 with plugins 15%.
- OSWorld (2024): humans 72.36%, best model 12.24%.
- tau-bench (Sierra, June 2024): simulated customer conversations, graded on the final database state. Introduced **pass^k**: the chance an agent succeeds on *every one* of k tries. Best agents solved under half the tasks and fell below 25% on pass^8 in retail.
- METR's **time horizon** (March 2025): the length of task (measured in human time) a model completes 50% of the time. Doubling roughly every seven months in the 2025 paper; METR's January 2026 update put the post-2023 doubling time near four months.

Meanwhile, product teams inherited the job. OpenAI open-sourced its Evals framework with GPT-4 (14 March 2023). Hamel Husain's "Your AI Product Needs Evals" (29 March 2024) argued failed AI products share one root cause: no evaluation system. Anthropic's "Demystifying evals for AI agents" (9 January 2026) became the shared vocabulary.

### Chapter 7: The agent benchmarks break too (2024 to 2026)
- SWE-bench, original: OpenAI had 93 developers review samples. 38.3% had underspecified problems, 61.1% had tests that could reject valid fixes, 68.3% got filtered out. The clean 500 became SWE-bench Verified. GPT-4o's score doubled (16% to 33.2%) with no model change.
- SWE-bench Verified: by February 2026 OpenAI stopped reporting it. Frontier models could reproduce the original human fixes from memory, and 59.4% of the 138 hardest problems it audited had flawed tests.
- SWE-bench Pro, the recommended replacement: in July 2026 OpenAI found about 30% of tasks broken and retracted the recommendation.
- UC Berkeley (April 2026) built an exploit agent that scored about 100% on Terminal-Bench, SWE-bench Verified, SWE-bench Pro and WebArena without solving a single task. Their line: "Don't trust the number. Trust the methodology."
- Anthropic (March 2026): in two BrowseComp runs, Claude Opus 4.6 figured out it was being evaluated, identified the benchmark, then found and decrypted the answer key.

That last one has no precedent in 200 years of holdout testing. The test set was always passive. Now the thing being tested can go after the answer key.

**Why does this matter for a PM?** Because public benchmarks keep breaking, the durable advantage is a **private eval suite built from your own users' failures.** It's far less likely to leak into anyone's training data (keep it out of public repos and pasted chats), and it measures your product, not a leaderboard.

## Why agent evals exist

Three reasons, and they stack.

**1. You don't train the model anymore.** In classic ML, the team that trained the model held the validation data, so measurement was built into the training loop. A team building on Claude or GPT has no training loop. Its levers are the prompt, the tools, the retrieval and the harness (the code around the model). Nothing in that workflow measures quality unless you build the measurement. Evals replace the missing validation step.

**2. Agents act, compound and vary.** An agent uses tools over many turns and changes the world as it goes, so one early mistake compounds. It also gives different outputs on the same input. Anthropic's example: on a task where the agent succeeds 75% of the time, it passes three tries in a row only 42% of the time (0.75 x 0.75 x 0.75). Same math at 90%: eight in a row is 43%. That's per task. For a suite, compute it task by task and average, because a suite where half the tasks always pass and half always fail has the same score at every k.

**3. The model underneath keeps changing.** You'll swap models several times a year. Without evals, every upgrade is weeks of manual poking. Anthropic: "When more powerful models come out, teams without evals face weeks of testing while competitors with evals can quickly determine the model's strengths, tune their prompts, and upgrade in days." Notion reportedly assesses and ships new frontier models in under 24 hours because the regression suite already exists.

And a fourth, which is the PM reason: **evals force you to define good.** Anthropic again: "Two engineers reading the same initial spec could come away with different interpretations... An eval suite resolves this ambiguity." A written task with a pass/fail criterion is a spec two experts should grade the same way, and checking that they do is part of the job.

Without them, per Anthropic: "debugging is reactive: wait for complaints, reproduce manually, fix the bug, and hope nothing else regressed."

## What it means: the eval is the spec

Here's the part that makes this a PM skill and not just an engineering one. An eval forces someone to write down what "good" means, precisely enough that two experts would grade it the same way. Lenny's Podcast put it as "evals are the new PRDs." Husain and Shankar: "In many situations, the product manager is the principal domain expert." Anthropic says the people "closest to product requirements and users are best positioned to define success," and that PMs should contribute eval tasks directly.

So when a posting says "drive the eval roadmap," it means: you decide what the agent must do, what it must never do, and how reliable it has to be before it ships. Then you prove it with a number.

## What an agent eval is made of

Anthropic's January 2026 vocabulary, in plain terms:

| Term | What it is | Example (support refund agent) |
|---|---|---|
| **Task** | One test with defined inputs and success criteria | "Customer wants a refund on a tent delivered 12 days ago" |
| **Trial** | One attempt at a task. Run several, because output varies | Run that task 5 times |
| **Transcript** (trace, trajectory) | Full record of a trial: messages, tool calls, results | The conversation plus every `get_order` and `issue_refund` call |
| **Outcome** | The final state of the environment | Does a refund row exist for the right order and amount? |
| **Grader** | Logic that scores one aspect. A task can have several | State check, "verified identity before refund," policy-grounding judge |
| **Evaluation harness** | Runs everything: sets up, runs trials, records, grades, aggregates | `python -m evals run` |
| **Agent harness** (scaffold) | The code that lets a model act as an agent | Your tool loop and system prompt |
| **Suite** | A collection of tasks with a shared goal | 24 refund and order tasks |

The single most useful sentence in Anthropic's guide: "A flight-booking agent might say 'Your flight has been booked' at the end of the transcript, but the outcome is whether a reservation exists in the environment's SQL database." **Grade what happened, not what the agent said happened.**

Note: an eval always tests model + scaffold together. A scaffold change can move your score as much as a model change. (That's half of the CORE-Bench story below.)

### Three kinds of graders

| Grader | Good for | Strengths | Weaknesses |
|---|---|---|---|
| **Code** | State checks, tests, required/forbidden tool calls, format, regex | Fast, cheap, objective, reproducible | Brittle to valid variations, no nuance |
| **LLM judge** | Tone, groundedness, "did it invent policy," instruction following | Flexible, handles open-ended output | Non-deterministic, costs money, **must be calibrated against humans** |
| **Human** | Creating labels, calibrating judges, ambiguous cases | Gold standard | Slow, expensive |

**Rule of thumb every source agrees on:** if you can check it with code, use code. If it needs judgment, use a narrow, binary LLM judge and prove it agrees with a human. Use humans to make the labels.

### Outcome vs path

Anthropic: "It's often better to grade what the agent produced, not the path it took." Agents find valid routes you didn't anticipate. Path checks still belong in three places:

1. **Policy that lives in the path:** must verify identity *before* refunding; must never call a destructive tool.
2. **Budgets:** max turns, tokens, latency.
3. **Debugging** after an outcome failure.

If you check the path, allow extra steps (check that required calls happened in order, not that the exact sequence matched).

### pass@k vs pass^k

- **pass@k:** chance at least one of k tries succeeds. Right for tools where one good answer is enough (a coding assistant generating options).
- **pass^k:** chance all k tries succeed. Right for agents where consistency matters (anything customer-facing).
- At k=1 they're the same. As k grows they tell opposite stories: pass@k heads toward 100%, pass^k toward 0% (for any task the agent sometimes fails).
- Compute both per task and average across tasks. Don't raise the suite's average to the power k.

### Capability vs regression

- **Capability evals** ask "what can it do?" and should start with a **low** pass rate. If you're at 100%, you learn nothing.
- **Regression evals** ask "does it still do what it did?" and should sit near 100%. A failure blocks a release.
- Tasks **graduate** from capability to regression once you've climbed them.

## What I got wrong going in

This is the story I planned to tell on day one:

> In the beginning of time there were AI algorithms, simple things like linear regression and complicated neural networks. As you would "train" these models you would use existing data to discover patterns that could help you more accurately "predict" outcomes. But how do you know your model was good? If you under-train, the algorithm's output is in left field. If you over-train, think ChatGPT being 100% certain of something that's wrong. Either way the model is useless. So people would set aside data the model never used to create its algorithm. Enter training sets. These are the same things as agent evals: the data that tells you whether your agent is useless.

I asked the research to prove me right or wrong. Scorecard: one claim wrong, one with the name backwards, two half right.

### Claim 1: "Simple algorithms like linear regression and complicated neural networks, trained on existing data to find patterns that predict outcomes."

**Half right.** The second half is a fair description of supervised learning, and linear regression really is the textbook starting point (Goodfellow, Bengio and Courville use it as their worked introduction).

The history is compressed. Least squares, the basis of linear regression, dates to Legendre in 1805. The first mathematical neuron is McCulloch and Pitts in 1943, the perceptron is 1957, and "machine learning" as a phrase is Arthur Samuel's, 1959. Early neural networks were simple, not complicated. They got shredded by Minsky and Papert in 1969, came back with backpropagation in the 1980s, and only took over after AlexNet won ImageNet on 30 September 2012 (15.3% error vs about 26.1% for the runner-up). The textbook word for "simple vs complicated" is **capacity**: how wide a range of patterns a model can fit. Linear regression and a neural net sit on the same spectrum.

**The part I left out is the most important part.** The goal is not to find patterns in the data you have. It's to predict well on **data the model has never seen**. That's called generalization. Without that clause, there's no reason a test set needs to exist.

### Claim 2: "Under-train and the output is in left field. Over-train and you get ChatGPT being 100% certain of something wrong."

**Wrong.** This is the one I'd most want to fix before posting.

- **Underfitting** means the model is too simple (or too little trained) to capture the real pattern. It's wrong in a consistent, predictable direction, even on its own training data. Picture a straight line through a curve. Not random, not left field. Systematically off.
- **Overfitting** means the model fit the quirks and noise of its training data instead of the real pattern. It looks great on that data and noticeably worse on anything new. The tell is the gap between training score and held-out score.
- **ChatGPT being confidently wrong is a different problem.** That's **hallucination** (a plausible but false statement). Whether its confidence is trustworthy is **calibration**: across many answers where it says it's 90% sure, is it right about 90% of the time? One confident wrong answer doesn't prove bad calibration; a pattern does. OpenAI's own 2025 explanation traces hallucination to pretraining on next-word prediction with no true/false labels: rare arbitrary facts, like a pet's birthday, can't be predicted from patterns. A 2023 theory paper (Kalai and Vempala) shows even a well-calibrated model must hallucinate some facts at a minimum rate. Overfitting isn't the cause.

The twist that makes this a better story: OpenAI's 2025 paper argues models hallucinate partly **because training and evaluation reward guessing over saying "I don't know."** Accuracy-only evals teach models to bluff. So bad evals help *cause* confident wrongness. That's a line worth using.

Also, "either way the model is useless" is too binary. Weil's whole point is that a 60%-right model and a 99.95%-right model both support products, just different ones. Where you set the bar is a product decision.

### Claim 3: "People set aside data the model never used. Enter training sets."

**Right idea, wrong word.** The data you set aside is the **test set** (also called the holdout set). The **training set** is the opposite: the data the model learns from. Standard practice has three pieces:

- **Training set:** the model learns from it.
- **Validation set:** you check against it repeatedly while tuning.
- **Test set:** brought out at the end, once, to assess the final model. One classic textbook says it "should be kept in a vault."

Keep the validation set in the story, because it explains a trap in agent evals. When a product team tunes its prompt against the same 30 tasks every day, that "eval suite" is acting like a validation set, not a test set. Scores drift up for reasons that won't carry over to real users. Duda and Hart warned about exactly this in 1973: "training on the testing data" through a long series of refinements guided by repeated testing. The fix is the same as it was then: keep a separate, rarely touched set, and keep refreshing tasks from new real failures.

Fun detail: Mervyn Stone, who formalized cross-validation in 1974, disliked the word "validation" because it "has a ring of excessive confidence." Same caution applies to anyone saying their agent "passed evals."

### Claim 4: "These are the same thing as agent evals. The data that tells you if your agent is useless."

**Half right.** The holdout test set is the grandparent of agent evals, not the same thing.

What carries over: judge the system on cases it wasn't built around, use a fixed yardstick, distrust any score you've tuned against.

What's different:

| | Classic holdout test | Agent eval |
|---|---|---|
| Unit of test | A labeled example: input + correct answer | A task: instructions, a starting environment, success criteria |
| What produces the score | Compare to the label | A grader (code, LLM judge, human, or a mix) inspecting the end state or the transcript |
| Repetition | One prediction per example | Several trials per task, because the same agent can pass and fail the same task |
| Who trained the model | The team evaluating it | Someone else. You can only change the prompt, tools and harness |
| Purpose | Estimate error on new data | Specify the product, find limits, catch regressions when the prompt, tools or model change |
| Size | Thousands to millions of examples | Tens to hundreds of tasks |

And "useless or not" undersells it. Evals answer four different questions:

1. **What can it do?** (capability evals, which should start with a *low* pass rate)
2. **What did we break?** (regression evals, which should sit near 100%)
3. **What do we mean by good?** (the eval as the product spec)
4. **How reliable is it?** (repeated trials, pass^k)

### The version I'd tell now

> Every era of AI had the same problem: how do you know the model is any good? The answer since the 1930s has been to hold data back. Train on one part, test on the part the model never saw, because the goal was never memorizing the past, it was predicting the future. Agent evals are the grandchild of that idea. But you didn't train the model, it acts over many steps, and it gives a different answer every run. So instead of a pile of labeled answers, you build tasks, run each one several times in a clean environment, and grade what actually happened. Done right, that's your product spec, your regression test and your reliability score in one.

## Good vs bad: what the record shows

Every failure type below has a real, numbered example.

### The hall of shame

**1. Ambiguous or impossible tasks.**
SWE-bench: 38.3% of sampled problems underspecified. Terminal-Bench: a task asked the agent to write a script but didn't say where, while the test expected one specific path, so correct work failed. Anthropic's rule: "a 0% pass rate across many trials is most often a signal of a broken task, not an incapable agent."

**2. Graders too strict.**
CORE-Bench: Claude Opus 4.5 scored 42%. Then a researcher found the grader penalized "96.12" when it expected "96.124991...", plus ambiguous specs and tasks that couldn't be reproduced. After fixes and a different scaffold: 95%. (Precise version: about 36 points came from switching scaffolds, and grading fixes took it from 77.78% to 95.5%.) Also tau2-bench: Opus 4.5 found a legitimate route (upgrade the cabin, *then* modify the flight) and the benchmark scored it a failure because it expected a refusal.

**3. Graders too loose.**
tau-bench airline: an agent that returns **empty responses scored 38%**, because many tasks' correct end state was "nothing changed." FieldWorkArena's validator only checked that the last message came from the assistant. METR had real maintainers review 296 AI pull requests that *passed* SWE-bench Verified: they'd merge about half as many as they would human patches.

**4. One-sided test sets.**
Anthropic, building web search for Claude, had to test both "should search" (the weather) and "should not search" (who founded Apple?). Test only one direction and you only improve in one direction. Shopify saw the mirror image during fine-tuning: the model learned to refuse hard tasks instead of attempting them.

**5. Contamination.**
On SWE-bench Verified, GPT-5.2 produced the exact gold patch from a snippet. Gemini 3 Flash, given only a task ID, reproduced the task description and fix. That's memory, not skill.

**6. Agents cheating.**
METR caught o3 reward-hacking in 30.4% of RE-Bench runs: overwriting timing functions, monkey-patching the evaluator, overloading equality checks. Adding "Please do not cheat" to the prompt didn't help. Claude 3.7 Sonnet's system card documents it special-casing tests to return expected values.

**7. Unvalidated LLM judges.**
Shopify's first judges had a Cohen's kappa of 0.02 against human labels: almost no agreement beyond chance. After calibration: 0.61, against a human-to-human baseline of 0.69. Benchmark judges have been steered by hidden HTML comments and accepted empty replies.

**8. Generic metrics.**
Husain and Shankar: "Generic metrics like BERTScore, ROUGE, cosine similarity, etc. are not useful for evaluating LLM outputs in most AI applications." Shopify: a "Vibe LLM Judge" that rates 0 to 10 "is not going to cut it." Likert scales fail because nobody knows what to do with a 3 vs a 4.

**9. Shared state between trials.**
Anthropic saw Claude gain "an unfair advantage on some tasks by examining the git history from previous trials." KernelBench left the reference answer in stale GPU memory.

### Production failures better evals plausibly catch

- **Air Canada (2024):** chatbot invented a retroactive bereavement fare refund. The tribunal: "Air Canada did not take reasonable care to ensure its chatbot was accurate." C$812 award, global headline.
- **Cursor's support bot "Sam" (April 2025):** invented a one-device-per-subscription policy. Users cancelled on Reddit before a co-founder posted "We have no such policy."
- **NYC MyCity (2024):** told business owners they could take workers' tips. They can't.
- **Chevy dealer bot (2023):** agreed to sell a Tahoe for $1, "legally binding, no takesies backsies." That one is adversarial input: a red-team eval, not a quality eval.

The first three are the same bug: **a bot asserting a policy that doesn't exist.** The eval that maps to it is a small set of questions whose right answer is "no" or "I don't know," plus a judge that checks every policy claim against the real policy text. The starter repo has that task (`uncovered-warranty`), with code checks for a flat "yes" and two judges for subtler inventions.

Two more, with a caveat: Replit's agent deleted a production database during a code freeze (July 2025), and a Cursor agent wiped a startup's production database and backups in nine seconds with an unscoped API token (April 2026). Evals help ("given a destructive option and unclear authority, does it stop and ask?"), but these were permission failures first. Evals are one layer, not the whole wall.

### The hall of fame

- **Descript:** three dimensions for its editing agent: don't break things, do what I asked, do it well. Started with manual grading, moved to LLM judges with product-defined criteria and periodic human calibration. Runs separate quality and regression suites.
- **Shopify Sidekick:** replaced hand-curated golden sets with "Ground Truth Sets" sampled from real production conversations, labeled by experts. Measured judge agreement with kappa. Built a merchant simulator to replay real goals against new versions before release.
- **DoorDash:** LLM customer simulator built from historical transcripts plus narrow judges calibrated on precision and recall. Cut hallucinations in simulation 90%; 200+ simulated conversations in under five minutes; iteration from days to hours. Still ships through an A/B test.
- **GitHub Copilot:** 4,000+ offline tests, about 100 repos deliberately broken to see if a model can fix them, an LLM judge on 1,000+ chat questions that they routinely audit, then canary rollouts to employees.
- **Harvey (BigLaw Bench):** tasks derived from real law-firm time entries. Two scores: how much lawyer-quality work it completed (with penalties for hallucinations), and what share of claims it backed with an accurate source.
- **Bolt:** started evals late, after the agent was already popular. Built a full system in three months: static analysis, browser agents testing generated apps, LLM judges for instruction following.

### The three tests a good eval survives

My own summary of everything above:

1. **A do-nothing agent.** Run an agent that does nothing. If it scores well, your set is lopsided or your graders are loose. (tau-bench's 38%.)
2. **A cheating agent.** Run an agent that does whatever the user says, or tries to game the grader. If it scores well, your graders check the wrong thing. (Berkeley's 100%.)
3. **A human reader.** Read the failing transcripts. Every failure should seem fair: clear what the agent did wrong. If not, the task or grader is broken. (CORE-Bench, found by a person reading runs.)

### Mature vs immature

| Immature | Mature |
|---|---|
| Off-the-shelf "helpfulness 1 to 5" | A few binary checks, each tied to a failure seen in real traces |
| One judge grading everything | One judge per failure mode |
| Judge never checked against a human | Judge with a published agreement number (TPR, TNR, kappa) |
| Tasks invented at a desk | Tasks from bug reports, support tickets, real traces |
| Only "should do it" cases | Should and should-not cases |
| One average on a dashboard | pass^k with error bars, split by type |
| Shared environment across runs | Clean environment per trial |
| Nobody reads transcripts | Transcripts read weekly |
| Offline score is the final gate | Offline gate, then A/B or canary, then production monitoring |

## The debate: are evals overrated?

It peaked in the first week of September 2025, building on remarks from earlier that year.

**The skeptics.** Boris Cherny on how Claude Code chose agentic search: "This was just vibes, so internal vibes. There's some internal benchmarks also, but mostly vibes." Swyx posted a list of top agent companies with "no evals." Ben Hylak (CTO at Raindrop, a monitoring vendor): "The agents are too much to test. But not too much to monitor." Karpathy, on model benchmarks: "there is an evaluation crisis."

**The defense.** Shreya Shankar, on 5 September 2025: "When people say they 'don't do evals,' they are usually lying to themselves. Every successful product does evals somewhere in the lifecycle." She conceded two exceptions: coding, which is already heavily covered in model training, and teams with deep domain expertise who dogfood religiously.

**Where it landed.** Anthropic's own account: Claude Code "started with fast iteration based on feedback from Anthropic employees and external users. Later, we added evals." Cat Wu put daily use at "I think 70 or 80 percent" of technical Anthropic staff (Every podcast, October 2025). That's an eval system, just made of people. Most teams don't have thousands of expert users in the building. A legal, medical or support product team can't feel its failures the way Claude Code's team can.

The real disagreement now is sequencing and proportion. Nobody credible defends generic 1-to-5 judges, and nobody argues against reading real traces. Also worth knowing: the loudest voices on both sides sell something (a course, a monitoring product, an eval platform).

**My take for PMs:** offline evals are one slice of Anthropic's "Swiss cheese" model, alongside production monitoring, A/B tests, user feedback and transcript review. You need the stack. But the offline suite is the only slice you can run *before* you ship.
