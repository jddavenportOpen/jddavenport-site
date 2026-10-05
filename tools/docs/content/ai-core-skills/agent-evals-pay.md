---
title: "What top PM roles pay for agent evals"
description: "The real job postings, checked, and an honest read on what the numbers mean."
section: ai-core-skills
group: "#1 Agent evals"
order: 20
updated: 2026-10-05
sources: ["ai-roles-skills-series/day-01-agent-evals"]
---

Here is what the postings say. The two Anthropic rows marked "verified" I re-checked on Anthropic's live job board on 5 October 2026. The rest come from a research pass the same day.

| Role | Company | Posted base | Eval language in the posting |
|---|---|---|---|
| Product Manager, Claude Science (verified) | Anthropic | $305,000 to $385,000 | "Have personally built evals or benchmarks for model capabilities, ideally agentic or scientific ones." Also: "build and shape evals grounded in real scientific workflows, surface failure modes from real usage." |
| Product Manager, Research (Code) (verified) | Anthropic | $305,000 to $385,000 | "Synthesize user insights into actionable requirements and evaluations." |
| Product Manager, Claude Code Model Performance | Anthropic | $305,000 to $460,000 reported | The research pass recorded "Have personally built agentic evals (e.g. SWE-bench-style task suites)." It was no longer on Anthropic's board when I re-checked, so treat it as closed. |
| Product Manager, Core Models | OpenAI | $347K to $490K plus equity | Define success across offline evaluations and online product metrics; "distinguish a useful metric from a convenient one"; build reusable platforms for evaluation. |
| Product Management, Research | Anthropic | $305,000 to $385,000 | None |
| Product Manager, API Agents | OpenAI | $293K to $325K plus equity | None, even though the role is about agents |
| Staff Product Manager, AI Platform | Databricks | $171,000 to $235,200 | None |

**Honest read:**

1. At frontier labs, $250k understates it. Posted base bands start around $293k to $347k before equity.
2. Inside the same lab, the eval-heavy PM roles sit in the same band as PM roles with no eval wording. So the band reflects "PM at a frontier lab at this level." Evals are a requirement for some of those seats, not a premium on top.
3. Outside the labs, $250k is mostly a total-comp number, not a base number. A June 2026 recruiter guide (KORE1) puts US AI PM base pay at $165K to $238K (25th to 75th percentile) and total comp at $244K to $390K, median $305K.
4. Eval requirements cluster in PM roles that sit next to research and model quality. Product-surface roles (like OpenAI's API Agents PM) don't mention them.
5. Nobody has a dataset comparing PMs with and without eval skills at the same company and level. Anyone quoting an "eval premium" is guessing.

**The sentence I can defend:** PM roles at frontier labs that ask for hands-on eval building post base salaries starting around $300k before equity, and senior AI PM roles elsewhere commonly clear $250k in total comp.

**Who's saying evals matter, and what they actually said:**

- Kevin Weil, then OpenAI CPO, on Lenny's Podcast (April 2025): "Writing evals is going to become a core skill for product managers." His point around it: a model that is right 99.95% of the time and one that is right 60% of the time need completely different products. That is a forecast, and it is about product design, not pay.
- Garry Tan (Feb 2025): "Evals are emerging as the real moat for AI startups." About startup defensibility.
- Greg Brockman (Dec 2023): "evals are surprisingly often all you need."
- A line attributed to Anthropic CPO Mike Krieger ("writing evals is probably the most important thing") circulates through Lenny Rachitsky's April 2025 post. I couldn't find the original venue, so I treat it as secondhand.
- Lenny's Podcast billed its episode with Hamel Husain and Shreya Shankar as "Evals are the new PRDs." Worth noting they teach the most popular paid evals course (5,000+ students at $4,200 as of October 2026), so the signal comes with an incentive.

There is also a dedicated eval job market. One specialist board tracked 1,119 open evaluation, post-training and red-teaming roles at 176 companies on 4 October 2026, median top-of-band $330,000. Almost all of them are engineering and research roles. For PMs, evals are a skill inside the job, not the job title.
