"""The purpose feature must remain a source-attributed, opt-in heuristic."""
import copy

import unittest
from unittest.mock import patch

from futuretwin_sdg import (
    clean_preferences, public_catalog, rank_by_purpose, reviewed_links,
    country_context, occupation_purpose, candidate_records, goal_connections,
)


def prefs(goals=None, skill=70):
    return {"goals": goals or ["7"], "skill_weight": skill,
            "purpose_weight": 100-skill, "demand_weight": 0}


def candidate(uri, pct):
    return {"uri": uri, "title": uri, "skill_coverage": {"percentage": pct}}


def test_official_catalog_and_desk_review_not_outcome_verification():
    c = public_catalog()
    assert len(c["goals"]) == 17
    assert len(c["targets"]) == 169
    assert c["reviewed_mapping_count"] == 6
    assert c["reviewed_career_count"] == 5
    assert c["assistant_desk_reviewed_count"] == 6
    assert c["reviewed_goal_count"] == 5
    assert c["independent_human_reviewed_count"] == 0
    assert c["total_occupation_count"] == 3039
    assert c["occupations_without_reviewed_evidence"] == 3034
    for link in reviewed_links():
        assert link["skills"][0]["uri"] == link["skill_uri"]
        assert link["review_status"] == "assistant_desk_reviewed"
        assert link["semantic_score"] is None
        assert len(link["evidence"]) >= 3


def test_candidate_queue_has_100_occupations_200_skills_and_all_goals():
    catalog = public_catalog()["candidate_summary"]
    rows = candidate_records()
    assert catalog["candidate_link_count"] == 200
    assert catalog["candidate_occupation_count"] == 100
    assert catalog["candidate_skill_count"] == 200
    assert catalog["candidate_goal_count"] == 17
    assert catalog["candidate_nace_division_count"] >= 10
    assert all(row["nace_codes"] and row["nace_divisions"] for row in rows)
    assert catalog["occupations_by_isco_major_group"].keys() >= set("123456789")
    assert len({row["occupation_uri"] for row in rows}) == 100
    assert len({row["skills"][0]["uri"] for row in rows}) == 200
    assert {str(row["goal_code"]) for row in rows} == {str(i) for i in range(1, 18)}
    assert all(row["review_status"] == "unreviewed_candidate" for row in rows)
    assert all(row["strength"] is None and row["direction"] is None for row in rows)
    assert all(row["relationship_status"] == "not_assessed" for row in rows)
    assert all(len(row["evidence"]) == 3 for row in rows)


def test_goal_explorer_separates_reviewed_links_from_candidate_suggestions():
    data = goal_connections("7")
    assert data["goal"]["code"] == "7"
    assert data["reviewed_connection_count"] > 0
    assert data["candidate_suggestion_count"] > 0
    assert all(
        str(row["target"]["goal_code"]) == "7"
        and row["review_status"] == "assistant_desk_reviewed"
        for row in data["reviewed_connections"]
    )
    assert all(
        str(row["goal_code"]) == "7"
        and row["review_status"] == "unreviewed_candidate"
        and row["strength"] is None
        and row["direction"] is None
        for row in data["candidate_suggestions"]
    )


def test_unreviewed_suggestions_are_not_used_for_purpose_ranking():
    row = next(row for row in candidate_records() if row["goal_code"] == "1")
    ranked, metadata = rank_by_purpose(
        [candidate(row["occupation_uri"], 90)], prefs(["1"])
    )
    assert "fallback_reason" in metadata
    assert "purpose" not in ranked[0]


def test_invalid_preferences_fail_closed():
    for bad in ({"goals": ["18"]}, {"goals": [1]}, {"goals": "7"},
                {"skill_weight": float("nan")}, {"skill_weight": True},
                {"demand_weight": 1}, {"skill_weight": 80, "purpose_weight": 30}):
        with unittest.TestCase().assertRaises(ValueError):
            clean_preferences(bad)


def test_default_and_deduplication():
    assert clean_preferences(None)["goals"] == []
    assert clean_preferences(prefs(["7", "7", "6"]))["goals"] == ["7", "6"]


