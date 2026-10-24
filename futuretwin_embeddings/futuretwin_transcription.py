"""Local CPU-only speech transcription for FutureTwin Voice-to-Skills."""
from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any

MAX_AUDIO_BYTES = 8 * 1024 * 1024
MAX_AUDIO_SECONDS = 120
MAX_TRANSCRIPT_CHARS = 12_000

_MODEL: Any | None = None
_MODEL_LOCK = threading.Lock()
_TRANSCRIPTION_LOCK = threading.Lock()


class VoiceRequestError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def audio_extension_for_mime(mime_type: str) -> str | None:
    media_type = (mime_type or "").split(";", 1)[0].strip().lower()
    return {
        "audio/webm": ".webm",
        "audio/mp4": ".mp4",
        "audio/m4a": ".m4a",
        "audio/x-m4a": ".m4a",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/ogg": ".ogg",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/aac": ".aac",
    }.get(media_type)


def validate_audio_file(path: str | Path) -> float:
    """Reject unsupported, malformed, silent-container, and overlong input."""
    try:
        import av

        with av.open(str(path), mode="r") as container:
            streams = [stream for stream in container.streams if stream.type == "audio"]
            if not streams:
                raise VoiceRequestError("No audio track was found. Record again or type instead.")
            duration = container.duration
            if duration is not None:
                seconds = float(duration) / av.time_base
            else:
                stream_durations = [
                    float(stream.duration * stream.time_base)
                    for stream in streams
                    if stream.duration is not None and stream.time_base is not None
                ]
                if not stream_durations:
                    raise VoiceRequestError("The recording duration could not be verified.")
                seconds = max(stream_durations)
    except VoiceRequestError:
        raise
    except Exception as exc:
        raise VoiceRequestError("This recording could not be read. Try recording again.") from exc

    if seconds <= 0:
        raise VoiceRequestError("No audio was found. Record again or type instead.")
    if seconds > MAX_AUDIO_SECONDS:
        raise VoiceRequestError("Recordings must be 2 minutes or shorter.", 413)
    return seconds


def _get_model():
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                from faster_whisper import WhisperModel

                _MODEL = WhisperModel(
                    os.getenv("FUTURETWIN_WHISPER_MODEL", "small"),
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=max(1, min(2, os.cpu_count() or 1)),
                    num_workers=1,
                )
    return _MODEL


def transcribe_audio_file(path: str | Path, language: str | None = "en") -> dict[str, str]:
    """Transcribe one temporary audio file; never writes audio or text to storage."""
    with _TRANSCRIPTION_LOCK:
        model = _get_model()
        segments, info = model.transcribe(
            str(path),
            language=language,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
            without_timestamps=True,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()

    if not transcript:
        raise VoiceRequestError("No clear speech was detected. Try again or type your experience.", 422)
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        raise VoiceRequestError("This transcript is too long. Record a shorter segment.", 413)
    return {"transcript": transcript, "language": str(info.language or "")}
