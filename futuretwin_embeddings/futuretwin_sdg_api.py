"""SDG routes reuse FutureTwin's encrypted browser-owned profile and CSRF."""
from __future__ import annotations

import uuid
from flask import request


def register_sdg_routes(app):
    from futuretwin_resume_api import (
        _response, _owner_hash, _csrf_token, _csrf_valid, _load_profile_document,
        _database_connection, _decrypt_profile, _encrypt_profile, PROFILE_TABLE,
    )
    from futuretwin_sdg import (
        clean_preferences, public_catalog, occupation_purpose, country_context,
        goal_connections,
    )

    @app.get("/api/sdg/map")
    def sdg_map_snapshot():
        try:
            from futuretwin_sdg_map import read_map_snapshot
            payload = read_map_snapshot()
            if payload is None:
                return _response({"error": "The SDG map snapshot is not available yet."}, 503)
            return _response(payload)
        except Exception:
            return _response({"error": "The precomputed SDG map could not be loaded."}, 503)

    @app.get("/api/sdg/map/entity")
    def sdg_map_entity():
        entity_type = request.args.get("type", "")
        uri = request.args.get("uri", "")
        if entity_type not in {"occupation", "skill"}:
            return _response({"error": "Choose an occupation or skill."}, 400)
        if not uri or len(uri) > 500:
            return _response({"error": "Choose a valid ESCO entity."}, 400)
        try:
            from futuretwin_sdg_map import map_entity_detail
            result = map_entity_detail(entity_type, uri)
            if result is None:
                return _response({"error": "That ESCO entity is not in this map snapshot."}, 404)
            return _response(result)
        except Exception:
            return _response({"error": "The ESCO entity details could not be loaded."}, 503)

    @app.get("/api/sdg/catalog")
    def sdg_catalog():
        try:
            return _response(public_catalog())
        except Exception:
            return _response({"error": "The sourced SDG catalogue is unavailable."}, 503)

    @app.get("/api/sdg/occupation")
    def sdg_occupation():
        uri = request.args.get("uri", "")
        if len(uri) > 500 or not uri:
            return _response({"error": "Choose an ESCO occupation."}, 400)
        try:
            return _response(occupation_purpose(uri, candidates=request.args.get("candidates", "1") != "0"))
        except LookupError as exc:
            return _response({"error": str(exc)}, 404)
        except Exception:
            return _response({"error": "SDG connections could not be loaded."}, 503)

    @app.get("/api/sdg/goal")
    def sdg_goal():
        try:
            return _response(goal_connections(request.args.get("goal", "")))
        except ValueError as exc:
            return _response({"error": str(exc)}, 400)
        except Exception:
            return _response({"error": "Connections for this SDG could not be loaded."}, 503)

    @app.get("/api/sdg/country")
    def sdg_country():
        try:
            return _response(country_context(request.args.get("target", "6.1")))
        except ValueError as exc:
            return _response({"error": str(exc)}, 400)
        except Exception:
            return _response({"error": "Country observations could not be loaded."}, 503)

    @app.get("/api/sdg/preferences")
    def sdg_preferences_get():
        try:
            from futuretwin_my_future import read_state
            stored = _load_profile_document(_owner_hash(create=True))
            state = read_state(stored.get("my_future") if stored else None)
            return _response({"preferences": state["purpose"], "csrf_token": _csrf_token(create=True)})
        except Exception:
            return _response({"error": "Your purpose priorities could not be loaded."}, 503)

    @app.post("/api/sdg/preferences")
    def sdg_preferences_save():
        if not _csrf_valid():
            return _response({"error": "Refresh the page and try again."}, 403)
        try:
            payload = request.get_json(silent=True)
            if not isinstance(payload, dict):
                return _response({"error": "Review your purpose priorities and try again."}, 400)
            prefs = clean_preferences(payload)
        except ValueError as exc:
            return _response({"error": str(exc)}, 400)
        try:
            from futuretwin_my_future import read_state
            owner = _owner_hash(create=True)
            with _database_connection() as conn:
                conn.execute("SELECT pg_advisory_xact_lock(%s)",
                             (int.from_bytes(owner[:8], "big", signed=True),))
                row = conn.execute(
                    f"SELECT encrypted_payload FROM {PROFILE_TABLE} WHERE owner_hash=%s FOR UPDATE",
                    (owner,)).fetchone()
                stored = _decrypt_profile(bytes(row[0])) if row else {"schema_version": 2, "skills": []}
                state = read_state(stored.get("my_future"))
                state["purpose"] = prefs
                stored["my_future"] = state
                conn.execute(
                    f"INSERT INTO {PROFILE_TABLE} (profile_id,owner_hash,encrypted_payload) VALUES (%s,%s,%s) "
                    "ON CONFLICT (owner_hash) DO UPDATE SET encrypted_payload=EXCLUDED.encrypted_payload,updated_at=NOW()",
                    (str(uuid.uuid4()), owner, _encrypt_profile(stored)))
            return _response({"preferences": prefs, "csrf_token": _csrf_token(create=True)})
        except Exception:
            return _response({"error": "Purpose priorities could not be saved. Try again."}, 503)
