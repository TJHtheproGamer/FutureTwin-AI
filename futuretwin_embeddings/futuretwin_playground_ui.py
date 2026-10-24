"""Career Playground UI: ESCO map, skill selections and practice interactions.

PLAYGROUND_CSS is appended to the My Future page CSS; PLAYGROUND_JS is injected
inside the page IIFE at the /*__PLAYGROUND_JS__*/ placeholder and reuses its
request/saveState/loadDetails/saveInsuranceSelection/insuranceComparison helpers.
"""

PLAYGROUND_CSS = r'''
.pg{margin:16px 0 4px;border:1px solid var(--line2);border-radius:15px;background:var(--paper);padding:16px;max-width:100%;overflow:hidden}
.pg-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.pg-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.pg-head h3{font:700 17px var(--body);letter-spacing:-.03em;margin:0}
.pg-head p{margin:3px 0 0;font-size:12px;color:var(--muted)}
.pg-seg{display:inline-flex;gap:3px;padding:3px;background:#eeeae0;border-radius:10px}
.pg-seg button{border:0;background:transparent;color:var(--muted);font-weight:700;font-size:12px;border-radius:8px;padding:6px 10px}
.pg-seg button[aria-pressed="true"]{background:var(--paper);color:var(--harbor);box-shadow:0 1px 3px #14263a14}
.pg button:focus-visible,.pg input:focus-visible,.pg summary:focus-visible{outline:2px solid var(--harbor);outline-offset:2px}
.pg-count{font-size:12px;color:var(--ink2);margin:10px 0 6px}
.pg-stage{position:relative;width:100%;aspect-ratio:16/11;background:radial-gradient(circle at 50% 44%,#f1f5f1,#faf7f0 70%);border-radius:13px;border:1px solid var(--line2);overflow:hidden}
.pg-stage svg{position:absolute;inset:0;width:100%;height:100%}
.pg-edge{stroke:#cfd8d1;stroke-width:1.2;vector-effect:non-scaling-stroke;transition:stroke .2s,opacity .2s}
.pg-edge.on{stroke:var(--harbor);stroke-width:2.4}
.pg-edge.dim{opacity:.25}
.pg-elabel{position:absolute;transform:translate(-50%,-50%);font-size:10px;font-weight:700;color:var(--harbor);background:var(--paper);border:1px solid var(--line2);border-radius:99px;padding:1px 6px;pointer-events:none}
.pg-node{position:absolute;transform:translate(-50%,-50%);max-width:25%;border:1px solid var(--line);background:#fffefa;color:var(--ink);border-radius:99px;padding:6px 10px;font-size:11px;font-weight:600;line-height:1.25;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;transition:background .18s,border-color .18s,opacity .18s}
.pg-node.confirmed{background:var(--sage-soft);border-color:#a7bdaf;color:#2f5a45}
.pg-node.explore{border-style:dashed}
.pg-node.alt{background:var(--paper2);border-radius:10px;color:var(--harbor);max-width:calc(100% / var(--n,3) - 2%)}
.pg-node.alt.linked{border-color:var(--harbor);background:var(--harbor-soft)}
.pg-node.center{max-width:30%;white-space:normal;text-align:center;background:var(--harbor);border-color:var(--harbor);color:#fbf8f1;font-size:13px;font-weight:700;border-radius:14px;padding:10px 14px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical}
.pg-node[aria-pressed="true"]{border-color:var(--harbor);box-shadow:0 0 0 3px #2d5a7a30;background:var(--harbor-soft);color:var(--harbor)}
.pg-node.dim{opacity:.4}
.pg-legend{display:flex;gap:12px;flex-wrap:wrap;font-size:11px;color:var(--muted);margin:8px 0 0}
.pg-panel{margin-top:10px;border:1px solid var(--line2);border-radius:12px;padding:12px 13px;background:#fffefa;font-size:12px;color:var(--ink2)}
.pg-panel h4{font:700 14px var(--body);margin:0 0 4px;color:var(--ink)}
.pg-panel p{margin:3px 0}
.pg-table-wrap{overflow-x:auto;margin:9px 0}
.pg-table{border-collapse:collapse;width:100%;font-size:12px}
.pg-table th,.pg-table td{border:1px solid var(--line2);padding:6px 8px;text-align:left}
.pg-table th{background:var(--paper2);font-weight:700}
.pg-scenario{margin:9px 0;padding:10px;border:1px solid var(--line2);border-radius:8px;background:var(--paper2)}
.pg-filter{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:10px 0}
.pg-filter input{flex:1;min-width:140px;border:1px solid var(--line);background:#fffefa;border-radius:10px;padding:8px 11px;font:inherit;font-size:13px;color:var(--ink)}
.pg-list{display:grid;gap:6px;margin:0;padding:0;list-style:none}
.pg-row{display:flex;justify-content:space-between;gap:8px;align-items:center;width:100%;text-align:left;border:1px solid var(--line2);background:var(--paper);border-radius:10px;padding:9px 11px;font-size:13px;color:var(--ink)}
.pg-row small{display:block;font-size:10px;color:var(--muted);margin-top:1px}
.pg-row[aria-pressed="true"]{border-color:var(--harbor);background:var(--harbor-soft)}
.pg-sub{font:700 12px var(--body);color:var(--muted);margin:12px 0 6px}
.pg-ins h3{font:700 16px var(--body);margin:18px 0 2px;letter-spacing:-.03em}
.pg-ins>p,.pg-ins-sec>p{font-size:12px;color:var(--muted);margin:0 0 8px}
.pg-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr));gap:8px}
.pg-card{border:1px solid var(--line2);border-radius:11px;background:var(--paper);padding:10px;display:grid;gap:6px;align-content:start;min-width:0}
.pg-card.revealed{border-color:var(--harbor)}
.pg-card.picked{background:#f1f6f1;border-color:#a7bdaf}
.pg-card-main{border:0;background:none;text-align:left;padding:0;color:var(--ink);font:inherit;min-width:0}
.pg-card-main strong{display:block;font-size:13px;overflow-wrap:anywhere}
.pg-card-main span{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:11px;color:var(--muted);margin-top:2px}
.pg-card-foot{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.pg-pick{border:1px solid var(--line);background:#fffefa;color:var(--harbor);border-radius:8px;padding:5px 9px;font-size:11px;font-weight:700}
.pg-pick[aria-pressed="true"]{background:var(--sage);border-color:var(--sage);color:#fbf8f1}
.pg-pick[disabled]{opacity:.6}
.pg-links{font-size:11px;color:var(--ink2);background:var(--paper2);border-radius:8px;padding:7px 9px}
.pg-bar{position:sticky;bottom:8px;display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:12px;padding:9px 12px;background:var(--paper);border:1px solid var(--line);border-radius:12px;box-shadow:0 6px 20px #14263a14;font-size:12px;z-index:3}
.pg-more{margin-top:8px}
@media(max-width:640px){.pg{padding:12px}.pg-stage{aspect-ratio:3/4}.pg-node{font-size:10px;padding:5px 7px;max-width:30%}.pg-node.center{font-size:11px;max-width:34%}.pg-bar{flex-direction:column;align-items:stretch}}

.pg-modes{margin-top:10px;max-width:100%;overflow-x:auto}
.pg-hyp{font-size:12px;color:var(--ink2);margin:10px 0}
.pg-prep{margin:7px 0;border:1px solid var(--line2);border-radius:9px;padding:8px 11px;font-size:12px}
.pg-prep summary{cursor:pointer;font-weight:600;color:var(--harbor)}
.pg-prep p{margin:8px 0 0;color:var(--ink2)}
.pg-steps{display:flex;gap:6px;list-style:none;margin:8px 0;padding:0}
.pg-steps button{width:34px;height:34px;border-radius:99px;border:1px solid var(--line);background:#fffefa;color:var(--ink2);font-weight:700}
.pg-steps button[aria-pressed="true"]{background:var(--harbor);border-color:var(--harbor);color:#fbf8f1}
.pg-panel small{color:var(--muted);font-size:10px}
.pg-grids{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
.pg-grids figure{margin:0}.pg-grids figcaption{font-size:11px;font-weight:700;margin-bottom:4px}
.pg-px{width:100%;height:auto;border:1px solid var(--line);border-radius:6px;display:block}
.pg-range{display:block;font-size:12px;font-weight:700;margin:10px 0 4px}
#pg-strength{width:100%;accent-color:var(--harbor)}
.pg-choices{border:0;padding:0;margin:10px 0 0;display:grid;gap:6px}
.pg-choice{display:flex;gap:8px;align-items:flex-start;border:1px solid var(--line2);border-radius:10px;padding:9px;font-size:12px}
.pg-choice:has(input:checked){border-color:var(--harbor);background:var(--harbor-soft)}
.pg-fb{margin-top:10px;background:#edf3f1;border-left:3px solid var(--harbor);padding:9px 11px;border-radius:0 10px 10px 0;font-size:12px}
.pg-fb p{margin:3px 0 0}
@media(max-width:400px){.pg-grids{grid-template-columns:1fr}}
@media(max-width:640px){.pg-modes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));width:100%;overflow:visible}.pg-modes button{min-width:0}}
@media(prefers-reduced-motion:reduce){.pg *{transition:none!important;animation:none!important}}
'''

