"""Read-only, session-owned comparisons and public opportunity evidence."""
from flask import request


def register_intelligence_routes(app):
    @app.get("/api/my-future/opportunities")
    def career_opportunities():
        from futuretwin_resume_api import _response
        from futuretwin_opportunities import opportunity_radar
        try:
            limit = int(request.args.get("limit", "12"))
        except ValueError:
            return _response({"error": "limit must be a whole number."}, 400)
        if not 1 <= limit <= 30:
            return _response({"error": "limit must be from 1 to 30."}, 400)
        return _response(opportunity_radar(limit))

    @app.get("/api/my-future/job-postings")
    def my_future_job_postings():
        from futuretwin_resume_api import (
            _load_profile_document, _owner_hash, _response,
        )
        from futuretwin_my_future import _confirmed_skills
        from futuretwin_occupation_api import get_esco_occupation_catalog
        from futuretwin_job_search import search_job_postings

        def bounded_text(name, maximum=100):
            value = request.args.get(name, "").strip()
            if len(value) > maximum:
                raise ValueError(f"{name} must be {maximum} characters or fewer.")
            return value

        try:
            limit = int(request.args.get("limit", "30"))
            if not 1 <= limit <= 50:
                raise ValueError("limit must be from 1 to 50.")
            q = bounded_text("q")
            occupation = bounded_text("occupation")
            occupation_uri = bounded_text("occupation_uri", 500)
            location = bounded_text("location")
            skill = bounded_text("skill")
            skill_uri = bounded_text("skill_uri", 500)
            workplace = bounded_text("workplace", 20)
            if workplace not in {"", "remote", "non_remote"}:
                raise ValueError("workplace must be remote or non_remote.")
        except ValueError as exc:
            return _response({"error": str(exc)}, 400)

        occupations, _, _ = get_esco_occupation_catalog()
        if occupation_uri:
            selected = occupations.get(occupation_uri)
            if not selected:
                return _response({"error": "ESCO occupation was not found."}, 404)
            occupation = selected["label"]
        owner = _owner_hash(create=False)
        try:
            stored = _load_profile_document(owner) if owner else None
            confirmed = _confirmed_skills(stored)
            result = search_job_postings(
                q=q,
                occupation=occupation,
                location=location,
                workplace=workplace,
                skill=skill,
                skill_uri=skill_uri,
                confirmed_skills=confirmed,
                limit=limit,
            )
            return _response(result)
        except Exception:
            return _response({
                "error": "Job listings are temporarily unavailable.",
            }, 503)

    @app.get("/api/my-future/compare")
    def compare_careers():
        from futuretwin_resume_api import _response, _owner_hash, _load_profile_document
        from futuretwin_my_future import build_career_details, read_state
        from futuretwin_occupation_api import get_esco_occupation_catalog
        from futuretwin_intelligence import comparison_status
        uris = request.args.getlist("uri")
        if (not 2 <= len(uris) <= 4 or len(set(uris)) != len(uris)
                or any(not u or len(u) > 500 for u in uris)):
            return _response({"error": "Choose 2–4 different ESCO careers to compare."}, 400)
        occupations, _, _ = get_esco_occupation_catalog()
        if any(uri not in occupations for uri in uris):
            return _response({"error": "An ESCO occupation was not found."}, 404)
        try:
            owner = _owner_hash(create=True)
            stored = _load_profile_document(owner)
            state = read_state(stored.get("my_future") if stored else None)
            careers = [build_career_details(uri, stored, state) for uri in uris]
            return _response({"careers": careers, "comparability": comparison_status(careers)})
        except Exception:
            return _response({"error": "Career comparison is temporarily unavailable."}, 503)
