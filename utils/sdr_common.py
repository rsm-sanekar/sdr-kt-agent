"""Shared CLI parser, JSON envelope, and step-runner helpers for SDR skills/automations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

ENVELOPE_KEYS = (
    "status",
    "next_action",
    "confidence",
    "review_required",
    "artifact_refs",
    "outputs",
    "error",
)

VALID_STATUSES = {"ok", "error", "needs_review"}


def make_skill_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--hire-id")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--out-dir", default="data/working")
    parser.add_argument("--workflow-run-id")
    parser.add_argument("--step-id")
    parser.add_argument("--mode", choices=["normal", "demo"], default="normal")
    parser.add_argument("--idempotency-mode", choices=["skip", "replace"], default="skip")
    parser.add_argument("--json", action="store_true")
    return parser


def make_envelope(
    *,
    status: str,
    next_action: str | None = None,
    confidence: float | None = None,
    review_required: bool = False,
    artifact_refs: list[str] | None = None,
    outputs: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}, got {status!r}")
    return {
        "status": status,
        "next_action": next_action,
        "confidence": confidence,
        "review_required": review_required,
        "artifact_refs": list(artifact_refs) if artifact_refs is not None else [],
        "outputs": dict(outputs) if outputs is not None else {},
        "error": error,
    }


def emit_envelope(envelope: dict[str, Any], *, as_json: bool = True) -> int:
    missing = [k for k in ENVELOPE_KEYS if k not in envelope]
    if missing:
        raise ValueError(f"envelope missing required keys: {missing}")
    if as_json:
        print(json.dumps(envelope))
    return 1 if envelope["status"] == "error" else 0


def emit_error(code: str, message: str) -> int:
    envelope = make_envelope(
        status="error",
        error={"code": code, "message": message},
    )
    return emit_envelope(envelope)


def ensure_run_dir(out_dir: str | Path, workflow_run_id: str | None) -> Path:
    base = Path(out_dir)
    run_dir = base / workflow_run_id if workflow_run_id else base
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def existing_envelope_for(run_dir: str | Path, step_id: str) -> dict[str, Any] | None:
    path = Path(run_dir) / f"{step_id}.envelope.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def write_envelope(run_dir: str | Path, step_id: str, envelope: dict[str, Any]) -> None:
    path = Path(run_dir) / f"{step_id}.envelope.json"
    path.write_text(json.dumps(envelope, indent=2))


def needs_human_review(confidence: float | None, threshold: float = 0.60) -> bool:
    if confidence is None:
        return True
    return confidence < threshold


def run_step(
    args: argparse.Namespace,
    do_work: Callable[[argparse.Namespace], dict[str, Any]],
) -> int:
    run_dir = ensure_run_dir(args.out_dir, args.workflow_run_id)
    step_id = args.step_id

    if step_id and args.idempotency_mode == "skip":
        prior = existing_envelope_for(run_dir, step_id)
        if prior is not None:
            return emit_envelope(prior, as_json=args.json)

    try:
        envelope = do_work(args)
    except Exception as exc:  # noqa: BLE001
        return emit_error("unhandled_exception", str(exc))

    if step_id:
        write_envelope(run_dir, step_id, envelope)
    return emit_envelope(envelope, as_json=args.json)
