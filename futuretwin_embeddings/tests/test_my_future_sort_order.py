"""Verify the visible My Future ranking controls and their order."""
import ast
import json
from pathlib import Path
import subprocess
import unittest


class MyFutureSortOrderTests(unittest.TestCase):
    def test_early_profile_status_copy_is_suppressed(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_my_future_page.py"
        tree = ast.parse(path.read_text())
        page_script = next(
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and "function recommendationMessage(data){" in node.value
        )
        start = page_script.index("function recommendationMessage(data){")
        end = page_script.index("function bmText", start)
        message_function = page_script[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const context={};
vm.runInNewContext(SOURCE+'\n;globalThis.recommendationMessage=recommendationMessage;',context);
assert.equal(context.recommendationMessage({
 ranking:{effective:'best_match',best_match:{profile:{status:'early'}}}
}), '');
console.log('Early-profile status copy suppression: passed');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", json.dumps(message_function), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("statusNode.textContent=statusMessage;statusNode.hidden=!statusMessage;", page_script)

    def test_sort_controls_show_only_best_match_and_lower_exposure(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_my_future_page.py"
        tree = ast.parse(path.read_text())
        page_script = next(
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and "function mfDrawSort(rank){" in node.value
        )
        start = page_script.index("let mfSort='best_match';")
        end = page_script.index("function renderRecommendations(data){", start)
        draw_sort = page_script[start:end]
        self.assertNotIn("ftRankingEvidence(rank)", draw_sort)
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
function element(tag){
 return {tag,textContent:'',children:[],attributes:{},
  setAttribute(k,v){this.attributes[k]=v},
  addEventListener(){},
  appendChild(child){this.children.push(child)},
  replaceChildren(){this.children=[]}
 };
}
const host=element('host');
const context={document:{createElement:element},$:()=>host,
 state:{recommendationsExpanded:false},loadRecommendations(){},
 ftRankingEvidence:()=>null};
vm.runInNewContext(SOURCE+'\n;globalThis.mfDrawSort=mfDrawSort;',context);
context.mfDrawSort({effective:'best_match',options:[
 {id:'lower_exposure',label:'Lower AI Exposure',available:true},
 {id:'growing_jobs',label:'Growing Jobs',available:false,reason:'No evidence'},
 {id:'purpose_alignment',label:'Purpose Alignment',available:true},
 {id:'best_match',label:'Best Match',available:true}
]});
const buttons=host.children[0].children;
assert.deepEqual(buttons.map(button=>button.textContent),
 ['Best Match','Lower AI Exposure']);
assert.equal(buttons[0].attributes['aria-pressed'],'true');
context.mfDrawSort({requested:'best_match',effective:'best_match',options:[
 {id:'best_match',label:'Best Match',available:true},
 {id:'lower_exposure',label:'Lower AI Exposure',available:false,reason:'No evidence'},
 {id:'purpose_alignment',label:'Purpose Alignment',available:true}
]});
assert.equal(host.children[0].children.length,2);
assert.equal(host.children[0].children[0].attributes['aria-pressed'],'true');
assert.ok(!host.children.some(x=>x.attributes.role==='status'));
console.log('My Future excludes Purpose Alignment and Growing Jobs: passed');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", json.dumps(draw_sort), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_removed_purpose_sort_has_no_unavailable_message_or_priorities_link(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_my_future_page.py"
        tree = ast.parse(path.read_text())
        page_script = next(
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and "function mfDrawSort(rank){" in node.value
        )
        start = page_script.index("let mfSort='best_match';")
        end = page_script.index("function renderRecommendations(data){", start)
        draw_sort = page_script[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
function element(tag){
 return {tag,textContent:'',children:[],attributes:{},
  setAttribute(k,v){this.attributes[k]=v},
  addEventListener(){},
  appendChild(child){this.children.push(child)},
  replaceChildren(){this.children=[]}
 };
}
const host=element('host');
const context={document:{createElement:element},$:()=>host,
 state:{recommendationsExpanded:false},loadRecommendations(){}};
vm.runInNewContext(SOURCE+'\n;globalThis.mfDrawSort=mfDrawSort;',context);
context.mfDrawSort({requested:'purpose_alignment',effective:'best_match',
 options:[
  {id:'best_match',label:'Best Match',available:true},
  {id:'lower_exposure',label:'Lower AI Exposure',available:false,reason:'No evidence'},
  {id:'purpose_alignment',label:'Purpose Alignment',available:false,
   reason:'Choose SDG priorities before using Purpose Alignment.'}
 ]});
const buttons=host.children[0].children;
assert.equal(buttons.length,2);
assert.ok(!host.children.some(x=>x.id==='mf-reason-purpose_alignment'));
assert.equal(host.children.filter(x=>x.textContent.includes('Showing Best Match')).length,0);
context.mfDrawSort({requested:'purpose_alignment',effective:'best_match',
 options:[
  {id:'best_match',label:'Best Match',available:true},
  {id:'purpose_alignment',label:'Purpose Alignment',available:false,
   reason:'Confirm Skills Passport skills before sorting career matches.'}
 ]});
assert.equal(host.children[0].children.length,1);
assert.ok(!host.children.some(x=>x.id==='mf-reason-purpose_alignment'));
console.log('Removed purpose controls stay absent even in legacy payloads: passed');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", json.dumps(draw_sort), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
