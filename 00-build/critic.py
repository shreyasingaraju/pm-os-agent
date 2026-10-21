"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict.
The revision cap that stops a critic<->drafter loop lives in `agent.py`.

Agent SDK port: the critic is a fresh single-turn `query()` with no tools, no
settings, and no shared session with the drafter.
"""

from __future__ import annotations

import json
import re

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from prompts import CRITIC_SYSTEM


async def review(model: str, proposed_output: str, source_data: str) -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...], "_cost": float}."""
    options = ClaudeAgentOptions(
        model=model,
        system_prompt=CRITIC_SYSTEM,
        tools=[],            # no tools at all: the critic only judges
        max_turns=1,
        setting_sources=[],  # don't inherit CLAUDE.md / user settings
    )
    prompt = (f"SOURCE DATA Cortex used:\n{source_data}\n\n"
              f"CORTEX PROPOSED OUTPUT:\n{proposed_output}")
    text, cost = "", 0.0
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, ResultMessage):
            text = msg.result or ""
            cost = msg.total_cost_usd or 0.0
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        verdict = json.loads(match.group(0)) if match else {}
        if verdict.get("verdict") not in ("pass", "fail"):
            raise ValueError("bad verdict")
    except (json.JSONDecodeError, ValueError, AttributeError):
        verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"]}
    if verdict["verdict"] == "fail" and verdict.get("tier") not in ("fixable", "safety"):
        verdict["tier"] = "fixable"
    verdict["_cost"] = cost
    return verdict
