"""Approachable career and skill map organised by the 17 Sustainable Development Goals."""
from __future__ import annotations

from futuretwin_pages import _page


SDG_MAP_CSS = r'''
.sm-page{max-width:1380px;margin:0 auto;padding:26px 24px 40px;color:var(--ink)}
.sm-head{max-width:760px;margin-bottom:16px}
.sm-head h1{font:700 clamp(26px,3.4vw,38px)/1.12 var(--body);letter-spacing:-.045em;margin:6px 0 8px}
.sm-intro{margin:0;font-size:16px;color:var(--ink2);line-height:1.5}
.sm-how{margin:6px 0 0;font-size:14px;color:var(--muted)}
.sm-bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
.sm-search-wrap{position:relative;flex:1 1 280px;min-width:200px;max-width:520px}
.sm-search{width:100%;height:44px;padding:0 14px 0 40px;border:1px solid var(--line);border-radius:12px;background:var(--paper);color:var(--ink);font:inherit;font-size:14px;box-shadow:var(--shadow)}
.sm-search:focus{outline:3px solid #8fb8d6;outline-offset:1px;border-color:var(--harbor)}
.sm-search-icon{position:absolute;left:15px;top:14px;width:13px;height:13px;border:2px solid var(--muted);border-radius:50%;pointer-events:none}
.sm-search-icon:after{content:"";position:absolute;width:6px;height:2px;background:var(--muted);right:-6px;bottom:-3px;transform:rotate(48deg)}
.sm-results{position:absolute;z-index:30;top:calc(100% + 6px);left:0;right:0;max-height:min(60vh,420px);overflow:auto;background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:0 16px 38px #14263a24;padding:6px}
.sm-results h4{font:700 11px var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:8px 8px 4px}
.sm-res{display:flex;align-items:center;gap:9px;width:100%;min-height:44px;border:0;background:transparent;text-align:left;border-radius:9px;padding:6px 9px;color:var(--ink);font-size:14px}
.sm-res:hover,.sm-res:focus-visible{background:var(--harbor-soft);outline-offset:-2px}
.sm-res small{display:block;color:var(--muted);font-size:12px}
.sm-sw{flex:0 0 auto;width:12px;height:12px;border-radius:50%;border:1.5px solid #14263a55}
.sm-seg{display:inline-flex;padding:3px;border:1px solid var(--line);background:var(--paper2);border-radius:12px}
.sm-seg button{border:0;background:transparent;color:var(--ink2);font:600 14px var(--body);min-height:38px;padding:0 15px;border-radius:9px;transition:background .15s,color .15s}
.sm-seg button:hover{background:#ece6d8}
.sm-seg button[aria-pressed=true]{background:var(--harbor);color:#fbf8f1}
.sm-reset{min-height:44px}
.sm-chips{display:flex;gap:7px;overflow-x:auto;padding:4px 2px 10px;margin-bottom:6px;scrollbar-width:thin}
.sm-chip{flex:0 0 auto;display:inline-flex;align-items:center;gap:7px;min-height:38px;padding:0 12px;border:1px solid var(--line);border-radius:99px;background:var(--paper);color:var(--ink2);font:600 13px var(--body);white-space:nowrap;transition:background .15s,border-color .15s,transform .15s}
.sm-chip:hover{border-color:#b9ad92;transform:translateY(-1px)}
.sm-chip[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:#fbf8f1}
.sm-chip .sm-sw{border-color:#fffdf8aa}
.sm-workspace{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:16px;align-items:start}
.sm-explorer{min-width:0;border-radius:18px;background:var(--paper);border:1px solid var(--line);box-shadow:var(--shadow);overflow:hidden}
.sm-canvas-shell{position:relative;height:min(72vh,720px);min-height:420px;background:#f1ecdf;overflow:hidden}
.sm-canvas{position:absolute;inset:0;width:100%;height:100%;touch-action:none;cursor:grab;display:block}
.sm-canvas.dragging{cursor:grabbing}
.sm-canvas.over{cursor:pointer}
.sm-canvas:focus-visible{outline:3px solid #8fb8d6;outline-offset:-3px;border-radius:0}
.sm-tooltip{position:absolute;z-index:3;pointer-events:none;max-width:260px;padding:8px 11px;border-radius:10px;background:var(--ink);color:#fbf8f1;font-size:13px;line-height:1.35;box-shadow:0 8px 22px #14263a40}
.sm-tooltip small{display:block;color:#c9d5df;font-size:11.5px;margin-top:2px}
.sm-zoom{position:absolute;right:12px;bottom:12px;z-index:2;display:flex;flex-direction:column;gap:2px;padding:4px;border:1px solid var(--line);border-radius:12px;background:#fffdf8ee}
.sm-zoom button{width:44px;height:44px;border:0;border-radius:9px;background:transparent;color:var(--ink);font:600 22px var(--body)}
.sm-zoom button:hover{background:var(--harbor-soft)}
.sm-map-hint{position:absolute;left:12px;bottom:12px;z-index:2;max-width:calc(100% - 90px);padding:6px 11px;border-radius:99px;background:#fffdf8ee;border:1px solid var(--line);color:var(--ink2);font-size:12px;pointer-events:none}
.sm-back{position:absolute;left:12px;top:12px;z-index:2}
.sm-state{position:absolute;inset:0;z-index:4;display:grid;place-content:center;justify-items:center;text-align:center;padding:24px;background:#f1ecdfef;color:var(--ink2);font-size:14px}
.sm-state strong{font-size:16px;color:var(--ink);display:block;margin-bottom:6px}
.sm-skel{position:absolute;inset:0;z-index:4;display:grid;grid-template-columns:repeat(5,1fr);gap:26px;padding:50px;background:#f1ecdf}
.sm-skel i{display:block;border-radius:50%;aspect-ratio:1;background:linear-gradient(90deg,#e7dfcc,#f3eddf,#e7dfcc);background-size:200% 100%;animation:sh 1.3s infinite linear}
.sm-legend{display:flex;gap:10px 20px;flex-wrap:wrap;padding:12px 16px;border-top:1px solid var(--line);font-size:12.5px;color:var(--ink2)}
.sm-legend b{font-weight:700;color:var(--ink)}
.sm-leg{display:inline-flex;align-items:center;gap:7px}
.sm-leg svg{width:18px;height:18px;flex:0 0 auto}
.sm-legend-note{flex-basis:100%;color:var(--muted)}
.sm-side{min-width:0;border:1px solid var(--line);border-radius:18px;background:var(--paper);box-shadow:var(--shadow);padding:18px;max-height:calc(min(72vh,720px) + 120px);overflow:auto;position:sticky;top:84px}
.sm-side:focus{outline:none}
.sm-side,#sm-related{scroll-margin-top:80px}
.sm-side h2{font:700 20px/1.25 var(--body);letter-spacing:-.025em;margin:0}
.sm-kicker{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin-bottom:7px}
.sm-tag{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:99px;background:var(--harbor-soft);color:var(--harbor);font-size:12px;font-weight:700}
.sm-tag.goal{background:var(--paper2);color:var(--ink);border:1px solid var(--line)}
.sm-desc{font-size:14px;color:var(--ink2);line-height:1.55;margin:10px 0 12px}
.sm-actions{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.sm-actions .btn{min-height:44px;justify-content:center;flex:1 1 auto}
.sm-sec{margin-top:18px;padding-top:15px;border-top:1px solid var(--line2)}
.sm-sec h3{font:700 15px var(--body);letter-spacing:-.01em;margin:0 0 4px}
.sm-sub{font-size:13px;color:var(--muted);margin:0 0 9px;line-height:1.5}
.sm-pass{border-radius:12px;padding:12px 13px;background:var(--sage-soft);font-size:13.5px;line-height:1.5;color:var(--ink)}
.sm-pass.warn{background:var(--amber-soft)}
.sm-pass.none{background:var(--paper2);border:1px solid var(--line)}
.sm-pass strong{display:block;font-size:14.5px;margin-bottom:3px}
.sm-meter{height:8px;border-radius:9px;background:#fffdf8;margin:8px 0;overflow:hidden;border:1px solid #c9dccf}
.sm-meter i{display:block;height:100%;background:var(--sage);transform-origin:left;transition:transform .5s}
.sm-skills{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:6px}
.sm-skill{display:inline-flex;align-items:center;gap:5px;padding:5px 10px;border:1px solid var(--line);border-radius:99px;background:var(--paper);font-size:12.5px;color:var(--ink2)}
.sm-skill.have{border-color:#9cc3ae;background:var(--sage-soft);color:var(--ink);font-weight:600}
.sm-skill.have:before{content:"";width:5px;height:9px;border:solid var(--sage);border-width:0 2px 2px 0;transform:rotate(40deg) translateY(-1px)}
.sm-list{list-style:none;margin:8px 0 0;padding:0;display:grid;gap:6px}
.sm-row{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:11px;padding:6px 6px 6px 11px;background:var(--paper);font-size:13.5px}
.sm-row>span{flex:1;min-width:0;overflow-wrap:anywhere}
.sm-row small{display:block;color:var(--muted);font-size:11.5px}
.sm-mini{flex:0 0 auto;min-height:36px;min-width:36px;padding:0 11px;border:1px solid var(--line);border-radius:9px;background:var(--paper2);color:var(--harbor);font:600 12.5px var(--body);text-decoration:none;display:inline-flex;align-items:center;justify-content:center}
.sm-mini:hover{border-color:var(--harbor);background:var(--harbor-soft)}
.sm-input{width:100%;height:42px;border:1px solid var(--line);border-radius:10px;padding:0 12px;background:#fffefa;font:inherit;font-size:14px;color:var(--ink);margin-top:6px}
.sm-group{margin-top:12px}
.sm-group h4{display:flex;align-items:center;gap:8px;font:700 13.5px/1.3 var(--body);margin:0 0 6px}
.sm-conn{border:1px solid var(--line);border-left:4px solid var(--harbor);border-radius:11px;padding:11px 12px;margin-top:7px;background:var(--paper);font-size:13.5px;line-height:1.5}
.sm-conn.desk{border-left-color:var(--amber)}
.sm-conn.ai{border-left-color:#a69a82;border-style:dashed;border-left-style:solid;background:var(--paper2)}
.sm-conn.human{border-left-color:var(--sage)}
.sm-conn strong{display:block;color:var(--ink);font-weight:650}
.sm-status{display:inline-flex;align-items:center;gap:6px;margin:6px 0 4px;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;background:var(--harbor-soft);color:var(--harbor)}
.sm-status.human{background:var(--sage-soft);color:#215e49}
.sm-status.desk{background:var(--amber-soft);color:#7d4e0e}
.sm-status.ai{background:#eeeae0;color:#5b5444}
.sm-why{margin:6px 0 0;color:var(--ink2)}
.sm-why b{color:var(--ink)}
.sm-more{margin-top:16px;border-top:1px dashed var(--line);padding-top:10px}
.sm-more summary,.sm-fold summary{cursor:pointer;font-size:13.5px;font-weight:700;color:var(--harbor);min-height:36px;display:flex;align-items:center}
.sm-fold{margin-top:8px}
.sm-fine{font-size:12.5px;color:var(--ink2);line-height:1.55;border-bottom:1px solid var(--line2);padding:9px 0}
.sm-fine:last-child{border-bottom:0}
.sm-fine blockquote{margin:5px 0;padding-left:9px;border-left:2px solid var(--line)}
.sm-note{margin:14px 0 0;padding:10px 12px;border-radius:10px;background:var(--paper2);border:1px solid var(--line2);color:var(--muted);font-size:12.5px;line-height:1.5}
.sm-steps{margin:10px 0;padding-left:20px;font-size:14px;color:var(--ink2);line-height:1.7}
.sm-err{border-radius:12px;background:var(--clay-soft);border:1px solid #ecc9c0;color:var(--clay);padding:12px 14px;font-size:13.5px;margin-top:10px}
.sm-err button{margin-top:8px}
.sm-skelline{height:14px;border-radius:7px;margin:10px 0;background:linear-gradient(90deg,#ece6d8,#f5f0e4,#ece6d8);background-size:200% 100%;animation:sh 1.3s infinite linear}
.sm-empty{font-size:13.5px;color:var(--muted);padding:6px 0}
.sm-browse{margin-top:16px;border:1px solid var(--line);border-radius:18px;background:var(--paper);box-shadow:var(--shadow);padding:16px 18px}
.sm-browse h2{font:700 18px var(--body);letter-spacing:-.02em;margin:0 0 3px}
.sm-blist{list-style:none;margin:12px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:7px}
.sm-bitem{display:flex;align-items:center;gap:9px;width:100%;min-height:46px;text-align:left;border:1px solid var(--line);border-radius:11px;background:var(--paper);padding:6px 11px;color:var(--ink);font-size:13.5px;transition:border-color .15s,background .15s}
.sm-bitem:hover{border-color:var(--harbor);background:var(--harbor-soft)}
.sm-bitem small{display:block;color:var(--muted);font-size:11.5px}
.sm-bitem[aria-current=true]{border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.sm-about{margin-top:14px;font-size:13px;color:var(--muted);line-height:1.6}
.sm-about summary{cursor:pointer;font-weight:700;color:var(--harbor);min-height:36px;display:flex;align-items:center}
.sm-metrics{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:8px 0}
.sm-metric{padding:9px 12px;background:var(--paper);border:1px solid var(--line);border-radius:10px}
.sm-metric b{display:block;color:var(--ink);font-size:16px}
.sm-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}
@media(max-width:1060px){.sm-workspace{grid-template-columns:1fr}.sm-side{position:static;max-height:none}.sm-canvas-shell{height:62vh}}
@media(max-width:600px){.sm-page{padding:16px 12px 30px}.sm-canvas-shell{min-height:740px;height:min(105vh,820px)}.sm-seg{flex:1}.sm-seg button{flex:1;padding:0 6px}.sm-reset{flex:1;justify-content:center}.sm-map-hint{display:none}.sm-blist{grid-template-columns:1fr}.sm-side{padding:15px}}
@media(prefers-reduced-motion:reduce){.sm-page *{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
'''


