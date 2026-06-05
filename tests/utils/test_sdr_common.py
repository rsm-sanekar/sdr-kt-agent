"""Tests for utils.sdr_common."""

from __future__ import annotations

import argparse
import json

import pytest

from utils.sdr_common import (
    ENVELOPE_KEYS,
    emit_envelope,
    emit_error,
    ensure_run_dir,
    existing_envelope_for,
    make_envelope,
    make_skill_parser,
    needs_human_review,
    run_step,
    write_envelope,
)

# ---------- make_skill_parser ----------


def test_parser_defaults():
    parser = make_skill_parser("desc")
    args = parser.parse_args([])
    assert args.hire_id is None
    assert args.data_dir == "data"
    assert args.out_dir == "data/working"
    assert args.workflow_run_id is None
    assert args.step_id is None
    assert args.mode == "normal"
    assert args.idempotency_mode == "skip"
    assert args.json is False


def test_parser_accepts_all_flags():
    parser = make_skill_parser("desc")
    args = parser.parse_args(
        [
            "--hire-id",
            "HIRE-1",
            "--data-dir",
            "d",
            "--out-dir",
            "o",
            "--workflow-run-id",
            "wf-1",
            "--step-id",
            "step-1",
            "--mode",
            "demo",
            "--idempotency-mode",
            "replace",
            "--json",
        ]
    )
    assert args.hire_id == "HIRE-1"
    assert args.data_dir == "d"
    assert args.out_dir == "o"
    assert args.workflow_run_id == "wf-1"
    assert args.step_id == "step-1"
    assert args.mode == "demo"
    assert args.idempotency_mode == "replace"
    assert args.json is True


def test_parser_rejects_bad_mode():
    parser = make_skill_parser("desc")
    with pytest.raises(SystemExit):
        parser.parse_args(["--mode", "bogus"])


def test_parser_rejects_bad_idempotency_mode():
    parser = make_skill_parser("desc")
    with pytest.raises(SystemExit):
        parser.parse_args(["--idempotency-mode", "bogus"])


# ---------- make_envelope ----------


def test_envelope_has_all_seven_keys_with_defaults():
    env = make_envelope(status="ok")
    assert set(env.keys()) == set(ENVELOPE_KEYS)
    assert env["status"] == "ok"
    assert env["next_action"] is None
    assert env["confidence"] is None
    assert env["review_required"] is False
    assert env["artifact_refs"] == []
    assert env["outputs"] == {}
    assert env["error"] is None


def test_envelope_with_all_fields_populated():
    env = make_envelope(
        status="needs_review",
        next_action="draft-email",
        confidence=0.42,
        review_required=True,
        artifact_refs=["working/x.csv"],
        outputs={"score": 0.42},
        error=None,
    )
    assert env["status"] == "needs_review"
    assert env["next_action"] == "draft-email"
    assert env["confidence"] == 0.42
    assert env["review_required"] is True
    assert env["artifact_refs"] == ["working/x.csv"]
    assert env["outputs"] == {"score": 0.42}


def test_envelope_rejects_invalid_status():
    with pytest.raises(ValueError):
        make_envelope(status="bogus")


def test_envelope_copies_mutable_inputs():
    refs = ["a.csv"]
    outs = {"k": 1}
    env = make_envelope(status="ok", artifact_refs=refs, outputs=outs)
    refs.append("b.csv")
    outs["k"] = 2
    assert env["artifact_refs"] == ["a.csv"]
    assert env["outputs"] == {"k": 1}


# ---------- emit_envelope ----------


def test_emit_envelope_prints_json_and_returns_zero(capsys):
    env = make_envelope(status="ok", next_action="done")
    rc = emit_envelope(env)
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed == env


def test_emit_envelope_error_returns_one(capsys):
    env = make_envelope(status="error", error={"code": "x", "message": "y"})
    rc = emit_envelope(env)
    assert rc == 1
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_emit_envelope_silent_when_as_json_false(capsys):
    env = make_envelope(status="ok")
    rc = emit_envelope(env, as_json=False)
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_emit_envelope_validates_missing_keys():
    incomplete = {"status": "ok"}
    with pytest.raises(ValueError):
        emit_envelope(incomplete)


# ---------- emit_error ----------


def test_emit_error_returns_one_and_prints_error_envelope(capsys):
    rc = emit_error("bad_input", "missing hire id")
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "error"
    assert parsed["error"] == {"code": "bad_input", "message": "missing hire id"}
    assert set(parsed.keys()) == set(ENVELOPE_KEYS)


# ---------- ensure_run_dir ----------


def test_ensure_run_dir_with_run_id(tmp_path):
    p = ensure_run_dir(tmp_path, "wf-1")
    assert p == tmp_path / "wf-1"
    assert p.is_dir()


