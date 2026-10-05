---
title: "The content pipeline"
description: "Sourcing, drafting in my voice, a preview and approval gate, one LinkedIn door, and a comment drafter that never posts on its own."
section: builds
group: "Research and content"
order: 80
updated: 2026-10-05
sources: ["learn/tier-3/f4-linkedin-growth-engine.mdx", "case-studies/content-pipeline.mdx"]
---

Every LinkedIn post my agents write, and every comment they write on someone else's post, goes through one door: a second model reviews it, and it sits on an approval card until I say yes to that exact text. Change one word after I approve and the approval is void. Getting that right took several quiet failures, and they're most of this article.

## What you'll learn

- Where post ideas come from, and why a draft with no evidence gets refused
- How drafts end up in my voice instead of the default AI voice
- The single door agents publish through, and the approval binding behind it
- The comment drafter, and the bug that hid its drafts from me for weeks
- How strategy is split from writing and from reviewing

## The idea that survived from March

In March 2026 I ran a chain of agents that turned one architecture document into documentation pages, then five LinkedIn drafts, then visuals for each, then a posting plan. Most of that chain is gone. One idea held up: **write the source once, derive the content from it.**

The source today isn't a document I write for the purpose. It's the work itself. My system logs everything it ships, one line per change, per project, with a date. That log is the best content source I have, because every line is something that actually happened.

## Sourcing: evidence or nothing

The content composer, built in July 2026, gathers three kinds of evidence, each with a stable id and a pointer to where it came from:

| Evidence | What it is |
|---|---|
| Ships | Recent entries from my ship log |
| News | Dated picks from a daily AI news sweep, with source links |
| My words | Things I've actually said or written, as raw material for opinions |

It composes one draft that must cite those ids. Two refusals are built in:

- A draft that cites zero real evidence is refused outright.
- Any evidence id the model invents is stripped.

A LinkedIn post about work that didn't happen is worse than no post.

The composer's first dry run taught me something else. It pulled private details about people close to me out of my notes and into a prompt for a public post. Nothing was posted, because the composer can't post, but the data had no business being in that prompt. A privacy filter now runs before anything reaches the model. If you build one of these: filter the inputs, not just the outputs.

## Drafting in my voice

The default voice of a language model is warm, hedged and slightly over-explained. Mine isn't. So the drafter loads a voice file before it writes anything: real examples of how I write, anti-examples of how I don't, and hard rules.

- The first sentence carries the point.
- No dashes of any kind. I banned them in June 2026; they read as machine-written.
- A banned-word list: the usual AI tells and consulting filler.
- "Honest read:" for real opinions, instead of hedging.
- No emoji openers, no "excited to share."

A brand check runs after drafting. Then an independent reviewer, a different model from the one that drafted, reads every post and comment before it reaches me. Its verdict rides on the approval card, so I see the second opinion at the moment I decide.

### The editor fixes facts, not voice

In late September I wrote a draft myself and handed it to the pipeline to check. It came back sanded down: my framing, my examples and the format that performs best for me were gone, replaced by something safer and blander. I called it out. The fix was to restore my draft and change only what was actually false: an unsourced statistic, a wrong date, two numbers that contradicted each other.

That's the rule now. When the writing is mine, the pipeline's job is to catch false claims, not to rewrite me.

## One door

Any agent in my system that wants to publish a post or a comment it wrote calls one service. It never touches the LinkedIn code directly. (The module path below is my internal one; the shape is what's worth copying.)

```python
from agents.linkedin.service import request_post, request_comment

request_post("what shipped this week and the one thing that broke ...",
             from_agent="ai-foundry", pillar="building-the-org")
```

What happens next:

```text
request_post / request_comment
  -> draft in my voice
  -> brand check
  -> independent review by a second model
  -> stage as a proposal bound to a hash of the exact text
  -> approval card to me
  -> my "approve" on that card -> the system publishes that exact text
```

Two properties matter:

1. **The ceiling is permanent.** LinkedIn posting sits at autonomy level one, forever: nothing fires without a yes on that specific item. No streak of good approvals can promote it to auto-post.
2. **The approval is bound to the content.** The proposal carries a hash of the exact text. At the moment of publishing, the hash is checked again. Edit the draft after approval and the hash no longer matches, so it doesn't publish.

The pipeline is just one client of the system-wide [send gate](/docs/safety-and-operations/the-send-gate/), which handles email and every other outbound channel the same way.

### The check that would have blocked everything

On August 11, 2026 I found the binding was broken in the strict direction. The proposal hashed the recipient, subject and body. The final check before publishing hashed only the body. They could never match, so every approved post would have been blocked at the last step.

Nobody had noticed because nothing had fired through that path yet. The log showed zero successful publishes. The fix made the final check rebuild exactly what the proposal hashed, plus an end-to-end test that runs the real mint path and the real check together. Two existing tests had encoded the same wrong assumption, and they were fixed too.

Failing closed is the right direction to fail. It's still a failure. A gate nobody has seen open is a gate you haven't tested.

## The comment drafter

Commenting early on a large account's fresh post is one of the better ways to be seen on LinkedIn. Watching dozens of feeds for fresh posts is a terrible use of a human.

In June 2026 I built a drafter for it. It watched a list of accounts I chose, noticed a fresh post, drafted a comment in my voice and pushed it to my phone with a "comment now to be early" flag. It had a daily cap of three, active hours, and a killswitch. It never posted. I posted, or I didn't.

Draft-only was a deliberate call. The research I'd run said automated posting at scale gets suppressed, and that a draft a human sends is the pattern that holds up.

It had a bug that's worth more than the feature. The drafter delivered through a separate notification bot that I had never started a chat with. Every delivery failed, and the drafter logged "surfaced" anyway, because it recorded the attempt, not the result. For weeks I got nothing and it reported success. On June 21 the fix routed delivery through my main channel and checked that a message actually arrived.

I retired the standalone drafter in August. Comments on other people's posts now go through `request_comment`, the same door and the same approval as posts.

Lesson: log the outcome, not the attempt. "Sent" should mean someone received it.

## Strategy is a separate job

At the end of September I added a LinkedIn strategist agent. It owns the plan: what to post this week and why, whether last week worked, the funnel, the cadence, which accounts are worth commenting on. It deliberately does not draft (the LinkedIn agent does that) and does not review (the independent reviewer does that).

Splitting it that way keeps each agent honest. The strategist can't fall in love with its own draft, because it doesn't write one. The writer can't grade its own work, because the reviewer is a different model.

The first finding from that strategy work was measured, not guessed: my posts weren't short of impressions, they were short of responses. In late September, posts were reaching thousands of people and well under one percent of them reacted or replied. People read and kept scrolling. That changes what you fix. Posts that end with a specific question, or lay out a framework and admit the gap in it, give people something to answer. Posting more doesn't.

## What I'd copy

- Make the content source your real work log, and refuse drafts that can't cite it.
- Filter private data out of the inputs before the model sees them.
- Put one door in front of each platform. Agents ask; they don't post.
- Bind every approval to a hash of the exact text, and test the path where it opens.
- Have a different model review the drafter.
- Log delivery, not intent.

**Next:** [The newsletter pipeline](/docs/builds/newsletter/)