SDG_MAP_BODY = r'''
<main class="sm-page" id="sdg-map-page">
  <header class="sm-head">
    <div class="eyebrow">SDG Map</div>
    <h1>Careers, skills and the global goals</h1>
    <p class="sm-intro">Explore how careers and skills connect to the 17 Sustainable Development Goals.</p>
    <p class="sm-how">Click a dot to discover a career or skill and its connection to an SDG.</p>
  </header>
  <div class="sm-bar">
    <div class="sm-search-wrap">
      <span class="sm-search-icon" aria-hidden="true"></span>
      <input class="sm-search" id="sm-search" type="search" maxlength="100" autocomplete="off" placeholder="Search careers, skills or goals" aria-label="Search careers, skills and Sustainable Development Goals" aria-controls="sm-results" aria-expanded="false">
      <div class="sm-results" id="sm-results" role="region" aria-label="Search results" hidden></div>
    </div>
    <div class="sm-seg" role="group" aria-label="Show on the map">
      <button type="button" data-kind="both" aria-pressed="true">All</button><button type="button" data-kind="occupation" aria-pressed="false">Careers</button><button type="button" data-kind="skill" aria-pressed="false">Skills</button>
    </div>
    <button type="button" class="btn btn-ghost sm-reset" id="sm-reset">Reset View</button>
  </div>
  <div class="sm-chips" id="sm-chips" role="group" aria-label="Filter by Sustainable Development Goal"></div>
  <div class="sm-workspace">
    <section class="sm-explorer" aria-label="Map of careers and skills grouped by Sustainable Development Goal">
      <div class="sm-canvas-shell" id="sm-shell">
        <canvas class="sm-canvas" id="sm-canvas" tabindex="0" role="application" aria-label="Map of careers and skills in 17 goal clusters. Arrow keys pan, plus and minus zoom. A full keyboard list of the same items follows the map."></canvas>
        <div class="sm-tooltip" id="sm-tooltip" hidden></div>
        <button type="button" class="btn btn-primary btn-sm sm-back" id="sm-back" hidden>&larr; Back to all 17 goals</button>
        <div class="sm-map-hint" id="sm-hint">Drag to move. Scroll or pinch to zoom.</div>
        <div class="sm-zoom" role="group" aria-label="Zoom controls"><button type="button" id="sm-zin" aria-label="Zoom in">+</button><button type="button" id="sm-zout" aria-label="Zoom out">&minus;</button></div>
        <div class="sm-skel" id="sm-skel" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <div class="sm-state" id="sm-state" hidden></div>
      </div>
      <div class="sm-legend" aria-label="Map legend">
        <span class="sm-leg"><b>Colour</b> = the goal cluster</span>
        <span class="sm-leg"><svg viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="6" fill="#4C9F38" stroke="#14263a" stroke-width="1.2"/></svg>Career</span>
        <span class="sm-leg"><svg viewBox="0 0 18 18" aria-hidden="true"><path d="M9 2.5 15.5 9 9 15.5 2.5 9Z" fill="#4C9F38" stroke="#14263a" stroke-width="1.2"/></svg>Skill</span>
        <span class="sm-leg"><svg viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="5.5" fill="#4C9F38" stroke="#14263a" stroke-width="1.2"/><circle cx="9" cy="9" r="7.8" fill="none" stroke="#14263a" stroke-width="1"/></svg>Approved by an independent person</span>
        <span class="sm-leg"><svg viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="6" fill="#fffdf8" stroke="#4C9F38" stroke-width="2.4"/></svg>Sources checked by an AI assistant</span>
        <span class="sm-leg"><svg viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="6" fill="#4C9F3855" stroke="#2c5f20" stroke-width="1.5" stroke-dasharray="2.2 2"/></svg>AI suggestion, not verified</span>
        <span class="sm-legend-note">Select a dot to see recorded career–skill connections as lines. Positions and distances are for browsing, not measures of impact.</span>
      </div>
    </section>
    <aside class="sm-side" id="sm-side" tabindex="-1" aria-label="Details" aria-live="polite">
      <div id="sm-panel"></div>
    </aside>
  </div>
  <section class="sm-browse" aria-labelledby="sm-browse-title">
    <h2 id="sm-browse-title">Browse as a list</h2>
    <p class="sm-sub" id="sm-browse-sub">Everything shown on the map, in a keyboard-friendly list.</p>
    <ul class="sm-blist" id="sm-blist"></ul>
    <div class="sm-actions"><button type="button" class="btn btn-ghost btn-sm" id="sm-bmore" hidden>Show more</button></div>
    <details class="sm-about"><summary>About this map</summary>
      <div class="sm-metrics" id="sm-metrics"></div>
      <p id="sm-foot"></p>
    </details>
  </section>
</main>
'''