PLAYGROUND_JS = r'''
const pg={view:null,sel:null,filter:'all',q:'',limit:12,picked:new Set(),uri:null,detail:null,reveal:null,focus:null,more:false,mode:'map',step:0,exp:{step:0,strength:50,choice:null}};
const pgLive=t=>{const n=$('pg-live');if(n)n.textContent=t};
const pgAddingSkills=new Set();
let pgSkillMessage='',pgSkillError=false;
const pgAlts=m=>(m.occupations||[]).filter(o=>o.uri!==m.occupation.uri);
const pgRel=(s,m)=>{const c=(s.connections||[]).find(x=>x.occupation_uri===m.occupation.uri);return c?(c.relation==='optional'?'optional':'essential'):null};
const pgAltConns=(s,m)=>(s.connections||[]).filter(c=>c.occupation_uri!==m.occupation.uri&&(m.occupations||[]).some(o=>o.uri===c.occupation_uri));
const pgSkillState=(s,m)=>{const r=m?pgRel(s,m):(s.relation||null);return s.confirmed?('Confirmed skill'+(m&&!r?', not listed for this career':'')):(r==='optional'?'Optional skill to explore':'Essential skill to explore')};
function pgLookup(m){const o={};(m.skills||[]).forEach(s=>{o[s.uri]=s});return o}
function pgVisible(m){
  const q=pg.q.trim().toLowerCase();
  return (m.skills||[]).filter(s=>(pg.filter==='all'||(pg.filter==='confirmed'?s.confirmed:!s.confirmed))&&(!q||s.label.toLowerCase().includes(q)));
}
function pgGraphSkills(m){
  const all=pgVisible(m),top=all.slice(0,9);
  if(pg.sel&&!top.some(s=>s.uri===pg.sel)){const s=all.find(x=>x.uri===pg.sel);if(s){top[top.length>=9?8:top.length]=s}}
  return {top,total:all.length};
}
function pgConnLabel(m,c){const o=(m.occupations||[]).find(x=>x.uri===c.occupation_uri);return (o?o.label:'Career')+' ('+(c.relation==='optional'?'optional':'essential')+')'}
function pgGraph(m,skills){
  const alts=pgAlts(m),sel=skills.find(s=>s.uri===pg.sel),cx=50,cy=44;
  const sp=skills.map((s,i)=>{const a=(-90+i*360/skills.length)*Math.PI/180;return {s,x:cx+38*Math.cos(a),y:cy+34*Math.sin(a)}});
  const ap=alts.map((o,i)=>({o,x:(i+.5)*100/alts.length,y:92}));
  const conn=sel?Object.fromEntries(pgAltConns(sel,m).map(c=>[c.occupation_uri,c])):{};
  let svg='',labels='',nodes='';
  sp.forEach(p=>{const rel=pgRel(p.s,m);if(!rel)return;const on=sel&&p.s.uri===sel.uri;svg+='<line class="pg-edge'+(on?' on':(sel?' dim':''))+'" x1="'+cx+'" y1="'+cy+'" x2="'+p.x+'" y2="'+p.y+'"/>';
    if(on)labels+='<span class="pg-elabel" style="left:'+(cx+p.x)/2+'%;top:'+(cy+p.y)/2+'%">'+rel+'</span>'});
  if(sel){const sx=sp.find(p=>p.s.uri===sel.uri);ap.forEach(a=>{const c=conn[a.o.uri];if(c&&sx){svg+='<line class="pg-edge on" x1="'+sx.x+'" y1="'+sx.y+'" x2="'+a.x+'" y2="'+a.y+'"/>';labels+='<span class="pg-elabel" style="left:'+(sx.x+a.x)/2+'%;top:'+(sx.y+a.y)/2+'%">'+(c.relation==='optional'?'optional':'essential')+'</span>'}})}
  nodes+='<button type="button" class="pg-node center" style="left:'+cx+'%;top:'+cy+'%" data-pg-center aria-label="Selected career: '+esc(m.occupation.label)+'. Press to clear skill highlight.">'+esc(m.occupation.label)+'</button>';
  sp.forEach(p=>{const s=p.s,n=pgAltConns(s,m).length;nodes+='<button type="button" class="pg-node skill '+(s.confirmed?'confirmed':'explore')+(sel&&sel.uri!==s.uri?' dim':'')+'" style="left:'+p.x+'%;top:'+p.y+'%" data-pg-skill="'+esc(s.uri)+'" aria-pressed="'+(!!sel&&sel.uri===s.uri)+'" title="'+esc(s.label)+'" aria-label="'+esc(s.label)+'. '+pgSkillState(s,m)+'. Listed for '+n+' of '+alts.length+' displayed alternative careers.">'+esc(s.label)+'</button>'});
  ap.forEach(a=>{const linked=!!conn[a.o.uri];nodes+='<button type="button" class="pg-node alt'+(linked?' linked':'')+(sel&&!linked?' dim':'')+'" style="left:'+a.x+'%;top:'+a.y+'%;--n:'+alts.length+'" data-pg-occ="'+esc(a.o.uri)+'" title="'+esc(a.o.label)+'" aria-label="Alternative career: '+esc(a.o.label)+(linked?', shares the selected skill':'')+'. Press to load this career.">'+esc(a.o.label)+'</button>'});
  return '<div class="pg-stage"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'+svg+'</svg>'+labels+nodes+'</div>';
}
function pgList(m){
  const all=pgVisible(m),show=all.slice(0,pg.limit),alts=pgAlts(m);
  return '<ul class="pg-list" aria-label="Skills">'+(show.length?show.map(s=>'<li><button type="button" class="pg-row" data-pg-skill="'+esc(s.uri)+'" aria-pressed="'+(pg.sel===s.uri)+'"><span>'+esc(s.label)+'<small>'+pgSkillState(s,m)+'</small></span><small>'+pgAltConns(s,m).length+' alt. careers</small></button></li>').join(''):'<li class="myf-empty">No skills match this filter.</li>')+'</ul>'+(all.length>show.length?'<button type="button" class="btn btn-ghost btn-sm pg-more" data-pg-more>Show '+Math.min(12,all.length-show.length)+' more ('+(all.length-show.length)+' left)</button>':'')+
   '<p class="pg-sub">Alternative careers</p><ul class="pg-list">'+(alts.length?alts.map(o=>'<li><button type="button" class="pg-row" data-pg-occ="'+esc(o.uri)+'"><span>'+esc(o.label)+'<small>Load this career</small></span></button></li>').join(''):'<li class="myf-empty">No comparison careers selected.</li>')+'</ul>';
}
function pgPanel(m){
  const s=(m.skills||[]).find(x=>x.uri===pg.sel);
  if(!s)return '<div class="pg-panel"><p>Select a skill to see which compared careers list the same ESCO skill.</p></div>';
  const cs=pgAltConns(s,m),rel=pgRel(s,m),inPlan=(state.roadmap_goals[m.occupation.uri]||[]).includes(s.uri);
   return '<div class="pg-panel"><h4>'+esc(s.label)+'</h4><p>'+(cs.length?'Listed for: '+cs.map(c=>esc(pgConnLabel(m,c))).join(', ')+'.':'Not listed for the displayed alternative careers.')+'</p><div class="pg-card-foot" style="margin-top:8px">'+(s.confirmed?'<button type="button" class="btn btn-ghost btn-sm" data-pg-passport="'+esc(s.label)+'">View in Passport</button>':!rel?'':'<button type="button" class="btn btn-ghost btn-sm" data-pg-passport="'+esc(s.label)+'">I already have this skill</button>'+(inPlan?'<span class="myf-chip">In your learning plan</span>':'<button type="button" class="pg-pick" data-pg-pick="'+esc(s.uri)+'" aria-pressed="'+pg.picked.has(s.uri)+'">'+(pg.picked.has(s.uri)?'Selected':'Select to add')+'</button>'))+'</div></div>';
}
function pgCard(p,m,goals,done){
  const inPlan=goals.includes(p.uri),rev=pg.sel===p.uri,picked=pg.picked.has(p.uri),sk=pgLookup(m)[p.uri];
  const known=state.confirmed_skills.some(s=>s.uri===p.uri),adding=pgAddingSkills.has(p.uri);
  const links=rev?'<div class="pg-links">'+((sk&&pgAltConns(sk,m)).length?'Listed for: '+pgAltConns(sk,m).map(c=>esc(pgConnLabel(m,c))).join(', '):'Not listed for the displayed alternative careers.')+'</div>':'';
  const why=p.why||{};
  const info='<details class="myf-disclosure" style="margin-top:0;padding-top:6px"><summary>Why this?</summary><div class="myf-disclosure-body">'+(p.description?'<p>'+esc(p.description)+'</p>':'')+'<p>Relation in occupation data: '+(p.relation==='optional'?'optional':'essential')+'. Not an employer requirement.</p>'+(why.diversity_note?'<p>'+esc(why.diversity_note)+'</p>':'')+((p.other_careers||[]).length?'<p>Also in: '+p.other_careers.map(c=>esc(c.label||c)).join(', ')+'</p>':'')+'</div></details>';
  return '<article class="pg-card'+(rev?' revealed':'')+(picked?' picked':'')+'"><button type="button" class="pg-card-main" data-pg-skill="'+esc(p.uri)+'" aria-pressed="'+!!rev+'"><strong>'+esc(p.label)+'</strong></button>'+links+'<div class="pg-card-foot">'+(inPlan?'<span class="myf-chip">'+(done.includes(p.uri)?'Step completed':'In your plan')+'</span>':'<button type="button" class="pg-pick" data-pg-pick="'+esc(p.uri)+'" aria-pressed="'+picked+'">'+(picked?'Selected':'Select')+'</button>')+'<button type="button" class="myf-link" data-pg-have="'+esc(p.uri)+'"'+(known||adding?' disabled':'')+'>'+(known?'In Passport':adding?'Saving…':'I have this')+'</button></div>'+info+'</article>';
}
async function pgHaveSkill(uri){
  if(pgAddingSkills.has(uri))return;
  const careerUri=pg.detail?.occupation.uri;
  pgAddingSkills.add(uri);pgSkillMessage='';pgSkillError=false;pgRender();
  try{
    const data=await request('/api/profile/skills/confirm',{method:'POST',headers:{'X-CSRF-Token':state.csrf_token},body:JSON.stringify({skill_uri:uri,confirmed:true})});
    state.confirmed_skills=data.confirmed_skills;
    delete state.detailsByUri[careerUri];
    pg.picked.delete(uri);
    if(pg.detail?.career_map)(pg.detail.career_map.skills||[]).forEach(s=>{s.confirmed=state.confirmed_skills.some(c=>c.uri===s.uri)});
    pgSkillMessage=data.added?'Added to My Skills Passport.':'Already in My Skills Passport.';
    renderSummary();loadRecommendations();
    try{
      const latest=await request('/api/my-future/career?uri='+encodeURIComponent(careerUri));
      state.detailsByUri[careerUri]=latest;
      if(pg.detail?.occupation.uri===careerUri&&!$('career-detail').hidden)renderDetail(latest);
    }catch(_error){pgSkillMessage+=' Refresh career details to update the suggestions.'}
  }catch(error){pgSkillMessage=error.message;pgSkillError=true}
  finally{pgAddingSkills.delete(uri);pgRender()}
}
function pgSection(title,sub,items,m,goals,done){
  const list=(items||[]).slice(0,8);
  return '<section class="pg-ins-sec" aria-label="'+esc(title)+'"><h3>'+esc(title)+'</h3><p>'+esc(sub)+'</p>'+(list.length?'<div class="pg-cards">'+list.map(p=>pgCard(p,m,goals,done)).join('')+'</div>':'<div class="myf-empty"><strong>Nothing to show</strong>No not-yet-confirmed skills here for the current comparison.</div>')+'</section>';
}
const PG_MODES=[['map','Career Map'],['insurance','Career Insurance'],['exp','Experience']];
const PG_SC={slower_adoption:'Slower',moderate_adoption:'Moderate',faster_adoption:'Faster'};
const pgScLabel=y=>PG_SC[y.id]||y.label;
function pgSim(detail,m,uri){
  const st=detail.stress_test;
  if(!st||!Array.isArray(st.scenarios)||!st.scenarios.length)return '<div class="myf-empty"><strong>Simulator not available</strong>Scenario details could not be loaded for this career.</div>';
  const sc=st.scenarios.find(x=>x.id===state.stress.scenario)||st.scenarios[0];
  const steps=(sc.workflow&&sc.workflow.steps)||[];
  if(pg.step>=steps.length)pg.step=Math.max(0,steps.length-1);
  const x=steps[pg.step],last=pg.step>=steps.length-1;
  const ev=st.evidence||{},conf=(sc.valuable||[]).filter(v=>state.confirmed_skills.some(c=>c.uri&&c.uri===v.uri));
  const actionLabels={
    limited_assistance:['Practise independently','Compare an assisted example','Choose learning options'],
    reviewed_sequence:['Build a reviewed sequence','Track and compare each step','Choose learning options'],
    validated_workflow:['Combine practice steps','Test failures and fallback','Choose learning options']
  }[sc.profile?.scope]||[];
  const prepare=(sc.prepare||[]).slice(0,3).map((action,i)=>'<details class="pg-prep"><summary>'+esc(actionLabels[i]||('Preparation option '+(i+1)))+'</summary><p>'+esc(action)+'</p></details>').join('');
  const workforce=(ev.labour_market||[]).map(row=>'<li>'+esc(row.label||row.id)+': '+esc(row.status==='unavailable'?'Data not available':row.status)+'</li>').join('');
  const detailsHtml=x?'<details class="myf-disclosure" style="margin-top:8px"><summary>Step details and evidence boundaries</summary><div class="myf-disclosure-body"><p>'+esc(x.description||'No official description available.')+'</p><p>Skill relation: official ESCO '+(x.relation==='optional'?'optional':'essential')+'.</p><p>Check: '+esc(x.review||'Check the result yourself before using it.')+'</p>'+((x.linked_tasks||[]).length?'<p>Unverified candidate benchmark task links (semantic, not verified):</p>'+x.linked_tasks.map(t=>'<p>'+esc(t.task)+' - '+esc(t.relationship||'')+'</p>').join(''):'<p>No linked benchmark task for this step.</p>')+'<p><strong>Measured:</strong> benchmark scores describe model performance on named tasks only. <strong>Semantic:</strong> task-to-skill links are text-similarity candidates. <strong>Hypothetical:</strong> this scenario and workflow are assumptions to explore, not forecasts.</p></div></details>':'';
  const evidence='<details class="myf-disclosure" id="pg-sim-evidence"><summary>Evidence and limits</summary><div class="myf-disclosure-body"><p>'+esc(st.notice||'Hypothetical scenarios for exploration, not predictions.')+'</p><p>'+esc((sc.workflow&&sc.workflow.note)||'')+' '+esc(sc.assistance_summary||'')+'</p>'+(conf.length?'<p>Confirmed in your Passport and listed here: '+conf.map(v=>esc(v.label)).join(', ')+'.</p>':'<p>None of the skills listed here are confirmed in your Passport yet. Skills not recorded are not absent from your experience.</p>')+taskExamples(sc)+stressList(sc.limitations)+renderBenchmarkEvidence(ev.benchmark_baseline||detail.ai_impact)+renderWorkforceContext(ev.workforce_context||detail.job_demand)+'</div></details>';
  return '<div class="pg-seg" role="group" aria-label="Hypothetical scenario">'+st.scenarios.map(y=>'<button type="button" data-pg-sc="'+esc(y.id)+'" aria-pressed="'+(y.id===sc.id)+'">'+esc(pgScLabel(y))+'</button>').join('')+'</div>'+
   '<p class="pg-hyp"><span class="myf-chip optional">Hypothetical</span> '+esc(sc.assumption)+'</p>'+
   (x?'<ol class="pg-steps" aria-label="Workflow steps">'+steps.map((y,i)=>'<li><button type="button" data-pg-step="'+i+'" aria-pressed="'+(i===pg.step)+'" aria-label="Step '+(i+1)+' of '+steps.length+': '+esc(y.label)+'">'+(i+1)+'</button></li>').join('')+'</ol><div class="pg-panel" id="pg-step-card" tabindex="-1"><small>Step '+(pg.step+1)+' of '+steps.length+'</small><h4>'+esc(x.label)+'</h4><p>'+esc(x.assistance||'')+'</p>'+detailsHtml+'<div class="pg-card-foot" style="margin-top:10px"><button type="button" class="btn btn-ghost btn-sm" data-pg-stepnav="-1"'+(pg.step?'':' disabled')+'>Back</button>'+(last?'<button type="button" class="btn btn-primary btn-sm" data-pg-mode="insurance">Open learning options</button>':'<button type="button" class="btn btn-primary btn-sm" data-pg-stepnav="1">Next step</button>')+'</div></div>':'<div class="myf-empty"><strong>No practice steps</strong>This career has no skill steps to practise.</div>')+
   '<p class="pg-sub">To prepare</p>'+prepare+'<div class="pg-card-foot"><button type="button" class="btn btn-ghost btn-sm" data-pg-mode="insurance">Skills to add to my plan</button><button type="button" class="btn btn-ghost btn-sm" data-pg-goplan>My Learning Plan</button></div>'+evidence+(workforce?'<details class="myf-disclosure"><summary>Workforce evidence availability</summary><div class="myf-disclosure-body"><ul>'+workforce+'</ul></div></details>':'');
}
function pgPixels(ce,strength){
  const px=ce.image.pixels,mn=Math.min(...px),mx=Math.max(...px),t=strength/100;
  return {mn,mx,flat:mx===mn,out:px.map(p=>mx===mn?p:Math.round(p+((p-mn)/(mx-mn)*255-p)*t))};
}
function pgGrid(ce,vals,label){
  const w=ce.image.width,h=ce.image.height;
  return '<svg viewBox="0 0 '+w+' '+h+'" class="pg-px" role="img" aria-label="'+esc(label)+': '+vals.join(', ')+'" shape-rendering="crispEdges">'+vals.map((v,i)=>'<rect x="'+i%w+'" y="'+Math.floor(i/w)+'" width="1" height="1" fill="rgb('+v+','+v+','+v+')"/><text x="'+(i%w+.5)+'" y="'+(Math.floor(i/w)+.58)+'" text-anchor="middle" font-size=".26" fill="'+(v>128?'#14263a':'#fbf8f1')+'">'+v+'</text>').join('')+'</svg>';
}
function pgActivity(ce){
  const a=ce.activity||{};
  if(a.type==='table'){
    return '<p>'+esc(a.caption||'Synthetic sample')+'</p><div class="pg-table-wrap"><table class="pg-table"><thead><tr>'+(a.headers||[]).map(v=>'<th scope="col">'+esc(v)+'</th>').join('')+'</tr></thead><tbody>'+(a.rows||[]).map(row=>'<tr>'+row.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
  }
  return '<div class="pg-scenario"><strong>Scenario</strong><p>'+esc(a.context||'')+'</p></div>';
}
function pgExperienceLinks(ce){
  const examples=ce.available_examples||[];
  if(!examples.length)return '';
  const current=ce.source&&ce.source.occupation?ce.source.occupation.uri:'';
  return '<details class="myf-disclosure"><summary>Available practice skills ('+examples.length+')</summary><div class="myf-disclosure-body">'+examples.map(x=>'<p><a href="/my-future?career='+encodeURIComponent(x.occupation_uri)+'&amp;mode=exp">'+esc(x.occupation_label)+' — '+esc(x.skill_label)+'</a>'+(x.occupation_uri===current?' <span class="muted">(current)</span>':'')+'</p>').join('')+'</div></details>';
}
function pgExp(detail){
  const ce=detail.career_experience;
  if(!ce||ce.status!=='available')return '<div class="myf-empty"><strong>No short exercise for this career yet</strong>'+esc((ce&&ce.notice)||'Career experiences are added only where the occupation data supports a grounded example.')+pgExperienceLinks(ce||{})+'</div>';
  const e=pg.exp,src=ce.source||{};
  const info='<details class="myf-disclosure"><summary>About this exercise</summary><div class="myf-disclosure-body"><p>'+esc(ce.notice||'')+'</p><p>This synthetic example is authored for practice. It is not workplace evidence or a competence assessment.</p>'+(src.basis?'<p>Basis: '+esc(src.basis)+'</p>':'')+(src.skill?'<p>Linked ESCO skill: '+esc(src.skill.label)+(src.skill.relation?' ('+esc(src.skill.relation)+')':'')+'. '+esc(src.skill.description||'')+'</p>':'')+'</div></details>';
  if(e.step===0)return '<div class="pg-panel"><h4>'+esc(ce.title)+'</h4><p>'+esc(ce.summary)+'</p>'+(src.skill?'<p><strong>Skill focus:</strong> '+esc(src.skill.label)+'</p>':'')+'<p><span class="myf-chip optional">Illustrative practice</span> Not scored, saved or certified.</p><div class="pg-card-foot" style="margin-top:8px"><button type="button" class="btn btn-primary btn-sm" data-pg-exp="start">Start exercise</button></div>'+info+pgExperienceLinks(ce)+'</div>';
  if(e.step===1){
    if(!ce.image)return '<div class="pg-panel"><small>Step 1 of 2</small><h4>Try the scenario</h4>'+pgActivity(ce)+'<p class="myf-disclaimer">Use the example to decide what you would check or ask next.</p><div class="pg-card-foot" style="margin-top:10px"><button type="button" class="btn btn-ghost btn-sm" data-pg-exp="intro">Back</button><button type="button" class="btn btn-primary btn-sm" id="pg-exp-next" data-pg-exp="question">Next: a question</button></div>'+info+'</div>';
    const r=pgPixels(ce,e.strength);
    return '<div class="pg-panel"><small>Step 1 of 2</small><h4>Stretch the contrast</h4><p>Move the slider and watch each pixel value change.</p><label class="pg-range" for="pg-strength">Contrast stretch: <output id="pg-strength-out">'+e.strength+'</output></label><input type="range" id="pg-strength" min="0" max="100" step="1" value="'+e.strength+'" aria-describedby="pg-exp-note"><div class="pg-grids"><figure><figcaption>Original</figcaption>'+pgGrid(ce,ce.image.pixels,'Original pixels')+'</figure><figure><figcaption>Result</figcaption><div id="pg-exp-result">'+pgGrid(ce,r.out,'Result pixels')+'</div></figure></div><p class="myf-disclaimer" id="pg-exp-note" aria-live="polite">'+(r.flat?'All pixels have the same value, so there is no range to stretch.':'Range '+r.mn+' to '+r.mx+' is mapped toward 0 to 255.')+'</p><details class="myf-disclosure"><summary>Pixel details and formula</summary><div class="myf-disclosure-body"><p>'+esc(ce.image.alt||'')+'</p><p>'+esc(ce.image.formula||'')+'</p></div></details><div class="pg-card-foot" style="margin-top:10px"><button type="button" class="btn btn-ghost btn-sm" data-pg-exp="intro">Back</button><button type="button" class="btn btn-primary btn-sm" data-pg-exp="question">Next: a question</button></div>'+info+'</div>'}
  const ch=(ce.choices||[]).find(c=>c.id===e.choice);
  return '<div class="pg-panel"><small>Step 2 of 2</small><h4>'+esc(ce.question)+'</h4><fieldset class="pg-choices"><legend class="pg-sr">Choose an answer</legend>'+(ce.choices||[]).map(c=>'<label class="pg-choice"><input type="radio" name="pg-choice" value="'+esc(c.id)+'"'+(e.choice===c.id?' checked':'')+'> <span>'+esc(c.label)+'</span></label>').join('')+'</fieldset><div id="pg-feedback" role="status" aria-live="polite">'+(ch?'<div class="pg-fb"><strong>'+(ch.supported?'Supported by this example':'Not supported by this example')+'</strong><p>'+esc(ch.feedback)+'</p></div>':'')+'</div><div class="pg-card-foot" style="margin-top:10px"><button type="button" class="btn btn-ghost btn-sm" data-pg-exp="try">Try again</button><button type="button" class="btn btn-primary btn-sm" data-pg-mode="map">Return to map</button></div>'+info+'</div>';
}
function pgMapBody(m,g,total,view,ins,uri){
  return '<div class="pg-filter"><span class="pg-filter-label">Skills</span><div class="pg-seg" role="group" aria-label="Filter skills">'+[['all','All'],['confirmed','Confirmed'],['explore','To explore']].map(f=>'<button type="button" data-pg-filter="'+f[0]+'" aria-pressed="'+(pg.filter===f[0])+'">'+f[1]+'</button>').join('')+'</div><input type="search" id="pg-q" maxlength="60" placeholder="Filter skills" aria-label="Filter skills" value="'+esc(pg.q)+'"></div>'+
    '<p class="pg-count" id="pg-count">'+(view==='graph'?'Map shows '+g.top.length+' of '+g.total+' filtered skills'+(g.total<total?' (filtered from '+total+')':'')+'.':'Showing '+Math.min(pg.limit,g.total)+' of '+g.total+' skills.')+'</p>'+
   (view==='graph'?pgGraph(m,g.top):pgList(m))+pgPanel(m);
}
function pgRender(){
  const host=$('playground'),detail=pg.detail;if(!host||!detail)return;
  const m=detail.career_map,st=detail.stress_test||{},ins=st.insurance||{},uri=detail.occupation.uri;
  if(!m||!m.occupation){host.innerHTML='';return}
  if(pg.sel&&!(m.skills||[]).some(s=>s.uri===pg.sel))pg.sel=null;
  const goals=state.roadmap_goals[uri]||[],done=state.roadmap_progress[uri]||[];
  const g=pgGraphSkills(m),total=(m.skills||[]).length,view=pg.view||(window.innerWidth<=640?'list':'graph');
  const nPick=[...pg.picked].filter(x=>!goals.includes(x)).length;
  const goal=state.preferences.target_occupation_uri,goalLabel=goal?(careerLabel(goal)||'a saved career'):'';
  let body='';
  if(pg.mode==='insurance')body='<div class="pg-ins">'+pgSection('For My Goal','Listed for '+m.occupation.label+', not yet confirmed.',ins.prepare,m,goals,done)+pgSection('For Other Careers','Shared with your compared careers.',ins.options,m,goals,done)+'<div class="pg-bar"><span id="pg-picked">'+nPick+' skill'+(nPick===1?'':'s')+' selected</span><button type="button" class="btn btn-primary btn-sm" data-pg-add'+(nPick?'':' disabled')+'>Add selected to plan</button></div></div>';
  else if(pg.mode==='sim')body=pgSim(detail,m,uri);
  else if(pg.mode==='exp')body=pgExp(detail);
  else body=pgMapBody(m,g,total,view,ins,uri);
  host.innerHTML='<div class="pg-head"><div><div class="eyebrow">Career Playground</div></div></div><div class="pg-seg pg-modes" role="group" aria-label="Playground mode">'+PG_MODES.map(x=>'<button type="button" data-pg-mode="'+x[0]+'" aria-pressed="'+(pg.mode===x[0])+'">'+x[1]+'</button>').join('')+'</div>'+(pgSkillMessage?'<p class="'+(pgSkillError?'myf-error':'myf-status')+'" role="status">'+esc(pgSkillMessage)+'</p>':'')+'<div class="pg-body">'+body+'</div><div class="pg-sr" role="status" aria-live="polite" id="pg-live"></div>';
  pgWire(host,detail,m,ins,uri);
  if(pg.focus){const n=host.querySelector(pg.focus);if(n)n.focus();pg.focus=null}
}
function pgWire(host,detail,m,ins,uri){
  const q=(sel,fn)=>host.querySelectorAll(sel).forEach(fn);
  const rr=(focus,msg)=>{pg.focus=focus;pgRender();if(msg)pgLive(msg)};
  q('[data-pg-filter]',b=>b.addEventListener('click',()=>{pg.filter=b.dataset.pgFilter;pg.limit=12;rr('[data-pg-filter="'+pg.filter+'"]','Filter: '+b.textContent)}));
  const qi=host.querySelector('#pg-q');if(qi)qi.addEventListener('input',()=>{pg.q=qi.value;pg.limit=12;const p=qi.selectionStart;pg.focus='#pg-q';pgRender();const n=$('pg-q');if(n){n.setSelectionRange(p,p)}});
  q('[data-pg-skill]',b=>b.addEventListener('click',()=>{const u=b.dataset.pgSkill;pg.sel=pg.sel===u?null:u;const s=(m.skills||[]).find(x=>x.uri===u);const n=s?pgAltConns(s,m).length:0;rr('[data-pg-skill="'+CSS.escape(u)+'"]',pg.sel?(s.label+' selected. Listed for '+n+' displayed alternative career'+(n===1?'':'s')+'.'):'Skill selection cleared.')}));
  q('[data-pg-occ]',b=>b.addEventListener('click',()=>{pg.focus='[data-pg-center]';pg.sel=null;pg.picked.clear();pgLive('Loading '+b.title+'…');loadDetails(b.dataset.pgOcc)}));
  q('[data-pg-center]',b=>b.addEventListener('click',()=>{pg.sel=null;rr('[data-pg-center]','Skill highlight cleared.')}));
  q('[data-pg-more]',b=>b.addEventListener('click',()=>{pg.limit+=12;pgRender();pgLive('More skills shown.')}));
  q('[data-pg-passport]',b=>b.addEventListener('click',()=>{window.location.href='/my-career?skill='+encodeURIComponent(b.dataset.pgPassport||'')}));
  q('[data-pg-have]',b=>b.addEventListener('click',()=>pgHaveSkill(b.dataset.pgHave)));
  q('[data-pg-pick]',b=>b.addEventListener('click',()=>{const u=b.dataset.pgPick;pg.picked.has(u)?pg.picked.delete(u):pg.picked.add(u);rr('[data-pg-pick="'+CSS.escape(u)+'"]',pg.picked.has(u)?'Skill selected.':'Skill unselected.')}));
  const add=host.querySelector('[data-pg-add]');if(add)add.addEventListener('click',()=>pgAddSelected(uri));
  q('[data-pg-mode]',b=>b.addEventListener('click',()=>{pg.mode=b.dataset.pgMode;if(pg.mode==='exp'&&b.closest('.pg-modes'))pg.exp={step:0,strength:50,choice:null};rr('.pg-modes [data-pg-mode="'+pg.mode+'"]',(PG_MODES.find(x=>x[0]===pg.mode)||[0,''])[1]+' mode.')}));
  q('[data-pg-sc]',b=>b.addEventListener('click',()=>{state.stress.scenario=b.dataset.pgSc;pg.step=0;rr('[data-pg-sc="'+b.dataset.pgSc+'"]','Scenario: '+b.textContent+'. Workflow and preparation updated.')}));
  q('[data-pg-step]',b=>b.addEventListener('click',()=>{pg.step=Number(b.dataset.pgStep);rr('[data-pg-step="'+pg.step+'"]','Step '+(pg.step+1)+'.')}));
  q('[data-pg-stepnav]',b=>b.addEventListener('click',()=>{pg.step=Math.max(0,pg.step+Number(b.dataset.pgStepnav));rr('#pg-step-card','Step '+(pg.step+1)+'.')}));
  q('[data-pg-goplan]',b=>b.addEventListener('click',()=>{state.learningCareerUri=uri;setTab('learning')}));
   q('[data-pg-exp]',b=>b.addEventListener('click',()=>{const a=b.dataset.pgExp,e=pg.exp;
     if(a==='start'){e.step=1;rr(detail.career_experience.image?'#pg-strength':'#pg-exp-next','Exercise started.')}
    else if(a==='intro'){e.step=0;rr('[data-pg-exp="start"]')}
    else if(a==='question'){e.step=2;e.choice=null;rr('input[name="pg-choice"]','Question.')}
     else if(a==='try'){e.step=1;e.choice=null;rr(detail.career_experience.image?'#pg-strength':'#pg-exp-next','Try again.')}}));
  const rg=host.querySelector('#pg-strength');if(rg)rg.addEventListener('input',()=>{const ce=detail.career_experience,v=Number(rg.value);pg.exp.strength=v;const r=pgPixels(ce,v);$('pg-strength-out').textContent=String(v);$('pg-exp-result').innerHTML=pgGrid(ce,r.out,'Result pixels')});
  q('input[name="pg-choice"]',i=>i.addEventListener('change',()=>{pg.exp.choice=i.value;const ch=(detail.career_experience.choices||[]).find(c=>c.id===i.value);pgLive('');$('pg-feedback').innerHTML=ch?'<div class="pg-fb"><strong>'+(ch.supported?'Supported by this example':'Not supported by this example')+'</strong><p>'+esc(ch.feedback)+'</p></div>':''}));
}
async function pgAddSelected(uri){
  if(roadmapBusy)return;
  const cur=state.roadmap_goals[uri]||[],add=[...pg.picked].filter(x=>!cur.includes(x));
  if(!add.length)return;
  roadmapBusy=true;
  const oldGoals=JSON.parse(JSON.stringify(state.roadmap_goals)),oldProg=JSON.parse(JSON.stringify(state.roadmap_progress));
  state.roadmap_goals[uri]=[...new Set([...cur,...add])];pgRender();
  const ok=await saveState(add.length+' skill'+(add.length===1?'':'s')+' added to your learning plan.');
  roadmapBusy=false;
  if(ok){pg.picked.clear();pgLive(add.length+' added to your learning plan.');loadDetails(uri);if(state.learningCareerUri===uri&&state.activeTab==='learning')loadLearningCareer(uri)}
  else{state.roadmap_goals=oldGoals;state.roadmap_progress=oldProg;pgRender();pgLive('Could not save. Your plan was not changed.')}
}
function pgMount(detail){
  if(!detail||!detail.career_map)return;
  const host=$('career-detail');if(!host||$('stress-back'))return;
  if(pg.uri!==detail.occupation.uri){pg.picked.clear();pg.sel=null;pg.q='';pg.limit=12;pg.uri=detail.occupation.uri;if(!pg.simIntent)pg.mode='map';pg.step=0;pg.exp={step:0,strength:50,choice:null}}
  pg.simIntent=false;pg.detail=detail;
  let box=$('playground');if(box)box.remove();
  box=document.createElement('section');box.id='playground';box.className='pg';box.setAttribute('aria-label','Career Playground');
  const top=host.querySelector('.myf-detail-top'),acts=host.querySelector('.myf-detail-actions');
  if(acts&&!$('pg-plan')){const b=document.createElement('button');b.type='button';b.className='btn btn-ghost btn-sm';b.id='pg-plan';b.textContent='My Learning Plan';b.addEventListener('click',()=>{state.learningCareerUri=detail.occupation.uri;setTab('learning')});acts.appendChild(b)}
  (acts||top)?(acts||top).insertAdjacentElement('afterend',box):host.prepend(box);
  const copy=host.querySelector('.myf-detail-copy');if(copy)copy.remove();
  while(box.nextSibling)box.nextSibling.remove();
  pgRender();
}
'''


# Shared interactive Career Map renderer: the exact pg* helper, graph, list, panel and
# map-body source above, reused on /career. Single source of truth (sliced, not copied).
_MAP_A = PLAYGROUND_JS.index("const pgAlts=")
_MAP_B = PLAYGROUND_JS.index("function pgCard(")
_MAP_C = PLAYGROUND_JS.index("function pgMapBody(")
_MAP_D = PLAYGROUND_JS.index("function pgRender(")
CAREER_MAP_JS = PLAYGROUND_JS[_MAP_A:_MAP_B] + PLAYGROUND_JS[_MAP_C:_MAP_D]
