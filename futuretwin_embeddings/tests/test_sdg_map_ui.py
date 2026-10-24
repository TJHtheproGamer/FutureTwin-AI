"""Browser-independent contracts for the map's evidence and selection state."""
import subprocess
import unittest

from futuretwin_sdg_map_page import SDG_MAP_BODY, SDG_MAP_JS


class SdgMapUiTests(unittest.TestCase):
    def test_browse_list_starts_small_expands_and_resets(self):
        prefix = SDG_MAP_JS.split("document.addEventListener('click'")[0]
        script = prefix + r"""
const assert=require('node:assert/strict');
S.vis=Array.from({length:30},(_,i)=>({
 id:'skill:'+i,label:'Skill '+String(i).padStart(2,'0'),type:'skill',
 primary_goal_code:'6',review_statuses:['unreviewed_candidate']
}));
const count=()=> (document.getElementById('sm-blist').innerHTML.match(/class="sm-bitem"/g)||[]).length;
assert.equal(S.blimit,12);
renderBrowse(true);assert.equal(count(),12);
assert.equal(document.getElementById('sm-bmore').hidden,false);
assert.equal(document.getElementById('sm-bmore').textContent,'Show more (18 left)');
S.blimit+=BROWSE_PAGE_SIZE;renderBrowse(false);assert.equal(count(),24);
renderBrowse(true);assert.equal(count(),12);
S.vis=S.vis.slice(0,5);renderBrowse(true);assert.equal(count(),5);
assert.equal(document.getElementById('sm-bmore').hidden,true);
})();"""
        setup = (
            "const hosts={};global.document={getElementById:id=>hosts[id]||(hosts[id]={})};"
            "global.matchMedia=()=>({matches:true});\n"
        )
        result = subprocess.run(
            ["node", "-e", setup + script],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_filters_passport_and_review_status_stay_exact(self):
        prefix = SDG_MAP_JS.split("document.addEventListener('click'")[0]
        script = prefix + r"""
// Rendering is tested separately; keep this check focused on state contracts.
renderBrowse=()=>{};syncChips=()=>{};go=()=>{};queue=()=>{};renderPanel=()=>{};
const assert=require('node:assert/strict');
const career={id:'occupation:one',uri:'one',type:'occupation',label:'Water worker',
 x:.4,y:.6,primary_goal_code:'4',goal_codes:['4','6'],
 review_statuses:['assistant_desk_reviewed','unreviewed_candidate']};
const skill={id:'skill:one',uri:'skill-one',type:'skill',label:'Test water',
 x:.6,y:.4,primary_goal_code:'6',goal_codes:['6'],
 review_statuses:['unreviewed_candidate']};
S.nodes=[career,skill];
S.statusesByGoal.set('4|occupation:one',['assistant_desk_reviewed']);
S.statusesByGoal.set('6|occupation:one',['unreviewed_candidate']);
layout();recompute();assert.equal(S.vis.length,2);
S.tok=10;setGoal('6');
assert.equal(S.tok,11,'changing goals must invalidate pending entity requests');
assert.equal(S.vis.length,2,'secondary SDG links must not disappear');
assert.equal(displayGoal(career),'6');
assert.equal(bestStatus(career),'unreviewed_candidate',
 'a desk-reviewed link to SDG4 must not mark its SDG6 suggestion as reviewed');
S.sel=career;const token=S.tok;setKind('skill');
assert.equal(S.sel,null);assert.equal(S.tok,token+1);
assert.equal(S.vis.length,1);assert.equal(S.vis[0].type,'skill');
const detail={skills:[
 {uri:'confirmed:one',label:'A skill',relation:'essential'},
 {uri:'unconfirmed:two',label:'Another skill',relation:'optional'}]};
const passport=passportHtml(detail,career,new Set(['confirmed:one','unrelated:skill']));
assert.ok(passport.includes('1 of 2 skills'),'only exact confirmed skill URIs count');
assert.ok(passport.includes('Essential skills: 1 of 1'));
assert.ok(passportHtml({},skill,new Set(['different-uri'])).includes('Not in your passport yet'));
const candidate=connCard({review_status:'unreviewed_candidate',target_code:'6.3',
 target_title:'Improve water quality',reason:'Text overlap only',semantic_score:.99});
assert.ok(candidate.includes('AI suggestion, not verified'));
assert.ok(candidate.includes('AI-suggested reasoning (unverified)'));
assert.ok(!candidate.includes('0.990'),'technical scores must stay behind More details');
assert.equal(safeHttps(''),'','missing evidence must not become a link to this app');
assert.equal(safeHttps('/made-up-source'),'');
assert.equal(safeHttps('javascript:alert(1)'),'');
assert.equal(safeHttps('https://example.org/source'),'https://example.org/source');
console.log('SDG map filtering, stale-request guards, Passport and evidence contracts passed.');
})();"""
        result = subprocess.run(
            ["node", "-e", "global.matchMedia=()=>({matches:true});\n" + script],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_scripts_parse_and_introduction_is_plain_language(self):
        result = subprocess.run(
            ["node", "--check"], input=SDG_MAP_JS,
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "Explore how careers and skills connect to the 17 Sustainable Development Goals.",
            SDG_MAP_BODY,
        )
        self.assertIn("Reset View", SDG_MAP_BODY)
        self.assertIn('id="sm-blist"', SDG_MAP_BODY)


if __name__ == "__main__":
    unittest.main()
