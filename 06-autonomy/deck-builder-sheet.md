# Deck builder sheet: Cortex PM Chief-of-Staff Agent

Paste each field into the course's Final Project Deliverables Builder.

## Repo paths (one per artifact)

- Agent line map: `01-agent-line/agent-line-map.md`
- Loop spec: `02-loop-design/loop-spec.md`
- Orchestration map: `03-orchestration/orchestration-map.md`
- Memory and context: `04-memory-context/memory-and-context.md`
- Bounds and evals: `05-bounds-evals/bounds-and-evals.md`
- Prototype: `06-autonomy/prototype.md`
- Production and autonomy: `06-autonomy/production-and-autonomy.md`
- Build insights: `06-autonomy/build-insights.md`

## The agent in one sentence

Cortex drafts the weekly leadership update for a PM to approve. The status color and any date commitment stay with the human. A critic checks every draft, and nothing is ever posted or committed by Cortex.

## Ship plan

A serverless scheduled function, fired daily by a scheduler with a webhook for new items. The operator is Shreya Singaraju (PM), with the Lead Engineer as backup (name to be assigned at rollout).

## Autonomy dial

- PM who owns the project: supervised
- Lead engineer who verifies the technical details: assisted
- Executive who reviews the update: assisted
- Product marketing: assisted (release dates enter only through the PM at the checkpoint)
- Customer support: assisted (internal summaries only, nothing customer-facing from Cortex)

## Trust Ladder and eval gate

The current rung is **supervised**. The gate to bounded-autonomous holds for 4 weeks with at least 20 runs per project:

- All 6 evals pass on every change.
- Corrections in at most 5% of drafts.
- 0 unsafe actions.
- Safety blocks in at most 2% of runs.
- Bound trips in at most 5% of runs.
- Every run at or under $0.50.

**The gate is a plan. It hasn't been run yet.**

## Deployment and rollback

Rollback, fastest first: the kill switch file, then drop the dial a rung, disable a tool, or revert to the last commit that passed the evals. The signals watched are eval pass rate, escalation rate, cost per run and per day, and trust incidents.

## ROI

- Time to a ready update of 15 minutes or less (baseline to be measured).
- First-pass approval of at least 95%.
- Cost to serve of at most $0.15 per approved update.
- 0 trust incidents.

## Governance

Confidential items, PII, credentials and HR or legal matters never enter a prompt or a stored log. Posting, committing dates or gates, deciding the status color and closing tickets stay human for everyone. The engineer, executive, product marketing and customer support segments only move up after the PM segment has held a new rung for a further 4 weeks. The caps are 14 iterations, 3 revisions, 360 seconds, $0.50 per run and $5 per day. If the model is down, Cortex fails closed. The next capability is live Jira and GitHub read connectors, gated by the same eval suite after 4 weeks in shadow mode.

## Build insights

The friction was trusting checks that weren't enforced. The main learnings are that bounds live outside the model, a model critic needs checks in code, and quiet failures matter most. The aha is that autonomy is per person, and the agent line and the dial are different things.

## Honesty notes the deck should keep

- Cortex is **supervised**, not autonomous.
- The roadmap confidentiality filter, memory persistence, and the eval CI gate are designs, not built.
- Names other than the PM's are open items to be assigned at rollout.
