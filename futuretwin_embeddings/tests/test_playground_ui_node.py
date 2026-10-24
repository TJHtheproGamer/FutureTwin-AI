"""Execute the real browser helpers with a minimal DOM-free Node harness."""
import ast
import json
from pathlib import Path
import subprocess
import unittest


class PlaygroundClientTests(unittest.TestCase):
    def test_actual_map_and_batch_plan_helpers(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_playground_ui.py"
        tree = ast.parse(path.read_text())
        js = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "PLAYGROUND_JS"
                          for t in n.targets))
        self.assertNotIn("Edit compared careers", js)
        self.assertNotIn('id="pg-cmp"', js)
        self.assertNotIn("m.notice", js)
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const context=vm.createContext({console,Set,Map,window:{innerWidth:1200},
  document:{getElementById:()=>null},$:()=>null,
  esc:s=>String(s??''),roadmapBusy:false,insuranceBusy:false,
   taskExamples:()=>'<p>Task examples</p>',
  stressList:rows=>'<ul>'+rows.join('|')+'</ul>',
  renderBenchmarkEvidence:()=>'',renderWorkforceContext:()=>'',
  state:{roadmap_goals:{target:['old']},roadmap_progress:{target:['old']},
    activeTab:'discover',learningCareerUri:null,confirmed_skills:[],
    stress:{scenario:'slower'}},
  loadDetails:u=>{context.loaded=u},saveState:async()=>true});
vm.runInContext(SOURCE + '\n;globalThis.api={pg,pgGraph,pgPanel,pgVisible,pgAddSelected,pgPixels,pgExp,pgSim};',context);
const {pg,pgGraph,pgPanel,pgVisible,pgAddSelected,pgPixels,pgExp,pgSim}=context.api;
const map={occupation:{uri:'target',label:'Target'},
 occupations:[{uri:'target',label:'Target'},{uri:'other',label:'Other'}],
 skills:[
 {uri:'one',label:'One',confirmed:false,relation:'essential',
  connections:[{occupation_uri:'target',relation:'essential'}]},
 {uri:'extra',label:'Extra',confirmed:true,relation:null,
  connections:[{occupation_uri:'other',relation:'optional'}]}]};
// No imaginary centre-to-skill link for an alternative-only confirmed skill.
pg.sel='extra';
let html=pgGraph(map,map.skills);
assert.equal((html.match(/<line /g)||[]).length,2); // One real target + one alt.
assert(!html.includes('aria-pressed="null"'));
assert(html.includes('Listed for 1 of 1 displayed alternative careers'));
 assert(pgPanel(map).includes('Listed for: Other (optional).'));
 assert(!pgPanel(map).includes('Essential skill to explore'));
pg.filter='confirmed';
assert.equal(pgVisible(map).length,1);
pg.filter='all';pg.q='one';
assert.equal(pgVisible(map).length,1);
pg.q='';
// Contrast transformation uses the actual helper, including a flat-image guard.
const exercise={status:'available',image:{width:2,height:1,pixels:[118,122]}};
assert.deepEqual(Array.from(pgPixels(exercise,0).out),[118,122]);
assert.deepEqual(Array.from(pgPixels(exercise,100).out),[0,255]);
assert.equal(pgPixels({image:{pixels:[122,122]}},100).flat,true);
assert.deepEqual(Array.from(pgPixels({image:{pixels:[122,122]}},100).out),[122,122]);
assert(!pgExp({career_experience:{status:'unavailable'}}).includes('Start exercise'));
const dataExercise={status:'available',title:'Check a small data sample',
  summary:'Spot issues before reporting.',question:'What should you verify?',
  activity:{type:'table',caption:'Synthetic order sample',
    headers:['Order ID','Date','Units'],rows:[['105','6 Jun','18'],['105','6 Jun','18']]},
  source:{occupation:{uri:'data-analyst'},skill:{label:'data quality assessment'}},
  available_examples:[{occupation_uri:'data-analyst',
    occupation_label:'data analyst',skill_label:'data quality assessment'}],
  choices:[{id:'verify',label:'Check the source records.',supported:true,feedback:'Verify first.'}]};
