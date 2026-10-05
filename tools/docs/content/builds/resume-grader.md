---
title: "Build your own resume grader"
description: "One Claude call scores any resume against any job on a six-dimension rubric. Run mine, then write your own in about 40 lines."
section: builds
group: "School and work"
order: 140
updated: 2026-10-05
sources: ["tutorials/build-your-own-resume-grader.mdx"]
---

One Claude call can score any resume against any job posting and tell the candidate exactly what's missing. No vector database, no fine-tuning, no labeled data. A fixed rubric, the posting pasted into the prompt, and a little deterministic code around the answer.

I built this for the [BYU AI Foundry jobs board](/docs/builds/byu-ai-foundry/) in July 2026. When the board launched with around 10,000 openings, AI had written the scraper and the site, but the grader was the only AI actually running inside the product. Everything else was ordinary code an agent happened to write. So I open-sourced the one part that mattered: [jddavenportOpen/resume-grader](https://github.com/jddavenportOpen/resume-grader), MIT licensed.

This page runs the repo, explains the design, then has you write your own version in Python.

## What you'll learn

- How a single LLM-as-judge call grades against a universal rubric
- Why this is not RAG, and when retrieval would actually help
- How to run the repo's CLI on your own resume
- How to write the same grader yourself in about 40 lines

## The design in one picture

```text
job posting URL -> pull the description from the posting's public API -> plain text
resume file     -> plain text
                         |
                         v
        ONE Claude call (system prompt: "you are the hiring manager")
                         |
                         v
    six subscores -> fixed weights in code -> score 0 to 100
    + 3 to 6 specific gaps
    + a one-sentence verdict
```

Three steps:

1. **Ingest.** Pull the job description from the posting's public applicant-tracking API. Greenhouse, Lever and Ashby each publish one. Each is a branch of about 30 lines.
2. **Normalize.** Every ATS returns different broken HTML. Decode it, strip it, flatten it to text.
3. **Grade.** One Messages API call. Claude returns JSON. Code applies the weights and clamps the result.

### The rubric

| Dimension | Weight | Question |
|---|---:|---|
| keyword | 25 | Do they have the hard skills and tools the role requires? |
| experience | 20 | Is their domain and functional experience actually relevant? |
| impact | 15 | Concrete results with numbers, or just responsibilities? |
| structure | 15 | Is the resume clear and fast to evaluate? |
| semantic | 13 | Does the overall trajectory fit this role and company? |
| seniority | 12 | Do level, scope and years match? |

Weights sum to 100. The model never does the arithmetic. It scores each dimension, and code computes the composite. That split matters: models are decent at judging a dimension and unreliable at weighted sums.

### Why it scales to any job

The rubric is universal and the posting is the only variable. The same six dimensions grade a barista and a principal product manager, and there's zero per-role code. A new job source is one adapter. A posting with almost no text (a link-out with no body, under 120 characters) gets graded conservatively on title, company and level instead of failing.

### Be honest about what it is

It's an **LLM-as-judge**, not retrieval-augmented generation. There's no vector store and no retrieval step, because the job description is already in hand. Putting a document you already have in the prompt is called context injection, and it's the right design when the context fits. Calling it RAG would be marketing.

## Step 1: run mine

You need Node 18 or newer (for built-in `fetch`) and an Anthropic API key. The CLI has no dependencies.

```bash
git clone https://github.com/jddavenportOpen/resume-grader
cd resume-grader
export ANTHROPIC_API_KEY=your-key-here
export RESUME_GRADER_MODEL=claude-sonnet-5
```

The repo's built-in default model id dates from July, so set the variable to a current model. Then save your resume as plain text, paste a job description into a text file, and grade:

```bash
node examples/grade-cli.mjs --resume ./resume.txt --jd ./job.txt \
  --title "Product Manager" --company "Example Co"
```

Or point it at a Greenhouse posting and let it fetch the description itself:

```bash
node examples/grade-cli.mjs --resume ./resume.txt \
  --title "Product Manager" --company "Example Co" \
  --url https://job-boards.greenhouse.io/<company>/jobs/<id>
```

> **Note:** The CLI's `--url` fetch only handles Greenhouse. The library code in `src/ingest.ts` also handles Lever and Ashby. For anything else, paste the description into a file and use `--jd`.

You get a fit score, the six subscores, a one-line verdict, and a "what to fix" list.

## Step 2: read the prompt

Open `src/grade.ts`. The whole trick is about 30 lines of prompt. The system message casts the model as the hiring manager for this specific role and tells it what the numbers mean:

```text
You are the hiring manager for this specific role. You have read hundreds of
resumes and you know exactly what you want. Be honest and direct. Never inflate
scores. A 70+ means you would likely call them. A 50-69 means maybe with
reservations. Below 50 means you would pass. Ground every judgment in evidence
from the resume and the job posting. Do not invent requirements the job posting
does not state. Output ONLY valid JSON.
```

(Lightly edited for punctuation.) Three things do the work:

- **A persona with stakes.** "Would you call them in" is a decision, not a vibe.
- **Anchors on the scale.** Without "70 means you'd call them", every model drifts toward a polite 75.
- **"Do not invent requirements."** Otherwise the judge grades the job it imagines, not the one posted.

The user prompt then asks for the six subscores and three to six specific gaps, each pointing at something concrete, like "the posting requires Python and your resume only mentions Excel." Generic advice is explicitly banned.

## Step 3: write your own

Here's the same grader in Python, small enough to read in one sitting. Install the SDK first:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your-key-here
export GRADER_MODEL=claude-sonnet-5
```

Save this as `grade.py`:

```python
from json import dumps, loads
from os import environ
from re import S, search
from sys import argv
from anthropic import Anthropic

WEIGHTS = {"keyword": 25, "experience": 20, "impact": 15,
           "structure": 15, "semantic": 13, "seniority": 12}

SYSTEM = ("You are the hiring manager for this specific role. Be honest and direct. "
          "Never inflate scores. A 70+ means you would likely call them. Below 50 "
          "means you would pass. Ground every judgment in evidence from the resume "
          "and the job posting. Do not invent requirements the posting does not "
          "state. Output ONLY valid JSON.")

def grade(resume: str, title: str, company: str, jd: str) -> dict:
    prompt = f"""ROLE YOU ARE HIRING FOR:
Title: {title}
Company: {company}
Job Description:
{jd[:12000]}

CANDIDATE RESUME:
{resume[:14000]}

Score 0-100 on: {", ".join(WEIGHTS)}.
Then give 3-6 specific gaps, each pointing at something the posting asks for.
Respond ONLY as:
{{"subscores": {{"keyword": 0, "experience": 0, "impact": 0, "structure": 0, "semantic": 0, "seniority": 0}},
 "suggestions": ["..."], "summary": "one sentence: would you call them?"}}"""
    msg = Anthropic().messages.create(
        model=environ["GRADER_MODEL"], max_tokens=1200, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}])
    text = msg.content[0].text
    data = loads(search(r"\{.*\}", text, S).group(0))
    sub = {k: max(0, min(100, int(data["subscores"].get(k, 0)))) for k in WEIGHTS}
    data["score"] = round(sum(sub[k] * w for k, w in WEIGHTS.items()) / 100)
    data["subscores"] = sub
    return data

