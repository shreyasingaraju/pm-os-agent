# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

The biggest friction was trusting checks that looked reliable and weren't. A model critic passed a draft with zero stories queued, and only a check in code caught it. A bound trip crashed with a traceback instead of escalating, and I only found it by tripping the bound on purpose. The cost cap was "checked" but one run still finished at $0.5046, because the critic's own call wasn't counted. Even the critic sometimes returned an unparseable reply and wasted a revision. The pattern was the same each time: a rule written down is not the same as a rule enforced.

## Learning

1. A bound has to be enforced outside the model: a counter, a budget, a file check. A sentence in a prompt isn't a bound.
2. A model checking a model isn't enough. The checks that mattered most were small pieces of code, like the done test and the cost cap. I needed both.
3. Quiet failures matter more than loud ones: stale data presented as current, a rule falsely credited to the norms, a wrong day count. They look fine until you grade the path.

## Aha moment

Autonomy isn't one setting. The same agent can be supervised for the PM, assisted for the engineer and the executive, and still never post anything, because the agent line and the dial are different things. Deciding what stays human first made every later decision easier.

## What you'd do differently

I'd write the evals and the bounds before the agent, not after, and build the roadmap confidentiality filter first, so confidential items never reach the model at all. I'd also log checkpoint corrections from day one, so the eval gate has real numbers to work from.
