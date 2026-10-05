---
title: "AgentTree Merch: an AI-operated store"
description: "A print-on-demand store run by an agent loop, with money, identity and IP sign-off kept human. What works and what doesn't yet."
section: builds
group: "Commerce"
order: 10
updated: 2026-10-05
sources: ["learn/tier-3/e1-agenttree-merch-ai-operator.mdx", "learn/tier-3/e4-autonomous-ceo-operator.mdx", "learn/tier-3/e5-merch-expert-consultant.mdx"]
---

[shop.agenttree.army](https://shop.agenttree.army) is a print-on-demand t-shirt store that an agent loop runs: it comes up with designs, screens them for trademark risk, generates the art, lists the products, takes payment and sends paid orders to the printer. It works as a machine. It is not a business yet. As of mid-June 2026 the store had two orders, both mine, and I have no outside sale on record since. Read this as an engineering case study, not a revenue story.

Any agent can make a t-shirt. The useful part is where this one has to stop.

## What you'll learn

- How the store is put together: a few vendors, a handful of small agents, one database
- The operator loop (sense, decide, act, review, learn) and the hard walls it can never cross
- Why an operator with no sales data should say so instead of guessing
- How an advisory agent stays honest by reading live store numbers
- What actually runs today, and what I turned off

## The shape of it

No inventory, no warehouse. A customer buys one shirt, Printful prints that one shirt and ships it. Everything else is software.

| Layer | What does it |
|---|---|
| Storefront | A small Next.js app on Vercel |
| Payment | Stripe Checkout (hosted page) |
| Printing and shipping | Printful, through its API |
| State | Supabase Postgres: catalog, size variants, orders |
| Art | Ideogram, a text-forward image model |
| Operations | Small Python agents on a schedule, each doing one job |

The daily loop, as it was designed:

```text
mine concepts (evergreen niches: dev humor, coffee, cats...)
  -> IP gate (blocklist, then a fail-closed classifier)
  -> generate art (only for concepts that passed)
  -> stage the draft, ping me: "approve N" or "reject N"
  -> list the approved design as a real Printful product
  -> storefront card appears
  -> customer picks a size, pays through Stripe Checkout
  -> signed Stripe webhook writes the order row
  -> fulfillment drain sends paid orders to Printful
```

Each agent wakes up, reads its state from files and the database, does one thing, writes the result back and exits. No long-running brain holds the store in memory. If one piece dies, the others don't care.

The catalog leans on typographic designs: terminal windows, dev jokes, one-liners. That's a product choice that plays to a text-forward image model and stays far away from logos and faces, which is where trademark trouble lives. (The [IP gate](/docs/builds/ip-safety-gate/) has its own article.)

## How fast it went up

The whole thing went from research to a live checkout in about a day, which is the part that sounds like hype, so here are the dated receipts from my project log:

- **June 8, 2026, afternoon:** a research run and a build plan. Stack chosen, IP safety written down as non-negotiable.
- **June 8, evening:** the agent package and storefront built and merged, tests green, checkout deliberately off. The one thing the API couldn't do was create the Printful store itself, so I clicked that in the dashboard.
- **June 9, morning:** the operator and the merch expert shipped. Checkout went live, with me as the first buyer.
- **June 9, afternoon:** my test order went through and exposed three fulfillment bugs. The next evening a fourth, worse one showed up. That story is [its own article](/docs/builds/merch-first-order/).
- **June 16:** order check. Two orders, both mine. One shipped, one failed. Zero outside customers.

A day is fast. It's also why the first real order found four bugs. Speed got me to the real test sooner. It didn't replace it.

## The operator

The operator is the decide-brain. It runs a five-step cycle:

1. **Sense.** Read the design ledger, sales data, margins, the queue of upcoming drops, its own health. Files and database only. It doesn't poll vendor APIs; that's the drain's job.
2. **Decide.** Produce a ranked list of decisions, each with a rationale. "Run a drop today in these themes." "Margin below floor on this product." "Ask me about a price change."
3. **Act.** Execute what falls inside its current autonomy. Everything else becomes a request to me.
4. **Review.** Check that the actions completed and log the outcome.
5. **Learn.** Write the next drop's themes to a file the design agent reads on its next run.

That last step was missing in the first build. The design agent ignored what sold and re-seeded the same evergreen list every day. Closing the learn-to-decide edge was the first upgrade, the morning after launch.

### No data means say so

With zero sales, the data-driven parts of the operator (kill the losers, scale the winners, reprice) have nothing to work with. They don't invent a signal. They report `dormant: awaiting first sales` and the operator falls back to the evergreen theme list.

Honest read: that is the most important behavior in the operator. An agent that fabricates a trend from zero data looks productive and is worse than useless, because you'll act on it.

### The hard walls

Three classes of capability can never be executed by the operator on its own: money, identity and IP sign-off. They're a frozen set in the code, not a paragraph in a README:

```python
HARD_WALL_CAPABILITIES = frozenset({
    "real_charge", "ad_spend", "payout", "money_reorder",  # money
    "bank", "account", "domain",                            # identity
    "ip_signoff",                                           # the IP gate never drops below a human
})
```

If a decision names one of these with any disposition other than request, draft or no-op, the decide step raises an error instead of acting. Hard-wall items can only appear as requests that land in front of me. Tests assert it on every merge, so a change that makes a money decision auto-executable fails CI before it ships.

On top of that sits earned autonomy. Every capability carries a clean streak. After 50 clean decisions in a row (no override, no IP miss, no margin breach), it moves up one rung, from "ask me" toward "tell me" toward "just do it." Any override resets the streak to zero. The hard-wall capabilities are capped at "ask me" forever. Their streak still counts, because it's useful data, but the ceiling doesn't move.

The goal file says the mission is $10,000 a month. That's a stated goal, not a result. The store has made no money from anyone but me.

## The merch expert

Business-advice agents have a specific failure: they answer from generic training data, not from your store. The merch expert is built against that. It's a knowledge base of researched print-on-demand material (niche selection, unit economics, traffic, conversion, retention, IP and operations law), plus one design choice: every answer gets the store's live config file injected alongside the retrieved notes.

When I moved the shirt price from $26 to $30 on June 9, the knowledge base didn't need an edit: the next question reads $30 straight from the config. Its first live answer, that same morning, was "no" to paid ads, with the break-even math to back it up, which is what a careful human would have said.

Retrieval is plain keyword scoring over topic files. The whole knowledge base is small enough that a vector store would have been ceremony. The expert can't write anything. It advises, the operator decides, and I approve whatever crosses a wall.

## What runs today

As of October 2026:

| Piece | Status |
|---|---|
| Storefront and checkout | Live, charging real cards |
| Fulfillment drain | Runs every couple of minutes, sends paid orders to Printful |
| Order reconcile | Every 15 minutes, asks Printful for the true status of each order |
| Storefront QA | Twice a day, pings me only on failure |
| Daily design drop | Off since July 2026, when I told it to stop sending me a daily approval ping |
| Operator standup | Paused in September 2026 |

That's an honest picture of a parked machine: the money path and the safety checks stay on, the idea generator is off until there's a reason to feed it.

## What it taught me

- **Building the store was the easy part.** Getting money truth right (paid in Stripe, accepted by the printer, actually produced) took longer than the whole build.
- **Put the walls in code.** A frozen set plus a test beats any amount of "the agent should never."
- **No data, no signal.** Make the dormant state explicit and visible.
- **Ground advisors in live state.** One injected config file kept the expert's numbers current for free.
- **Traffic is a separate problem.** An autonomous store with no audience is a very well-tested empty room.

**Next:** [The IP-safety gate](/docs/builds/ip-safety-gate/)
