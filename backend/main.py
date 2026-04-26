from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import mock_data  # always available — no external dependencies
from embeddings import add_qa_pair, add_coaching_note, add_handoff_doc, _get_collection
from prompts import (
    PREBOARDING_SYSTEM,
    PREBOARDING_USER,
    OFFBOARDING_SYSTEM,
    OFFBOARDING_USER,
    COACHING_SYSTEM,
    COACHING_USER,
)
from rag import answer_question, log_gap, _GAP_TRACKER_PATH
import whisper as whisper_module

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ─── Toggle ──────────────────────────────────────────────────────────────────
# Set MOCK_MODE = True to run without API keys or ChromaDB (hardcoded responses).
# Set MOCK_MODE = False to use real claude-sonnet-4-6 + ChromaDB.
MOCK_MODE = True
# ─────────────────────────────────────────────────────────────────────────────


app = FastAPI(
    title="SDR KT Onboarding Agent",
    description="AI-powered onboarding for Salesforce SDRs — MGT 449 class project",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Anthropic client (lazy) ──────────────────────────────────────────────────

_anthropic: anthropic.Anthropic | None = None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic
    if _anthropic is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set — check .env")
        _anthropic = anthropic.Anthropic(api_key=key)
    return _anthropic


def _call_claude(
    system: str,
    user: str,
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> anthropic.types.Message:
    return _get_anthropic().messages.create(
        model="claude-sonnet-4-6",
        system=system,
        messages=[{"role": "user", "content": user}],
        max_tokens=max_tokens,
        temperature=temperature,
    )


def _parse_json(text: str) -> dict | list:
    """Strip markdown fences if Claude wraps JSON despite instructions."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": MOCK_MODE}


# ─────────────────────────────────────────────────────────────────────────────
# Feature 1 — AI Tutor  (onboarding Step 4)
# ─────────────────────────────────────────────────────────────────────────────


class TutorAskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


class TutorAskResponse(BaseModel):
    answer: str
    sources: list[dict]
    confidence_score: float
    flagged: bool
    model: str
    token_count: int
    generation_time: float
    pair_id: str


class TutorApproveRequest(BaseModel):
    question: str = Field(..., min_length=3)
    answer: str = Field(..., min_length=1)
    pair_id: str
    was_edited: bool = False


class TutorApproveResponse(BaseModel):
    status: str
    pair_id: str
    was_edited: bool


@app.post("/tutor/ask", response_model=TutorAskResponse)
def tutor_ask(req: TutorAskRequest):
    """
    Core AI Tutor: retrieve relevant KB chunks, generate cited answer.
    Low-confidence answers (score < 0.4) are flagged and logged to gap_tracker.json.
    In MOCK_MODE, keyword-matches the question against hardcoded Q&A pairs.
    """
    if MOCK_MODE:
        time.sleep(0.9)
        pair = mock_data.match_tutor_question(req.question)
        return TutorAskResponse(
            answer=pair["answer"],
            sources=pair["sources"],
            confidence_score=pair["confidence_score"],
            flagged=pair["confidence_score"] < 0.4,
            model="mock",
            token_count=pair["token_count"],
            generation_time=0.9,
            pair_id=str(uuid.uuid4()),
        )

    try:
        start = time.perf_counter()
        result = answer_question(req.question)
        elapsed = round(time.perf_counter() - start, 3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {e}")

    if result["flagged"]:
        try:
            log_gap(req.question)
        except Exception:
            pass

    return TutorAskResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence_score=result["confidence_score"],
        flagged=result["flagged"],
        model=result["model"],
        token_count=result["token_count"],
        generation_time=elapsed,
        pair_id=str(uuid.uuid4()),
    )


@app.post("/tutor/approve", response_model=TutorApproveResponse)
def tutor_approve(req: TutorApproveRequest):
    """
    Human checkpoint: stores the approved Q&A pair in ChromaDB.
    Edited answers are stored with source='edited_qa' for academic tracking.
    """
    if MOCK_MODE:
        return TutorApproveResponse(
            status="stored_mock",
            pair_id=req.pair_id,
            was_edited=req.was_edited,
        )

    source = "approved_qa" if not req.was_edited else "edited_qa"
    try:
        add_qa_pair(
            question=req.question,
            answer=req.answer,
            pair_id=req.pair_id,
            source=source,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KB write error: {e}")

    return TutorApproveResponse(
        status="stored",
        pair_id=req.pair_id,
        was_edited=req.was_edited,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Feature 2 — Pre-boarding Plan Generator  (Step 1)
# ─────────────────────────────────────────────────────────────────────────────


class PreboardingGenerateRequest(BaseModel):
    sdr_name: str = Field(..., min_length=1)
    territory: str = Field(..., min_length=1)
    vertical: str = Field(..., min_length=1)
    experience_level: str = Field(..., pattern="^(entry|mid|senior)$")
    notes: str = Field("", description="Optional manager notes for personalisation")


class PreboardingApproveRequest(BaseModel):
    plan_id: str
    sdr_name: str
    approved_plan: Any
    was_edited: bool = False
    manager_name: str = ""


@app.post("/preboarding/generate")
def preboarding_generate(req: PreboardingGenerateRequest):
    """
    Generate a personalised Trailhead learning path for a new SDR.
    Calls claude-sonnet-4-6 with PREBOARDING_SYSTEM + PREBOARDING_USER.
    """
    if MOCK_MODE:
        time.sleep(1.1)
        plan = mock_data.get_preboarding_plan(req.vertical, req.experience_level)
        return {
            "plan_id": str(uuid.uuid4()),
            "sdr_name": req.sdr_name,
            "model": "mock",
            "generation_time": 1.1,
            "token_count": 520,
            **{k: v for k, v in plan.items() if k != "id"},
        }

    user_msg = PREBOARDING_USER.format(
        sdr_name=req.sdr_name,
        territory=req.territory,
        vertical=req.vertical,
        experience_level=req.experience_level,
        notes=req.notes or "None provided",
    )
    try:
        start = time.perf_counter()
        resp = _call_claude(
            PREBOARDING_SYSTEM, user_msg, max_tokens=2048, temperature=0.4
        )
        elapsed = round(time.perf_counter() - start, 3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude error: {e}")

    try:
        plan = _parse_json(resp.content[0].text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON parse error: {e} | Raw: {resp.content[0].text[:300]}",
        )

    return {
        "plan_id": str(uuid.uuid4()),
        "sdr_name": req.sdr_name,
        "model": "claude-sonnet-4-6",
        "generation_time": elapsed,
        "token_count": resp.usage.input_tokens + resp.usage.output_tokens,
        **plan,
    }


@app.post("/preboarding/approve")
def preboarding_approve(req: PreboardingApproveRequest):
    """
    Human checkpoint: manager approves/edits plan before it is sent to the SDR.
    Approval metadata is tracked for the self-improving KB.
    """
    if MOCK_MODE:
        return {
            "status": "approved_mock",
            "plan_id": req.plan_id,
            "was_edited": req.was_edited,
            "message": f"Plan for {req.sdr_name} approved{' with edits' if req.was_edited else ''} by {req.manager_name or 'manager'}.",
        }

    plan_text = (
        req.approved_plan
        if isinstance(req.approved_plan, str)
        else json.dumps(req.approved_plan)
    )
    try:
        from embeddings import add_documents

        add_documents(
            texts=[plan_text],
            ids=[req.plan_id],
            source="approved_plan" if not req.was_edited else "edited_plan",
            doc_type="preboarding_plan",
            extra_metadata={"sdr_name": req.sdr_name, "manager": req.manager_name},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KB write error: {e}")

    return {
        "status": "approved",
        "plan_id": req.plan_id,
        "was_edited": req.was_edited,
        "message": f"Plan for {req.sdr_name} approved{' with edits' if req.was_edited else ''} by {req.manager_name or 'manager'}.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Feature 3 — Offboarding KT  (knowledge-loop closer)
# ─────────────────────────────────────────────────────────────────────────────


class OffboardingGenerateRequest(BaseModel):
    departing_rep_name: str = Field(..., min_length=1)
    territory: str = Field(..., min_length=1)
    tenure_months: int = Field(..., ge=1)
    interview_answers: dict = Field(
        default_factory=dict,
        description="Key: question slug, Value: departing rep's answer",
    )


class OffboardingApproveRequest(BaseModel):
    doc_id: str
    departing_rep_name: str
    approved_content: Any
    was_edited: bool = False
    manager_approved: bool = False


@app.post("/offboarding/generate")
def offboarding_generate(req: OffboardingGenerateRequest):
    """
    Synthesise interview answers into a structured handoff document.
    Calls claude-sonnet-4-6 with OFFBOARDING_SYSTEM + OFFBOARDING_USER.
    """
    if MOCK_MODE:
        time.sleep(1.3)
        t = req.territory.lower()
        doc = (
            mock_data.MOCK_HANDOFF_DOCS[1]
            if "health" in t
            else mock_data.MOCK_HANDOFF_DOCS[0]
        )
        return {
            "doc_id": str(uuid.uuid4()),
            "model": "mock",
            "generation_time": 1.3,
            "token_count": 680,
            **{
                k: v
                for k, v in doc.items()
                if k not in ("id", "approved", "approval_status")
            },
        }

    answers_text = "\n".join(f"{k}: {v}" for k, v in req.interview_answers.items())
    user_msg = OFFBOARDING_USER.format(
        rep_name=req.departing_rep_name,
        territory=req.territory,
        tenure_months=req.tenure_months,
        answers=answers_text,
    )
    try:
        start = time.perf_counter()
        resp = _call_claude(
            OFFBOARDING_SYSTEM, user_msg, max_tokens=2048, temperature=0.3
        )
        elapsed = round(time.perf_counter() - start, 3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude error: {e}")

    try:
        doc = _parse_json(resp.content[0].text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON parse error: {e} | Raw: {resp.content[0].text[:300]}",
        )

    return {
        "doc_id": str(uuid.uuid4()),
        "model": "claude-sonnet-4-6",
        "generation_time": elapsed,
        "token_count": resp.usage.input_tokens + resp.usage.output_tokens,
        **doc,
    }


@app.post("/offboarding/approve")
def offboarding_approve(req: OffboardingApproveRequest):
    """
    Dual-approval checkpoint: both departing rep and manager must approve.
    Approved docs are written to ChromaDB so future SDRs can retrieve them.
    """
    if MOCK_MODE:
        return {
            "status": "approved_mock",
            "doc_id": req.doc_id,
            "was_edited": req.was_edited,
            "manager_approved": req.manager_approved,
            "message": "Handoff document approved. In production this writes to ChromaDB.",
        }

    content_text = (
        req.approved_content
        if isinstance(req.approved_content, str)
        else json.dumps(req.approved_content)
    )
    try:
        add_handoff_doc(
            content=content_text,
            doc_id=req.doc_id,
            departing_rep=req.departing_rep_name,
            territory="",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KB write error: {e}")

    return {
        "status": "approved",
        "doc_id": req.doc_id,
        "was_edited": req.was_edited,
        "manager_approved": req.manager_approved,
        "message": "Handoff document stored in KB.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Feature 4 — Coaching Notes  (Step 10)
# ─────────────────────────────────────────────────────────────────────────────


class CoachingGenerateRequest(BaseModel):
    sdr_name: str = Field(..., min_length=1)
    transcript: str = Field(
        "", description="Call transcript text (from Whisper or manual paste)"
    )
    audio_file_path: str = Field(
        "", description="Path to audio file if Whisper transcription needed"
    )
    call_context: str = Field("", description="Optional manager context about the call")


class CoachingApproveRequest(BaseModel):
    note_id: str
    sdr_name: str
    approved_note: Any
    was_edited: bool = False
    manager_name: str = ""
    is_zero_edit: bool = False


@app.post("/coaching/generate")
def coaching_generate(req: CoachingGenerateRequest):
    """
    Generate a structured coaching note from a call transcript.
    If audio_file_path is provided, Whisper transcribes it first.
    Uses claude-sonnet-4-6 with the COACHING_SYSTEM rubric.
    Zero-edit approvals are stored as gold standard examples in the KB.
    """
    if MOCK_MODE:
        time.sleep(1.0)
        length = len(req.transcript)
        quality = "strong" if length > 800 else "weak" if length < 200 else "average"
        note = mock_data.get_coaching_note(quality)
        return {
            "note_id": str(uuid.uuid4()),
            "model": "mock",
            "generation_time": 1.0,
            "token_count": 410,
            **{
                k: v
                for k, v in note.items()
                if k not in ("id", "approved", "zero_edit_candidate")
            },
            "is_zero_edit_candidate": note["zero_edit_candidate"],
        }

    # Resolve transcript: prefer pasted text, fall back to Whisper transcription.
    transcript_text = req.transcript
    if not transcript_text.strip() and req.audio_file_path:
        try:
            transcript_text = whisper_module.transcribe(req.audio_file_path)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Whisper transcription error: {e}"
            )

    if not transcript_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Provide a transcript (paste or audio_file_path).",
        )

    user_msg = COACHING_USER.format(
        sdr_name=req.sdr_name,
        transcript=transcript_text,
        call_context=req.call_context or "No additional context provided.",
    )
    try:
        start = time.perf_counter()
        resp = _call_claude(COACHING_SYSTEM, user_msg, max_tokens=1024, temperature=0.2)
        elapsed = round(time.perf_counter() - start, 3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude error: {e}")

    try:
        note = _parse_json(resp.content[0].text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON parse error: {e} | Raw: {resp.content[0].text[:300]}",
        )

    # Score >= 80 with no requested edits qualifies as a gold-standard example.
    is_zero_edit_candidate = note.get("overall_score", 0) >= 80

    return {
        "note_id": str(uuid.uuid4()),
        "model": "claude-sonnet-4-6",
        "generation_time": elapsed,
        "token_count": resp.usage.input_tokens + resp.usage.output_tokens,
        **note,
        "is_zero_edit_candidate": is_zero_edit_candidate,
    }


@app.post("/coaching/approve")
def coaching_approve(req: CoachingApproveRequest):
    """
    Manager approval checkpoint. Zero-edit approvals are stored as gold-standard
    examples in ChromaDB — used to improve future coaching prompts.
    """
    if MOCK_MODE:
        return {
            "status": "approved_mock",
            "note_id": req.note_id,
            "was_edited": req.was_edited,
            "stored_as_gold_standard": req.is_zero_edit,
            "message": (
                "Stored as gold standard example."
                if req.is_zero_edit
                else "Approved with edits. Not stored as gold standard."
            ),
        }

    note_text = (
        req.approved_note
        if isinstance(req.approved_note, str)
        else json.dumps(req.approved_note)
    )
    try:
        add_coaching_note(
            note=note_text,
            note_id=req.note_id,
            coach=req.manager_name or "unknown",
            topic=f"coaching:{req.sdr_name}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KB write error: {e}")

    return {
        "status": "approved",
        "note_id": req.note_id,
        "was_edited": req.was_edited,
        "stored_as_gold_standard": req.is_zero_edit,
        "message": (
            "Stored as gold standard example."
            if req.is_zero_edit
            else "Approved with edits. Not stored as gold standard."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard metrics
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/dashboard/metrics")
def dashboard_metrics():
    """
    KB health metrics for the dashboard page.
    In MOCK_MODE, returns hardcoded demo metrics.
    In real mode, queries ChromaDB for live chunk counts and reads gap_tracker.json.
    """
    if MOCK_MODE:
        return {
            "mock_mode": True,
            "total_interactions": 234,
            "kb_health": {
                "total_chunks": 1847,
                "approval_rate": 79,
                "edit_rate": 22,
                "approved_qa_chunks": 89,
                "coaching_gold_chunks": 19,
                "handoff_chunks": 38,
                "raw_doc_chunks": 1701,
            },
            "weekly_interactions": [
                {"week": "Mon", "count": 28},
                {"week": "Tue", "count": 34},
                {"week": "Wed", "count": 31},
                {"week": "Thu", "count": 42},
                {"week": "Fri", "count": 38},
                {"week": "Sat", "count": 12},
                {"week": "Sun", "count": 9},
            ],
            "feature_breakdown": {
                "AI Tutor": 142,
                "Pre-boarding": 31,
                "Offboarding": 7,
                "Coaching": 54,
            },
            "recent_approvals": [
                {
                    "type": "AI Tutor",
                    "description": "What is the MEDDIC framework?",
                    "status": "approved",
                },
                {
                    "type": "Coaching Note",
                    "description": "Taylor Nguyen — Fintech VP discovery call",
                    "status": "approved",
                },
                {
                    "type": "Pre-boarding",
                    "description": "Alex Johnson — Manufacturing / Entry level",
                    "status": "edited",
                },
                {
                    "type": "AI Tutor",
                    "description": "How do I handle the 'send me an email' objection?",
                    "status": "approved",
                },
                {
                    "type": "Offboarding",
                    "description": "Jordan Lee — AMER West Mid-Market Tech handoff",
                    "status": "approved",
                },
                {
                    "type": "Coaching Note",
                    "description": "Casey Park — Manufacturing Director cold call",
                    "status": "rejected",
                },
                {
                    "type": "AI Tutor",
                    "description": "Champion vs economic buyer — what's the difference?",
                    "status": "edited",
                },
                {
                    "type": "Pre-boarding",
                    "description": "Sam Rivera — Healthcare / Mid level",
                    "status": "approved",
                },
            ],
            "baseline_vs_target": [
                {
                    "metric": "Time to Certification",
                    "baseline": "6 wks",
                    "target": "4 wks",
                    "current": "4.8 wks",
                    "progress": 60,
                },
                {
                    "metric": "Feedback Latency",
                    "baseline": "48 hrs",
                    "target": "4 hrs",
                    "current": "3.2 hrs",
                    "progress": 100,
                },
                {
                    "metric": "Manager Review Time",
                    "baseline": "4 hrs/wk",
                    "target": "1 hr/wk",
                    "current": "1.4 hrs/wk",
                    "progress": 87,
                },
                {
                    "metric": "Content Update Lag",
                    "baseline": "168 hrs",
                    "target": "24 hrs",
                    "current": "18 hrs",
                    "progress": 100,
                },
            ],
            "tutor": {
                "total_questions": 142,
                "approved_qa_pairs": 89,
                "edited_qa_pairs": 23,
                "rejected": 8,
                "flagged_gaps": 22,
            },
            "preboarding": {
                "plans_generated": 31,
                "plans_approved": 28,
                "plans_edited": 11,
            },
            "offboarding": {
                "handoffs_generated": 7,
                "handoffs_dual_approved": 6,
                "handoffs_edited": 4,
                "kb_chunks_added": 38,
            },
            "coaching": {
                "notes_generated": 54,
                "notes_approved": 47,
                "zero_edit_approvals": 19,
                "gold_standard_in_kb": 19,
                "avg_score": 67,
            },
        }

    # Real mode: pull live counts from ChromaDB and gap_tracker.json.
    try:
        coll = _get_collection()
        total_chunks = coll.count()
        all_meta = coll.get(include=["metadatas"])["metadatas"] or []
        types = [m.get("type", "unknown") for m in all_meta]
        qa_chunks = types.count("qa_pair")
        coaching_chunks = types.count("coaching_note")
        handoff_chunks = types.count("handoff_doc")
        raw_chunks = total_chunks - qa_chunks - coaching_chunks - handoff_chunks
    except Exception:
        total_chunks = qa_chunks = coaching_chunks = handoff_chunks = raw_chunks = 0

    open_gaps = 0
    try:
        with open(_GAP_TRACKER_PATH) as f:
            open_gaps = len(json.load(f))
    except Exception:
        pass

    return {
        "mock_mode": False,
        "total_interactions": 0,
        "open_gaps": open_gaps,
        "kb_health": {
            "total_chunks": total_chunks,
            "approval_rate": 0,
            "edit_rate": 0,
            "approved_qa_chunks": qa_chunks,
            "coaching_gold_chunks": coaching_chunks,
            "handoff_chunks": handoff_chunks,
            "raw_doc_chunks": raw_chunks,
        },
        "weekly_interactions": [
            {"week": d, "count": 0}
            for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ],
        "feature_breakdown": {
            "AI Tutor": 0,
            "Pre-boarding": 0,
            "Offboarding": 0,
            "Coaching": 0,
        },
        "recent_approvals": [],
        "baseline_vs_target": [
            {
                "metric": "Time to Certification",
                "baseline": "6 wks",
                "target": "4 wks",
                "current": "—",
                "progress": 0,
            },
            {
                "metric": "Feedback Latency",
                "baseline": "48 hrs",
                "target": "4 hrs",
                "current": "—",
                "progress": 0,
            },
            {
                "metric": "Manager Review Time",
                "baseline": "4 hrs/wk",
                "target": "1 hr/wk",
                "current": "—",
                "progress": 0,
            },
            {
                "metric": "Content Update Lag",
                "baseline": "168 hrs",
                "target": "24 hrs",
                "current": "—",
                "progress": 0,
            },
        ],
    }