def test_unknown_is_excluded_not_zero_and_no_semantic_candidates_rank():
    solar = next(r for r in reviewed_links() if r["id"] == "solar-generation-7.2")
    before = [candidate("unknown", 100), candidate(solar["occupation_uri"], 20)]
    untouched = copy.deepcopy(before)
    ranked, meta = rank_by_purpose(before, prefs())
    assert before == untouched
    assert [x["uri"] for x in ranked] == [solar["occupation_uri"]]
    assert abs(ranked[0]["purpose"]["heuristic_points"] - 44) < .000001
    assert meta["excluded_candidate_count"] == 1
    assert meta["demand_applied"] is False


def test_no_evidence_falls_back_not_fake_purpose():
    rows = [candidate("unknown", 50)]
    ranked, metadata = rank_by_purpose(rows, prefs(["1"]))
    assert ranked == rows
    assert "fallback_reason" in metadata
    assert "purpose" not in ranked[0]


def test_zero_purpose_weight_does_not_require_evidence():
    ranked, meta = rank_by_purpose([candidate("unknown", 50)], prefs(skill=100))
    assert ranked[0]["purpose"]["heuristic_points"] == 50
    assert ranked[0]["purpose"]["score"] is None


def test_tradeoff_not_personal_harm_score():
    solar = next(r for r in reviewed_links() if r["id"] == "solar-generation-7.2")
    data = occupation_purpose(solar["occupation_uri"], candidates=False)
    assert len(data["connections"]) <= 3
    assert any(r["direction"] == "mixed" and r["relationship_scope"] == "technology_lifecycle_context"
               for r in data["connections"])
    assert "individual outcomes are not measured" in data["tradeoff_status"]


def test_country_dimensions_are_not_combined():
    with patch("jobmarket_store.get_stats_series", return_value=[]):
        for target in ("3.8", "4.1", "6.1", "7.2"):
            d = country_context(target)
            assert d["impact_gap_score"] is None
            assert d["comparison_status"] == "context_only"
            assert d["indicator"]["latest"]
            years = [p["year"] for p in d["indicator"]["observations"]]
            assert len(years) == len(set(years))
            assert d["wages"] == []
        d = country_context("4.1")
        assert d["indicator"]["latest"]["dimensions"]["Sex"] == "BOTHSEX"
        assert d["indicator"]["latest"]["dimensions"]["Education level"] == "PRIMAR"


def test_existing_state_round_trip_preserves_purpose():
    from futuretwin_my_future import empty_state, validate_state, read_state
    s = empty_state()
    s["purpose"] = prefs(["7", "6"], 40)
    assert read_state(validate_state(s))["purpose"] == s["purpose"]


def test_existing_recommendation_flow_uses_saved_priorities():
    from futuretwin_my_future import build_recommendations, empty_state
    solar = next(r for r in reviewed_links() if r["id"] == "solar-generation-7.2")
    skill = solar["skills"][0]
    state = empty_state()
    state["purpose"] = prefs(["7"], 40)
    with patch("futuretwin_my_future._confirmed_skills",
               return_value={skill["uri"]: {"uri": skill["uri"], "label": skill["label"]}}):
        result = build_recommendations({}, state, sort="purpose_alignment")
    assert result["status"] == "ok"
    # Purpose preferences remain saved for the separate SDG experience, but the
    # user explicitly removed this ranking mode and its Best Match contribution.
    assert result["ranking"]["effective"] == "best_match"
    assert result["recommendations"]
    assert all("purpose" not in r for r in result["recommendations"])
    assert state["purpose"] == prefs(["7"], 40)
    assert any(r["uri"] == solar["occupation_uri"] for r in result["recommendations"])


class PurposeTests(unittest.TestCase):
    """Expose the dependency-free cases through the project's unittest runner."""


for _name, _case in list(globals().items()):
    if _name.startswith("test_") and callable(_case):
        setattr(PurposeTests, _name, lambda self, case=_case: case())