SDG_MAP_JS = r'''
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeHttps=v=>{try{if(typeof v!=='string'||!/^https:\/\//i.test(v.trim()))return'';const u=new URL(v.trim());return u.protocol==='https:'?u.href:''}catch(_e){return''}};
const req=async(url,opt)=>{const r=await fetch(url,Object.assign({headers:{Accept:'application/json'},credentials:'same-origin'},opt||{}));let d={};try{d=await r.json()}catch(_e){}if(!r.ok)throw new Error(d.error||'Something went wrong. Please try again.');return d};
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const NAMES=['No Poverty','Zero Hunger','Good Health and Well-being','Quality Education','Gender Equality','Clean Water and Sanitation','Affordable and Clean Energy','Decent Work and Economic Growth','Industry, Innovation and Infrastructure','Reduced Inequalities','Sustainable Cities and Communities','Responsible Consumption and Production','Climate Action','Life Below Water','Life on Land','Peace, Justice and Strong Institutions','Partnerships for the Goals'];
const COLORS=['#E5243B','#DDA63A','#4C9F38','#C5192D','#FF3A21','#26BDE2','#FCC30B','#A21942','#FD6925','#DD1367','#FD9D24','#BF8B2E','#3F7E44','#0A97D9','#56C02B','#00689D','#19486A'];
const STATUS={
 independently_human_approved:{cls:'human',label:'Approved by an independent person',text:'A person who is independent of the assistant checked the sources and approved this link.'},
 assistant_desk_reviewed:{cls:'desk',label:'Sources checked by an AI assistant',text:'An AI assistant checked the sources. This is not approval by an independent person.'},
 unreviewed_candidate:{cls:'ai',label:'AI suggestion, not verified',text:'Suggested by a text-matching AI model. Nobody has verified that this is a real contribution.'}};
const RANK={independently_human_approved:0,assistant_desk_reviewed:1,unreviewed_candidate:2};
const BROWSE_PAGE_SIZE=12;
const S={goals:[],nodes:[],byId:new Map(),statusesByGoal:new Map(),clusters:{},kind:'both',goal:'',sel:null,view:{k:1,tx:0,ty:0},fitK:1,W:1,H:1,hover:null,vis:[],pts:[],tok:0,snapshot:null,blimit:BROWSE_PAGE_SIZE,pointers:new Map(),anim:0,raf:0};
let passportP=null;
const goalOf=n=>String(n.primary_goal_code||(n.goal_codes||[])[0]||'');
const hasGoal=(n,code)=>(n.goal_codes||[]).map(String).includes(String(code));
const displayGoal=n=>S.goal&&hasGoal(n,S.goal)?S.goal:goalOf(n);
const gInfo=c=>S.goals.find(g=>g.code===String(c))||{code:String(c),title:NAMES[Number(c)-1]||'',color:COLORS[Number(c)-1]||'#8997a4'};
const gName=c=>gInfo(c).title||NAMES[Number(c)-1]||'';
const gCol=c=>{const x=gInfo(c).color;return /^#[0-9a-f]{6}$/i.test(x||'')?x:(COLORS[Number(c)-1]||'#8997a4')};
const dark=hex=>{const n=parseInt(hex.slice(1),16),f=.55;return'rgb('+[(n>>16)&255,(n>>8)&255,n&255].map(v=>Math.round(v*f)).join(',')+')'};
const bestStatus=n=>{const st=S.goal?(S.statusesByGoal.get(S.goal+'|'+n.id)||[]):n.review_statuses||[];return st.slice().sort((a,b)=>(RANK[a]??9)-(RANK[b]??9))[0]||''};
const stInfo=s=>STATUS[s]||{cls:'',label:String(s||'Review status not recorded').replaceAll('_',' '),text:'Review status as recorded: '+s};
const typeName=t=>t==='occupation'?'Career':'Skill';

/* ---------- layout: UI-only cluster placement, preserves snapshot x/y inside each cluster ---------- */
function layout(){
 const CW=340,CH=360,rows=S.W<600?[3,3,3,3,3,2]:[5,4,4,4];S.clusters={};
 const groups={};for(let i=1;i<=17;i++)groups[i]=[];
 S.nodes.forEach(n=>{const g=displayGoal(n);if(groups[g])groups[g].push(n)});
 let code=1;
 rows.forEach((cnt,ri)=>{for(let ci=0;ci<cnt;ci++,code++){
   const cx=(ci-(cnt-1)/2)*CW,cy=(ri-(rows.length-1)/2)*CH;
  const list=groups[code],r=Math.max(52,Math.min(135,4.2*Math.sqrt(list.length)+30));
  S.clusters[code]={code:String(code),cx,cy,r,n:list.length};
  if(!list.length)continue;
  const xs=list.map(n=>+n.x),ys=list.map(n=>+n.y),x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
  const sp=Math.max(x1-x0,y1-y0,1e-6),mx=(x0+x1)/2,my=(y0+y1)/2,used=new Set(),cell=6.5;
  list.slice().sort((a,b)=>a.id<b.id?-1:1).forEach(n=>{
   let u=(+n.x-mx)/sp*2,v=(+n.y-my)/sp*2;const l=Math.hypot(u,v);if(l>1){u/=l;v/=l}
   let px=cx+u*r*.92,py=cy+v*r*.92,gx=Math.round(px/cell),gy=Math.round(py/cell),placed=false;
   for(let ring=0;ring<9&&!placed;ring++){for(let dx=-ring;dx<=ring&&!placed;dx++)for(let dy=-ring;dy<=ring;dy++){if(Math.max(Math.abs(dx),Math.abs(dy))!==ring)continue;const key=(gx+dx)+','+(gy+dy);if(!used.has(key)){used.add(key);px=(gx+dx)*cell;py=(gy+dy)*cell;placed=true;break}}}
   n._x=px;n._y=py});
 }});
}
function resize(){const c=$('sm-canvas'),r=c.getBoundingClientRect();S.W=Math.max(1,r.width);S.H=Math.max(1,r.height);const d=devicePixelRatio||1;if(c.width!==Math.round(S.W*d)||c.height!==Math.round(S.H*d)){c.width=Math.round(S.W*d);c.height=Math.round(S.H*d)}}
function rectView(x0,y0,x1,y1,pad){const k=Math.min((S.W-pad*2)/(x1-x0),(S.H-pad*2)/(y1-y0));return{k,tx:S.W/2-k*(x0+x1)/2,ty:S.H/2-k*(y0+y1)/2}}
function fullView(){const clusters=Object.values(S.clusters);if(!clusters.length)return{k:1,tx:S.W/2,ty:S.H/2};return rectView(Math.min(...clusters.map(c=>c.cx))-170,Math.min(...clusters.map(c=>c.cy))-280,Math.max(...clusters.map(c=>c.cx))+170,Math.max(...clusters.map(c=>c.cy))+140,14)}
function goalView(code){const c=S.clusters[code];return rectView(c.cx-c.r-40,c.cy-c.r-52,c.cx+c.r+40,c.cy+c.r+36,10)}
function go(target,instant){cancelAnimationFrame(S.anim);if(reduce||instant){S.view=target;queue();return}
 const a={...S.view},t0=performance.now(),D=380;
 const step=t=>{const p=Math.min(1,(t-t0)/D),e=1-Math.pow(1-p,3);S.view={k:a.k+(target.k-a.k)*e,tx:a.tx+(target.tx-a.tx)*e,ty:a.ty+(target.ty-a.ty)*e};draw();if(p<1)S.anim=requestAnimationFrame(step)};S.anim=requestAnimationFrame(step)}
function queue(){if(S.raf)return;S.raf=requestAnimationFrame(()=>{S.raf=0;draw()})}
const sx=x=>x*S.view.k+S.view.tx,sy=y=>y*S.view.k+S.view.ty;
function isVis(n){return n._x!=null&&(S.kind==='both'||n.type===S.kind)&&(!S.goal||hasGoal(n,S.goal))}
function recompute(){S.vis=S.nodes.filter(isVis)}
function shape(c,x,y,r,t){c.beginPath();if(t==='skill'){const q=r*1.25;c.moveTo(x,y-q);c.lineTo(x+q,y);c.lineTo(x,y+q);c.lineTo(x-q,y);c.closePath()}else c.arc(x,y,r,0,7)}
function wrap(c,text,maxW){const w=text.split(' '),lines=[];let cur='';w.forEach(t=>{const tt=cur?cur+' '+t:t;if(c.measureText(tt).width>maxW&&cur){lines.push(cur);cur=t}else cur=tt});if(cur)lines.push(cur);return lines}
function draw(){
 const cv=$('sm-canvas'),c=cv.getContext('2d');if(!c)return;resize();const d=devicePixelRatio||1;c.setTransform(d,0,0,d,0,0);c.clearRect(0,0,S.W,S.H);
 const k=S.view.k,counts={};S.vis.forEach(n=>{const g=displayGoal(n);counts[g]=counts[g]||{o:0,s:0};counts[g][n.type==='occupation'?'o':'s']++});
 /* cluster fields and labels */
 Object.values(S.clusters).forEach(cl=>{
  const x=sx(cl.cx),y=sy(cl.cy),r=cl.r*k,col=gCol(cl.code),off=S.goal&&S.goal!==cl.code;
  if(x+r<-200||x-r>S.W+200||y+r<-120||y-r>S.H+120)return;
  c.save();c.globalAlpha=off?.35:1;
  c.beginPath();c.arc(x,y,r+8*k,0,7);c.fillStyle=col+'1f';c.fill();c.lineWidth=1.5;c.strokeStyle=col+(cl.n?'88':'66');if(!cl.n)c.setLineDash([4,4]);c.stroke();c.setLineDash([]);
   const fs=Math.max(10,Math.min(16,340*k/14)),ls=fs*1.22;
  c.font='700 '+fs+'px "Plus Jakarta Sans",system-ui,sans-serif';
   const lines=wrap(c,'SDG '+cl.code+' · '+gName(cl.code),Math.max(64,Math.min(260,340*k-18))),top=y-r-10-lines.length*ls-13;
   c.textAlign='center';c.textBaseline='top';c.fillStyle='#14263a';
   lines.forEach((t,i)=>c.fillText(t,x,top+i*ls));
  const cnt=counts[cl.code],sub=cl.n?(cnt?(cnt.o+' careers, '+cnt.s+' skills'):'Hidden by filter'):'No mapped careers or skills yet';
   c.font='500 '+Math.max(9,fs-2)+'px "Plus Jakarta Sans",system-ui,sans-serif';c.fillStyle='#66778a';c.fillText(sub,x,top+lines.length*ls);
  c.restore()});
  /* Only selected, stored ESCO career–skill pairs are connected; lines do not
     assert that an SDG contribution has been verified. */
  if(S.sel&&S.snapshot){
   const visible=new Set(S.vis.map(n=>n.id)),seen=new Set();
   (S.snapshot.links||[]).forEach(link=>{
    if(S.goal&&String(link.goal_code)!==S.goal)return;
    const occupationId='occupation:'+link.occupation_uri,skillId='skill:'+link.skill_uri;
    const other=S.sel.id===occupationId?skillId:S.sel.id===skillId?occupationId:null;
    if(!other||!visible.has(other)||seen.has(other))return;
    const n=S.byId.get(other);if(!n)return;seen.add(other);
    c.beginPath();c.moveTo(sx(S.sel._x),sy(S.sel._y));c.lineTo(sx(n._x),sy(n._y));
    c.strokeStyle='#315c7a55';c.lineWidth=1.2;c.stroke();
   });
  }
  /* dots */
 const base=Math.max(3.2,Math.min(8,3*Math.pow(k/S.fitK,.55)));S.pts=[];
 S.vis.forEach(n=>{
  const x=sx(n._x),y=sy(n._y);if(x<-20||y<-20||x>S.W+20||y>S.H+20)return;S.pts.push({n,x,y});
   const col=gCol(displayGoal(n)),dk=dark(col),st=bestStatus(n),r=base*(n.type==='occupation'?1:.9);
  shape(c,x,y,r,n.type);
  if(st==='unreviewed_candidate'||!st){c.fillStyle=col+'55';c.fill();c.setLineDash([2.2,1.8]);c.lineWidth=1.5;c.strokeStyle=dk;c.stroke();c.setLineDash([])}
  else if(st==='assistant_desk_reviewed'){c.fillStyle='#fffdf8';c.fill();c.lineWidth=2.4;c.strokeStyle=col;c.stroke();c.lineWidth=.8;c.strokeStyle=dk;c.stroke()}
  else{c.fillStyle=col;c.fill();c.lineWidth=1.2;c.strokeStyle=dk;c.stroke();shape(c,x,y,r+3,n.type);c.lineWidth=1.2;c.strokeStyle='#14263a';c.stroke()}
  const hv=S.hover&&S.hover.id===n.id,sl=S.sel&&S.sel.id===n.id;
  if(hv||sl){shape(c,x,y,r+(sl?7:5),n.type);c.lineWidth=sl?2.5:2;c.strokeStyle=sl?'#14263a':'#1c4a6e';c.stroke()}
 });
 if(S.sel&&S.sel._x!=null&&isVis(S.sel)&&k>S.fitK*1.6){const x=sx(S.sel._x),y=sy(S.sel._y);c.font='700 13px "Plus Jakarta Sans",system-ui,sans-serif';c.textAlign='left';c.textBaseline='middle';const t=S.sel.label,w=c.measureText(t).width;c.fillStyle='#14263a';c.fillRect(x+13,y-13,w+14,26);c.fillStyle='#fbf8f1';c.fillText(t,x+20,y)}
 $('sm-canvas').dataset.points=String(S.pts.length);
}
function nodeAt(px,py,touch){let best=null,bd=1e9;const R=touch?20:13;for(const p of S.pts){const d=Math.hypot(px-p.x,py-p.y);if(d<R&&d<bd){best=p.n;bd=d}}return best}
function clusterAt(px,py){const wx=(px-S.view.tx)/S.view.k,wy=(py-S.view.ty)/S.view.k;for(const cl of Object.values(S.clusters)){if(Math.hypot(wx-cl.cx,wy-cl.cy)<cl.r+8)return cl}return null}
function zoomAt(f,px,py){const v=S.view,nk=Math.max(S.fitK*.85,Math.min(S.fitK*18,v.k*f)),r=nk/v.k;px=px==null?S.W/2:px;py=py==null?S.H/2:py;S.view={k:nk,tx:px-(px-v.tx)*r,ty:py-(py-v.ty)*r};queue()}

/* ---------- canvas input ---------- */
function bindCanvas(){
 const cv=$('sm-canvas'),tip=$('sm-tooltip');let drag=null,pinch=0;
 const pt=e=>{const r=cv.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top}};
 cv.addEventListener('pointerdown',e=>{cancelAnimationFrame(S.anim);const p=pt(e);S.pointers.set(e.pointerId,p);cv.setPointerCapture(e.pointerId);
  if(S.pointers.size===2){const [a,b]=[...S.pointers.values()];pinch=Math.hypot(a.x-b.x,a.y-b.y);drag=null}
  else drag={x:p.x,y:p.y,tx:S.view.tx,ty:S.view.ty,moved:false,touch:e.pointerType!=='mouse'}});
 cv.addEventListener('pointermove',e=>{const p=pt(e);
  if(S.pointers.has(e.pointerId))S.pointers.set(e.pointerId,p);
  if(S.pointers.size===2){const [a,b]=[...S.pointers.values()],d=Math.hypot(a.x-b.x,a.y-b.y);if(pinch)zoomAt(d/pinch,(a.x+b.x)/2,(a.y+b.y)/2);pinch=d;return}
  if(drag){const dx=p.x-drag.x,dy=p.y-drag.y;if(Math.hypot(dx,dy)>5)drag.moved=true;if(drag.moved){cv.classList.add('dragging');tip.hidden=true;S.view={...S.view,tx:drag.tx+dx,ty:drag.ty+dy};queue()}return}
  if(e.pointerType!=='mouse')return;
  const n=nodeAt(p.x,p.y,false);if((S.hover&&S.hover.id)!==(n&&n.id)){S.hover=n;queue()}
  cv.classList.toggle('over',!!n);
   if(n){const st=stInfo(bestStatus(n)).label;tip.innerHTML=esc(n.label)+'<small>'+typeName(n.type)+' · SDG '+esc(displayGoal(n))+' '+esc(gName(displayGoal(n)))+' · '+esc(st)+'</small>';tip.hidden=false;tip.style.left=Math.max(6,Math.min(p.x+14,S.W-270))+'px';tip.style.top=Math.max(6,Math.min(p.y+14,S.H-80))+'px'}
  else tip.hidden=true});
 const end=e=>{const p=pt(e);S.pointers.delete(e.pointerId);if(S.pointers.size<2)pinch=0;
  if(drag&&e.type==='pointerup'){const d=drag;drag=null;cv.classList.remove('dragging');
   if(!d.moved){const n=nodeAt(p.x,p.y,d.touch);if(n)selectNode(n,false);else{const cl=clusterAt(p.x,p.y);if(cl)setGoal(cl.code)}}}
  else{drag=null;cv.classList.remove('dragging')}};
 cv.addEventListener('pointerup',end);cv.addEventListener('pointercancel',end);
 cv.addEventListener('pointerleave',()=>{tip.hidden=true;if(S.hover){S.hover=null;queue()}});
 cv.addEventListener('wheel',e=>{e.preventDefault();const p=pt(e);zoomAt(e.deltaY<0?1.15:.87,p.x,p.y)},{passive:false});
 cv.addEventListener('keydown',e=>{const m=60;const v=S.view;
  if(e.key==='ArrowLeft')S.view={...v,tx:v.tx+m};else if(e.key==='ArrowRight')S.view={...v,tx:v.tx-m};else if(e.key==='ArrowUp')S.view={...v,ty:v.ty+m};else if(e.key==='ArrowDown')S.view={...v,ty:v.ty-m};
  else if(e.key==='+'||e.key==='=')zoomAt(1.25);else if(e.key==='-')zoomAt(.8);else if(e.key==='Escape'){clearSel();return}else return;e.preventDefault();queue()});
 new ResizeObserver(()=>{if(!S.nodes.length)return;resize();layout();recompute();S.fitK=fullView().k;if(!S.sel)S.view=S.goal?goalView(S.goal):fullView();else{const k=S.fitK*3.2;S.view={k,tx:S.W/2-k*S.sel._x,ty:S.H/2-k*S.sel._y}}queue()}).observe($('sm-shell'));
}

/* ---------- state changes ---------- */
function syncChips(){document.querySelectorAll('[data-goal-chip]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.goalChip===S.goal)));$('sm-back').hidden=!S.goal;document.querySelectorAll('[data-kind]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.kind===S.kind)))}
function setGoal(code,keepSel){S.goal=String(code||'');if(!keepSel){S.sel=null;S.tok++}layout();recompute();syncChips();renderBrowse(true);
 if(S.goal)go(goalView(S.goal));else go(fullView());
 queue();if(!keepSel)renderPanel()}
function setKind(k){S.kind=k;if(S.sel&&!isVis(S.sel)){S.sel=null;S.tok++}recompute();syncChips();renderBrowse(true);queue();if(!S.sel)renderPanel()}
function resetAll(){S.kind='both';S.goal='';S.sel=null;S.tok++;$('sm-search').value='';closeResults();layout();recompute();syncChips();renderBrowse(true);go(fullView());renderPanel();queue()}
function clearSel(){S.sel=null;S.tok++;renderPanel();renderBrowse(false);queue()}
function revealPanel(){
 if(!matchMedia('(max-width:1060px)').matches)return;
 requestAnimationFrame(()=>{const side=$('sm-side');side.focus({preventScroll:true});
  // Explicit document scrolling avoids a smooth scroll being cancelled by
  // asynchronous panel replacement or a focus change in the search results.
  window.scrollTo({top:Math.max(0,window.scrollY+side.getBoundingClientRect().top-80),behavior:'instant'});
 });
}
function selectNode(n,focus){
 if(S.goal&&!hasGoal(n,S.goal)){S.goal='';layout()}
 if((S.kind!=='both'&&n.type!==S.kind)){S.kind='both'}
 S.sel=n;recompute();syncChips();
 if(focus){const t=Math.max(S.view.k,S.fitK*3.2);go({k:t,tx:S.W/2-t*n._x,ty:S.H/2-t*n._y})}
 queue();renderBrowse(false);loadEntity(n);
 revealPanel();
}

/* ---------- search ---------- */
function closeResults(){$('sm-results').hidden=true;$('sm-search').setAttribute('aria-expanded','false')}
function runSearch(){
 const q=$('sm-search').value.trim().toLocaleLowerCase(),box=$('sm-results');if(!q){closeResults();return}
 const goals=S.goals.filter(g=>('sdg '+g.code+' '+(g.title||'')).toLocaleLowerCase().includes(q)||('goal '+g.code)===q||String(g.code)===q).slice(0,5);
 const occ=[],sk=[];for(const n of S.nodes){if(n._x==null||!String(n.label).toLocaleLowerCase().includes(q))continue;(n.type==='occupation'?occ:sk).push(n);if(occ.length>40&&sk.length>40)break}
 const rank=(a,b)=>{const A=a.label.toLocaleLowerCase().startsWith(q)?0:1,B=b.label.toLocaleLowerCase().startsWith(q)?0:1;return A-B||a.label.localeCompare(b.label)};
 occ.sort(rank);sk.sort(rank);
 const row=n=>'<button type="button" class="sm-res" data-pick="'+esc(n.id)+'"><i class="sm-sw" style="background:'+gCol(goalOf(n))+'"></i><span>'+esc(n.label)+'<small>SDG '+esc(goalOf(n))+' '+esc(gName(goalOf(n)))+'</small></span></button>';
 let h='';
 if(goals.length)h+='<h4>Goals</h4>'+goals.map(g=>'<button type="button" class="sm-res" data-pick-goal="'+esc(g.code)+'"><i class="sm-sw" style="background:'+gCol(g.code)+'"></i><span>SDG '+esc(g.code)+': '+esc(g.title)+'<small>Show this cluster</small></span></button>').join('');
 if(occ.length)h+='<h4>Careers</h4>'+occ.slice(0,7).map(row).join('');
 if(sk.length)h+='<h4>Skills</h4>'+sk.slice(0,7).map(row).join('');
 if(!h)h='<p class="sm-empty" style="padding:10px 12px">No careers, skills or goals match "'+esc($('sm-search').value.trim())+'". Try a shorter word.</p>';
 box.innerHTML=h;box.hidden=false;$('sm-search').setAttribute('aria-expanded','true')}

/* ---------- panel ---------- */
const WELCOME=()=>'<div class="sm-kicker"><span class="sm-tag">How it works</span></div><h2>Find work that matters to you</h2><ol class="sm-steps"><li>Pick a goal you care about from the colour chips.</li><li>Click a career or skill dot, or choose from the list.</li><li>See why it connects, and how it compares with your Skills Passport.</li><li>Open the full career page when you are ready.</li></ol><p class="sm-note">Every link here is labelled by how well it has been checked. A link is never proof that a job makes a real-world difference.</p>';
function renderPanel(){
 const p=$('sm-panel');
 if(S.sel)return;
 if(!S.goal){p.innerHTML=WELCOME();return}
 const g=gInfo(S.goal),cl=S.clusters[S.goal],occ=S.vis.filter(n=>n.type==='occupation').sort((a,b)=>a.label.localeCompare(b.label)),sk=S.vis.filter(n=>n.type==='skill');
 const items=l=>l.slice(0,12).map(n=>'<li class="sm-row"><span>'+esc(n.label)+'<small>'+esc(stInfo(bestStatus(n)).label)+'</small></span><button type="button" class="sm-mini" data-act="pick" data-id="'+esc(n.id)+'">View</button></li>').join('');
 p.innerHTML='<div class="sm-kicker"><span class="sm-tag goal"><i class="sm-sw" style="background:'+gCol(S.goal)+'"></i>SDG '+esc(g.code)+'</span></div><h2>'+esc(g.title)+'</h2>'
 +(cl.n?'<p class="sm-desc">'+occ.length.toLocaleString()+' careers and '+sk.length.toLocaleString()+' skills have a recorded link to this goal. Links may be reviewed or only suggested by AI. The UN lists '+esc(g.target_count||'several')+' targets under this goal.</p>':'<p class="sm-desc">Nothing is mapped to this goal yet. That means no link has been recorded, not that no work contributes to it.</p>')
 +'<div class="sm-actions"><button type="button" class="btn btn-ghost btn-sm" data-act="all">Back to all 17 goals</button></div>'
 +(occ.length?'<section class="sm-sec"><h3>Careers in this goal</h3><ul class="sm-list">'+items(occ)+'</ul>'+(occ.length>12?'<p class="sm-sub" style="margin-top:8px">Showing 12 of '+occ.length+'. Use the list below the map for the rest.</p>':'')+'</section>':'')
 +(sk.length&&S.kind!=='occupation'?'<section class="sm-sec"><h3>Skills in this goal</h3><ul class="sm-list">'+items(sk)+'</ul></section>':'')
 +'<p class="sm-note">Clusters organise the map for browsing. They do not show how much any career contributes.</p>'}
function loadEntity(n){
 const tok=++S.tok,p=$('sm-panel');
 $('sm-side').scrollTop=0;
 p.innerHTML='<div class="sm-kicker"><span class="sm-tag">'+typeName(n.type)+'</span></div><h2>'+esc(n.label)+'</h2><div class="sm-skelline" style="width:90%"></div><div class="sm-skelline" style="width:75%"></div><div class="sm-skelline" style="width:84%"></div><p class="sm-sub">Loading details...</p>';
 req('/api/sdg/map/entity?type='+encodeURIComponent(n.type)+'&uri='+encodeURIComponent(n.uri)).then(d=>{if(tok!==S.tok)return;renderEntity(d,n,tok);revealPanel()}).catch(e=>{if(tok!==S.tok)return;p.innerHTML='<h2>'+esc(n.label)+'</h2><div class="sm-err" role="alert">'+esc(e.message)+'<br><button type="button" class="btn btn-ghost btn-sm" data-act="retry-entity">Try again</button></div><div class="sm-actions"><button type="button" class="btn btn-ghost btn-sm" data-act="close">Close</button></div>';revealPanel()})
}
function connCard(c){
 const si=stInfo(c.review_status),cand=c.review_status==='unreviewed_candidate',tu=safeHttps(c.target_uri),title=(c.target_code?c.target_code+' ':'')+(c.target_title||'');
 const ev=Array.isArray(c.evidence)?c.evidence.length:0;
 return '<article class="sm-conn '+si.cls+'"><strong>'+(tu?'<a href="'+esc(tu)+'" target="_blank" rel="noopener noreferrer">'+esc(title)+'</a>':esc(title))+'</strong><span class="sm-status '+si.cls+'">'+esc(si.label)+'</span><div class="sm-sub" style="margin:0">'+esc(si.text)+'</div>'
 +(c.reason?'<p class="sm-why"><b>'+(cand?'AI-suggested reasoning (unverified):':'Why this link was made:')+'</b> '+esc(c.reason)+'</p>':'')
 +(c.skill&&c.skill.label?'<p class="sm-sub" style="margin:6px 0 0">Through the skill: '+esc(c.skill.label)+'</p>':'')
 +(ev?'<p class="sm-sub" style="margin:4px 0 0">'+ev+' source'+(ev>1?'s':'')+' listed under More details.</p>':'')+'</article>'}
function renderEntity(d,n,tok){
 const e=d.entity||{},isOcc=(e.type||n.type)==='occupation',skills=d.skills||[],occs=d.occupations||[],conns=d.connections||[];
 const desc=String(e.description||'').trim(),short=desc.length>300?desc.slice(0,desc.lastIndexOf(' ',300)).replace(/[.,;:]$/,'')+'...':desc;
  let h='<div class="sm-kicker"><span class="sm-tag">'+(isOcc?'Career':'Skill')+'</span><span class="sm-tag goal"><i class="sm-sw" style="background:'+gCol(displayGoal(n))+'"></i>SDG '+esc(displayGoal(n))+'</span></div><h2>'+esc(e.label||n.label)+'</h2>';
 h+=desc?'<p class="sm-desc">'+esc(short)+'</p>':'<p class="sm-desc sm-empty">No description is recorded for this '+(isOcc?'career':'skill')+'.</p>';
 h+='<div class="sm-actions">'+(isOcc?'<a class="btn btn-primary btn-sm" href="/career?occupation_uri='+encodeURIComponent(e.uri||n.uri)+'">Explore full career profile</a>':'<button type="button" class="btn btn-primary btn-sm" data-act="related">Explore related careers</button>')+'<button type="button" class="btn btn-ghost btn-sm" data-act="close">Close</button></div>';
 h+='<section class="sm-sec"><h3>Compare with your Skills Passport</h3><div id="sm-passport"><div class="sm-skelline"></div></div></section>';
 if(isOcc){
  h+='<section class="sm-sec"><h3>Skills this career uses</h3>'+(skills.length?'<p class="sm-sub">'+skills.length+' skills from the ESCO skills library. Essential ones come first.</p><ul class="sm-skills">'+skills.slice(0,10).map(s=>'<li class="sm-skill" data-skill-uri="'+esc(s.uri)+'">'+esc(s.label)+'</li>').join('')+'</ul>'+(skills.length>10?'<details class="sm-fold"><summary>Show all '+skills.length+' skills</summary><ul class="sm-skills">'+skills.slice(10).map(s=>'<li class="sm-skill" data-skill-uri="'+esc(s.uri)+'">'+esc(s.label)+'</li>').join('')+'</ul></details>':''):'<p class="sm-empty">No skills are recorded for this career.</p>')+'</section>'}
 else{
  h+='<section class="sm-sec" id="sm-related"><h3>Careers that use this skill</h3>'+(occs.length?'<p class="sm-sub">'+(d.occupation_count>occs.length?'Showing '+occs.length+' of '+Number(d.occupation_count).toLocaleString()+' careers.':Number(d.occupation_count||occs.length).toLocaleString()+' careers.')+'</p><input class="sm-input" id="sm-relfilter" type="search" placeholder="Filter these careers" aria-label="Filter careers that use this skill"><ul class="sm-list" id="sm-rellist">'+occs.map(o=>{const nn=S.byId.get('occupation:'+o.uri);return '<li class="sm-row" data-label="'+esc(String(o.label).toLocaleLowerCase())+'"><span>'+esc(o.label)+'<small>'+(o.relation==='essential'?'Essential skill':'Optional skill')+'</small></span>'+(nn?'<button type="button" class="sm-mini" data-act="pick" data-id="'+esc(nn.id)+'">On map</button>':'')+'<a class="sm-mini" href="/career?occupation_uri='+encodeURIComponent(o.uri)+'">Full career</a></li>'}).join('')+'</ul><p class="sm-empty" id="sm-relnone" hidden>No careers match that filter.</p>':'<p class="sm-empty">No careers are recorded for this skill.</p>')+'</section>'}
 h+='<section class="sm-sec"><h3>Goals it may connect to</h3>';
 if(conns.length){
  const by={};conns.forEach(c=>{(by[c.goal_code]=by[c.goal_code]||[]).push(c)});
  const codes=Object.keys(by).sort((a,b)=>Number(a)-Number(b));
  h+='<p class="sm-sub">Each link shows how well it has been checked. '+(conns.some(c=>c.review_status==='unreviewed_candidate')?'AI suggestions are only leads to explore.':'')+'</p>';
  codes.forEach(g=>{const links=by[g];h+='<div class="sm-group"><h4><i class="sm-sw" style="background:'+gCol(g)+'"></i>SDG '+esc(g)+': '+esc(gName(g))+'</h4>'+links.slice(0,3).map(connCard).join('')+(links.length>3?'<details class="sm-fold"><summary>Show '+(links.length-3)+' more links</summary>'+links.slice(3).map(connCard).join('')+'</details>':'')+'</div>'});
 }else h+='<p class="sm-empty">No goal links are recorded for this '+(isOcc?'career':'skill')+'. That does not mean it has no contribution.</p>';
 h+='</section>';
 h+='<details class="sm-more"><summary>More details</summary>'+(conns.length?conns.map(c=>{const si=stInfo(c.review_status);return '<div class="sm-fine"><b>Target '+esc(c.target_code)+'</b> · SDG '+esc(c.goal_code)+'<br>Review status as recorded: <code>'+esc(c.review_status)+'</code>'+(c.skill&&c.skill.label?'<br>ESCO skill used: '+esc(c.skill.label)+(c.skill.relation?' ('+esc(c.skill.relation)+')':''):'')+(c.strength||c.direction?'<br>Reviewer rating: '+[c.strength,c.direction].filter(Boolean).map(esc).join(', '):'')+(c.review_status==='unreviewed_candidate'&&c.semantic_score!=null?'<br>Text-match score: '+esc(Number(c.semantic_score).toFixed(3))+'. This only ranks leads and is not a probability or a measure of impact.':'')+((c.evidence||[]).length?(c.evidence||[]).map(v=>{const u=safeHttps(v.url);return '<blockquote><b>'+esc(v.label||'Source')+'</b>'+(v.quote?'<br>'+esc(v.quote):'')+(u?'<br><a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">Open source</a>':'')+'</blockquote>'}).join(''):(c.review_status==='unreviewed_candidate'?'<br>No sources have been reviewed for this suggestion.':''))+'</div>'}).join(''):'<p class="sm-empty">No link details to show.</p>')+'<div class="sm-fine">ESCO identifier: '+esc(e.uri||n.uri)+'<br>Map position: layout only.</div></details>';
 if(d.notice)h+='<p class="sm-note">'+esc(d.notice)+'</p>';
 $('sm-panel').innerHTML=h;
 const rf=$('sm-relfilter');if(rf)rf.addEventListener('input',()=>{const q=rf.value.trim().toLocaleLowerCase();let c=0;document.querySelectorAll('#sm-rellist [data-label]').forEach(li=>{const ok=!q||li.dataset.label.includes(q);li.hidden=!ok;if(ok)c++});$('sm-relnone').hidden=c>0});
 fillPassport(d,n,tok)}
function fillPassport(d,n,tok){
 const host=$('sm-passport');if(!host)return;
 loadPassport().then(set=>{if(tok!==S.tok)return;const h=$('sm-passport');if(!h)return;h.innerHTML=passportHtml(d,n,set)
  if(n.type==='occupation')document.querySelectorAll('[data-skill-uri]').forEach(li=>{if(set.has(li.dataset.skillUri))li.classList.add('have')})})
 .catch(()=>{if(tok!==S.tok)return;const h=$('sm-passport');if(h)h.innerHTML='<div class="sm-pass warn"><strong>Your Skills Passport could not be loaded</strong>This is not the same as having no skills. <button type="button" class="sm-mini" data-act="retry-pass" style="margin-top:8px">Try again</button></div>'})}
function loadPassport(force){if(!passportP||force)passportP=req('/api/my-future').then(d=>new Set((d.confirmed_skills||[]).map(s=>s&&s.uri).filter(Boolean))).catch(e=>{passportP=null;throw e});return passportP}
function passportHtml(d,n,set){
 const link='<a href="/my-career">Open My Skills Passport</a>';
 if(!set.size)return '<div class="sm-pass none"><strong>No confirmed skills yet</strong>Confirm skills in your passport and they will be compared here. '+link+'</div>';
 if(n.type==='skill'){const has=set.has(n.uri);return has?'<div class="sm-pass"><strong>This skill is in your passport</strong>You have already confirmed it. '+link+'</div>':'<div class="sm-pass none"><strong>Not in your passport yet</strong>Only skills you have confirmed are compared, so this does not mean you lack it. '+link+'</div>'}
 const sk=d.skills||[];if(!sk.length)return '<div class="sm-pass none"><strong>No skills to compare</strong>This career has no ESCO skills recorded.</div>';
 const m=sk.filter(s=>set.has(s.uri)),ess=sk.filter(s=>s.relation==='essential'),em=ess.filter(s=>set.has(s.uri)),pct=Math.round(m.length/sk.length*100);
 return '<div class="sm-pass"><strong>You have confirmed '+m.length+' of '+sk.length+' skills for this career</strong>'+(ess.length?'Essential skills: '+em.length+' of '+ess.length+'. ':'')+'<div class="sm-meter" role="img" aria-label="'+m.length+' of '+sk.length+' skills confirmed"><i style="transform:scaleX('+(pct/100)+')"></i></div>'+(m.length?'Matching skills are highlighted below. ':'None of your confirmed skills match exactly yet. ')+'Skills you have not confirmed may still be skills you have. '+link+'</div>'}

/* ---------- browse list ---------- */
function renderBrowse(reset){
 if(reset)S.blimit=BROWSE_PAGE_SIZE;
 const list=S.vis.slice().sort((a,b)=>a.label.localeCompare(b.label)),host=$('sm-blist');
 $('sm-browse-sub').textContent=list.length.toLocaleString()+' '+(S.kind==='occupation'?'careers':S.kind==='skill'?'skills':'careers and skills')+(S.goal?' in SDG '+S.goal+': '+gName(S.goal):' across all 17 goals')+'.';
  host.innerHTML=list.length?list.slice(0,S.blimit).map(n=>'<li><button type="button" class="sm-bitem" data-act="pick" data-id="'+esc(n.id)+'"'+(S.sel&&S.sel.id===n.id?' aria-current="true"':'')+'><i class="sm-sw" style="background:'+gCol(displayGoal(n))+'"></i><span>'+esc(n.label)+'<small>'+typeName(n.type)+' · SDG '+esc(displayGoal(n))+' · '+esc(stInfo(bestStatus(n)).label)+'</small></span></button></li>').join(''):'<li class="sm-empty">Nothing to show with these filters. Try Reset View.</li>';
 const more=$('sm-bmore');more.hidden=list.length<=S.blimit;more.textContent='Show more ('+Math.max(0,list.length-S.blimit).toLocaleString()+' left)'}

/* ---------- load ---------- */
function setupChips(){
 $('sm-chips').innerHTML='<button type="button" class="sm-chip" data-goal-chip="" aria-pressed="true">All goals</button>'+S.goals.map(g=>'<button type="button" class="sm-chip" data-goal-chip="'+esc(g.code)+'" aria-pressed="false"><i class="sm-sw" style="background:'+gCol(g.code)+'"></i>'+esc(g.code)+'. '+esc(g.title)+'</button>').join('')}
function showState(html){const s=$('sm-state');s.hidden=false;s.innerHTML=html;const b=s.querySelector('button');if(b)b.addEventListener('click',load)}
async function load(){
 $('sm-state').hidden=true;$('sm-skel').hidden=false;
 try{
  const d=await req('/api/sdg/map');S.snapshot=d;
  const have=new Map((d.goals||[]).map(g=>[String(g.code),g]));
   S.goals=NAMES.map((t,i)=>Object.assign({code:String(i+1),color:COLORS[i],target_count:0,node_count:0},have.get(String(i+1))||{},{title:t,official_title:(have.get(String(i+1))||{}).title||t}));
  S.nodes=(d.nodes||[]).filter(n=>n&&n.id&&Number.isFinite(+n.x)&&Number.isFinite(+n.y)&&goalOf(n));
  S.byId=new Map(S.nodes.map(n=>[n.id,n]));
   S.statusesByGoal=new Map();
   (d.links||[]).forEach(link=>{['occupation:'+link.occupation_uri,'skill:'+link.skill_uri].forEach(id=>{const key=String(link.goal_code)+'|'+id;if(!S.statusesByGoal.has(key))S.statusesByGoal.set(key,[]);S.statusesByGoal.get(key).push(link.review_status)})});
   resize();layout();setupChips();S.fitK=fullView().k;S.view=fullView();recompute();syncChips();renderBrowse(true);renderPanel();
  $('sm-skel').hidden=true;
  const c=d.coverage||{},rows=[[c.occupation_node_count,'careers on the map'],[c.skill_node_count,'skills on the map'],[c.independently_human_approved_count,'links approved by an independent person'],[c.assistant_desk_reviewed_count,'links with sources checked by an AI assistant'],[c.candidate_link_count,'AI suggestions, not verified'],[(c.reviewed_goal_count!=null?c.reviewed_goal_count+' of '+(c.total_goal_count||17):null),'goals with at least one reviewed link']];
  $('sm-metrics').innerHTML=rows.filter(r=>r[0]!=null).map(r=>'<div class="sm-metric"><b>'+esc(typeof r[0]==='number'?r[0].toLocaleString():r[0])+'</b>'+esc(r[1])+'</div>').join('');
   $('sm-foot').textContent='The full map groups dots by their recorded primary goal. Some dots link to several goals; choosing a goal includes all its recorded links. Positions are only for browsing, not measures of impact or verified association.'+(d.generated_at?' Snapshot generated '+new Date(d.generated_at).toLocaleDateString()+'.':'');
  if(!S.nodes.length)showState('<strong>No careers or skills are on the map yet</strong>The 17 goals are shown, but nothing is linked to them in this snapshot.');
  draw();
   const linkedGoal=new URLSearchParams(location.search).get('goal');
   if(S.goals.some(g=>String(g.code)===linkedGoal))setGoal(linkedGoal);
 }catch(e){$('sm-skel').hidden=true;showState('<strong>The map could not load</strong><p>'+esc(e.message)+'</p><button type="button" class="btn btn-primary btn-sm">Try again</button>')}
}
document.addEventListener('click',e=>{
 const t=e.target.closest('button,a');
 if(!e.target.closest('.sm-search-wrap'))closeResults();
 if(!t)return;
 if(t.dataset.kind){setKind(t.dataset.kind);return}
 if(t.dataset.goalChip!==undefined&&t.hasAttribute('data-goal-chip')){setGoal(t.dataset.goalChip);return}
 if(t.dataset.pick){const n=S.byId.get(t.dataset.pick);closeResults();$('sm-search').value='';if(n)selectNode(n,true);return}
 if(t.dataset.pickGoal){closeResults();$('sm-search').value='';setGoal(t.dataset.pickGoal);return}
 const a=t.dataset.act;if(!a)return;
 if(a==='pick'){const n=S.byId.get(t.dataset.id);if(n)selectNode(n,true)}
 else if(a==='close')clearSel();
 else if(a==='all')setGoal('');
 else if(a==='retry-entity'&&S.sel)loadEntity(S.sel);
 else if(a==='retry-pass'){passportP=null;if(S.sel)loadEntity(S.sel)}
 else if(a==='related'){const r=$('sm-related');if(r){r.scrollIntoView({behavior:'instant',block:'start'});const f=$('sm-relfilter');if(f)f.focus({preventScroll:true})}}
});
$('sm-search').addEventListener('input',runSearch);
$('sm-search').addEventListener('focus',()=>{if($('sm-search').value.trim())runSearch()});
$('sm-search').addEventListener('keydown',e=>{if(e.key==='Escape')closeResults();else if(e.key==='Enter'){const f=$('sm-results').querySelector('button');if(f){e.preventDefault();f.click()}}else if(e.key==='ArrowDown'){const f=$('sm-results').querySelector('button');if(f){e.preventDefault();f.focus()}}});
$('sm-results').addEventListener('keydown',e=>{const bs=[...$('sm-results').querySelectorAll('button')],i=bs.indexOf(document.activeElement);if(e.key==='ArrowDown'&&i<bs.length-1){e.preventDefault();bs[i+1].focus()}else if(e.key==='ArrowUp'){e.preventDefault();(i>0?bs[i-1]:$('sm-search')).focus()}else if(e.key==='Escape'){closeResults();$('sm-search').focus()}});
$('sm-reset').addEventListener('click',resetAll);
$('sm-back').addEventListener('click',()=>setGoal(''));
$('sm-zin').addEventListener('click',()=>zoomAt(1.35));
$('sm-zout').addEventListener('click',()=>zoomAt(.74));
$('sm-bmore').addEventListener('click',()=>{S.blimit+=BROWSE_PAGE_SIZE;renderBrowse(false)});
bindCanvas();load();
})();
'''


SDG_MAP_HTML = _page(
    "SDG Career Map | FutureTwin AI",
    "sdg-map",
    SDG_MAP_CSS,
    SDG_MAP_BODY,
    SDG_MAP_JS,
)
