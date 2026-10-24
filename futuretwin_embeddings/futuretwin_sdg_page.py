"""Purpose & Impact page (/purpose): SDG priorities, reviewed links, country context."""
from __future__ import annotations

from futuretwin_pages import _page

SDG_CSS = r'''
.pp{padding:44px 0 0}
.pp h1{font-size:clamp(30px,5vw,44px);line-height:1.1}
.pp .lead{max-width:640px;margin:12px 0 0}
.pp-sec{margin-top:40px}
.pp-sec>h2{font-size:26px;margin-bottom:6px}
.pp-sec>.sub{color:var(--muted);font-size:14px;margin:0 0 16px;max-width:680px}
.pp-pad{padding:20px}
.pp-note{font-size:13px;color:var(--muted);margin:8px 0 0}
.pp-goals{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:8px}
.pp-goal{display:flex;gap:10px;align-items:flex-start;text-align:left;background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:10px 12px;color:var(--ink);font-size:13.5px;line-height:1.35}
.pp-goal b{font-variant-numeric:tabular-nums;min-width:22px;color:var(--harbor)}
.pp-goal[aria-pressed=true]{background:var(--harbor-soft);border-color:#9bbad0}
.pp-goal:hover{border-color:#cfc5b0}
.pp-row{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:16px}
.pp-slider{margin-top:18px}
.pp-slider input{width:100%;accent-color:var(--harbor)}
.pp-split{display:flex;justify-content:space-between;font-size:13px;font-weight:600;color:var(--ink2)}
.pp-msg{font-size:13px;margin-top:10px}
.pp-msg.ok{color:var(--sage)}.pp-msg.bad{color:var(--clay)}
.pp-list{display:grid;gap:12px}
.pp-item{padding:16px 18px}
.pp-item h3{font-size:19px}
.pp-top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:flex-start}
.pp-chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.pp-input{width:100%;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--paper);color:var(--ink)}
.pp-res{margin-top:6px;border:1px solid var(--line);border-radius:12px;background:var(--paper);overflow:hidden}
.pp-res button{display:block;width:100%;text-align:left;background:none;border:0;border-bottom:1px solid var(--line2);padding:10px 14px;color:var(--ink);font-size:14px}
.pp-res button:hover{background:var(--paper2)}
.pp-ex{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;align-items:center}
.pp-ex span{font-size:13px;color:var(--muted)}
.pp-conn{padding:16px 18px;border-left:3px solid var(--harbor)}
.pp-conn.cand{border-left-color:var(--amber)}
.pp-sk{display:flex;gap:10px;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-top:8px;font-size:13.5px;border-top:1px dashed var(--line);padding-top:8px}
.pp-quote{margin:6px 0;padding-left:10px;border-left:2px solid var(--line);color:var(--ink2)}
.pp-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.pp-tab{border:1px solid var(--line);background:var(--paper);border-radius:99px;padding:6px 14px;font-weight:600;font-size:13px;color:var(--ink2)}
.pp-tab[aria-pressed=true]{background:var(--harbor);color:#fbf8f1;border-color:var(--harbor)}
.pp-chart{width:100%;height:auto;display:block}
.pp-bars{display:grid;gap:8px;margin-top:10px}
.pp-bar{display:grid;grid-template-columns:minmax(120px,220px) 1fr 90px;gap:10px;align-items:center;font-size:13px}
.pp-bar i{display:block;height:10px;border-radius:6px;background:#b9cfdf}
.pp-bar i.rel{background:var(--harbor)}
.pp-bar b{text-align:right;font-variant-numeric:tabular-nums}
.pp-grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.pp-links{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.pp-goal-explorer{margin-top:14px;padding-top:14px;border-top:1px solid var(--line2)}
.pp-goal-explorer h3{font-size:18px;margin:0 0 8px}
@media(max-width:760px){.pp-grid2{grid-template-columns:1fr}.pp-bar{grid-template-columns:1fr 70px}.pp-bar i{grid-column:1/-1;order:3}}
'''

