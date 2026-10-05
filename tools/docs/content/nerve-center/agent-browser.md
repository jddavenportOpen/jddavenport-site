---
title: "The agent browser"
description: "When an agent needs a real browser: Playwright, a signed-in profile, per-site adapters, and the rule that a human finishes the risky part."
section: nerve-center
group: "Interfaces and tools"
order: 200
updated: 2026-10-05
sources: ["learn/tier-3/h5-agent-browser.mdx", "tutorials/browser-automation.mdx"]
---

Most of what my agents need from the web comes through an API, a feed or a plain HTTP fetch. A real browser is the last resort, for pages that only exist after JavaScript runs, flows that need a signed-in session, and consoles with no API at all. When an agent does need one, it goes through one shared module with a fixed ladder of rules, and anything where one botched submission matters ends with a human, not a click.

## What you'll learn

- The fetch ladder: robots rules, cache, rate limit, then a browser
- Per-site adapters, and when they beat "fetch plus an LLM"
- The signed-in profile pattern, and the bug class it comes with
- A form-filling pattern with honesty rules and a human handoff

## The fetch ladder

Every browser read in my system goes through one function:

```python
from agents.shared.browser import fetch_page

result = fetch_page("https://example.com/listings")
print(result.backend, len(result.html))
```

Inside, in order:

1. **robots.txt, strictly.** If the site's robots rules disallow the URL, the call returns nothing and logs it once. A crawl delay in robots.txt is honored too. Overrides are per domain and explicit.
2. **Cache.** Results are cached in Postgres for an hour by default. Ten agents asking for the same page in an hour cost the site one fetch.
3. **Rate limit.** A per-domain limiter spaces requests out.
4. **Playwright.** Headless Chromium, locally, by default. No per-request bill.

The order is the point. Politeness and caching come before the browser, not after. It's cheaper for you and kinder to the site, and a site that throttles you is a site you lose.

Browsers are also the heaviest thing my agents run. In September a run of kernel panics on the Mac traced partly to swarms of browser and Node processes stacking up on top of a large local model. The fix was system-wide: a memory gauge that tells the truth, wired into every gate that admits heavy work, browsers included. Details are in [Watchdogs](/docs/safety-and-operations/watchdogs/).

## Per-site adapters

Generic fetch gives you HTML. If you need structured data from one site repeatedly, write an adapter: a small module that knows that site's search form, pagination and fields, and returns JSON.

```python
# The adapter contract, with an invented site
domain = "listings.example.com"
cache_ttl_seconds = 3600        # how long a page stays fresh
min_interval_ms = 2000          # politeness floor between requests

def search(query: dict) -> list:
    """Build search URLs from the query, fetch each page through fetch_page()."""
    ...

def parse(html: str) -> dict:
    """Turn one results page into {"listings": [{"title", "price", "location", "url"}]}."""
    ...

# caller
results = fetch_with_adapter(example_listings, {"state": "CO"})
```

The first adapter I wrote walks a public listings site, pages through results, and returns structured listings, with a fixture mode that parses a saved HTML file so its tests never touch the network. An adapter is faster and cheaper than fetching pages and asking a model to extract fields, and it fails loudly when the site changes, which is what you want. Honest read: build an adapter on the third time you need the same site, not the first.

## Signed-in profiles

Some pages only exist when you're logged in. Logging in fresh on every run is slow and brittle, and it means handing the agent your password. The better pattern is a **persistent browser profile**: a profile directory where I'm already signed in, reused by the agent until the session expires, at which point I sign in again myself.

The bug class that comes with it is the wrong profile. In June a reply job kept failing at the composer with a logged-out "join the conversation" wall. It was launching an old, signed-out profile instead of the warm one. Nothing was broken except a path.

The fix generalizes: **before any authenticated action, check for a logged-in marker on the page and stop if it's missing.** Make "am I actually signed in?" an explicit assertion, not an assumption. Run in dry-run mode first, and never share a warm profile between a test environment and production. A staging agent holding your real session can act as you.

## "You drive, I'll log in"

Some setup work lives only in a web console: creating an OAuth client, configuring a workspace, flipping settings no API exposes. For those, the agent doesn't log in at all. It attaches Playwright to my real Chrome window over the browser's debugging protocol. I sign in with my own credentials and second factor. The agent clicks through the rest while I watch.

This splits the work along the right line. The human does identity. The agent does the tedious 40 clicks.

## Filling forms honestly

Sometimes an agent has to fill a form on your behalf: a vendor intake, a registration, a support request. Speed is the wrong goal there. Correctness is the goal, and three rules get you most of it.

**1. Fill only facts.** The agent answers from a record of true facts about you: name, contact details, past roles, dates. Each field is matched to a known answer. It doesn't improvise.

**2. Never invent an answer.** If a required question can't be answered from the record (a credential you don't have, a date nobody agreed to, an opinion you haven't stated) the agent leaves it and flags it. "I don't know" beats a plausible lie with your name on it.

**3. A human finishes anything one-shot.** Sort forms by what a mistake costs:

| Form | Mistake cost | Who submits |
|---|---|---|
| Internal tool, editable later | Low | Agent, with a log |
| Something you can withdraw or fix | Medium | Agent drafts, you approve in one tap |
| One shot that can't be withdrawn, or anything involving money, identity or a legal acknowledgment you haven't seen | High | Agent prepares, you review and submit |

The agent's job on a high-cost form is to get it to 95% and hand it over with every field it filled and every field it skipped listed. You click submit.

> **Warning:** An agent that can submit forms as you is an agent that can make commitments as you. Gate it the same way you gate email: drafts are free, sends need a yes.

This is the same principle as the [send gate](/docs/safety-and-operations/the-send-gate/), applied to a browser instead of an inbox.

## Copy this

1. One fetch function, with robots rules, a cache and a rate limit in front of the browser.
2. Adapters for sites you hit repeatedly.
3. Persistent profiles plus a logged-in assertion before every authenticated action.
4. For consoles: attach to your own browser, sign in yourself, let the agent click.
5. For forms: facts only, no invented answers, and a human on anything one-shot.

**Next:** [One door out: the send gate](/docs/safety-and-operations/the-send-gate/)
