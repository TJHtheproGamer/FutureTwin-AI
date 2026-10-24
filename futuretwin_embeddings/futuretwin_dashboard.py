"""FutureTwin career exploration and workforce intelligence dashboards."""
from __future__ import annotations

import os
from flask import Response, jsonify, request

from futuretwin_esco_normalized_api import app
from futuretwin_pages import CAREER_HTML, HOME_HTML, MY_CAREER_HTML, TRENDS_HTML
from futuretwin_my_future_page import MY_FUTURE_HTML
from futuretwin_resume_api import register_resume_routes
from futuretwin_exposure_api import register_exposure_routes
from futuretwin_sdg_api import register_sdg_routes

register_resume_routes(app)
register_exposure_routes(app)
register_sdg_routes(app)


DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="light" />
<title>FutureTwin · Job Intelligence</title>
<style>
:root{--navy:#0a1b2d;--navy2:#132a42;--sky:#1d6d87;--blue:#176b88;--teal:#0d806d;--ink:#172b40;--muted:#687b8d;--bg:#f4f7fa;--line:#e5ecf1;--paper:#fff;--radius:16px}
*{box-sizing:border-box} body{margin:0;min-height:100vh;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:-.009em}
button,textarea,select{font:inherit}button{cursor:pointer}button:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid #8bcddb;outline-offset:2px}
.shell{display:flex;min-height:100vh}.sidebar{flex:0 0 238px;background:var(--navy);color:#fff;display:flex;flex-direction:column;padding:29px 18px;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:12px;padding:2px 12px 36px}.brand-logo{height:38px;width:38px;border:1px solid #63b3be55;border-radius:12px;background:linear-gradient(135deg,#176f86,#194261);display:grid;place-items:center;font-weight:800;font-size:15px;letter-spacing:-1px;box-shadow:0 4px 22px #3a9eb126}.brand b{display:block;letter-spacing:-.045em;font-size:20px;line-height:1.1}.brand small{font-size:10px;letter-spacing:.19em;color:#9aafc0;text-transform:uppercase}
.sidetitle{color:#8099ac;letter-spacing:.15em;text-transform:uppercase;font-size:10px;font-weight:700;padding:0 13px;margin:10px 0 10px}.navitem{display:flex;align-items:center;gap:12px;border-radius:10px;padding:12px 13px;font-size:13px;color:#b9cbda;margin-bottom:5px}.navitem.active{background:#1c4055;color:#e6fcfc;font-weight:650;border:1px solid #30637a}.navicon{font-size:17px;width:22px;text-align:center;opacity:.9}.sideline{height:1px;background:#294057;margin:15px 11px 24px}.sidebar-bottom{margin-top:auto;padding:17px 13px;background:#122c43;border:1px solid #29465c;border-radius:12px}.sidebar-bottom .live{color:#b1e3dc;font-weight:700;font-size:12px}.small-dot{width:8px;height:8px;border-radius:50%;background:#67ccb6;display:inline-block;margin-right:6px}.sidebar-bottom p{font-size:11px;line-height:1.65;color:#a4b8c8;margin-bottom:0}
.content{flex:1;min-width:0;padding:0 40px 55px;max-width:1670px;margin:0 auto}.topbar{height:81px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.topbar .crumb{font-size:13px;color:#718597}.crumb strong{color:#23374d;font-weight:700}.top-right{display:flex;align-items:center;gap:11px}.pill{border:1px solid #d5e7e7;color:#237668;background:#edfaf7;padding:7px 12px;border-radius:100px;font-size:11px;font-weight:750}.version{font-size:12px;color:#7990a0}
.pagehead{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin:27px 0 21px}.kicker{font-size:11px;color:#0a788c;font-weight:800;letter-spacing:.14em;text-transform:uppercase}.pagehead h1{font-size:30px;line-height:1.2;margin:8px 0 7px;letter-spacing:-.065em}.pagehead p{color:var(--muted);font-size:13px;margin:0;line-height:1.7}.hero{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:space-between;gap:16px;border-radius:17px;padding:24px 28px;background:linear-gradient(107deg,#133750,#0e5666 79%,#0e6670);color:white;margin-bottom:24px}.hero:after{content:"";position:absolute;width:250px;height:250px;border:1px solid #b3f0e82b;border-radius:50%;right:-70px;top:-125px;box-shadow:0 0 0 45px #a1e1e510,0 0 0 90px #a1e1e508}.hero>*{position:relative;z-index:1}.hero h2{font-size:21px;letter-spacing:-.045em;font-weight:700;margin:0 0 8px}.hero p{font-size:12px;color:#c4e1e5;line-height:1.6;margin:0;max-width:550px}.hero-kpi{text-align:center;padding:7px 18px;border-left:1px solid #ffffff3c;white-space:nowrap}.hero-kpi strong{font-size:28px;display:block;letter-spacing:-.05em}.hero-kpi span{font-size:10px;color:#b9dfe2}
.workbench{display:grid;grid-template-columns:minmax(315px,0.94fr) minmax(360px,1.2fr);gap:21px;align-items:start}.card{background:white;border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 3px 17px #172b3b05;overflow:hidden}.card-head{padding:21px 24px 17px;border-bottom:1px solid #eff2f5;display:flex;align-items:center;justify-content:space-between;gap:10px}.card-head h3{font-size:15px;margin:0;letter-spacing:-.025em}.sub{font-size:11px;color:#8a9aa8}.editor{padding:22px 23px 24px}.label{display:block;font-size:12px;font-weight:700;margin-bottom:9px}.editor textarea{width:100%;min-height:290px;resize:vertical;border:1px solid #dce7ee;background:#f9fbfd;border-radius:12px;padding:16px;line-height:1.75;font-size:13px;color:#274056;outline:none}.editor textarea:focus{background:white;border-color:#5facc1;box-shadow:0 0 0 3px #c5eaf15b}.hint{display:flex;justify-content:space-between;align-items:center;margin:9px 1px 19px;color:#8a9aab;font-size:11px}.samples{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:19px}.sample{border-radius:100px;border:1px solid #d8e4e9;background:#f6fafb;color:#426278;padding:7px 12px;font-size:11px;font-weight:650}.sample:hover{border-color:#89b7bf;background:#edf8f8}.controls{display:flex;gap:13px;align-items:center}.controls label{font-size:11px;color:#718495;font-weight:650}.controls select{margin-left:6px;border:1px solid #d6e2e9;background:#fff;padding:9px;border-radius:8px;font-size:12px}.analyze{background:#11778a;color:white;border:0;padding:14px 17px;border-radius:10px;font-weight:750;font-size:12px;flex:1;box-shadow:0 5px 17px #107a8e2a;transition:background .2s}.analyze:hover{background:#0c6577}.analyze:disabled{opacity:.6;cursor:wait}.disclaimer{border-top:1px solid var(--line);background:#fbfcfd;color:#75889a;font-size:11px;line-height:1.65;padding:17px 23px}.disclaimer b{color:#406073}
.rightcol{display:flex;flex-direction:column;gap:20px}.resulthead{display:flex;align-items:center;justify-content:space-between;gap:10px}.tinybutton{border:1px solid #dbe6ec;border-radius:8px;background:white;color:#446175;padding:8px 11px;font-size:11px;font-weight:650}.tinybutton:hover{background:#f4f9fb}.tinybutton:disabled{opacity:.45;cursor:not-allowed}.emptystate{text-align:center;padding:65px 20px 72px}.emptyicon{margin:auto auto 17px;width:64px;height:64px;background:#eaf4f5;border:1px solid #d6e6e9;border-radius:17px;display:grid;place-items:center;color:#1f8296;font-size:28px}.emptystate h4{font-size:15px;margin:0 0 8px}.emptystate p{font-size:12px;color:#8d9daa;max-width:285px;margin:0 auto;line-height:1.65}.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:21px}.metric{background:#f7fafc;border:1px solid #edf1f5;border-radius:11px;padding:13px 14px}.metric strong{display:block;font-size:25px;letter-spacing:-.045em;margin:2px 0}.metric span{display:block;color:#7f92a3;font-size:10px}.resultbody{padding:20px 23px 23px}.sectionrow{display:flex;align-items:center;justify-content:space-between;margin:15px 0 10px}.sectionrow h4{font-size:13px;margin:0}.sectionrow small{font-size:10px;color:#8ea0af}.skills{display:flex;flex-direction:column;gap:9px}.skillcard{border:1px solid #e3ebf0;border-radius:11px;padding:12px 14px;background:#fff}.skilltop{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.skillname{font-weight:700;font-size:12px;margin-right:auto}.tag{font-size:9px;font-weight:800;border-radius:100px;padding:5px 9px;letter-spacing:.01em}.required{color:#12634f;background:#e4f7ee}.preferred{color:#835b13;background:#fff2d7}.not_required{color:#a54351;background:#fff0f2}.unspecified{color:#6e7886;background:#eef2f5}.matched{color:#177b68;background:#edf9f4}.ambiguous{color:#855b1d;background:#fff6e6}.unmatched{color:#8896a4;background:#f2f4f6}.evidence{font-size:11px;color:#63798a;line-height:1.65;margin-top:8px}.evidence code{background:#edf6f8;border:1px solid #dfecef;border-radius:5px;padding:2px 5px;color:#21677b}.mapline{font-size:10px;color:#718698;margin-top:8px;line-height:1.55;overflow-wrap:anywhere}.mapping a{color:#207a93;text-decoration:none}.mapping a:hover{text-decoration:underline}.suggestion{padding:10px 0;border-bottom:1px solid #edf1f4}.suggestion:last-child{border-bottom:0}.suggestion-row{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:12px}.suggestion-row b{font-weight:650}.suggestion-row span{font-size:11px;color:#3f7383;font-variant-numeric:tabular-nums}.track{background:#edf4f6;border-radius:100px;height:5px;margin-top:8px;overflow:hidden}.track i{display:block;background:linear-gradient(90deg,#6bb9bf,#1a829a);height:100%;border-radius:100px}.sugghelp{color:#8b9caa;font-size:10px;line-height:1.6;margin-top:8px}.source-preview{background:#f7fafc;border:1px solid #e8eef2;border-radius:10px;padding:14px;font-size:12px;line-height:1.8;white-space:pre-wrap;overflow-wrap:anywhere;color:#536f83}.source-preview mark{background:#d7f0eb;border-radius:3px;padding:1px 2px;color:#174c48}.warn{margin-top:18px;color:#8e7017;background:#fffcf0;border:1px solid #f0e7bb;border-radius:10px;padding:12px 14px;font-size:10px;line-height:1.7}.raw{margin-top:14px}.raw summary{cursor:pointer;color:#528199;font-size:11px;font-weight:700}.raw pre{max-height:400px;overflow:auto;background:#102a3f;color:#d8edf0;padding:15px;border-radius:9px;font-size:10px;line-height:1.5}.error{padding:15px;background:#fff1f1;border:1px solid #f4cfcf;color:#9b2d2d;border-radius:10px;margin-bottom:14px;font-size:12px}.footnote{margin-top:20px;color:#9badb9;font-size:11px;text-align:right} [hidden]{display:none!important}
@media(max-width:1150px){.sidebar{flex-basis:198px}.content{padding:0 22px 35px}.workbench{grid-template-columns:minmax(290px,1fr) minmax(300px,1fr)}.hero-kpi{display:none}}
@media(max-width:850px){.sidebar{display:none}.content{padding:0 18px 32px}.workbench{grid-template-columns:1fr}.editor textarea{min-height:190px}.pagehead h1{font-size:26px}}
@media(max-width:520px){.topbar{height:65px}.top-right .version{display:none}.hero{padding:20px}.hero h2{font-size:18px}.metrics{gap:6px}.metric{padding:11px 9px}.metric strong{font-size:23px}.card-head{padding:18px}.resultbody,.editor{padding:17px}.controls{flex-direction:column;align-items:stretch}.controls label{align-self:flex-end}}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <div class="brand"><div class="brand-logo">FT</div><div><b>futuretwin<span style="color:#6fcac5">.</span></b><small>Workforce Intelligence</small></div></div>
  <div class="sidetitle">Workspace</div>
  <div class="navitem active"><span class="navicon">▣</span> Job Intelligence</div>
  <a class="navitem" href="/advancements" style="text-decoration:none"><span class="navicon">◈</span> AI Advancements</a>
  <a class="navitem" href="/benchmarks" style="text-decoration:none"><span class="navicon">▤</span> Benchmark Intelligence</a>
  <div class="navitem"><span class="navicon">◇</span> Skill Discovery <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <a class="navitem" href="/jobmarket" style="text-decoration:none"><span class="navicon">◷</span> Job Market</a>
  <div class="navitem"><span class="navicon">✧</span> Future Scenarios <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <div class="sideline"></div>
  <div class="sidetitle">Model stack</div>
  <div class="navitem"><span class="navicon">↗</span> Fine-tuned MiniLM</div>
  <div class="navitem"><span class="navicon">≋</span> ESCO Ontology</div>
  <div class="sidebar-bottom"><span class="live"><span class="small-dot"></span>Local model pipeline</span><p>Skills extracted from source text are kept separate from AI-inferred suggestions.</p></div>
</aside>
<main class="content">
  <div class="topbar"><div class="crumb">FutureTwin / <strong>Job Intelligence</strong></div><div class="top-right"><span class="version">Prototype v4</span><span class="pill">● &nbsp;ESCO + MiniLM</span></div></div>
  <div class="pagehead"><div><div class="kicker">Job description analyzer</div><h1>Decode a job into skills.</h1><p>Understand what's stated, what's preferred, and what AI can infer.</p></div></div>
  <section class="hero"><div><h2>From job descriptions to structured intelligence.</h2><p>Evidence-first skill extraction, official ESCO normalization, and semantic matching — in one workspace.</p></div><div class="hero-kpi"><strong>13,939</strong><span>ESCO candidates indexed</span></div></section>
  <div class="workbench">
    <section class="card">
      <div class="card-head"><h3>Job description</h3><span class="sub">01 / Input</span></div>
      <div class="editor">
        <label class="label" for="jobtext">Paste a job posting or try a sample</label>
        <textarea id="jobtext" maxlength="12000" spellcheck="false" aria-label="Job description">We require JavaScript, machine learning, data analytics and software frameworks. Python is not required. Knowledge of project management is preferred.</textarea>
        <div class="hint"><span>Evidence is extracted directly from this text.</span><span id="charcount">0 / 12,000</span></div>
        <div class="label">Try an example</div>
        <div class="samples"><button class="sample" type="button" data-sample="technical">AI / Tech role</button><button class="sample" type="button" data-sample="analyst">Data analyst</button><button class="sample" type="button" data-sample="manager">Project manager</button></div>
        <div class="controls"><label for="topk">AI suggestions <select id="topk"><option value="5" selected>Top 5</option><option value="10">Top 10</option><option value="20">Top 20</option></select></label><button class="analyze" id="analyze" type="button">✦ &nbsp; Analyze job description →</button></div>
      </div>
      <div class="disclaimer"><b>Evidence-first approach.</b> Explicit matches are literal mentions, not automatically verified employer requirements. Context labels are experimental rules; cosine similarity is not a confidence score.</div>
    </section>
    <div class="rightcol">
      <section class="card">
        <div class="card-head"><div><h3>Analysis results</h3><span class="sub" id="analysis-sub">Waiting for input</span></div><button class="tinybutton" id="download" type="button" disabled>↓ Export JSON</button></div>
        <div id="empty" class="emptystate"><div class="emptyicon">⌁</div><h4>Your intelligence report appears here</h4><p>Click <b>Analyze job description</b> to explore explicit mentions, ESCO mappings, and semantic suggestions.</p></div>
        <div id="error" class="error" hidden></div>
        <div class="resultbody" id="results" hidden>
          <div class="metrics"><div class="metric"><span>Explicit mentions</span><strong id="n-mentions">0</strong><span>from source text</span></div><div class="metric"><span>Verified ESCO IDs</span><strong id="n-matched">0</strong><span>unambiguous matches</span></div><div class="metric"><span>Required / preferred</span><strong id="n-requirements">0</strong><span>heuristic classifications</span></div></div>
          <div class="sectionrow"><h4>Detected skill mentions</h4><small id="skillcount">0 found</small></div><div id="mentions" class="skills"></div>
          <div class="sectionrow" style="margin-top:22px"><h4>Highlighted evidence</h4><small>exact text spans</small></div><div id="preview" class="source-preview"></div>
          <div class="sectionrow" style="margin-top:23px"><h4>Related ESCO skills</h4><small>MiniLM predictions</small></div><div id="suggestions"></div><p class="sugghelp">These are related candidate skills, not skills confirmed as requested by the employer. Bar lengths represent relative cosine scores, not probabilities.</p>
          <div class="warn">⚠ Requirement labels use unvalidated lexical rules, and some skill mappings may be ambiguous. Validate on real job advertisements before counting hiring demand.</div>
          <details class="raw"><summary>View full API response</summary><pre id="rawjson"></pre></details>
        </div>
      </section>
    </div>
  </div>
  <div class="footnote">FutureTwin AI · Development preview · Powered by your local Replit model</div>
</main>
</div>
<script>
(()=>{
'use strict';
const $=id=>document.getElementById(id);
const input=$('jobtext'),button=$('analyze'),results=$('results'),empty=$('empty'),error=$('error'),download=$('download');
let last=null;
const samples={
 technical:'We require JavaScript, machine learning, data analytics and software frameworks. Python is not required. Knowledge of project management is preferred.',
 analyst:'Data analyst responsible for SQL queries, data visualization, statistical analysis and dashboard development. Python is preferred but not required.',
 manager:'We require project management and stakeholder communication. Knowledge of data analytics is preferred. JavaScript is not required.'
};
const labels={required:'Required',preferred:'Preferred',not_required:'Not required',unspecified:'Unspecified'};
function element(tag,cls,content){let node=document.createElement(tag);if(cls)node.className=cls;if(content!==undefined)node.textContent=String(content);return node}
function ncount(){ $('charcount').textContent=input.value.length.toLocaleString()+' / 12,000' }
function clear(node){node.replaceChildren()}
function add(node,child){node.appendChild(child);return child}
function spanValue(m){return m.evidence&&m.evidence.length?m.evidence[0]:{quote:m.term||'',start:0,end:0}}
function drawMentions(rows){let target=$('mentions');clear(target);if(!rows.length){add(target,element('p','sugghelp','No explicit glossary mentions detected. This does not imply the posting has no skills.'));return}
for(const m of rows){const ev=spanValue(m),mapping=m.esco_mapping||{},status=m.requirement_status||'unspecified';let card=add(target,element('div','skillcard')),top=add(card,element('div','skilltop'));add(top,element('span','skillname',ev.quote||m.term||'Skill'));add(top,element('span','tag '+(labels[status]?status:'unspecified'),labels[status]||'Unspecified'));add(top,element('span','tag '+(mapping.status||'unmatched'),mapping.status||'unmatched'));
let detail=add(card,element('div','evidence'));detail.append('Mention detected: ');add(detail,element('code','',ev.quote||m.term||''));if(m.requirement_evidence&&m.requirement_evidence.cue){detail.append(' · Context cue: ');add(detail,element('code','',m.requirement_evidence.cue))}
let sub=add(card,element('div','mapline mapping'));if(mapping.status==='matched'&&mapping.skill_uri){sub.append('ESCO: '+(mapping.label||m.term)+' · ');let link=element('a','', 'View identifier ↗');link.href=mapping.skill_uri;link.target='_blank';link.rel='noopener noreferrer';add(sub,link)}else if(mapping.status==='ambiguous'){sub.textContent='ESCO: Multiple possible IDs — not automatically resolved'}else{sub.textContent='ESCO: No verified ID — not guessed from similarity'}
}}
function drawHighlights(text,rows){const box=$('preview');clear(box);const spans=rows.map(m=>spanValue(m)).filter(ev=>Number.isInteger(ev.start)&&Number.isInteger(ev.end)&&ev.start>=0&&ev.end>ev.start&&ev.end<=text.length).sort((a,b)=>a.start-b.start||b.end-a.end);let pos=0;for(const ev of spans){if(ev.start<pos)continue;box.appendChild(document.createTextNode(text.slice(pos,ev.start)));add(box,element('mark','',text.slice(ev.start,ev.end)));pos=ev.end}box.appendChild(document.createTextNode(text.slice(pos)))}
function drawSuggestions(rows){let target=$('suggestions');clear(target);if(!rows.length){add(target,element('p','sugghelp','No semantic suggestions returned.'));return}for(const s of rows){let row=add(target,element('div','suggestion')),line=add(row,element('div','suggestion-row'));add(line,element('b','',s.skill||'Unnamed skill'));let score=Number(s.cosine_similarity);add(line,element('span','',Number.isFinite(score)?score.toFixed(4):'—'));let track=add(row,element('div','track')),bar=add(track,element('i'));bar.style.width=(Number.isFinite(score)?Math.max(0,Math.min(score,1))*100:0)+'%'}}
function render(data){last=data;const mentions=Array.isArray(data.explicit_mentions)?data.explicit_mentions:[],suggestions=Array.isArray(data.semantic_candidates)?data.semantic_candidates:[];empty.hidden=true;error.hidden=true;results.hidden=false;download.disabled=false;
$('analysis-sub').textContent='Analysis complete · '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});$('n-mentions').textContent=mentions.length;$('n-matched').textContent=mentions.filter(m=>m.esco_mapping&&m.esco_mapping.status==='matched').length;$('n-requirements').textContent=mentions.filter(m=>['required','preferred'].includes(m.requirement_status)).length;$('skillcount').textContent=mentions.length+' detected';drawMentions(mentions);drawHighlights(data.input||input.value,mentions);drawSuggestions(suggestions);$('rawjson').textContent=JSON.stringify(data,null,2)}
async function analyze(){const text=input.value.trim();if(!text){input.focus();return}button.disabled=true;button.textContent='Analyzing…';error.hidden=true;try{const response=await fetch('/api/analyze-job-v4',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,top_k:Number($('topk').value)})});let data;try{data=await response.json()}catch{throw new Error('Server returned a non-JSON response. Check the Replit console.')}if(!response.ok)throw new Error(data.error||`Request failed (HTTP ${response.status})`);render(data)}catch(e){error.textContent='Could not complete analysis: '+e.message;error.hidden=false;$('analysis-sub').textContent='Request failed'}finally{button.disabled=false;button.textContent='✦   Analyze job description →'}}
button.addEventListener('click',analyze);input.addEventListener('input',ncount);document.querySelectorAll('[data-sample]').forEach(b=>b.addEventListener('click',()=>{input.value=samples[b.dataset.sample];ncount();input.focus()}));download.addEventListener('click',()=>{if(!last)return;let blob=new Blob([JSON.stringify(last,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='futuretwin-job-analysis.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)});ncount();
})();
</script>
</body>
</html>'''


@app.get("/")
def futuretwin_home():
    return Response(HOME_HTML, mimetype="text/html")


@app.get("/career")
def futuretwin_dashboard():
    # Flask Response avoids templating user-controlled content into HTML.
    return Response(CAREER_HTML, mimetype="text/html")


@app.get("/my-career")
def futuretwin_my_career():
    return Response(MY_CAREER_HTML, mimetype="text/html")


@app.get("/my-future")
def futuretwin_my_future():
    return Response(MY_FUTURE_HTML, mimetype="text/html")


@app.get("/purpose")
def futuretwin_purpose():
    from futuretwin_sdg_page import SDG_HTML
    return Response(SDG_HTML, mimetype="text/html")


@app.get("/sdg-map")
def futuretwin_sdg_map():
    from futuretwin_sdg_map_page import SDG_MAP_HTML
    return Response(SDG_MAP_HTML, mimetype="text/html")


@app.get("/api/occupations/search")
def api_occupations_search():
    from futuretwin_occupation_api import search_occupations

    query = request.args.get("q", "")
    try:
        limit = int(request.args.get("limit", "10"))
        return jsonify(search_occupations(query, limit=limit))
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"ESCO occupation search failed: {exc}"}), 500


@app.get("/api/occupations/explore")
def api_occupations_explore():
    from futuretwin_occupation_api import explore_occupation

    uri = request.args.get("uri", "")
    try:
        result = explore_occupation(uri)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Occupation data could not be loaded: {exc}"}), 500
    if result is None:
        return jsonify({"error": "ESCO occupation not found."}), 404
    return jsonify(result)


@app.get("/trends")
def futuretwin_trends():
    return Response(TRENDS_HTML, mimetype="text/html")


ADVANCEMENTS_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="light" />
<title>FutureTwin · AI Advancements</title>
<style>
:root{--navy:#0a1b2d;--navy2:#132a42;--sky:#1d6d87;--blue:#176b88;--teal:#0d806d;--ink:#172b40;--muted:#687b8d;--bg:#f4f7fa;--line:#e5ecf1;--paper:#fff;--radius:16px}
*{box-sizing:border-box} body{margin:0;min-height:100vh;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:-.009em}
button,textarea,select{font:inherit}button{cursor:pointer}button:focus-visible,select:focus-visible{outline:3px solid #8bcddb;outline-offset:2px}
.shell{display:flex;min-height:100vh}.sidebar{flex:0 0 238px;background:var(--navy);color:#fff;display:flex;flex-direction:column;padding:29px 18px;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:12px;padding:2px 12px 36px}.brand-logo{height:38px;width:38px;border:1px solid #63b3be55;border-radius:12px;background:linear-gradient(135deg,#176f86,#194261);display:grid;place-items:center;font-weight:800;font-size:15px;letter-spacing:-1px;box-shadow:0 4px 22px #3a9eb126}.brand b{display:block;letter-spacing:-.045em;font-size:20px;line-height:1.1}.brand small{font-size:10px;letter-spacing:.19em;color:#9aafc0;text-transform:uppercase}
.sidetitle{color:#8099ac;letter-spacing:.15em;text-transform:uppercase;font-size:10px;font-weight:700;padding:0 13px;margin:10px 0 10px}.navitem{display:flex;align-items:center;gap:12px;border-radius:10px;padding:12px 13px;font-size:13px;color:#b9cbda;margin-bottom:5px}.navitem.active{background:#1c4055;color:#e6fcfc;font-weight:650;border:1px solid #30637a}.navicon{font-size:17px;width:22px;text-align:center;opacity:.9}.sideline{height:1px;background:#294057;margin:15px 11px 24px}.sidebar-bottom{margin-top:auto;padding:17px 13px;background:#122c43;border:1px solid #29465c;border-radius:12px}.sidebar-bottom .live{color:#b1e3dc;font-weight:700;font-size:12px}.small-dot{width:8px;height:8px;border-radius:50%;background:#67ccb6;display:inline-block;margin-right:6px}.sidebar-bottom p{font-size:11px;line-height:1.65;color:#a4b8c8;margin-bottom:0}
.content{flex:1;min-width:0;padding:0 40px 55px;max-width:1670px;margin:0 auto}.topbar{height:81px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.topbar .crumb{font-size:13px;color:#718597}.crumb strong{color:#23374d;font-weight:700}.top-right{display:flex;align-items:center;gap:11px}.pill{border:1px solid #d5e7e7;color:#237668;background:#edfaf7;padding:7px 12px;border-radius:100px;font-size:11px;font-weight:750}.version{font-size:12px;color:#7990a0}
.pagehead{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin:27px 0 21px}.kicker{font-size:11px;color:#0a788c;font-weight:800;letter-spacing:.14em;text-transform:uppercase}.pagehead h1{font-size:30px;line-height:1.2;margin:8px 0 7px;letter-spacing:-.065em}.pagehead p{color:var(--muted);font-size:13px;margin:0;line-height:1.7}.hero{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:space-between;gap:16px;border-radius:17px;padding:24px 28px;background:linear-gradient(107deg,#133750,#0e5666 79%,#0e6670);color:white;margin-bottom:24px}.hero:after{content:"";position:absolute;width:250px;height:250px;border:1px solid #b3f0e82b;border-radius:50%;right:-70px;top:-125px;box-shadow:0 0 0 45px #a1e1e510,0 0 0 90px #a1e1e508}.hero>*{position:relative;z-index:1}.hero h2{font-size:21px;letter-spacing:-.045em;font-weight:700;margin:0 0 8px}.hero p{font-size:12px;color:#c4e1e5;line-height:1.6;margin:0;max-width:560px}.hero-kpi{text-align:center;padding:7px 18px;border-left:1px solid #ffffff3c;white-space:nowrap}.hero-kpi strong{font-size:28px;display:block;letter-spacing:-.05em}.hero-kpi span{font-size:10px;color:#b9dfe2}
.card{background:white;border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 3px 17px #172b3b05;overflow:hidden;margin-bottom:21px}.card-head{padding:21px 24px 17px;border-bottom:1px solid #eff2f5;display:flex;align-items:center;justify-content:space-between;gap:10px}.card-head h3{font-size:15px;margin:0;letter-spacing:-.025em}.sub{font-size:11px;color:#8a9aa8}.card-body{padding:20px 23px 23px}
.tag-evidence{font-size:9px;font-weight:800;border-radius:100px;padding:5px 9px;letter-spacing:.06em}.observed{color:#12634f;background:#e4f7ee}.hypothesis{color:#6a53a8;background:#f0ecfa}
.banner{border-radius:11px;padding:13px 16px;font-size:12px;line-height:1.65;margin-bottom:15px}.banner-none{background:#f2f6f9;border:1px solid #dfe8ee;color:#4a6478}.banner-demo{background:#fffcf0;border:1px solid #f0e7bb;color:#8e7017}.banner-live{background:#edfaf4;border:1px solid #c4e9d8;color:#136247}
.cmptable,.occtable{width:100%;border-collapse:collapse;font-size:12px}.cmptable th,.occtable th{text-align:left;color:#7f92a3;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:8px 10px;border-bottom:1px solid var(--line)}.cmptable td,.occtable td{padding:9px 10px;border-bottom:1px solid #f0f4f7;color:#2c445a}.cmptable tr:last-child td,.occtable tr:last-child td{border-bottom:0}.num{font-variant-numeric:tabular-nums}.up{color:#0d806d;font-weight:750}.flat{color:#8a9aa8}.nc{color:#b08968;font-weight:650}
.workbench{display:grid;grid-template-columns:minmax(300px,0.85fr) minmax(360px,1.3fr);gap:21px;align-items:start}.caplist{display:flex;flex-direction:column;gap:7px;margin-bottom:16px}.capbtn{display:flex;align-items:center;gap:10px;border:1px solid #dbe6ec;background:#f8fbfc;border-radius:10px;padding:11px 13px;font-size:12px;font-weight:650;color:#37536b;text-align:left}.capbtn:hover{border-color:#89b7bf;background:#f0f8f9}.capbtn.active{border-color:#1d8296;background:#eaf6f7;color:#104f5e}.capbtn .delta{margin-left:auto;font-size:10px;color:#7f92a3;font-variant-numeric:tabular-nums}.capbtn .delta.up{color:#0d806d}.modebox{border:1px dashed #d8e4e9;border-radius:10px;padding:12px 13px;font-size:11px;color:#5d7283;line-height:1.6;margin-bottom:14px}.modebox label{display:flex;gap:8px;align-items:flex-start;cursor:pointer}.modebox input{margin-top:2px}.tasklist{display:flex;flex-direction:column;gap:7px}.taskitem{border-left:3px solid #bcdde2;background:#f7fafc;border-radius:0 8px 8px 0;padding:8px 11px;font-size:11px;color:#46617a;line-height:1.55}.taskitem small{display:block;color:#8a9aa8;font-size:9px;margin-top:2px}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:18px}.metric{background:#f7fafc;border:1px solid #edf1f5;border-radius:11px;padding:13px 14px}.metric strong{display:block;font-size:22px;letter-spacing:-.045em;margin:2px 0}.metric span{display:block;color:#7f92a3;font-size:10px}
.legend{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:15px}.tag{font-size:9px;font-weight:800;border-radius:100px;padding:5px 9px;letter-spacing:.01em}.cl-exposure{color:#a54351;background:#fff0f2}.cl-augment{color:#12634f;background:#e4f7ee}.cl-complement{color:#6a53a8;background:#f0ecfa}.cl-unknown{color:#6e7886;background:#eef2f5}.rel-essential{color:#12634f;background:#e4f7ee}.rel-optional{color:#835b13;background:#fff2d7}
.skills{display:flex;flex-direction:column;gap:9px}.skillcard{border:1px solid #e3ebf0;border-radius:11px;padding:12px 14px;background:#fff;cursor:pointer}.skillcard:hover{border-color:#a8cdd6}.skillcard.open{border-color:#1d8296;box-shadow:0 0 0 3px #c5eaf14d}.skilltop{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.skillname{font-weight:700;font-size:12px;margin-right:auto}.skillmeta{display:flex;align-items:center;gap:10px;margin-top:9px}.simval{font-size:11px;color:#3f7383;font-variant-numeric:tabular-nums;white-space:nowrap}.track{flex:1;background:#edf4f6;border-radius:100px;height:5px;overflow:hidden}.track i{display:block;background:linear-gradient(90deg,#6bb9bf,#1a829a);height:100%;border-radius:100px}.skillwhy{display:none;margin-top:11px;border-top:1px dashed #e3ebf0;padding-top:10px}.skillcard.open .skillwhy{display:block}.why-rule{font-size:10px;color:#8e7017;background:#fffcf0;border:1px solid #f0e7bb;border-radius:8px;padding:8px 10px;line-height:1.6;margin-bottom:9px}.why-task{font-size:11px;color:#46617a;padding:6px 0;border-bottom:1px solid #f0f4f7;display:flex;justify-content:space-between;gap:10px}.why-task:last-child{border-bottom:0}.why-task span{color:#3f7383;font-variant-numeric:tabular-nums;white-space:nowrap}
.occrow{border:1px solid #e3ebf0;border-radius:11px;padding:11px 14px;background:#fff;cursor:pointer;margin-bottom:8px}.occrow:hover{border-color:#a8cdd6}.occrow.open{border-color:#1d8296}.occtop{display:flex;align-items:center;gap:9px;font-size:12px}.occname{font-weight:700;margin-right:auto}.occsub{font-size:10px;color:#8a9aa8;margin-top:5px}.occev{display:none;margin-top:10px;border-top:1px dashed #e3ebf0;padding-top:9px}.occrow.open .occev{display:block}.occevrow{display:flex;align-items:center;gap:8px;font-size:11px;color:#46617a;padding:4px 0}.occevrow b{font-weight:650}.occevrow span{margin-left:auto;color:#3f7383;font-variant-numeric:tabular-nums}
.emptystate{text-align:center;padding:55px 20px 62px}.emptyicon{margin:auto auto 17px;width:64px;height:64px;background:#eaf4f5;border:1px solid #d6e6e9;border-radius:17px;display:grid;place-items:center;color:#1f8296;font-size:28px}.emptystate h4{font-size:15px;margin:0 0 8px}.emptystate p{font-size:12px;color:#8d9daa;max-width:300px;margin:0 auto;line-height:1.65}
.sectionrow{display:flex;align-items:center;justify-content:space-between;margin:15px 0 10px}.sectionrow h4{font-size:13px;margin:0}.sectionrow small{font-size:10px;color:#8ea0af}.error{padding:15px;background:#fff1f1;border:1px solid #f4cfcf;color:#9b2d2d;border-radius:10px;margin-bottom:14px;font-size:12px}.warn{margin-top:18px;color:#8e7017;background:#fffcf0;border:1px solid #f0e7bb;border-radius:10px;padding:12px 14px;font-size:10px;line-height:1.7}.footnote{margin-top:20px;color:#9badb9;font-size:11px;text-align:right} [hidden]{display:none!important}
@media(max-width:1150px){.sidebar{flex-basis:198px}.content{padding:0 22px 35px}.workbench{grid-template-columns:minmax(280px,1fr) minmax(300px,1fr)}.hero-kpi{display:none}}
@media(max-width:850px){.sidebar{display:none}.content{padding:0 18px 32px}.workbench{grid-template-columns:1fr}.pagehead h1{font-size:26px}.metrics{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <div class="brand"><div class="brand-logo">FT</div><div><b>futuretwin<span style="color:#6fcac5">.</span></b><small>Workforce Intelligence</small></div></div>
  <a class="navitem" href="/" style="text-decoration:none;color:#9fd8cf"><span class="navicon">&larr;</span> Back to FutureTwin</a>
  <div class="sidetitle">Workspace</div>
  <a class="navitem" href="/career" style="text-decoration:none"><span class="navicon">▣</span> Job Intelligence</a>
  <div class="navitem active"><span class="navicon">◈</span> AI Advancements</div>
  <a class="navitem" href="/benchmarks" style="text-decoration:none"><span class="navicon">▤</span> Benchmark Intelligence</a>
  <div class="navitem"><span class="navicon">◇</span> Skill Discovery <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <a class="navitem" href="/jobmarket" style="text-decoration:none"><span class="navicon">◷</span> Job Market</a>
  <div class="navitem"><span class="navicon">✧</span> Future Scenarios <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <div class="sideline"></div>
  <div class="sidetitle">Model stack</div>
  <div class="navitem"><span class="navicon">↗</span> Fine-tuned MiniLM</div>
  <div class="navitem"><span class="navicon">≋</span> ESCO Ontology</div>
  <div class="sidebar-bottom"><span class="live"><span class="small-dot"></span>Observed vs hypothesis</span><p>Benchmark changes are measured. Skill matches and impact classes are labelled hypotheses.</p></div>
</aside>
<main class="content">
  <div class="topbar"><div class="crumb">FutureTwin / <strong>AI Advancements</strong></div><div class="top-right"><span class="version">Impact engine v1</span><span class="pill">● &nbsp;PostgreSQL + MiniLM + ESCO</span></div></div>
  <div class="pagehead"><div><div class="kicker">AI Advancement → Skill → Occupation</div><h1>From AI progress to workforce signals.</h1><p>Measured benchmark change first. Skill and occupation impact is always labelled as hypothesis.</p></div></div>
  <section class="hero"><div><h2>Measure first. Infer second.</h2><p>Compares the latest two stored benchmark snapshots, matches benchmark-supported tasks to ESCO skills with the fine-tuned MiniLM, then traces affected skills to occupations.</p></div><div class="hero-kpi"><strong id="kpi-snapshots">–</strong><span>snapshots tracked</span></div><div class="hero-kpi"><strong id="kpi-advancements">–</strong><span>advancements detected</span></div></section>

  <section class="card">
    <div class="card-head"><div><h3>Benchmark comparison</h3><span class="sub" id="cmp-sub">Loading snapshots…</span></div><span class="tag-evidence observed">OBSERVED · measured</span></div>
    <div class="card-body">
      <div id="cmp-banner" class="banner banner-none" hidden></div>
      <table class="cmptable"><thead><tr><th>Capability</th><th>Previous best</th><th>Latest best</th><th>Change</th><th>Comparable</th><th>Leading model</th></tr></thead><tbody id="cmp-rows"><tr><td colspan="6" style="color:#8a9aa8">Loading…</td></tr></tbody></table>
    </div>
  </section>

  <div class="workbench">
    <section class="card">
      <div class="card-head"><div><h3>Capability scenario</h3><span class="sub">01 / Select</span></div></div>
      <div class="card-body">
        <div class="caplist" id="caplist"></div>
        <div class="modebox"><label><input type="checkbox" id="demomode" checked /> <span><b>Simulated scenario (demo).</b> Runs the matching pipeline without claiming a real advancement. Turned off automatically when a real improvement is detected.</span></label></div>
        <div class="sectionrow"><h4>Task evidence used</h4><small id="task-granularity">—</small></div>
        <div class="tasklist" id="tasklist"><p class="sub" style="margin:0">Select a capability to see which occupational task descriptions drive the matching.</p></div>
      </div>
    </section>
    <div class="rightcol" style="display:flex;flex-direction:column;gap:0">
      <section class="card">
        <div class="card-head"><div><h3>Impact report</h3><span class="sub" id="report-sub">Waiting for a capability</span></div><span class="tag-evidence hypothesis" id="report-tag" hidden>HYPOTHESIS · unvalidated</span></div>
        <div class="card-body">
          <div id="error" class="error" hidden></div>
          <div id="empty" class="emptystate"><div class="emptyicon">◈</div><h4>Select a capability to inspect impact</h4><p>Skills matched by the fine-tuned MiniLM, related ESCO occupations, and the rule behind every impact label.</p></div>
          <div id="report" hidden>
            <div id="report-banner" class="banner banner-demo" hidden></div>
            <div class="metrics">
              <div class="metric"><span>Benchmark change</span><strong id="m-change">—</strong><span>observed points</span></div>
              <div class="metric"><span>Skills matched</span><strong id="m-skills">0</strong><span>fine-tuned MiniLM</span></div>
              <div class="metric"><span>Occupations</span><strong id="m-occ">0</strong><span>ESCO relations</span></div>
              <div class="metric"><span>Essential links</span><strong id="m-ess">0</strong><span>vs optional</span></div>
            </div>
            <div class="legend">
              <span class="tag cl-exposure">Potential automation exposure</span>
              <span class="tag cl-augment">AI augmentation opportunity</span>
              <span class="tag cl-complement">Complementary / newly valuable</span>
              <span class="tag cl-unknown">Unknown impact</span>
            </div>
            <div class="sectionrow"><h4>Potentially affected skills</h4><small>click a skill for why it matched</small></div>
            <div id="skills" class="skills"></div>
            <div class="sectionrow" style="margin-top:22px"><h4>Related ESCO occupations</h4><small>click for skill evidence</small></div>
            <div id="occupations"></div>
            <div class="warn">⚠ Skill matches are semantic hypotheses from a fine-tuned embedding model, and impact classes come from unvalidated rules (each card shows its rule). Cosine similarity is not an automation probability. Only the benchmark comparison above is observed data.</div>
          </div>
        </div>
      </section>
    </div>
  </div>
  <div class="footnote">FutureTwin AI · Development preview · Evidence-qualified impact hypotheses</div>
</main>
</div>
<script>
(()=>{
'use strict';
const $=id=>document.getElementById(id);
const CL_LABEL={potential_automation_exposure:'Potential automation exposure',ai_augmentation_opportunity:'AI augmentation opportunity',complementary_or_emerging:'Complementary / newly valuable',unknown_impact:'Unknown impact'};
const CL_CLASS={potential_automation_exposure:'cl-exposure',ai_augmentation_opportunity:'cl-augment',complementary_or_emerging:'cl-complement',unknown_impact:'cl-unknown'};
let comparison=null,currentCap=null,openSkill=null;
function element(tag,cls,content){let n=document.createElement(tag);if(cls)n.className=cls;if(content!==undefined)n.textContent=String(content);return n}
function add(node,child){node.appendChild(child);return child}
function esc(v){return v===null||v===undefined?'—':String(v)}

async function loadComparison(){
  let data;
  try{
    const res=await fetch('/api/advancements');
    data=await res.json();
    if(!res.ok)throw new Error(data.error||('HTTP '+res.status));
  }catch(e){
    $('cmp-sub').textContent='Comparison unavailable';
    $('cmp-rows').innerHTML='';
    const tr=add($('cmp-rows'),element('tr'));const td=add(tr,element('td','', 'Could not load benchmark comparison: '+e.message));td.colSpan=6;td.style.color='#9b2d2d';
    return;
  }
  comparison=data;
  $('kpi-snapshots').textContent=(data.snapshots||[]).length;
  $('kpi-advancements').textContent=(data.advancements||[]).length;
  $('cmp-sub').textContent='Latest: '+(data.latest_snapshot||'—')+' vs '+(data.previous_snapshot||'—');
  const banner=$('cmp-banner');
  banner.hidden=false;
  if((data.advancements||[]).length){
    banner.className='banner banner-live';
    banner.textContent=data.note;
  }else{
    banner.className='banner banner-none';
    banner.textContent=(data.note||'No advancement data.')+' This is an accurate result, not an error — the pipeline only infers impact from real, comparable change.';
  }
  const tbody=$('cmp-rows');tbody.replaceChildren();
  for(const c of data.comparisons||[]){
    const tr=add(tbody,element('tr'));
    add(tr,element('td','',c.capability));
    add(tr,element('td','num',esc(c.previous_best)));
    add(tr,element('td','num',esc(c.latest_best)));
    const ch=add(tr,element('td','num',c.change===null||c.change===undefined?'n/a':(c.change>0?'+'+c.change:c.change)));
    ch.className='num '+(c.change>0?'up':c.change===null||c.change===undefined?'nc':'flat');
    if(c.change===null||c.change===undefined)ch.title=c.note||'Not comparable';
    add(tr,element('td','',c.comparable?'Yes':'No'));
    add(tr,element('td','',esc(c.leading_model)));
  }
  const list=$('caplist');list.replaceChildren();
  const advanced=new Set((data.advancements||[]).map(a=>a.capability));
  for(const cap of data.capabilities||[]){
    const cmp=(data.comparisons||[]).find(c=>c.capability===cap);
    const btn=add(list,element('button','capbtn'));
    btn.type='button';
    add(btn,element('span','',cap));
    const d=add(btn,element('span','delta',cmp&&cmp.change!==null&&cmp.change!==undefined?(cmp.change>0?'+'+cmp.change:String(cmp.change)):'0'));
    if(cmp&&cmp.change>0)d.classList.add('up');
    btn.addEventListener('click',()=>selectCapability(cap,advanced.has(cap)));
  }
}

async function selectCapability(cap,hasAdvancement){
  currentCap=cap;openSkill=null;
  document.querySelectorAll('.capbtn').forEach(b=>b.classList.toggle('active',b.firstChild.textContent===cap));
  const demoBox=$('demomode');
  demoBox.checked=!hasAdvancement;
  demoBox.disabled=false;
  await runReport();
}

async function runReport(){
  if(!currentCap)return;
  const demo=$('demomode').checked;
  $('empty').hidden=true;$('report').hidden=true;$('error').hidden=true;$('report-tag').hidden=true;
  $('report-sub').textContent='Analysing '+currentCap+'…';
  let data;
  try{
    const res=await fetch('/api/advancements/impact?capability='+encodeURIComponent(currentCap)+'&demo='+(demo?'1':'0')+'&top_k=15');
    data=await res.json();
    if(!res.ok)throw new Error(data.error||('HTTP '+res.status));
  }catch(e){
    $('error').textContent='Could not build impact report: '+e.message;$('error').hidden=false;
    $('report-sub').textContent='Request failed';
    return;
  }
  renderReport(data);
}

function renderReport(data){
  $('report').hidden=false;$('report-tag').hidden=false;
  $('report-sub').textContent=data.capability+' · '+(data.mode==='demo'?'simulated scenario':'live data');
  const banner=$('report-banner');
  if(data.advancement_status==='no_meaningful_advancement'){
    banner.hidden=false;banner.className='banner banner-none';
    banner.textContent='No meaningful measured advancement for '+data.capability+' between the latest snapshots — so no impact is inferred. Enable the simulated scenario to preview the pipeline.';
    $('m-change').textContent='—';$('m-skills').textContent='0';$('m-occ').textContent='0';$('m-ess').textContent='0';
    $('skills').replaceChildren();$('occupations').replaceChildren();
    renderTasks(data);
    return;
  }
  banner.hidden=false;
  if(data.mode==='demo'){banner.className='banner banner-demo';banner.textContent='⚠ '+data.demo_notice;}
  else{banner.className='banner banner-live';banner.textContent='Observed improvement of +'+(data.event&&data.event.change)+' points ('+(data.event&&data.event.leading_model)+'). Impact below is hypothesis built on that measurement.';}
  const skills=data.skills||[],occ=data.occupations||[];
  $('m-change').textContent=data.mode==='demo'?'demo':(data.event&&data.event.change!==null?'+'+data.event.change:'—');
  $('m-skills').textContent=skills.length;
  $('m-occ').textContent=occ.length;
  $('m-ess').textContent=occ.reduce((n,o)=>n+o.essential_matches,0);
  renderTasks(data);
  renderSkills(skills);
  renderOccupations(occ);
}

function renderTasks(data){
  $('task-granularity').textContent=data.task_granularity==='occupation_tasks'?'occupation tasks':'capability-level fallback';
  const box=$('tasklist');box.replaceChildren();
  for(const t of data.capability_tasks||[]){
    const item=add(box,element('div','taskitem',t.task_text));
    if(t.occupation)add(item,element('small','',t.task_id+' · '+t.occupation));
  }
}

function renderSkills(skills){
  const box=$('skills');box.replaceChildren();
  if(!skills.length){add(box,element('p','sub','No skills passed the similarity floor for this scenario.'));return}
  for(const s of skills){
    const card=add(box,element('div','skillcard'));
    const top=add(card,element('div','skilltop'));
    add(top,element('span','skillname',s.skill));
    add(top,element('span','tag '+(CL_CLASS[s.impact.classification]||'cl-unknown'),CL_LABEL[s.impact.classification]||s.impact.classification));
    const meta=add(card,element('div','skillmeta'));
    add(meta,element('span','simval','cos '+s.cosine_similarity.toFixed(4)));
    const track=add(meta,element('div','track'));const bar=add(track,element('i'));
    bar.style.width=(Math.max(0,Math.min(s.cosine_similarity,1))*100)+'%';
    const why=add(card,element('div','skillwhy'));
    add(why,element('div','why-rule','Impact rule: '+s.impact.rule+' — '+s.impact.basis));
    for(const t of s.matched_tasks||[]){
      const row=add(why,element('div','why-task'));
      add(row,element('b','',t.task_text));
      add(row,element('span','',t.cosine_similarity.toFixed(4)));
    }
    card.addEventListener('click',()=>{
      const opening=!card.classList.contains('open');
      document.querySelectorAll('.skillcard.open').forEach(c=>c.classList.remove('open'));
      if(opening)card.classList.add('open');
    });
  }
}

function renderOccupations(occs){
  const box=$('occupations');box.replaceChildren();
  if(!occs.length){add(box,element('p','sub','No ESCO occupation relations for the matched skills.'));return}
  for(const o of occs){
    const row=add(box,element('div','occrow'));
    const top=add(row,element('div','occtop'));
    add(top,element('span','occname',o.occupation));
    add(top,element('span','tag rel-essential',o.essential_matches+' essential'));
    add(top,element('span','tag rel-optional',o.optional_matches+' optional'));
    add(row,element('div','occsub','relevance '+o.relevance_score.toFixed(3)+' · '+o.matched_skills+' of '+o.total_esco_skills+' ESCO skills matched'));
    const ev=add(row,element('div','occev'));
    for(const e of o.evidence||[]){
      const er=add(ev,element('div','occevrow'));
      add(er,element('b','',e.skill));
      add(er,element('span','tag '+(e.relation==='essential'?'rel-essential':'rel-optional'),e.relation));
      add(er,element('span','',e.cosine_similarity.toFixed(4)));
    }
    row.addEventListener('click',()=>row.classList.toggle('open'));
  }
}

$('demomode').addEventListener('change',runReport);
loadComparison();
})();
</script>
</body>
</html>'''


@app.get("/advancements")
def futuretwin_advancements_page():
    return Response(ADVANCEMENTS_HTML, mimetype="text/html")


@app.get("/api/advancements")
def api_advancements():
    from futuretwin_impact_engine import CAPABILITY_FALLBACK_TEXT, get_snapshot_comparison
    try:
        comparison = get_snapshot_comparison()
    except Exception as exc:  # DB unavailable: report honestly, don't hang the UI
        return jsonify({"status": "error", "error": str(exc)}), 500
    comparison["capabilities"] = sorted(CAPABILITY_FALLBACK_TEXT)
    return jsonify(comparison)


@app.get("/api/advancements/impact")
def api_advancements_impact():
    from futuretwin_impact_engine import CAPABILITY_FALLBACK_TEXT, build_impact_report
    capability = request.args.get("capability", "")
    demo = request.args.get("demo", "").strip().lower() in ("1", "true", "yes")
    try:
        top_k = int(request.args.get("top_k", "15"))
    except ValueError:
        return jsonify({"error": "top_k must be an integer."}), 400
    if not 1 <= top_k <= 50:
        return jsonify({"error": "top_k must be an integer from 1 to 50."}), 400
    try:
        report = build_impact_report(capability, demo=demo, top_k=top_k)
    except ValueError as exc:
        return jsonify({"error": str(exc),
                        "capabilities": sorted(CAPABILITY_FALLBACK_TEXT)}), 400
    except Exception as exc:
        return jsonify({"error": f"Impact engine failed: {exc}"}), 500
    return jsonify(report)


BENCHMARKS_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="light" />
<title>FutureTwin · Benchmark Intelligence</title>
<style>
:root{--navy:#0a1b2d;--navy2:#132a42;--sky:#1d6d87;--blue:#176b88;--teal:#0d806d;--ink:#172b40;--muted:#687b8d;--bg:#f4f7fa;--line:#e5ecf1;--paper:#fff;--radius:16px}
*{box-sizing:border-box} body{margin:0;min-height:100vh;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:-.009em}
button,select{font:inherit}button{cursor:pointer}button:focus-visible,select:focus-visible{outline:3px solid #8bcddb;outline-offset:2px}
.shell{display:flex;min-height:100vh}.sidebar{flex:0 0 238px;background:var(--navy);color:#fff;display:flex;flex-direction:column;padding:29px 18px;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:12px;padding:2px 12px 36px}.brand-logo{height:38px;width:38px;border:1px solid #63b3be55;border-radius:12px;background:linear-gradient(135deg,#176f86,#194261);display:grid;place-items:center;font-weight:800;font-size:15px;letter-spacing:-1px;box-shadow:0 4px 22px #3a9eb126}.brand b{display:block;letter-spacing:-.045em;font-size:20px;line-height:1.1}.brand small{font-size:10px;letter-spacing:.19em;color:#9aafc0;text-transform:uppercase}
.sidetitle{color:#8099ac;letter-spacing:.15em;text-transform:uppercase;font-size:10px;font-weight:700;padding:0 13px;margin:10px 0 10px}.navitem{display:flex;align-items:center;gap:12px;border-radius:10px;padding:12px 13px;font-size:13px;color:#b9cbda;margin-bottom:5px}.navitem.active{background:#1c4055;color:#e6fcfc;font-weight:650;border:1px solid #30637a}.navicon{font-size:17px;width:22px;text-align:center;opacity:.9}.sideline{height:1px;background:#294057;margin:15px 11px 24px}.sidebar-bottom{margin-top:auto;padding:17px 13px;background:#122c43;border:1px solid #29465c;border-radius:12px}.sidebar-bottom .live{color:#b1e3dc;font-weight:700;font-size:12px}.small-dot{width:8px;height:8px;border-radius:50%;background:#67ccb6;display:inline-block;margin-right:6px}.sidebar-bottom p{font-size:11px;line-height:1.65;color:#a4b8c8;margin-bottom:0}
.content{flex:1;min-width:0;padding:0 40px 55px;max-width:1670px;margin:0 auto}.topbar{height:81px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.topbar .crumb{font-size:13px;color:#718597}.crumb strong{color:#23374d;font-weight:700}.top-right{display:flex;align-items:center;gap:11px}.pill{border:1px solid #d5e7e7;color:#237668;background:#edfaf7;padding:7px 12px;border-radius:100px;font-size:11px;font-weight:750}.version{font-size:12px;color:#7990a0}
.pagehead{margin:27px 0 21px}.kicker{font-size:11px;color:#0a788c;font-weight:800;letter-spacing:.14em;text-transform:uppercase}.pagehead h1{font-size:30px;line-height:1.2;margin:8px 0 7px;letter-spacing:-.065em}.pagehead p{color:var(--muted);font-size:13px;margin:0;line-height:1.7}.hero{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:space-between;gap:16px;border-radius:17px;padding:24px 28px;background:linear-gradient(107deg,#133750,#0e5666 79%,#0e6670);color:white;margin-bottom:24px}.hero:after{content:"";position:absolute;width:250px;height:250px;border:1px solid #b3f0e82b;border-radius:50%;right:-70px;top:-125px;box-shadow:0 0 0 45px #a1e1e510,0 0 0 90px #a1e1e508}.hero>*{position:relative;z-index:1}.hero h2{font-size:21px;letter-spacing:-.045em;font-weight:700;margin:0 0 8px}.hero p{font-size:12px;color:#c4e1e5;line-height:1.6;margin:0;max-width:560px}.hero-kpi{text-align:center;padding:7px 18px;border-left:1px solid #ffffff3c;white-space:nowrap}.hero-kpi strong{font-size:28px;display:block;letter-spacing:-.05em}.hero-kpi span{font-size:10px;color:#b9dfe2}
.card{background:white;border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 3px 17px #172b3b05;overflow:hidden;margin-bottom:21px}.card-head{padding:21px 24px 17px;border-bottom:1px solid #eff2f5;display:flex;align-items:center;justify-content:space-between;gap:10px}.card-head h3{font-size:15px;margin:0;letter-spacing:-.025em}.sub{font-size:11px;color:#8a9aa8}.card-body{padding:20px 23px 23px}
.tag-evidence{font-size:9px;font-weight:800;border-radius:100px;padding:5px 9px;letter-spacing:.06em}.observed{color:#12634f;background:#e4f7ee}.hypothesis{color:#6a53a8;background:#f0ecfa}.tag{font-size:9px;font-weight:800;border-radius:100px;padding:5px 9px;letter-spacing:.01em}.src-connected{color:#12634f;background:#e4f7ee}.src-paid{color:#835b13;background:#fff2d7}.src-local_only{color:#6e7886;background:#eef2f5}.src-error{color:#a54351;background:#fff0f2}
.srctable,.domtable,.restable{width:100%;border-collapse:collapse;font-size:12px}.srctable th,.domtable th,.restable th{text-align:left;color:#7f92a3;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:8px 10px;border-bottom:1px solid var(--line)}.srctable td,.domtable td,.restable td{padding:10px;border-bottom:1px solid #f0f4f7;color:#2c445a;vertical-align:top}.srctable tr:last-child td,.domtable tr:last-child td,.restable tr:last-child td{border-bottom:0}.srcnote{font-size:10px;color:#8a9aa8;line-height:1.55;max-width:520px}.num{font-variant-numeric:tabular-nums}
.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px}.controls label{font-size:11px;color:#718495;font-weight:650}.controls select{margin-left:6px;border:1px solid #d6e2e9;background:#fff;padding:9px;border-radius:8px;font-size:12px;max-width:340px}.analyze{background:#11778a;color:white;border:0;padding:10px 14px;border-radius:9px;font-weight:750;font-size:11px;box-shadow:0 5px 17px #107a8e2a}.analyze:hover{background:#0c6577}.analyze:disabled{opacity:.6;cursor:wait}
.chartbox{background:#f9fbfd;border:1px solid #e8eef2;border-radius:11px;padding:14px;margin-bottom:16px}.chartbox svg{width:100%;height:220px;display:block}.axislabel{font-size:9px;fill:#7f92a3}.bestline{fill:none;stroke:#1a829a;stroke-width:2}.dot{fill:#6bb9bf}.dotbest{fill:#0d6675}.emptychart{display:grid;place-items:center;height:220px;color:#8a9aa8;font-size:12px}
.advfeed{display:flex;flex-direction:column;gap:9px}.advent{border:1px solid #e3ebf0;border-radius:11px;padding:11px 14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}.advdate{font-size:10px;color:#8a9aa8;font-variant-numeric:tabular-nums;min-width:78px}.advbench{font-size:11px;font-weight:750;color:#104f5e;min-width:170px}.advmodel{font-size:11px;color:#2c445a;margin-right:auto}.advdelta{font-size:11px;font-weight:750;color:#0d806d;font-variant-numeric:tabular-nums;white-space:nowrap}
.skillspanel{margin-top:16px;border-top:1px dashed #e3ebf0;padding-top:14px}.skillrow{display:flex;align-items:center;gap:10px;font-size:12px;padding:7px 0;border-bottom:1px solid #f0f4f7}.skillrow:last-child{border-bottom:0}.skillrow b{font-weight:650;min-width:260px}.track{flex:1;background:#edf4f6;border-radius:100px;height:5px;overflow:hidden}.track i{display:block;background:linear-gradient(90deg,#6bb9bf,#1a829a);height:100%;border-radius:100px}.skillrow span{font-size:11px;color:#3f7383;font-variant-numeric:tabular-nums;white-space:nowrap}
.error{padding:15px;background:#fff1f1;border:1px solid #f4cfcf;color:#9b2d2d;border-radius:10px;margin-bottom:14px;font-size:12px}.warn{margin-top:18px;color:#8e7017;background:#fffcf0;border:1px solid #f0e7bb;border-radius:10px;padding:12px 14px;font-size:10px;line-height:1.7}.footnote{margin-top:20px;color:#9badb9;font-size:11px;text-align:right} [hidden]{display:none!important}
@media(max-width:850px){.sidebar{display:none}.content{padding:0 18px 32px}.pagehead h1{font-size:26px}}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <div class="brand"><div class="brand-logo">FT</div><div><b>futuretwin<span style="color:#6fcac5">.</span></b><small>Workforce Intelligence</small></div></div>
  <a class="navitem" href="/" style="text-decoration:none;color:#9fd8cf"><span class="navicon">&larr;</span> Back to FutureTwin</a>
  <div class="sidetitle">Workspace</div>
  <a class="navitem" href="/career" style="text-decoration:none"><span class="navicon">▣</span> Job Intelligence</a>
  <a class="navitem" href="/advancements" style="text-decoration:none"><span class="navicon">◈</span> AI Advancements</a>
  <div class="navitem active"><span class="navicon">▤</span> Benchmark Intelligence</div>
  <div class="navitem"><span class="navicon">◇</span> Skill Discovery <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <a class="navitem" href="/jobmarket" style="text-decoration:none"><span class="navicon">◷</span> Job Market</a>
  <div class="navitem"><span class="navicon">✧</span> Future Scenarios <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <div class="sideline"></div>
  <div class="sidetitle">Model stack</div>
  <div class="navitem"><span class="navicon">↗</span> Fine-tuned MiniLM</div>
  <div class="navitem"><span class="navicon">≋</span> ESCO Ontology</div>
  <div class="sidebar-bottom"><span class="live"><span class="small-dot"></span>Multi-source frontier</span><p>Frontier advancement = a dated new result beating the previous best on the same benchmark version.</p></div>
</aside>
<main class="content">
  <div class="topbar"><div class="crumb">FutureTwin / <strong>Benchmark Intelligence</strong></div><div class="top-right"><span class="version">Multi-source v1</span><span class="pill">● &nbsp;PostgreSQL · 5 sources</span></div></div>
  <div class="pagehead"><div><div class="kicker">Multi-source benchmark intelligence</div><h1>Track the AI frontier, benchmark by benchmark.</h1><p>Observed results from connected sources. Skill implications stay labelled as hypotheses.</p></div></div>
  <section class="hero"><div><h2>One frontier, many measuring sticks.</h2><p>Artificial Analysis indexes, SWE-bench leaderboards and LiveBench releases in one normalized store — compared only where benchmark versions allow it.</p></div><div class="hero-kpi"><strong id="kpi-sources">–</strong><span>sources connected</span></div><div class="hero-kpi"><strong id="kpi-models">–</strong><span>models tracked</span></div><div class="hero-kpi"><strong id="kpi-frontier">–</strong><span>frontier advancements</span></div></section>

  <section class="card">
    <div class="card-head"><div><h3>Source connectors</h3><span class="sub">access, attribution and coverage</span></div><span class="tag-evidence observed">OBSERVED · collected</span></div>
    <div class="card-body"><table class="srctable"><thead><tr><th>Source</th><th>Access</th><th>Benchmarks</th><th>Models</th><th>Results</th><th>Status / attribution</th></tr></thead><tbody id="src-rows"><tr><td colspan="6" style="color:#8a9aa8">Loading…</td></tr></tbody></table></div>
  </section>

  <section class="card">
    <div class="card-head"><div><h3>AI progress by domain</h3><span class="sub">aggregated over connected sources</span></div><span class="tag-evidence observed">OBSERVED · measured</span></div>
    <div class="card-body"><table class="domtable"><thead><tr><th>Domain</th><th>Benchmarks</th><th>Models</th><th>Results</th><th>Latest dated evaluation</th></tr></thead><tbody id="dom-rows"><tr><td colspan="5" style="color:#8a9aa8">Loading…</td></tr></tbody></table></div>
  </section>

  <section class="card">
    <div class="card-head"><div><h3>Benchmark explorer</h3><span class="sub" id="explorer-sub">running best score over time</span></div><span class="tag-evidence observed">OBSERVED · measured</span></div>
    <div class="card-body">
      <div class="controls">
        <label>Benchmark <select id="benchsel"></select></label>
        <label>Period <select id="periodsel"><option value="">All time</option><option value="365">Last 12 months</option><option value="180">Last 6 months</option><option value="90">Last 90 days</option></select></label>
        <button class="analyze" id="mapskills" type="button" disabled>✦ &nbsp;Map benchmark tasks to ESCO skills</button>
      </div>
      <div id="error" class="error" hidden></div>
      <div class="chartbox" id="chartbox"><div class="emptychart">Loading…</div></div>
      <table class="restable"><thead><tr><th>#</th><th>Model</th><th>Score</th><th>Unit</th><th>Evaluation date</th><th>Model release</th><th>Source</th></tr></thead><tbody id="res-rows"></tbody></table>
      <div id="skillspanel" class="skillspanel" hidden>
        <div class="controls" style="margin-bottom:6px"><span class="tag-evidence hypothesis">HYPOTHESIS · unvalidated MiniLM matching</span></div>
        <div id="tasktexts" class="sub" style="margin-bottom:10px;line-height:1.6"></div>
        <div id="skillrows"></div>
        <div class="warn">⚠ These are ESCO skills semantically similar to what the benchmark measures — not verified occupational impacts and not skill-demand predictions. Cosine similarity is not a probability.</div>
      </div>
    </div>
  </section>

  <section class="card">
    <div class="card-head"><div><h3>Frontier advancements</h3><span class="sub" id="frontier-sub">dated new results beating the previous best on the same benchmark version</span></div><span class="tag-evidence observed">OBSERVED · measured</span></div>
    <div class="card-body"><div class="advfeed" id="advfeed"><p class="sub" style="margin:0">Loading…</p></div></div>
  </section>

  <div class="footnote">FutureTwin AI · Development preview · Sources retain their own terms and attribution</div>
</main>
</div>
<script>
(()=>{
'use strict';
const $=id=>document.getElementById(id);
function element(tag,cls,content){let n=document.createElement(tag);if(cls)n.className=cls;if(content!==undefined)n.textContent=String(content);return n}
function add(node,child){node.appendChild(child);return child}
let benchmarks=[];

async function fetchJSON(url){
  const res=await fetch(url);let data;
  try{data=await res.json()}catch{throw new Error('Non-JSON response (HTTP '+res.status+')')}
  if(!res.ok)throw new Error(data.error||('HTTP '+res.status));
  return data;
}

async function loadSources(){
  try{
    const rows=await fetchJSON('/api/benchmarks/sources');
    const tbody=$('src-rows');tbody.replaceChildren();
    let connected=0,models=new Set();
    for(const s of rows){
      if(s.access==='connected'&&s.results>0)connected++;
      const tr=add(tbody,element('tr'));
      add(tr,element('td','',s.name)).style.fontWeight='650';
      add(tr,element('td','')).appendChild(Object.assign(element('span','tag src-'+s.access,s.access.replace('_',' ')),{}));
      add(tr,element('td','num',s.benchmarks));
      add(tr,element('td','num',s.models));
      add(tr,element('td','num',s.results.toLocaleString()));
      const notecell=add(tr,element('td','srcnote',s.note+' — '+s.attribution));
      if(s.last_status){
        const line=document.createElement('div');
        line.style.cssText='font-size:10px;margin-top:3px;color:'+(s.last_status==='ok'?'#0b6e5d':'#a33327');
        line.textContent='Last run: '+s.last_status+(s.last_run_at?' · '+String(s.last_run_at).slice(0,16).replace('T',' '):'')+(s.last_error?' — '+s.last_error.slice(0,90):'');
        notecell.appendChild(line);
        if(s.last_success){
          const ok=document.createElement('div');
          ok.style.cssText='font-size:10px;color:#687b8d';
          ok.textContent='Last successful refresh: '+String(s.last_success).slice(0,16).replace('T',' ');
          notecell.appendChild(ok);
        }
      }
    }
    $('kpi-sources').textContent=connected+' / '+rows.length;
  }catch(e){
    $('src-rows').innerHTML='';const tr=add($('src-rows'),element('tr'));const td=add(tr,element('td','','Sources unavailable: '+e.message));td.colSpan=6;td.style.color='#9b2d2d';
  }
}

async function loadOverview(){
  const data=await fetchJSON('/api/benchmarks/overview');
  benchmarks=data.benchmarks||[];
  const tbody=$('dom-rows');tbody.replaceChildren();
  let modelSet=new Set();
  for(const d of data.domains||[]){
    const tr=add(tbody,element('tr'));
    add(tr,element('td','',d.domain)).style.fontWeight='650';
    add(tr,element('td','num',d.benchmarks));
    add(tr,element('td','num',d.models));
    add(tr,element('td','num',Number(d.results).toLocaleString()));
    add(tr,element('td','num',d.latest_evaluation||'—'));
  }
  for(const b of benchmarks){
    // models per benchmark row already counted server-side; total distinct across store approximated below
  }
  const sel=$('benchsel');sel.replaceChildren();
  const seen=new Set();
  for(const b of benchmarks){
    const label=b.benchmark_name+(b.benchmark_version?' ('+b.benchmark_version+')':'');
    if(seen.has(label))continue;seen.add(label);
    const opt=add(sel,element('option','',label));
    opt.value=b.benchmark_name+'||'+b.benchmark_version;
  }
  $('kpi-models').textContent=(data.models_total||'—');
  sel.disabled=!benchmarks.length;
  if(benchmarks.length){await loadResults()}
}

async function loadResults(){
  const val=$('benchsel').value;if(!val)return;
  const [benchmark,version]=val.split('||');
  const days=$('periodsel').value;
  $('error').hidden=true;
  let rows;
  try{
    rows=await fetchJSON('/api/benchmarks/results?benchmark='+encodeURIComponent(benchmark)+'&version='+encodeURIComponent(version||'')+(days?'&days='+days:''));
  }catch(e){$('error').textContent='Could not load results: '+e.message;$('error').hidden=false;return}
  $('explorer-sub').textContent=rows.length+' results · running best over time';
  $('mapskills').disabled=false;
  renderResults(rows);
  renderChart(rows);
}

function effDate(r){return r.evaluation_date||r.model_release_date||(r.collected_at?String(r.collected_at).slice(0,10):null)}

function renderResults(rows){
  const tbody=$('res-rows');tbody.replaceChildren();
  const sorted=[...rows].sort((a,b)=>b.score-a.score).slice(0,15);
  sorted.forEach((r,i)=>{
    const tr=add(tbody,element('tr'));
    add(tr,element('td','num',i+1));
    add(tr,element('td','',r.model_name)).style.fontWeight='650';
    add(tr,element('td','num',r.score));
    add(tr,element('td','',r.score_unit||''));
    add(tr,element('td','num',r.evaluation_date||'—'));
    add(tr,element('td','num',r.model_release_date||'—'));
    add(tr,element('td','',r.source));
  });
}

function renderChart(rows){
  const box=$('chartbox');box.replaceChildren();
  const dated=rows.map(r=>({d:effDate(r),s:r.score,m:r.model_name})).filter(r=>r.d).sort((a,b)=>a.d<b.d?-1:1);
  if(dated.length<2){add(box,element('div','emptychart','Not enough dated results to draw a frontier for this selection.'));return}
  const W=860,H=220,pad={l:44,r:14,t:14,b:26};
  const times=dated.map(r=>new Date(r.d).getTime());
  const t0=Math.min(...times),t1=Math.max(...times);
  const s0=Math.min(...dated.map(r=>r.s)),s1=Math.max(...dated.map(r=>r.s));
  const x=t=>pad.l+(t1>t0?(t-t0)/(t1-t0):0.5)*(W-pad.l-pad.r);
  const y=s=>pad.t+(1-(s1>s0?(s-s0)/(s1-s0):0.5))*(H-pad.t-pad.b);
  let best=-Infinity;const frontier=[];
  for(const r of dated){if(r.s>best){best=r.s;frontier.push(r)}}
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('viewBox','0 0 '+W+' '+H);
  const ns=n=>document.createElementNS('http://www.w3.org/2000/svg',n);
  for(let i=0;i<=4;i++){
    const val=s0+(s1-s0)*i/4,gy=y(val);
    const line=ns('line');line.setAttribute('x1',pad.l);line.setAttribute('x2',W-pad.r);line.setAttribute('y1',gy);line.setAttribute('y2',gy);line.setAttribute('stroke','#e5ecf1');svg.appendChild(line);
    const lbl=ns('text');lbl.setAttribute('x',6);lbl.setAttribute('y',gy+3);lbl.setAttribute('class','axislabel');lbl.textContent=Math.round(val*10)/10;svg.appendChild(lbl);
  }
  for(const r of dated){const c=ns('circle');c.setAttribute('cx',x(new Date(r.d).getTime()));c.setAttribute('cy',y(r.s));c.setAttribute('r',2.4);c.setAttribute('class','dot');c.setAttribute('opacity','.45');const t=ns('title');t.textContent=r.d+' · '+r.m+' · '+r.s;c.appendChild(t);svg.appendChild(c)}
  const path=ns('polyline');path.setAttribute('points',frontier.map(r=>x(new Date(r.d).getTime())+','+y(r.s)).join(' '));path.setAttribute('class','bestline');svg.appendChild(path);
  for(const r of frontier){const c=ns('circle');c.setAttribute('cx',x(new Date(r.d).getTime()));c.setAttribute('cy',y(r.s));c.setAttribute('r',3.6);c.setAttribute('class','dotbest');const t=ns('title');t.textContent='Frontier: '+r.d+' · '+r.m+' · '+r.s;c.appendChild(t);svg.appendChild(c)}
  const first=ns('text');first.setAttribute('x',pad.l);first.setAttribute('y',H-6);first.setAttribute('class','axislabel');first.textContent=dated[0].d;svg.appendChild(first);
  const last=ns('text');last.setAttribute('x',W-pad.r);last.setAttribute('y',H-6);last.setAttribute('text-anchor','end');last.setAttribute('class','axislabel');last.textContent=dated[dated.length-1].d;svg.appendChild(last);
  box.appendChild(svg);
}

async function loadFrontier(){
  try{
    const events=await fetchJSON('/api/benchmarks/frontier?limit=40');
    $('kpi-frontier').textContent=events.length+(events.length>=40?'+':'');
    const feed=$('advfeed');feed.replaceChildren();
    if(!events.length){add(feed,element('p','sub','No frontier advancements detected yet. Unchanged snapshots are not treated as evidence of no progress — only dated new results count.'));return}
    for(const e of events){
      const row=add(feed,element('div','advent'));
      add(row,element('span','advdate',e.evaluation_date||'undated'));
      add(row,element('span','advbench',e.benchmark_name));
      add(row,element('span','advmodel',e.model_name));
      add(row,element('span','advdelta',(e.previous_best===null?'':e.previous_best+' → ')+e.new_best+' (+'+e.improvement+')'));
    }
  }catch(e){$('advfeed').innerHTML='';add($('advfeed'),element('p','sub','Frontier feed unavailable: '+e.message))}
}

async function mapSkills(){
  const val=$('benchsel').value;if(!val)return;
  const [benchmark]=val.split('||');
  const btn=$('mapskills');btn.disabled=true;btn.textContent='Mapping…';
  $('error').hidden=true;
  try{
    const data=await fetchJSON('/api/benchmarks/skills?benchmark='+encodeURIComponent(benchmark)+'&top_k=10');
    const panel=$('skillspanel');panel.hidden=false;
    $('tasktexts').textContent='Task descriptions matched: '+(data.tasks||[]).map(t=>t.task_text).join('  |  ');
    const box=$('skillrows');box.replaceChildren();
    for(const s of data.skills||[]){
      const row=add(box,element('div','skillrow'));
      add(row,element('b','',s.skill));
      const track=add(row,element('div','track'));const bar=add(track,element('i'));
      bar.style.width=(Math.max(0,Math.min(s.cosine_similarity,1))*100)+'%';
      add(row,element('span','','cos '+s.cosine_similarity.toFixed(4)));
    }
    if(!(data.skills||[]).length)add(box,element('p','sub','No skills passed the similarity floor.'));
  }catch(e){$('error').textContent='Skill mapping failed: '+e.message;$('error').hidden=false}
  finally{btn.disabled=false;btn.textContent='✦  Map benchmark tasks to ESCO skills'}
}

$('benchsel').addEventListener('change',loadResults);
$('periodsel').addEventListener('change',loadResults);
$('mapskills').addEventListener('click',mapSkills);
loadSources();loadFrontier();loadOverview().catch(e=>{$('error').textContent='Overview failed: '+e.message;$('error').hidden=false});
})();
</script>
</body>
</html>'''


@app.get("/benchmarks")
def futuretwin_benchmarks_page():
    return Response(BENCHMARKS_HTML, mimetype="text/html")


@app.get("/api/benchmarks/sources")
def api_benchmarks_sources():
    from benchmark_store import get_source_summaries
    try:
        return jsonify(get_source_summaries())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/api/benchmarks/overview")
def api_benchmarks_overview():
    from benchmark_store import (
        get_benchmark_list,
        get_current_baseline,
        get_domain_overview,
        _rows,
    )
    try:
        domains = get_domain_overview()
        benchmarks = get_benchmark_list()
        total = _rows("SELECT COUNT(DISTINCT model_name) AS n FROM benchmark_results")
        return jsonify({
            "domains": domains,
            "benchmarks": benchmarks,
            "models_total": total[0]["n"] if total else 0,
            "current_measurements": get_current_baseline(),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/api/benchmarks/results")
def api_benchmarks_results():
    from benchmark_store import get_benchmark_results
    benchmark = request.args.get("benchmark", "").strip()
    version = request.args.get("version", "").strip() or None
    days_raw = request.args.get("days", "").strip()
    if not benchmark:
        return jsonify({"error": "benchmark is required."}), 400
    days = None
    if days_raw:
        try:
            days = int(days_raw)
        except ValueError:
            return jsonify({"error": "days must be an integer."}), 400
        if not 1 <= days <= 3650:
            return jsonify({"error": "days must be between 1 and 3650."}), 400
    try:
        rows = get_benchmark_results(benchmark, version=version, days=days)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    for row in rows:
        for key in ("evaluation_date", "model_release_date", "collected_at"):
            if row.get(key) is not None:
                row[key] = str(row[key])
    return jsonify(rows[:500])


@app.get("/api/benchmarks/frontier")
def api_benchmarks_frontier():
    from benchmark_store import get_frontier_events
    benchmark = request.args.get("benchmark", "").strip() or None
    try:
        limit = int(request.args.get("limit", "60"))
    except ValueError:
        return jsonify({"error": "limit must be an integer."}), 400
    if not 1 <= limit <= 500:
        return jsonify({"error": "limit must be between 1 and 500."}), 400
    try:
        events = get_frontier_events(benchmark=benchmark, limit=limit)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    for event in events:
        if event.get("evaluation_date") is not None:
            event["evaluation_date"] = str(event["evaluation_date"])
    return jsonify(events)


@app.get("/api/benchmarks/skills")
def api_benchmarks_skills():
    """Map a benchmark's preserved task descriptions to ESCO skill candidates
    with the fine-tuned MiniLM. Hypothesis output, clearly labelled."""
    from benchmark_store import get_benchmark_tasks
    from futuretwin_impact_engine import match_task_texts
    benchmark = request.args.get("benchmark", "").strip()
    if not benchmark:
        return jsonify({"error": "benchmark is required."}), 400
    try:
        top_k = int(request.args.get("top_k", "10"))
    except ValueError:
        return jsonify({"error": "top_k must be an integer."}), 400
    if not 1 <= top_k <= 50:
        return jsonify({"error": "top_k must be an integer from 1 to 50."}), 400
    tasks = get_benchmark_tasks(benchmark)
    if not tasks:
        return jsonify({"error": f"No preserved task descriptions for {benchmark!r}."}), 404
    try:
        skills = match_task_texts(tasks, top_k=top_k)
    except Exception as exc:
        return jsonify({"error": f"Skill matching failed: {exc}"}), 500
    return jsonify({
        "benchmark": benchmark,
        "tasks": tasks,
        "skills": skills,
        "warning": (
            "Semantic candidates from the fine-tuned MiniLM; cosine similarity "
            "is not a probability and these are not verified occupational "
            "impacts or skill-demand predictions."
        ),
    })


JOBMARKET_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="light" />
<title>FutureTwin · Job-Market Intelligence</title>
<style>
:root{--navy:#0a1b2d;--navy2:#132a42;--sky:#1d6d87;--blue:#176b88;--teal:#0d806d;--ink:#172b40;--muted:#687b8d;--bg:#f4f7fa;--line:#e5ecf1;--paper:#fff;--radius:16px}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:-.009em}
button,select{font:inherit}
.shell{display:flex;min-height:100vh}.sidebar{flex:0 0 238px;background:var(--navy);color:#fff;display:flex;flex-direction:column;padding:29px 18px;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:11px;padding:0 8px 20px}.brand-logo{width:37px;height:37px;border-radius:11px;background:linear-gradient(135deg,#58c1b0,#2b7f95);display:grid;place-items:center;font-weight:800;font-size:13px}.brand b{font-size:16.5px}.brand small{display:block;color:#92a9bb;font-size:10.5px;margin-top:2px}
.sidetitle{color:#8099ac;letter-spacing:.15em;text-transform:uppercase;font-size:10px;font-weight:700;padding:0 13px;margin:10px 0 10px}.navitem{display:flex;align-items:center;gap:12px;border-radius:10px;padding:12px 13px;font-size:13px;color:#b9cbda;margin-bottom:5px}.navitem.active{background:#1c4055;color:#e6fcfc;font-weight:650;border:1px solid #30637a}.navicon{font-size:17px;width:22px;text-align:center;opacity:.9}.sideline{height:1px;background:#294057;margin:15px 11px 24px}.sidebar-bottom{margin-top:auto;padding:17px 13px;background:#122c43;border:1px solid #29465c;border-radius:12px}.sidebar-bottom .live{color:#b1e3dc;font-weight:700;font-size:12px}.small-dot{width:8px;height:8px;border-radius:50%;background:#67ccb6;display:inline-block;margin-right:6px}.sidebar-bottom p{font-size:11px;line-height:1.65;color:#a4b8c8;margin-bottom:0}
.content{flex:1;min-width:0;padding:0 34px 40px}
.topbar{display:flex;justify-content:space-between;align-items:center;height:70px}.crumb{color:var(--muted);font-size:12.5px}.crumb strong{color:var(--ink)}.pill{background:#e3f3ef;color:#0b6e5d;font-size:11px;font-weight:700;padding:6px 12px;border-radius:999px}
.pagehead{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin:6px 0 18px}.pagehead h1{font-size:30px;margin:4px 0 6px;letter-spacing:-.03em}.pagehead p{margin:0;color:var(--muted);font-size:13.5px;max-width:680px}.kicker{color:var(--sky);text-transform:uppercase;font-size:10.5px;font-weight:800;letter-spacing:.14em}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;margin-bottom:18px}
.grid2 .card{margin-bottom:0}
.card-head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:18px 20px;border-bottom:1px solid var(--line)}.card-head h3{margin:0;font-size:15px}.sub{color:var(--muted);font-size:11.5px}
.card-body{padding:14px 20px 18px;overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:12.5px}th{text-align:left;color:var(--muted);font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;padding:6px 8px;border-bottom:1px solid var(--line)}td{padding:7px 8px;border-bottom:1px solid #eef3f7;vertical-align:top}
.chip{display:inline-block;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.07em;padding:3px 9px;border-radius:999px}.chip-connected{background:#e3f3ef;color:#0b6e5d}.chip-pending_key{background:#fdf1dd;color:#8a5d00}.chip-unreachable{background:#fbe7e5;color:#a33327}
.up{color:#0b6e5d;font-weight:700}.down{color:#a33327;font-weight:700}
.tag{display:inline-block;font-size:10px;font-weight:800;padding:3px 9px;border-radius:999px;letter-spacing:.07em}.tag-observed{background:#e3f3ef;color:#0b6e5d}.tag-hypothesis{background:#efe9fb;color:#5b3d99}
.warn{background:#fdf6e8;border:1px solid #eedcaa;color:#6b5410;border-radius:10px;padding:11px 13px;font-size:11.5px;line-height:1.6;margin:12px 20px 16px}
.muted{color:var(--muted);font-size:11.5px;line-height:1.6}
.error{background:#fbe7e5;border:1px solid #f0b9b2;color:#8c2f22;border-radius:10px;padding:12px 14px;font-size:12px;margin:0 0 16px}
.footnote{color:var(--muted);font-size:11px;text-align:center;margin-top:8px;line-height:1.8}.footnote a{color:var(--sky)}
.barwrap{display:flex;align-items:flex-end;gap:3px;height:70px;padding:4px 2px 20px;position:relative}
.bar{flex:1;background:#bfd9e2;border-radius:3px 3px 0 0;position:relative;min-width:8px}
.bar em{position:absolute;top:-15px;left:50%;transform:translateX(-50%);font-style:normal;font-size:9px;color:var(--ink);font-weight:700}
.bar span{position:absolute;bottom:-16px;left:50%;transform:translateX(-50%);font-size:9px;color:var(--muted);white-space:nowrap}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:9px;padding:16px 20px}
.kpi{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:11px 12px}.kpi strong{display:block;font-size:20px;margin:2px 0}.kpi span{font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;font-weight:700}
@media(max-width:1150px){.sidebar{flex-basis:198px}.content{padding:0 22px 35px}}
@media(max-width:850px){.sidebar{display:none}.content{padding:0 18px 32px}.grid2{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <div class="brand"><div class="brand-logo">FT</div><div><b>futuretwin<span style="color:#6fcac5">.</span></b><small>Workforce Intelligence</small></div></div>
  <a class="navitem" href="/" style="text-decoration:none;color:#9fd8cf"><span class="navicon">&larr;</span> Back to FutureTwin</a>
  <div class="sidetitle">Workspace</div>
  <a class="navitem" href="/career" style="text-decoration:none"><span class="navicon">▣</span> Job Intelligence</a>
  <a class="navitem" href="/advancements" style="text-decoration:none"><span class="navicon">◈</span> AI Advancements</a>
  <a class="navitem" href="/benchmarks" style="text-decoration:none"><span class="navicon">▤</span> Benchmark Intelligence</a>
  <div class="navitem active"><span class="navicon">◷</span> Job Market</div>
  <div class="navitem"><span class="navicon">◇</span> Skill Discovery <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <div class="navitem"><span class="navicon">✧</span> Future Scenarios <span style="font-size:9px;margin-left:auto;color:#7190a6">Soon</span></div>
  <div class="sideline"></div>
  <div class="sidetitle">Model stack</div>
  <div class="navitem"><span class="navicon">↗</span> Fine-tuned MiniLM</div>
  <div class="navitem"><span class="navicon">≋</span> ESCO Ontology</div>
  <div class="sidebar-bottom"><span class="live"><span class="small-dot"></span>Observed evidence only</span><p>Job-market trends are measurements from collected sources. No forecasting model is trained yet.</p></div>
</aside>
<main class="content">
  <div class="topbar"><div class="crumb">FutureTwin / <strong>Job Market</strong></div><div class="top-right"><span class="pill">● &nbsp;Phase 2 · Evidence engine</span></div></div>
  <div class="pagehead"><div><div class="kicker">Job-market intelligence</div><h1>What hiring demand actually shows.</h1><p>Real job advertisements and official Malaysian labour statistics — deduplicated, dated, and skill-standardized with the existing ESCO + MiniLM pipeline. Observed trends are kept strictly separate from AI-impact hypotheses.</p></div></div>
  <div id="error" class="error" hidden></div>

  <section class="card">
    <div class="card-head"><h3>Source coverage &amp; collection</h3><span class="sub">Deduplicated · every run logged</span></div>
    <div class="card-body"><div class="kpis" id="covkpis" style="padding:2px 0 14px"></div><table><thead><tr><th>Source</th><th>Type / coverage</th><th>Status</th><th>Postings</th><th>Duplicates</th><th>With skills</th><th>Posting dates</th><th>Latest refresh</th></tr></thead><tbody id="sources"></tbody></table>
    <p class="muted" style="margin:14px 0 6px"><b>Collection history</b> — every run is logged; a failure in one source never stops the others. Postings are never deleted, so history survives listings disappearing from source APIs.</p>
    <table><thead><tr><th>Run finished</th><th>Source</th><th>Status</th><th>Stored</th><th>New</th><th>Duplicates</th><th>Date coverage</th></tr></thead><tbody id="history"></tbody></table></div>
  </section>

  <section class="card">
    <div class="card-head"><h3>Job advertisements per month</h3><span class="sub" id="monthsub">Global remote boards · NOT representative of Malaysia</span></div>
    <div class="card-body"><div class="barwrap" id="monthchart"></div></div>
    <div class="warn">⚠ <b>Coverage caution.</b> Job boards expose only their current listing window — historical depth accumulates with each scheduled run. Malaysian official statistics (below) reach back years; job ads do not. Remote boards skew toward tech roles. No forecasting model is trained until coverage is adequate (Phase-2 requirement).</div>
  </section>

  <div class="grid2">
    <section class="card">
      <div class="card-head"><h3>Rising-demand skills</h3><span class="sub">Global remote ads · not Malaysia</span><span class="tag tag-observed">OBSERVED</span></div>
      <div class="card-body"><table><thead><tr><th>ESCO skill</th><th>Ads (recent)</th><th>Share</th><th>Δ share</th><th>Δ ads</th></tr></thead><tbody id="rising"></tbody></table></div>
    </section>
    <section class="card">
      <div class="card-head"><h3>Declining-demand skills</h3><span class="sub">Global remote ads · not Malaysia</span><span class="tag tag-observed">OBSERVED</span></div>
      <div class="card-body"><table><thead><tr><th>ESCO skill</th><th>Ads (recent)</th><th>Share</th><th>Δ share</th><th>Δ ads</th></tr></thead><tbody id="declining"></tbody></table></div>
    </section>
  </div>
  <p class="muted" id="trendnote" style="margin:-6px 0 18px"></p>

  <section class="card">
    <div class="card-head"><h3>Malaysia labour indicators</h3><span class="sub">OpenDOSM · Dept. of Statistics Malaysia · observed statistics</span></div>
    <div class="kpis" id="mykpis"></div>
    <div class="card-body">
      <div class="grid2" style="margin-bottom:0">
        <table><thead><tr><th>Occupation (employees)</th><th>Latest</th><th>Δ year</th><th>Median wage</th></tr></thead><tbody id="occmovers"></tbody></table>
        <table><thead><tr><th>Sector (employment share)</th><th>First</th><th>Latest</th><th>Δ pp</th></tr></thead><tbody id="sectors"></tbody></table>
      </div>
    </div>
  </section>

  <section class="card">
    <div class="card-head"><h3>AI advancements in the same window</h3><span class="tag tag-hypothesis">HYPOTHESIS SPACE</span></div>
    <div class="card-body"><table><thead><tr><th>Date</th><th>Benchmark</th><th>Model</th><th>Frontier move</th></tr></thead><tbody id="ailinks"></tbody></table></div>
    <div class="warn" id="ailinkwarn">⚠ Frontier benchmark events are shown next to hiring trends for exploration only. <b>Temporal co-occurrence is not evidence that AI caused a hiring change.</b> Any causal claim needs a validated study design, which is out of scope here.</div>
  </section>

  <div class="footnote">FutureTwin AI · Development preview · Job ads: <a href="https://remotive.com/">Remotive</a> · <a href="https://remoteok.com/">Remote OK</a> (attribution required by Remote OK API terms) · Statistics: <a href="https://open.dosm.gov.my/">OpenDOSM / DOSM</a></div>
</main>
</div>
<script>
const $=id=>document.getElementById(id);
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function fetchJSON(url){const r=await fetch(url);const t=await r.text();let d;try{d=JSON.parse(t)}catch(e){throw new Error(r.status+' non-JSON response')}if(!r.ok)throw new Error(d.error||r.status);return d}
function tr(tds){const row=document.createElement('tr');for(const h of tds){const td=document.createElement('td');td.innerHTML=h;row.appendChild(td)}return row}

async function loadOverview(){
  const d=await fetchJSON('/api/jobmarket/overview');
  const tb=$('sources');tb.replaceChildren();
  for(const s of d.sources){
    tb.appendChild(tr([
      '<b>'+esc(s.name)+'</b><br><span class="muted">'+esc(s.license)+'</span>',
      esc(s.kind)+' · '+esc(s.country),
      '<span class="chip chip-'+esc(s.access)+'">'+esc(s.access.replace('_',' '))+'</span>',
      s.postings||'—', s.duplicates||'—', s.with_skills||'—',
      s.earliest_posting?esc(s.earliest_posting)+' → '+esc(s.latest_posting):'<span class="muted">'+esc((s.note||'').slice(0,90))+'…</span>',
      (s.last_success?'<span class="up">'+esc(String(s.last_success).slice(0,16).replace('T',' '))+'</span>':(s.last_status?'<span class="muted">'+esc(s.last_status)+'</span>':'<span class="muted">—</span>'))+(s.last_error?'<br><span class="down" style="font-size:10px">'+esc(s.last_error.slice(0,80))+'</span>':'')
    ]));
  }
  const t=d.totals||{};
  const k=$('covkpis');k.replaceChildren();
  const kpis=[['Canonical postings',t.canonical??0,'deduplicated, never deleted'],['Duplicates flagged',t.duplicates??0,'kept, excluded from trends'],['With ESCO skills',t.with_skills??0,'fine-tuned MiniLM'],['Posting window',(t.earliest&&t.latest)?esc(t.earliest)+' → '+esc(t.latest):'—','grows with every run'],['Coverage contexts',(t.countries||[]).length,esc((t.countries||[]).join(' · '))]];
  for(const [label,val,sub] of kpis){const div=document.createElement('div');div.className='kpi';div.innerHTML='<span>'+label+'</span><strong style="font-size:15px">'+val+'</strong><span>'+sub+'</span>';k.appendChild(div)}
  const hb=$('history');hb.replaceChildren();
  for(const log of d.collection_log||[]){
    hb.appendChild(tr([String(log.finished_at).slice(0,19),esc(log.source),esc(log.status),log.stored,log.new_postings??'—',log.duplicates,log.min_date?esc(log.min_date)+' → '+esc(log.max_date):'<span class="muted">—</span>']));
  }
}

function trendRows(tbody,rows,cls){
  const tb=$(tbody);tb.replaceChildren();
  if(!rows.length){tb.appendChild(tr(['<span class="muted">Not enough observations yet (min '+(window.__minMentions||5)+' recent ads per skill).</span>','','','','']));return}
  for(const r of rows.slice(0,10)){
    tb.appendChild(tr(['<b>'+esc(r.skill)+'</b>',r.recent_ads,r.share_recent_pct+'%',
      '<span class="'+cls+'">'+(r.share_delta_pp>0?'+':'')+r.share_delta_pp+' pp</span>',
      '<span class="'+(r.abs_delta>=0?'up':'down')+'">'+(r.abs_delta>0?'+':'')+r.abs_delta+'</span>']));
  }
}

async function loadTrends(){
  const d=await fetchJSON('/api/jobmarket/skill-trends');
  window.__minMentions=d.min_mentions;
  trendRows('rising',d.rising,'up');
  trendRows('declining',d.declining,'down');
  const w=d.windows||{};
  if(w.recent_start)$('trendnote').textContent='Share = % of that window’s canonical ads mentioning the skill (MiniLM cosine ≥ '+d.similarity_floor+', unvalidated heuristic). Recent: '+w.recent_start+' → '+w.recent_end+' ('+w.postings_recent+' ads) vs prior: '+w.prior_start+' → '+w.prior_end+' ('+w.postings_prior+' ads). Absolute counts and shares are reported separately — they can move in opposite directions.';
  const mc=$('monthchart');mc.replaceChildren();
  const months=d.postings_by_month||[];
  const max=Math.max(1,...months.map(m=>m.count));
  for(const m of months){
    const bar=document.createElement('div');bar.className='bar';
    bar.style.height=Math.max(4,Math.round(m.count/max*60))+'px';
    bar.innerHTML='<em>'+m.count+'</em><span>'+esc(m.month)+'</span>';
    mc.appendChild(bar);
  }
  if(!months.length)mc.innerHTML='<p class="muted">No dated postings collected yet.</p>';
}

async function loadMalaysia(){
  const d=await fetchJSON('/api/jobmarket/malaysia');
  const k=$('mykpis');k.replaceChildren();
  const lf=d.labour_force||{};
  const kpis=[
    ['Unemployment (MY)',lf.unemployment_rate!=null?lf.unemployment_rate+'%':'—',esc(lf.latest_date||'')],
    ['Year earlier',lf.unemployment_rate_year_ago!=null?lf.unemployment_rate_year_ago+'%':'—',esc(lf.year_ago_date||'')],
    ['Participation rate',lf.participation_rate!=null?lf.participation_rate+'%':'—','labour force'],
    ['Employed (000s)',lf.employed_thousands!=null?lf.employed_thousands.toLocaleString():'—','Malaysia'],
  ];
  for(const [label,val,sub] of kpis){const div=document.createElement('div');div.className='kpi';div.innerHTML='<span>'+label+'</span><strong>'+val+'</strong><span>'+sub+'</span>';k.appendChild(div)}
  const occ=$('occmovers');occ.replaceChildren();
  for(const m of (d.occupation_movers||[]).slice(0,8)){
    occ.appendChild(tr(['<b>'+esc(m.occupation)+'</b>',m.employees_latest,'<span class="'+(m.change_pct>=0?'up':'down')+'">'+(m.change_pct>0?'+':'')+m.change_pct+'%</span>',m.median_wage!=null?'RM '+m.median_wage:'—']));
  }
  const sec=$('sectors');sec.replaceChildren();
  for(const s of (d.sector_shifts||[]).slice(0,8)){
    sec.appendChild(tr(['<b>'+esc(s.sector)+'</b>',s.share_first_pct+'%',s.share_latest_pct+'%','<span class="'+(s.delta_pp>=0?'up':'down')+'">'+(s.delta_pp>0?'+':'')+s.delta_pp+' pp</span>']));
  }
}

async function loadAiLinks(){
  const d=await fetchJSON('/api/jobmarket/ai-links');
  const tb=$('ailinks');tb.replaceChildren();
  if(!d.frontier_events.length)tb.appendChild(tr(['<span class="muted">No frontier benchmark events fall inside the current ad-collection window'+(d.window&&d.window.earliest_posting?' ('+esc(d.window.earliest_posting)+' → '+esc(d.window.latest_posting)+')':'')+'.</span>','','','']));
  for(const e of d.frontier_events){
    tb.appendChild(tr([esc(e.evaluation_date),esc(e.benchmark_name),'<b>'+esc(e.model_name)+'</b>',(e.previous_best!=null?e.previous_best+' → ':'')+e.new_best+' (+'+e.improvement+')']));
  }
}

(async()=>{
  const jobs=[loadOverview(),loadTrends(),loadMalaysia(),loadAiLinks()];
  const settled=await Promise.allSettled(jobs);
  const failed=settled.find(r=>r.status==='rejected');
  if(failed){$('error').textContent='Some panels failed to load: '+failed.reason.message;$('error').hidden=false}
})();
</script>
</body>
</html>'''


@app.get("/jobmarket")
def futuretwin_jobmarket_page():
    return Response(JOBMARKET_HTML, mimetype="text/html")


@app.get("/api/jobmarket/overview")
def api_jobmarket_overview():
    from jobmarket_trends import get_overview
    try:
        return jsonify(get_overview())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/api/jobmarket/skill-trends")
def api_jobmarket_skill_trends():
    from jobmarket_trends import compute_skill_trends
    try:
        return jsonify(compute_skill_trends())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/api/jobmarket/malaysia")
def api_jobmarket_malaysia():
    from jobmarket_trends import compute_malaysia_indicators
    try:
        return jsonify(compute_malaysia_indicators())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/api/jobmarket/ai-links")
def api_jobmarket_ai_links():
    from jobmarket_trends import get_ai_cooccurrence
    try:
        limit = int(request.args.get("limit", "15"))
    except ValueError:
        return jsonify({"error": "limit must be an integer."}), 400
    if not 1 <= limit <= 100:
        return jsonify({"error": "limit must be between 1 and 100."}), 400
    try:
        return jsonify(get_ai_cooccurrence(limit=limit))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def main():
    from futuretwin_esco_fulltext_api import get_glossary
    # Warm up once before opening UI, so users know when the model is ready.
    get_glossary()
    print("FutureTwin dashboard is ready. Open the Replit web preview.", flush=True)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)


if __name__ == "__main__":
    main()
