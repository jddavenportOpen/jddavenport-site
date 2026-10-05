---
title: "Agent evals reference: real tasks, tools, learning path"
description: "Real benchmark task files, the October 2026 tool landscape, a learning path, the interview angle, and sources."
section: ai-core-skills
group: "#1 Agent evals"
order: 70
updated: 2026-10-05
sources: ["ai-roles-skills-series/day-01-agent-evals"]
---

## Part 6: Real task files from real benchmarks
Reading professional task files is the fastest way to see what "good" looks like.

**tau2-bench airline, task 0: testing a correct refusal.**

```json
{
  "id": "0",
  "description": {
    "purpose": "Testing that agent refuses to proceed with a cancellation that is not allowed even if User mentions that she had been told she didn't need insurance."
  },
  "user_scenario": {
    "instructions": {
      "reason_for_call": "You want to cancel reservation EHGLP3. It may be more than 24 hours after booking, but it is ok because you were out of town for that time.",
      "task_instructions": "If Agent tells you that cancellation is not possible, mention that you were told that you didn't need to get insurance because your previous trip was booked with the same agency with insurance. You don't want to cancel if you don't get a refund.",
      "known_info": "You are Emma Kim. Your user id is emma_kim_9957."
    }
  },
  "evaluation_criteria": {
    "actions": [],
    "nl_assertions": ["Agent should refuse to proceed with the cancellation."],
    "reward_basis": ["DB", "COMMUNICATE"]
  }
}
```

The instructions go to a second model playing the customer, and they include a push. The expected action list is empty, because the right answer is to change nothing.

**tau-bench retail, task 0: graded by database state.** The simulated customer, Yusuf Rossi, wants to exchange a keyboard and a thermostat in one go. The agent sees only the conversation, 16 tools and a policy that says "obtain explicit user confirmation (yes) to proceed." Grading: reload a fresh database, replay the correct actions, hash it, compare to the hash of the database the agent left. Binary. The path isn't scored.

**WebArena task 465.** "Add Tide PODS Spring Meadow Scent HE Turbo Laundry Detergent Pacs, 81 Count to my wish list." The grader opens the wishlist page afterward and checks the text contains the product.

**OSWorld.** "The volume of my system is too small. Can you help me turn up to the max volume?" The grader runs a shell command on the VM, reads the volume, expects 100.

Same pattern every time: **a plain-language instruction, an environment you can reset, and a grader that checks the outcome.**

---

## Part 7: Tools, a learning path, and the interview
### Tools, as of October 2026

Tools are secondary. Every practitioner says to start in a spreadsheet or notebook. Husain: "I have no favorite vendor. At the core, their features are very similar." When you're ready:

| Tool | Best for | Open? | Note |
|---|---|---|---|
| **Promptfoo** | YAML test cases with code and LLM-rubric checks, in CI | MIT | Acquired by OpenAI (March 2026); still open source. OpenAI's recommended migration path. |
| **Inspect AI** | Python evals with agent sandboxes (Docker), 200+ prebuilt evals | MIT | From the UK AI Security Institute |
| **Harbor** | Containerized agent tasks, Terminal-Bench format | Apache-2.0 | The official Terminal-Bench 2.0 harness |
| **DeepEval** | pytest-style LLM tests | Apache-2.0 | |
| **Braintrust** | Hosted evals plus production tracing | Proprietary (autoevals lib is MIT) | Notion, Replit, Ramp |
| **LangSmith** | Tracing, datasets, evals in the LangChain world | Proprietary | Free tier |
| **Langfuse** | Self-hosted tracing and evals | MIT | Acquired by ClickHouse (Jan 2026) |
| **Arize Phoenix** | Tracing and evals, self-hostable | Elastic License 2.0 (source-available) | |

**Watch out:** OpenAI's hosted Evals product goes read-only on 31 October 2026 and shuts down 30 November 2026. Any 2025 tutorial built on the Evals API or dashboard is legacy.

My suggested stack for a beginner: spreadsheet for the first 50 to 100 traces, the starter repo or Promptfoo for tasks and graders, Inspect or Harbor once you need sandboxes, a tracing platform only when you have production traffic.

### A learning path (about 25 to 30 hours)

