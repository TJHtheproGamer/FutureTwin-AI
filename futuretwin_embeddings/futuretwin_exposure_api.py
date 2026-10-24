"""Additive public-catalog APIs; no profile writes or remote inference."""
from __future__ import annotations

import time
from flask import jsonify, request, session
from werkzeug.exceptions import BadRequest

from futuretwin_distilbert import CLASSIFIER, ModelBusy, ModelUnavailable
from futuretwin_task_exposure import occupation_exposure


def register_exposure_routes(app):
    def response(data, status=200):
        result = jsonify(data)
        result.status_code = status
        result.headers["Cache-Control"] = "no-store"
        return result

    @app.post("/api/occupations/classify-tasks")
    def classify_tasks():
        from futuretwin_resume_api import _csrf_valid
        if not _csrf_valid():
            return response({"error": "Refresh your profile session and supply its CSRF token."}, 403)
        if request.content_length is None or request.content_length > 65536:
            return response({"error": "Task requests must be 64 KB or smaller."}, 413)
        try:
            payload = request.get_json(silent=True)
            texts = payload.get("tasks") if isinstance(payload, dict) else None
            if not isinstance(texts, list) or not 1 <= len(texts) <= 16:
                return response({"error": "Provide 1–16 task descriptions in tasks."}, 400)
            if any(not isinstance(t, str) or not t.strip() or len(t) > 8000 for t in texts):
                return response({"error": "Each task must contain 1–8000 characters."}, 400)
            task_ids = payload.get("task_ids")
            if task_ids is not None and (
                not isinstance(task_ids, list) or len(task_ids) != len(texts)
                or any(not isinstance(t, str) or not t.strip() or len(t) > 100 for t in task_ids)
            ):
                return response({"error": "task_ids must match the task count, with IDs of 1–100 characters."}, 400)
            now = time.time()
            recent = [t for t in session.get("ft_task_classify_times", [])
                      if isinstance(t, (int, float)) and now - t < 60]
            if len(recent) >= 10:
                return response({"error": "Too many classification requests. Wait one minute."}, 429)
            session["ft_task_classify_times"] = [*recent, now]
            result = CLASSIFIER.classify(texts)
            predictions = result.pop("predictions")
            return response({**result, "tasks": [
                {"task_id": task_ids[index] if task_ids else f"input:{index + 1}",
                 "task_id_source": "caller_supplied" if task_ids else "request_index",
                 "text": text, **prediction}
                for index, (text, prediction) in enumerate(zip(texts, predictions))
            ]})
        except (ValueError, BadRequest):
            return response({"error": "Provide valid JSON task descriptions."}, 400)
        except ModelBusy as exc:
            return response({"error": str(exc), "status": "busy"}, 429)
        except ModelUnavailable as exc:
            return response({"error": str(exc), "status": "model_unavailable"}, 503)

    @app.get("/api/occupations/exposure")
    def get_occupation_exposure():
        from futuretwin_occupation_api import get_esco_occupation_catalog
        uri = request.args.get("uri", "")
        occupations, _, _ = get_esco_occupation_catalog()
        if uri not in occupations:
            return response({"error": "Choose an occupation from ESCO search."}, 404)
        try:
            result = occupation_exposure(uri)
            return response({"occupation": {"uri": uri, "label": occupations[uri]["label"]}, **result})
        except ModelBusy as exc:
            return response({"error": str(exc), "status": "busy"}, 429)
        except ModelUnavailable as exc:
            return response({"error": str(exc), "status": "model_unavailable"}, 503)
        except (OSError, KeyError):
            return response({"error": "The stored task catalog is unavailable.",
                             "status": "task_data_unavailable"}, 503)
