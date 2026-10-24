"""Compact, non-probabilistic presentation of actual local classifier outputs."""
EXPOSURE_CSS = r'''
.task-exposure{padding-bottom:16px;margin-bottom:16px;border-bottom:1px solid var(--line)}
.task-exposure h3{font-size:16px;margin:0 0 8px}
.task-exposure .exposure-caution{padding:10px 12px;border-left:3px solid #c29042;background:#fbf7ee;border-radius:6px}
.task-exposure .exposure-row{display:grid;grid-template-columns:32px 1fr 100px;gap:10px;align-items:center;margin:8px 0;font-size:13px}
.exposure-track{height:7px;background:var(--line2);border-radius:5px;overflow:hidden}
.exposure-track i{display:block;height:100%;background:var(--harbor);border-radius:5px}
.exposure-count{text-align:right;font-variant-numeric:tabular-nums}
.task-exposure details{margin-top:12px;font-size:13px}
.task-exposure summary{color:var(--harbor);cursor:pointer;min-height:32px}
.exposure-task{padding:10px 0;border-bottom:1px solid var(--line2)}
.exposure-task strong{display:inline-block;margin-right:8px;color:var(--harbor)}
.exposure-mapping{padding:10px 0;border-top:1px solid var(--line2)}
.exposure-source-link{color:var(--harbor);text-decoration:underline}
.task-exposure code{overflow-wrap:anywhere}
.xd{display:grid;grid-template-columns:170px minmax(0,1fr);gap:16px;align-items:center;margin:6px 0 10px;position:relative}
.xd svg{width:170px;height:170px;display:block}
.xd circle.seg{cursor:pointer;transition:opacity .15s}
.xd circle.seg:hover,.xd circle.seg:focus-visible{opacity:.8;outline:none;stroke-width:26}
.xd circle.seg.dim{opacity:.3}
.xd-c{font:700 22px var(--body);fill:var(--ink)}.xd-s{font:500 10px var(--body);fill:var(--muted)}
.xd-leg{display:grid;gap:6px}
.xd-leg button{display:flex;align-items:center;gap:8px;text-align:left;border:1px solid var(--line);background:var(--paper);border-radius:8px;padding:8px 10px;font-size:13px;color:var(--ink);min-height:44px}
.xd-leg button:hover{background:var(--paper2)}
.xd-leg button[aria-pressed=true]{border-color:var(--harbor);background:var(--harbor-soft)}
.xd-leg i{width:12px;height:12px;border-radius:3px;flex:none}
.xd-tip{position:absolute;left:0;top:176px;background:var(--ink);color:#fcfdfe;font-size:12px;border-radius:6px;padding:6px 9px;pointer-events:none;max-width:240px;z-index:3}
.xd-filter{font-size:13px;color:var(--ink2);margin:6px 0}
@media(max-width:600px){.xd{grid-template-columns:1fr;justify-items:center}.xd-leg{width:100%}}
@media(max-width:600px){.task-exposure .exposure-row{grid-template-columns:30px 1fr 86px;gap:7px}.exposure-count{font-size:12px}}
'''

