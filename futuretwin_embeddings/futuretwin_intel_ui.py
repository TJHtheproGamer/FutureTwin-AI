"""Frontend-only career intelligence UI: ranked job cards, compare, radar, detail tabs."""

INTEL_CSS = r'''
.ft-cov{font-size:13px;color:var(--ink2);display:grid;gap:3px}
.ft-cov strong{font-size:15px;color:var(--ink)}
.ft-cov details{font-size:12px;color:var(--muted)}.ft-cov summary{cursor:pointer;color:var(--harbor);font-weight:600;min-height:24px}
.ft-job:hover{border-color:#9bbbdd}
.ft-cmp{display:flex;gap:8px;align-items:center;font-size:13px;color:var(--ink2);min-height:32px}
.ft-cmp input{accent-color:var(--harbor);width:18px;height:18px}
.ft-sort{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 6px}
.ft-sort button{border:1px solid #b9cfe6;background:var(--paper);color:var(--harbor);border-radius:99px;padding:7px 14px;font-size:13px;font-weight:600;min-height:40px}
.ft-sort button:hover:not(:disabled){background:var(--harbor-soft)}
.ft-sort button[aria-pressed=true]{background:var(--harbor);color:#fcfdfe;border-color:var(--harbor)}
.ft-sort button:disabled{color:var(--faint);border-style:dashed;background:var(--paper2);cursor:not-allowed}
.ft-reason{font-size:12px;color:var(--muted);margin:2px 0}
.ft-cmpbar{position:sticky;bottom:10px;z-index:15;display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--paper);border:1px solid var(--harbor);border-radius:var(--r);padding:10px 14px;margin:12px 0;box-shadow:0 8px 24px #13202e22}
.ft-tbl{width:100%;border-collapse:collapse;font-size:13px}
.ft-tbl th,.ft-tbl td{text-align:left;vertical-align:top;padding:8px;border-top:1px solid var(--line2)}
.ft-tbl thead th{border-top:0;font-size:14px}
.ft-tbl tbody th{color:var(--muted);font-weight:600;width:120px}
.ft-scroll{overflow-x:auto}
.ft-tabs{display:flex;gap:2px;border-bottom:1px solid var(--line);margin:14px 0 4px;overflow-x:auto}
.ft-tabs button{border:0;background:none;padding:11px 16px;font-weight:600;font-size:14px;color:var(--muted);border-bottom:3px solid transparent;min-height:44px;white-space:nowrap}
.ft-tabs button:hover{color:var(--ink)}
.ft-tabs button[aria-selected=true]{color:var(--harbor);border-bottom-color:var(--harbor)}
.ft-meth{margin-top:12px;font-size:13px;color:var(--ink2)}.ft-meth summary{cursor:pointer;color:var(--harbor);font-weight:600;min-height:28px}
.ft-state{border:1px dashed #c4d2e0;border-radius:10px;background:var(--paper2);padding:10px 12px;font-size:13px;color:var(--ink2);margin:8px 0}
.ft-state b{display:block;color:var(--ink)}
.ft-ev{font-size:12px;color:var(--muted)}.ft-ev a{color:var(--harbor)}
.ft-kv{display:flex;justify-content:space-between;gap:10px;font-size:13px;padding:6px 0;border-top:1px solid var(--line2)}
.ft-saved{background:var(--sage-soft)!important;color:#17604a!important;border-color:#9fc5b4!important}
.ft-btn-busy{opacity:.6}
.ft-radar-count{font-size:12px;color:var(--ink2);font-weight:600}
.ft-radar-method{font-size:12px;color:var(--muted);margin:0}
.ft-radar-evidence{display:grid;gap:9px;margin-top:2px}
.ft-radar-evidence-row{border-top:1px solid var(--line2);padding-top:8px;font-size:12px;color:var(--ink2)}
.ft-radar-evidence-row a{color:var(--harbor);font-weight:600}
.ft-radar-evidence-meta{display:block;color:var(--muted);margin-top:2px}
.ft-radar-evidence-method{display:block;color:var(--faint);font-size:11px;margin-top:2px}
.ft-radar-evidence details{margin-top:4px}
.ft-radar-evidence summary{color:var(--harbor);font-weight:600;cursor:pointer;min-height:30px}
.ft-radar-passport{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);border-radius:99px;background:var(--paper2);color:var(--ink2);padding:4px 9px;font-size:11px;font-weight:600}
.ft-radar-passport.match{border-color:#9fc5b4;background:var(--sage-soft);color:#17604a}
.ft-radar-subhead{font-size:15px;margin:18px 0 8px}
.ft-radar-candidate{border-top:1px solid var(--line2);padding-top:10px;margin-top:2px}
.ft-job-filters{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:0 0 12px}
.ft-job-filters input,.ft-job-filters select{min-width:0;width:100%;border:1px solid var(--line);border-radius:9px;background:var(--paper);color:var(--ink);font:inherit;font-size:13px;padding:9px 10px;min-height:42px}
.ft-job-filter-actions{display:flex;gap:8px;grid-column:1/-1}
.ft-real-job{display:grid;gap:8px}
.ft-real-job h3{font:700 16px/1.35 var(--body);margin:0}
.ft-real-job p{margin:0}
.ft-real-job-meta{font-size:12px;color:var(--muted);line-height:1.5}
.ft-real-job-desc{font-size:13px;color:var(--ink2);line-height:1.55}
.ft-real-job details summary{cursor:pointer;color:var(--harbor);font-size:12px;font-weight:600;min-height:30px}
.ft-job-match{display:inline-flex;align-items:center;border:1px solid #b9cfe6;border-radius:99px;background:var(--harbor-soft);color:var(--harbor);padding:4px 9px;font-size:11px;font-weight:700}
.ft-job-match.exact{background:var(--sage-soft);border-color:#9fc5b4;color:#17604a}
.ft-job-skill-tags{display:flex;flex-wrap:wrap;gap:5px}
.ft-job-skill-tags .ft-tag{font-size:11px}
@media(max-width:700px){
  .ft-cmpbar .btn{flex:1;justify-content:center}
  .ft-tabs{flex-wrap:wrap;overflow:visible}
  .ft-tabs button{flex:1 1 auto;padding:8px 9px;font-size:12px}
  .ft-job-filters{grid-template-columns:1fr}
  .ft-job-filter-actions .btn{flex:1}
}
'''

