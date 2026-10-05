---
title: "Durable state: Postgres as the system of record"
description: "If it matters, it lives in a table, not a context window. Backups, the incident that tested them, and the move to local hardware."
section: safety-and-operations
group: "Keeping it running"
order: 60
updated: 2026-10-05
sources: ["learn/tier-3/h6-supabase-shared-backend.mdx"]
---

Sessions rotate. State doesn't. Every agent session in my system will end, crash or hit its context limit, so anything that has to survive that lives in Postgres, not in a context window. The database is Supabase-hosted Postgres with 250+ tables, and it's the system of record for everything many processes write at once.

This article covers what goes in it, the outage that taught me to read warning emails, the backups, and the honest status of moving it onto my own hardware.

## What you'll learn

- What belongs in a table and what belongs in a file
- The outage, and the write pattern that removed a class of blank-page bugs
- What the backups are, and what "tested" actually means
- Where the move to local hardware stands as of October 5, 2026

## Files or tables

I use both, on purpose:

| Kind of state | Lives in | Why |
|---|---|---|
| Things a human reads and agents append to: changelogs, person files, instructions, personal context | Markdown files | Diffable, greppable, readable without a tool |
| Things many processes write concurrently: workflow runs, task queues, approval queues, the agent message bus, cost records, the open-loops backlog | Postgres | Transactions, row locks, one writer can't clobber another |
| Things the cloud cockpit has to show | Postgres | The cockpit runs on Vercel and can't read my Mac's disk |

The rule from the [teardown](https://jddavenport.com/teardown): if it matters, it lives in a table, not in a context window. A promise an agent made, an approval waiting on me, a queued task, a message from one agent to another: all rows. When a session dies, the next one reads the row.

A queue worker claims a task with `FOR UPDATE SKIP LOCKED`, so two workers never grab the same row. An approval is a row with a hash of the exact text I approved. A message between agents is persisted before it's delivered. None of that works in a chat transcript.

## The outage

On May 26, 2026 the database went fully unresponsive: the database, the REST layer and auth all unhealthy, requests timing out, the dashboard stuck loading. I assumed a platform outage. The provider's status page said everything was operational. It was right.

The cause was mine. The project was on the smallest default compute size and had exhausted its disk IO budget under dozens of agents writing on schedules. The provider had emailed a warning six days earlier. Nobody read it. When the budget ran out, the database was throttled until it stopped accepting connections. Resizing the compute brought it back in a few minutes.

Two lessons. Size for agents, not for a demo: scheduled writers produce a steady IO load a hobby app never does. And a provider's warning email is a P0 the day it arrives. Today a deterministic watcher reads vendor warning mail and pages me, and a weekly watchdog checks the database's size and plan settings. Neither existed in May.

## Upserts, not delete-and-reinsert

Several early pipelines refreshed data by deleting a table's rows and inserting fresh ones. That leaves a window where the table is empty, and a cockpit page that reads during the window shows nothing. Users see "no tasks" for a second, then tasks. It looks like a ghost.

The fix, at the end of May, was to upsert everything on a stable external id: one statement that creates or updates, never a gap. The id has to identify the *thing*, not the version of it: the calendar system's own event id, a hash of domain plus title for a task. Get that wrong and every refresh creates duplicates instead of gaps.

## Migrations belong to agents

Early on, schema changes were punted to me to paste into a web console. That made me the bottleneck for every feature with a new column. Now agents apply migrations themselves through a script that runs the SQL and confirms the change. An agent that builds a feature and then waits on a human to run its migration hasn't finished the feature.

A related trap: two queues in two different schemas share the same table name, and each is drained by a different process. A doc once said one worker drained the other's queue. Now a lint check fails on that exact mix-up.

## Backups

| Layer | What it is | Cadence |
|---|---|---|
| Cloud export | Every table exported as JSON through the REST API, compressed, kept 30 days | Nightly |
| Memory stores | The vector and graph stores, archived | Nightly |
| Off-box copy | Database and memory archives copied to cloud storage, each copy verified | After each backup |
| Cold snapshots | A deduplicated, versioned backup repository in cloud storage, with a weekly integrity check that reads a sample of the data back | Twice daily |
| Local database | A native dump of the new local Postgres, encrypted, decryption verified before the plaintext is deleted | Nightly, plus a full restore test every Sunday |

### What "tested" means

A backup nobody restores is a hope, not a backup. So here is exactly what has been tested.

- **July 17:** a test restore from the cold snapshot repository came back byte-identical. That proves the files come back. It doesn't prove the database can be rebuilt from them.
- **October 2:** the real test, by accident of the migration. I dumped the entire cloud database through a temporary read-only role and restored it into a fresh local Postgres: zero errors, every table accounted for, every difference explained. That's the first time the whole thing was rebuilt from a copy.
- **Weekly since early October:** every Sunday the latest encrypted dump of the local database is decrypted, restored into a scratch database, checked against row counts saved at backup time, then dropped. The nightly runs only prove the file decrypts and the archive is readable.

### The off-box leg had a single point of failure

On October 2 the sign-in my tooling uses for Google services died with a genuine invalid-grant error. The off-box copies went to cloud storage through that same sign-in. Every consumer of it went blind, the off-box backup leg included. It was about 42 hours before anyone dug in, and about two days before it was fixed. The alert re-paged every six hours the whole time while nothing could act on it, because the fix was me approving a new sign-in on my phone. Once I did, the backlog uploaded and the restore test passed.

The lesson: your backup's off-box path depends on credentials, and credentials expire. Alert on the backup *result*, not just on the job running, and know which human step un-sticks it.

## The move to local hardware

As of October 5, 2026 I'm moving the database and the cockpit's hosting onto my own always-on hardware. Status, plainly:

- **Built:** a local Postgres with the same REST layer and gateway, so existing keys and clients work unchanged. Destructive REST calls without a filter are refused, matching the cloud. Encrypted nightly backups with a restore test.
- **Rehearsed:** a full copy of the cloud data, restored and reconciled. Local reads took 1 to 6 milliseconds against 72 to 162 milliseconds from the cloud.
- **Not done:** the cutover. A preflight gate refuses to flip until an off-box backup exists *and* I've stored an offline copy of the backup decryption key. Public-facing writers stay pointed at the cloud by design, and a lint check refuses any code that falls back to the local database after the flip.

Honest read: the speed win is real, and so is the new risk. On a hosted database, the provider owns the hardware failure. On mine, I do. That's why the cutover is gated on backups and a key I can reach when the machine can't, not on a date.

**Next:** [AgentTree Merch: an AI-operated store](/docs/builds/agenttree-merch/)
