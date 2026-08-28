# CLAUDE.md — jddavenport.com

## Read this first

**This file used to describe a Next.js 15 / Tailwind 4 / shadcn / Framer Motion /
MDX / pnpm application. None of that has ever been true of the deployed site.**
It was an aspirational spec that was never built, and it sat here long enough
that agents kept arriving, reading it, and reaching for `pnpm build` in a repo
with no build step. If you came here looking for the stack, the next section is
the real one.

The site is **hand-written static HTML with inline CSS and vanilla JS**, plus a
handful of Vercel serverless functions in `api/`. There is no framework, no
bundler, no build, and no `node_modules` at the root. Do not migrate it, and do
not add a dependency. The whole page is one file you can read top to bottom,
which is why it loads in 200ms and why a recruiter's first impression is
"someone actually built this."

---

## What this site is

JD Davenport's public personal site: the surface an Anthropic Applied-AI / FDE
recruiter lands on from his resume header. High stakes, low volume. Every claim
on it should be one click from its receipt.

## Stack (the real one)

| Thing | Reality |
|---|---|
| Pages | `index.html`, `teardown.html`, `book.html`. Self-contained: inline `<style>`, inline `<script>`, no shared CSS file. |
| Fonts | Geist + Geist Mono from Google Fonts, `display=swap`, with preconnect. |
| Serverless | `api/*.js`, CommonJS (`module.exports = async function handler(req, res)`), Node runtime on Vercel. |
| Config | `vercel.json`: `framework: null`, `outputDirectory: "."`, `buildCommand: ""`, plus rewrites `/book -> /book.html` and `/teardown -> /teardown.html`. |
| Deploy | `bash deploy.sh` (see below). |
| Tooling | `tools/` holds the og-image source + renderer and the link checker. Nothing in `tools/` is served. |

Files at the root that are NOT part of the live site: `_legacy/`, `survey.html`,
`dashboard.html`, `mba-*.html`, `check-sheet.js`, `setup-sheets.js`,
`regenerate-oauth.js`, `mdx-components.tsx`, `pnpm-workspace.yaml`,
`package-lock.json`, and every `*.md` report. They are history from earlier
projects. Leave them alone; do not treat them as the site.

### ⚠️ Two repos. This clone is not the one that deploys.