SDG_BODY = r'''
<main class="pp"><div class="wrap">
<div class="eyebrow">Purpose and impact</div>
<h1>Where your skills meet the goals you care about</h1>
<p class="lead">Compare linked skills and sources. These are potential associations, not measured social impact.</p>

<section class="pp-sec" aria-labelledby="g-h"><h2 id="g-h">Your priorities</h2>
<p class="sub">Choose the Sustainable Development Goals that matter to you. Saved to your profile only when you press Save.</p>
<div class="card pp-pad"><div id="goals" class="pp-goals" aria-busy="true"><div class="skel" style="height:300px;grid-column:1/-1"></div></div>
<div class="pp-slider"><div class="pp-split"><span id="w-skill">Skills 70</span><span id="w-purpose">Purpose 30</span></div>
<input type="range" id="w" min="0" max="100" step="5" value="30" aria-label="Purpose weight, remainder goes to skills"></div>
<p class="pp-note">This slider also changes the Skills/Purpose balance in Best Match. The applied weights are shown there.</p>
<p class="pp-note">Role demand weight: 0, unavailable. No verified role-level vacancy data exists, so it is not used.</p>
<div class="pp-row"><button class="btn btn-primary btn-sm" id="save" disabled>Save priorities</button><button class="btn btn-ghost btn-sm" id="clear" disabled>Clear goals</button></div>
<div id="prefmsg" class="pp-msg" role="status" aria-live="polite"></div>
<details class="ev" style="margin-top:12px"><summary>SDG mapping coverage</summary><div class="evbody"><p id="catnote" class="pp-note"></p></div></details>
<div id="goal-explorer" class="pp-goal-explorer" aria-live="polite"><p class="pp-note">Click a goal above to preview its reviewed careers and ESCO skills. This does not save a priority until you press Save.</p></div>
</div></section>

<section class="pp-sec" aria-labelledby="r-h"><h2 id="r-h">Careers ranked with your priorities</h2>
<p class="sub">Heuristic points combine listed-skill coverage with reviewed purpose links for your selected goals. They are not proficiency or a social-impact percentage.</p>
<div id="recs" class="pp-list" aria-live="polite"></div></section>

<section class="pp-sec" aria-labelledby="e-h"><h2 id="e-h">Explore one career</h2>
<p class="sub">Search any ESCO career or start from a reviewed example. Up to three connections are shown.</p>
<div class="card pp-pad"><label for="q" class="muted" style="font-size:13px">Search career titles</label>
<input id="q" class="pp-input" type="search" maxlength="100" autocomplete="off" placeholder="For example: environmental engineer">
<div id="qres" class="pp-res" hidden></div>
<div class="pp-ex" id="examples"><span>Reviewed examples:</span></div></div>
<div id="occ" style="margin-top:14px" aria-live="polite"></div></section>

<section class="pp-sec" aria-labelledby="c-h"><h2 id="c-h">Malaysia context</h2>
<p class="sub">Real national observations shown side by side. They are context only and are never combined into a need score or pay gap.</p>
<div class="pp-tabs" id="ctabs" role="group" aria-label="SDG target"></div>
<div id="country" aria-live="polite"><div class="skel" style="height:260px"></div></div></section>
</div></main>
'''

