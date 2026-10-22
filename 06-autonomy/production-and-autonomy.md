# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting._

| Segment | Desired autonomy | Why |
|---|---|---|
| PM who owns the project | Supervised | They own tone, commitments and the status color, which are above the line in M1. Cortex does the work and stops at the checkpoint for the PM to approve every update. |
| Lead engineer who verifies the technical details | Assisted | Cortex has made small technical slips, such as a wrong day count and a false citation to the norms. The engineer checks and corrects the PR IDs, metrics and claims. Cortex drafts, and the engineer edits. |
| Executive who reviews the update | Assisted | The executive only ever receives an update the PM has approved. A wrong status in front of leadership has the largest blast radius, and posting stays above the line for everyone. |
| Product marketing | Assisted | They contribute release dates, and dates are above the line. A date reaches Cortex only through the PM at the checkpoint, never as an input Cortex handles. They see only the shareable slice, never Orbit or Pulsar. |
| Customer support | Assisted | They read known-issue status to answer customers. Cortex gives an internal summary only, and a human writes anything customer-facing. Cortex never states a date or a promise. |

The dial never moves the M1 agent line: posting an unapproved company-wide update stays human-only for all five segments.

## Trust Ladder

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
- **Incident record so far:**
  - **What counts as an incident (any one breaks a clean window):** (1) anything posted, sent or committed without human approval; (2) confidential content (Orbit or Pulsar) in a draft shown to someone outside the core team, or stored in memory or an evidence log; (3) a firm date or a launch gate committed by Cortex; (4) a jailbreak obeyed; (5) the kill switch used because Cortex misbehaved; (6) a cost cap overshoot or a runaway run.
  - **A clean window:** zero incidents of types 1 to 4 and 6, with every near-miss logged and reviewed.
  - **Record so far:** **0 production incidents.** Every run to date was on fixtures, and nothing has been posted or committed.
  - **Near-misses caught before they reached a human:**
    - A model critic passed a draft with zero stories queued, and the code check caught it.
    - A draft credited the norms with a rule they don't contain, and the critic caught it.
    - One run finished at $0.5046, over the $0.50 cap, which led to the post-critic cost check.
    - A bound trip crashed instead of escalating, which led to the graceful halt.
    - An escalation named Orbit while quoting an attack. It went to the PM only, with no roadmap content.

## Deployment plan

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

## ROI metrics (beyond adoption & tokens)

| Metric | Target | How it is captured |
|---|---|---|
| **Outcome: time to a ready update** | The PM spends 15 minutes or less from trigger to an approved update (baseline to be measured at rollout, by timing a manual update first) | The PM logs time at the checkpoint, together with the correction count |
| **Outcome: first-pass approval** | At least 95% of drafts approved with no corrections (the same number as the eval gate) | The checkpoint log of corrections against by-design edits |
| **Cost to serve** | At most $0.15 per approved update on average, and never over the $0.50 per-run cap | The evidence logs: cost per run, summed and divided by approved updates |
| **Trust incidents** | 0 incidents of the six types defined in the Trust Ladder | The incident log, reviewed weekly with the evidence logs |

## Widen-autonomy decision rule

The PM segment moves from supervised to bounded-autonomous for **routine updates only** (fresh data of 14 days or less, no confidential item in scope, no commitment requested) when **every line of the eval gate holds for 4 consecutive weeks with at least 20 runs per project and zero Cortex incidents (the six types in the Trust Ladder section), and the PM signs off in writing**; any incident resets the clock and drops the dial one rung. The engineer, executive, product marketing and customer support segments only move after the PM segment has held the new rung for a further 4 weeks.

## Governance & forward strategy

- **Compliance:** these must never enter a prompt or a stored log: confidential or embargoed items (Orbit, Pulsar) outside the core team, customer or personal data (PII), credentials and API keys, and HR or legal matters. The roadmap filter drops confidential items before they reach Cortex (the target design). Nothing personal is stored in memory, and evidence logs are retained for 1 year with restricted read access. Product marketing sees only the shareable slice, customer support receives internal summaries only, and no customer-facing text, release date or promise comes from Cortex.
- **Safety:** these stay above the line for everyone: posting or sending, committing a date or marking a launch gate, deciding the status color, and closing or merging tickets. The kill switch is the `.cortex-kill` file.
- **Reliability:** the caps are 14 iterations, 3 revisions, 360 seconds, $0.50 per run and $5 per day. A stuck run escalates to a human. If the model is down, Cortex fails closed: the run stops with no draft and no retry loop, and the PM writes that update by hand.
- **Strategy:** the next capability is **live Jira and GitHub read connectors** in place of fixtures. The gate is the same eval suite, plus new cases for real API failures (a 500 means one retry and then escalate) and a data-freshness case, after 4 weeks in shadow mode. After that, the next segment is projects with open Sev-1s or launch holds, such as Vega.
