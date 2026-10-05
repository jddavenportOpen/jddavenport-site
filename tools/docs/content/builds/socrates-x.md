---
title: "Socrates: the X autopilot"
description: "A self-learning X content agent: variant testing, caps and killswitches, a pause, and a relaunch with explicit approval."
section: builds
group: "Research and content"
order: 70
updated: 2026-10-05
sources: ["learn/tier-3/f3-socrates-x-autopilot.mdx"]
---

Socrates was my attempt at an X account that runs itself: an agent that plans content, drafts posts, tests variants against each other, learns from what performs and posts on a schedule. It had all of that architecture months before it had safety rails that actually worked. As of October 2026 its scheduled loops are off, and nothing posts to X on its own. When I post to X now, it's on my own account, through the official API, one approved post at a time.

I learned more from this build than from any other, mostly because of how it failed.

## What it was built to do

Socrates ran a separate persona account, not mine. The design:

- **A strategist** read recent engagement each day and set themes.
- **An executor** drafted posts in one of several "genomes": different voice registers and format mixes.
- **Quality gates** checked every draft for AI tells, personal data, leftover artifacts, and variant collapse (every genome drifting into the same post).
- **A bandit** split the daily post budget across genomes, giving more to whatever earned engagement.
- **Population-based training** periodically pruned weak genomes and mutated strong ones.
- **A reward backfill** fetched each post's performance a day later and fed it back to the bandit.
- **Heartbeats, a self-review and killswitches** around all of it.

On paper that's a self-improving content system. In practice every one of those learning pieces depends on the account reaching people, and that's where it went wrong.

## Two bugs that cancelled out

On May 1, 2026 I halted Socrates. The account's impressions had dropped about 95 percent, and an old reply worker had been replying to posts nobody engaged with. I set the master killswitch.

On May 25, an audit of the whole X stack found that the halt had been ignored. The deployed version read its killswitch from a different file, and that file didn't exist. The check treated a missing file as "safe to run."

The only reason this didn't turn into weeks of unwanted posts: the same audit found that all of the publishing backends were dead too. The pipeline had been running daily and had shipped zero posts. Two bugs cancelled out. That is not a safety design.

The audit also found the generator would publish a stub with a failure marker in it whenever the model call errored, instead of stopping.

The fixes, shipped that night:

- **One authoritative killswitch check** that reads both the master and per-module files. Either one set means halt. **Unreadable means halt.**
- **Fail-closed generation.** A model error raises and drops the candidate. It never publishes a placeholder.
- **New gates** for failure markers and variant collapse, and an alert when every candidate fails.

```python
def halted() -> bool:
    for path in (MASTER_SWITCH, MODULE_SWITCH):
        try:
            if yaml.safe_load(path.read_text()).get("enabled", False):
                return True       # explicitly halted
        except Exception:
            return True           # missing or unreadable: halt, don't guess
    return False                  # both files exist and say not halted
```

It's the same rule as my merch store's [IP gate](/docs/builds/ip-safety-gate/): when a gate can't read its own input, the answer is stop.

## The learning loop that didn't learn

Early June turned up another quiet one. The reward signal feeding the bandit had been a flat 0.5 for every post. The bandit was dutifully splitting budget on a number that never changed, so it learned nothing. The orchestrator that ran the population-training step had also fallen off the schedule. Both were fixed by June 8, which meant self-improvement finally ran for real.

And it still didn't matter, for a reason no code could fix.

## You can't tune your way out of a reach problem

In early June the account had about 167 followers, and posts were getting single- and double-digit impressions. A bandit needs variance in its signal to learn anything. Two impressions versus eleven is noise.

On June 8 I pushed Socrates toward volume: more posts, more replies under bigger accounts, less caution. The research I'd asked for that same morning said auto-posting at scale is exactly what X suppresses in 2026, and that the one pattern that holds up is drafting for a human to send. I paused the auto-firing within hours.

Honest read: that morning is the whole lesson. I built a learning system for an audience that didn't exist yet, then tried to buy the audience with volume. The research was right and I should have read it first.

A daily probe added in early July checked whether the account was even searchable. It wasn't: the account was still suppressed. Go/no-go: hold.

## The pause, and what it revealed

On July 16, 2026 a token audit led me to park autonomous firing across several domains, Socrates included. Its scheduled jobs were disabled, and a pause gate was added so any Socrates entry point exits before doing work while the pause is set.

That pause exposed a design flaw. The Socrates heartbeat lived inside the paused package, so the pause silenced the monitor that would have reported on it, and the dashboard showed a false red. In August the heartbeat moved to a package the pause doesn't gate, and it now reports "paused by directive, not crashed." That became a standing rule in my system: a pause must never silence its own monitor.

## The suspension, and why

In August, rebuilding X access, I confirmed the persona account had been suspended and its API credentials were dead with it. The root cause was in my own code. Back in June the paid API hadn't been funded, so I'd made a logged-in browser the primary way to post. X's rules prohibit that kind of automation. The "fix" I was pleased with in June is what got the account suspended.

## Where it stands

- **September 3, 2026:** X posting relaunched on my own account, [@theJDDavenport](https://x.com/theJDDavenport), through the official API with new credentials. Before the first real post, a test post was created, read back and deleted to prove the path. Then I approved a four-post thread about loop engineering and it went out, chained correctly.
- **Today:** nothing posts to X autonomously. Socrates's scheduled loops are still disabled and its project is marked paused. Posting to X is a deliberate, approved act, like every other outbound message in my system (see [the send gate](/docs/safety-and-operations/the-send-gate/)).

## What I'd keep, and what I'd do first next time

Keep:

- Fail closed everywhere: killswitches, generation, publishing.
- Quality gates on every draft, especially for variant collapse.
- Monitors that live outside whatever they monitor.
- A probe that tells you whether anyone can see you before you tune anything.

Do first next time:

- Use the platform's official API from day one, and pay for it.
- Earn an audience by hand before automating anything.
- Read the research before shipping the volume knob, not after.

**Next:** [The content pipeline](/docs/builds/linkedin-and-content/)