SDG_JS = r'''
(function(){
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl=u=>/^https?:\/\//i.test(u||'')?esc(u):'';
async function req(url,opt={}){const headers=Object.assign({'Accept':'application/json'},opt.body?{'Content-Type':'application/json'}:{},opt.headers||{});const r=await fetch(url,Object.assign({},opt,{credentials:'same-origin',headers}));let d=null;try{d=await r.json()}catch(e){}if(!r.ok)throw new Error((d&&d.error)||'Something went wrong. Try again.');return d}
const errBox=(m,id)=>'<div class="errbox"><span>'+esc(m)+'</span><button class="btn btn-ghost btn-sm" data-retry="'+id+'">Retry</button></div>';
let goals=[],saved=[],weight=30,csrf='',cat=null,dirty=false,curUri=null,browseGoal=null;
const goalNames=['No Poverty','Zero Hunger','Good Health & Well-being','Quality Education','Gender Equality','Clean Water & Sanitation','Affordable & Clean Energy','Decent Work & Economic Growth','Industry, Innovation & Infrastructure','Reduced Inequalities','Sustainable Cities & Communities','Responsible Consumption & Production','Climate Action','Life Below Water','Life on Land','Peace, Justice & Strong Institutions','Partnerships for the Goals'];

function drawGoals(){
  if(!cat)return;
  $('goals').setAttribute('aria-busy','false');
  $('goals').innerHTML=cat.goals.map(g=>'<button type="button" class="pp-goal" data-g="'+esc(g.code)+'" aria-pressed="'+goals.includes(String(g.code))+'" title="'+esc(g.title||'')+'"><b>'+esc(g.code)+'</b><span>'+esc(goalNames[Number(g.code)-1]||g.title)+'</span></button>').join('');
  $('w').value=weight;$('w-skill').textContent='Skills '+(100-weight);$('w-purpose').textContent='Purpose '+weight;
  $('save').disabled=!dirty;$('clear').disabled=!goals.length;
}
$('goals').addEventListener('click',e=>{const b=e.target.closest('[data-g]');if(!b)return;const g=b.dataset.g;goals=goals.includes(g)?goals.filter(x=>x!==g):goals.concat(g);browseGoal=g;dirty=true;drawGoals();loadGoalConnections(g)});
$('w').addEventListener('input',e=>{weight=+e.target.value;dirty=true;drawGoals()});
$('clear').addEventListener('click',()=>{goals=[];dirty=true;drawGoals()});
$('save').addEventListener('click',async()=>{
  const m=$('prefmsg');m.className='pp-msg';m.textContent='Saving...';$('save').disabled=true;
  try{const d=await req('/api/sdg/preferences',{method:'POST',headers:{'X-CSRF-Token':csrf},body:JSON.stringify({goals:goals,skill_weight:100-weight,purpose_weight:weight,demand_weight:0})});
    csrf=d.csrf_token||csrf;dirty=false;m.className='pp-msg ok';m.textContent='Saved to your profile.';drawGoals();loadRecs()}
  catch(err){m.className='pp-msg bad';m.textContent=err.message;$('save').disabled=false}
});
async function loadPrefs(){
  try{const [c,p]=await Promise.all([req('/api/sdg/catalog'),req('/api/sdg/preferences')]);
    cat=c;csrf=p.csrf_token;goals=(p.preferences.goals||[]).map(String);weight=Math.round(p.preferences.purpose_weight);
    const cs=c.candidate_summary||{};
    $('catnote').textContent=(c.assistant_desk_reviewed_count||0)+' assistant desk-reviewed links across '+(c.reviewed_career_count||0)+' careers and '+(c.reviewed_goal_count||0)+' of 17 SDGs; '+(c.independent_human_reviewed_count||0)+' independently human-approved. '+(cs.candidate_link_count||0)+' unreviewed suggestions cover '+(cs.candidate_occupation_count||0)+' careers, '+(cs.candidate_skill_count||0)+' skills and '+(cs.candidate_goal_count||0)+' of 17 SDGs. Similarity suggestions do not affect ranking. '+(c.occupations_without_reviewed_evidence||0)+' occupations have no desk-reviewed link.';
    $('catnote').textContent+=' Industry diversity spans '+(cs.candidate_nace_division_count||0)+' source-listed NACE divisions.';
    drawGoals();drawExamples();
    const requestedGoal=new URLSearchParams(location.search).get('goal');
    browseGoal=(requestedGoal&&c.goals.some(g=>String(g.code)===requestedGoal))?requestedGoal:(goals[0]||null);
    if(browseGoal)loadGoalConnections(browseGoal);
  }catch(err){$('goals').setAttribute('aria-busy','false');$('goals').innerHTML='<div style="grid-column:1/-1">'+errBox(err.message,'prefs')+'</div>'}
}
function evidenceHtml(items){
  return (items||[]).map(v=>'<p><b>'+esc(v.label)+'</b>'+(safeUrl(v.url)?' <a href="'+safeUrl(v.url)+'" target="_blank" rel="noopener noreferrer">source</a>':'')+'<br><span class="pp-quote" style="display:block">'+esc(v.quote)+'</span></p>').join('');
}
function reviewedConnectionHtml(c){
  const t=c.target||{},o=c.occupation||{},s=(c.skills||[])[0]||{};
  const goal=String(t.goal_code||c.goal_code||'');
  const status=c.review_status==='independently_human_approved'?'Independently human-approved':'Assistant desk-reviewed';
  return '<article class="card pp-conn"><div class="pp-top"><a href="/career?occupation_uri='+encodeURIComponent(o.uri||c.occupation_uri)+'">'+esc(o.label||c.occupation_label)+'</a><div class="pp-chips" style="margin:0"><span class="chip c-obs">'+status+'</span><span class="chip c-flat">'+esc(c.strength)+'</span><span class="chip '+(c.direction==='positive'?'c-up':c.direction==='negative'?'c-clay':'c-warn')+'">'+esc(c.direction)+'</span></div></div>'+
    '<p style="margin:8px 0"><a href="/purpose?goal='+encodeURIComponent(goal)+'"><b>Target '+esc(t.target_code||c.target_code)+'</b></a>: '+esc(t.target_title||c.target_title)+'</p>'+
    '<p class="pp-note"><b>ESCO skill:</b> '+esc(s.label||c.skill_label)+' ('+esc(s.relation||c.skill_relation)+' skill)</p><p class="pp-note">'+esc(c.reason||'')+'</p>'+
    ((c.evidence||[]).length?'<details class="ev"><summary>Sources</summary><div class="evbody">'+evidenceHtml(c.evidence)+'</div></details>':'')+'</article>';
}
function candidateConnectionHtml(c){
  const t=c.target||{},o=c.occupation||{},s=(c.skills||[])[0]||{};
  return '<article class="card pp-conn cand"><div class="pp-top"><a href="/career?occupation_uri='+encodeURIComponent(o.uri||c.occupation_uri)+'">'+esc(o.label||c.occupation_label)+'</a><div class="pp-chips" style="margin:0"><span class="chip c-warn">Unreviewed suggestion</span><span class="chip c-flat">Relation not assessed</span></div></div>'+
    '<p style="margin:8px 0"><b>Target '+esc(t.target_code||c.target_code)+'</b>: '+esc(t.target_title||c.target_title)+'</p>'+
    '<p class="pp-note"><b>ESCO skill:</b> '+esc(s.label||c.skill_label)+' ('+esc(s.relation||c.skill_relation)+' skill)</p><p class="pp-note">'+esc(c.reason||'')+'</p>'+
    '<details class="ev"><summary>Sources and retrieval detail</summary><div class="evbody">'+
    '<p>Local MiniLM cosine similarity: '+Number(c.semantic_score||0).toFixed(3)+'. Retrieval ordering only—not a probability, impact score or reviewed connection.</p>'+
    evidenceHtml(c.evidence)+'</div></details></article>';
}
async function loadGoalConnections(goalCode){
  const host=$('goal-explorer');if(!host)return;
  host.innerHTML='<p class="pp-note">Loading SDG connections...</p>';
  try{
    const d=await req('/api/sdg/goal?goal='+encodeURIComponent(goalCode));
    let html='<h3>SDG '+esc(d.goal.code)+': '+esc(d.goal.title)+'</h3><p class="pp-note">'+esc(d.notice)+'</p>';
    const reviewed=d.reviewed_connections||[],candidates=d.candidate_suggestions||[];
    if(reviewed.length){
      html+='<h4>Reviewed career and skill links ('+reviewed.length+')</h4><div class="pp-list">'+reviewed.map(reviewedConnectionHtml).join('')+'</div>';
    }else{
      html+='<p class="pp-note">No assistant desk-reviewed links for this SDG yet. Missing links do not mean zero contribution.</p>';
    }
    if(candidates.length){
      html+='<details class="ev" style="margin-top:12px"><summary>Unreviewed suggestions ('+candidates.length+')</summary><div class="evbody"><p class="pp-note">These are local MiniLM retrieval leads only. Relationship strength and direction have not been assessed; they never affect Purpose Alignment.</p><div class="pp-list">'+candidates.map(candidateConnectionHtml).join('')+'</div></div></details>';
    }
    host.innerHTML=html;
  }catch(err){host.innerHTML='<div class="errbox">'+esc(err.message)+'</div>'}
}
function drawExamples(){
  $('examples').innerHTML='<span>Reviewed examples:</span>'+(cat.reviewed_careers||[]).map(o=>'<button class="btn btn-ghost btn-sm" data-occ="'+esc(o.uri)+'">'+esc(o.label)+'</button>').join('');
  const u=new URLSearchParams(location.search).get('occupation_uri');if(u)loadOcc(u);
}

async function loadRecs(){
  const h=$('recs');h.innerHTML='<div class="skel" style="height:110px"></div><div class="skel" style="height:110px"></div>';
  try{const d=await req('/api/my-future/recommendations?sort=purpose_alignment&limit=12');
    const rk=d.ranking||{},pm=rk.purpose||{};let out='';
    if(pm.fallback_reason)out+='<div class="card pp-pad"><span class="chip c-warn">Fallback</span> <span style="font-size:14px">'+esc(pm.fallback_reason)+'</span></div>';
    const items=d.recommendations||[];
    if(!items.length)out+='<div class="card pp-pad"><strong>No careers to rank yet</strong><p class="pp-note">Confirm skills in My Profile so careers can be matched by exact skill links.</p><a class="btn btn-ghost btn-sm" href="/my-career">Open My Profile</a></div>';
    out+=items.map(it=>{const p=it.purpose;const uri=it.uri||it.occupation_uri;
      let meta='';if(p){meta='<div class="pp-chips"><span class="chip c-obs">'+Number(p.heuristic_points).toFixed(1)+' heuristic points</span><span class="chip c-flat">'+p.evidenced_selected_goals+' of '+p.selected_goal_count+' selected goals with reviewed evidence</span>'+(p.score==null?'':'<span class="chip c-pos">Reviewed alignment '+Number(p.score).toFixed(2)+'</span>')+'</div>'+
        ((p.connections||[]).length?'<details class="ev"><summary>Reviewed links</summary><div class="evbody">'+p.connections.map(c=>'<p><b>SDG '+esc(c.target.target_code)+'</b> '+esc(c.strength)+', '+esc(c.direction)+'. '+esc(c.reason||'')+'</p>').join('')+'</div></details>':'')}
      return '<article class="card pp-item"><div class="pp-top"><h3>'+esc(it.label||it.title)+'</h3><div class="pp-chips" style="margin:0"><button class="btn btn-ghost btn-sm" data-occ="'+esc(uri)+'">See connections</button></div></div>'+meta+'</article>'}).join('');
    if(pm.formula)out+='<details class="ev"><summary>How points are calculated</summary><div class="evbody"><p>'+esc(pm.formula)+'</p><p>'+esc(pm.purpose_formula||'')+'</p><p>'+esc(pm.unknown_policy||'')+'</p><p>'+esc(pm.demand_reason||'')+'</p></div></details>';
    h.innerHTML=out;
  }catch(err){h.innerHTML=errBox(err.message,'recs')}
}

let st;$('q').addEventListener('input',e=>{clearTimeout(st);const q=e.target.value.trim(),r=$('qres');if(q.length<2){r.hidden=true;return}
  st=setTimeout(async()=>{r.hidden=false;r.innerHTML='<div class="pp-note" style="padding:10px 14px">Searching...</div>';
    try{const d=await req('/api/occupations/search?q='+encodeURIComponent(q)+'&limit=8');const s=d.suggestions||[];
      r.innerHTML=s.length?s.map(o=>'<button type="button" data-occ="'+esc(o.uri)+'">'+esc(o.label)+(o.matched_as==='also known as'?' <span class="muted">('+esc(o.matched_label)+')</span>':'')+'</button>').join(''):'<div class="pp-note" style="padding:10px 14px">No titles matched. Try another search.</div>'}
    catch(err){r.innerHTML='<div class="pp-note" style="padding:10px 14px;color:var(--clay)">'+esc(err.message)+'</div>'}},250)});

document.addEventListener('click',e=>{
  const o=e.target.closest('[data-occ]');if(o){$('qres').hidden=true;loadOcc(o.dataset.occ,true);return}
  const r=e.target.closest('[data-retry]');if(r){({prefs:loadPrefs,recs:loadRecs,occ:()=>loadOcc(curUri),country:()=>loadCountry(tgt)})[r.dataset.retry]()}
});

async function loadOcc(uri,scroll){
  curUri=uri;const h=$('occ');h.innerHTML='<div class="skel" style="height:180px"></div>';
  if(scroll)h.scrollIntoView({behavior:'smooth',block:'nearest'});
  try{const d=await req('/api/sdg/occupation?uri='+encodeURIComponent(uri));const o=d.occupation;
    let x='<div class="card pp-pad"><div class="pp-top"><div><h3>'+esc(o.label)+'</h3><p class="pp-note" style="max-width:640px">'+esc((o.description||'').slice(0,260))+(o.description&&o.description.length>260?'...':'')+'</p></div></div>'+
      '<div class="pp-chips"><span class="chip c-obs">'+d.reviewed_count+' assistant desk-reviewed link'+(d.reviewed_count===1?'':'s')+'</span></div>'+
      '<p class="pp-note">'+esc(d.notice)+'</p>'+(d.candidate_status==='unavailable'?'<p class="pp-note">Similarity suggestions are unavailable right now.</p>':'')+
      '<div class="pp-links"><a class="btn btn-ghost btn-sm" href="/career?occupation_uri='+encodeURIComponent(uri)+'">Open career</a><a class="btn btn-ghost btn-sm" href="/my-future">My Future</a></div></div>';
    if(!d.connections.length)x+='<div class="card pp-pad" style="margin-top:12px"><strong>No connections to show</strong><p class="pp-note">This career has no reviewed link and no suggestion. That is not evidence of zero impact.</p></div>';
    d.connections.forEach((c,i)=>{const cand=c.review_status==='unreviewed_candidate';const t=c.target||{};
      const status=c.review_status==='independently_human_approved'?'Independent human-approved':'Assistant desk-reviewed';
      x+='<article class="card pp-conn'+(cand?' cand':'')+'" style="margin-top:12px"><div class="pp-top"><strong>SDG '+esc(c.target_code)+'</strong><div class="pp-chips" style="margin:0">'+
        (cand?'<span class="chip c-warn">Unreviewed suggestion</span><span class="chip c-flat">Relation not assessed</span>':'<span class="chip c-obs">'+status+'</span><span class="chip c-flat">'+esc(c.strength)+'</span><span class="chip '+(c.direction==='positive'?'c-up':c.direction==='negative'?'c-clay':'c-warn')+'">'+esc(c.direction)+'</span>')+'</div></div>'+
        '<p style="margin:6px 0;font-size:14px">'+esc(t.target_title||'')+'</p><p class="pp-note">'+esc(c.reason||'')+'</p>'+
        (cand&&c.semantic_score!=null?'<p class="pp-note">Wording similarity '+Number(c.semantic_score).toFixed(2)+'. This is cosine similarity, not a probability.</p>':'')+
        (c.skills||[]).map((s,j)=>'<div class="pp-sk"><span>'+esc(s.label)+' <span class="muted">('+esc(s.relation)+' skill)</span></span><button class="btn btn-ghost btn-sm" data-add="'+i+':'+j+'">Add to learning plan</button></div>').join('')+
        '<div class="pp-msg" id="am'+i+'" role="status"></div>'+
        ((c.evidence||[]).length?'<details class="ev"><summary>Evidence</summary><div class="evbody">'+c.evidence.map(v=>'<p><b>'+esc(v.label)+'</b>'+(safeUrl(v.url)?' <a href="'+safeUrl(v.url)+'" target="_blank" rel="noopener noreferrer">source</a>':'')+'<br><span class="pp-quote" style="display:block">'+esc(v.quote)+'</span></p>').join('')+'</div></details>':'')+'</article>'});
    x+='<p class="pp-note">'+esc(d.tradeoff_status)+'</p><p class="pp-note">'+esc(d.review_scope)+'</p>';
    h.innerHTML=x;h._d=d;
  }catch(err){h.innerHTML=errBox(err.message,'occ')}
}
$('occ').addEventListener('click',async e=>{
  const b=e.target.closest('[data-add]');if(!b)return;const d=$('occ')._d;const [i,j]=b.dataset.add.split(':').map(Number);
  const skill=d.connections[i].skills[j],uri=d.occupation.uri,m=$('am'+i);
  b.disabled=true;m.className='pp-msg';m.textContent='Saving...';
  try{const s=await req('/api/my-future');
    const plan=Object.assign({},s.roadmap_goals||{});const cur=(plan[uri]||[]).slice();if(!cur.includes(skill.uri))cur.push(skill.uri);plan[uri]=cur;
    const sv=(s.saved_occupations||[]).slice();if(!sv.includes(uri))sv.push(uri);
    await req('/api/my-future',{method:'POST',headers:{'X-CSRF-Token':s.csrf_token},body:JSON.stringify({preferences:s.preferences,saved_occupations:sv,roadmap_progress:s.roadmap_progress||{},roadmap_goals:plan,insurance_alternatives:s.insurance_alternatives||{}})});
    m.className='pp-msg ok';m.innerHTML='Added to your learning plan. This does not mean you have the skill. <a href="/my-future?career='+encodeURIComponent(uri)+'">View plan</a>';
  }catch(err){m.className='pp-msg bad';m.textContent=err.message;b.disabled=false}
});

let tgt='6.1';
function chart(obs,unit){
  if(!obs.length)return '<p class="pp-note">No single unambiguous series is available for this indicator.</p>';
  const W=640,H=220,P=36,ys=obs.map(o=>o.value),mn=Math.min(...ys),mx=Math.max(...ys),pad=(mx-mn||1)*.15,lo=mn-pad,hi=mx+pad;
  const x0=obs[0].year,x1=obs[obs.length-1].year;const X=y=>P+(x1===x0?(W-2*P)/2:(y-x0)/(x1-x0)*(W-2*P)),Y=v=>H-P-(v-lo)/(hi-lo)*(H-2*P);
  const pts=obs.map(o=>X(o.year).toFixed(1)+','+Y(o.value).toFixed(1)).join(' ');
  return '<svg class="pp-chart" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Indicator timeline"><line x1="'+P+'" y1="'+(H-P)+'" x2="'+(W-P)+'" y2="'+(H-P)+'" stroke="#e6dfd0"/><polyline fill="none" stroke="#1c4a6e" stroke-width="2.5" points="'+pts+'"/>'+
   obs.map(o=>'<circle cx="'+X(o.year).toFixed(1)+'" cy="'+Y(o.value).toFixed(1)+'" r="4" fill="#1c4a6e"><title>'+o.year+': '+o.value+'</title></circle>').join('')+
   '<text x="'+P+'" y="'+(H-10)+'" font-size="12" fill="#66778a">'+x0+'</text><text x="'+(W-P)+'" y="'+(H-10)+'" font-size="12" text-anchor="end" fill="#66778a">'+x1+'</text><text x="'+P+'" y="14" font-size="12" fill="#66778a">'+esc(unit)+': '+mx.toFixed(1)+' high, '+mn.toFixed(1)+' low</text></svg>';
}
async function loadCountry(t){
  tgt=t;const h=$('country');h.innerHTML='<div class="skel" style="height:260px"></div>';
  try{const d=await req('/api/sdg/country?target='+encodeURIComponent(t));const ind=d.indicator,l=ind.latest;
    $('ctabs').innerHTML=d.available_targets.map(a=>'<button class="pp-tab" data-t="'+esc(a)+'" aria-pressed="'+(a===t)+'">Target '+esc(a)+'</button>').join('');
    const mxw=Math.max(1,...d.wages.map(w=>w.value));
    h.innerHTML='<div class="pp-grid2"><div class="card pp-pad"><h3 style="font-size:18px">'+esc(ind.title)+'</h3><p class="pp-note">Target '+esc(d.target.target_code)+': '+esc(d.target.target_title)+'</p>'+
      (l?'<p style="margin:10px 0 0;font-size:28px;font-family:var(--display)" class="num">'+Number(l.value).toFixed(1)+' <span class="muted" style="font-size:14px">'+esc(ind.unit)+', '+l.year+'</span></p>':'')+chart(ind.observations,ind.unit)+
      '<details class="ev"><summary>Source details</summary><div class="evbody"><p>Release '+esc(ind.release)+', retrieved '+esc(ind.retrieved_at)+'. '+(safeUrl(ind.source_url)?'<a href="'+safeUrl(ind.source_url)+'" target="_blank" rel="noopener noreferrer">UN SDG data</a>':'')+'</p><p>Filters: '+(Object.keys(ind.filters).length?esc(Object.entries(ind.filters).map(([k,v])=>k+' = '+v).join(', ')):'none')+'</p></div></details></div>'+
      '<div class="card pp-pad"><h3 style="font-size:18px">Median monthly pay, broad occupation groups</h3><p class="pp-note">Malaysian-citizen employees. Not a role salary, vacancy count or hiring demand.</p>'+
      (d.wage_error?'<div class="errbox" style="margin-top:10px">'+esc(d.wage_error)+'</div>':d.wages.length?'<div class="pp-bars">'+d.wages.map(w=>'<div class="pp-bar"><span>'+esc(w.group)+(w.related_broad_group?' <span class="chip c-obs">has reviewed link</span>':'')+'</span><i class="'+(w.related_broad_group?'rel':'')+'" style="width:'+(w.value/mxw*100).toFixed(1)+'%"></i><b>'+Math.round(w.value).toLocaleString()+' '+esc(w.unit.replace('MYR/month','MYR'))+'</b></div>').join('')+'</div><p class="pp-note">Data date '+esc(d.wages[0].date)+'. '+(safeUrl(d.wage_source_url)?'<a href="'+safeUrl(d.wage_source_url)+'" target="_blank" rel="noopener noreferrer">DOSM source</a>':'')+'</p>':'<p class="pp-note">No wage rows available.</p>')+
      '<details class="ev"><summary>Scope</summary><div class="evbody"><p>'+esc(d.wage_scope)+'</p></div></details></div></div>'+
      '<p class="pp-note">'+esc(d.notice)+'</p>'+
      ((d.associations||[]).length?'<p class="pp-note">Careers with a reviewed link to this target: '+d.associations.map(a=>'<a href="/career?occupation_uri='+encodeURIComponent(a.occupation_uri)+'">'+esc(a.occupation.label)+'</a>').join(', ')+'</p>':'');
  }catch(err){h.innerHTML=errBox(err.message,'country')}
}
$('ctabs').addEventListener('click',e=>{const b=e.target.closest('[data-t]');if(b)loadCountry(b.dataset.t)});
const first=['3.8','4.1','6.1','7.2'];$('ctabs').innerHTML=first.map(a=>'<button class="pp-tab" data-t="'+a+'" aria-pressed="'+(a==='6.1')+'">Target '+a+'</button>').join('');
loadPrefs();loadRecs();loadCountry('6.1');
})();
'''

SDG_HTML = _page("Purpose and Impact | FutureTwin AI", "future", SDG_CSS, SDG_BODY, SDG_JS)
