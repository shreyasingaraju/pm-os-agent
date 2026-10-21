# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** cron (primary) + hook (backup)

**Why this type?** The work is calendar-driven. A daily cron run builds the follow-up list and prepares the inputs, so the weekly update is ready on time. A hook picks up new items that arrive during the day instead of waiting for tomorrow's run. Cortex's output is still the weekly leadership update plus proposed stories, as scoped in the M1 agent line map.

**Ruled out:**
- *Heartbeat:* polling all day would spend budget on runs where nothing changed, and nothing here needs a response within minutes.
- *Goal:* Cortex can't validate its own "done" yet. An independent validator arrives in M3.

**Dedupe (idempotency):** if the same item fires the hook twice, or both the cron and the hook see it, Cortex must not draft twice. Dedupe by item or message ID, with a processed-IDs list kept in the run's state. Each ID is handled once.

## 2. Goal / definition of done

Produce the weekly leadership update draft, grounded in real activity, and queue proposed stories for human review. Nothing is posted.

**Done test (all must hold):** the draft exists; the critic passed it; `propose_stories` was called and queued at least 1 story; nothing was posted.

**Evidence log:** data pulled, context included and excluded, the draft, the stories queued, and the critic verdict.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | The done test passes | Save the draft, queue stories, log evidence, stop, and notify a human it's ready for review |
| **Stuck / give up** | 8 iterations, 2 critic revisions, or the $0.50 cap; a tool fails or data is missing after 3 attempts; no progress across 2 iterations | Stop, log which condition fired, escalate with the last draft held |
| **Escalate to human** | A commitment is requested (a firm date, a promise, or a launch gate); a flag needs a severity call; a post or send is needed; confidential content or a jailbreak is suspected; story batch is over 10 | Stop at the HITL checkpoint and hand to a human (M1 Actions 4, 6, 8 and the Action 7 cap) |

## 4. State

Kept **per project** (for example Northstar), with a shared read-only layer for norms and format preferences. Nothing crosses between projects, so embargoed items from one project can't leak into another's update.

**Holds:** the processed-IDs list (dedupe), the evidence log, the attempt and iteration counters that drive the stuck conditions, and previous human-approved updates plus general tone and format preferences.

**Never holds:** status color, dates, or commitments. Norms and roadmap are re-read fresh from the source each run.

## 5. The five things a loop can lean on

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet, because Cortex writes only drafts to `run-output/` and queues stories. It edits no code. Revisit if several projects run in parallel. |
| **Skills** (reusable capabilities) | Not needed yet, because there's one fixed task. Later, the status-update format could be packaged as a reusable skill. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | A plan, not wired. Read-only Jira and GitHub. Slack, MS Teams and Outlook with read and unsent drafts only. Today Cortex reads mock fixtures. |
| **Subagents** (independent check when the loop can't grade itself) | Placeholder, defined in M3 `orchestration-map.md`. The independent critic in `critic.py` already acts as a first one. |
| **State tracking** | The per-project state in §4. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

`00-build/agent.py` (loop, done test, stop conditions), with prompts in `00-build/prompts.py` and the independent validator in `00-build/critic.py`.
