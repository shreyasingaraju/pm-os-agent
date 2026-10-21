# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

**Decision:** single agent plus one validating subagent (the critic). No larger fleet.

**Why:** the only reason that holds is an **independent validator**. Cortex can't grade its own draft. An earlier run finished with zero stories queued, and a check outside the model was needed to catch it.

**Why not the others:**
- *Separation of concerns:* one task over one set of data. Reading, drafting and queuing don't contaminate each other.
- *Parallelism:* a run is about five quick reads in one turn, so splitting saves no real time.
- *Context-window pressure:* a run uses a few KB of fixtures, far below any context limit.

## 2. Topology

**Pattern:** single + subagents

```
[Cron / hook trigger]
   → [Cortex: pulls data, drafts the update, queues stories]
   → [Done test, in code: were stories queued?]
   → [Critic: 5 checks, independent]
        fixable fail → back to Cortex (max 3 revisions) → escalate
        safety fail  → block and escalate now
        pass         → [PM review checkpoint] → queued, never auto-sent
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Cortex | Pulls data, drafts the update, queues stories | The M2 loop (cron, hook backup) |
| Critic / Validator | Runs the 5 checks and returns a verdict | A validation loop: one turn, no tools |

The done test is plain code in `agent.py`, not an agent, so it isn't a roster row.

## 4. Communication & hand-offs

Everything runs in-process inside `agent.py`. No MCP or A2A is used.

- **Cortex to critic:** the proposed draft plus the source log: the task, today's date, and every tool call with its result.
- **Critic to Cortex:** a JSON verdict, `{verdict, reasons}`. On a fixable fail, the reasons go back as the next prompt.
- **Cortex to the human:** the draft file and the evidence log in `run-output/`.

## 5. The validator

- **What the critic checks:**
  1. Claims, project and IDs are traceable to the pulled data, including dates and date arithmetic.
  2. Norms and confidentiality: no unconfirmed date, no launch gate marked, no CONFIDENTIAL roadmap item in the update.
  3. Nothing was posted or committed. Stories are only queued.
  4. Stories were actually queued: `propose_stories` returned `queued_for_approval`, or the output escalates.
  5. Citations match their source: if the draft says a source states a rule, the source text contains it.
- **Fail action (tiered):** fixable errors (checks 1, 4, 5) are revised and sent back to Cortex with the reasons, up to the cap, then escalated. Safety failures (checks 2 and 3: a confidential leak, or something posted or committed) are blocked and escalated immediately, with no retry.
- **Revision cap:** 3 revisions (up to 4 drafts), enforced in code, then escalate with the last draft held.
- **Pass action:** a passing draft advances to the PM review checkpoint. It is never auto-sent.
- **Also enforced in code, outside the model:** the done test from the Loop Spec (stories queued), because a model critic alone missed it once.

## 6. State: shared vs isolated

**Shared:** the task, today's date, the tool results (the source data), and the draft. **Isolated:** Cortex's reasoning and conversation. The critic runs in a fresh session, with no tools and no session resume, so it can't inherit the drafter's blind spots. It sees the source data, so it can verify traceability and citations.

## 7. Cost & latency budget

_Coordination has a price. Rough token/latency cost of the fleet vs a single agent. (Forward-link to M5 bounds.)_
