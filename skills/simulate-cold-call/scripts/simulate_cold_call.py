"""LLM skill: drive one turn of a role-played cold-call prospect persona.

Stateless — the UI keeps the running conversation log and POSTs the entire
history each turn. The skill loads the persona from sim_personas.json, builds
a persona-shaped system prompt, replays the conversation, and returns the
prospect's next message as JSON.

CLI args:
  --persona-id     (required) one of the ids in data/raw/sim_personas.json
  --messages-file  (required) path to JSON array of {role, text} objects where
                              role is one of "trainee" | "prospect"
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.connect import ask_json  # noqa: E402
from utils.sdr_common import (  # noqa: E402
    make_envelope,
    make_skill_parser,
    run_step,
)


class ProspectTurn(BaseModel):
    prospect_response: str = Field(min_length=2, max_length=2000)
    suggested_objection_used: str | None = None
    confidence: float = Field(ge=0, le=1)


PERSONAS_PATH = REPO_ROOT / "data" / "raw" / "sim_personas.json"


def _load_personas() -> list[dict]:
    if not PERSONAS_PATH.exists():
        return []
    return json.loads(PERSONAS_PATH.read_text(encoding="utf-8"))


def _find_persona(persona_id: str) -> dict | None:
    for p in _load_personas():
        if p.get("id") == persona_id:
            return p
    return None


def _system_prompt(persona: dict) -> str:
    objections_block = "\n".join(f"  - {o}" for o in persona.get("top_objections", []))
    return (
        "You are role-playing as a prospect in a sales-training simulation. "
        "This is an educational SDR practice scenario; the trainee is a new "
        "Sales Development Representative practicing cold calls. Stay fully in "
        "character throughout — you ARE the prospect, not a coach.\n"
        "\n"
        f"PERSONA: {persona['name']}, {persona['role']} at {persona['company']} "
        f"({persona['vertical']} vertical).\n"
        "\n"
        f"PERSONALITY: {persona['personality']}\n"
        "\n"
        "YOUR TYPICAL OBJECTIONS (use one when fitting — don't list them, just "
        "raise one naturally if the trainee is vague, uses fluffy sales "
        "language, or hasn't earned more of your time):\n"
        f"{objections_block}\n"
        "\n"
        "RULES:\n"
        "- Stay in character. You are the prospect, not a coach.\n"
        "- Respond ONLY as the prospect would in this conversation.\n"
        "- Do NOT give the trainee tips, feedback, or coaching.\n"
        "- Keep responses to 2-4 sentences. Real prospects are not verbose.\n"
        "- If the trainee is vague or uses fluffy sales language ('just "
        "checking in', 'circle back', 'touch base'), push back with an "
        "objection from your list.\n"
        "- If discovery is genuinely good and value is clear, you can warm up "
        "and propose a next step.\n"
        "- Never break the fourth wall. Never say 'as an AI', 'as a model', "
        "or anything similar.\n"
        "\n"
        "You MUST return a JSON object with these fields filled in with real "
        "content — never echo the schema definition itself:\n"
        "  - prospect_response: your next message as the prospect (2-4 sentences)\n"
        "  - suggested_objection_used: the objection you raised (one of the "
        "objection strings above) or null if you didn't raise one this turn\n"
        "  - confidence: float 0-1 — your confidence you stayed in character"
    )


def _format_conversation(messages: list[dict], persona_name: str) -> str:
    """Render the conversation history in a way Claude can role-play against."""
    if not messages:
        return "(no turns yet — the trainee will speak first)"
    lines = []
    for m in messages:
        role = m.get("role", "trainee")
        text = m.get("text", "")
        speaker = persona_name.upper() if role == "prospect" else "TRAINEE"
        lines.append(f"{speaker}: {text}")
    return "\n\n".join(lines)


def _build_user_prompt(persona: dict, messages: list[dict]) -> str:
    convo = _format_conversation(messages, persona["name"])
    last = messages[-1] if messages else None
    if last and last.get("role") == "trainee":
        cue = (
            f"The trainee just said:\n\n\"{last.get('text', '')}\"\n\n"
            f"Respond as {persona['name']}. Keep it 2-4 sentences. Output JSON."
        )
    else:
        cue = (
            f"It's your turn to speak as {persona['name']}. Keep it 2-4 sentences. "
            "Output JSON."
        )
    return f"Conversation transcript:\n\n{convo}\n\n{cue}"


def do_work(args) -> dict:
    persona_id = getattr(args, "persona_id", None)
    if not persona_id:
        return make_envelope(
            status="error",
            error={"code": "persona_id_missing", "message": "--persona-id is required"},
        )

    persona = _find_persona(persona_id)
    if persona is None:
        return make_envelope(
            status="error",
            error={
                "code": "persona_not_found",
                "message": f"persona_id {persona_id!r} not present in {PERSONAS_PATH}",
            },
        )

    messages_file = getattr(args, "messages_file", None)
    if not messages_file:
        return make_envelope(
            status="error",
            error={"code": "messages_file_missing", "message": "--messages-file is required"},
        )

    messages_path = Path(messages_file)
    if not messages_path.exists():
        return make_envelope(
            status="error",
            error={"code": "messages_file_missing", "message": f"{messages_path} not found"},
        )

    try:
        messages = json.loads(messages_path.read_text(encoding="utf-8"))
        if not isinstance(messages, list):
            raise ValueError("messages-file must contain a JSON array")
    except (json.JSONDecodeError, ValueError) as exc:
        return make_envelope(
            status="error",
            error={"code": "messages_file_invalid", "message": str(exc)},
        )

    system_prompt = _system_prompt(persona)
    user_prompt = _build_user_prompt(persona, messages)

    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock is not None:
        turn = ProspectTurn.model_validate_json(mock)
    else:
        turn = ask_json(
            user_prompt,
            schema=ProspectTurn,
            system=system_prompt,
            model="claude-sonnet-4-6",
        )

    return make_envelope(
        status="ok",
        next_action="done",
        confidence=turn.confidence,
        review_required=False,
        artifact_refs=[],
        outputs={
            "persona_id": persona["id"],
            "persona_name": persona["name"],
            "prospect_response": turn.prospect_response,
            "suggested_objection_used": turn.suggested_objection_used,
            "n_messages_in": len(messages),
        },
    )


def main() -> int:
    parser = make_skill_parser("LLM skill: drive one turn of a role-played prospect persona")
    parser.add_argument("--persona-id", required=False)
    parser.add_argument("--messages-file", required=False)
    args = parser.parse_args()
    return run_step(args, do_work)


if __name__ == "__main__":
    raise SystemExit(main())