EXPOSURE_JS = r'''
function exSafe(u){try{const x=new URL(u,location.origin);return(x.protocol==='http:'||x.protocol==='https:')?x.href:''}catch(_e){return''}}
function renderTaskExposure(host,data){
 if(!host)return;host.replaceChildren();
 const box=node('section','task-exposure');box.setAttribute('aria-label','Local task classification');host.appendChild(box);
 box.appendChild(node('h3','','O*NET task classes'));
 const available=data&&data.status==='available';
 const candidates=data&&data.candidate_mappings||[];
 if(!data||(!available&&data.status!=='uncertain_mapping')){
  const text=data&&data.status==='not_enough_task_data'?'Not enough linked O*NET task data':data&&data.status==='not_precomputed'?'Official task predictions have not been precomputed':'Local task database or classifier unavailable';
  box.appendChild(node('p','ft-note',text));return;
 }
 if(available){
  const n=data.sample_task_count;
  const COLS={E0:'#0b5cab',E1:'#a86414',E2:'#5b4a99'},LAB=['E0','E1','E2'];
   let pick=null,shownN=10;
   const wrap=node('div','xd');box.appendChild(wrap);
   const total=LAB.reduce((t,l)=>t+(Number(data.distribution[l].count)||0),0);
   const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox','0 0 140 140');svg.setAttribute('role','group');svg.setAttribute('aria-label','Task class distribution, three unordered categories, unweighted task counts');
   const R=52,C=2*Math.PI*R;let off=0;const segs={};
   const tip=node('div','xd-tip');tip.hidden=true;tip.setAttribute('role','status');
   const showTip=l=>{const d=data.distribution[l];tip.textContent=l+': '+d.count+' of '+n+' tasks ('+d.percentage+'%)';tip.hidden=false};
   LAB.forEach(l=>{const c=Number(data.distribution[l].count)||0;if(!c||!total)return;const len=C*c/total;
    const ci=document.createElementNS(NS,'circle');ci.setAttribute('class','seg');ci.setAttribute('cx','70');ci.setAttribute('cy','70');ci.setAttribute('r',R);ci.setAttribute('fill','none');ci.setAttribute('stroke',COLS[l]);ci.setAttribute('stroke-width','22');
    ci.setAttribute('stroke-dasharray',len+' '+(C-len));ci.setAttribute('stroke-dashoffset',String(-off));ci.setAttribute('transform','rotate(-90 70 70)');ci.setAttribute('tabindex','0');ci.setAttribute('role','button');
    ci.setAttribute('aria-label','Class '+l+': '+c+' of '+n+' tasks. Activate to filter tasks.');
    ci.addEventListener('mouseenter',()=>showTip(l));ci.addEventListener('focus',()=>showTip(l));ci.addEventListener('mouseleave',()=>tip.hidden=true);ci.addEventListener('blur',()=>tip.hidden=true);
    ci.addEventListener('click',()=>toggle(l));ci.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle(l)}});
    svg.appendChild(ci);segs[l]=ci;off+=len});
   const t1=document.createElementNS(NS,'text');t1.setAttribute('x','70');t1.setAttribute('y','72');t1.setAttribute('text-anchor','middle');t1.setAttribute('class','xd-c');t1.textContent=String(n);
   const t2=document.createElementNS(NS,'text');t2.setAttribute('x','70');t2.setAttribute('y','86');t2.setAttribute('text-anchor','middle');t2.setAttribute('class','xd-s');t2.textContent='tasks';
   svg.append(t1,t2);wrap.appendChild(svg);
   const leg=node('div','xd-leg');wrap.appendChild(leg);wrap.appendChild(tip);
   const btns={};
   LAB.forEach(l=>{const d=data.distribution[l],b=node('button');b.type='button';b.setAttribute('aria-pressed','false');
    const sw=node('i');sw.style.background=COLS[l];b.appendChild(sw);b.appendChild(node('span','','Class '+l+' · '+d.count+' of '+n+' · '+d.percentage+'%'));
    b.addEventListener('click',()=>toggle(l));btns[l]=b;leg.appendChild(b)});
   const filt=node('p','xd-filter');filt.setAttribute('aria-live','polite');box.appendChild(filt);
   const tasks=node('details');tasks.open=false;const sum=node('summary','','Inspect classified tasks ('+n+')');tasks.appendChild(sum);
   const list=node('div');tasks.appendChild(list);box.appendChild(tasks);
   function toggle(l){pick=pick===l?null:l;shownN=10;paint()}
   function paint(){
    LAB.forEach(l=>{btns[l].setAttribute('aria-pressed',String(pick===l));if(segs[l])segs[l].classList.toggle('dim',!!pick&&pick!==l)});
    const all=(data.tasks||[]).filter(t=>!pick||t.label===pick);
    filt.textContent=pick?'Showing '+all.length+' task(s) in class '+pick+'. Select it again to clear.':'';
    list.replaceChildren();all.slice(0,shownN).forEach(t=>appendExposureTask(list,t));
    if(all.length>shownN){const m=node('button','btn btn-ghost btn-sm ft-more','Show more ('+(all.length-shownN)+')');m.type='button';m.addEventListener('click',()=>{shownN+=10;paint()});list.appendChild(m)}
    if(!all.length)list.appendChild(node('p','ft-note','No stored task records for this class.'));
   }
   paint();
   if(data.near_tie_e1_e2_task_count)box.appendChild(node('p','ft-note',data.near_tie_e1_e2_task_count+' task(s) have a close E1/E2 model-score split.'));
 }else{
  box.appendChild(node('p','exposure-caution','No exact occupation mapping is available, so no occupation-level class distribution is reported. Possible crosswalk relationships are shown separately.'));
 }
  if(!data.label_definitions_verified)box.appendChild(node('p','ft-note','Training-label provenance is unverified; no predicted exposure share is shown.'));
 if(candidates.length){
  const candidateDetails=node('details');
  candidateDetails.appendChild(node('summary','','Possible O*NET mappings ('+candidates.length+')'));
  candidates.forEach(mapping=>{
   const panel=node('article','exposure-mapping');
   panel.appendChild(node('strong','',mapping.relationship+' · O*NET-SOC '+mapping.onet_soc_code));
   panel.appendChild(node('p','',mapping.onet_occupation+' · '+mapping.task_record_count+' source tasks'));
   panel.appendChild(node('p','ft-note','Possible task set only; not included in the exact-match distribution.'));
   const mix=node('details');mix.appendChild(node('summary','','Class shares in this source task set'));
   ['E0','E1','E2'].forEach(label=>{
    const d=mapping.distribution[label];
    mix.appendChild(node('p','ft-note',label+': '+(d.percentage===null?'Not enough data':d.count+' / '+mapping.classified_task_count+' · '+d.percentage+'%')));
   });
   panel.appendChild(mix);
   const taskDetails=node('details');taskDetails.appendChild(node('summary','','View source tasks ('+mapping.task_record_count+')'));
   (mapping.tasks||[]).forEach(task=>appendExposureTask(taskDetails,task));
   panel.appendChild(taskDetails);
   const source=node('a','exposure-source-link',mapping.source+' · '+mapping.mapping_version+' ('+mapping.mapping_date+')');
   source.href=exSafe(data.mapping_source.url);source.target='_blank';source.rel='noopener noreferrer';panel.appendChild(source);
   candidateDetails.appendChild(panel);
  });
  box.appendChild(candidateDetails);
 }
 const details=node('details');details.appendChild(node('summary','','Sources, definitions and method'));
 const onet=node('a','exposure-source-link',data.source.name+' · CC BY 4.0');
 onet.href=exSafe(data.source.url);onet.target='_blank';onet.rel='noopener noreferrer';details.appendChild(onet);
 details.appendChild(node('p','ft-note',data.source.attribution));
 const crosswalk=node('a','exposure-source-link',data.mapping_source.name);
 crosswalk.href=exSafe(data.mapping_source.url);crosswalk.target='_blank';crosswalk.rel='noopener noreferrer';details.appendChild(crosswalk);
 details.appendChild(node('p','ft-note',data.mapping_source.attribution));
 details.appendChild(node('p','ft-note',data.mapping_source.relationship_note));
 const versions=data.mapping_source.published_metadata||{};
 if(versions['Classification 1 Version'])details.appendChild(node('p','ft-note','Crosswalk versions: '+versions['Classification 1 Version']+' → ESCO '+versions['Classification 2 Version']+' · '+versions['Mapping project version date']));
 details.appendChild(node('p','ft-note',data.model&&data.model.label_definition_note||'E0/E1/E2 definitions are unverified.'));
  const contract=(data.model||{}).label_contract||{};
  if(contract.training_label_contract_verified){
   ['E0','E1','E2'].forEach(label=>details.appendChild(node('p','ft-note',label+': '+((contract.definitions||{})[label]||'Not documented'))));
   details.appendChild(node('p','ft-note',contract.e3_note||''));
   details.appendChild(node('p','ft-note',contract.verification_scope||''));
   details.appendChild(node('p','ft-note','Predicted task-exposure share = (E1 + E2 task records) / assessed task records × 100. Based on historical GPT-4 annotations, not live AI performance or employment outcomes.'));
  }
 details.appendChild(node('p','ft-note',data.combined_exposure_note||'No combined exposure score is calculated.'));
 details.appendChild(node('p','ft-note',data.uncertainty_method||'Softmax outputs are not calibrated confidence.'));
 if(data.model){
  details.appendChild(node('p','ft-note','Local CPU inference · checkpoint SHA-256:'));
  details.appendChild(node('code','',data.model.checkpoint_fingerprint));
 }
  const rep=node('div','ft-note');rep.appendChild(node('strong','',contract.training_label_contract_verified?'Package-reported held-out evaluation':'User-reported historical evaluation'));
 const he=(data.model||{}).historical_evaluation;
 const pc=v=>typeof v==='number'?(100*v).toFixed(1)+'%':'not stated';
 if(he){
  const tbl=node('div');
   [['E0 F1',pc(he.E0_f1)],['E1 F1',pc(he.E1_f1)],['E2 F1',pc(he.E2_f1)],['Macro F1',pc(he.macro_f1)],['Accuracy',pc(he.accuracy)],['Test samples',he.test_samples||'not stated'],['Accuracy independently reproduced',he.independently_verified?'Yes':'No']].forEach(r=>{const row=node('div','ft-kv');row.appendChild(node('span','',r[0]));row.appendChild(node('b','',r[1]));tbl.appendChild(row)});
  rep.appendChild(tbl);
  if(he.source)rep.appendChild(node('p','ft-note',he.source));
  if(he.limitation)rep.appendChild(node('p','ft-note',he.limitation));
 }else rep.appendChild(node('p','ft-note','No historical evaluation metadata was returned.'));
 rep.appendChild(node('p','ft-note','This is not a new validation run, and softmax outputs are not confidence or risk.'));
 if(data.model&&data.model.max_token_length)rep.appendChild(node('p','ft-note','Maximum input length: '+data.model.max_token_length+' tokens.'));
 if(data.model&&data.model.prediction_fingerprint){rep.appendChild(node('p','ft-note','Prediction method fingerprint:'));rep.appendChild(node('code','',data.model.prediction_fingerprint))}
 details.appendChild(rep);
 box.appendChild(details);
}
function appendExposureTask(parent,task){
 const item=node('article','exposure-task');
 const name=node('strong','',task.label||'Prediction pending');item.appendChild(name);
 item.appendChild(node('span','',task.text||''));
 item.appendChild(node('p','ft-note','O*NET-SOC '+task.onet_soc_code+' · Task '+task.task_id+' · '+(task.task_type||'Task')+' · '+(task.task_date||'')));
 if(task.domain_source)item.appendChild(node('p','ft-note','Source: '+task.domain_source));
 if(task.near_tie_e1_e2)item.appendChild(node('p','ft-note','Near-tie E1/E2 model scores; not calibrated confidence.'));
 if(task.label&&task.probabilities){
  const more=node('details');more.appendChild(node('summary','','Model outputs'));
  more.appendChild(node('p','ft-note','Softmax scores are not calibrated confidence or replacement probabilities.'));
  ['E0','E1','E2'].forEach(label=>more.appendChild(node('div','',label+': '+(100*task.probabilities[label]).toFixed(2)+'%')));
  more.appendChild(node('p','ft-note','Top-two raw-score gap: '+(100*(task.top_two_score_gap||0)).toFixed(2)+' percentage points.'));
  if(task.truncated)more.appendChild(node('p','ft-note','Input truncated to the model maximum length.'));
  item.appendChild(more);
 }
 parent.appendChild(item);
}
'''