INTEL_JS = r'''
function ftSafeUrl(u){try{const x=new URL(u,location.origin);return(x.protocol==='http:'||x.protocol==='https:')?x.href:''}catch(_e){return''}}
const ftPath=p=>(window.FT_BASE_PATH||'')+p;
const ftNum=v=>(typeof v==='number'&&isFinite(v))?v:null;
const ftPct=v=>ftNum(v)===null?null:(Math.round(v*10)/10)+'%';
function ftRankingEvidence(rank){
  const e=rank&&rank.evidence;if(!e)return null;
  const d=document.createElement('details');d.className='ft-meth';
  const t=e.tasks||{},v=e.vacancies||{},l=e.labels||{};
  const link=(url,text)=>{const u=typeof url==='string'&&/^https?:\/\//i.test(url)?ftSafeUrl(url):'';return u?'<a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">'+esc(text)+'</a>':esc(text)};
  const tasks=t.catalog_occupations?esc(t.exact_complete_occupations)+' careers have complete exact-linked task inventories out of '+esc(t.catalog_occupations)+'. '+esc(t.task_records)+' source tasks. '+link(t.source_url,t.source)+'. Other mapping types are not treated as exact.':esc(t.reason||'Task inventory not available.');
  d.innerHTML='<summary>Ranking evidence</summary><div class="ft-note"><p><strong>AI exposure</strong> — '+esc(l.reason||'Training lineage unverified.')+' '+link(l.paper,'Original research')+'.</p>'+
    (l.e3_note?'<p>'+esc(l.e3_note)+'</p>':'')+
    '<p>'+tasks+'</p>'+
    (t.eligibility_policy?'<p>'+esc(t.eligibility_policy)+'</p>':'')+
    '<p><strong>Hiring history</strong> — '+(v.observation_count?esc(v.observation_count)+' observations across '+esc(v.group_count)+' broad Malaysian groups, '+esc(v.period_start)+'–'+esc(v.period_end)+'. Historical data, not current vacancies. ':'')+esc(v.reason||'No verified exact-occupation series.')+' '+link(v.source_url,'DOSM source')+'.</p>'+
    '<p>Eligible now: '+esc(t.eligible_occupation_count||0)+' for Lower AI Exposure; '+esc(v.eligible_occupation_count||0)+' for Growing Jobs. Best Match remains the default.</p>'+
    (v.attribution?'<p>'+esc(v.attribution)+'. Analysis is by FutureTwin, not endorsed by DOSM.</p>':'')+'</div>';
  return d;
}
function ftCoverageEl(r){
  const sc=r.skill_coverage||{},e=sc.essential||{},o=sc.optional||{};
  const tot=(e.total_count||0)+(o.total_count||0),mat=(e.matched_count||0)+(o.matched_count||0);
  const M=ftNum(sc.matched_count)!==null?sc.matched_count:mat,T=ftNum(sc.total_count)!==null?sc.total_count:tot;
  const d=document.createElement('div');d.className='ft-cov';
  const pct=ftPct(sc.percentage);
  let h=pct&&T?'<span><strong>'+esc(pct)+'</strong> skill coverage ('+esc(M)+' of '+esc(T)+' skills)</span>':'<span>Skill coverage not available</span>';
  const te=r.task_exposure;
   const share=te&&te.predicted_task_exposure;
   if(share&&share.status==='available'&&ftNum(share.percentage)!==null)h+='<span><strong>'+esc(ftPct(share.percentage))+'</strong> predicted task-exposure share</span>';
  const ht=r.hiring_trend;
  if(ht&&ftNum(ht.growth_pct)!==null)h+='<span title="'+esc(ht.reason||'')+'">Hiring: '+(ht.growth_pct>0?'+':'')+esc(ftPct(ht.growth_pct))+' change</span>';
  d.innerHTML=h;return d;
}
function ftEnrichCard(el,c){
  if(!c.rec)return;
  el.insertBefore(ftCoverageEl(c.rec),el.querySelector('.ft-actions'));
  if(c.onCompare){
    const l=document.createElement('label');l.className='ft-cmp';
    l.innerHTML='<input type="checkbox"><span>Compare</span>';
    const i=l.querySelector('input');i.checked=!!c.compared;i.setAttribute('aria-label','Compare '+c.title);
    i.addEventListener('change',()=>{const ok=c.onCompare(c,i.checked);if(ok===false)i.checked=!i.checked});
    el.insertBefore(l,el.querySelector('.ft-actions'));
  }
}
'''

