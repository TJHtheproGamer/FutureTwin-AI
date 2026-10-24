"""Experience-to-skills drafts and transient, self-hosted audio transcription."""
from __future__ import annotations

import tempfile
import threading
import time
from pathlib import Path

from flask import request, session
from werkzeug.exceptions import RequestEntityTooLarge

from futuretwin_skills_profile import ProfileValidationError
from futuretwin_transcription import (
    MAX_AUDIO_BYTES,
    MAX_AUDIO_SECONDS,
    VoiceRequestError,
    audio_extension_for_mime,
    transcribe_audio_file,
    validate_audio_file,
)

MAX_TRANSCRIPT_CHARS = 12_000
MAX_VOICE_REQUEST_BYTES = MAX_AUDIO_BYTES + 128 * 1024
MAX_TRANSCRIPTIONS_PER_HOUR = 5
VOICE_LANGUAGES = {"auto": None, "en": "en", "ms": "ms", "zh": "zh"}
_VOICE_REQUEST_LOCK = threading.Lock()


def register_experience_routes(app) -> None:
    # Import lazily: the resume module owns the shared security/storage pipeline.
    import futuretwin_resume_api as api

    @app.get("/api/profile/voice")
    def voice_capabilities():
        return api._response({
            "transcription_available": True,
            "provider": "self-hosted faster-whisper",
            "languages": ["en", "ms", "zh", "auto"],
            "max_recording_seconds": MAX_AUDIO_SECONDS,
            "max_audio_bytes": MAX_AUDIO_BYTES,
            "notice": "Audio is transcribed locally on the FutureTwin server and deleted after processing.",
        })

    @app.post("/api/profile/voice")
    def voice_transcribe():
        if not api._csrf_valid():
            return api._response({"error": "Refresh the page and try again."}, 403)
        if request.content_length is not None and request.content_length > MAX_VOICE_REQUEST_BYTES:
            return api._response({"error": "Keep recordings to 8 MB or less."}, 413)
        if request.form.get("consent") != "true":
            return api._response({"error": "Please agree to server-side transcription first."}, 400)

        language = request.form.get("language", "en").strip().lower()
        if language not in VOICE_LANGUAGES:
            return api._response({"error": "Choose English, Malay, Mandarin, or auto-detect."}, 400)
        upload = request.files.get("audio")
        if upload is None:
            return api._response({"error": "Choose a recording to transcribe."}, 400)

        extension = audio_extension_for_mime(upload.mimetype)
        if extension is None:
            upload.close()
            return api._response({"error": "This audio format is not supported. Record again or type instead."}, 415)

        acquired = _VOICE_REQUEST_LOCK.acquire(blocking=False)
        if not acquired:
            upload.close()
            return api._response({"error": "Another recording is being transcribed. Please wait and try again."}, 409)

        raw_audio = b""
        try:
            now = time.time()
            recent = [
                value for value in session.get("ft_voice_transcribe_times", [])
                if isinstance(value, (int, float)) and now - value < 3600
            ]
            if len(recent) >= MAX_TRANSCRIPTIONS_PER_HOUR:
                return api._response({"error": "Too many transcription attempts. Please try again in an hour."}, 429)

            raw_audio = upload.stream.read(MAX_AUDIO_BYTES + 1)
            if not raw_audio:
                return api._response({"error": "The recording is empty. Record again or type instead."}, 400)
            if len(raw_audio) > MAX_AUDIO_BYTES:
                return api._response({"error": "Keep recordings to 8 MB or less."}, 413)

            session["ft_voice_transcribe_times"] = recent + [now]
            with tempfile.TemporaryDirectory(prefix="futuretwin-voice-") as temp_dir:
                # PyAV probes the actual container bytes. A fixed basename
                # avoids incorporating any request-derived text in a file path.
                audio_path = Path(temp_dir) / "recording.audio"
                with audio_path.open("xb") as temporary_audio:
                    temporary_audio.write(raw_audio)
                raw_audio = b""
                validate_audio_file(audio_path)
                result = transcribe_audio_file(audio_path, VOICE_LANGUAGES[language])
                transcript = result.get("transcript", "").strip()
                detected_language = result.get("language", "")
                if not transcript:
                    raise VoiceRequestError(
                        "No clear speech was detected. Try again or type your experience.", 422
                    )
                if len(transcript) > MAX_TRANSCRIPT_CHARS:
                    raise VoiceRequestError("This transcript is too long. Record a shorter segment.", 413)
            return api._response({
                "transcript": transcript,
                "language": detected_language,
                "audio_retained": False,
            })
        except VoiceRequestError as exc:
            return api._response({"error": str(exc)}, exc.status)
        except RequestEntityTooLarge:
            return api._response({"error": "Keep recordings to 8 MB or less."}, 413)
        except Exception:
            # Never include source audio, transcript text, or model exception details.
            return api._response({
                "error": "Speech recognition is temporarily unavailable. Your audio was not saved. Try again or type instead."
            }, 503)
        finally:
            raw_audio = b""
            upload.close()
            _VOICE_REQUEST_LOCK.release()

    @app.post("/api/profile/experience")
    def experience_extract():
        if not api._csrf_valid():
            return api._response({"error": "Refresh the page and try again."}, 403)
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or payload.get("consent") is not True:
            return api._response({"error": "Please consent to AI processing first."}, 400)
        text = payload.get("transcript")
        if not isinstance(text, str) or not text.strip():
            return api._response({"error": "Describe some work or a project first."}, 400)
        if len(text) > MAX_TRANSCRIPT_CHARS:
            return api._response({"error": "Keep your experience under 12,000 characters."}, 413)
        now = time.time()
        recent = [
            value for value in session.get("ft_experience_extract_times", [])
            if isinstance(value, (int, float)) and now - value < 3600
        ]
        if len(recent) >= 5:
            return api._response({"error": "Too many extraction attempts. Please try again in an hour."}, 429)
        session["ft_experience_extract_times"] = recent + [now]
        try:
            raw = api._extract_skills_local(text.strip(), "experience")
            draft = api._validated_extraction(raw, text.strip())
            draft["skills"] = [
                {**item, "source": "experience", "evidence_consent": False}
                for item in api._match_skill_candidates(draft["skills"])
            ]
            return api._response({
                "draft": draft,
                "notice": "Nothing has been saved. Confirm your matches. Supporting quotes are saved only if you opt in.",
            })
        except Exception:
            # Never include source text, provider responses or exception details.
            return api._response({
                "error": "Skills could not be extracted right now. Your experience was not saved. Try again or enter skills manually."
            }, 502)

    @app.post("/api/profile/experience/save")
    def experience_save():
        if not api._csrf_valid():
            return api._response({"error": "Refresh the page and try again."}, 403)
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or payload.get("consent") is not True:
            return api._response({"error": "Please confirm you want to save these skills."}, 400)
        rows = payload.get("skills")
        if not isinstance(rows, list) or not rows or any(not isinstance(row, dict) for row in rows):
            return api._response({"error": "Confirm at least one skill before saving."}, 400)
        if any(row.get("confirmed") is not True or not row.get("selected_esco_uri") for row in rows):
            return api._response({"error": "Confirm each new skill before saving."}, 400)
        save_quotes = payload.get("save_quotes") is True
        try:
            # Whitelist profile fields downstream; never store an entire transcript.
            profile = api._clean_user_profile({"skills": [
                {**row, "source": "experience", "evidence_consent": save_quotes,
                 "evidence": row.get("evidence", "") if save_quotes else ""}
                for row in rows
            ]})
            saved = api._save_profile(api._owner_hash(create=True), profile, append=True)
            added = saved.pop("_added_count")
            duplicates = saved.pop("_duplicate_count")
            return api._response({"profile": saved, "added_count": added, "duplicate_count": duplicates})
        except (api.ResumeRequestError, ProfileValidationError) as exc:
            return api._response({"error": str(exc)}, getattr(exc, "status", 400))
        except Exception:
            return api._response({"error": "Your skills could not be saved right now. Please try again."}, 503)
