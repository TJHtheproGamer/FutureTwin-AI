"""Validate locally authored practice against exact, real ESCO relationships."""
import copy
import json
import subprocess
import unittest

from futuretwin_occupation_api import get_esco_occupation_catalog
from futuretwin_playground import AVAILABLE_EXPERIENCE_EXAMPLES, career_experience
from futuretwin_playground_ui import PLAYGROUND_JS
from futuretwin_practice_scenarios import PRACTICE_SCENARIOS


class PracticeLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.occupations, _, cls.relations = get_esco_occupation_catalog()

    def test_sixteen_examples_have_distinct_real_career_skill_pairs(self):
        self.assertEqual(len(AVAILABLE_EXPERIENCE_EXAMPLES), 16)
        self.assertEqual(len(PRACTICE_SCENARIOS), 12)
        ids = set()
        for row in AVAILABLE_EXPERIENCE_EXAMPLES:
            with self.subTest(career=row["occupation_label"]):
                uri = row["occupation_uri"]
                occupation = self.occupations[uri]
                self.assertEqual(occupation["label"], row["occupation_label"])
                detail = career_experience(occupation, self.relations[uri])
                self.assertEqual(detail["status"], "available")
                self.assertEqual(detail["source"]["skill"]["uri"], row["skill_uri"])
                self.assertEqual(detail["source"]["skill"]["label"], row["skill_label"])
                self.assertTrue(detail["source"]["skill"]["description"])
                self.assertNotIn(detail["id"], ids)
                ids.add(detail["id"])

    def test_new_exercises_have_complete_feedback_and_do_not_mutate_inputs(self):
        for row in PRACTICE_SCENARIOS:
            with self.subTest(exercise=row["id"]):
                uri = row["occupation_uri"]
                occupation = self.occupations[uri]
                relations = self.relations[uri]
                before = copy.deepcopy((occupation, relations))
                detail = career_experience(occupation, relations)
                self.assertEqual((occupation, relations), before)
                self.assertEqual(detail["kind"], "illustrative_practice")
                self.assertNotIn("score", detail)
                self.assertNotIn("proficiency", detail)
                self.assertIn("No competence score", detail["notice"])
                self.assertTrue(detail["question"])
                self.assertEqual(len(detail["choices"]), 3)
                self.assertEqual(sum(choice["supported"] for choice in detail["choices"]), 1)
                self.assertEqual(len({c["id"] for c in detail["choices"]}), 3)
                self.assertTrue(all(c["label"] and c["feedback"] for c in detail["choices"]))
                self.assertEqual(
                    career_experience(occupation, {})["status"], "unavailable",
                    "An exercise must not survive removal of its official skill relation.",
                )

    def test_every_new_exercise_renders_all_steps_and_selected_answer_feedback(self):
        details = [
            career_experience(self.occupations[row["occupation_uri"]],
                              self.relations[row["occupation_uri"]])
            for row in PRACTICE_SCENARIOS
        ]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const context=vm.createContext({
 window:{innerWidth:1200},document:{getElementById:()=>null},$:()=>null,
 esc:s=>String(s??''),state:{roadmap_goals:{},roadmap_progress:{}}
});
vm.runInContext(SOURCE+'\n;globalThis.api={pg,pgExp};',context);
const {pg,pgExp}=context.api;
for(const ce of EXERCISES){
 pg.exp={step:0,strength:50,choice:null};
 let html=pgExp({career_experience:ce});
 assert.ok(html.includes(ce.title));
 assert.ok(html.includes('Available practice skills (16)'));
 assert.ok(html.includes('Start exercise'));
 pg.exp.step=1;html=pgExp({career_experience:ce});
 assert.ok(html.includes('Step 1 of 2'));
 assert.ok(html.includes(ce.activity.type==='table'?ce.activity.caption:ce.activity.context));
 pg.exp.step=2;
 for(const choice of ce.choices){
  pg.exp.choice=choice.id;
  html=pgExp({career_experience:ce});
  assert.ok(html.includes(ce.question));
  assert.ok(html.includes(choice.feedback));
  assert.ok(html.includes(choice.supported?'Supported by this example':'Not supported by this example'));
  assert.ok(html.includes('Try again'));
 }
}
"""
        script = script.replace("SOURCE", json.dumps(PLAYGROUND_JS), 1)
        script = script.replace("EXERCISES", json.dumps(details), 1)
        result = subprocess.run(
            ["node", "-e", script], capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