if __name__ == "__main__":
    resume_path, jd_path, title, company = argv[1:5]
    result = grade(open(resume_path).read(), title, company, open(jd_path).read())
    print(dumps(result, indent=2))
```

Run it:

```bash
python3 grade.py resume.txt job.txt "Product Manager" "Example Co"
```

Two details worth copying. The regex pulls the first `{` to the last `}`, because models sometimes wrap JSON in a sentence even when told not to. And the clamp plus the weighted sum live in Python, not in the prompt.

## Step 4: make it cheap

- **Cache by a hash of the resume plus the posting.** A repeat view costs nothing.
- **One call per resume-and-job pair.** No chains, no agents, no human in the loop.
- When I built it in July, a fresh grade was roughly one to two cents. Check current pricing at [claude.com/pricing](https://claude.com/pricing) before you plan around that number.

## Known limits

The repo says these out loud, and so should you if you ship one:

- **Run-to-run variance.** The same inputs can drift a few points between calls. That can be bigger than the effect of a real edit, so never treat a two-point change as signal. If you need stability, grade three times and take the median.
- **Polish bias.** A well-written but thin resume can outscore a messy strong one. A deterministic skill-match gate in front of the judge counters it.
- **No ground-truth calibration.** The scores are internally consistent. Nobody has checked them against who actually got hired.

## When to add retrieval

Add more machinery only when one prompt stops being enough. The repo's architecture doc lays out three tiers:

| Tier | What it does | Add it when |
|---|---|---|
| 1. Deterministic | Parse required skills from the posting, hard-match them, compute coverage | You want zero-variance gating of obvious misses |
| 2. Retrieval | Embed resume bullets and the posting's requirements; for each requirement, find the nearest evidence | The context won't fit, or you want each score tied to evidence |
| 3. Judge | This repo, fed the coverage and the evidence map | Always; it's the part that writes the feedback |

Tier 2 is where it becomes real RAG, and "dynamic" because the retrieval queries are generated per job from that job's requirements.

Honest read: most AI features don't need a pipeline. They need one good prompt pointed at the right problem, plus code for the parts that must be exact. Ship tier 3 first. Retrieval you don't need is just latency and a database to babysit.

For a judge you can actually trust, the next step is calibration: label examples by hand and measure how often the judge agrees. That's the whole subject of [validating an agent eval](/docs/ai-core-skills/agent-evals-validate/).

**Next:** [OpenBudget: a self-hosted budget app](/docs/builds/openbudget/)
