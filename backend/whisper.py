import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set — check .env (Whisper requires OpenAI)")
        _client = OpenAI(api_key=key)
    return _client


def transcribe(audio_path: str) -> str:
    """Transcribe an audio file to text using OpenAI Whisper."""
    with open(audio_path, "rb") as f:
        result = _get_client().audio.transcriptions.create(model="whisper-1", file=f)
    return result.text
