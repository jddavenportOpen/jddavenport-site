---
title: "Memory: graph plus vectors plus keywords"
description: "Hybrid retrieval over a graph store, a vector store and a keyword index, and why relationships need a graph."
section: nerve-center
group: "Memory and context"
order: 110
updated: 2026-10-05
sources: ["learn/tier-3/c1-mnemosyne-hybrid-memory.mdx", "learn/tier-3/c2-why-hybrid-beats-vector-only.mdx"]
---

Vector search answers one question well: "what text looks like this?" My agents need two more: "what is connected to this?" and "what did we decide, and when?" So memory in my system is three stores behind one call: a vector store for similarity, a graph for relationships, and a dated decision log with a keyword index. Internally the layer is called Mnemosyne (after the Greek goddess of memory). The name doesn't matter. The split does.

## What you'll learn

- The three stores and what each one answers
- What one retrieval call actually does, step by step
- Why a relationship question breaks vector-only retrieval
- Four failures, each of which taught me something a design doc wouldn't

## Why I built it

In April 2026 an audit of how agents got context found two things. The existing vector search module was indexed on a schedule and called by zero application code. Dead. And context assembly was what the design doc called dump-and-pray: a project chat got the README, the workplan, the tail of the changelog and the links file concatenated into the prompt, up to about 40KB, whether the task needed any of it or not.

The lesson wasn't "build better vector search." Agents had routed around the vector store because it couldn't answer the questions they had. Those questions were mostly about relationships and time.

## The three stores

| Store | Technology | Answers | Holds |
|---|---|---|---|
| Vectors | Qdrant, running as a local server | "What is similar to this?" | Person files, project document chunks, voice-note transcript chunks |
| Graph | Kùzu, an embedded graph database | "What is connected to this?" | People, companies, projects, topics, courses, and edges like `KNOWS`, `WORKS_AT`, `MENTIONED_IN`, `INTERACTED` |
| Decision log | SQLite with an FTS5 full-text index | "What did we decide about X, and when?" | Dated decisions with context, outcome and tags |

Embeddings come from `nomic-embed-text` running locally through Ollama: 768 dimensions, no per-query bill. A hosted embedding API exists as a fallback only when the local model is unreachable, and it can be switched off. Local by default matters because the CRM and voice notes are exactly the data I least want on someone else's server.

The decision log exists because similarity has no date axis. "What did we decide about the onboarding flow on Tuesday?" is a filter on a date plus a keyword match, not a nearest-neighbor search. That store is small and boring and it answers a question the other two can't.

## One call, step by step

Agents don't talk to the stores directly. They call one function, or the same thing exposed as MCP tools (`semantic_search`, `cypher_query`, `hybrid_retrieve`, `episodic_recall`) so any Claude Code session can use it without importing anything.

```python
from agents.shared.memory import hybrid_retrieve

hits = hybrid_retrieve("who do I know at Northwind Logistics?", top_k=8)
for h in hits:
    print(round(h.score, 2), h.source, h.text[:80])
```

What happens inside:

1. **Embed** the query locally.
2. **Vector search** each collection and pull a wider candidate pool than you need.
3. **Graph expansion.** For every hit that maps to a graph node, walk one hop: the company they work at, people they've interacted with, topics they're mentioned in. Neighbors get a score boost.
4. **Fuse** the scores. Vector similarity is weighted 0.7 and graph proximity 0.3 by default, because for most questions semantic relevance matters more than adjacency.
5. **Lexical rerank** when the query contains a proper noun. A BM25 pass over names keeps "Dana Reyes" from losing to a paragraph that merely sounds like her.
6. **Return** ranked hits, each tagged with its source (collection plus slug) so the agent can cite where a fact came from.

When context assembly calls it on an agent's behalf, it runs under a hard timeout and fails soft: if a store is slow or down, the caller gets an empty result, never an exception and never a hung turn. Memory is an enhancement to a turn, not a dependency of it.

## Why relationships need a graph

Here's the question that sells the graph. (Names invented.)

> Which of my contacts could introduce me to someone at Northwind Logistics?

Vector search finds people whose files mention Northwind. That's useful, and it's not the answer. The answer is the people who *know* someone who works there, and that fact doesn't live in any one person's embedding. It's an edge between two nodes:

```text
you --INTERACTED--> Marcus Okafor --KNOWS--> Dana Reyes --WORKS_AT--> Northwind Logistics
```

Marcus's file never mentions Northwind. No amount of embedding quality finds him. One graph hop from Dana does. The general rule: whenever the question crosses from one kind of thing to another (person to company, person to project, topic to people), you need edges, not similarity.

## What broke

### Single-writer stores lock each other out

Both stores started embedded, and an embedded database is usually single-writer. The always-on memory servers held the stores open for reading, which blocked the nightly ingest from writing. From April to June, ingestion quietly froze. A May 31 audit found the vector store hadn't updated in 32 days.

Two fixes. Qdrant now runs as a local server, which is the only mode that supports many readers and a writer at once. Kùzu stays embedded, so readers open a read-only replica that the nightly ingest refreshes after it finishes writing the primary.

### A quiet fallback is worse than a loud failure

The old embedded vector store is still on disk, frozen. If a caller's environment doesn't point at the server, the client falls back to that frozen copy. Recall "works." It returns months-old results with full confidence. Cron jobs and launchd services that didn't load the environment file were silently reading the past. The fix so far: set the server address explicitly in every scheduled job's environment, and log loudly when the server is configured but unreachable. The no-address case still falls back quietly. That's a known gap, written down where callers will see it. The general lesson: **a memory layer that degrades silently is worse than none, because nobody distrusts it.**

### Scores from different collections aren't comparable

In July I found that a weekly consolidation job's output (the distilled "what the system learned" notes) was stored correctly and never retrieved. The cause: voice-note chunks routinely scored above 0.75 while project chunks topped out near 0.59. A global sort across collections let the voice notes flood the candidate pool, so the consolidated notes never made the cut. The fix was small: guarantee the top two consolidated hits a place in the pool, add a modest score boost, and put both behind a kill switch. If you mix collections, normalize or reserve slots. Raw cosine scores from different corpora are not on the same scale.

### Your own context can poison memory

On September 20 I found a prompt hook had been minting fake people. It scanned each prompt for names and created person entries, but it couldn't tell my typing from text the system had injected into the prompt: carried-over context, recalled memory, command output. "Merge Gate" and "Los Angeles" both became people, and a name classifier rated every one of them a person. The fix stripped injected regions before scanning, added a provenance check that refuses to trust entries the hook authored itself, quarantined more than a hundred fake entries (nothing deleted), pruned their vectors and graph nodes, and added a weekly guard so the class can't come back silently.

Honest read: this is the failure I'd warn anyone about first. Once agents read memory and also write it, every bit of text in the prompt becomes a potential write. Track where each fact came from.

## Copy this

- Start with one store that matches your most common question. For most people that's vectors.
- Add a graph the first time you need a two-hop answer. Seed it from data that already has structure (a contacts list, a project list).
- Add a dated log for decisions. It's the cheapest of the three and it answers "when did we decide that?" perfectly.
- Put it behind one function with a timeout and a soft failure, and log loudly when it degrades.

**Next:** [The CRM: every person becomes a file](/docs/nerve-center/the-crm/)
