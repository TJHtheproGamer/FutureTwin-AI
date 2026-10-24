"""Home uses real map coverage and links directly to the selected SDG."""
import subprocess
import unittest

from futuretwin_site_ui import HOME_DASH_BODY, HOME_DASH_JS
from futuretwin_sdg_map_page import SDG_MAP_JS


class HomeSdgPreviewTests(unittest.TestCase):
    def run_js(self, script):
        result = subprocess.run(
            ["node", "-e", script], capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_preview_counts_and_goal_links_come_from_existing_map(self):
        start = HOME_DASH_JS.index("function renderHomeSdgMap(data){")
        end = HOME_DASH_JS.index("async function loadSdgMap()", start)
        function = HOME_DASH_JS[start:end]
        self.run_js(
            "const assert=require('node:assert/strict');const esc=s=>String(s);\n"
            + function + r"""
const nodes=[{type:'occupation'},{type:'skill'},{type:'skill'}];
const html=renderHomeSdgMap({goals:[
 {code:'3',color:'#4C9F38'},{code:'6',color:'#26BDE2'}
],nodes});
assert.ok(html.includes('2 goals'));
assert.ok(html.includes('>1 career</span>'));
assert.ok(html.includes('2 skills'));
assert.ok(html.includes('href="/sdg-map?goal=6"'));
assert.ok(html.includes('Clean Water and Sanitation'));
assert.ok(html.includes('#26BDE2'));
assert.ok(!html.includes('href="/sdg-map?goal=7"'),'do not invent missing goal links');
assert.ok(html.includes('AI-suggested and reviewed'));
assert.throws(()=>renderHomeSdgMap({}),/unavailable/);
"""
        )
        self.assertIn('id="home-sdg"', HOME_DASH_BODY)
        self.assertIn('href="/sdg-map"', HOME_DASH_BODY)
        # Load independently of profile availability, before the profile request.
        init = HOME_DASH_JS.split("async function init(){", 1)[1]
        self.assertLess(init.index("loadSdgMap()"), init.index("await ftLoad()"))

    def test_goal_link_opens_filtered_map(self):
        prefix = SDG_MAP_JS.split("document.addEventListener('click'")[0]
        setup = r"""
const assert=require('node:assert/strict'),hosts={};
global.document={getElementById:id=>hosts[id]||(hosts[id]={})};
global.matchMedia=()=>({matches:true});
global.location={search:'?goal=6'};
global.fetch=async()=>({ok:true,json:async()=>({
 goals:[{code:'6',title:'Clean water',color:'#26BDE2'}],
 nodes:[{id:'skill:test',uri:'test',type:'skill',label:'Test water',
 x:.5,y:.5,primary_goal_code:'6',goal_codes:['6'],review_statuses:[]}],
 links:[],coverage:{}
})});
"""
        self.run_js(setup + prefix + r"""
resize=()=>{};setupChips=()=>{};syncChips=()=>{};renderBrowse=()=>{};
renderPanel=()=>{};draw=()=>{};go=()=>{};queue=()=>{};
load().then(()=>{
 assert.equal(S.goal,'6');
 assert.equal(S.vis.length,1);
 assert.equal(S.vis[0].label,'Test water');
}).catch(e=>{console.error(e);process.exitCode=1});
})();""")


if __name__ == "__main__":
    unittest.main()