FIND_JS = r'''
let recSort='best_match',recRank=null;const cmp=new Map();
function updCmp(){
  const bar=$('cr-cmpbar');bar.hidden=cmp.size===0;
  $('cr-cmp-text').textContent=cmp.size+' selected'+(cmp.size<2?' - choose at least 2':'')+' (max 4)';
  $('cr-cmp-go').disabled=cmp.size<2;
}
function toggleCmp(c,on){
  if(on){if(cmp.size>=4){ftLive('You can compare up to 4 careers.');$('cr-cmp-text').textContent='Limit reached: compare up to 4 careers.';return false}cmp.set(c.uri,c.title)}else cmp.delete(c.uri);
  c.compared=on;updCmp();return true;
}
function drawSort(){
  const host=$('cr-sort');host.replaceChildren();if(!recRank)return;
  const order=['best_match','lower_exposure','purpose_alignment'];
  const opts=(recRank.options||[]).filter(o=>order.includes(o.id))
    .sort((a,b)=>order.indexOf(a.id)-order.indexOf(b.id));
  const grp=node('div','ft-sort');grp.setAttribute('role','group');grp.setAttribute('aria-label','Sort jobs');
  opts.forEach(o=>{const b=node('button','',o.label);b.type='button';b.setAttribute('aria-pressed',String(o.id===recRank.effective));
    if(!o.available){b.disabled=true;if(o.id==='growing_jobs')b.setAttribute('aria-label',o.label+' unavailable');else b.setAttribute('aria-describedby','sort-reason-'+o.id)}
    else b.addEventListener('click',()=>{recSort=o.id;loadRecs()});grp.appendChild(b)});
  host.appendChild(grp);
  opts.filter(o=>!o.available&&o.id!=='growing_jobs').forEach(o=>{const p=node('p','ft-reason',o.label+' unavailable: '+(o.reason||'required evidence is not available.'));p.id='sort-reason-'+o.id;host.appendChild(p)});
  if(recRank.fallback_reason)host.appendChild(node('p','ft-reason','Showing Best Match. '+recRank.fallback_reason));
  const evidence=ftRankingEvidence(recRank);if(evidence)host.appendChild(evidence);
}
async function runCompare(){
  const host=$('cr-compare');host.hidden=false;host.innerHTML='<div class="skel ft-skel"></div>';
  const q=[...cmp.keys()].map(u=>'uri='+encodeURIComponent(u)).join('&');
  try{
    const d=await ftReq(ftPath('/api/my-future/compare?'+q));
    const cs=d.careers||[],cp=d.comparability||{};
    const recBy=u=>recAll.find(x=>x.uri===u);
    const lab=['E0','E1','E2'];
    const rows=[
      ['Skill coverage',c=>{const r=recBy(c.occupation.uri);if(!r||!r.rec)return 'Not in your list';const s=r.rec.skill_coverage||{};return ftPct(s.percentage)?esc(ftPct(s.percentage)):'Not available'}],
      ['Task classes',c=>{const t=c.task_exposure;if(!t||t.status!=='available')return 'Not enough exact task data';return lab.map(l=>l+': '+esc(t.distribution[l].count)+'/'+esc(t.sample_task_count)).join('<br>')}],
      ['Task coverage',c=>{const t=c.task_exposure;return t&&t.status==='available'&&ftNum(t.task_coverage_percentage)!==null?esc(ftPct(t.task_coverage_percentage)):'Not available'}],
      ['Predicted task-exposure share',c=>{const s=(c.task_exposure||{}).predicted_task_exposure||{};return s.status==='available'&&ftNum(s.percentage)!==null?esc(ftPct(s.percentage))+' ('+esc(s.numerator)+'/'+esc(s.denominator)+' E1+E2)':'Not enough verified task data'}]
    ];
    host.innerHTML='<div class="ft-card"><div class="ft-sec-head"><h2>Compare careers</h2><button type="button" class="btn btn-ghost btn-sm" id="cr-cmp-close">Close</button></div><div class="ft-scroll"><table class="ft-tbl"><thead><tr><th><span class="pg-sr" style="position:absolute;left:-9999px">Measure</span></th>'+cs.map(c=>'<th scope="col"><a href="'+ftPath('/career?occupation_uri=')+encodeURIComponent(c.occupation.uri)+'">'+esc(c.occupation.label)+'</a></th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr><th scope="row">'+r[0]+'</th>'+cs.map(c=>'<td>'+r[1](c)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div><p class="ft-note" style="margin-top:8px">'+(cp.class_distributions_comparable?'Class counts use the same source definitions.':'Class distributions are not directly comparable. '+esc(cp.reason||''))+' No career is labelled safer or riskier here; missing data is not a result.</p></div>';
    $('cr-cmp-close').addEventListener('click',()=>{host.hidden=true;$('cr-cmp-go').focus()});
    host.scrollIntoView({block:'nearest'});ftLive('Comparison ready.');
  }catch(e){host.innerHTML='<div class="ft-err" role="alert"><span>'+esc(e.message)+'</span><button type="button" class="btn btn-ghost btn-sm" id="cmp-retry">Try again</button></div>';$('cmp-retry').addEventListener('click',runCompare)}
}
async function loadRecs(){
  const host=$('cr-recs'),wrap=$('cr-recs-wrap');skeletons(host);$('cr-recs-more').hidden=true;
  try{
    const d=await ftReq(ftPath('/api/my-future/recommendations?limit=30&sort='+encodeURIComponent(recSort)));
    recStatus=d.status||'';recRank=d.ranking||null;
    recAll=(d.recommendations||[]).map(r=>({...ftRecToCard(r),onCompare:toggleCmp,compared:cmp.has(r.uri)}));recShown=wide()?6:3;
    drawSort();
    if(!recAll.length){
      host.replaceChildren();
      if(recStatus==='no_confirmed_skills'){wrap.hidden=true}
      else{wrap.hidden=false;host.innerHTML='<div class="ft-empty" style="grid-column:1/-1"><strong>No eligible matches</strong><p>'+esc(d.message||'Choose Best Match or try another career.')+'</p></div>'}
      return;
    }
    wrap.hidden=false;
    drawList(host,recAll,recShown,$('cr-recs-more'));
  }catch(e){wrap.hidden=false;host.innerHTML='<div class="ft-err" style="grid-column:1/-1" role="alert"><span>'+esc(e.message)+'</span><button type="button" class="btn btn-ghost btn-sm" id="recs-retry">Try again</button></div>';$('recs-retry').addEventListener('click',loadRecs)}
}
/* ---------- Opportunity Radar ---------- */
let radarTab='jobs',radar=null;
let radarVisible={jobs:6,skills:8,careers:6};
let jobFilters={q:'',occupation:'',location:'',workplace:'',skill:'',skill_uri:''};
let jobListingData=null,jobListingError='',jobLoadSequence=0;
function radarMoreButton(key,total,label){
  const initial=({jobs:6,skills:8,careers:6})[key]||6;
  if(total<=initial&&radarVisible[key]===initial)return null;
  const expand=radarVisible[key]<total;
  const button=node('button','btn btn-ghost btn-sm ft-more',expand?('Show all '+total+' '+label):'Show fewer');
  button.type='button';button.setAttribute('aria-expanded',String(expand));
  button.addEventListener('click',()=>{radarVisible[key]=expand?total:initial;drawRadar()});
  return button;
}
function radarSourceName(s){return({remoteok:'Remote OK',remotive:'Remotive',himalayas:'Himalayas',greenhouse:'Greenhouse',lever:'Lever'})[String(s||'').toLowerCase()]||String(s||'Source')}
function radarLocation(e){
  const parts=[e.location,e.country].filter(x=>x&&String(x).trim());
  if(e.remote===true&&!parts.some(x=>/remote/i.test(String(x))))parts.push('Remote');
  return parts.join(' · ')||'Location not provided';
}
function radarDate(d){if(!d)return'Date not provided';const x=new Date(String(d).slice(0,10)+'T00:00:00');return isNaN(x.getTime())?String(d):x.toLocaleDateString(undefined,{day:'numeric',month:'short',year:'numeric'})}
function evidenceRow(e){
  const u=ftSafeUrl(e.url),title=e.title||radarSourceName(e.source);
  const link=u?'<a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">'+esc(title)+' ↗</a>':esc(title);
  const meta=radarSourceName(e.source)+' · Posted '+esc(radarDate(e.posted_date))+' · '+esc(radarLocation(e));
  return '<div class="ft-radar-evidence-row">'+link+'<span class="ft-radar-evidence-meta">'+meta+'</span>'+(e.evidence_quote?'<details><summary>Supporting text</summary><p class="ft-note">'+esc(e.evidence_quote)+'</p></details>':'')+'</div>';
}
function evidenceBlock(list,total,label){
  const rows=Array.isArray(list)?list:[];
  if(!rows.length)return '<span class="ft-note">No source links are available.</span>';
  const first=evidenceRow(rows[0]);
  const count=Number(total)||rows.length,remaining=Math.max(0,count-rows.length);
  if(rows.length===1&&remaining===0)return '<div class="ft-radar-evidence">'+first+'</div>';
  const rest=rows.slice(1).map(evidenceRow).join('');
  return '<div class="ft-radar-evidence">'+first+'<details><summary>View '+esc(rows.length)+' sample link'+(rows.length===1?'':'s')+' of '+esc(count)+' distinct ads</summary>'+rest+(remaining?'<p class="ft-note">'+esc(remaining)+' additional ads are counted but not expanded here.</p>':'')+'</details></div>';
}
function radarSaveButton(uri,title,msg){
  const s=node('button','btn btn-ghost btn-sm');s.type='button';
  const paint=()=>{const on=ftSaved(uri);s.textContent=on?'Saved':'Save career';s.classList.toggle('ft-saved',on);s.setAttribute('aria-pressed',String(on))};paint();
  s.addEventListener('click',async()=>{s.disabled=true;try{await ftToggleSave(uri);paint();ftLive(ftSaved(uri)?'Career saved.':'Career removed.')}catch(e){msg.innerHTML='<div class="ft-err" role="alert">'+esc(e.message)+'</div>'}s.disabled=false;s.focus()});
  return s;
}
function jobPostingCard(it){
  const el=node('article','ft-card ft-job');
  const msg=node('div','');
  el.innerHTML='<div class="ft-tags"><span class="ft-tag sage">Direct job-title match</span></div><h3>'+esc(it.title)+'</h3>'+
    '<div class="ft-radar-count">'+esc(it.sample_supporting_ads||0)+' distinct matching ad'+((it.sample_supporting_ads||0)===1?'':'s')+'</div>'+
    ((it.matched_skills||[]).length?'<div class="ft-tags" aria-label="Explicit skill terms in matched ads">'+it.matched_skills.slice(0,5).map(s=>'<span class="ft-tag">'+esc(s.label||s)+'</span>').join('')+'</div>':'')+
    evidenceBlock(it.evidence,it.sample_supporting_ads,'source ads')+
    '<div class="ft-actions"></div>';
  const actions=el.querySelector('.ft-actions');
  const view=node('a','btn btn-primary btn-sm','View career');view.href=ftPath('/career?occupation_uri=')+encodeURIComponent(it.uri);view.setAttribute('aria-label','View '+it.title);actions.appendChild(view);
  actions.appendChild(radarSaveButton(it.uri,it.title,msg));el.appendChild(msg);
  return el;
}
function confirmedPassportUriSet(){
  return new Set(((FT.state&&FT.state.confirmed_skills)||[]).map(s=>s&&s.uri).filter(Boolean));
}
function skillCard(it){
  const el=node('article','ft-card ft-job');
  const match=confirmedPassportUriSet().has(it.uri);
  const status=match?'Exact ESCO match in My Skills Passport':'Not listed in My Skills Passport';
  const evidence=it.evidence||[];
  el.innerHTML='<div class="ft-tags"><span class="ft-tag">Explicit skill mention</span></div><h3>'+esc(it.label)+'</h3>'+
    '<div class="ft-radar-count">'+esc(it.sample_mentions||0)+' distinct ad mention'+((it.sample_mentions||0)===1?'':'s')+' · '+esc(it.sample_postings||0)+' collected ads</div>'+
    '<span class="ft-radar-passport'+(match?' match':'')+'">'+(match?'✓ ':'')+esc(status)+'</span>'+
    evidenceBlock(evidence,it.sample_mentions,'source ads');
  return el;
}
function skillCareerCard(it){
  const el=node('article','ft-card ft-job');
  const msg=node('div','');
  const terms=it.supporting_skills||[];
  const evidence=it.evidence||[];
  el.innerHTML='<div class="ft-tags"><span class="ft-tag plain">Related career idea · not a job opening</span></div><h3>'+esc(it.title)+'</h3>'+
    '<div class="ft-radar-count">'+esc(it.sample_supporting_ads||0)+' distinct ad'+((it.sample_supporting_ads||0)===1?'':'s')+' with linked skill evidence</div>'+
    '<div class="ft-tags" aria-label="Explicit skills supporting this career idea">'+terms.map(s=>'<span class="ft-tag">'+esc(s.label)+(s.relation?' · '+esc(s.relation):'')+'</span>').join('')+'</div>'+
    evidenceBlock(evidence,it.sample_supporting_ads,'source ads')+
    '<div class="ft-actions"></div>';
  const actions=el.querySelector('.ft-actions');
  const view=node('a','btn btn-primary btn-sm','View career');view.href=ftPath('/career?occupation_uri=')+encodeURIComponent(it.uri);view.setAttribute('aria-label','View related career '+it.title);actions.appendChild(view);
  actions.appendChild(radarSaveButton(it.uri,it.title,msg));
  const p=node('button','btn btn-ghost btn-sm','Add skills to Plan');p.type='button';
  const skillUris=terms.map(s=>s.uri).filter(Boolean);
  const inPlan=()=>skillUris.length>0&&skillUris.every(uri=>((FT.state.roadmap_goals[it.uri])||[]).includes(uri));
  const paint=()=>{p.textContent=inPlan()?'Skills in Plan':'Add skills to Plan';p.classList.toggle('ft-saved',inPlan());p.setAttribute('aria-pressed',String(inPlan()))};paint();
  p.addEventListener('click',async()=>{if(!skillUris.length)return;p.disabled=true;try{await ftSave(x=>{const goals=new Set(x.roadmap_goals[it.uri]||[]);skillUris.forEach(uri=>goals.add(uri));x.roadmap_goals[it.uri]=[...goals]});paint();ftLive('Skills added to the learning plan. This does not confirm mastery.')}catch(e){msg.innerHTML='<div class="ft-err" role="alert">'+esc(e.message)+'</div>'}p.disabled=false;p.focus()});
  actions.appendChild(p);el.appendChild(msg);
  return el;
}
function actualJobCard(it){
  const match=it.occupation_match||null;
  const matchText=!match?'No ESCO occupation match':
    match.status==='exact_title'?'Exact ESCO title match · '+(match.label||''):
    match.status==='semantic_suggested'?'Possible ESCO match · '+(match.label||''):
    '';
  const matchClass=match&&match.status==='exact_title'?'ft-job-match exact':'ft-job-match';
  const workplace=it.workplace_type==='unspecified'
    ?(it.remote===true?'Remote':'Work setting not provided')
    :(it.workplace_type==='on-site'?'On-site':it.workplace_type==='hybrid'?'Hybrid':'Remote');
  const date=it.posted_date?'Posted '+radarDate(it.posted_date):
    it.source_updated_at?'Updated '+radarDate(it.source_updated_at):'Posting date not provided';
  const salary=it.salary_text||((it.salary_min!=null||it.salary_max!=null)
    ?[(it.salary_currency||''),it.salary_min!=null?Number(it.salary_min).toLocaleString():null,
      it.salary_max!=null?Number(it.salary_max).toLocaleString():null]
      .filter(Boolean).join(' ')+(it.salary_period?' · '+it.salary_period:''):'');
  const passport=(it.matched_passport_skills||[]).map(s=>'<span class="ft-tag sage">'+esc(s.label)+'</span>').join('');
  const adOnly=(it.ad_skills_not_in_passport||[]).slice(0,5);
  const adTags=adOnly.map(s=>'<span class="ft-tag">'+esc(s.label)+'</span>').join('');
  const evidence=(it.explicit_skills||[]).slice(0,6).map(s=>
    '<div class="ft-radar-evidence-row"><b>'+esc(s.label||'ESCO skill')+
    '</b>'+(s.evidence_quote?'<span class="ft-radar-evidence-meta">'+esc(s.evidence_quote)+'</span>':'')+
    '<span class="ft-radar-evidence-method">ESCO candidate plus literal wording in the ad</span></div>'
  ).join('');
  const desc=it.description?'<details><summary>Job details</summary><p class="ft-real-job-desc">'+esc(it.description)+'</p></details>':'';
  const mapping=match?'<details><summary>Why this ESCO label?</summary><p class="ft-note">'+
    (match.status==='exact_title'
      ?'The normalized job title matches an ESCO preferred or alternate title. This links the ad title; it does not verify the role requirements.'
      :'Fine-tuned MiniLM retrieved this as a semantic candidate using the title, duties and extracted skill evidence. It is a suggestion, not an independently verified match or a probability.')+
    '</p>'+((it.semantic_candidates||[]).length&&match.status!=='exact_title'
      ?'<ol class="ft-note">'+it.semantic_candidates.slice(0,3).map(c=>'<li>'+esc(c.label)+' · cosine '+Number(c.cosine_similarity).toFixed(3)+'</li>').join('')+'</ol><p class="ft-note">Similarity is not confidence or a probability.</p><p class="ft-note">'+esc(it.matching_text||'')+'</p>':'')+
    (match.supporting_skill_uris&&match.supporting_skill_uris.length
      ?'<p class="ft-note">Related ESCO skill evidence: '+esc(match.supporting_skill_uris.length)+' exact skill link(s).</p>':'')+
    '</details>':'';
  const link=ftSafeUrl(it.url);
  const action=link?'<a class="btn btn-primary btn-sm" href="'+esc(link)+'" target="_blank" rel="noopener noreferrer">'+
    (it.source==='himalayas'?'Apply via Himalayas':'View job via '+esc(it.source_label||'source'))+' ↗</a>':'';
  const card=node('article','ft-card ft-real-job');
  card.innerHTML=(matchText?'<div class="'+matchClass+'">'+esc(matchText)+'</div>':'')+
    '<h3>'+esc(it.title)+'</h3><p class="ft-real-job-meta">'+
    esc(it.employer||'Employer not provided')+' · '+esc(workplace)+' · '+esc(it.location||it.country||'Location not provided')+
    '<br>'+esc(it.source_label||'Job source')+' · '+esc(date)+
    (it.collected_at?' · Collected '+esc(radarDate(it.collected_at)):'')+
    (it.seniority?' · '+esc(it.seniority):'')+(it.employment_type?' · '+esc(it.employment_type):'')+
    (salary?' · '+esc(salary):'')+'</p>'+
    (it.confirmed_skill_match_count
      ?'<div class="ft-job-skill-tags" aria-label="Confirmed Passport skills mentioned in this ad">'+passport+'</div>'+
       '<p class="ft-note">'+esc(it.confirmed_skill_match_count)+' exact Passport skill match'+(it.confirmed_skill_match_count===1?'':'es')+
       '. Other confirmed skills are not mentioned in this ad; that does not say whether you have them.</p>'
      :'<p class="ft-note">No exact confirmed Passport skill mention was found in this ad. That does not indicate your qualifications.</p>')+
    (adTags?'<div><div class="ft-job-skill-tags">'+adTags+'</div></div>':'')+
    desc+(evidence?'<details><summary>Skill evidence ('+esc((it.explicit_skills||[]).length)+')</summary><div class="ft-radar-evidence">'+evidence+'</div></details>':'')+
    mapping+'<div class="ft-actions">'+action+'</div>';
  return card;
}
function renderJobResults(){
  const area=$('cr-job-listings');if(!area)return;
  area.replaceChildren();
  if(jobListingError){
    area.innerHTML='<div class="ft-err" role="alert"><span>'+esc(jobListingError)+'</span><button type="button" class="btn btn-ghost btn-sm" id="job-listings-retry">Try again</button></div>';
    $('job-listings-retry').addEventListener('click',loadActualJobPostings);return;
  }
  if(!jobListingData){area.innerHTML='<div class="skel ft-skel"></div>';return}
  const items=jobListingData.postings||[];
  if(!items.length){
    area.appendChild(node('div','ft-state','No listings match these filters in the current collected sample.'));
    return;
  }
  const grid=node('div','ft-grid');items.forEach(item=>grid.appendChild(actualJobCard(item)));area.appendChild(grid);
  const aggregate=((radar||{}).job_postings||radar.jobs||[]);
  if(aggregate.length){
    const details=node('details','ft-meth');
    details.innerHTML='<summary>Role-level evidence from ads (not individual openings)</summary><div class="ft-grid" style="margin-top:8px"></div>';
    const roleGrid=details.querySelector('.ft-grid');
    aggregate.slice(0,12).forEach(item=>roleGrid.appendChild(jobPostingCard(item)));
    area.appendChild(details);
  }
}
function drawJobTab(host){
  const passport=(FT.state&&FT.state.confirmed_skills)||[];
  const skillOptions=passport.filter(s=>s&&s.uri).map(s=>'<option value="'+esc(s.uri)+'">'+esc(s.label||s.uri)+'</option>').join('');
  host.innerHTML='<form class="ft-job-filters" id="job-filter-form">'+
    '<input id="job-q" type="search" maxlength="100" placeholder="Search job title or company" aria-label="Search job title or company">'+
    '<input id="job-occupation" type="search" maxlength="100" placeholder="Filter by occupation" aria-label="Filter by occupation">'+
    '<input id="job-location" type="search" maxlength="100" placeholder="Location or country" aria-label="Filter by location">'+
    '<select id="job-workplace" aria-label="Filter by work setting"><option value="">Any work setting</option><option value="remote">Remote only</option><option value="non_remote">Not fully remote</option></select>'+
    '<input id="job-skill" type="search" maxlength="100" placeholder="Skill named in the ad" aria-label="Filter by skill named in the ad">'+
    '<select id="job-skill-uri" aria-label="Match a confirmed Passport skill"><option value="">Any Passport skill</option>'+skillOptions+'</select>'+
    '<div class="ft-job-filter-actions"><button type="submit" class="btn btn-primary btn-sm">Search jobs</button><button type="button" class="btn btn-ghost btn-sm" id="job-filters-clear">Clear</button></div></form>'+
    '<div id="cr-job-listings" aria-live="polite"></div>';
  $('job-q').value=jobFilters.q;$('job-occupation').value=jobFilters.occupation;
  $('job-location').value=jobFilters.location;$('job-workplace').value=jobFilters.workplace;
  $('job-skill').value=jobFilters.skill;$('job-skill-uri').value=jobFilters.skill_uri;
  $('job-filter-form').addEventListener('submit',e=>{
    e.preventDefault();jobFilters={q:$('job-q').value.trim(),occupation:$('job-occupation').value.trim(),
      location:$('job-location').value.trim(),workplace:$('job-workplace').value,
      skill:$('job-skill').value.trim(),skill_uri:$('job-skill-uri').value};
    jobListingData=null;jobListingError='';loadActualJobPostings();
  });
  $('job-filters-clear').addEventListener('click',()=>{
    jobFilters={q:'',occupation:'',location:'',workplace:'',skill:'',skill_uri:''};
    jobListingData=null;jobListingError='';drawJobTab(host);
  });
  renderJobResults();
  if(!jobListingData&&!jobListingError)loadActualJobPostings();
}
async function loadActualJobPostings(){
  const area=$('cr-job-listings');if(!area)return;
  const sequence=++jobLoadSequence;
  jobListingError='';area.innerHTML='<div class="skel ft-skel"></div><div class="skel ft-skel"></div>';
  const p=new URLSearchParams({limit:'50'});
  Object.entries(jobFilters).forEach(([key,value])=>{if(value)p.set(key,value)});
  try{
    const data=await ftReq(ftPath('/api/my-future/job-postings?'+p.toString()));
    if(sequence!==jobLoadSequence)return;
    jobListingData=data;jobListingError='';renderJobResults();
  }catch(e){
    if(sequence!==jobLoadSequence)return;
    jobListingData=null;jobListingError=e.message||'Job listings could not be loaded.';
    renderJobResults();
  }
}
function drawRadar(){
  const host=$('cr-radar-body'),summary=$('cr-radar-summary');host.replaceChildren();
  document.querySelectorAll('[data-rtab]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.rtab===radarTab)));
  if(!radar)return;
  const c=radar.coverage||{},sources=Object.keys(c.sources||{}).map(radarSourceName),days=c.collection_days||[];
  const dayText=days.length===1?'collected '+radarDate(days[0])+' (one day)':days.length?('collected across '+days.length+' days'):'collection date not recorded';
  summary.textContent=(c.posting_count||0)+' ads · '+(sources.join(', ')||'sources not recorded')+' · '+dayText+' · mixed locations';
  if(radar.status==='unavailable'){host.innerHTML='<div class="ft-state"><b>Job data unavailable</b>'+esc(radar.reason||'Stored posting evidence could not be loaded.')+'</div>';return}
  if(radarTab==='growth'){
    const growth=radar.growing_careers||{};
    host.innerHTML='<div class="ft-state"><b>Not enough comparable history</b>'+esc(growth.reason||'Repeated collection periods are needed before showing hiring growth.')+'</div>';return
  }
  if(radarTab==='jobs'){
    const jobs=radar.job_postings||radar.jobs||[];
    drawJobTab(host);return
  }
  const skillItems=radar.skills||[];
  if(!skillItems.length){host.innerHTML='<div class="ft-state"><b>No explicit skill mentions yet</b>ESCO skill candidates are shown only when the original ad also contains the named term.</div>';return}
  const shownSkills=skillItems.slice(0,radarVisible.skills),sg=node('div','ft-grid');shownSkills.forEach(i=>sg.appendChild(skillCard(i)));host.appendChild(sg);
  const moreSkills=radarMoreButton('skills',skillItems.length,'skill mentions');if(moreSkills)host.appendChild(moreSkills);
  const careers=radar.skill_related_careers||[];
  const heading=node('h3','ft-radar-subhead','Related career ideas · not job openings');
  host.appendChild(heading);
  if(!careers.length){host.appendChild(node('div','ft-state','No career suggestions meet the current multi-skill evidence rule.'));return}
  const shownCareers=careers.slice(0,radarVisible.careers),cg=node('div','ft-grid');shownCareers.forEach(i=>cg.appendChild(skillCareerCard(i)));host.appendChild(cg);
  const moreCareers=radarMoreButton('careers',careers.length,'career ideas');if(moreCareers)host.appendChild(moreCareers);
}
async function loadRadar(){
  const host=$('cr-radar-body');host.innerHTML='<div class="skel ft-skel"></div>';
  try{radar=await ftReq(ftPath('/api/my-future/opportunities?limit=30'));
    const m=$('cr-radar-meth');m.replaceChildren();
    (radar.methodology||[]).forEach(t=>m.appendChild(node('p','ft-note',typeof t==='string'?t:JSON.stringify(t))));
    const c=radar.coverage||{},range=c.posting_date_range||{};
    if(range.first||range.last)m.appendChild(node('p','ft-note','Original posting dates: '+(range.first||'not recorded')+' to '+(range.last||'not recorded')+'. These are ad publication dates, not the collection period.'));
    if(c.geography)m.appendChild(node('p','ft-note','Sample geography: '+c.geography));
    (c.collection_windows||[]).forEach(w=>m.appendChild(node('p','ft-note',radarSourceName(w.source)+' collection window: '+(w.started_at||'start not recorded')+' to '+(w.finished_at||'end not recorded')+'.')));
    const counts=radar.counts||{};
    m.appendChild(node('p','ft-note','Current sample: '+(counts.title_matched_ad_count||0)+' distinct title-matched ads; '+(counts.skill_related_career_candidate_count||0)+' separate skill-related career candidates; '+(counts.explicit_skill_count||0)+' explicit skill terms; '+(counts.supported_esco_occupation_count||0)+' distinct ESCO occupations supported.'));
    m.appendChild(node('p','ft-note','Passport comparisons use exact ESCO URIs from your saved confirmed skills. An absent match is not evidence that you lack a skill.'));
    drawRadar()}
  catch(e){host.innerHTML='<div class="ft-err" role="alert"><span>'+esc(e.message)+'</span><button type="button" class="btn btn-ghost btn-sm" id="radar-retry">Try again</button></div>';$('radar-retry').addEventListener('click',loadRadar)}
}
function initRadar(){
  document.querySelectorAll('[data-rtab]').forEach(b=>b.addEventListener('click',()=>{radarTab=b.dataset.rtab;drawRadar()}));
  $('cr-cmp-go').addEventListener('click',runCompare);
  $('cr-cmp-clear').addEventListener('click',()=>{cmp.clear();recAll.forEach(c=>c.compared=false);updCmp();drawList($('cr-recs'),recAll,recShown,$('cr-recs-more'))});
  loadRadar();
}
/* ---------- selected career: tabs + intelligence ---------- */
let crTab='tasks';
function ftSummary(){
  const te=D.task_exposure||{},I=D.intelligence||{},adv=I.advancement||{};
  const av=te.status==='available';
  const share=te.predicted_task_exposure||{},hasShare=share.status==='available'&&ftNum(share.percentage)!==null;
  const c1=hasShare?'<strong>'+esc(ftPct(share.percentage))+'</strong> · '+esc(share.numerator)+' of '+esc(share.denominator)+' tasks classified E1 or E2':av?'Class counts available; predicted share unavailable':te.status==='uncertain_mapping'?'Possible mapping only: no distribution shown':'Not enough exact task data';
  const nseries=(adv.series||[]).length;
  const c2=adv.status==='available'&&nseries?'Available: '+nseries+' measured benchmark series':'Not available'+(adv.reason?': '+esc(adv.reason):'');
  const it=(t,v)=>'<div class="ft-card" style="padding:12px"><div class="ft-note">'+t+'</div><div style="font-size:14px;margin-top:4px">'+v+'</div></div>';
  return '<section class="ft-sec" aria-labelledby="ai-h"><h2 id="ai-h">AI &amp; This Career</h2><div class="ft-grid" style="margin-top:10px">'+it('Predicted task-exposure share',c1)+it('Measured AI advancement',c2)+'</div></section>';
}
function relItems(){
  const st=D.stress_test||{},ins=D.insurance||{},cm=ins.comparison||{};
  const raw=[...(st.related_careers||[]),...(cm.alternatives||[]),...(cm.suggestions||[])];
  const seen=new Set([uri]),out=[];
  raw.forEach(r=>{const u=r&&r.uri,l=r&&(r.label||r.title);if(u&&l&&!seen.has(u)){seen.add(u);out.push({uri:u,label:l})}});
  return out.slice(0,6);
}
function relRow(r){
  const el=node('div','ft-skill-row');el.appendChild(node('span','',r.label));
  const a=node('div','ft-actions');
  const v=node('a','btn btn-ghost btn-sm','View');v.href=ftPath('/career?occupation_uri=')+encodeURIComponent(r.uri);v.setAttribute('aria-label','View '+r.label);
  const s=node('button','btn btn-ghost btn-sm');s.type='button';
  const g=node('button','btn btn-ghost btn-sm');g.type='button';
  const paint=()=>{const on=ftSaved(r.uri),go=ftGoal()===r.uri;s.textContent=on?'Saved':'Save';s.classList.toggle('ft-saved',on);s.setAttribute('aria-pressed',String(on));s.setAttribute('aria-label',(on?'Remove ':'Save ')+r.label);g.textContent=go?'My Goal':'Set Goal';g.classList.toggle('ft-saved',go);g.setAttribute('aria-pressed',String(go))};paint();
  const run=(b,fn)=>async()=>{b.disabled=true;try{await fn();paint();ftLive('Updated.')}catch(e){el.appendChild(node('div','ft-err',e.message))}b.disabled=false;b.focus()};
  s.addEventListener('click',run(s,()=>ftToggleSave(r.uri)));g.addEventListener('click',run(g,()=>ftSetGoal(r.uri)));
  a.append(v,s,g);el.appendChild(a);return el;
}
async function fillRelated(){
  const box=$('cr-related');if(!box)return;
   let items=((D.career_map||{}).occupations||[]).filter(r=>!r.is_selected&&r.uri!==uri);
   if(!items.length)items=relItems();
  box.replaceChildren();
   if(!items.length){box.appendChild(node('p','ft-note','Not enough ESCO comparison data to show related careers.'));return}
  items.forEach(r=>box.appendChild(relRow(r)));
}
function ftTabify(h){
  const tabs=[['tasks','AI Tasks'],['skills','Skills'],['jobs','Jobs']];
  const bar='<div class="ft-tabs" role="tablist" aria-label="Career evidence">'+tabs.map(t=>'<button type="button" role="tab" id="crt-'+t[0]+'" data-crtab="'+t[0]+'" aria-selected="'+(crTab===t[0])+'" aria-controls="crp-'+t[0]+'">'+t[1]+'</button>').join('')+'</div>';
  const pan=(k,inner)=>'<div role="tabpanel" id="crp-'+k+'" aria-labelledby="crt-'+k+'" '+(crTab===k?'':'hidden')+'>'+inner+'</div>';
  return [h[0],h[1],h[2],h[3],ftSummary(),bar,pan('tasks',h[6]),pan('skills',h[4]+h[5]),pan('jobs','<section class="ft-sec"><h2>Jobs</h2><div class="ft-card" style="margin:10px 0"><h3 style="font:700 15px var(--body);margin:0 0 4px">Related careers</h3><div id="cr-related"></div></div></section>'),h[7]];
}
function wireTabs(){
  const bs=[...document.querySelectorAll('[data-crtab]')];
  const sel=k=>{crTab=k;bs.forEach(b=>{const on=b.dataset.crtab===k;b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;$('crp-'+b.dataset.crtab).hidden=!on})};
  bs.forEach((b,i)=>{b.tabIndex=b.dataset.crtab===crTab?0:-1;b.addEventListener('click',()=>sel(b.dataset.crtab));
    b.addEventListener('keydown',e=>{const j=e.key==='ArrowRight'?(i+1)%bs.length:e.key==='ArrowLeft'?(i-1+bs.length)%bs.length:-1;if(j>=0){e.preventDefault();sel(bs[j].dataset.crtab);bs[j].focus()}})});
}
'''