- `JDDavenport/jddavenport-site` (this clone's `origin`) is **private**, default
  branch `master`. Full working history.
- `jddavenportOpen/jddavenport-site` is **public** and is the **deploy source**.
  It carries a curated subset: `index.html`, `teardown.html`, `book.html`,
  `favicon.svg`, `resume.pdf`, `robots.txt`, `sitemap.xml`, `images/`, `public/`,
  `api/{book-slots,book-create,metrics}.js`, `api/lib/`, `api/package.json`,
  `vercel.json`, `.gitignore`, `LICENSE`, `README.md`.

Pushing a branch here does **not** reach production. Changes have to be mirrored
into the public repo (`~/agent-system/scripts/gh-mirror-to-open.sh`) and any new
served file has to be added to that curated set or it will 404 in prod.

The curation is load-bearing, not cosmetic: `api/send-email-via-gog.js` in this
private repo contains a hardcoded `GOG_KEYRING_PASSWORD`, and it is not in the
public set. Verify before widening the mirror.

---

## Design system: Warm Graphite

Mirrored from the NC6 cockpit's `globals.css`. The identical `:root` block is
inlined in all three pages. **Extend it, never replace it**, and if you add a
token add it to every page that needs it.

```css
--canvas:#0E0C0A;  --sunken:#090705;
--surface-1:#15120F; --surface-2:#1D1A17; --surface-3:#26221E; --surface-4:#302C27;
--accent:#F5A623;  --accent-hover:#FFB44B; --accent-text:#F8C384; --on-accent:#1C140C;
--text-1:#ECEBEA;  --text-2:#AEABA8; --text-3:#827F7C;
--working:#7CB4CF; --ready:#69B27A;  --danger:#D98A7E;   /* danger only on /book */
--hairline:rgba(255,255,255,.07);
--border-default:rgba(255,255,255,.10);
--border-strong:rgba(255,255,255,.14);
--radius-sm:6px; --radius-md:8px; --radius-lg:12px;
--font-ui:'Geist',system-ui,-apple-system,sans-serif;
--font-mono:'Geist Mono',ui-monospace,'SF Mono',Menlo,monospace;
```

Recurring idioms, all already in the markup. Reuse them rather than inventing:

- `.kicker` — mono, uppercase, `.18em` tracking, amber `●` prefix.
- `.stat-strip` — hairline cell dividers, tabular-nums amber numerals, a dated
  caption underneath.
- `.build-card` — 2px amber left edge; `.builds-grid.headline` elevates a card
  with an amber ring; `.support-strip` is the compact one-line-per-item variant.
- `.telemetry` — the system-telemetry band with the sparkline.
- `.showcase-frame` / `.frame-bar` — browser chrome around a screenshot.
- `.timeline` — amber dots, first one glowing.
- `.pullquote`, `.stackline` — teardown prose furniture.
- `.addendum` — dated addendum block on the teardown.
- Focus rings: `0 0 0 4px rgba(245,166,35,.55)`.
- Container 1120px (content pages 780px), sections 72px, body letter-spacing
  `-0.005em`, headings `-0.02em`.

Single committed dark theme. There is no light variant and none is wanted.

**Hard rules for anything you write here:**

- **No emoji. Anywhere.**
- **No em-dashes and no en-dashes** in any copy (JD directive 2026-06-08).
  Use a period, a comma, parentheses, a colon, or the `·` separator the design
  already uses everywhere.
- No hype, no buzzwords, no "passionate about". Read
  `~/clawd/state/jd-voice.md` before writing a sentence in JD's voice.
- Mobile-responsive and **zero horizontal scroll at 390px**. Grid minimums must
  be `minmax(min(Npx,100%),1fr)`, never a bare `Npx`: `auto-fit`/`auto-fill`
  will not shrink a track below its stated minimum, and a bare value wider than
  the viewport scrolls the whole page sideways. This has bitten once already.

---

## The counting rule (do not break this)

Four different public agent counts were live at once (30 on the site, 50+ on the
og-image, 62 on the showcase, ~38 in the case study). A reader who sees two of
them in one sitting discounts all of them, on a page whose entire argument is
real numbers.

**The rule is split by provenance:**

- **Static copy never names a precise count.** It says
  **"30+ agents in daily production · 100+ built over time."** The public
  roster is curated and moves; a number typed into HTML does not. Applies to
  meta descriptions, og/twitter descriptions, JSON-LD, hero copy, section
  subheads, teardown prose, the architecture diagram, and the og-image.
- **Exact numbers appear only where a generator produced them**, which means the
  hero stat strip and the telemetry band, both fed by `/api/metrics`.

The og-image is the strictest case: link-preview cards are cached by every
platform that has ever rendered them, so a count baked there outlives any
correction. That is exactly how the old card was still claiming "50+ autonomous
agents" months after nothing else said it.

**Never write "spend" about tokens.** The label is
**"work volume through the system, list-price equivalent."** List-price
repricing of local transcripts and plan consumption are two different
measurements; conflating them has already produced a wrong conclusion
internally, and on a public page it invites both "you are burning money" and
"so it is just a subsidized plan" at once.

---

## Live metrics: `/api/metrics`

`api/metrics.js` fetches `https://nerve-center-showcase.vercel.app/capabilities.json`
server-side and returns the subset the homepage renders, with
`Cache-Control: s-maxage=3600, stale-while-revalidate=86400`.

Response shape (**every field optional**):

```json
{
  "as_of": "2026-08-28",
  "source": "nerve-center-showcase.vercel.app/capabilities.json",
  "stats": { "agents": 0, "skills": 0, "automations": 0, "domains": 0, "ships_last_30d": 0 },
  "metrics": {
    "as_of": "2026-08-28",
    "tokens_yesterday": { "input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "total": 0 },
    "turns_yesterday": 0,
    "tokens_30d_sparkline": [ { "d": "2026-08-27", "total": 0 } ],
    "usd_equivalent_yesterday": 0.0,
    "repos": { "public": 0, "total": 0, "accounts": 2 },
    "tools": { "agents": 0, "skills": 0, "automations": 0, "mcp_servers": 0, "domains": 0 },
    "live_users": 13256,
    "building_since": 2017,
    "production_since": "2026-04-10",
    "incidents_documented": 0,
    "tests_estate": 0
  }
}
```

Three properties to preserve when editing it:

1. **Explicit allowlist.** The upstream file is generated by a different
   pipeline and can grow keys at any time. Only fields named in `STAT_KEYS`,
   `METRIC_NUMBER_KEYS`, `METRIC_DATE_KEYS`, and the `pick*` helpers are
   forwarded, so nothing new lands on a public page without a change here. Add a
   key deliberately or not at all.
2. **Fail-open.** The `metrics` block may be absent entirely; the endpoint still
   returns 200 with `stats`. Upstream failure returns 503 with a 60s cache.
3. **Progressive enhancement on the page.** Every number in the HTML is already
   a real dated snapshot. The script upgrades a value only when the API hands
   one over, and nothing in it can blank a value. The `SNAPSHOT ·` caption
   becomes `LIVE · generated daily by the system it measures` only on a real
   `as_of`. **If you change a baked value, change it to something true**, and
   move its date with it.

Element ids the script writes: `stat-agents`, `stat-tokens`, `stat-users`,
`stat-users-asof`, `stat-asof`, `tele-tokens`, `tele-turns`, `tele-spark-line`,
`tele-spark-area`, `tele-spark-from`, `tele-spark-to`, `tele-days`,
`tele-incidents`, `tele-tests`, `tele-src`, `tele-live-note`.

`tele-repos` is deliberately **not** wired to `metrics.repos.public`: that field
aggregates two GitHub accounts and one of them is invisible to logged-out
visitors, so the total is unverifiable by the reader.

---

## Links: verify every one anonymously

**`github.com/JDDavenport` returns 404 to every logged-out visitor**, profile
and public repos alike (the GitHub API answers "User flagged as spammy" for it;
JD is appealing). Nothing public may link it. Every GitHub href on the site must
point at `github.com/jddavenportOpen/...`.

Repos also go private without warning (`byu-mba-alumni-portal` did, for a PII
leak). So: **check with an anonymous request, never with `gh` while
authenticated as JD**, which happily 200s things the public cannot see.

```bash
bash tools/link-check.sh                    # index, book, teardown
bash tools/link-check.sh index.html         # one page
```

Exits non-zero on any status >= 400. LinkedIn answering 999 is a bot-block, not
a broken link, and is reported as SKIP.

---

## og-image regen

`images/og-image.png` is **generated, not drawn**. Source is
`tools/og-card.html`, built from the same `:root` tokens as `index.html`.

```bash
python3.12 tools/render-og.py     # -> images/og-image.png, exactly 1200x630
```

Edit the HTML, re-run, commit the PNG. All three pages share this one card. Keep
the durable count phrasing on it (see the counting rule above).

---

## Deploying

```bash
bash deploy.sh              # stamp version.json, then vercel --prod
bash deploy.sh --dry-run    # stamp only, print the deploy command
bash deploy.sh --stamp-only # stamp only
```

`deploy.sh` writes `{sha, short_sha, branch, deployed_at}` to `version.json` and
then runs `vercel --prod`, which uploads the working directory, so the fresh
stamp ships without needing a commit.

- **`version.json` is gitignored on purpose.** A committed stamp always names
  the *previous* commit, and the done-gate would then report SHA mismatch
  (exit 2) on a perfectly good deploy, sending the next agent hunting drift that
  does not exist. Absent, the gate exits 4 ("SHA could not be discovered"),
  which correctly means "this was not deployed through deploy.sh."
- **It refuses a dirty tree** (exit 3, `--allow-dirty` to override). A
  `version.json` naming HEAD while uncommitted edits get uploaded makes the gate
  certify a deploy whose contents are not the commit it names.

---

## Before you call it done

There is no `pnpm build`, no typecheck, and no lint. The gates are these:

```bash
# 1. serve locally and look at it, both viewports
python3.12 -m http.server 8765 --bind 127.0.0.1
#    /teardown and /book rewrites do NOT apply under http.server;
#    open /teardown.html and /book.html directly.

# 2. every external link resolves for a logged-out visitor
bash tools/link-check.sh

# 3. after deploy, the Definition-of-Done gate
bash ~/agent-system/scripts/done-gate.sh \
  --url https://jddavenport.com \
  --sha "$(git rev-parse HEAD)" \
  --sha-probe "curl -s https://jddavenport.com/version.json" \
  --journey ~/clawd/projects/jd-portfolio/qa/site-journey.yaml
#    then again with teardown-journey.yaml and book-journey.yaml
#    (the gate loader takes exactly one TestSpec per file)
```

Journeys live in `~/clawd/projects/jd-portfolio/qa/`; screenshots from the last
verification pass are in `qa/screens/` beside them.

Manual checks that no script covers: zero horizontal scroll at 390px, the stat
strip renders real numbers with JS disabled, and the og-image preview matches
the current positioning.

## Open items

- **Vercel Web Analytics is not switched on.** Both `index.html` and
  `teardown.html` carry `<script defer src="/_vercel/insights/script.js">`,
  which 404s harmlessly until someone enables Analytics for the project in the
  Vercel dashboard. Until then the campaign gets zero signal on recruiter
  clicks.
- **The playbook's third leg is still missing:** repo ✓, case study ✓
  (`/teardown`), short demo ✗. A 90-second screen recording is the single
  highest-value artifact this site does not have.
- `images/builds/nc_memory.jpg` still shows a "10/14 Domains" chip in the
  cockpit chrome it screenshots. It is small and dated in the caption, but a
  fresh capture would remove the last count on the page that nothing else
  agrees with.
