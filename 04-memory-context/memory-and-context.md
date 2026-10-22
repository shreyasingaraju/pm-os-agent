# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

**Always in context, highest priority first:**
1. Cortex's operating rules and output template (the system prompt).
2. The task brief and today's date.
3. The team norms, in full.

**Retrieved per run, in priority order:**
4. The project record and its activity, only for the project named in the task.
5. The relevant roadmap slice, with confidential items excluded (the target design).
6. The top few past updates and decisions, for format and precedent only.

**If the budget is tight, cut from the bottom:** past updates first, then the roadmap slice. Never cut the rules, the task, the norms, or the activity, since the draft can't be grounded without them.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| `get_activity` | Small today, grows and changes weekly | Retrieve | Deciding factor: volatility. Pull only this project's slice, and cite the IDs. |
| `search_past_updates` | Small today, unbounded and grows weekly | Retrieve | Deciding factor: size. Only the few relevant precedents are needed. |
| `get_roadmap` | About 1 KB, slow-changing, mixed shareable and confidential | Retrieve (target design) | Deciding factor: citation. Pulling the relevant slice keeps embargoed items out, and the draft must cite what it used. Today the build returns the whole file, so confidential items reach context; a filter is still to be built. |
| `get_norms` | About 2 KB, bounded, rarely changes | Long-context | Deciding factor: size. Every rule must apply on every run, and a missed rule is a violation. |
| `get_task` | Bounded, static | Long-context | Deciding factor: size. One document for this run, so reason over all of it. |

## 3. Retrieval quality plan

Each retrieved source gets the agentic moves that answer its failure mode. A retrieved source with no move is naive RAG, so every row has at least one.

| Source | Failure mode | Routing | Document grading | Reranking | Self-verification | Caching |
|---|---|---|---|---|---|---|
| `get_activity` | Wrong project, stale or missing items, and old activity presented as current | · | ✓ Check the project and freshness, and flag anything older than 14 days | · | ✓ The critic's check 1 traces every claim to the pulled data | · |
| `search_past_updates` | Keyword overlap returns irrelevant precedents, with a fallback to the first two items | · | ✓ Drop irrelevant or fallback results | ✓ Same project and most recent first | · | ✓ Cache approved updates by project and week for 1 year, and invalidate an entry if that update is amended |
| `get_roadmap` | Returns the whole file, so confidential items reach context | · | ✓ Drop confidential items before they reach Cortex | · | ✓ The critic's checks 2 and 5 catch a leak or a false citation | · |

**Not used, and why:** *routing*, because each need maps to exactly one tool. *Caching* is used only for past updates, because an approved update never changes. Activity and the roadmap change every week, so they are read fresh.

**Status in the build:** self-verification is partly in place through the critic's checks. Document grading is not built yet. It is the target design.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | The task brief, today's date, tool results, drafts, critic verdicts, and the attempt and revision counters | This run only. Discarded at the end. The evidence log is kept. |
| **Episodic** (past runs) | Previous human-approved status updates and decisions, evidence logs, and a dated snapshot of each project's shareable roadmap section (Orbit and Pulsar filtered out before storing) | Per project. Approved updates, roadmap snapshots and evidence logs for **1 year**. Evidence logs are readable only by the PM and the episodic-memory scope, because the critic's reasons can quote confidential names. A snapshot is written only after the update is approved. Comparisons use the latest snapshot and state its age. |
| **Semantic** (durable facts/prefs) | General tone, wording and format preferences. Never status color, dates or commitments. | Until you change them, reviewed quarterly. The norms are re-read fresh each run, and so is the roadmap, which is compared with the last snapshot. |
| **Shared** (across agents) | The processed-IDs list, so the cron and the hook don't draft twice. The critic shares only the source data and the draft, never Cortex's reasoning. | Processed IDs for 14 days. |

**Read and write scope (M1 agent line):** Cortex can read all four. On its own it writes only working memory and the evidence log. Anything that enters episodic or semantic memory needs a human's approval, because a human owns tone and commitments.

## 5. Memory risks & mitigations

| Risk | Where it bites Cortex | Mitigation |
|---|---|---|
| **Drift** | A stored tone preference slowly pulls drafts away from the facts, or quietly starts deciding status color or commitments. | Tone memory covers wording and format only. Never status color, dates or commitments. The critic's check 2 still applies. Review preferences quarterly. |
| **Poisoning** | A bad input is trusted forever: a poisoned brief or pasted notes, a bad roadmap snapshot, or a wrong update saved to memory. | Memory writes only after human approval. The brief is treated as data and not as instructions. The critic checks a draft before it's approved. A snapshot is written only from an approved run. |
| **Staleness** | A year-old snapshot is compared as if it were last week's. A cached update is out of date. A project resumes after a pause with no context on what happened before. | **Date comparison:** each snapshot carries its date, and comparisons use the latest one and state its age. The 14-day freshness rule applies to activity. Cache entries are invalidated if an update is amended. **Context comparison policy:** when the newest activity is more than 14 days old, or a project resumes after a gap, search the same project's episodic memory (approved updates, decisions, roadmap snapshots) and report the last known state, its date, the length of the gap, and what changed since. Memory is context only, never evidence of current progress, and every claim from memory carries its source and date. An old status color is never carried forward, and if the pause is longer than the 1-year retention window the draft says "no memory before <date>" and does not guess. |
| **Confidential / retention** | Orbit and Pulsar names end up in a stored snapshot or an evidence log. A year of logs holds data that should have expired. | Confidential items are filtered out before anything is stored. Evidence logs have restricted read access. Per-project scope prevents cross-project leakage. |

**Read/write scope:** tied to the M1 agent line. Cortex writes only working memory and the evidence log on its own, and anything entering episodic or semantic memory needs a human's approval.

**Forward link to M5:** every lifetime above (1 year for history, 14 days for processed IDs, 12-month retention for logs) becomes an enforced cap in `bounds-and-evals.md`.
