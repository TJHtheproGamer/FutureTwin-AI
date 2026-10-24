"""Read-only contracts for the five public platform destinations."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile
import unittest
import json


class PageStructure(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.nav_links = []
        self.nav_depth = 0
        self.nav_link = None
        self.scripts = []
        self.in_script = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "nav" and attrs.get("id") == "navlinks":
            self.nav_depth = 1
        elif tag == "nav" and self.nav_depth:
            self.nav_depth += 1
        if tag == "a" and self.nav_depth:
            self.nav_link = {"href": attrs.get("href"), "label": "",
                             "active": attrs.get("aria-current") == "page"}
        if tag == "script" and not attrs.get("src"):
            self.in_script = True
            self.scripts.append("")

    def handle_data(self, text):
        if self.nav_link:
            self.nav_link["label"] += text
        if self.in_script:
            self.scripts[-1] += text

    def handle_endtag(self, tag):
        if tag == "a" and self.nav_link:
            self.nav_link["label"] = self.nav_link["label"].strip()
            self.nav_links.append(self.nav_link)
            self.nav_link = None
        if tag == "nav" and self.nav_depth:
            self.nav_depth -= 1
        if tag == "script":
            self.in_script = False


class PlatformUIContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from futuretwin_pages import HOME_HTML, MY_CAREER_HTML, CAREER_HTML, TRENDS_HTML
        from futuretwin_my_future_page import MY_FUTURE_HTML
        cls.pages = {
            "/": HOME_HTML, "/my-career": MY_CAREER_HTML,
            "/career": CAREER_HTML, "/my-future": MY_FUTURE_HTML,
            "/trends": TRENDS_HTML,
        }

    def test_shared_navigation_and_active_destination(self):
        expected = [
            ("/", "Home"), ("/career", "Explore Careers"),
            ("/sdg-map", "SDG Map"),
            ("/my-future", "My Future"), ("/trends", "AI Trends"),
        ]
        for route, html in self.pages.items():
            with self.subTest(route=route):
                structure = PageStructure(html)
                nav = structure.nav_links
                self.assertEqual([(n["href"], n["label"]) for n in nav], expected)
                active = [n["href"] for n in nav if n["active"]]
                self.assertEqual(active, [] if route == "/my-career" else [route])
                self.assertIn('role="menuitem" href="/my-career"', html)
                if route == "/my-career":
                    self.assertIn('role="menuitem" href="/my-career" aria-current="page"', html)

    def test_unique_ids_on_each_page(self):
        for route, html in self.pages.items():
            with self.subTest(route=route):
                repeated = [key for key, count in Counter(
                    PageStructure(html).ids
                ).items() if count > 1]
                self.assertEqual(repeated, [])

    def test_career_and_purpose_pages_expose_sdg_connections(self):
        from futuretwin_sdg_page import SDG_HTML, SDG_JS

        career = self.pages["/career"]
        self.assertIn('id="cr-sdg-list"', career)
        self.assertIn("loadCareerPurpose(uri)", career)
        self.assertIn('id="goal-explorer"', SDG_HTML)
        self.assertIn("loadGoalConnections(g)", SDG_JS)
        self.assertIn("/api/sdg/goal?goal=", SDG_JS)
        self.assertIn("Unreviewed suggestion", SDG_JS)
        self.assertIn("assistant desk-reviewed", SDG_JS)

    def test_home_trends_show_live_benchmark_coverage_separately_from_advances(self):
        from futuretwin_pages import HOME_DASH_JS

        self.assertIn("AI benchmark tracker", HOME_DASH_JS)
        self.assertIn("overview.current_measurements", HOME_DASH_JS)
        self.assertIn("overview.domains", HOME_DASH_JS)
        self.assertIn("overview.models_total", HOME_DASH_JS)
        self.assertIn("overview.benchmarks", HOME_DASH_JS)
        self.assertIn("Latest data collected", HOME_DASH_JS)
        self.assertIn("hm-trend-status", HOME_DASH_JS)
        self.assertIn("No new comparable improvements in the latest snapshot.", HOME_DASH_JS)

    def test_home_omits_the_three_shortcut_buttons(self):
        html = self.pages["/"]

        self.assertNotIn('id="hm-profile"', html)
        self.assertNotIn('id="hm-explore"', html)
        self.assertNotIn('id="hm-future"', html)
        self.assertNotIn('class="ft-quick"', html)
        self.assertIn('id="home-jobs"', html)

    def test_career_page_omits_the_historical_rubric_note(self):
        html = self.pages["/career"]

        self.assertNotIn(
            "Unweighted predictions under a historical research rubric", html
        )

    def test_task_exposure_detail_omits_task_summary_lines(self):
        from futuretwin_exposure_ui import EXPOSURE_JS

        self.assertNotIn("Predicted task-exposure share: ", EXPOSURE_JS)
        self.assertNotIn(" task records from ", EXPOSURE_JS)

    def test_my_future_passport_summary_sits_beside_saved_careers(self):
        html = self.pages["/my-future"]

        self.assertIn('class="myf-hero-tools"', html)
        self.assertIn('class="myf-passport-mini"', html)
        self.assertIn('id="confirmed-skill-count"', html)
        self.assertIn('id="saved-shortcut"', html)
        self.assertLess(html.index('class="myf-hero-tools"'), html.index('id="workspace"'))
        self.assertNotIn('aria-label="Skills Passport summary"', html)

    def test_my_future_interests_sit_beside_the_passport(self):
        html = self.pages["/my-future"]
        tools = html.index('class="myf-hero-tools"')
        passport = html.index('class="myf-passport-mini"', tools)
        interests = html.index('id="interest-chips"', tools)
        saved = html.index('id="saved-shortcut"', tools)
        discover = html.index('id="view-discover"')

        self.assertLess(passport, interests)
        self.assertNotIn('class="myf-interest-purpose"', html)
        self.assertLess(interests, saved)
        self.assertLess(saved, discover)
        self.assertEqual(html.count('id="interest-chips"'), 1)

    def test_my_future_hides_evidence_group_summary_copy(self):
        html = self.pages["/my-future"]

        self.assertNotIn("myf-evidence-group", html)
        self.assertNotIn("compare scores within this group", html)

    def test_my_future_disclosure_and_its_scenario_controls_are_removed(self):
        html = self.pages["/my-future"]

        self.assertNotIn("<summary>View Details</summary>", html)
        self.assertNotIn('id="scenario-tabs"', html)
        self.assertNotIn('id="scenario-copy"', html)
        self.assertNotIn('id="scenario-note"', html)
        self.assertNotIn("function renderScenarios(framework)", html)
        self.assertIn('aria-label="Scenario"', html)

    def test_playground_mode_selector_omits_try_scenarios(self):
        from futuretwin_playground_ui import PLAYGROUND_JS

        start = PLAYGROUND_JS.index("const PG_MODES=")
        end = PLAYGROUND_JS.index(";", start)
        modes = PLAYGROUND_JS[start:end]
        self.assertNotIn("['sim','Try Scenarios']", modes)
        self.assertIn("['map','Career Map']", modes)
        self.assertIn("['insurance','Career Insurance']", modes)
        self.assertIn("['exp','Experience']", modes)

    def test_my_future_hides_lower_exposure_explanation_copy(self):
        html = self.pages["/my-future"]

        self.assertNotIn("Lower predicted E1+E2 task share, not replacement risk.", html)

    def test_profile_working_controls_remain_separate_from_home(self):
        profile = set(PageStructure(self.pages["/my-career"]).ids)
        for required in ("resume-file", "resume-consent", "extract-resume",
                         "profile-form", "passport-review-list",
                         "passport-tag-list", "save-profile"):
            self.assertIn(required, profile)
        self.assertNotIn("resume-file", PageStructure(self.pages["/"]).ids)
        self.assertIn("/api/profile/extract", self.pages["/my-career"])
        self.assertIn("X-CSRF-Token", self.pages["/my-career"])

    def test_manual_passport_skill_add_searches_esco_automatically(self):
        from futuretwin_pages import PROFILE_JS
        start = PROFILE_JS.index("async function addSkill(){")
        end = PROFILE_JS.index("$('skill-add-btn').addEventListener", start)
        add_skill = PROFILE_JS[start:end]
        self.assertIn("refreshSkillMatches(r,li,button)", add_skill)
        self.assertIn("$('skill-add-btn').addEventListener('click',addSkill)", PROFILE_JS)
        self.assertIn("if(e.key==='Enter'){e.preventDefault();addSkill()}", PROFILE_JS)

        match_start = PROFILE_JS.index("async function refreshSkillMatches")
        match_end = PROFILE_JS.index("async function saveProfileState", match_start)
        match_function = PROFILE_JS[match_start:match_end]
        self.assertIn("fetch('/api/profile/match'", match_function)
        self.assertIn("r.selected_esco_uri=null", match_function)
        self.assertIn("r.esco_candidates.length?'Search again':'Find matches'", PROFILE_JS)

    def test_all_inline_javascript_parses(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, (route, html) in enumerate(self.pages.items()):
                with self.subTest(route=route):
                    path = Path(directory) / f"page-{index}.js"
                    path.write_text("\n;\n".join(PageStructure(html).scripts))
                    result = subprocess.run(
                        ["node", "--check", str(path)], capture_output=True,
                        text=True, timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_resume_replacement_preserves_existing_confirmations(self):
        from futuretwin_pages import PROFILE_JS
        start = PROFILE_JS.index("function keepConfirmed(d){")
        end = PROFILE_JS.index("function renderProfile(data){", start)
        function = PROFILE_JS[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const rows=[
 {value:'Python',evidence:'Original Python evidence',selected_esco_uri:'python',
  confirmed:true,esco_candidates:[{uri:'python',label:'Python'}]},
 {value:'machine learning',evidence:'Original ML evidence',
  selected_esco_uri:'ml',confirmed:true,esco_candidates:[{uri:'ml'}]}];
const context={rows,result:null};
vm.runInNewContext(FUNCTION+`
 result=keepConfirmed({skills:[
  {value:'Python',selected_esco_uri:null,confirmed:false},
  {value:'SQL',selected_esco_uri:null,confirmed:false}]});`,context);
assert.equal(context.result.skills.length,3);
assert.equal(context.result.skills[0].selected_esco_uri,'python');
assert.equal(context.result.skills[0].confirmed,true);
assert.equal(context.result.skills[0].evidence,'Original Python evidence');
assert.equal(context.result.skills[1].selected_esco_uri,'ml');
assert.equal(context.result.skills[1].confirmed,true);
assert.equal(context.result.skills[2].value,'SQL');
assert.equal(context.result.skills[2].confirmed,false);
"""
        result = subprocess.run(
            ["node", "-e", script.replace("FUNCTION", json.dumps(function), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_impact_metadata_requires_expanding_details(self):
        from futuretwin_pages import CAREER_JS
        start = CAREER_JS.index("function addImpactMeta(")
        end = CAREER_JS.index("function renderOccupation(", start)
        helpers = CAREER_JS[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const context={URL,result:null};
vm.runInNewContext(`
 function node(tag,cls,text){
  return {tag,className:cls,text:text||'',childNodes:[],
   appendChild(n){this.childNodes.push(n);return n}};
 }
`+HELPERS+`
 result=renderImpactTaskGroup({
  task:'Join data tables',benchmark:'Synthetic benchmark',
  model:'Synthetic evaluated model',score:93,date_value:'2026-01-01',
  skills:[{skill:'data modelling',skill_uri:'synthetic-skill'}]});
`,context);
function texts(n,expanded=false){
 if(n.tag==='details'&&!expanded)
  return n.childNodes.filter(x=>x.tag==='summary').map(x=>texts(x)).join(' ');
 return [n.text,...n.childNodes.map(x=>texts(x,expanded))].join(' ');
}
const visible=texts(context.result),all=texts(context.result,true);
assert(visible.includes('Join data tables'));
assert(visible.includes('data modelling'));
assert(visible.includes('Possible task relationship'));
assert(visible.includes('View Details'));
for(const value of ['Synthetic benchmark','Synthetic evaluated model','93','2026-01-01']){
 assert(!visible.includes(value),'Metadata was exposed: '+value);
 assert(all.includes(value),'Evidence was lost: '+value);
}
"""
        result = subprocess.run(
            ["node", "-e", script.replace("HELPERS", json.dumps(helpers), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_resume_skill_list_is_not_presented_as_work_experience(self):
        from futuretwin_pages import PROFILE_JS
        start = PROFILE_JS.index("function experienceRows(){")
        end = PROFILE_JS.index("function drawExperience(){", start)
        function = PROFILE_JS[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const common={confirmed:true,selected_esco_uri:'synthetic-skill'};
const context={rows:[
 {...common,value:'Python',origin:'explicit',evidence:'Skills: Python'},
 {...common,value:'Built a dashboard',origin:'activity_suggestion',
  evidence:'Project: Built a dashboard'},
 {...common,value:'Mentoring',source:'experience',evidence:'I mentored interns'},
 {...common,value:'Draft activity',origin:'activity_suggestion',
  evidence:'An unconfirmed draft',confirmed:false}],result:null};
vm.runInNewContext(FUNCTION+'result=experienceRows();',context);
assert.equal(context.result.length,2);
assert.equal(context.result[0].value,'Built a dashboard');
assert.equal(context.result[1].value,'Mentoring');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("FUNCTION", json.dumps(function), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_career_detail_reuses_playground_graph_source(self):
        from futuretwin_playground_ui import CAREER_MAP_JS, PLAYGROUND_JS
        self.assertIn(CAREER_MAP_JS[:400], PLAYGROUND_JS)
        self.assertIn("function pgGraph(", self.pages["/career"])
        self.assertIn("cr-map-host", self.pages["/career"])


if __name__ == "__main__":
    unittest.main()
