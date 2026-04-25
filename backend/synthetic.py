from __future__ import annotations

import json
import os
import random
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from prompts import (
    SYNTHETIC_AE_SYSTEM,
    SYNTHETIC_AE_USER,
    SYNTHETIC_SDR_SYSTEM,
    SYNTHETIC_SDR_USER,
    SYNTHETIC_TRANSCRIPT_SYSTEM,
    SYNTHETIC_TRANSCRIPT_USER,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_client: anthropic.Anthropic | None = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set — check .env")
        _client = anthropic.Anthropic(api_key=key)
    return _client


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SYNTHETIC_DIR = os.path.join(_PROJECT_ROOT, "data", "synthetic")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _claude(system: str, user: str) -> str:
    """Single claude-sonnet-4-6 call. Returns the raw text content of the response."""
    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        system=system,
        messages=[{"role": "user", "content": user}],
        max_tokens=4096,
        temperature=0.9,  # high temp for varied synthetic data
    )
    return response.content[0].text.strip()


def _parse_json(raw: str) -> list | dict:
    """
    Strip markdown fences if present and parse JSON.
    Claude sometimes wraps JSON in ```json ... ``` despite being told not to.
    """
    text = raw
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def _save(data: list | dict, filename: str) -> str:
    """Save synthetic data to data/synthetic/<filename>.json and return the path."""
    os.makedirs(_SYNTHETIC_DIR, exist_ok=True)
    path = os.path.join(_SYNTHETIC_DIR, filename if filename.endswith(".json") else filename + ".json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


# ---------------------------------------------------------------------------
# Public generators
# ---------------------------------------------------------------------------

def generate_sdr_profiles(n: int = 30) -> list[dict]:
    """
    Generate n synthetic SDR profiles calibrated against Bridge Group benchmarks.
    Generates in batches of 10 to keep responses clean and parseable.
    Saves to data/synthetic/sdr_profiles.json and returns the list.
    """
    profiles: list[dict] = []
    batch_size = 10

    for start in range(0, n, batch_size):
        count = min(batch_size, n - start)
        raw = _claude(
            system=SYNTHETIC_SDR_SYSTEM,
            user=SYNTHETIC_SDR_USER.format(n=count),
        )
        batch = _parse_json(raw)
        if isinstance(batch, list):
            profiles.extend(batch)
        else:
            profiles.append(batch)

    profiles = profiles[:n]
    _save(profiles, "sdr_profiles")
    print(f"Generated {len(profiles)} SDR profiles → data/synthetic/sdr_profiles.json")
    return profiles


def generate_ae_profiles(n: int = 20) -> list[dict]:
    """
    Generate n synthetic AE profiles for the Trail Guide matching feature.
    Saves to data/synthetic/ae_profiles.json and returns the list.
    """
    profiles: list[dict] = []
    batch_size = 10

    for start in range(0, n, batch_size):
        count = min(batch_size, n - start)
        raw = _claude(
            system=SYNTHETIC_AE_SYSTEM,
            user=SYNTHETIC_AE_USER.format(n=count),
        )
        batch = _parse_json(raw)
        if isinstance(batch, list):
            profiles.extend(batch)
        else:
            profiles.append(batch)

    profiles = profiles[:n]
    _save(profiles, "ae_profiles")
    print(f"Generated {len(profiles)} AE profiles → data/synthetic/ae_profiles.json")
    return profiles


def generate_call_transcripts(
    n: int = 50,
    sdr_profiles: list[dict] | None = None,
) -> list[dict]:
    """
    Generate n synthetic cold call transcripts for SDR coaching practice.

    If sdr_profiles is provided, each transcript is assigned a real profile
    so the data is internally consistent. Otherwise, placeholder values are used.
    Saves to data/synthetic/call_transcripts.json and returns the list.
    """
    transcripts: list[dict] = []

    for i in range(n):
        if sdr_profiles:
            profile = sdr_profiles[i % len(sdr_profiles)]
            sdr_name = profile.get("name", f"SDR_{i}")
            territory = profile.get("territory", "AMER")
            vertical = profile.get("vertical", "SaaS")
        else:
            sdr_name = f"SDR_{i + 1}"
            territory = random.choice(["AMER", "EMEA", "APAC"])
            vertical = random.choice(["fintech", "healthcare", "retail", "SaaS"])

        raw = _claude(
            system=SYNTHETIC_TRANSCRIPT_SYSTEM,
            user=SYNTHETIC_TRANSCRIPT_USER.format(
                sdr_name=sdr_name,
                territory=territory,
                vertical=vertical,
            ),
        )
        transcript = _parse_json(raw)
        transcripts.append(transcript)

        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{n} transcripts…")

    _save(transcripts, "call_transcripts")
    print(f"Generated {len(transcripts)} transcripts → data/synthetic/call_transcripts.json")
    return transcripts


def generate_all(
    n_sdr: int = 30,
    n_ae: int = 20,
    n_transcripts: int = 50,
) -> dict:
    """
    Convenience function: generate the full synthetic dataset in one call.
    Used as a setup script before demo day. Returns paths to all saved files.
    """
    print("Generating synthetic SDR profiles…")
    sdrs = generate_sdr_profiles(n_sdr)

    print("Generating synthetic AE profiles…")
    aes = generate_ae_profiles(n_ae)

    print("Generating synthetic call transcripts…")
    transcripts = generate_call_transcripts(n_transcripts, sdr_profiles=sdrs)

    return {
        "sdr_profiles": len(sdrs),
        "ae_profiles": len(aes),
        "call_transcripts": len(transcripts),
        "output_dir": _SYNTHETIC_DIR,
    }


if __name__ == "__main__":
    result = generate_all()
    print(f"\nDone: {result}")
