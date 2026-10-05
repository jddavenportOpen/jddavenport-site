---
title: "Build your own AI-operated merch store"
description: "Step by step: print-on-demand, Stripe, Next.js, a database, an image model and an agent loop, with the human gates in the right places."
section: builds
group: "Commerce"
order: 40
updated: 2026-10-05
sources: ["tutorials/build-your-own-ai-merch-store.mdx"]
---

This is the build guide for a t-shirt store with no inventory, where small agents do the daily work and you hold the money, your identity and the final say on designs. It's the stack behind my own store, [shop.agenttree.army](https://shop.agenttree.army). One honest caveat up front: mine is a working machine, not a revenue business. The only orders it has taken were my own test buys. What I can give you is a pipeline that works and the four bugs I already paid for.

Read [the first-order story](/docs/builds/merch-first-order/) before you go live. Every item on the checklist at the end comes from it.

## What you'll build

| Layer | Tool | Why |
|---|---|---|
| Printing and shipping | Printful | Prints one shirt per order. No stock, no minimums, an API. |
| Payment | Stripe Checkout | Hosted page. Card handling and compliance aren't your problem. |
| Storefront | Next.js on Vercel | A thin catalog you own and an agent can change |
| State | Postgres (I use Supabase) | Catalog, size-to-variant maps, orders |
| Art | An image model (I use Ideogram) | Text-forward, good at typographic designs |
| Operations | Claude Code plus small scheduled Python agents | Each one does one job and exits |

Why not Shopify? Your agents need to drive the store from code. A thin storefront you own is easier to drive than a platform you rent and then fight with plugins. Why not dropshipping? A middleman marks up the unit cost and gives you no control. Printful is the supplier and it has an API, so call it directly.

These examples use Printful's v1 API, which is what my store runs on. Printful also publishes a v2 API in beta. Check [the Printful docs](https://developers.printful.com/docs/) before you copy anything.

## Step 1: Printful

1. Create a Printful account.
2. In the dashboard, add a store of type **Manual order platform / API**. Do this by hand: the API can't create stores. It was the one setup step my agents couldn't do.
3. Generate an API token. If it's an account-level token, every store-scoped call needs an `X-PF-Store-Id` header. Mine was missing at first and every store endpoint returned 400.
4. Pick a base product (a unisex tee is the safe first choice) and write down the variant ID for each size you'll sell. S, M, L, XL and 2XL each have their own.
5. **Add a payment method under Billing, now, before anything else.**

> **Warning:** Printful charges *you* for production when an order is confirmed. With no card on file, it accepts your API call, shows the order as pending, then fails it later with "No payment method added." Meanwhile Stripe has already charged your customer. That exact sequence happened on my first order. Add the card first.

## Step 2: Stripe

1. Create a Stripe account and complete identity verification yourself. This is a human-only step, permanently.
2. Create Checkout Sessions on the server, never in the browser. Collect a shipping address and put the design and size in metadata so the webhook can map the order back to a Printful variant.

```typescript
// app/api/checkout/route.ts (Next.js App Router)
// Stripe is the default export of the "stripe" npm package
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const { designId, size } = await req.json();
  const product = await getListedProduct(designId);          // from your database
  const variant = product?.sizeVariants?.[size];             // resolve on the SERVER
  if (!variant) return new Response("unknown size", { status: 400 });

  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{
      quantity: 1,
      price_data: {
        currency: "usd",
        unit_amount: product.priceCents,
        product_data: { name: `${product.title} (${size})` },
      },
    }],
    shipping_address_collection: { allowed_countries: ["US", "CA"] },
    metadata: { design_id: designId, size },
    success_url: `${process.env.SITE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.SITE_URL}/`,
  });
  return Response.json({ url: session.url });
}
```

Never trust a variant ID from the browser. A tampered request could order something you never listed. Resolve the size to a variant on the server and refuse anything unknown.

3. Add a webhook endpoint for `checkout.session.completed` and verify the signature on every event, so nobody can forge "payment succeeded":

```typescript
// app/api/webhook/stripe/route.ts
export async function POST(req: Request) {
  const body = await req.text();                       // raw body, not parsed JSON
  const sig = req.headers.get("stripe-signature")!;
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return new Response("bad signature", { status: 400 });
  }
  if (event.type === "checkout.session.completed") {
    await insertOrder(event.data.object);              // status: paid
  }
  return new Response("ok");
}
```

## Step 3: The storefront

Keep it small. You need four things:

- A product grid that reads listed designs from the database, with a size picker.
- The checkout route above.
- The webhook route above.
- A success page that reads the session and says what was ordered. (Mine bounced to the home page at first. Customers notice.)

