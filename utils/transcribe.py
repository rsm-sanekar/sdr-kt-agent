"""Local speech-to-text for Coaching Notes.

Uses mlx-whisper — Apple-Silicon-native, runs on the GPU/Neural Engine, no
API key and no audio sent off-device. The model is pulled from HuggingFace on
first use and cached locally thereafter.

mlx-whisper is an optional dependency (``uv sync --group audio``) and is
imported lazily, so importing this module never fails on a machine without it;
the failure surfaces only when transcription is actually requested.
"""

from __future__ import annotations

# Small English model — fast on Apple Silicon and accurate enough for a
# coaching-call transcript. Override with a larger repo if needed.
DEFAULT_MODEL = "mlx-community/whisper-small.en-mlx"


class TranscriptionUnavailable(RuntimeError):
    """Raised when mlx-whisper (or ffmpeg) is not available in this environment."""


def transcribe_audio(file_path: str, model: str = DEFAULT_MODEL) -> str:
    """Transcribe an audio file to clean plain text.

    Returns the transcript as paragraphs. Raises ``TranscriptionUnavailable``
    if the optional audio stack is missing so callers can return a helpful
    error instead of a 500.
    """
    try:
        import mlx_whisper
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise TranscriptionUnavailable(
            "mlx-whisper is not installed. Run `uv sync --group audio` "
            "(Apple Silicon) to enable local audio transcription."
        ) from exc

    try:
        result = mlx_whisper.transcribe(file_path, path_or_hf_repo=model)
    except Exception as exc:  # noqa: BLE001 - surface a clean message to the UI
        msg = str(exc)
        if "ffmpeg" in msg.lower():
            raise TranscriptionUnavailable(
                "ffmpeg is required to decode audio. Install it with "
                "`brew install ffmpeg`."
            ) from exc
        raise TranscriptionUnavailable(f"Transcription failed: {msg}") from exc

    text = (result or {}).get("text", "")
    return _tidy(text)


def _tidy(text: str) -> str:
    """Whisper returns one long run of sentences. Break it into readable
    paragraphs roughly every few sentences so the transcript textarea is
    legible before the user adds SDR:/Prospect: role labels."""
    text = (text or "").strip()
    if not text:
        return ""
    sentences = []
    buf = ""
    for ch in text:
        buf += ch
        if ch in ".!?" :
            sentences.append(buf.strip())
            buf = ""
    if buf.strip():
        sentences.append(buf.strip())

    paragraphs = []
    for i in range(0, len(sentences), 3):
        paragraphs.append(" ".join(sentences[i : i + 3]))
    return "\n\n".join(paragraphs)
