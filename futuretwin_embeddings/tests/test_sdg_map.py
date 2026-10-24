import unittest
from unittest.mock import patch

import numpy as np

from futuretwin_sdg_map import _pca_coordinates, map_entity_detail


class SdgMapProjectionTests(unittest.TestCase):
    def test_projection_is_repeatable_and_stays_inside_map_bounds(self):
        ids = ["occupation:a", "skill:b", "occupation:c", "skill:d"]
        vectors = {
            node_id: np.asarray([index + 1, 3 - index, index * 2 + 1, 1], dtype=float)
            for index, node_id in enumerate(ids)
        }
        goals = {"occupation:a": "1", "skill:b": "1",
                 "occupation:c": "12", "skill:d": "12"}
        anchors = {"1": np.asarray([1, 0, 0, 1], dtype=float),
                   "12": np.asarray([0, 1, 1, 0], dtype=float)}

        first = _pca_coordinates(ids, vectors, goals, anchors)
        second = _pca_coordinates(ids, vectors, goals, anchors)

        self.assertEqual(first, second)
        for x, y in first.values():
            self.assertGreaterEqual(x, .06)
            self.assertLessEqual(x, .94)
            self.assertGreaterEqual(y, .06)
            self.assertLessEqual(y, .94)

    def test_entity_details_preserve_multiple_review_states_and_targets(self):
        occupation_uri = "http://example.test/occupation/1"
        skill_uri = "http://example.test/skill/1"
        links = []
        for status, goal, target, score in (
            ("unreviewed_candidate", "1", "1.3", .67),
            ("assistant_desk_reviewed", "3", "3.8", None),
            ("independently_human_approved", "4", "4.4", None),
        ):
            links.append({
                "occupation_uri": occupation_uri,
                "skill_uri": skill_uri,
                "skill_label": "support learners",
                "skill_relation": "essential",
                "target_code": target,
                "goal_code": goal,
                "target_title": f"Target {target}",
                "target_uri": f"https://unstats.un.org/sdgs/UNSDGAPIV5/v1/Target/{target}",
                "review_status": status,
                "semantic_score": score,
                "strength": "direct" if score is None else None,
                "direction": "positive" if score is None else None,
                "reason": "",
                "evidence": [],
            })
        snapshot = {
            "nodes": [{
                "type": "occupation", "uri": occupation_uri,
                "label": "learning support worker",
            }],
            "links": links,
        }
        occupations = {
            occupation_uri: {
                "uri": occupation_uri,
                "label": "learning support worker",
                "description": "Supports learning.",
            }
        }
        relations = {
            occupation_uri: {
                "essential": [{"uri": skill_uri, "label": "support learners"}],
                "optional": [],
            }
        }
        with (
            patch("futuretwin_sdg_map.read_map_snapshot", return_value=snapshot),
            patch("futuretwin_occupation_api.get_esco_occupation_catalog",
                  return_value=(occupations, [], relations)),
            patch("futuretwin_career_insurance.skill_descriptions",
                  return_value={skill_uri: {"description": "Help learners."}}),
        ):
            result = map_entity_detail("occupation", occupation_uri)

        self.assertEqual(result["entity"]["label"], "learning support worker")
        self.assertEqual(result["skills"][0]["description"], "Help learners.")
        self.assertEqual(
            [item["review_status"] for item in result["connections"]],
            ["independently_human_approved", "assistant_desk_reviewed",
             "unreviewed_candidate"],
        )
        self.assertEqual(
            [item["target_code"] for item in result["connections"]],
            ["4.4", "3.8", "1.3"],
        )

    def test_skill_detail_returns_only_exact_related_careers(self):
        uri = "skill:water-testing"
        snapshot = {
            "nodes": [{"type": "skill", "uri": uri, "label": "test water quality"}],
            "links": [{
                "occupation_uri": "occupation:water",
                "skill_uri": uri,
                "skill_label": "test water quality",
                "skill_relation": "essential",
                "goal_code": "6",
                "target_code": "6.3",
                "target_title": "Improve water quality",
                "target_uri": "https://example.test/target/6.3",
                "review_status": "unreviewed_candidate",
                "semantic_score": .61,
                "strength": None,
                "direction": None,
                "reason": "Text similarity suggests a connection to investigate.",
                "evidence": [],
            }],
        }
        occupations = {
            "occupation:water": {"label": "water technician"},
            "occupation:lab": {"label": "laboratory technician"},
            "occupation:unrelated": {"label": "unrelated career"},
        }
        relations = {
            "occupation:water": {
                "essential": [{"uri": uri, "label": "test water quality"}],
                "optional": [],
            },
            "occupation:lab": {
                "essential": [],
                "optional": [{"uri": uri, "label": "test water quality"}],
            },
            "occupation:unrelated": {
                "essential": [{"uri": "skill:other", "label": "another skill"}],
                "optional": [],
            },
        }
        with (
            patch("futuretwin_sdg_map.read_map_snapshot", return_value=snapshot),
            patch("futuretwin_occupation_api.get_esco_occupation_catalog",
                  return_value=(occupations, [], relations)),
            patch("futuretwin_career_insurance.skill_descriptions",
                  return_value={uri: {"description": "Test samples of water."}}),
        ):
            result = map_entity_detail("skill", uri)
        self.assertEqual(result["entity"]["description"], "Test samples of water.")
        self.assertEqual(result["occupation_count"], 2)
        self.assertEqual(
            {(row["uri"], row["relation"]) for row in result["occupations"]},
            {("occupation:water", "essential"), ("occupation:lab", "optional")},
        )
        self.assertEqual(result["skills"], [])
        self.assertEqual(
            result["connections"][0]["review_status"], "unreviewed_candidate"
        )
        self.assertEqual(result["connections"][0]["evidence"], [])

    def test_missing_snapshot_or_entity_stays_unavailable(self):
        with patch("futuretwin_sdg_map.read_map_snapshot", return_value=None):
            self.assertIsNone(map_entity_detail("occupation", "unknown"))
        with patch("futuretwin_sdg_map.read_map_snapshot",
                   return_value={"nodes": [], "links": []}):
            self.assertIsNone(map_entity_detail("skill", "unknown"))


if __name__ == "__main__":
    unittest.main()
