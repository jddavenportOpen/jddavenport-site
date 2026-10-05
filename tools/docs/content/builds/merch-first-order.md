---
title: "The first order and the three bugs it found"
description: "One real order through Stripe and a print vendor exposed three fulfillment bugs no mock had caught, then a fourth that charged me for nothing."
section: builds
group: "Commerce"
order: 30
updated: 2026-10-05
sources: ["learn/tier-3/e3-first-sale-three-bugs.mdx"]
---

The first order on my merch store was mine. On June 9, 2026 I bought one "Out Of Usage" tee, white, XL, for $26, and it became Printful order 161851271. That single purchase found three bugs that a full synthetic test harness had missed. Then, the evening after I'd written "billing confirmed working" in my own log, it found a fourth: Stripe had taken my money and the shirt was never going to be printed.

This is the most useful thing the store has produced so far.

## The setup

The pipeline (described in [AgentTree Merch](/docs/builds/agenttree-merch/)) goes: Stripe Checkout takes payment, a signed webhook writes the order to the database, and a fulfillment drain running every couple of minutes re-fetches the Checkout Session from Stripe and submits the order to Printful.

Before going live I had a two-layer test harness, and it passed:

- **Layer 1:** Playwright against the live storefront. Product cards render, checkout is gated, sizes work, desktop and mobile.
- **Layer 2:** a synthetic, correctly signed Stripe webhook driving a buy-to-ship run that ended at Printful's cost-estimate endpoint. Zero money moved. It even checked margin.

That harness proved the architecture. It could not prove the live path, because the cost-estimate endpoint doesn't create an order, doesn't touch billing, and a synthetic event never makes the drain fetch a real session from Stripe. Every bug below lives in exactly that gap.

## Bug 1: expanding something that can't be expanded

The drain re-fetches the Checkout Session because the webhook payload doesn't carry the line items. It asked Stripe to expand the line items and also the customer and shipping details.

`line_items` has to be expanded; it isn't on the session by default. `customer_details` and `shipping_details` are different: they're plain objects already inline on the session, not references, so they can't be expanded. Asking anyway doesn't get ignored. Stripe returns a 400, "This property cannot be expanded", for the whole request. The fetch failed and the order sat there.

**Fix:** expand `line_items` and read the rest straight off the session. One parameter removed.

## Bug 2: billing address instead of shipping

The webhook pulled the recipient from the card's billing details. On my order the billing address had an empty first line, and Printful rejected the order: line 1 blank.

Billing and shipping are often the same address, which is exactly why a test can pass for weeks with the wrong one. For physical goods you ship to the shipping address. Always.

**Fix:** read the session's shipping details (newer Stripe API versions also mirror them under `collected_information`), and fall back to billing only if there's no shipping address at all.

## Bug 3: the confirm flag in the wrong place

Printful creates orders as drafts. A draft is never produced or shipped. To submit for fulfillment in the same call, you pass `confirm` as a **query parameter** on `POST /orders`. My code put `"confirm": true` in the JSON body.

Printful accepted the request, ignored the body field, and created a draft. No error. The order just never moved.

**Fix:** `POST /orders?confirm=1`. I also added `retry_count` and `last_error` columns to the orders table so a failed submission is visible and retryable instead of silent. Because the drain is idempotent, the fixed code picked up the stuck order on its next tick with no manual re-queue.

All three fixes shipped the same afternoon. The order showed up at Printful as pending. My log entry at 1:34 PM says the first sale was proven end to end and that Printful billing was confirmed working.

It wasn't.

## Bug 4: Stripe charged, Printful couldn't

The next evening, June 10, the order's status at Printful was **failed**, reason: "No payment method added."

Here's the money loop as it actually existed:

```text
customer card --Stripe--> my Stripe balance      (funded, worked)
my Printful account --> pays for production      (no card on file)
```

Printful charges the store owner for production when an order is confirmed. I had never put a card on the Printful account. So Stripe collected from the customer, Printful accepted the order as pending, and then Printful's own billing failed asynchronously, after my drain had already logged success. The customer (me) was charged. Nothing was going to be printed. Nobody would have been told.

And checkout was live. For more than a day, the store could have charged a stranger's card for a shirt it had no way to pay for. My agents flagged it as the top blocker before the launch post went out.

**Fix, in two parts:**

1. **The human part.** Adding a payment method to the vendor account is a money and identity action, which my agents are walled off from by design. I added the card myself.
2. **The process part.** "Pending" at the moment of submission is not the truth. I added an order reconcile job that asks Printful for the real status of every order every 15 minutes, records failures honestly at submit time, and writes an operator ledger. Paid in Stripe, accepted by Printful and actually produced are now three separate facts, checked separately.

## The tally

By June 16, 2026 the store had two orders, both mine. The first ($26) failed at Printful for the billing reason above and never shipped. The second ($30, after a price change) shipped. Zero outside customers. I'm not rounding that up.

## What I'd tell you before your first order

- **One real transaction beats a hundred mocks.** The synthetic harness was worth building. It just tests a different system from the one that takes money.
- **A money loop isn't done until both sides are funded.** Collecting payment is half. Paying your supplier is the other half, and it fails somewhere you aren't watching.
- **Trust the system that does the work.** For fulfillment status, ask the printer, not the payment processor and not your own logs.
- **Your own log can be wrong.** Mine said "billing confirmed" about 32 hours before the failure showed up. A status read at the wrong moment is a guess with a timestamp.
- **Failures must page you.** The drain now reports any failed submission, and reconcile catches the ones that fail later. A charged-but-never-shipped order should be loud within minutes, not discovered by accident.

The [tutorial](/docs/builds/build-an-ai-merch-store/) turns all four bugs into checklist items so you can skip paying for them yourself.

**Next:** [Build your own AI-operated merch store](/docs/builds/build-an-ai-merch-store/)