Deploy to Vercel. Check current free-tier limits on [Vercel](https://vercel.com/pricing) and your database host before you assume a cost of zero.

## Step 4: The database

Two tables carry the store:

```sql
create table merch_products (
  id text primary key,
  title text not null,
  image_url text not null,          -- a PUBLIC url, see step 5
  printful_product_id bigint,
  size_variants jsonb not null,     -- {"M": 4012, "L": 4013, ...}
  price_usd numeric not null,
  status text not null default 'pending_review'   -- pending_review | listed | retired
);

create table merch_orders (
  stripe_session_id text primary key,
  design_id text,
  size text,
  status text not null,             -- paid | submitted | in_production | shipped | failed
  printful_order_id bigint,
  retry_count int not null default 0,
  last_error text,
  last_reconciled_at timestamptz,
  created_at timestamptz not null default now()
);
```

The `retry_count`, `last_error` and `last_reconciled_at` columns aren't decoration. They're how a failed order becomes visible instead of lost. The database also works as the message bus: agents don't call each other, they read and write rows.

## Step 5: The agents

Each agent is a small script on a schedule. It reads state, does one job, writes the result and exits.

| Agent | Schedule | Job |
|---|---|---|
| Design agent | Daily (optional) | Mine concepts, run each through the IP gate, generate art only for passes, stage drafts for your approval |
| IP gate | Called by the design agent | Blocklist, then a fail-closed classifier. See [the IP-safety gate](/docs/builds/ip-safety-gate/) |
| Catalog agent | On approval | Host the art at a public URL, then create the Printful product and save the size-to-variant map |
| Fulfillment drain | Every couple of minutes | Send paid orders to Printful as confirmed orders, record retries and errors |
| Reconcile | Every 15 minutes | Ask Printful for each order's true status and update the row |
| Operator | Daily | Sense, decide, act, review, learn, with hard walls. See [AgentTree Merch](/docs/builds/agenttree-merch/) |

Three details that each cost me an afternoon:

- **Host before you list.** Printful needs a public image URL. My catalog agent first passed a local file path and Printful returned "File URL not valid." Upload, then list.
- **Expand only `line_items`.** When the drain re-fetches a Checkout Session, expand `line_items` and nothing else. `shipping_details` and `customer_details` are already inline, and asking to expand them fails the whole request with a 400.
- **Confirm in the query string.** `confirm` belongs on the URL. In the body it's ignored and you get a draft that never ships.

The drain's submit call, trimmed:

```python
from os import environ
from requests import post

def submit_to_printful(order, session, live: bool):
    ship = session.get("shipping_details") or \
           (session.get("collected_information") or {}).get("shipping_details")
    if not ship:
        raise ValueError("no shipping address")            # refuse; don't ship to billing
    addr = ship["address"]
    body = {
        "external_id": order["id"],                         # your own order id
        "recipient": {
            "name": ship["name"], "address1": addr["line1"], "address2": addr.get("line2") or "",
            "city": addr["city"], "state_code": addr.get("state") or "",
            "country_code": addr["country"], "zip": addr["postal_code"],
        },
        "items": [{"sync_variant_id": order["sync_variant_id"], "quantity": 1}],
    }
    if not live:
        return {"dry_run": True, "body": body}             # default: no real order
    r = post(
        "https://api.printful.com/orders",
        params={"confirm": 1},                             # query string, not body
        headers={"Authorization": f"Bearer {environ['PRINTFUL_API_KEY']}",
                 "X-PF-Store-Id": environ["PRINTFUL_STORE_ID"]},
        json=body, timeout=30,
    )
    r.raise_for_status()
    return r.json()["result"]
```

Make the drain idempotent: it should only pick up paid orders with no Printful order yet, so a fixed bug gets retried on the next tick without a manual re-queue.

## Step 6: Put the hard walls in code

Before anything goes live, make these real checks in the code path, defaulting to off:

1. **Money.** No real charge and no real order without explicit live flags (`CHECKOUT_LIVE`, `LIVE_ORDERS`) that you set yourself. My Printful client refuses to submit unless it's told `confirm=True` and no dry-run override is set.
2. **Identity.** The agents have no credentials for your bank, your Stripe verification, your domain registrar or your vendor billing. There's no flag that grants access. The access doesn't exist in their environment.
3. **IP sign-off.** Every concept passes the gate, and every design still needs your explicit approve before it lists.

## Step 7: Test, and know what your tests can't see

I ran two layers before launch: Playwright against the live storefront, and a synthetic signed webhook that drove a buy-to-ship run ending at Printful's cost-estimate endpoint. Both passed with zero money moved.

Neither could catch the live-path bugs, because a cost estimate creates no order and touches no billing. Use the harness to prove the shape. Then place one real order yourself.

## Go-live checklist

- Printful has a payment method on file.
- Stripe is in live mode and the live webhook signing secret is set.
- The webhook verifies signatures and rejects unsigned events.
- Size-to-variant resolution happens on the server.
- Checkout collects a shipping address, and the order uses it (not billing).
- Orders are submitted with `?confirm=1` and reach production, not draft.
- Order status is reconciled against Printful, not Stripe and not your own logs.
- A failed submission pages you within minutes.
- Live flags stay off until you've placed one real order yourself and watched it reach production at Printful.

## What's autonomous and what isn't

| The agents do | You do |
|---|---|
| Concepts, IP screening, art generation | Approve each design before it lists |
| Product listing and size variants | Stripe and vendor account setup and verification |
| Checkout sessions, order intake, fulfillment | Put a card on the vendor account |
| Reconciliation and failure alerts | Flip the live flags |
| Advice on pricing and ads | Any price change, ad buy or payout |

If you want looser supervision later, make a capability earn it with a long run of clean decisions, and cap money, identity and IP so they never graduate. Earned autonomy, with a ceiling on what can hurt you.

## Cost reality (dated)

| Item | Figure | Source and date |
|---|---|---|
| Stripe card processing (US) | 2.9% + 30 cents per transaction | stripe.com/pricing, checked October 5, 2026 |
| Image generation | A few cents per image (a 20-design drop cost under $1) | My June 2026 runs on Ideogram |
| Printful production | Billed to you per order; Printful's cost for my white XL tee was $17.31 | My first order, June 2026 |
| Margin | About $12 a shirt at a $30 price with free shipping, by my log | June 2026; product, size and destination change it |

There's no monthly platform rent in that list. That's the point of owning the storefront. Run your own numbers for your product before you trust anyone's spreadsheet, including mine.

**Next:** [The deep-research agent](/docs/builds/deep-research-agent/)
