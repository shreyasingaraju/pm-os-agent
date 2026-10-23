# Cortex, a PM Chief-of-Staff Agent

> A single agent with an independent critic that triages a PM task, pulls internal state, and preps a status update plus a story batch, so the team approves instead of assembling from scratch.

_Shreya Singaraju · Agentic Loops for PMs Cohort · October 2026_

Repo: https://github.com/shreyasingaraju/pm-os-agent

This repo is my final project for the Agentic Loops for PMs Certification, **Cortex**. Each module’s artifact lives in its own folder; this README is the dashboard and the pitch.

---

## Module artifacts

### M1 · The Agent Line
- **Agent-line map**: [`01-agent-line/agent-line-map.md`](01-agent-line/agent-line-map.md)

### M2 · Loop Engineering
- **Loop spec**: [`02-loop-design/loop-spec.md`](02-loop-design/loop-spec.md)

### M3 · Orchestration & Subagents
- **Orchestration map**: [`03-orchestration/orchestration-map.md`](03-orchestration/orchestration-map.md)

### M4 · Context Engineering & Memory
- **Memory & context plan**: [`04-memory-context/memory-and-context.md`](04-memory-context/memory-and-context.md)

### M5 · Bounds & Evals
- **Bounds & evals**: [`05-bounds-evals/bounds-and-evals.md`](05-bounds-evals/bounds-and-evals.md)

### M6 · Autonomy & Production
- **Production & autonomy plan**: [`06-autonomy/production-and-autonomy.md`](06-autonomy/production-and-autonomy.md)
- **Prototype write-up**: [`06-autonomy/prototype.md`](06-autonomy/prototype.md)
- **Build insights**: [`06-autonomy/build-insights.md`](06-autonomy/build-insights.md)

---

## Ship plan

### Autonomy dial (per segment)

| Segment | Desired autonomy | Why |
|---|---|---|
| PM who owns the project | Supervised | They own tone, commitments and the status color, which are above the line in M1. Cortex does the work and stops at the checkpoint for the PM to approve every update. |
| Lead engineer who verifies the technical details | Assisted | Cortex has made small technical slips, such as a wrong day count and a false citation to the norms. The engineer checks and corrects the PR IDs, metrics and claims. Cortex drafts, and the engineer edits. |
| Executive who reviews the update | Assisted | The executive only ever receives an update the PM has approved. A wrong status in front of leadership has the largest blast radius, and posting stays above the line for everyone. |
| Product marketing | Assisted | They contribute release dates, and dates are above the line. A date reaches Cortex only through the PM at the checkpoint, never as an input Cortex handles. They see only the shareable slice, never Orbit or Pulsar. |
| Customer support | Assisted | They read known-issue status to answer customers. Cortex gives an internal summary only, and a human writes anything customer-facing. Cortex never states a date or a promise. |

The dial never moves the M1 agent line: posting an unapproved company-wide update stays human-only for all five segments.

### Trust Ladder rung + eval gate
- **Current rung:** **supervised.** Cortex does the work and stops at the human checkpoint every time. A human approves every update, story batch and memory write. Edits at the checkpoint are split in two: **by design** (the status color, date commitments and tone, which are above the line in M1) are tracked but excluded from the gate, and **corrections** (a wrong PR ID, number, claim or missing item) count against Cortex.
- **Eval gate to reach the next rung (bounded-autonomous):** every line below holds over **4 weeks of supervised runs, with at least 20 runs per project.**

| Measure | Source | Threshold |
|---|---|---|
| Eval suite (EV-1 to EV-6) | `evals/run_evals.py` on every change | 6 of 6 pass on every change, no exceptions |
| Correction rate | The checkpoint (corrections only, not by-design edits) | At most 5% of drafts need a correction |
| Unsafe actions | Evidence logs, EV-5 | 0 posts, commits, leaks or committed dates |
| Critic safety blocks | The critic's `safety` tier | At most 2% of runs |
| Bound trips | Exit type `stuck` | At most 5% of runs |
| Cost | Evidence logs | Every run at or under the $0.50 cap, with no overshoot |

The correction rate needs corrections to be recorded at the checkpoint. That isn't built yet, so the PM logs it by hand for now.
- **What counts as an incident (any one breaks a clean window):** (1) anything posted, sent or committed without human approval; (2) confidential content (Orbit or Pulsar) in a draft shown to someone outside the core team, or stored in memory or an evidence log; (3) a firm date or a launch gate committed by Cortex; (4) a jailbreak obeyed; (5) the kill switch used because Cortex misbehaved; (6) a cost cap overshoot or a runaway run.
- **A clean window:** zero incidents of types 1 to 4 and 6, with every near-miss logged and reviewed.
- **Record so far:** **0 production incidents.** Every run to date was on fixtures, and nothing has been posted or committed.
  - A model critic passed a draft with zero stories queued, and the code check caught it.
  - A draft credited the norms with a rule they don't contain, and the critic caught it.
  - One run finished at $0.5046, over the $0.50 cap, which led to the post-critic cost check.
  - A bound trip crashed instead of escalating, which led to the graceful halt.
  - An escalation named Orbit while quoting an attack. It went to the PM only, with no roadmap content.

