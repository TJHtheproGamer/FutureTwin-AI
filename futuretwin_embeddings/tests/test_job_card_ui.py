"""Test the browser-rendered job-card occupation-match labels."""
import ast
from pathlib import Path
import subprocess
import unittest


class JobCardUiTests(unittest.TestCase):
    def test_review_badge_is_hidden_but_verified_match_labels_remain(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_intel_ui.py"
        tree = ast.parse(path.read_text())
        js = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "FIND_JS"
                          for t in n.targets))
        intel_js = next(ast.literal_eval(n.value) for n in tree.body
                        if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "INTEL_JS"
                                for t in n.targets))
        start = intel_js.index("function ftCoverageEl(r){")
        end = intel_js.index("function ftEnrichCard(el,c){", start)
        coverage_function = intel_js[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const ctx={
 document:{createElement:()=>({className:'',innerHTML:''})},
 esc:v=>String(v??''),
 ftNum:v=>v===undefined||v===null||v===''?null:Number(v),
 ftPct:v=>v===undefined||v===null?'':Number(v)+'%'
};
vm.runInNewContext(SOURCE+'\n;globalThis.ftCoverageEl=ftCoverageEl;',ctx);
const unavailable=ctx.ftCoverageEl({hiring_trend:{growth_pct:null,reason:'not comparable'}}).innerHTML;
assert(!unavailable.includes('Hiring:'));
assert(!unavailable.includes('trend not available'));
const available=ctx.ftCoverageEl({
 task_exposure:{
  status:'available',classified_task_count:25,task_coverage_percentage:100,
  predicted_task_exposure:{status:'available',percentage:30}
 },
 hiring_trend:{growth_pct:4}
}).innerHTML;
assert(available.includes('Hiring: +4% change'));
assert(!available.includes('Tasks:'));
assert(available.includes('predicted task-exposure share'));
console.log('Hiring trend label visibility: passed');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", coverage_function, 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn(
            "Add confirmed skills to My Skills Passport to see exact skill mentions.",
            js,
        )
        self.assertNotIn(
            ". Check availability on the source. This sample does not measure hiring growth.",
            js,
        )
        self.assertNotIn("Also named in the ad · not in your Passport", js)
        self.assertNotIn(
            '<span class="ft-radar-evidence-method">Match: ',
            js,
        )
        self.assertNotIn(
            "Not listed in your Passport does not mean you lack a skill.",
            js,
        )
        start = js.index("function actualJobCard(it){")
        end = js.index("function renderJobResults(){", start)
        card_function = js[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const node=(_tag,cls)=>({className:cls,innerHTML:''});
const ctx={esc:s=>String(s??''),ftSafeUrl:()=>'',radarDate:()=> '',
  ftNum:()=>null,ftPct:()=>null,node};
vm.runInNewContext(SOURCE+'\n;globalThis.actualJobCard=actualJobCard;',ctx);
function card(status){
 return ctx.actualJobCard({
   title:'Sample role', employer:'Sample employer', workplace_type:'unspecified',
   remote:false, location:'', country:'', source_label:'Sample source',
   posted_date:null, source_updated_at:null, collected_at:null, seniority:'',
   employment_type:'', salary_text:'', salary_min:null, salary_max:null,
   salary_currency:'', salary_period:'', description:'', url:'',
   confirmed_skill_match_count:0, explicit_skills:[],
   matched_passport_skills:[], ad_skills_not_in_passport:[],
   semantic_candidates:[],
   occupation_match:{status,label:'Sample ESCO occupation'}
 }).innerHTML;
}
const uncertain=card('uncertain_suggestion');
assert(!uncertain.includes('ESCO candidates · needs review'));
assert(uncertain.includes('Why this ESCO label?'));
assert(card('exact_title').includes('Exact ESCO title match'));
assert(card('semantic_suggested').includes('Possible ESCO match'));
console.log('Job-card match labels: passed');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", ast.literal_eval(
                repr(card_function)), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_career_summary_omits_exact_source_task_coverage_card(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_intel_ui.py"
        tree = ast.parse(path.read_text())
        js = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "FIND_JS"
                          for t in n.targets))
        start = js.index("function ftSummary(){")
        end = js.index("function relItems(){", start)
        summary_function = js[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const ctx={
 D:{
  task_exposure:{
   status:'available',
   predicted_task_exposure:{status:'available',percentage:60,numerator:15,denominator:25},
   classified_task_count:25,occupation_total_task_count:25,task_coverage_percentage:100
  },
  intelligence:{advancement:{status:'available',series:[{}]}}
 },
 esc:v=>String(v??''),
 ftNum:v=>v===undefined||v===null||v===''?null:Number(v),
 ftPct:v=>v===undefined||v===null?'':Number(v)+'%'
};
vm.runInNewContext(SOURCE+'\n;globalThis.ftSummary=ftSummary;',ctx);
const html=ctx.ftSummary();
assert(!html.includes('Exact source-task coverage'));
assert(!html.includes('source tasks assessed'));
assert(html.includes('Predicted task-exposure share'));
assert(html.includes('Measured AI advancement'));
console.log('Career summary cards: passed');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", summary_function, 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_jobs_tab_keeps_related_careers_without_intelligence_card(self):
        root = Path(__file__).resolve().parents[1]
        tree = ast.parse((root / "futuretwin_intel_ui.py").read_text())
        js = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "FIND_JS"
                          for t in n.targets))
        site_js = (root / "futuretwin_site_ui.py").read_text()
        self.assertNotIn('id="cr-jobs"', js)
        self.assertNotIn("function renderIntel()", js)
        self.assertIn("id=\"cr-related\"", js)
        self.assertIn("fillRelated();wireTabs();", site_js)
        self.assertNotIn("renderIntel();wireTabs();", site_js)

    def test_career_comparison_table_omits_hiring_row(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_intel_ui.py"
        tree = ast.parse(path.read_text())
        js = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "FIND_JS"
                          for t in n.targets))
        self.assertNotIn("['Hiring',c=>", js)
        self.assertIn("['Skill coverage',c=>", js)
        self.assertIn("['Task classes',c=>", js)
        self.assertIn("['Task coverage',c=>", js)
        self.assertIn("['Predicted task-exposure share',c=>", js)


if __name__ == "__main__":
    unittest.main()
