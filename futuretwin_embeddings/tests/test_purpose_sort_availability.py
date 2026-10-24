"""Legacy purpose-sort requests must not re-enable the removed My Future mode."""
import unittest
from unittest.mock import patch

from futuretwin_my_future import _recommendation_ranking, build_recommendations, empty_state


class PurposeSortRemovalTests(unittest.TestCase):
    def test_legacy_purpose_sort_becomes_best_match(self):
        ranking = _recommendation_ranking("purpose_alignment")
        self.assertEqual(ranking["effective"], "best_match")
        self.assertEqual(
            {option["id"] for option in ranking["options"]},
            {"best_match", "lower_exposure"},
        )

    def test_empty_profile_uses_three_factors_without_loading_sdg_reviews(self):
        with (
            patch("futuretwin_my_future.get_esco_occupation_catalog", return_value=({}, {}, {})),
            patch("futuretwin_sdg.reviewed_links", side_effect=AssertionError("SDG reviews must not be loaded")),
        ):
            state = empty_state()
            state["purpose"] = {"goals": ["3"], "purpose_weight": 100, "skill_weight": 0}
            result = build_recommendations(None, state, sort="purpose_alignment")
        self.assertEqual(result["ranking"]["effective"], "best_match")
        self.assertEqual(len(result["ranking"]["best_match"]["configured_weights"]), 3)
        self.assertNotIn("purpose_alignment", result["ranking"]["best_match"]["effective_weights"])


if __name__ == "__main__":
    unittest.main()
