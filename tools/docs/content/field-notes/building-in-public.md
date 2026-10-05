---
title: "Building in public without fooling anyone"
description: "Why I build in the open, and the over-claim traps I caught in my own posts: inflated counts, dropped asterisks, compressed timelines."
section: field-notes
order: 20
updated: 2026-10-05
sources: ["learn/tier-3/i3-honest-marketing.mdx", "articles/building-openclaw-in-public.mdx"]
---

I post about what I build while I'm building it: what shipped, what broke, what it cost. It's the best way I know to get feedback and to keep myself honest. It's also an easy way to drift ahead of your own receipts without noticing. Every trap on this page is one I fell into in my own posts or docs, caught later, and fixed with a rule.

## Why I do it

Three reasons, none of them about follower counts.

- **Receipts make me better.** A post that says "the agents found seven bugs this weekend" has to be true on Monday when someone asks which seven. Writing for strangers forces me to check.
- **Failures teach more than wins.** My most useful posts are the ones where something broke: the restart that killed every session at once, the phone tab that resurrected closed sessions, the dialog box that froze the system for four and a half hours. People building the same thing need those more than a highlight reel.
- **Public work is a better resume than a resume.** A repo someone can clone and a teardown they can check say more than a bullet point.

What I keep private: the code of the system itself (it runs my actual life and work), anything personal, and anything that would map my attack surface. What I publish: architecture, failures with root causes, dated numbers, and the parts I've extracted into [public repos](https://github.com/jddavenportOpen).

## Trap 1: counts that inflate

My posts cited several different project counts. Each one was defensible on the day, depending on what you called a project. My registry counted shipped products, experiments, demos, abandoned ideas and planning docs the same way. So the number grew whenever I started something, including things I'd never finish.

Agent counts were worse. At one point four different agent counts were live on my public surfaces at the same time: the site, the link-preview image, the capabilities page and a case study. A reader who sees two different numbers in one sitting discounts both. On a page whose whole argument is "these are real numbers," that's fatal.

The link-preview image was the nastiest one. Social platforms cache those cards, so the old number kept showing up in link previews months after nothing else said it.

**The rule I use now**, split by where the number comes from:

- **Typed copy never names a precise count.** It says "30+ agents in daily production, 100+ built over time." A floor stays true as the system changes. A typed number starts going stale the day you type it.
- **Exact numbers appear only where a generator produced them.** My system publishes its own census every day on a [capabilities page](https://nerve-center-showcase.vercel.app) regenerated from live state, and the numbers on my homepage come from that feed. Nobody types them, so nobody can forget to update them.

## Trap 2: the autonomy claim that drops its asterisk

Some of my early posts said the system "manages things end to end." The autonomy was real. It also had gates the posts left out: no money moves, nothing is sent as me, and no identity or IP decision is made without my explicit yes. Those gates are the design.

The merch store is the clearest case. An agent loop runs a print-on-demand store: designs, listings, fulfillment, with money, identity and trademark sign-off held by a human. The "first sale" in June 2026 ran real money through Stripe and a real print vendor, and it caught three real bugs before failing at the vendor on a fourth. It was also my own test purchase. As of mid-June there had been two orders, both mine, and zero outside customers. Calling that "first sale" without the asterisk is technically true and practically misleading. The honest version is better anyway: a test order that found three bugs no mock had caught is a good story.

**The fix:** keep the gate inside the sentence. "The agent runs the store, and I approve anything that touches money or IP." That's still impressive, and it's checkable. "Fully autonomous" can be disproved by one counterexample. "Autonomous up to these gates" has a scope you can verify.

## Trap 3: the timeline that compresses

I once posted that I rebuilt my cockpit "in one day." The day happened. It sat inside a ten-day arc in late May 2026 that also held a research pass by several agents, a brutal self-audit, and an architecture pivot. The post compressed the arc into the sprint.

Sprint stories are more fun to read, which is exactly why they drift. **The fix:** name the arc. "After a week of architecture work, yesterday's sprint landed the last pieces" is accurate and still conveys the pace. The full arc is in [What the cockpit rebuilds taught me](/docs/nerve-center/cockpit-rebuilds/).

## Trap 4: the origin story my own git history disproved

For months my posts and old docs said my system grew out of OpenClaw, as if it had been my first harness and the foundation for everything after. It's a clean origin story. It's also wrong.

OpenClaw is a real, large open-source agent project. I installed it in early 2026, experimented with it, and wrote tutorials about it. But when an agent audited my git history in September, the word "openclaw" appeared exactly twice in my main system's history, both in June: once as the name of a merch store, and once in a commit retiring a dead bridge to it. My system is built on Claude Code and my own scaffolding.

How did the story stick? An internal file named after OpenClaw actually described my own system as of April 2026. The file was mislabeled, and later documents, including one written specifically to separate fact from marketing, trusted the filename. A mislabeled file outlived the memory of what was in it.

**The fix:** history claims get checked against something that can't drift. Git log, a dated changelog entry, a receipt. Not a filename, and not my memory. The real story, starting from a chat bot in early 2026, is in [How the system got built](/docs/nerve-center/the-story/), and it's a better story than the one it replaced.

## Trap 5: a number that measures something else

My site shows token volume from my system. It's easy to read that as a bill. It isn't. It's a list-price repricing of local transcripts: what the work would cost at published API rates. My actual cost is a set of flat-rate plans, and plan consumption is a third, separate measurement.

I've watched the conflation go wrong inside my own system: an agent once read the dollar-equivalent figure as plan consumption and concluded one of my plans was exhausted when it wasn't. On a public page the same confusion invites two opposite wrong takes at once ("you're burning money" and "so it's just a subsidized plan").

**The fix:** label the measurement every time. I write "work volume, list-price equivalent" and never describe token volume as money I paid.

## The checklist I run before posting

| Test | Question |
|---|---|
| Count | Where does this number come from? If someone asked me to list every item it counts, could I? |
| Asterisk | Who approves the risky part? If the answer is "nobody," is that true, or did I just leave it out? |
| Timeline | Is this the sprint or the arc? Did I say which? |
| Origin | Can git or a dated log prove this history, or is it memory? |
| Measurement | Does this number measure what the sentence implies it measures? |

My post drafts now go through an automated voice gate (a lint plus an LLM judge) before I see them, and it has caught a drafting agent contradicting itself two lines apart. It doesn't replace the five questions. It just asks some of them before I'm tired.

## The point

None of this makes the work sound smaller. Accurate claims hold up when someone checks, and the right readers do check. Inflated ones cost you the first time they don't. Build in public, post the failures, and keep every claim one click from its receipt.

**Next:** [Why agents will eat a lot of SaaS](/docs/field-notes/agents-vs-saas/)
