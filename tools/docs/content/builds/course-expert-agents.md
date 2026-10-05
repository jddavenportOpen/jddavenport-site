---
title: "Course-expert agents"
description: "Agents grounded in a course's real materials that answer with citations, plus deadlines and announcements from the school LMS."
section: builds
group: "School and work"
order: 110
updated: 2026-10-05
sources: ["learn/tier-3/g1-expert-professor-canvas.mdx", "building-ai-os/arch-canvas-lms.mdx"]
---

Every class I take gets its own expert agent: one that has read the actual slides, readings and syllabus, answers with citations back to the exact deck and slide, and knows what's due. A general model answering a course question gives you the textbook version. A course expert gives you the version your instructor teaches, which is the one you get graded on.

This started in April 2026 with one analytics course. Since the fall 2026 semester it's one expert per enrolled course, plus a seat for a course where I'm the TA.

## What you'll learn

- The retrieval pipeline behind a course expert, and why it lives offline
- Why the expert should retrieve and reason, not call a second model
- How LMS data (deadlines, announcements) feeds the same agents
- Five failures that taught me more than the build did

## The shape of it

A course expert has two halves: a knowledge base built ahead of time, and a thin agent that queries it at answer time.

```text
LMS course pages + linked files + readings + syllabus
        |
        v
  crawl -> download -> parse (PPTX, PDF, DOCX, Markdown)
        |
        v
  chunk -> embed -> vector store (one collection per course)
        |
        v
  agent: retrieve top hits -> reason over them -> answer with [n] citations
```

**Ingestion** runs offline. A crawler walks the course in the LMS, follows links to the university's file storage, and downloads the decks and data files. Parsers turn each format into text chunks tagged with the document title and slide or page number. Each chunk gets embedded and stored in a per-course collection in a local Chroma store, using Voyage embeddings.

**Answering** is cheap. The agent sends the question (plus the first few hundred characters of any attached file, so an attached homework PDF steers retrieval toward its own topic), gets back the top chunks with their titles and slide numbers, and answers. Every claim drawn from a slide carries a bracket citation, and the reply ends with the list of sources. The shape, with made-up content:

```text
Compare models with adjusted R-squared, not R-squared: plain R-squared never
goes down when you add a predictor, so it always favors the bigger model [1].
Check the gap between the two before you trust either [2].

Sources:
[1] Unit 2 regression deck, slide 14
[2] Week 6 lab walkthrough, page 3
```

If the answer can't name a slide, you don't know whether it came from the course or from the model's general training. That's the whole reason to build one.

Not every course lives in the LMS. When I set up the fall courses, more than half of them didn't: one ran on a different university system, one on a class Slack, one on a public website, and one was "TBA" everywhere. So the ingest step dispatches on a declared source type per course instead of assuming one LMS. Each course can also have a hand-written knowledge file, and that file outranks anything the crawler builds.

## Retrieve, then reason. Don't call a second model.

The first version had the expert call the model API itself: retrieve chunks, stuff them in a prompt, call a model, return the answer. That works, but it's two models where one will do. The agent asking the question is already a capable model.

The current pattern is a retrieval-only command. The course expert is a Claude Code sub-agent whose instructions say, in effect: never answer course content from memory, run the retrieval query, read what comes back, cite it.

```bash
python3.12 -m agents.professor --course <COURSE> --retrieve "what the instructor says about backward selection"
```

Each hit prints its document title, category, source and distance. The agent reasons over those directly. Fewer moving parts, one fewer API key to keep alive, and the answer comes from the model that has the rest of the conversation in context.

## Invoked by phrasing, not by command

Nobody remembers slash commands for their study tools. The routing rule in my main instruction file says that when a message names a course or its instructor, or says something like "ask the analytics prof", the main agent must call that course's expert and reply with its answer. It is explicitly not allowed to answer from its own head.

That last clause matters more than the trigger list. Without it, the main agent will happily answer a course question from general knowledge, and it will sound right. See [Expert agents: route by topic](/docs/nerve-center/expert-agents/) for the general pattern.

## The LMS side: deadlines, not just content

Course content is half the job. The other half is knowing what's due. The school LMS feeds the system through an MCP server with six read tools: list courses, list assignments, get one assignment, get grades, list announcements, and get course pages. On top of that:

- An hourly sync pulls assignments and due dates across every course into a local cache and writes a receipt, so a stale sync is visible instead of silent.
- A deadline watch turns that cache into one ledger of what's due, which the daily views read.
- Each course's knowledge base is rebuilt on a weekly refresh, so new readings show up without me re-running anything.

The TA seat is a different shape. For the course I TA, an agent reads the course, the class Slack channel and the course inbox, and drafts answers to unanswered student questions. By default every draft waits for my approval on that specific reply. The only exception is a class of answer I promote by hand, like a due date read straight from the LMS or one of my own saved answers sent word for word, and I can take that back with one command. Setup help and anything judgment-shaped always comes to me.

## What broke

This is the useful part.

### The token that died quietly for 12 weeks

The LMS caps API tokens at 90 days. One expired in mid-June 2026 and nothing complained. Every sync after that failed, the deadline view went quietly empty, and an empty deadline list looks exactly like a light week. It stayed that way for about 12 weeks.

The fix is two machines, not a reminder: a weekly job renews the token before it expires, and the MCP health check has a row for the LMS token that pages me if renewal ever stops working. A credential with a hard expiry needs both halves.

### "Historical" means nothing to a vector store

In September a course expert kept telling me about a points system the instructor had replaced. The old rule was still in the knowledge file, under a heading that said it was historical. A human skims past that heading. Retrieval doesn't read headings as instructions; it matches the text, and the superseded table matched well.

The fix was to delete the superseded table outright. If a fact is wrong, it doesn't belong in the corpus with a warning label on it.

### Deleting text doesn't delete chunks

Then I deleted the text and the expert kept citing it. The store upserts on stable chunk ids, so removing a passage from a file leaves its old chunks in place. You have to clear the document's chunks first and re-ingest. Worth knowing before you trust an edit to "fix" a retrieval answer.

### Placeholders that became 27 fake assignments

The deadline file once carried two generic recurring placeholders ("pre-class prep", "weekly check"). Expanded across the semester they became 27 identical rows, so the board named a placeholder instead of the actual assignment, which is the one piece of information a deadline board exists to give you. The fix replaced the placeholders with the real items read from the course's own system.

### A course that was invisible for a month

One course had a live LMS shell from mid-August, and every rail in the system called it a blind spot until late September. The cause was a hardcoded list of two courses, copied into three different places. The fix was one function that reads the active course list, used everywhere. A hand-kept list is a bug with a delay on it.

## What to copy

| Do this | Because |
|---|---|
| Build the index offline, query it live | Answer time stays one retrieval plus one reasoning pass |
| One collection per course, with title and slide on every chunk | Citations are only as good as the metadata you kept |
| Let a hand-written knowledge file outrank the crawler | You know things the LMS doesn't say |
| Make the expert retrieve, then reason | The asking agent is already a model |
| Delete superseded facts, and clear their chunks | Retrieval can't read your intent |
| Give every expiring credential a renewal job and a health check | Silent expiry looks like "nothing due" |

Honest read: the retrieval stack is the easy part. The hard part is keeping the corpus and the deadline list true as the semester moves. Most of the fixes above are about that, not about embeddings.

The analytics expert led straight into the next build, which answers the questions retrieval can't: the ones you have to compute.

**Next:** [The analytics suite](/docs/builds/analytics-suite/)