pg.exp={step:0,strength:50,choice:null};
let expHtml=pgExp({career_experience:dataExercise});
assert(expHtml.includes('Skill focus:</strong> data quality assessment'));
assert(expHtml.includes('Available practice skills (1)'));
assert(expHtml.includes('href="/my-future?career=data-analyst&amp;mode=exp"'));
pg.exp.step=1;expHtml=pgExp({career_experience:dataExercise});
assert(expHtml.includes('Synthetic order sample'));
assert(expHtml.includes('<th scope="col">Order ID</th>'));
assert(expHtml.includes('Step 1 of 2'));
pg.exp.step=2;expHtml=pgExp({career_experience:dataExercise});
assert(expHtml.includes('What should you verify?'));
assert(expHtml.includes('Check the source records.'));
// Switching profiles selects real content; step navigation changes the card.
const scenario=(id,count)=>({id,label:id,assumption:'Hypothetical',valuable:[],
 workflow:{steps:Array.from({length:count},(_,i)=>({
  uri:'s'+i,label:'Skill '+i,relation:'essential',assistance:'Assistance '+i
 }))},prepare:['Action for '+id],limitations:[]});
const detail={stress_test:{scenarios:[scenario('slower',1),scenario('faster',3)]}};
pg.step=0;
assert(pgSim(detail,map,'target').includes('Step 1 of 1'));
context.state.stress.scenario='faster';pg.step=1;
const simulator=pgSim(detail,map,'target');
assert(simulator.includes('Step 2 of 3'));
assert(simulator.includes('Assistance 1'));
assert(simulator.includes('Action for faster'));
// Actual UI batch-add path preserves existing goals/progress and deduplicates.
(async()=>{
 pg.picked.add('one');pg.picked.add('old');
 await pgAddSelected('target');
 assert.deepEqual(Array.from(context.state.roadmap_goals.target),['old','one']);
 assert.deepEqual(Array.from(context.state.roadmap_progress.target),['old']);
 assert.equal(context.loaded,'target');
 assert.equal(pg.picked.size,0);
 // Rejected save rolls back, retaining the in-progress selection for retry.
 context.saveState=async()=>false;
 pg.picked.add('next');
 await pgAddSelected('target');
 assert.deepEqual(Array.from(context.state.roadmap_goals.target),['old','one']);
 assert.deepEqual(Array.from(context.state.roadmap_progress.target),['old']);
 assert(pg.picked.has('next'));
 console.log('Map edges, filters, multi-selection, persistence calls, rollback: passed');
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", json.dumps(js), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_career_ranking_controls_use_requested_order_and_exclude_others(self):
        path = Path(__file__).resolve().parents[1] / "futuretwin_intel_ui.py"
        tree = ast.parse(path.read_text())
        js = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "FIND_JS"
                          for t in n.targets))
        start = js.index("function drawSort(){")
        end = js.index("async function runCompare(){", start)
        draw_sort = js[start:end]
        script = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
function node(tag,cls,text=''){return {tag,cls,textContent:text,children:[],attrs:{},
  setAttribute(k,v){this.attrs[k]=v},appendChild(c){this.children.push(c)},
  addEventListener(){}}}
const host={children:[],replaceChildren(){this.children=[]},appendChild(c){this.children.push(c)}};
const recRank={effective:'best_match',options:[
 {id:'purpose_alignment',label:'Purpose Alignment',available:true},
 {id:'growing_jobs',label:'Growing Jobs',available:false},
 {id:'lower_exposure',label:'Lower AI Exposure',available:true},
 {id:'best_match',label:'Best Match',available:true}
]};
const ctx={node,$:()=>host,recRank,ftRankingEvidence:()=>null};
vm.runInNewContext(SOURCE,ctx);ctx.drawSort();
const buttons=host.children[0].children;
assert.deepEqual(buttons.map(b=>b.textContent),
 ['Best Match','Lower AI Exposure','Purpose Alignment']);
assert.equal(buttons[0].attrs['aria-pressed'],'true');
console.log('Ranking control order and Growing Jobs exclusion: passed');
"""
        result = subprocess.run(
            ["node", "-e", script.replace("SOURCE", json.dumps(draw_sort), 1)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
