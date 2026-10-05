---
title: "OpenBudget: a self-hosted budget app"
description: "Envelope budgeting on free-tier hosting with read-only bank sync, productized and scrubbed into a public repo."
section: builds
group: "Open source"
order: 150
updated: 2026-10-05
sources: ["learn/tier-3/i1-openbudget.mdx"]
---

OpenBudget is a self-hosted envelope budgeting app: every dollar gets a job, your real bank transactions sync in automatically, and the data lives in a database you own. I built it for myself first, then stripped out everything personal and published it in early June 2026 at [jddavenportOpen/openbudget](https://github.com/jddavenportOpen/openbudget), MIT licensed.

The pitch is simple. A popular budgeting subscription runs about $109 a year, per the repo's comparison. OpenBudget runs on free tiers plus a read-only bank data feed that costs about $15 a year.

This page covers how it works, how a private app becomes a public repo without leaking anything, and the test gap I shipped with on purpose.

## How it works

```text
your banks -> SimpleFIN Bridge (read-only) -> sync script -> Postgres (your Supabase project)
                                                                  |
                                          Next.js app (server-side reads and writes)
                                                                  |
                                          you, signed in by magic link
```

- **Bank data comes only through SimpleFIN Bridge.** You connect your banks on SimpleFIN's side and get a read-only access URL. A sync script pulls transactions into the app's tables. OpenBudget never sees a bank password.
- **The web app** (Next.js 15) reads and writes those tables server-side with your database's service-role key. The browser never holds a database key.
- **Sign-in is a magic link.** A single-use token, valid for 15 minutes, is emailed to you. The session is a signed cookie. Every request checks your email against an allowlist, and an empty allowlist means nobody gets in. It fails closed.
- **Row-level security is on with no public policies**, as a second layer behind the server-only key.

The features are the core of envelope budgeting: automatic sync, envelopes with spent versus remaining per month, a "to be budgeted" number you allocate down to zero, a review queue where new charges land unassigned, plus savings goals and a short list of money to-dos. Mobile first, because that's where you check a budget.

## Try it

You need a SimpleFIN account, a free Supabase project, a free Vercel account and an email sender (the repo uses Resend for login links). The full walkthrough is `SETUP.md` in the repo. The short version:

```bash
git clone https://github.com/jddavenportOpen/openbudget
cd openbudget
npm install
cp .env.example .env.local        # fill in your keys and ALLOWED_EMAILS
openssl rand -hex 32              # paste the result in as SESSION_SECRET
```

1. Create the Supabase project and run `supabase/schema.sql` in its SQL editor.
2. Deploy with the Vercel CLI (`vercel deploy`), setting the same environment variables there.
3. Claim your SimpleFIN setup token, then run the sync and schedule it:

```bash
npm run sync -- claim <SETUP_TOKEN>   # prints your read-only access URL
npm run sync                          # after saving that URL as SIMPLEFIN_ACCESS_URL
```

Visit `/setup` on your deployment any time. It lists which environment variables are still missing, which beats reading a stack trace.

> **Tip:** Running locally before your email domain is verified with the email sender? Set `BUDGET_DEV_MAGIC_LINK=true` and the login response includes the link directly.

## From private app to public repo

The private app came first and stays private. The public version is a clean fork, not the original with the names find-and-replaced. The steps, in order:

1. **Fork clean from the private branch.** The original stays untouched, so nothing in the public history ever held real data.
2. **Strip every personal thing**: names, account identifiers, envelope amounts, transactions, seed data, and anything secret.
3. **Run a PII and secret scan** over every tracked file. It came back clean.
4. **Add the onboarding a stranger needs**: `SETUP.md`, the `/setup` page, and a sync script that runs on its own without the rest of my system.
5. **Re-scan before launch.** On launch morning the repo got one more pass: a stale line in the description and a placeholder came out, and the scan ran again.

What made this cheap was a decision made long before: the budget data lived in a hosted Postgres database, not a file on my laptop, and the sync was already its own script. Open-sourcing meant removing data and writing docs, not re-architecting. If you think you might ever publish something, build the private version that way from day one.

## The honest gap

Before the launch post went out, my system flagged a real problem: the sync script had been ported by an agent from the original version for the public release. The build passed and the scan was clean, but the ported script had not been run against a live SimpleFIN account. The recommendation was a 30-minute real-sync test before promoting it hard.

I shipped anyway and said so. I have no record of a live end-to-end test of the public sync script since, so as of October 2026 treat it as unverified. If bank sync is the reason you're installing it, test it against your own account before you rely on it, and open an issue if it breaks.

Honest read: that's the right trade for a free side project, and the wrong one for anything that moves money. The rule I use: ship with a plain statement of what was verified and what wasn't. Holding a release until every path is tested means it never ships. Claiming it's tested when it isn't is lying.

## What to copy

- **Read-only data feeds beat stored credentials.** If a third party offers a read-only token, take it, and never hold a password you don't need.
- **Fail closed on auth.** An empty allowlist should lock everyone out, not let everyone in.
- **A `/setup` page that names what's missing** saves every new user the same hour of debugging.
- **Fork clean, scan, then publish.** Never publish the repo that once held the real data, even after you delete it. Git remembers.

**Next:** [harnessview: see your harness](/docs/builds/harnessview/)
