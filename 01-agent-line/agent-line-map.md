# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state and activity | H | L | H | Below | No |
| Decide relevant context | H | M | M | Below | Yes |
| Draft the update | H | M | M | Below | Yes |
| Decide tone and commitment level | L | H | L | Above | n/a |
| Flag at-risk items and escalations | M | L | M | Below | No |
| Choose what to escalate | M | H | L | Above | n/a |
| Propose a story batch (capped) | M | M | M | Below | Yes |
| Post an update | L | H | M | Above | n/a |

## Agent anatomy (sketch)

- **Model:** Haiku 4.5 by default. Escalate to a frontier model when the critic rejects a draft, sources conflict or are missing, or a jailbreak or injection is suspected.
- **Tools:** Read: project state, activity, past-update search, roadmap, team norms, plus Jira and GitHub (read-only). Slack, MS Teams and Outlook (read plus unsent drafts only, no send). Write, capped: story proposals (max 10 per run), queued for approval. Deliberately absent: posting or sending, creating or merging tickets or PRs, and committing dates.
- **Memory:** Persists: previous human-approved status updates, and general tone, wording and format preferences. Never persisted: status color, dates or commitments. Roadmap and norms are re-read fresh each run, and run scratch work is purged.
- **Loop:** _placeholder, defined in M2 loop-spec.md_
- **Bounds:** _placeholder, defined in M5 bounds-and-evals.md_
- **Evals:** _placeholder, defined in M5 bounds-and-evals.md_

## The golden rule, applied

1. **Pull project state and activity** sits **below** the line because it's easy to reverse, has a small blast radius, and is easy to verify. Deciding factor: reversibility.
2. **Decide relevant context** sits **below** the line, with human review, because it's easy to reverse, has a moderate blast radius, and is only moderately easy to verify. Deciding factor: measurability.
3. **Draft the update** sits **below** the line, with human review, because it's easy to reverse and moderately easy to verify, but has a moderate blast radius. Deciding factor: blast radius.
4. **Decide tone and commitment level** sits **above** the line because it's hard to reverse, has a large blast radius, and is hard to verify. Deciding factor: blast radius.
5. **Flag at-risk items and escalations** sits **below** the line because it's moderately reversible, has a small blast radius, and is moderately easy to verify. Deciding factor: blast radius. Condition: Cortex also lists what it checked and found clear, so a missed flag is visible.
6. **Choose what to escalate** sits **above** the line because it's only moderately reversible, has a large blast radius, and is hard to verify. Deciding factor: reversibility.
7. **Propose a story batch (capped)** sits **below** the line, with human review, because it's moderately reversible, has a moderate blast radius, and is moderately easy to verify. Deciding factor: reversibility.
8. **Post an update** sits **above** the line because it's hard to reverse, has a large blast radius, and is moderately easy to verify. Deciding factor: reversibility.

## Hardest call

**Action 5: flag at-risk items and escalations.** I first put flagging at HITL, then moved it Below because Action 6 (choose what to escalate) already has a human deciding severity and criticality, so a flag alone does nothing until a human acts on it. The concern was that a missed flag never reaches the human. I kept it Below, on the condition that Cortex lists what it checked and found clear. The axis that settled it was blast radius: a flag is only an alert, so a wrong one costs little.
