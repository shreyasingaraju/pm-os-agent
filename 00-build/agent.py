"""Cortex, a minimal, explicit agent you (and your coding agent) can read end to
end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

AGENT SDK PORT: this version runs on the Claude Agent SDK instead of a hand-written
OpenAI tool-calling loop. The SDK drives the tool loop; the bounds the course cares
about are still set here, in code, and enforced OUTSIDE the model:
  - iteration cap   -> SDK `max_turns`, tracked across revisions
  - cost cap        -> SDK `max_budget_usd`, plus our own running total
  - revision cap    -> the critic<->drafter loop below
  - queue cap       -> enforced inside tools.propose_stories
  - no publish tool -> `tools=[]` removes every built-in tool (no Bash/Write/Web), and
                       only the Cortex tools in tools.py are allowed
The original OpenAI version is on git branch `main`; `git checkout main` reverts.

Usage:
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak      # the prompt-injection refusal case

Every run ends by showing the drafted status update in a FINAL STATUS UPDATE block
(or LAST DRAFT, held, if a bound trips), and saves it to run-output/. That file is
always a draft held for a human, it is never posted, there is no publish tool.

Auth: the SDK uses your Claude Code login, or ANTHROPIC_API_KEY if that is set (see
.env.example). Model and bounds are read from env, that tuning is your M5 deliverable.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

import tools
from critic import review
from prompts import CORTEX_SYSTEM

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "claude-haiku-4-5")
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
MAX_REVISIONS = int(os.environ.get("CORTEX_MAX_REVISIONS", "2"))
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))

SERVER = "cortex"


def _wrap(fn, name: str, description: str, schema: dict):
    """Expose a plain function from tools.py to the SDK as an MCP tool."""
    @tool(name, description, schema)
    async def _tool(args):
        result = fn(**args)
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    return _tool


# The agent line lives in tools.py: only these tools exist. There is no publish tool.
CORTEX_TOOLS = [
    _wrap(tools.get_project, "get_project",
          "Look up a project by its ID (status, flags, linked PRD).",
          {"project_id": str}),
    _wrap(tools.get_activity, "get_activity",
          "Pull recent engineering activity for a project (merged PRs, open issues, Sev-1s).",
          {"project_id": str}),
    _wrap(tools.search_past_updates, "search_past_updates",
          "Search previous status updates and decisions for tone and precedent.",
          {"query": str}),
    _wrap(tools.get_roadmap, "get_roadmap",
          "Return the roadmap. Some items are flagged confidential/embargoed.",
          {"query": str}),
    _wrap(tools.get_norms, "get_norms",
          "Return the team norms / PM playbook the agent must follow.",
          {"query": str}),
    _wrap(tools.propose_stories, "propose_stories",
          "Queue a set of backlog stories for human approval (creates nothing; "
          "rejected above the item cap).",
          {"type": "object",
           "properties": {"project_id": {"type": "string"},
                          "stories": {"type": "array", "items": {"type": "string"}},
                          "reason": {"type": "string"}},
           "required": ["project_id", "stories"]}),
]
ALLOWED = [f"mcp__{SERVER}__{t.name}" for t in CORTEX_TOOLS]

OUTPUT_DIR = Path(__file__).parent / "run-output"


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def emit_deliverable(which: str, draft: str, *, accepted: bool,
                     reason: str, cost: float) -> None:
    """Surface AND persist Cortex's drafted status update so it can't get lost in
    the scroll-back. This is still a DRAFT held for human review, never a post,
    there is no publish tool, and an escalated run is held on purpose.

    Runs on every exit: an accepted pass prints the FINAL update; a bound trip or
    escalation prints the LAST draft it managed to write plus why it was held.
    """
    banner("FINAL STATUS UPDATE (draft, validator-approved, NOT posted)" if accepted
           else "LAST DRAFT (held, NOT posted, escalated to a human)")
    if draft.strip():
        print(draft.rstrip())
    else:
        print("(Cortex stopped before it produced a draft, nothing to show.)")
    if not accepted:
        print(f"\nWhy it was held: {reason}")

    if draft.strip():
        OUTPUT_DIR.mkdir(exist_ok=True)
        out = OUTPUT_DIR / f"status-update-{which}.md"
        state = "accepted by validator" if accepted else "HELD, escalated"
        out.write_text(
            f"<!-- Cortex draft, {state}; NOT posted. Run cost ~ ${cost:.4f}. -->\n"
            f"<!-- {reason} -->\n\n{draft.rstrip()}\n", encoding="utf-8")
        print(f"\nSaved draft -> {out.relative_to(Path(__file__).parent)}  "
              f"(for your review, nothing was posted)")


async def run(which: str = "happy") -> None:
    task = tools.get_task(which)
    if "error" in task:
        print(task)
        return

    banner(f"CORTEX RUN, fixture: task-{which}  (auto-queue cap {MAX_QUEUE_ITEMS} items)")
    print(task["body"])

    server = create_sdk_mcp_server(name=SERVER, tools=CORTEX_TOOLS)
    source_log: list[str] = [task["body"]]
    pending_calls: dict[str, tuple[str, dict]] = {}
    session_id: str | None = None
    turns_used, cost, revisions = 0, 0.0, 0
    last_draft = ""
    prompt = f"PM task brief:\n\n{task['body']}"

    while True:
        # Bounds are checked BEFORE every model call, outside the model.
        if cost >= COST_CAP_USD:
            reason = f"cost cap ${COST_CAP_USD} hit at ${cost:.4f}"
            banner(f"BOUND TRIPPED, {reason}. Halting and escalating to a human.")
            emit_deliverable(which, last_draft, accepted=False, reason=reason, cost=cost)
            return
        if turns_used >= MAX_ITERATIONS:
            break

        options = ClaudeAgentOptions(
            model=MODEL,
            system_prompt=CORTEX_SYSTEM,
            mcp_servers={SERVER: server},
            tools=[],                      # no built-in tools: no shell, no files, no web
            allowed_tools=ALLOWED,         # only the Cortex tools in tools.py
            max_turns=MAX_ITERATIONS - turns_used,
            max_budget_usd=max(COST_CAP_USD - cost, 0.0001),
            setting_sources=[],            # don't inherit CLAUDE.md / user settings
            resume=session_id,
        )

        proposed, result = "", None
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        name = block.name.removeprefix(f"mcp__{SERVER}__")
                        pending_calls[block.id] = (name, block.input)
                    elif isinstance(block, TextBlock):
                        proposed = block.text
            elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
                for block in msg.content:
                    if isinstance(block, ToolResultBlock) and block.tool_use_id in pending_calls:
                        name, args = pending_calls.pop(block.tool_use_id)
                        content = block.content
                        text = content if isinstance(content, str) else "".join(
                            p.get("text", "") for p in (content or []) if isinstance(p, dict))
                        source_log.append(f"{name}({args}) -> {text}")
                        print(f"\n[turn {turns_used + 1}] TOOL {name}({args})")
                        print(f"          -> {text[:300]}")
            elif isinstance(msg, ResultMessage):
                result = msg

        if result is None:
            emit_deliverable(which, last_draft, accepted=False,
                             reason="SDK returned no result", cost=cost)
            return
        session_id = result.session_id
        turns_used += result.num_turns or 0
        cost += result.total_cost_usd or 0.0

        if result.subtype == "error_max_budget_usd":
            reason = f"cost cap ${COST_CAP_USD} hit at ${cost:.4f}"
            banner(f"BOUND TRIPPED, {reason}. Halting and escalating to a human.")
            emit_deliverable(which, last_draft, accepted=False, reason=reason, cost=cost)
            return
        if result.subtype == "error_max_turns":
            break
        if result.is_error:
            emit_deliverable(which, last_draft, accepted=False,
                             reason=f"SDK error: {result.subtype} {result.errors}", cost=cost)
            return

        # No pending tool calls => Cortex produced a proposed output. Validate it.
        last_draft = result.result or proposed
        print(f"\n[turn {turns_used}] PROPOSED OUTPUT:\n{last_draft}")

        banner("CRITIC, independent validation")
        verdict = await review(MODEL, last_draft, "\n".join(source_log))
        cost += verdict["_cost"]
        print(json.dumps({k: v for k, v in verdict.items() if k != "_cost"}, indent=2))

        if verdict["verdict"] == "pass":
            banner(f"HITL CHECKPOINT, status update + any proposed stories queued for "
                   f"your review. Nothing posted, no commitments made. "
                   f"Run cost ≈ ${cost:.4f}")
            emit_deliverable(which, last_draft, accepted=True,
                             reason="validator passed", cost=cost)
            return

        if revisions >= MAX_REVISIONS:
            reason = f"validator rejected {MAX_REVISIONS}x (revision cap)"
            banner(f"REVISION CAP hit ({MAX_REVISIONS}). Escalating to a human "
                   f"instead of looping. Run cost ≈ ${cost:.4f}")
            emit_deliverable(which, last_draft, accepted=False, reason=reason, cost=cost)
            return

        revisions += 1
        print(f"\n-> critic rejected; revision {revisions}/{MAX_REVISIONS}")
        prompt = ("A validator rejected that for these reasons: "
                  f"{verdict['reasons']}. Fix it or escalate.")

    banner(f"MAX ITERATIONS ({MAX_ITERATIONS}) reached without finishing. "
           f"Escalating. Run cost ≈ ${cost:.4f}")
    emit_deliverable(which, last_draft, accepted=False,
                     reason=f"max iterations ({MAX_ITERATIONS}) reached", cost=cost)


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1] if len(sys.argv) > 1 else "happy"))