1. **Orientation (3 to 4 hours).** Read Anthropic's "Demystifying evals for AI agents." Skim Husain and Shankar's evals FAQ. Read Eugene Yan's "Product Evals in Three Simple Steps."
2. **First evals, no agent (4 to 6 hours).** Anthropic's free `prompt_evaluations` course (nine notebooks) or the `building_evals` cookbook notebook.
3. **Agent concepts (2.5 hours).** DeepLearning.AI's free "Evaluating AI Agents" short course: tracing, router and trajectory evals, improving a judge.
4. **Weekend project (12 to 16 hours).** Clone the starter repo (https://github.com/jddavenportOpen/agent-evals-starter). Run the controls. Run Claude. Read every failing transcript. Add five tasks from failures you saw. Write and validate one new judge.
5. **Read real benchmarks (2 to 3 hours).** One tau-bench task and its policy file, one Terminal-Bench task directory, a few WebArena configs.
6. **Go further (optional).** The recipe-chatbot homeworks, the Husain and Shankar Maven course ($4,200, six weeks), or their O'Reilly book, *Evals for AI Engineers*, due late October 2026.

### How to talk about this in a PM interview

If a posting says "have personally built agentic evals," here's what they're probing:

1. **Did you look at data before picking metrics?** Say how many traces you read and what the top three failure categories were, with counts.
2. **Can you write a task two experts would grade the same way?** Show one. Show its reference solution.
3. **Do you know why outcome grading beats path grading, and when it doesn't?**
4. **Did you validate your judge?** Have a TPR and TNR on a held-out set ready. "We checked it against 120 human labels" beats "we used GPT as a judge."
5. **Do you know pass@k from pass^k, and which one your product needs?**
6. **Do you know what broke?** The CORE-Bench and tau-bench stories show you understand evals fail in both directions.
7. **What decision did the eval change?** A shipped model swap, a blocked release, a prompt change you reverted. Evals are only worth something if they changed a call.

A story shape that works: "Users said the agent felt worse after we switched models. We had no way to check. I read 80 transcripts, found three failure types covering most of the complaints, turned them into 30 tasks, validated a judge for the fuzzy one at 0.9 TPR, and from then on every model swap ran the suite first. The next upgrade shipped in two days instead of two weeks."

Make yours true. Then go build the thing so it is.

---

## Sources
The core reading, in the order I'd read it:

- Anthropic, "Demystifying evals for AI agents" (9 Jan 2026): anthropic.com/engineering/demystifying-evals-for-ai-agents
- Hamel Husain and Shreya Shankar, "AI Evals: Everything You Need to Know" (FAQ): hamel.dev/blog/posts/evals-faq/
- Hamel Husain, "Using LLM-as-a-Judge For Evaluation" (Oct 2024): hamel.dev/blog/posts/llm-judge/
- Eugene Yan, "Product Evals in Three Simple Steps" (Nov 2025): eugeneyan.com/writing/product-evals/
- Shreya Shankar, "In Defense of AI Evals, for Everyone" (Sep 2025): sh-reya.com/blog/in-defense-ai-evals/
- Anthropic, "A statistical approach to model evaluations" (Nov 2024): anthropic.com/research/statistical-approach-to-model-evals
- Yao et al., tau-bench (June 2024): arxiv.org/abs/2406.12045
- Zhu et al., "Establishing Best Practices for Building Rigorous Agentic Benchmarks" (2025): arxiv.org/abs/2507.02825
- UC Berkeley RDI, "How We Broke Top AI Agent Benchmarks" (Apr 2026): rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/
- OpenAI, "Why SWE-bench Verified no longer measures frontier coding capabilities" (Feb 2026): openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- METR, "Recent frontier models are reward hacking" (June 2025): metr.org/blog/2025-06-05-recent-reward-hacking/
- Shopify Engineering, "Building production-ready agentic systems" (Aug 2025): shopify.engineering/building-production-ready-agentic-systems
- DoorDash, simulation and evaluation flywheel (Jan 2026): careersatdoordash.com/blog/doordash-simulation-evaluation-flywheel-to-develop-llm-chatbots-at-scale/
- Hardt and Recht, *Patterns, Predictions, and Actions*, "Datasets" chapter: mlstory.org/data.html
- Goodfellow, Bengio and Courville, *Deep Learning*, Chapter 5: deeplearningbook.org/contents/ml.html
- OpenAI, "Why language models hallucinate" (Sep 2025): openai.com/index/why-language-models-hallucinate/
- Moffatt v. Air Canada, 2024 BCCRT 149

Job postings (read 5 Oct 2026): Anthropic Claude Code Model Performance PM (job-boards.greenhouse.io/anthropic/jobs/5247640008), Anthropic Claude Science PM (job-boards.greenhouse.io/anthropic/jobs/5394887008), OpenAI Core Models PM (openai.com/careers/product-manager-core-models-san-francisco/).

A note on quotes: the Anthropic job postings were re-checked against Anthropic's live job board on 5 October 2026. Other quotes come from the published pages and posts linked above; tweet wording comes from the posts as indexed, so follow the links if you want to quote them yourself.
