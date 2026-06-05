"""FastAPI backend that wraps the 3-step SDR onboarding CLI workflow.

Endpoints expose the chain as a stateful HTTP API for the frontend at
http://localhost:5173. Run state lives in an in-memory dict — no database.

    uv run python workflow_server.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
WORKING_DIR = DATA_DIR / "working"
PROFILES_CSV = DATA_DIR / "raw" / "sdr_profiles.csv"

STEP_SCRIPTS: dict[str, Path] = {
    "generate-onboarding-plan": REPO_ROOT
    / "skills"
    / "generate-onboarding-plan"
    / "scripts"
    / "generate_onboarding_plan.py",
    "rank-trail-guides": REPO_ROOT / "automations" / "rank-trail-guides" / "scripts" / "rank_trail_guides.py",
    "welcome-new-hire": REPO_ROOT / "automations" / "welcome-new-hire" / "scripts" / "welcome_new_hire.py",
}
STEP_ORDER = list(STEP_SCRIPTS.keys())
LLM_STEPS = {"generate-onboarding-plan"}

# AI Tutor (Phase 1 of M04 — standalone Q&A, not part of the chain).
TUTOR_SCRIPT = REPO_ROOT / "skills" / "answer-sdr-question" / "scripts" / "answer_sdr_question.py"
GAP_TRACKER_PATH = DATA_DIR / "gap_tracker.json"

# Coaching Notes (M04 — manager uploads a transcript on demand, scored against
# the gold-standard rubric in rag/knowledge_base/cold_call_quality_rubric.md).
# Standalone — the score-cold-call skill is no longer part of the 3-step chain.
SCORE_COLD_CALL_SCRIPT = REPO_ROOT / "skills" / "score-cold-call" / "scripts" / "score_cold_call.py"
COACHING_DIR = WORKING_DIR / "coaching"
COACHING_SESSIONS: dict[str, dict[str, Any]] = {}

# Onboarding debrief (M04 — UI walks a newly-certified SDR through QUESTIONS.md,
# the skill synthesizes a manager-facing program debrief grounded in the
# territory + vertical playbook).
GENERATE_HANDOFF_DOC_SCRIPT = REPO_ROOT / "skills" / "generate-handoff-doc" / "scripts" / "generate_handoff_doc.py"
OFFBOARDING_DIR = WORKING_DIR / "offboarding"
OFFBOARDING_SESSIONS: dict[str, dict[str, Any]] = {}

# Cold Call Simulation (M04 round 2 — trainee practices vs. an LLM-driven
# persona; debrief uses Coaching Rubric v3.1). Both skills are stateless;
# the UI keeps the running conversation log and POSTs it every turn.
SIMULATE_COLD_CALL_SCRIPT = REPO_ROOT / "skills" / "simulate-cold-call" / "scripts" / "simulate_cold_call.py"
DEBRIEF_COLD_CALL_SCRIPT = REPO_ROOT / "skills" / "debrief-cold-call" / "scripts" / "debrief_cold_call.py"
SIM_PERSONAS_PATH = DATA_DIR / "raw" / "sim_personas.json"
SIMULATION_DIR = WORKING_DIR / "simulation"

# Certification Gap Analysis (M04 step 7 — manager-view cohort roster of all
# SDRs with PASS/BORDERLINE/FAIL badges and per-dimension gap analyses scored
# against rag/knowledge_base/certification_rubric.md). Read-only on persisted
# data under data/sdr_records/ (no live exam intake UI in this release).
SCORE_CERTIFICATION_SCRIPT = REPO_ROOT / "skills" / "score-certification" / "scripts" / "score_certification.py"
SDR_RECORDS_DIR = DATA_DIR / "sdr_records"
CERTIFICATION_DIR = WORKING_DIR / "certification"

# Dashboard + decision log (Phase 4). Every approve/edit/reject/escalate from
# either the chain or the tutor is appended to DECISION_LOG_PATH so the
# dashboard can compute approval/edit/rejection rates and show recent activity.
DECISION_LOG_PATH = DATA_DIR / "decision_log.json"

# Demo numbers for the 4 process metrics the original app's dashboard surfaced.
# These are aspirational — this system cannot derive them from its own data —
# so we hardcode plausible "after AI rollout" values per the spec.
DEMO_BASELINE_TARGETS = [
    {
        "key": "time_to_cert",
        "label": "Time to certification",
        "baseline": 6.0,
        "current": 4.2,
        "target": 4.0,
        "unit": "weeks",
        "source": "demo",
    },
    {
        "key": "feedback_latency",
        "label": "Cold-call feedback latency",
        "baseline": 48.0,
        "current": 3.5,
        "target": 4.0,
        "unit": "hours",
        "source": "demo",
    },
    {
        "key": "manager_review",
        "label": "Manager review time per rep",
        "baseline": 4.0,
        "current": 0.8,
        "target": 1.0,
        "unit": "hours",
        "source": "demo",
    },
    {
        "key": "content_update_lag",
        "label": "KB content update lag",
        "baseline": 7.5,
        "current": 0.5,
        "target": 1.0,
        "unit": "days",
        "source": "demo",
    },
]

RUNS: dict[str, dict[str, Any]] = {}


app = FastAPI(title="SDR KT Onboarding Workflow API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApprovalDecision(BaseModel):
    decision: str  # "approve" | "reject" | "escalate"
    note: str = ""
    # When set on an approve, overwrite the paused step's first artifact with
    # this content before resuming. The review_log entry is tagged edited=true.
    edited_content: str | None = None


class TutorAskRequest(BaseModel):
    question: str


class TutorApproveRequest(BaseModel):
    question: str
    answer: str
    edited_answer: str | None = None


class TutorRejectRequest(BaseModel):
    question: str
    answer: str
    reason: str = ""


class CoachingScoreRequest(BaseModel):
    hire_id: str
    transcript_text: str
    call_context: str = ""
    outcome: str = "unknown"


class CoachingApprovalRequest(BaseModel):
    session_id: str
    decision: str  # "approve" | "reject"
    note: str = ""
    edited_content: str | None = None


class OffboardingRepInfo(BaseModel):
    name: str
    territory: str
    vertical: str


class OffboardingQA(BaseModel):
    question_id: int
    question: str
    answer: str


class OffboardingSynthesizeRequest(BaseModel):
    rep_info: OffboardingRepInfo
    qa_pairs: list[OffboardingQA]


class OffboardingApprovalRequest(BaseModel):
    session_id: str
    decision: str  # "approve" | "reject"
    note: str = ""
    edited_content: str | None = None


class CertificationDecideRequest(BaseModel):
    sdr_id: str
    decision: str  # "pass" | "fail"
    comment: str


class SimulationMessage(BaseModel):
    role: str  # "trainee" | "prospect"
    text: str


class SimulationTurnRequest(BaseModel):
    persona_id: str
    messages: list[SimulationMessage]


class SimulationDebriefRequest(BaseModel):
    persona_id: str
    messages: list[SimulationMessage]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_artifact(run_id: str, artifact_refs: list[str]) -> str | None:
    if not artifact_refs:
        return None
    artifact_path = WORKING_DIR / run_id / artifact_refs[0]
    if not artifact_path.exists():
        return None
    return artifact_path.read_text(encoding="utf-8")


def _refresh_artifacts(run: dict[str, Any]) -> None:
    """Re-read artifact content from disk for every completed step."""
    for step in run["completed_steps"]:
        refs = step.get("envelope", {}).get("artifact_refs") or []
        step["artifact_content"] = _read_artifact(run["workflow_run_id"], refs)


def _run_step(step_name: str, run_id: str, hire_id: str) -> dict[str, Any]:
    script = STEP_SCRIPTS[step_name]
    cmd = [
        "uv",
        "run",
        "python",
        str(script),
        "--hire-id",
        hire_id,
        "--workflow-run-id",
        run_id,
        "--step-id",
        step_name,
        "--json",
        "--data-dir",
        str(DATA_DIR),
        "--out-dir",
        str(WORKING_DIR),
    ]
    env = os.environ.copy()
    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if step_name in LLM_STEPS and mock:
        env["MOCK_LLM_RESPONSE"] = mock
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {
                "code": "no_output",
                "message": (completed.stderr or "").strip() or "step produced no output",
            },
        }
    try:
        return json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {"code": "invalid_envelope", "message": str(exc)},
        }


def _next_step_after(step_name: str) -> str | None:
    idx = STEP_ORDER.index(step_name)
    if idx + 1 >= len(STEP_ORDER):
        return None
    return STEP_ORDER[idx + 1]


def _advance(run: dict[str, Any], start_step: str) -> dict[str, Any]:
    """Run steps in order starting from start_step, mutating run in place."""
    step_name: str | None = start_step
    while step_name is not None:
        envelope = _run_step(step_name, run["workflow_run_id"], run["hire_id"])
        artifact_content = _read_artifact(
            run["workflow_run_id"], envelope.get("artifact_refs") or []
        )
        run["completed_steps"].append(
            {
                "step_name": step_name,
                "envelope": envelope,
                "artifact_content": artifact_content,
            }
        )
        run["updated_at"] = _now()

        if envelope.get("status") == "error":
            run["status"] = "rejected"
            run["pending_step"] = None
            run["review_envelope"] = None
            return run

        if envelope.get("review_required"):
            next_step = _next_step_after(step_name)
            run["status"] = "paused"
            run["pending_step"] = next_step
            run["review_envelope"] = envelope
            return run

        next_step = _next_step_after(step_name)
        if next_step is None:
            run["status"] = "complete"
            run["pending_step"] = None
            run["review_envelope"] = None
            return run
        step_name = next_step
    return run


@app.get("/hires")
def list_hires() -> list[dict[str, Any]]:
    if not PROFILES_CSV.exists():
        raise HTTPException(status_code=500, detail=f"{PROFILES_CSV} not found")
    return pl.read_csv(PROFILES_CSV).to_dicts()


@app.post("/run/{hire_id}")
def start_run(hire_id: str) -> dict[str, Any]:
    profiles = pl.read_csv(PROFILES_CSV)
    row = profiles.filter(pl.col("hire_id") == hire_id)
    if row.is_empty():
        raise HTTPException(status_code=404, detail=f"hire_id {hire_id!r} not found")
    hire_name = row.row(0, named=True)["name"]

    workflow_run_id = f"wf-{uuid.uuid4().hex[:12]}"
    now = _now()
    run: dict[str, Any] = {
        "workflow_run_id": workflow_run_id,
        "hire_id": hire_id,
        "hire_name": hire_name,
        "status": "running",
        "completed_steps": [],
        "pending_step": None,
        "review_envelope": None,
        "review_log": [],
        "started_at": now,
        "updated_at": now,
    }
    RUNS[workflow_run_id] = run

    _advance(run, STEP_ORDER[0])
    return run


@app.post("/runs/{workflow_run_id}/approve")
def approve_run(workflow_run_id: str, decision: ApprovalDecision) -> dict[str, Any]:
    run = RUNS.get(workflow_run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"run {workflow_run_id!r} not found")

    if decision.decision not in {"approve", "reject", "escalate"}:
        raise HTTPException(
            status_code=400,
            detail=f"decision must be approve|reject|escalate, got {decision.decision!r}",
        )

    edited = bool(decision.edited_content)

    # Approve+edit: overwrite the most recent completed step's first artifact
    # with the human-edited content before resuming the chain. This way the
    # paused step's artifact on disk reflects the human-approved version, and
    # any downstream step that reads the artifact (or the UI on next refresh)
    # sees the edit.
    if decision.decision == "approve" and edited and run["completed_steps"]:
        last_step = run["completed_steps"][-1]
        refs = last_step.get("envelope", {}).get("artifact_refs") or []
        if refs:
            artifact_path = WORKING_DIR / run["workflow_run_id"] / refs[0]
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(decision.edited_content, encoding="utf-8")
            last_step["artifact_content"] = decision.edited_content

    log_entry = {
        "decision": decision.decision,
        "note": decision.note,
        "timestamp": _now(),
        "at_step": run.get("pending_step"),
        "edited": edited and decision.decision == "approve",
    }
    run["review_log"].append(log_entry)
    run["updated_at"] = _now()

    # Persist to the cross-system decision log so the dashboard can count it.
    # An approve with edited_content counts as "edit" so rates separate the two.
    persisted_action = (
        "edit" if (decision.decision == "approve" and edited) else decision.decision
    )
    _append_decision(
        {
            "timestamp": log_entry["timestamp"],
            "feature": "chain",
            "action": persisted_action,
            "context": {
                "run_id": run["workflow_run_id"],
                "hire_id": run.get("hire_id"),
                "at_step": log_entry["at_step"],
                "note": decision.note,
                "edited": log_entry["edited"],
            },
        }
    )

    if decision.decision == "reject":
        run["status"] = "rejected"
        run["pending_step"] = None
        run["review_envelope"] = None
        return run
    if decision.decision == "escalate":
        run["status"] = "escalated"
        run["pending_step"] = None
        run["review_envelope"] = None
        return run

    pending = run.get("pending_step")
    if pending is None:
        run["status"] = "complete"
        run["review_envelope"] = None
        return run
    run["status"] = "running"
    run["review_envelope"] = None
    _advance(run, pending)
    return run


@app.get("/runs/{workflow_run_id}")
def get_run(workflow_run_id: str) -> dict[str, Any]:
    run = RUNS.get(workflow_run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"run {workflow_run_id!r} not found")
    _refresh_artifacts(run)
    return run


@app.get("/runs")
def list_runs() -> list[dict[str, Any]]:
    summaries = [
        {
            "workflow_run_id": r["workflow_run_id"],
            "hire_id": r["hire_id"],
            "hire_name": r["hire_name"],
            "status": r["status"],
            "started_at": r["started_at"],
        }
        for r in RUNS.values()
    ]
    summaries.sort(key=lambda r: r["started_at"], reverse=True)
    return summaries


# ---------------------------------------------------------------------------
# AI Tutor endpoints (Phase 1 of M04)
# ---------------------------------------------------------------------------


def _run_tutor(question: str) -> dict[str, Any]:
    cmd = [
        "uv",
        "run",
        "python",
        str(TUTOR_SCRIPT),
        "--question",
        question,
        "--json",
    ]
    env = os.environ.copy()
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {
                "code": "no_output",
                "message": (completed.stderr or "").strip() or "tutor produced no output",
            },
        }
    try:
        return json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {"code": "invalid_envelope", "message": str(exc)},
        }


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _append_json_list(path: Path, entry: dict[str, Any]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = _read_json_list(path)
    entries.append(entry)
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    return len(entries)


def _append_gap(entry: dict[str, Any]) -> int:
    return _append_json_list(GAP_TRACKER_PATH, entry)


def _append_decision(entry: dict[str, Any]) -> int:
    return _append_json_list(DECISION_LOG_PATH, entry)


@app.post("/tutor/ask")
def tutor_ask(req: TutorAskRequest) -> dict[str, Any]:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    envelope = _run_tutor(req.question)
    # Log low-confidence answers as gaps so the dashboard's "open gaps" list
    # surfaces topics a human should fill — without waiting for a reject.
    outputs = envelope.get("outputs") or {}
    if outputs.get("flagged") is True:
        _append_gap(
            {
                "type": "low_confidence_query",
                "question": req.question,
                "confidence_score": outputs.get("confidence_score"),
                "timestamp": _now(),
            }
        )
    return envelope


@app.post("/tutor/approve")
def tutor_approve(req: TutorApproveRequest) -> dict[str, Any]:
    from rag.embeddings_retrieval import add_approved_qa, collection_size

    final_answer = req.edited_answer if req.edited_answer is not None else req.answer
    qa_id = add_approved_qa(req.question, final_answer)
    edited = req.edited_answer is not None and req.edited_answer != req.answer
    _append_decision(
        {
            "timestamp": _now(),
            "feature": "tutor",
            "action": "edit" if edited else "approve",
            "context": {
                "question": req.question,
                "qa_id": qa_id,
                "edited": edited,
            },
        }
    )
    return {
        "status": "approved",
        "qa_id": qa_id,
        "edited": req.edited_answer is not None,
        "answer_written": final_answer,
        "kb_chunk_count": collection_size(),
    }


@app.post("/tutor/reject")
def tutor_reject(req: TutorRejectRequest) -> dict[str, Any]:
    now = _now()
    gap_index = _append_gap(
        {
            "type": "rejected_answer",
            "question": req.question,
            "rejected_answer": req.answer,
            "reason": req.reason,
            "timestamp": now,
        }
    )
    _append_decision(
        {
            "timestamp": now,
            "feature": "tutor",
            "action": "reject",
            "context": {
                "question": req.question,
                "reason": req.reason,
                "gap_index": gap_index,
            },
        }
    )
    return {
        "status": "rejected",
        "kb_written": False,
        "gap_index": gap_index,
        "gap_tracker_path": str(GAP_TRACKER_PATH.relative_to(REPO_ROOT)),
    }


# ---------------------------------------------------------------------------
# Dashboard (Phase 4 of M04)
# ---------------------------------------------------------------------------


def _decision_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(entries)
    counts = {"approve": 0, "edit": 0, "reject": 0, "escalate": 0}
    for e in entries:
        action = e.get("action")
        if action in counts:
            counts[action] += 1
    if total == 0:
        rates = {"approval_rate": 0.0, "edit_rate": 0.0, "rejection_rate": 0.0, "escalation_rate": 0.0}
    else:
        rates = {
            "approval_rate": round(counts["approve"] / total, 4),
            "edit_rate": round(counts["edit"] / total, 4),
            "rejection_rate": round(counts["reject"] / total, 4),
            "escalation_rate": round(counts["escalate"] / total, 4),
        }
    return {
        "total_interactions": total,
        "counts": counts,
        **rates,
    }


@app.get("/dashboard/metrics")
def dashboard_metrics() -> dict[str, Any]:
    """Aggregate everything the dashboard needs in one round-trip.

    Real metrics are computed from disk (decision_log.json, gap_tracker.json,
    ChromaDB collection). The four ``baseline_targets`` are demo numbers from
    the spec — this system can't derive time-to-cert / latency / lag from
    its own data, so they're hardcoded with ``source: "demo"`` so the UI
    can label them accordingly.
    """
    from rag.embeddings_retrieval import collection_size

    decisions = _read_json_list(DECISION_LOG_PATH)
    gaps = _read_json_list(GAP_TRACKER_PATH)
    summary = _decision_summary(decisions)

    try:
        kb_chunk_count = collection_size()
    except Exception:
        # ChromaDB may not be initialized in a fresh environment; that's fine.
        kb_chunk_count = 0

    # By-feature breakdown so the UI can show "tutor vs chain" if it wants.
    by_feature: dict[str, dict[str, int]] = {"tutor": {}, "chain": {}}
    for e in decisions:
        feat = e.get("feature", "unknown")
        action = e.get("action", "unknown")
        by_feature.setdefault(feat, {})
        by_feature[feat][action] = by_feature[feat].get(action, 0) + 1

    return {
        "kb_chunk_count": kb_chunk_count,
        **summary,
        "by_feature": by_feature,
        "open_gap_count": len(gaps),
        "recent_decisions": list(reversed(decisions[-10:])),
        "open_gaps": list(reversed(gaps[-10:])),
        "baseline_targets": DEMO_BASELINE_TARGETS,
    }


@app.get("/dashboard/gaps")
def dashboard_gaps() -> list[dict[str, Any]]:
    """Full gap tracker contents (newest first) for the dedicated gap view."""
    return list(reversed(_read_json_list(GAP_TRACKER_PATH)))


# ---------------------------------------------------------------------------
# Coaching Notes endpoints (M04 — standalone transcript scoring)
# ---------------------------------------------------------------------------


_ROLE_PREFIX_RE = re.compile(r"^(sdr|prospect)\s*:\s*(.*)$", re.IGNORECASE)


def _transcript_to_messages(text: str) -> tuple[list[dict[str, str]], str | None]:
    """Parse raw transcript text into the schema score-cold-call expects.

    Accepts either:
      - A JSON object with the same shape as sample_transcript.json
        ({"messages": [...], "outcome": "..."}). Used verbatim.
      - Free-form text with role-prefixed lines like "SDR: ..." / "Prospect: ...".

    Returns (messages, outcome_override). If the text is JSON, ``outcome_override``
    is the JSON's outcome (if present); otherwise None and the caller uses the
    explicit outcome passed in the request.
    """
    text = (text or "").strip()
    if not text:
        return [], None

    if text.startswith("{"):
        try:
            data = json.loads(text)
            if isinstance(data, dict) and isinstance(data.get("messages"), list):
                return data["messages"], data.get("outcome")
        except json.JSONDecodeError:
            pass

    messages: list[dict[str, str]] = []
    current_role = "sdr"
    current_text: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = _ROLE_PREFIX_RE.match(line)
        if m:
            if current_text:
                messages.append({"role": current_role, "text": " ".join(current_text).strip()})
                current_text = []
            current_role = m.group(1).lower()
            tail = m.group(2).strip()
            if tail:
                current_text.append(tail)
        else:
            current_text.append(line)
    if current_text:
        messages.append({"role": current_role, "text": " ".join(current_text).strip()})
    if not messages:
        messages = [{"role": "sdr", "text": text}]
    return messages, None


def _read_coaching_artifact(session_id: str, artifact_refs: list[str]) -> str | None:
    if not artifact_refs:
        return None
    path = COACHING_DIR / session_id / artifact_refs[0]
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _run_score_cold_call(transcript_path: Path, hire_id: str, session_id: str) -> dict[str, Any]:
    cmd = [
        "uv",
        "run",
        "python",
        str(SCORE_COLD_CALL_SCRIPT),
        "--hire-id",
        hire_id,
        "--workflow-run-id",
        session_id,
        "--step-id",
        "score-cold-call",
        "--json",
        "--data-dir",
        str(DATA_DIR),
        "--out-dir",
        str(COACHING_DIR),
        "--transcript-file",
        str(transcript_path),
    ]
    env = os.environ.copy()
    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock:
        env["MOCK_LLM_RESPONSE"] = mock
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {
                "code": "no_output",
                "message": (completed.stderr or "").strip() or "coaching skill produced no output",
            },
        }
    try:
        return json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {"code": "invalid_envelope", "message": str(exc)},
        }


def _coaching_session_status(envelope: dict[str, Any]) -> str:
    if envelope.get("status") == "error":
        return "error"
    if envelope.get("review_required"):
        return "paused"
    return "complete"


@app.post("/coaching/score")
def coaching_score(req: CoachingScoreRequest) -> dict[str, Any]:
    if not req.transcript_text.strip():
        raise HTTPException(status_code=400, detail="transcript_text is required")

    profiles = pl.read_csv(PROFILES_CSV)
    row = profiles.filter(pl.col("hire_id") == req.hire_id)
    if row.is_empty():
        raise HTTPException(status_code=404, detail=f"hire_id {req.hire_id!r} not found")
    hire_name = row.row(0, named=True)["name"]

    messages, outcome_override = _transcript_to_messages(req.transcript_text)
    outcome = outcome_override or req.outcome or "unknown"

    session_id = f"co-{uuid.uuid4().hex[:12]}"
    session_dir = COACHING_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = session_dir / "transcript.json"
    transcript_path.write_text(
        json.dumps(
            {
                "hire_id": req.hire_id,
                "messages": messages,
                "outcome": outcome,
                "call_context": req.call_context,
            },
            indent=2,
        )
    )

    envelope = _run_score_cold_call(transcript_path, req.hire_id, session_id)
    artifact_content = _read_coaching_artifact(session_id, envelope.get("artifact_refs") or [])
    now = _now()

    session: dict[str, Any] = {
        "session_id": session_id,
        "hire_id": req.hire_id,
        "hire_name": hire_name,
        "envelope": envelope,
        "artifact_content": artifact_content,
        "call_context": req.call_context,
        "outcome": outcome,
        "status": _coaching_session_status(envelope),
        "review_log": [],
        "created_at": now,
        "updated_at": now,
    }
    COACHING_SESSIONS[session_id] = session
    return session


@app.post("/coaching/approve")
def coaching_approve(req: CoachingApprovalRequest) -> dict[str, Any]:
    session = COACHING_SESSIONS.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"session {req.session_id!r} not found")

    if req.decision not in {"approve", "reject"}:
        raise HTTPException(
            status_code=400,
            detail=f"decision must be approve|reject, got {req.decision!r}",
        )

    edited = bool(req.edited_content)
    if req.decision == "approve" and edited:
        refs = session.get("envelope", {}).get("artifact_refs") or []
        if refs:
            artifact_path = COACHING_DIR / req.session_id / refs[0]
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(req.edited_content, encoding="utf-8")
            session["artifact_content"] = req.edited_content

    now = _now()
    log_entry = {
        "decision": req.decision,
        "note": req.note,
        "timestamp": now,
        "edited": edited and req.decision == "approve",
    }
    session["review_log"].append(log_entry)
    session["updated_at"] = now

    persisted_action = "edit" if (req.decision == "approve" and edited) else req.decision
    _append_decision(
        {
            "timestamp": now,
            "feature": "coaching",
            "action": persisted_action,
            "context": {
                "session_id": req.session_id,
                "hire_id": session.get("hire_id"),
                "note": req.note,
                "edited": log_entry["edited"],
            },
        }
    )

    session["status"] = "rejected" if req.decision == "reject" else "complete"
    return session


@app.get("/coaching/sessions/{session_id}")
def get_coaching_session(session_id: str) -> dict[str, Any]:
    session = COACHING_SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"session {session_id!r} not found")
    refs = session.get("envelope", {}).get("artifact_refs") or []
    session["artifact_content"] = _read_coaching_artifact(session_id, refs)
    return session


# ---------------------------------------------------------------------------
# Onboarding debrief endpoints (M04 — post-cert process questions → manager debrief)
# ---------------------------------------------------------------------------


def _read_offboarding_artifact(session_id: str, artifact_refs: list[str]) -> str | None:
    if not artifact_refs:
        return None
    path = OFFBOARDING_DIR / session_id / artifact_refs[0]
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _run_generate_handoff_doc(interview_path: Path, session_id: str) -> dict[str, Any]:
    cmd = [
        "uv",
        "run",
        "python",
        str(GENERATE_HANDOFF_DOC_SCRIPT),
        "--workflow-run-id",
        session_id,
        "--step-id",
        "generate-handoff-doc",
        "--json",
        "--data-dir",
        str(DATA_DIR),
        "--out-dir",
        str(OFFBOARDING_DIR),
        "--interview-file",
        str(interview_path),
    ]
    env = os.environ.copy()
    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock:
        env["MOCK_LLM_RESPONSE"] = mock
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {
                "code": "no_output",
                "message": (completed.stderr or "").strip() or "handoff skill produced no output",
            },
        }
    try:
        return json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {"code": "invalid_envelope", "message": str(exc)},
        }


def _offboarding_session_status(envelope: dict[str, Any]) -> str:
    if envelope.get("status") == "error":
        return "error"
    if envelope.get("review_required"):
        return "paused"
    return "complete"


@app.post("/offboarding/synthesize")
def offboarding_synthesize(req: OffboardingSynthesizeRequest) -> dict[str, Any]:
    if not req.qa_pairs:
        raise HTTPException(status_code=400, detail="qa_pairs is required")

    session_id = f"off-{uuid.uuid4().hex[:12]}"
    session_dir = OFFBOARDING_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    interview_path = session_dir / "interview.json"
    interview_path.write_text(
        json.dumps(
            {
                "rep_info": req.rep_info.model_dump(),
                "qa_pairs": [qa.model_dump() for qa in req.qa_pairs],
            },
            indent=2,
        )
    )

    envelope = _run_generate_handoff_doc(interview_path, session_id)
    artifact_content = _read_offboarding_artifact(session_id, envelope.get("artifact_refs") or [])
    now = _now()

    session: dict[str, Any] = {
        "session_id": session_id,
        "rep_info": req.rep_info.model_dump(),
        "envelope": envelope,
        "artifact_content": artifact_content,
        "status": _offboarding_session_status(envelope),
        "review_log": [],
        "created_at": now,
        "updated_at": now,
    }
    OFFBOARDING_SESSIONS[session_id] = session
    return session


@app.post("/offboarding/{session_id}/approve")
def offboarding_approve(session_id: str, req: OffboardingApprovalRequest) -> dict[str, Any]:
    if req.session_id and req.session_id != session_id:
        raise HTTPException(
            status_code=400,
            detail=f"session_id mismatch: url {session_id!r} vs body {req.session_id!r}",
        )

    session = OFFBOARDING_SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"session {session_id!r} not found")

    if req.decision not in {"approve", "reject"}:
        raise HTTPException(
            status_code=400,
            detail=f"decision must be approve|reject, got {req.decision!r}",
        )

    edited = bool(req.edited_content)
    if req.decision == "approve" and edited:
        refs = session.get("envelope", {}).get("artifact_refs") or []
        if refs:
            artifact_path = OFFBOARDING_DIR / session_id / refs[0]
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(req.edited_content, encoding="utf-8")
            session["artifact_content"] = req.edited_content

    now = _now()
    log_entry = {
        "decision": req.decision,
        "note": req.note,
        "timestamp": now,
        "edited": edited and req.decision == "approve",
    }
    session["review_log"].append(log_entry)
    session["updated_at"] = now

    persisted_action = "edit" if (req.decision == "approve" and edited) else req.decision
    _append_decision(
        {
            "timestamp": now,
            "feature": "offboarding",
            "action": persisted_action,
            "context": {
                "session_id": session_id,
                "rep_name": session.get("rep_info", {}).get("name"),
                "note": req.note,
                "edited": log_entry["edited"],
            },
        }
    )

    session["status"] = "rejected" if req.decision == "reject" else "complete"
    return session


@app.get("/offboarding/sessions")
def list_offboarding_sessions() -> list[dict[str, Any]]:
    """Manager's review queue: every debrief session (newly-certified SDR's
    post-certification onboarding debrief) the backend has seen this process
    lifetime. Most-recent first.

    Returns a lean row per session so the manager-side roster page can list them
    without loading the full artifact content for each. Per-session detail is
    available via ``GET /offboarding/{session_id}``.
    """
    rows: list[dict[str, Any]] = []
    for session_id, session in OFFBOARDING_SESSIONS.items():
        rep_info = session.get("rep_info") or {}
        envelope = session.get("envelope") or {}
        outputs = envelope.get("outputs") or {}
        rows.append(
            {
                "session_id": session_id,
                "rep_name": rep_info.get("name"),
                "territory": rep_info.get("territory"),
                "vertical": rep_info.get("vertical"),
                "status": session.get("status", "pending"),
                "created_at": session.get("created_at"),
                "updated_at": session.get("updated_at"),
                "confidence": envelope.get("confidence"),
                "review_required": envelope.get("review_required"),
                "n_elements": outputs.get("n_elements"),
            }
        )
    rows.sort(key=lambda r: r.get("created_at") or "", reverse=True)
    return rows


@app.get("/offboarding/{session_id}")
def get_offboarding_session(session_id: str) -> dict[str, Any]:
    session = OFFBOARDING_SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"session {session_id!r} not found")
    refs = session.get("envelope", {}).get("artifact_refs") or []
    session["artifact_content"] = _read_offboarding_artifact(session_id, refs)
    return session


# ---------------------------------------------------------------------------
# Certification Gap Analysis endpoints (M04 step 7 — manager-view cohort roster)
# ---------------------------------------------------------------------------


def _load_sdr_record(sdr_id: str) -> dict[str, Any] | None:
    path = SDR_RECORDS_DIR / f"{sdr_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_cached_gap_analysis(sdr_id: str) -> dict[str, Any] | None:
    path = SDR_RECORDS_DIR / sdr_id / "gap_analysis.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _resolve_record_artifact(rel_path: str) -> str | None:
    """Read an artifact path stored on an SDR record event (path is relative to
    data/sdr_records/). Returns None on missing or unreadable files."""
    if not rel_path:
        return None
    full = SDR_RECORDS_DIR / rel_path
    if not full.exists() or not full.is_file():
        return None
    try:
        return full.read_text(encoding="utf-8")
    except OSError:
        return None


def _resolve_record_artifacts(record: dict[str, Any]) -> dict[str, str]:
    """Resolve every artifact file referenced by a record's events into a
    {filename: contents} dict. Skips missing files silently."""
    resolved: dict[str, str] = {}
    for event in record.get("events", []):
        for key in ("transcript_file", "qa_file", "note_file"):
            rel = event.get(key)
            if not rel:
                continue
            content = _resolve_record_artifact(rel)
            if content is not None:
                resolved[rel] = content
    return resolved


def _roster_row(sdr_id: str) -> dict[str, Any] | None:
    record = _load_sdr_record(sdr_id)
    if record is None:
        return None
    gap = _load_cached_gap_analysis(sdr_id)
    overall = "not_analyzed"
    weakest = None
    confidence = None
    last_analyzed_at = None
    if gap:
        outputs = gap.get("outputs") or {}
        overall = outputs.get("overall_recommendation") or "not_analyzed"
        weakest = outputs.get("weakest_dimension")
        confidence = gap.get("confidence")
        last_analyzed_at = outputs.get("generated_at")
    return {
        "sdr_id": sdr_id,
        "name": record.get("name"),
        "cohort": record.get("cohort"),
        "territory": record.get("territory"),
        "experience_level": record.get("experience_level"),
        "overall_recommendation": overall,
        "weakest_dimension": weakest,
        "confidence": confidence,
        "last_analyzed_at": last_analyzed_at,
        "event_count": len(record.get("events", [])),
    }


def _run_score_certification(sdr_id: str) -> dict[str, Any]:
    cmd = [
        "uv",
        "run",
        "python",
        str(SCORE_CERTIFICATION_SCRIPT),
        "--sdr-id",
        sdr_id,
        "--workflow-run-id",
        f"cert-{sdr_id}",
        "--step-id",
        "score-certification",
        "--idempotency-mode",
        "replace",
        "--json",
        "--data-dir",
        str(DATA_DIR),
        "--out-dir",
        str(CERTIFICATION_DIR),
    ]
    env = os.environ.copy()
    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock:
        env["MOCK_LLM_RESPONSE"] = mock
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {
                "code": "no_output",
                "message": (completed.stderr or "").strip() or "score-certification produced no output",
            },
        }
    try:
        return json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "next_action": None,
            "confidence": None,
            "review_required": False,
            "artifact_refs": [],
            "outputs": {},
            "error": {"code": "invalid_envelope", "message": str(exc)},
        }


@app.get("/certification/roster")
def certification_roster() -> list[dict[str, Any]]:
    if not SDR_RECORDS_DIR.exists():
        return []
    rows: list[dict[str, Any]] = []
    for json_path in sorted(SDR_RECORDS_DIR.glob("*.json")):
        sdr_id = json_path.stem
        row = _roster_row(sdr_id)
        if row is not None:
            rows.append(row)
    return rows


@app.get("/certification/sdr/{sdr_id}")
def certification_sdr_detail(sdr_id: str) -> dict[str, Any]:
    record = _load_sdr_record(sdr_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"SDR record {sdr_id!r} not found")
    resolved = _resolve_record_artifacts(record)
    gap = _load_cached_gap_analysis(sdr_id)
    return {
        "record": record,
        "resolved_artifacts": resolved,
        "gap_analysis": gap,
    }


@app.post("/certification/sdr/{sdr_id}/analyze")
def certification_analyze(sdr_id: str) -> dict[str, Any]:
    if _load_sdr_record(sdr_id) is None:
        raise HTTPException(status_code=404, detail=f"SDR record {sdr_id!r} not found")
    envelope = _run_score_certification(sdr_id)
    if envelope.get("status") == "error":
        raise HTTPException(
            status_code=500,
            detail=envelope.get("error") or {"code": "unknown", "message": "score-certification failed"},
        )
    return envelope


@app.post("/certification/decide")
def certification_decide(req: CertificationDecideRequest) -> dict[str, Any]:
    if req.decision not in {"pass", "fail"}:
        raise HTTPException(
            status_code=400,
            detail=f"decision must be pass|fail, got {req.decision!r}",
        )
    if not req.comment.strip():
        raise HTTPException(status_code=400, detail="comment is required")
    if _load_sdr_record(req.sdr_id) is None:
        raise HTTPException(status_code=404, detail=f"SDR record {req.sdr_id!r} not found")

    action = "approve" if req.decision == "pass" else "reject"
    decision_index = _append_decision(
        {
            "timestamp": _now(),
            "feature": "certification",
            "action": action,
            "context": {
                "sdr_id": req.sdr_id,
                "decision": req.decision,
                "comment": req.comment.strip(),
            },
        }
    )
    return {
        "status": "logged",
        "decision": req.decision,
        "decision_index": decision_index,
        "sdr_id": req.sdr_id,
    }


# ---------------------------------------------------------------------------
# Cold Call Simulation endpoints (M04 round 2 — trainee feature)
# ---------------------------------------------------------------------------


def _run_simulation_skill(
    script: Path,
    *,
    persona_id: str,
    messages: list[SimulationMessage],
) -> tuple[dict[str, Any], str]:
    """Spawn the simulation or debrief skill; return (envelope, session_id).

    Each invocation creates a fresh session_id under SIMULATION_DIR. The
    messages file is written there; the script reads it via --messages-file.
    """
    SIMULATION_DIR.mkdir(parents=True, exist_ok=True)
    session_id = f"sim-{uuid.uuid4().hex[:12]}"
    session_dir = SIMULATION_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    msg_path = session_dir / "messages.json"
    msg_path.write_text(
        json.dumps([m.model_dump() for m in messages], indent=2)
    )

    cmd = [
        "uv",
        "run",
        "python",
        str(script),
        "--persona-id",
        persona_id,
        "--messages-file",
        str(msg_path),
        "--workflow-run-id",
        session_id,
        "--step-id",
        script.stem.replace("_", "-"),
        "--json",
        "--data-dir",
        str(DATA_DIR),
        "--out-dir",
        str(SIMULATION_DIR),
    ]
    env = os.environ.copy()
    mock = os.environ.get("MOCK_LLM_RESPONSE")
    if mock:
        env["MOCK_LLM_RESPONSE"] = mock
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    stdout = (completed.stdout or "").strip()
    if not stdout:
        return (
            {
                "status": "error",
                "next_action": None,
                "confidence": None,
                "review_required": False,
                "artifact_refs": [],
                "outputs": {},
                "error": {
                    "code": "no_output",
                    "message": (completed.stderr or "").strip() or "simulation skill produced no output",
                },
            },
            session_id,
        )
    try:
        return json.loads(stdout.splitlines()[-1]), session_id
    except json.JSONDecodeError as exc:
        return (
            {
                "status": "error",
                "next_action": None,
                "confidence": None,
                "review_required": False,
                "artifact_refs": [],
                "outputs": {},
                "error": {"code": "invalid_envelope", "message": str(exc)},
            },
            session_id,
        )


def _read_simulation_artifact(session_id: str, artifact_refs: list[str]) -> str | None:
    if not artifact_refs:
        return None
    path = SIMULATION_DIR / session_id / artifact_refs[0]
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


@app.get("/simulation/personas")
def list_personas() -> list[dict[str, Any]]:
    if not SIM_PERSONAS_PATH.exists():
        raise HTTPException(status_code=500, detail=f"{SIM_PERSONAS_PATH} not found")
    return json.loads(SIM_PERSONAS_PATH.read_text(encoding="utf-8"))


@app.post("/simulation/turn")
def simulation_turn(req: SimulationTurnRequest) -> dict[str, Any]:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages must include at least one turn")
    envelope, _session_id = _run_simulation_skill(
        SIMULATE_COLD_CALL_SCRIPT,
        persona_id=req.persona_id,
        messages=req.messages,
    )
    return envelope


@app.post("/simulation/debrief")
def simulation_debrief(req: SimulationDebriefRequest) -> dict[str, Any]:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages must include at least one turn")
    envelope, session_id = _run_simulation_skill(
        DEBRIEF_COLD_CALL_SCRIPT,
        persona_id=req.persona_id,
        messages=req.messages,
    )
    artifact_content = _read_simulation_artifact(session_id, envelope.get("artifact_refs") or [])
    # Log the debrief decision-free for the dashboard so simulation activity is
    # visible (no manager approval flow on simulations — trainee runs alone).
    if envelope.get("status") != "error":
        _append_decision(
            {
                "timestamp": _now(),
                "feature": "simulation",
                "action": "approve",
                "context": {
                    "session_id": session_id,
                    "persona_id": req.persona_id,
                    "weighted_total": envelope.get("outputs", {}).get("weighted_total"),
                    "n_turns": envelope.get("outputs", {}).get("n_turns"),
                },
            }
        )
    return {
        "session_id": session_id,
        "persona_id": req.persona_id,
        "envelope": envelope,
        "artifact_content": artifact_content,
    }


@app.on_event("startup")
def _startup_index_new_kb_docs() -> None:
    """Idempotently index any new KB docs into the Tutor's ChromaDB collection.
    Catches new files like certification_rubric.md without losing existing
    approved_qa chunks. Failures are non-fatal — the server still boots."""
    CERTIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    try:
        from rag.embeddings_retrieval import index_new_docs

        added = index_new_docs()
        if added:
            print(f"[startup] indexed {added} new KB chunks into ChromaDB", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[startup] ChromaDB index_new_docs skipped: {exc}", flush=True)


if __name__ == "__main__":
    uvicorn.run("workflow_server:app", port=8000, reload=True)
