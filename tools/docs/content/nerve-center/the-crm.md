---
title: "The CRM: every person becomes a file"
description: "Markdown person files with machine facts kept apart from real human events, built from mail, calendar and meetings."
section: nerve-center
group: "Memory and context"
order: 120
updated: 2026-10-05
sources: ["learn/tier-3/c3-the-crm.mdx", "building-ai-os/arch-crm.mdx"]
---

Every contact manager dies the same way: you mean to log people, you don't, and six months later you're searching your inbox for someone's last name five minutes before a call. So in my system nobody logs people. The CRM is a folder of Markdown files, one per person, written by machines from mail, calendar, messages, meetings and voice notes. Agents read it before they draft anything to anyone.

The part worth copying is the write contract that keeps machine noise from burying the human record. It took two rounds of cleanup to get right.

## What you'll learn

- The file format and its two sections
- The write contract: which facts go where, and why
- The entity gate that keeps "Acme Inc" from becoming a person
- What went wrong at scale, and the guards that came out of it

## Where the data comes from

| Source | What it adds |
|---|---|
| Email | People I correspond with, last contact, real exchanges |
| Calendar | Meeting attendees, last meeting |
| Messages | Phone numbers and last-contact dates for people I actually talk to (metadata, gated on a minimum number of messages) |
| Voice notes | People mentioned in recorded meetings, as notes on their file |
| Address book | Email and phone enrichment for existing entries |
| Chat workspaces and LinkedIn | Membership and connection context |

Each source runs on its own schedule and writes through one shared module. That last part is the whole design: there is one door into the people folder, and the door enforces the contract.

The cockpit has a CRM page that reads a synced copy of the folder every 30 minutes, so agents and I see the same record. The rule in every agent's instructions is blunt: when a person's name comes up, check for their file and create it if it's missing. A missing file costs more than a spurious one, because an agent with no file treats a long-time contact like a cold lead.

## The file format

Plain Markdown, no front matter. Here's an invented example:

```markdown
# Dana Reyes
## Contact
- **Email:** dana@example.com
- **Phone:** (555) 010-0199
## Relationship
- **Role:** Operations lead / **Organization:** Northwind Logistics
- **Context:** Met at a regional supply chain meetup / **Source:** calendar
## Status
- **last_contact:** 2026-09-30
- **last_calendar:** 2026-09-24 (intro call)
- **last_message:** 2026-09-30 (12 msgs)
- **pending:intro-01:** draft intro to Marcus waiting on my approval, since 2026-09-28
## Interactions
- 2026-09-24: Intro call about warehouse scheduling pilot [src: calendar]
- 2026-09-30: Sent the pilot one-pager; she'll loop in her CTO [src: email]
```

Two sections carry the weight:

- **`## Status`** is keyed and mutable. One line per key, updated in place. Machine facts live here: last contact, last meeting, message counts, pending approvals, backfill attempts.
- **`## Interactions`** is append-only and holds real human events only. A meeting happened. A real email went out. Something was said. Each line is deduplicated by a content hash.

## The write contract

The module exposes three calls, and the contract is which one you're allowed to use:

```python
set_status(path, "last_contact", "2026-09-30")          # upsert one keyed line
append_interaction(path, "Sent the pilot one-pager", kind="event", source="email")
ensure_crm_entry("Dana Reyes", email="dana@example.com") # find or create, gated
```

The rule: **any recurring or mutating machine fact goes to `set_status`. Never to the timeline.** "Pending approval, 5 days stale" is a status that changes every day. If you append it, you get a new line every day. If you upsert it, you get one line that's always current.

`append_interaction` normalizes text before hashing: it strips the date prefix, the source tag, and volatile tokens like "5d stale", "ready to send" or "overdue". So "draft waiting, 5d stale" and "draft waiting, 6d stale" hash the same and the second one is dropped. And `append_interaction` refuses `kind="status"` outright with an error, so the wrong door is closed in code, not just in the docs.

### Why this exists

Before the split, every update appended to the timeline. Cron jobs that reported pending approvals re-blasted the same line on every tick. One person's file grew to about 490 near-identical lines. Another was a wall of "backfill attempted, no email found." The real human history, the part an agent drafting a note actually needs, was buried. The June 27 schema split fixed the class: two record types, two calls, one of them dedupes and the other upserts.

## The entity gate

The other early failure was things becoming people. Any string handed to the create function became a file, so the folder filled up with concepts, product names and companies. Now every new file goes through a classifier first:

| Verdict | Signals | Result |
|---|---|---|
| Not a person | A company or product suffix (Inc, LLC, Labs, University, Capital...), a digit in the name, an all-caps acronym, a known concept word | No file. Logged to a review queue |
| Person | Two or more capitalized name tokens with no "not a person" signal, or a real email or phone attached | File created |
| Ambiguous | A single capitalized word with no identity signal | No file. Review queue |

Organization signals win even when an email is attached. A company with a contact address is still a company.

## What broke after that

### Fake people from my own prompts

On September 20 I found a prompt hook that looked up names in every message had been creating people from text I never typed: carried-over context, recalled memory blocks, messages from other agents. "Merge Gate" became a person. So did "Los Angeles." Worse, the hook then injected each fake person's "context" into later prompts, so a stub born from one bad prompt fed itself back into every prompt after it.

The classifier didn't catch it, because "Merge Gate" looks exactly like a name. The fix had to be about provenance, not spelling: strip injected regions before scanning, refuse to trust entries the hook authored itself, quarantine the fakes (more than a hundred, nothing deleted), prune their vectors and graph nodes, and move the hook's own bookkeeping out of the human timeline into `## Status`.

### One phone number, several people

On September 29 a check found the same phone number attached to several different people. A fallback in the address book enrichment matched on first name alone, so everyone sharing a common first name could inherit the same number, and about thirty other numbers turned out to be shared by two or more people. Any agent texting from the CRM could have reached the wrong human. Writers now refuse to attach a number that already belongs to someone else.

## The guards, and an honest note about them

There's a health check script that scans every person file for six classes of problem: machine status in the timeline, runaway or duplicated interaction lines, non-person files, hook-authored stubs, hook lines in the timeline, and shared phone numbers. It exits non-zero on any of them, and it reports "blind" (a failure, not a pass) if it scanned zero files, because an empty folder is exactly when a count-based check would report a triumphant zero.

Here's the honest part. When I wired up the September fix, I found the weekly guard I thought I had was scheduled nowhere. The script existed. Nothing ran it. A guard nobody schedules is a guard that doesn't exist. It now runs inside a weekly sweep that pages on regression, but that sweep pages only on the hook classes, because the other classes have a small known backlog, and paging every week on a backlog is how a page gets muted. The backlog is a to-do, not a secret.

## Copy this

1. One file per person, plain Markdown, two sections: keyed status and append-only events.
2. One module that every writer goes through. Make the wrong call raise.
3. Gate creation on "is this a person?" and send the maybes to a queue.
4. Track who wrote each entry. Your own tooling is the most likely source of garbage.
5. Schedule the health check, then confirm it ran.

**Next:** [Personal context files](/docs/nerve-center/personal-context/)
