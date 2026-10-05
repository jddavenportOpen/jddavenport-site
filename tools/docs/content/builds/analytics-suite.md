---
title: "The analytics suite"
description: "Seven statistical playbooks, a classifier, a solver that computes and a verifier. Tool use beat model choice by a mile."
section: builds
group: "School and work"
order: 120
updated: 2026-10-05
sources: ["learn/tier-3/g2-analytics-suite.mdx"]
---

In April 2026 I had a take-home MBA analytics final coming, and the course allowed LLMs. So the real question wasn't whether to use a model. It was which setup gets the right numbers. I built one in a day, on top of a stats engine I already had, and tested it against frontier models answering cold. The setup that computed scored 30 of 30 on the practice exam. The models that didn't compute landed between about 15 and 21, no matter which model it was.

That gap is the whole lesson. A statistics question about a 3,000-row dataset has one right answer, and you only get it by running the regression.

## What it is

The analytics suite is a small, opinionated solver for business-school statistics. It isn't a general coding assistant. It knows seven kinds of problems and has a playbook for each.

| Playbook | What it handles |
|---|---|
| SQL | Query construction, aggregation, window functions |
| Regression | OLS, with an enforced diagnose-before-escalate order |
| Random forest | Feature importance, thresholds, precision and recall tradeoffs |
| Logistic | Logit models, threshold choice, reading a confusion matrix |
| K-means | Elbow and silhouette, and never R-squared as a cluster metric |
| Conjoint | Part-worth utilities, attribute importance, share and revenue questions |
| Text analytics | Sentiment, themes, prompt patterns for qualitative data |

Around the playbooks sit three pieces:

1. **A problem parser** reads a question and classifies it into one of the seven topics.
2. **A solver** loads the actual data file and runs the computation with pandas, statsmodels and scikit-learn, then exports the work as a notebook a human can audit.
3. **A verifier** sanity-checks the output against rules that catch obvious screw-ups: R-squared outside 0 to 1, feature importances that don't sum to one, an AUC below 0.5, an empty cluster, a query that returned zero rows.

```bash
python3.12 -m agents.analytics_suite parse "<question>"
python3.12 -m agents.analytics_suite solve "<question>" --data <file>
python3.12 -m agents.analytics_suite topics
```

The model plans and interprets. The tools compute. The verifier checks. Keeping those jobs separate is what lets you check each one on its own.

## The rule the solver can't skip

The most important part isn't the solver. It's a constraint on what the solver is allowed to do.

The course taught a specific order for regression problems, and the tempting mistake is to skip it: jump straight to Ridge, LASSO or a random forest without first checking whether a cleaned-up OLS model already answers the question. So the order is written into the regression playbook as a rule:

```text
1. Diagnose   fit OLS; check the R-squared vs adjusted R-squared gap, VIFs, F p-value, residuals
2. Refine     backward variable selection, dropping the highest p-value each pass
3. Validate   train/test split on the refined model only
4. Escalate   Ridge, LASSO or a forest ONLY if step 3 shows refined OLS can't meet the need
```

The regression playbook does steps one through three in code: fit OLS, drop predictors by backward selection, validate on a held-out split. There's no shortcut to a regularized model inside it. Step four is a deliberate, separate decision, and the rule file says when it's allowed.

This came out of the course, not out of general machine-learning habit. A few days after the first build, the [course-expert agent](/docs/builds/course-expert-agents/) audited the suite against the actual course materials and found exactly this gap. That's the right direction for a domain tool: derive the constraints from the domain, then enforce them in code. The same audit produced a handful of Claude Code skills (regression diagnostics, logistic classification, survey analysis, data prep, picking the right tool) that carry the course's checklists into any future session.

## The test

The build took one day, on April 18, 2026, in six milestones: integration smoke test, a cheat sheet built from my own graded work, the seven playbooks, the parser, the solver with notebook export, and an end-to-end run across all seven topics.

Then the practice exam. It had 19 questions worth 30 points: regression, logistic models, clustering, conjoint, random forests. The pipeline downloaded the real data files, computed every answer, and for the conjoint questions drove a browser against the survey platform's simulator and read the results off the page.

| Setup | Score on the practice exam (of 30) |
|---|---|
| The pipeline (computes on the data) | 30 |
| Frontier models answering without tools | about 15 to 21, across several models and runs |

Every answer the pipeline selected matched the answer key. Three separate models, from two vendors, then reviewed the pipeline's answers seeing only the questions, the data and the answers, with no key, and none of them flagged a wrong one. One flagged the conjoint answers as hard to verify, because a text-only judge can't re-run the simulator. Fair point, and a good reminder to ask what your judge can actually check.

> **Note:** The models in the comparison were run without data access on purpose. This measures tool use against no tool use. It is not a ranking of models. One of them scored the same with and without the data pasted into the prompt, because pasting a CSV into context isn't the same as computing on it.

## What the numbers say

The spread between frontier models was about six points. The gap between computing and not computing was nine to fifteen points. Honest read: if you're choosing between a better model and giving your current model a way to run code against the real data, give it the tools first.

A model reading a question about employee satisfaction will produce a plausible paragraph. A solver that loads the file, drops the noise predictors, checks the VIFs and prints the coefficient table produces the right number. Plausible and right look identical until someone checks.

## What to copy

- **Separate plan, compute and check.** Parser, playbook, solver, verifier. Each one can be tested alone.
- **Write the domain's order of operations into code.** A rule in a prompt gets skipped under pressure. A rule in the solver doesn't.
- **Export the work, not just the answer.** The notebook is what lets a human audit a number in a minute.
- **Benchmark against the no-tools baseline.** If your fancy setup doesn't beat a model answering cold by a wide margin, you built the wrong thing.

The suite was built for school, but the pattern is the same one behind the rest of the system: agents decide what to do, deterministic code does the part that has to be right.

**Next:** [The BYU AI Foundry](/docs/builds/byu-ai-foundry/)
