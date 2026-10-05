---
title: "The IP-safety gate"
description: "A blocklist plus a fail-closed classifier that refuses trademarked designs, and why fail closed is the only safe default."
section: builds
group: "Commerce"
order: 20
updated: 2026-10-05
sources: ["learn/tier-3/e2-ip-safety-gate.mdx"]
---

A print-on-demand vendor will print anything you upload. That includes a famous wizard on a broomstick. So before my merch agents pay a cent for art, every design concept goes through one function that answers a single question: could this get the store banned? If that function can't answer, the answer is no.

That last sentence is the whole design. Everything else is detail.

## Why this gets its own module

Print-on-demand platforms and marketplaces ban repeat IP offenders, and a ban takes the store and every product with it. The costs are lopsided:

| Mistake | What it costs |
|---|---|
| False reject (a safe idea gets refused) | One wasted concept. The agent makes another. |
| False pass (an infringing design ships) | A takedown, a strike, possibly the store. |

When one error costs a few cents and the other costs the business, a 50/50 threshold is wrong. You want "reject unless confident." The build plan for the store said it plainly before a line of code existed: the design pipeline must never generate or list a concept that hasn't passed the gate.

## Two layers, cheap first

**Layer 1: a blocklist.** Deterministic, free, runs first. A starter list of brand names, celebrities, sports teams, characters and franchises, bands, and risky phrases like "logo", "trademark" and "in the style of". Whole-word, case-insensitive matching. A YAML overlay extends it without a code change.

The blocklist can reject. It can't approve. It's a high-precision filter, not a clearance, because no list is complete.

My store sells AI-humor tees, and the list includes "anthropic", "openai" and "chatgpt". Yes, I blocked the brand I'd most like to put on a shirt. That's the point.

**Layer 2: a classifier.** A mid-tier Claude model gets a strict system prompt: you are an IP-safety classifier for a print-on-demand company, refuse on doubt. It scores the concept 0 to 10 and returns JSON:

```text
0-2   clearly original or generic, safe to print
3-5   borderline, evokes something protectable  -> REJECT
6-10  clearly references protected IP           -> REJECT
```

The threshold is deliberately low. Three out of ten is a reject.

One detail worth copying: the code enforces the threshold on the **score**, not on the model's own "safe"/"reject" label. If the model says score 4 and verdict "safe", the code reads the 4 and rejects. The model doesn't get to grade its own homework.

## The fail-closed contract

Most gates treat a missing signal as a pass. This one treats it as a no.

- The classifier call throws: reject.
- The model returns something that isn't parseable JSON: reject.
- The JSON has no score: reject.
- The classifier was skipped in production: reject.

Here is the shape of it, simplified from the real module:

```python
from dataclasses import dataclass, field

REJECT_AT = 3

@dataclass
class Verdict:
    safe: bool
    score: int
    reasons: list = field(default_factory=list)
    layer: str = ""

def screen_concept(concept: str, slogan: str = "", *, require_llm: bool = True) -> Verdict:
    if not concept.strip():
        return Verdict(False, 10, ["empty concept"], "blocklist")

    hit = blocklist_match(concept + " " + slogan)
    if hit:
        return Verdict(False, 10, [f"blocklist: {hit}"], "blocklist")  # no model call needed

    if not require_llm:  # offline tests only, never the production default
        return Verdict(True, 0, ["blocklist only"], "blocklist")

    try:
        raw = classify(concept, slogan)          # the LLM call
        score = int(parse_json(raw)["score"])    # any parse failure raises
    except Exception as exc:
        return Verdict(False, 10, [f"failed closed: {exc}"], "fail-closed")

    return Verdict(score < REJECT_AT, score, ["classifier"], "llm")
```

`require_llm=False` exists so tests can run without a model. If you ever see it outside a test file, that's a bug.

## Where it sits in the pipeline

Order matters for cost as well as safety:

```text
concept -> blocklist (free) -> classifier (fractions of a cent) -> image model (real money)
```

A concept that fails never reaches the image model, so you never pay to render art you can't sell. The operator's hard walls include IP sign-off too: no automated decision can skip the gate, and an approved design still needs my explicit "approve" before it lists.

## What it caught

My project log for June 8, 2026 records one line: the gate caught a Harry Potter reference in testing, "unnamed." Best guess: that means the concept evoked the franchise without naming it, which only the classifier can catch, since "harry potter" and "hogwarts" are both on the blocklist. The log doesn't say which layer fired, so treat that as a guess. It's still the case for two layers: a list catches the words, and only something that reads for meaning catches the idea.

Every design that went live passed the gate. The terminal-style redesign on June 9 went 20 for 20, and nothing in it is branded.

## Copy the pattern, not just the gate

This isn't really about t-shirts. Any agent that touches something legal, financial or irreversible should start the same way:

1. Write down what each kind of mistake costs. If they're lopsided, your threshold should be too.
2. Put a cheap deterministic filter first. It saves money and catches the obvious cases.
3. Let the model decide only what the list can't, and enforce its number yourself.
4. Make "I don't know" mean no. Error, timeout, garbage output: no.
5. Keep a human sign-off on top for anything that ships.

The same rule shows up elsewhere in my system: a killswitch file that can't be read means stop, not go. It took a real incident to learn that one, and it's in the [Socrates article](/docs/builds/socrates-x/).

**Next:** [The first order and the three bugs it found](/docs/builds/merch-first-order/)