def test_ensure_run_dir_without_run_id(tmp_path):
    p = ensure_run_dir(tmp_path / "out", None)
    assert p == tmp_path / "out"
    assert p.is_dir()


def test_ensure_run_dir_is_idempotent(tmp_path):
    p1 = ensure_run_dir(tmp_path, "wf-1")
    p2 = ensure_run_dir(tmp_path, "wf-1")
    assert p1 == p2
    assert p1.is_dir()


# ---------- write_envelope + existing_envelope_for ----------


def test_existing_envelope_returns_none_when_missing(tmp_path):
    assert existing_envelope_for(tmp_path, "step-1") is None


def test_write_then_read_envelope_roundtrip(tmp_path):
    env = make_envelope(status="ok", outputs={"k": "v"})
    write_envelope(tmp_path, "step-1", env)
    assert (tmp_path / "step-1.envelope.json").exists()
    read_back = existing_envelope_for(tmp_path, "step-1")
    assert read_back == env


# ---------- needs_human_review ----------


def test_needs_review_below_threshold():
    assert needs_human_review(0.4) is True


def test_needs_review_above_threshold():
    assert needs_human_review(0.9) is False


def test_needs_review_at_threshold_is_false():
    assert needs_human_review(0.60) is False


def test_needs_review_none_confidence_is_true():
    assert needs_human_review(None) is True


def test_needs_review_custom_threshold():
    assert needs_human_review(0.7, threshold=0.8) is True
    assert needs_human_review(0.9, threshold=0.8) is False


# ---------- run_step ----------


def _args(**overrides) -> argparse.Namespace:
    base = dict(
        hire_id="HIRE-1",
        data_dir="data",
        out_dir="out",
        workflow_run_id="wf-1",
        step_id="step-1",
        mode="normal",
        idempotency_mode="skip",
        json=True,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


def test_run_step_happy_path_writes_envelope_and_prints(tmp_path, capsys):
    args = _args(out_dir=str(tmp_path))

    def do_work(a):
        return make_envelope(status="ok", next_action="next-skill", confidence=0.9)

    rc = run_step(args, do_work)
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["next_action"] == "next-skill"
    assert (tmp_path / "wf-1" / "step-1.envelope.json").exists()


def test_run_step_skip_idempotency_returns_prior(tmp_path, capsys):
    args = _args(out_dir=str(tmp_path))
    run_dir = ensure_run_dir(tmp_path, "wf-1")
    prior = make_envelope(status="ok", next_action="cached")
    write_envelope(run_dir, "step-1", prior)

    called = {"n": 0}

    def do_work(a):
        called["n"] += 1
        return make_envelope(status="ok", next_action="fresh")

    rc = run_step(args, do_work)
    assert rc == 0
    assert called["n"] == 0  # skipped
    assert json.loads(capsys.readouterr().out)["next_action"] == "cached"


def test_run_step_replace_idempotency_overwrites(tmp_path, capsys):
    args = _args(out_dir=str(tmp_path), idempotency_mode="replace")
    run_dir = ensure_run_dir(tmp_path, "wf-1")
    write_envelope(run_dir, "step-1", make_envelope(status="ok", next_action="old"))

    def do_work(a):
        return make_envelope(status="ok", next_action="new")

    rc = run_step(args, do_work)
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["next_action"] == "new"
    on_disk = existing_envelope_for(run_dir, "step-1")
    assert on_disk["next_action"] == "new"


def test_run_step_catches_exception_and_emits_error(tmp_path, capsys):
    args = _args(out_dir=str(tmp_path))

    def do_work(a):
        raise RuntimeError("boom")

    rc = run_step(args, do_work)
    assert rc == 1
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["status"] == "error"
    assert parsed["error"]["code"] == "unhandled_exception"
    assert "boom" in parsed["error"]["message"]


def test_run_step_error_envelope_returns_one(tmp_path, capsys):
    args = _args(out_dir=str(tmp_path))

    def do_work(a):
        return make_envelope(status="error", error={"code": "x", "message": "y"})

    rc = run_step(args, do_work)
    assert rc == 1
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_run_step_without_step_id_does_not_write_file(tmp_path, capsys):
    args = _args(out_dir=str(tmp_path), step_id=None, workflow_run_id=None)

    def do_work(a):
        return make_envelope(status="ok", next_action="done")

    rc = run_step(args, do_work)
    assert rc == 0
    # No envelope file should exist anywhere under tmp_path
    assert list(tmp_path.rglob("*.envelope.json")) == []
    assert json.loads(capsys.readouterr().out)["next_action"] == "done"


def test_run_step_respects_as_json_false(tmp_path, capsys):
    args = _args(out_dir=str(tmp_path), json=False)

    def do_work(a):
        return make_envelope(status="ok", next_action="done")

    rc = run_step(args, do_work)
    assert rc == 0
    assert capsys.readouterr().out == ""