### Deployment plan
- **Runtime:** a serverless scheduled function. A cloud scheduler fires it daily and a webhook handles new items, which matches the M2 loop (cron primary, hook backup). The workload is short and bursty, and the 360-second timeout, the daily cost cap and the kill switch all fit runs that start and stop.
- **Operator / on-call owner:** **Shreya Singaraju (PM)** is the primary operator. The **Lead Engineer** is the backup (name to be assigned at rollout). Escalation depends on the issue:

| If the issue is… | First responder | Then escalate to |
|---|---|---|
| A wrong or misleading update already shared, or a commitment made | PM (primary operator) | The executive sponsor |
| A cost, bound or loop problem, a tool failure, or a model outage | Lead Engineer (backup) | The engineering manager |
| A confidential leak or a permission problem | PM and Lead Engineer together, with the kill switch on | Security |
| Cortex misbehaving and needing to be stopped | Whoever sees it first creates the `.cortex-kill` file | Both the PM and Lead Engineer, to review before it's turned back on |

**Open item:** the names of the Lead Engineer, executive sponsor, engineering manager and Security contact are to be assigned at rollout.
- **Rollback**, fastest first: the `.cortex-kill` file; drop the dial a rung; disable a tool; revert the prompt or version to the last commit that passed the eval suite.
- **Monitoring:** the eval pass rate, the escalation rate (the share of runs that end in `escalate`), the cost per run and per day, and trust incidents, all read from the evidence logs.

### ROI metrics + widen-autonomy rule

| Metric | Target | How it is captured |
|---|---|---|
| **Outcome: time to a ready update** | The PM spends 15 minutes or less from trigger to an approved update (baseline to be measured at rollout, by timing a manual update first) | The PM logs time at the checkpoint, together with the correction count |
| **Outcome: first-pass approval** | At least 95% of drafts approved with no corrections (the same number as the eval gate) | The checkpoint log of corrections against by-design edits |
| **Cost to serve** | At most $0.15 per approved update on average, and never over the $0.50 per-run cap | The evidence logs: cost per run, summed and divided by approved updates |
| **Trust incidents** | 0 incidents of the six types defined in the Trust Ladder | The incident log, reviewed weekly with the evidence logs |

### Governance & strategy
- **Compliance:** these must never enter a prompt or a stored log: confidential or embargoed items (Orbit, Pulsar) outside the core team, customer or personal data (PII), credentials and API keys, and HR or legal matters. The roadmap filter drops confidential items before they reach Cortex (the target design). Nothing personal is stored in memory, and evidence logs are retained for 1 year with restricted read access. Product marketing sees only the shareable slice, customer support receives internal summaries only, and no customer-facing text, release date or promise comes from Cortex.
- **Safety:** these stay above the line for everyone: posting or sending, committing a date or marking a launch gate, deciding the status color, and closing or merging tickets. The kill switch is the `.cortex-kill` file.
- **Reliability:** the caps are 14 iterations, 3 revisions, 360 seconds, $0.50 per run and $5 per day. A stuck run escalates to a human. If the model is down, Cortex fails closed: the run stops with no draft and no retry loop, and the PM writes that update by hand.
- **Strategy:** the next capability is **live Jira and GitHub read connectors** in place of fixtures. The gate is the same eval suite, plus new cases for real API failures (a 500 means one retry and then escalate) and a data-freshness case, after 4 weeks in shadow mode. After that, the next segment is projects with open Sev-1s or launch holds, such as Vega.

---

## Build insights

- **Friction point.** The biggest friction was trusting checks that looked reliable and weren't. A model critic passed a draft with zero stories queued, and only a check in code caught it. A bound trip crashed with a traceback instead of escalating, and I only found it by tripping the bound on purpose. The cost cap was "checked" but one run still finished at $0.5046, because the critic's own call wasn't counted. Even the critic sometimes returned an unparseable reply and wasted a revision. The pattern was the same each time: a rule written down is not the same as a rule enforced.
- **Key learning.**
  1. A bound has to be enforced outside the model: a counter, a budget, a file check. A sentence in a prompt isn't a bound.
  2. A model checking a model isn't enough. The checks that mattered most were small pieces of code, like the done test and the cost cap. I needed both.
  3. Quiet failures matter more than loud ones: stale data presented as current, a rule falsely credited to the norms, a wrong day count. They look fine until you grade the path.
- **Aha moment.** Autonomy isn't one setting. The same agent can be supervised for the PM, assisted for the engineer and the executive, and still never post anything, because the agent line and the dial are different things. Deciding what stays human first made every later decision easier.

---

_Certification submission, Agentic Loops for PMs Certification._
