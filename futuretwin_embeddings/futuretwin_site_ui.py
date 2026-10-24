"""Shared site UI for FutureTwin AI: theme, navigation, Home dashboard, Find a Career.

Presentation only. futuretwin_pages.py imports these pieces and keeps the existing
route-facing names (HOME_HTML, MY_CAREER_HTML, CAREER_HTML, TRENDS_HTML).
"""

from futuretwin_intel_ui import FIND_JS, INTEL_CSS, INTEL_JS

FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&display=swap');"
)

# --------------------------------------------------------------- THEME
SITE_CSS = r'''
:root{
  --bg:#f2f5f9;--paper:#fcfdfe;--paper2:#f5f8fb;--ink:#13202e;--ink2:#38485a;--muted:#5f6f80;--faint:#8b98a6;
  --line:#d9e1ea;--line2:#e6ecf2;
  --harbor:#0b5cab;--harbor2:#094a8b;--harbor-soft:#e3eefa;
  --sage:#1c7a58;--sage-soft:#e1f1ea;
  --amber:#a86414;--amber-soft:#fbf0dc;
  --clay:#b0382c;--clay-soft:#fbe9e6;
  --plum:#5b4a99;--plum-soft:#ece8f7;
  --r:12px;--shadow:0 1px 2px #13202e0d;
  --display:'Public Sans',ui-sans-serif,system-ui,sans-serif;--body:'Public Sans',ui-sans-serif,system-ui,sans-serif;
}
body{font-size:15px;line-height:1.55}
body:before{display:none}
h1,h2,h3{font-weight:700;letter-spacing:-.02em}
.eyebrow{display:none}
:focus-visible{outline:2px solid var(--harbor);outline-offset:2px}
/* nav */
.nav{background:#fcfdfef2;border-bottom:1px solid var(--line)}
.nav .wrap{height:58px;gap:18px}
.logo{font-size:16px}
.logo-mark{border-radius:8px;width:30px;height:30px}
.logo-mark:before{border-color:#fcfdfe}
.navlinks{margin-left:6px;gap:2px;flex:1}
.navlink{font-size:14px;padding:7px 12px;border-radius:8px;border-bottom:0}
a.navlink:hover{background:var(--paper2);color:var(--ink)}
.navlink.active{color:var(--harbor);background:var(--harbor-soft)}
.pmenu-wrap{position:relative;margin-left:auto}
.pmenu-btn{display:flex;align-items:center;gap:8px;border:1px solid var(--line);background:var(--paper);border-radius:99px;padding:3px 10px 3px 3px;color:var(--ink2);font-weight:600;font-size:13px;min-height:44px;min-width:44px}
.pmenu-btn:hover{background:var(--paper2)}
.avatar{width:28px;height:28px;border-radius:50%;background:var(--harbor);color:#fcfdfe;display:grid;place-items:center;font-size:12px;font-weight:700}
.pmenu{position:absolute;right:0;top:calc(100% + 8px);min-width:210px;background:var(--paper);border:1px solid var(--line);border-radius:12px;box-shadow:0 10px 30px #13202e1f;padding:6px;z-index:30}
.pmenu a{display:block;padding:9px 11px;border-radius:8px;color:var(--ink);text-decoration:none;font-size:14px}
.pmenu a:hover,.pmenu a:focus-visible{background:var(--harbor-soft)}
.menu-btn{margin-left:0;border-radius:8px;font-size:14px;padding:7px 12px;min-height:44px;min-width:44px}
#passport-continue-btn{min-height:44px}
@media(max-width:900px){
  .nav .wrap{gap:10px}
  .menu-btn{display:block;order:3}
  .pmenu-wrap{order:2}
  .navlinks{top:58px;border-bottom:1px solid var(--line);box-shadow:0 12px 24px #13202e14}
  .navlink{padding:12px 12px;font-size:15px}
  .pmenu-btn span.pm-label{display:none}
  .pmenu-btn{padding:3px}
}
/* buttons / cards */
.btn{border-radius:8px;padding:10px 16px;font-size:14px;font-weight:600;box-shadow:none;gap:7px}
.btn-primary{background:var(--harbor);color:#fcfdfe;box-shadow:none}
.btn-primary:hover{background:var(--harbor2);transform:none;box-shadow:none}
.btn-ghost{background:var(--paper);color:var(--harbor);border:1px solid #b9cfe6}
.btn-ghost:hover{background:var(--harbor-soft);border-color:#9bbbdd;transform:none}
.btn-sm{padding:7px 12px;font-size:13px;border-radius:8px}
.card{border-radius:var(--r);box-shadow:var(--shadow)}
.c-flat{background:var(--paper2)}
.skel{background:linear-gradient(90deg,#e7edf3 0%,#f3f6f9 50%,#e7edf3 100%);background-size:200% 100%}
.foot{margin-top:40px;padding:20px 0 28px}
.foot .wrap{align-items:center}
.reveal{opacity:1;transform:none}
/* legacy cream overrides used by My Future / playground */
.myf-hero{background:transparent;padding:22px 0 0;border:0}
.myf-hero h1{font-size:28px;letter-spacing:-.02em;margin:0}
.myf-tabs,.pg-seg{background:#e8eef4}
.myf-empty{border-color:#c9d6e3;background:var(--paper2)}
.myf-rec:hover{border-color:#9bbbdd;transform:none}
.myf-error{border-color:#efc4be}
.pg-stage{background:radial-gradient(circle at 50% 44%,#eef4fa,#f7fafc 70%)}
.pg-node.confirmed{border-color:#9fc5b4;color:#1c6a4d}
.myf-chip{color:#1c6a4d}
/* shared page components */
.ft-main{max-width:1080px;margin:0 auto;padding:22px 20px 24px}
.ft-h1{font:700 28px/1.2 var(--body);letter-spacing:-.02em;margin:0 0 14px}
.ft-sec{margin-top:22px}
.ft-sec>h2,.ft-sec-head h2{font:700 18px var(--body);margin:0}
.ft-sec-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}
.ft-card{background:var(--paper);border:1px solid var(--line);border-radius:var(--r);padding:16px;box-shadow:var(--shadow);min-width:0}
.ft-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,290px),1fr));gap:12px}
.ft-job{display:flex;flex-direction:column;gap:10px}
.ft-job h3{font:700 16px/1.3 var(--body);margin:0;overflow-wrap:anywhere}
.ft-tags{display:flex;flex-wrap:wrap;gap:6px}
.ft-tag{display:inline-flex;align-items:center;background:var(--harbor-soft);color:var(--harbor2);border-radius:99px;padding:4px 10px;font-size:12px;font-weight:600}
.ft-tag.sage{background:var(--sage-soft);color:#17604a}
.ft-tag.plain{background:var(--paper2);color:var(--ink2);border:1px solid var(--line)}
.ft-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:auto}
.ft-actions>*{flex:0 0 auto}
.ft-note{font-size:13px;color:var(--muted);margin:0}
.ft-err{display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:var(--clay-soft);border:1px solid #efc4be;color:var(--clay);border-radius:10px;padding:10px 12px;font-size:13px;margin:8px 0}
.ft-empty{border:1px dashed #c4d2e0;border-radius:var(--r);padding:18px;background:var(--paper2);display:flex;gap:10px 14px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.ft-empty strong{display:block;font-size:15px}
.ft-skel{height:112px;border-radius:var(--r)}
.ft-more{margin-top:12px}
.ft-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;align-items:start}
.ft-search{display:flex;gap:8px;align-items:stretch;margin-bottom:6px}
.ft-search input{flex:1;min-width:0;border:1px solid #b9c9d9;background:var(--paper);border-radius:8px;padding:11px 13px;font:inherit;font-size:15px;color:var(--ink)}
.ft-search input:focus{border-color:var(--harbor)}
.ft-cta{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;background:var(--harbor);color:#fcfdfe;border-radius:var(--r);padding:20px}
.ft-cta h2{color:#fcfdfe;font:700 20px var(--body);margin:0}
.ft-cta .btn{background:#fcfdfe;color:var(--harbor2)}
.ft-back{display:inline-flex;gap:6px;align-items:center;font-size:14px;font-weight:600;color:var(--harbor);text-decoration:none;margin-bottom:8px;border:0;background:none;padding:4px 0}
.ft-skill-row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:9px 0;border-top:1px solid var(--line2);font-size:14px}
.ft-skill-row:first-child{border-top:0}
.ft-skill-row .ft-actions{margin:0}
.ft-info{width:30px;height:30px;border-radius:50%;border:1px solid var(--line);background:var(--paper);color:var(--harbor);font-weight:700;font-size:14px}
.ft-panel{margin-top:10px;padding-top:10px;border-top:1px solid var(--line2);font-size:13px;color:var(--ink2)}
.ft-panel p{margin:5px 0}
.ft-status{font-size:13px;color:var(--muted);min-height:18px;margin:6px 0 0}
.ft-cap{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.ft-aibar{display:flex;gap:4px;margin:4px 0 2px}
.ft-aibar i{display:block;height:6px;flex:1;border-radius:3px;background:var(--harbor-soft)}
.ft-aibar i.on{background:var(--harbor)}
.ft-goal{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.ft-goal strong{font-size:17px}
@media(max-width:700px){
  .ft-main{padding:16px 14px 20px}.ft-h1{font-size:24px}.ft-split{grid-template-columns:1fr}
  .ft-search{flex-wrap:wrap}.ft-search .btn{flex:1;justify-content:center}
  .ft-actions .btn{flex:1;justify-content:center}.ft-skill-row{flex-wrap:wrap}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
/*__INTEL_CSS__*/
/* profile page */
.pf-main{max-width:920px;margin:0 auto;padding:22px 20px 24px}
.pf-sec{margin-top:14px;padding:18px}
.pf-sec>h2,.pf-sec-head h2{font:700 18px var(--body);margin:0}
.pf-sec-head{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.pf-about{display:flex;gap:16px;align-items:flex-start}
.pf-avatar{width:56px;height:56px;font-size:20px;flex:none}
.pf-about dl{margin:6px 0 0;display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:14px}
.pf-about dt{color:var(--muted)}.pf-about dd{margin:0;min-width:0}
.pf-exp{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.pf-exp li{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;padding:10px 0;border-top:1px solid var(--line2);font-size:14px}
.pf-exp li:first-child{border-top:0}
.pf-exp q{display:block;color:var(--muted);font-size:13px;margin-top:3px;quotes:"\201C" "\201D"}
.pf-continue{display:flex;justify-content:flex-end;margin-top:14px}
@media(max-width:600px){.pf-about{flex-direction:column}.pf-about dl{grid-template-columns:1fr}.pf-continue .btn{width:100%;justify-content:center}}
'''.replace('/*__INTEL_CSS__*/',INTEL_CSS)

# --------------------------------------------------------------- NAV / FOOTER
NAV_ITEMS = (
    ("home", "/", "Home"),
    ("explore", "/career", "Explore Careers"),
    ("sdg-map", "/sdg-map", "SDG Map"),
    ("future", "/my-future", "My Future"),
    ("trends", "/trends", "AI Trends"),
)


def build_nav(active: str) -> str:
    def link(k, h, label):
        on = k == active
        return (
            f'<a class="navlink{" active" if on else ""}" href="{h}"'
            + (' aria-current="page"' if on else "")
            + f'>{label}</a>'
        )

    links = "".join(link(k, h, label) for k, h, label in NAV_ITEMS)
    profile_current = ' aria-current="page"' if active == "profile" else ""
    return (
        '<header class="nav" id="nav"><div class="wrap">'
        '<a class="logo" href="/" aria-label="FutureTwin home"><span class="logo-mark" aria-hidden="true"></span>FutureTwin<span>&nbsp;AI</span></a>'
        f'<nav class="navlinks" id="navlinks" aria-label="Main">{links}</nav>'
        '<div class="pmenu-wrap"><button class="pmenu-btn" id="pmenu-btn" type="button" aria-haspopup="true" aria-expanded="false" aria-controls="pmenu" aria-label="Profile menu">'
        '<span class="avatar" aria-hidden="true">Me</span><span class="pm-label">Profile</span></button>'
        '<div class="pmenu" id="pmenu" role="menu" hidden>'
        f'<a role="menuitem" href="/my-career"{profile_current}>My Profile</a>'
        '<a role="menuitem" href="/my-future?edit=interests">My Interests</a>'
        '<a role="menuitem" href="/my-future">Saved Careers and Plan</a>'
        '</div></div>'
        '<button class="menu-btn" type="button" aria-expanded="false" aria-controls="navlinks" id="menu-btn">Menu</button>'
        '</div></header>'
    )


FOOTER_HTML = r'''<footer class="foot"><div class="wrap">
<a class="logo" href="/" style="font-size:14px"><span class="logo-mark" aria-hidden="true" style="width:24px;height:24px"></span>FutureTwin<span>&nbsp;AI</span></a>
<div class="research"><a href="/trends">AI Trends</a><a href="/career">Explore Careers</a></div>
</div></footer>
<script>(()=>{const nav=document.getElementById('nav'),mb=document.getElementById('menu-btn'),pb=document.getElementById('pmenu-btn'),pm=document.getElementById('pmenu');
if(!nav||!mb||!pb||!pm)return;
mb.addEventListener('click',()=>{nav.classList.toggle('open');mb.setAttribute('aria-expanded',String(nav.classList.contains('open')));if(nav.classList.contains('open')){pm.hidden=true;pb.setAttribute('aria-expanded','false')}});
function closeP(focus){pm.hidden=true;pb.setAttribute('aria-expanded','false');if(focus)pb.focus()}
pb.addEventListener('click',()=>{const open=pm.hidden;pm.hidden=!open;pb.setAttribute('aria-expanded',String(open));if(open){nav.classList.remove('open');mb.setAttribute('aria-expanded','false');const a=pm.querySelector('a');if(a)a.focus()}});
document.addEventListener('click',e=>{if(!pm.hidden&&!e.target.closest('.pmenu-wrap'))closeP(false)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(!pm.hidden)closeP(true);else if(nav.classList.contains('open')){nav.classList.remove('open');mb.setAttribute('aria-expanded','false');mb.focus()}}});
pm.addEventListener('keydown',e=>{const items=[...pm.querySelectorAll('a')],i=items.indexOf(document.activeElement);if(e.key==='ArrowDown'){e.preventDefault();items[(i+1)%items.length].focus()}else if(e.key==='ArrowUp'){e.preventDefault();items[(i-1+items.length)%items.length].focus()}});
})();</script>'''

# --------------------------------------------------------------- SHARED JS CORE
CORE_JS = r'''
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const FT={state:null};
async function ftReq(url,opts={}){
  const h={Accept:'application/json',...(opts.body?{'Content-Type':'application/json'}:{}),...(opts.headers||{})};
  const r=await fetch(url,{...opts,credentials:'same-origin',headers:h});
  let d={};try{d=await r.json()}catch(_e){}
  if(!r.ok)throw new Error(d.error||'Something went wrong. Please try again.');
  return d;
}
async function ftLoad(){
  const d=await ftReq('/api/my-future');
  d.preferences=d.preferences||{career_areas:[],interests:[],target_occupation_uri:null};
  d.saved_occupations=d.saved_occupations||[];d.saved_careers=d.saved_careers||[];
  d.roadmap_goals=d.roadmap_goals||{};d.roadmap_progress=d.roadmap_progress||{};d.insurance_alternatives=d.insurance_alternatives||{};
  FT.state=d;return d;
}
function ftPayload(){
  const s=FT.state,c=o=>JSON.parse(JSON.stringify(o||{}));
  return {preferences:{career_areas:[...(s.preferences.career_areas||[])],interests:[...(s.preferences.interests||[])],target_occupation_uri:s.preferences.target_occupation_uri||null},
    saved_occupations:[...s.saved_occupations],roadmap_progress:c(s.roadmap_progress),roadmap_goals:c(s.roadmap_goals),insurance_alternatives:c(s.insurance_alternatives),purpose:c(s.purpose)};
}
async function ftSave(mutate){
  const p=ftPayload();mutate(p);
  const d=await ftReq('/api/my-future',{method:'POST',headers:{'X-CSRF-Token':FT.state.csrf_token},body:JSON.stringify(p)});
  Object.assign(FT.state,{preferences:d.preferences,saved_occupations:d.saved_occupations,saved_careers:d.saved_careers,roadmap_progress:d.roadmap_progress||{},roadmap_goals:d.roadmap_goals||{},insurance_alternatives:d.insurance_alternatives||{},csrf_token:d.csrf_token||FT.state.csrf_token});
  return d;
}
const ftSaved=u=>FT.state.saved_occupations.includes(u);
const ftGoal=()=>FT.state.preferences.target_occupation_uri||null;
function ftToggleSave(u){return ftSave(p=>{const i=p.saved_occupations.indexOf(u);if(i>=0){p.saved_occupations.splice(i,1);if(p.preferences.target_occupation_uri===u)p.preferences.target_occupation_uri=null}else p.saved_occupations.push(u)})}
function ftSetGoal(u){return ftSave(p=>{if(!p.saved_occupations.includes(u))p.saved_occupations.push(u);p.preferences.target_occupation_uri=u})}
function ftLive(t){const n=$('ft-live');if(n)n.textContent=t}
function ftJobCard(c){
  const el=document.createElement('article');el.className='ft-card ft-job';
  const skills=(c.skills||[]).slice(0,2);
  el.innerHTML='<h3>'+esc(c.title)+'</h3>'+(skills.length?'<div class="ft-tags" aria-label="Matching skills">'+skills.map(s=>'<span class="ft-tag">'+esc(s)+'</span>').join('')+'</div>':'')+
    '<div class="ft-actions"><button type="button" class="btn btn-ghost btn-sm" data-save></button><a class="btn btn-primary btn-sm" href="/career?occupation_uri='+encodeURIComponent(c.uri)+'">View Career</a></div><div data-msg></div>';
  if(c.task_exposure){
    const evidence=c.task_exposure,hasData=['available','uncertain_mapping'].includes(evidence.status);
    const note=document.createElement(hasData?'a':'p');note.className='ft-note';
    note.textContent=evidence.status==='available'?'O*NET tasks: '+evidence.classified_task_count+' assessed · exact link':evidence.status==='uncertain_mapping'?'O*NET tasks: possible mapping · inspect evidence':'O*NET tasks: not enough data';
    if(hasData)note.href='/career?occupation_uri='+encodeURIComponent(c.uri);
    el.insertBefore(note,el.querySelector('.ft-actions'));
  }
  ftEnrichCard(el,c);
  const b=el.querySelector('[data-save]');
  const paint=()=>{const s=ftSaved(c.uri);b.textContent=s?'Saved':'Save';b.setAttribute('aria-pressed',String(s));b.setAttribute('aria-label',(s?'Remove ':'Save ')+c.title+(s?' from saved careers':''))};
  paint();
  b.addEventListener('click',async()=>{
    b.disabled=true;el.querySelector('[data-msg]').innerHTML='';
    try{await ftToggleSave(c.uri);paint();ftLive(ftSaved(c.uri)?'Career saved.':'Career removed.');document.dispatchEvent(new CustomEvent('ft:saved-changed'))}
    catch(e){el.querySelector('[data-msg]').innerHTML='<div class="ft-err" role="alert">'+esc(e.message)+'</div>'}
    finally{b.disabled=false;b.focus()}
  });
  return el;
}
function ftRecToCard(r){return {uri:r.uri,title:r.title,skills:(r.matched_skills||[]).map(s=>s.label),task_exposure:r.task_exposure,rec:r}}
'''+INTEL_JS+r'''
'''

# --------------------------------------------------------------- HOME
HOME_DASH_CSS = r'''
.hm-welcome{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:6px}
.hm-welcome .ft-h1{margin:0}
.hm-trend-panel{display:grid;gap:14px}
.hm-trend-header{display:flex;align-items:center;gap:12px;min-width:0}
.hm-trend-orbit{width:52px;height:52px;flex:0 0 52px;display:grid;place-items:center;border-radius:15px;background:linear-gradient(145deg,#e3eefa,#f0f6fc);border:1px solid #d5e4f3}
.hm-trend-orbit svg{width:36px;height:36px}
.hm-trend-heading{min-width:0;flex:1}
.hm-trend-eyebrow{display:block;color:var(--harbor);font-size:11px;font-weight:700;letter-spacing:.075em;text-transform:uppercase}
.hm-trend-heading strong{display:block;color:var(--ink);font-size:16px;line-height:1.3}
.hm-trend-date{margin:3px 0 0;color:var(--muted);font-size:12px}
.hm-trend-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.hm-trend-metric{min-width:0;padding:10px 12px;border:1px solid var(--line2);border-radius:11px;background:var(--paper2)}
.hm-trend-metric strong{display:block;color:var(--ink);font-size:19px;line-height:1.2;font-variant-numeric:tabular-nums}
.hm-trend-metric span{display:block;margin-top:3px;color:var(--muted);font-size:11px;line-height:1.35}
.hm-trend-domains{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.hm-trend-domains-label{margin-right:2px;color:var(--muted);font-size:12px;font-weight:600}
.hm-trend-tags{display:flex;gap:6px;flex-wrap:wrap}
.hm-trend-tags .ft-tag{font-size:11px}
.hm-trend-status{display:flex;align-items:flex-start;gap:8px;padding:9px 11px;border:1px solid var(--line2);border-radius:10px;background:#f6f9fc;color:var(--ink2);font-size:12px;line-height:1.45}
.hm-trend-status-dot{width:7px;height:7px;flex:0 0 7px;margin-top:5px;border-radius:50%;background:var(--harbor)}
.hm-sdg-panel{display:grid;gap:14px}
.hm-sdg-panel h3{margin:0;font-size:17px;line-height:1.4}
.hm-sdg-panel p{margin:4px 0 0;color:var(--muted);font-size:13px}
.hm-sdg-counts{display:flex;gap:8px;flex-wrap:wrap}
.hm-sdg-goals{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.hm-sdg-goal{display:flex;align-items:center;gap:10px;min-height:58px;padding:10px 12px;border:1px solid var(--line);border-radius:12px;background:var(--paper2);color:var(--ink);text-decoration:none;font-size:13px;font-weight:600;transition:background .15s,border-color .15s}
.hm-sdg-goal:hover{background:var(--harbor-soft);border-color:var(--harbor)}
.hm-sdg-goal i{width:12px;height:28px;flex:0 0 12px;border-radius:4px}
.hm-sdg-goal small{display:block;color:var(--muted);font-size:10px;font-weight:600;letter-spacing:.04em}
@media(max-width:600px){.hm-sdg-goals{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(prefers-reduced-motion:reduce){.hm-sdg-goal{transition:none}}
@media(max-width:480px){
  .hm-trend-metric{padding:9px}
  .hm-trend-metric strong{font-size:17px}
  .hm-trend-metric span{font-size:10px}
}
'''

HOME_DASH_BODY = r'''
<main class="ft-main" id="home-main">
  <div class="hm-welcome"><h1 class="ft-h1" id="home-title">Welcome</h1></div>
  <div id="home-error" class="ft-err" role="alert" hidden><span id="home-error-text"></span><button type="button" class="btn btn-ghost btn-sm" id="home-retry">Try again</button></div>
  <section id="home-cta" class="ft-sec" hidden>
    <div class="ft-cta"><h2>Build your profile</h2><a class="btn" id="home-cta-btn" href="/my-career">Create My Profile</a></div>
  </section>
  <section id="home-jobs" class="ft-sec" aria-labelledby="jobs-h">
    <div class="ft-sec-head"><h2 id="jobs-h">Jobs for You</h2><a class="btn btn-ghost btn-sm" href="/career" id="jobs-all">See more</a></div>
    <div id="jobs-grid" class="ft-grid" aria-live="polite"><div class="skel ft-skel"></div><div class="skel ft-skel"></div><div class="skel ft-skel"></div></div>
  </section>
  <section id="home-goal" class="ft-sec" aria-labelledby="goal-h">
    <div class="ft-sec-head"><h2 id="goal-h">My Career Goal</h2></div>
    <div class="ft-card ft-goal" id="goal-card"><div class="skel" style="height:24px;width:40%"></div></div>
  </section>
  <section id="home-sdg" class="ft-sec" aria-labelledby="home-sdg-h">
    <div class="ft-sec-head"><h2 id="home-sdg-h">SDG Map</h2><a class="btn btn-ghost btn-sm" href="/sdg-map">Explore SDG Map</a></div>
    <div class="ft-card" id="home-sdg-card" aria-live="polite"><div class="skel" style="height:80px"></div></div>
  </section>
  <section id="home-trends" class="ft-sec" aria-labelledby="trends-h">
    <div class="ft-sec-head"><h2 id="trends-h">Latest AI Trends</h2><a class="btn btn-ghost btn-sm" href="/trends" id="trends-all">View AI Trends</a></div>
    <div class="ft-card" id="trends-card"><div class="skel" style="height:40px"></div></div>
  </section>
  <div class="pg-sr" id="ft-live" role="status" aria-live="polite" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)"></div>
</main>
'''

HOME_DASH_JS = r'''
(()=>{'use strict';
''' + CORE_JS + r'''
async function loadJobs(){
  const grid=$('jobs-grid');
  grid.innerHTML='<div class="skel ft-skel"></div><div class="skel ft-skel"></div><div class="skel ft-skel"></div>';
  try{
    const d=await ftReq('/api/my-future/recommendations?limit=3');
    const recs=(d.recommendations||[]).slice(0,3);
    grid.replaceChildren();
    if(!recs.length){
      const noSkills=d.status==='no_confirmed_skills';
      grid.innerHTML='<div class="ft-empty" style="grid-column:1/-1"><div><strong>'+(noSkills?'No jobs yet':'No matches yet')+'</strong></div><a class="btn btn-primary btn-sm" href="'+(noSkills?'/my-career':'/career')+'">'+(noSkills?'Create My Profile':'Explore Careers')+'</a></div>';
      return;
    }
    recs.forEach(r=>grid.appendChild(ftJobCard(ftRecToCard(r))));
  }catch(e){
    grid.innerHTML='<div class="ft-err" style="grid-column:1/-1" role="alert"><span>'+esc(e.message)+'</span><button type="button" class="btn btn-ghost btn-sm" id="jobs-retry">Try again</button></div>';
    $('jobs-retry').addEventListener('click',loadJobs);
  }
}
function renderGoal(){
  const card=$('goal-card'),g=ftGoal();
  if(!g){card.innerHTML='<span>No goal set</span><a class="btn btn-ghost btn-sm" href="/career">Find a Career</a>';return}
  const c=FT.state.saved_careers.find(x=>x.uri===g);
  card.innerHTML='<strong>'+esc(c?c.label:'Selected career')+'</strong><a class="btn btn-primary btn-sm" href="/my-future?career='+encodeURIComponent(g)+'">View My Future</a>';
}
function renderHomeSdgMap(data){
  if(!Array.isArray(data.goals)||!Array.isArray(data.nodes))throw new Error('The map data is unavailable.');
  const goals=new Map(data.goals.map(g=>[String(g.code),g]));
  const featured=[['3','Good Health and Well-being'],['4','Quality Education'],['6','Clean Water and Sanitation'],['7','Affordable and Clean Energy'],['12','Responsible Consumption and Production'],['13','Climate Action']];
  const careers=data.nodes.filter(n=>n.type==='occupation').length,skills=data.nodes.filter(n=>n.type==='skill').length;
  const counts=[[goals.size,'goals'],[careers,'careers'],[skills,'skills']].map(([count,label])=>'<span class="ft-tag plain">'+count.toLocaleString()+' '+(count===1?label.slice(0,-1):label)+'</span>').join('');
  const tiles=featured.filter(([code])=>goals.has(code)).map(([code,label])=>{
    const goal=goals.get(code),color=/^#[0-9a-f]{6}$/i.test(goal.color||'')?goal.color:'#1c4a6e';
    return '<a class="hm-sdg-goal" href="/sdg-map?goal='+encodeURIComponent(code)+'"><i style="background:'+color+'" aria-hidden="true"></i><span><small>SDG '+esc(code)+'</small>'+esc(label)+'</span></a>';
  }).join('');
  return '<div class="hm-sdg-panel"><div><h3>Find careers connected to goals you care about</h3><p>Explore careers and skills linked to the Sustainable Development Goals.</p></div><div class="hm-sdg-counts" aria-label="Current map coverage">'+counts+'</div><div class="hm-sdg-goals" aria-label="Explore a Sustainable Development Goal">'+tiles+'</div><p>Explore AI-suggested and reviewed connections. Each link shows how it has been checked.</p></div>';
}
async function loadSdgMap(){
  const card=$('home-sdg-card');
  card.innerHTML='<div class="skel" style="height:80px"></div>';
  try{card.innerHTML=renderHomeSdgMap(await ftReq('/api/sdg/map'))}
  catch(_e){
    card.innerHTML='<div class="ft-err" role="alert"><span>The SDG Map preview could not be loaded.</span><button type="button" class="btn btn-ghost btn-sm" id="home-sdg-retry">Try again</button></div>';
    $('home-sdg-retry').addEventListener('click',loadSdgMap);
  }
}
async function loadTrends(){
  const card=$('trends-card');
  card.innerHTML='<div class="skel" style="height:40px"></div>';
  const [ov,adv]=await Promise.allSettled([ftReq('/api/benchmarks/overview'),ftReq('/api/advancements')]);
  if(ov.status==='rejected'&&adv.status==='rejected'){
    card.innerHTML='<div class="ft-err" role="alert"><span>AI Trends could not be loaded.</span><button type="button" class="btn btn-ghost btn-sm" id="trends-retry">Try again</button></div>';
    $('trends-retry').addEventListener('click',loadTrends);return;
  }
  let html='';
  if(ov.status==='fulfilled'){
    const overview=ov.value;
    const ms=Array.isArray(overview.current_measurements)?overview.current_measurements:[];
    const domainRows=Array.isArray(overview.domains)?overview.domains:[];
    const benchmarkRows=Array.isArray(overview.benchmarks)?overview.benchmarks:[];
    const names=[...new Set(ms.map(m=>m.domain).filter(Boolean))].sort((a,b)=>a.localeCompare(b));
    const areaCount=domainRows.length||names.length;
    const modelCount=Number(overview.models_total)||0;
    const seriesCount=benchmarkRows.length;
    const latestCollected=ms.map(m=>Date.parse(m.collected_at||'')).filter(Number.isFinite).reduce((latest,value)=>Math.max(latest,value),0);
    const collectedLabel=latestCollected
      ?new Date(latestCollected).toLocaleDateString('en-SG',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'})
      :'Date not recorded';
    const metrics=[
      [areaCount?areaCount.toLocaleString('en-SG'):'—','capability areas'],
      [modelCount?modelCount.toLocaleString('en-SG'):'—','models in results'],
      [seriesCount?seriesCount.toLocaleString('en-SG'):'—','benchmark series']
    ];
    const metricHtml=metrics.map(([value,label])=>'<div class="hm-trend-metric"><strong>'+value+'</strong><span>'+label+'</span></div>').join('');
    const shownDomains=names.slice(0,5);
    const moreDomains=names.length-shownDomains.length;
    const domainHtml=names.length
      ?'<div class="hm-trend-domains"><span class="hm-trend-domains-label">Areas</span><div class="hm-trend-tags" aria-label="AI capability areas">'+shownDomains.map(n=>'<span class="ft-tag plain">'+esc(n)+'</span>').join('')+(moreDomains>0?'<span class="ft-tag plain">+'+moreDomains+' more</span>':'')+'</div></div>'
      :'<p class="ft-note">No capability areas are stored yet.</p>';
    html+='<div class="hm-trend-panel"><div class="hm-trend-header"><span class="hm-trend-orbit" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="17" stroke="#9bbbdc" stroke-width="1.5" stroke-dasharray="2.5 3.5"/><circle cx="24" cy="24" r="10" stroke="#0b5cab" stroke-width="1.5"/><path d="M24 7v7m17 10h-7M24 41v-7M7 24h7" stroke="#6d98c2" stroke-width="1.5" stroke-linecap="round"/><circle cx="24" cy="24" r="3.5" fill="#0b5cab"/><circle cx="37" cy="16" r="2.5" fill="#1c7a58"/></svg></span><div class="hm-trend-heading"><span class="hm-trend-eyebrow">AI benchmark tracker</span><strong>Following real model evaluations</strong><p class="hm-trend-date">Latest data collected '+esc(collectedLabel)+'</p></div></div><div class="hm-trend-metrics">'+metricHtml+'</div>'+domainHtml;
  }
  if(adv.status==='fulfilled'){
    const d=adv.value,list=Array.isArray(d.advancements)?d.advancements.filter(a=>a.comparable&&Number(a.change)>=0.5):[];
    let line;
    if(d.status==='insufficient_snapshots'||!(d.comparisons||[]).length)line='Not enough comparable snapshots yet.';
    else if(!list.length)line='No new comparable improvements in the latest snapshot.';
    else line=list.length+' new comparable improvement'+(list.length===1?'':'s')+': '+list.slice(0,3).map(a=>esc(a.capability)).join(', ')+'.';
    html+='<div class="hm-trend-status" role="status"><span class="hm-trend-status-dot" aria-hidden="true"></span><span>'+(list.length?line:esc(line))+'</span></div>';
  }else html+='<div class="hm-trend-status" role="status"><span class="hm-trend-status-dot" aria-hidden="true"></span><span>New advances could not be loaded.</span></div>';
  if(ov.status==='fulfilled')html+='</div>';
  else html+='<div class="ft-note">Benchmark coverage could not be loaded.</div>';
  card.innerHTML=html;
}
async function init(){
  $('home-error').hidden=true;
  loadSdgMap();
  try{await ftLoad()}catch(e){
    $('home-error-text').textContent=e.message;$('home-error').hidden=false;
    $('home-jobs').hidden=true;$('home-goal').hidden=true;loadTrends();return;
  }
  const s=FT.state,confirmed=Number(s.confirmed_skill_count||0),returning=!!s.profile_exists;
  $('home-title').textContent=returning&&confirmed?'Welcome back':'Welcome';
  $('home-cta').hidden=confirmed>0;
  $('home-cta-btn').textContent=returning?'Continue My Profile':'Create My Profile';
  $('home-jobs').hidden=confirmed===0;
  $('home-goal').hidden=!ftGoal()&&confirmed===0;
  renderGoal();
  if(confirmed>0)loadJobs();
  loadTrends();
}
$('home-retry').addEventListener('click',init);
document.addEventListener('ft:saved-changed',renderGoal);
init();
})();
'''

# --------------------------------------------------------------- FIND A CAREER / DETAIL
CAREER_NEW_CSS = r'''
.cr-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
.cr-head .ft-h1{margin-bottom:8px}
.cr-ai-task{border:1px solid var(--line2);border-radius:10px;background:var(--paper2);padding:10px 12px;margin-top:8px}
.cr-ai-task h4{font:600 14px/1.4 var(--body);margin:0}
.cr-chips{display:flex;gap:6px;flex-wrap:wrap}
.cr-chip{border:1px solid #b9cfe6;background:var(--paper);color:var(--harbor);border-radius:99px;padding:5px 12px;font-size:13px;font-weight:600}
.cr-chip:hover{background:var(--harbor-soft)}
.impact-evidence{margin-top:8px}.impact-evidence summary{cursor:pointer;color:var(--harbor);font-size:12px;font-weight:700}
.impact-evidence-body{font-size:12px;padding-top:6px}
.impact-meta-row{display:grid;grid-template-columns:96px minmax(0,1fr);gap:8px;padding:4px 0;border-bottom:1px solid var(--line2);overflow-wrap:anywhere}
.impact-meta-row b{color:var(--muted);font-weight:600}
.impact-task{padding:10px 12px;border:1px solid var(--line2);border-radius:10px;background:var(--paper2);margin-top:8px}
.impact-task-head{display:flex;justify-content:space-between;gap:8px}
.impact-task h3{font:600 14px/1.4 var(--body);margin:0}
.impact-rel-tag{flex:none;font-size:10px;font-weight:700;color:var(--harbor);background:var(--harbor-soft);border-radius:99px;padding:2px 8px;height:fit-content}
.impact-measure-line,.impact-model-line{font-size:11px;color:var(--muted);margin-top:4px;overflow-wrap:anywhere}
.impact-skills-label{font-size:10px;font-weight:700;color:var(--muted);margin-top:8px;text-transform:uppercase;letter-spacing:.04em}
.impact-skills{display:flex;flex-wrap:wrap;gap:5px;margin-top:4px}
.impact-skill{font-size:11px;border:1px solid var(--line);border-radius:99px;padding:3px 8px;background:var(--paper)}
.impact-more-skills{font-size:11px;color:var(--muted)}
.impact-candidates{margin:6px 0 0;padding-left:18px}
.impact-source{display:inline-block;margin-top:6px;font-weight:700}
'''

CAREER_NEW_BODY = r'''
<main class="ft-main" id="career-main">
  <section id="cr-find" hidden>
    <h1 class="ft-h1">Find a Career</h1>
    <form class="ft-search" id="cr-form" role="search" autocomplete="off">
      <input id="cr-q" type="search" maxlength="100" placeholder="Search careers..." aria-label="Search careers">
      <button class="btn btn-primary" type="submit" id="cr-go">Search</button>
    </form>
    <div id="cr-results-wrap" hidden>
      <div class="ft-sec-head" style="margin-top:16px"><h2 id="cr-results-h">Results</h2><button type="button" class="btn btn-ghost btn-sm" id="cr-clear">Clear</button></div>
      <div id="cr-results" class="ft-grid" aria-live="polite"></div>
      <button type="button" class="btn btn-ghost btn-sm ft-more" id="cr-results-more" hidden>See More</button>
    </div>
    <section id="cr-recs-wrap" class="ft-sec">
      <div class="ft-sec-head"><h2 id="cr-recs-h">Jobs for You</h2></div>
      <div id="cr-sort"></div>
      <div id="cr-recs" class="ft-grid" aria-live="polite"></div>
      <button type="button" class="btn btn-ghost btn-sm ft-more" id="cr-recs-more" hidden>See More</button>
    </section>
  </section>
  <div id="cr-cmpbar" class="ft-cmpbar" hidden role="region" aria-label="Compare careers"><span id="cr-cmp-text" aria-live="polite"></span><span class="ft-actions" style="margin:0"><button type="button" class="btn btn-ghost btn-sm" id="cr-cmp-clear">Clear</button><button type="button" class="btn btn-primary btn-sm" id="cr-cmp-go" disabled>Compare</button></span></div>
  <div id="cr-compare" class="ft-sec" hidden></div>
  <section id="cr-radar" class="ft-sec" aria-labelledby="radar-h" hidden>
    <div class="ft-sec-head"><h2 id="radar-h">Explore Job Opportunities</h2></div>
    <div id="cr-radar-summary" class="ft-note" role="note"></div>
    <div class="ft-tabs" role="tablist" aria-label="Job opportunity evidence">
      <button type="button" role="tab" data-rtab="jobs" aria-selected="true">Job Postings</button>
      <button type="button" role="tab" data-rtab="skills" aria-selected="false">Skills in Job Ads</button>
    </div>
    <div id="cr-radar-body" aria-live="polite" style="margin-top:10px"></div>
    <details class="ft-meth"><summary>How these results are matched</summary><div id="cr-radar-meth"></div></details>
  </section>
  <section id="cr-detail" hidden></section>
  <div id="cr-error" class="ft-err" role="alert" hidden><span id="cr-error-text"></span><button type="button" class="btn btn-ghost btn-sm" id="cr-retry">Try again</button></div>
  <div id="ft-live" role="status" aria-live="polite" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)"></div>
</main>
'''

CAREER_NEW_JS = r'''
(()=>{'use strict';
''' + CORE_JS + r'''
function node(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n}
/*__IMPACT__*/
const pg={view:null,sel:null,filter:'all',q:'',limit:12,picked:new Set(),focus:null};
const state={get roadmap_goals(){return FT.state.roadmap_goals}};
const pgLive=t=>{const n=$('pg-live');if(n)n.textContent=t};
/*__MAP__*/
const params=new URLSearchParams(location.search);
const uri=params.get('occupation_uri')||params.get('uri')||'';
const wide=()=>window.matchMedia('(min-width:900px)').matches;
let recAll=[],recShown=0,resAll=[],resShown=0,recStatus='';
function showErr(msg,retry){$('cr-error-text').textContent=msg;$('cr-error').hidden=false;$('cr-retry').onclick=()=>{$('cr-error').hidden=true;retry()}}
function skeletons(host,n=3){host.innerHTML=Array.from({length:n},()=>'<div class="skel ft-skel"></div>').join('')}
/* ---------- find view ---------- */
function drawList(host,items,shown,moreBtn){
  host.replaceChildren();items.slice(0,shown).forEach(c=>host.appendChild(ftJobCard(c)));
  moreBtn.hidden=items.length<=shown;
}
'''+FIND_JS+r'''
async function runSearch(q){
  q=(q||'').trim();if(q.length<2){$('cr-q').focus();return}
  $('cr-results-wrap').hidden=false;const host=$('cr-results');skeletons(host);$('cr-results-more').hidden=true;
  $('cr-results-h').textContent='Results';
  try{
    const d=await ftReq('/api/occupations/search?q='+encodeURIComponent(q)+'&limit=12');
    resAll=(d.suggestions||[]).map(s=>({uri:s.uri,title:s.label,skills:[]}));resShown=wide()?6:3;
    if(!resAll.length){host.innerHTML='<div class="ft-empty" style="grid-column:1/-1"><strong>No careers found</strong></div>';ftLive('No careers found.');return}
    drawList(host,resAll,resShown,$('cr-results-more'));ftLive(resAll.length+' careers found.');
  }catch(e){host.innerHTML='<div class="ft-err" style="grid-column:1/-1" role="alert"><span>'+esc(e.message)+'</span><button type="button" class="btn btn-ghost btn-sm" id="search-retry">Try again</button></div>';$('search-retry').addEventListener('click',()=>runSearch(q))}
}
function initFind(){
  $('cr-find').hidden=false;
  $('cr-form').addEventListener('submit',e=>{e.preventDefault();runSearch($('cr-q').value)});
  $('cr-clear').addEventListener('click',()=>{$('cr-results-wrap').hidden=true;$('cr-q').value='';$('cr-q').focus()});
  $('cr-results-more').addEventListener('click',()=>{resShown+=6;drawList($('cr-results'),resAll,resShown,$('cr-results-more'))});
  $('cr-recs-more').addEventListener('click',()=>{recShown+=6;drawList($('cr-recs'),recAll,recShown,$('cr-recs-more'))});
  const q0=params.get('q');if(q0){$('cr-q').value=q0;runSearch(q0)}
  loadRecs();
  $('cr-radar').hidden=false;initRadar();
}
/* ---------- detail view ---------- */
let D=null,skillsShown=3,aiOpen=false,aiShown=3,infoOpen=false;
function plan(){return FT.state.roadmap_goals[uri]||[]}
function missingSkills(){return [...(D.missing_essential||[]).map(s=>({...s,relation:'essential'})),...(D.missing_optional||[]).map(s=>({...s,relation:'optional'}))]}
function loadCareerPurpose(uri){
  const host=$('cr-sdg-list');if(!host)return;
  host.innerHTML='<p class="ft-note">Loading SDG links...</p>';
  ftReq('/api/sdg/occupation?uri='+encodeURIComponent(uri)).then(d=>{
    const rows=(d.connections||[]).slice(0,3);
    if(!rows.length){
      host.innerHTML='<p class="ft-note">No reviewed link or suggestion is available for this career yet. This is not evidence of zero contribution.</p><a class="btn btn-ghost btn-sm" href="/purpose?occupation_uri='+encodeURIComponent(uri)+'">Explore SDG connections</a>';
      return;
    }
    host.innerHTML='<div class="ft-grid">'+rows.map(r=>{
      const t=r.target||{},s=(r.skills||[])[0]||{},goal=String(t.goal_code||r.target_code.split('.')[0]);
      const candidate=r.review_status==='unreviewed_candidate';
      const status=candidate?'Unreviewed suggestion':r.review_status==='independently_human_approved'?'Independently human-approved':'Assistant desk-reviewed';
      const classification=candidate?'Relationship not assessed':esc(r.strength)+' · '+esc(r.direction);
      return '<article class="ft-card" style="padding:12px"><div class="ft-sec-head"><a href="/purpose?goal='+encodeURIComponent(goal)+'&occupation_uri='+encodeURIComponent(uri)+'"><strong>SDG '+esc(t.target_code||r.target_code)+'</strong></a><span class="ft-tag plain">'+classification+'</span></div><p class="ft-note">'+esc(t.target_title||'')+'</p><p class="ft-note"><strong>'+esc(s.label||'')+'</strong> ('+esc(s.relation||'')+' ESCO skill)</p><p class="ft-note">'+esc(r.reason||'')+'</p><p class="ft-note">'+status+' · <a href="/purpose?goal='+encodeURIComponent(goal)+'&occupation_uri='+encodeURIComponent(uri)+'">Sources and related careers</a></p></article>';
    }).join('')+'</div><p class="ft-note">These are potential associations, not measured social impact. <a href="/purpose?occupation_uri='+encodeURIComponent(uri)+'">Explore all connections</a>.</p>';
  }).catch(()=>{
    host.innerHTML='<p class="ft-note">SDG links are temporarily unavailable.</p>';
  });
}
function renderDetail(){
  const o=D.occupation,matched=[...(D.matched_essential||[]),...(D.matched_optional||[])],miss=missingSkills();
  const saved=ftSaved(uri),goal=ftGoal()===uri,exp=D.career_experience&&D.career_experience.status==='available';
  const inPlan=new Set(plan());
  const ai=D.ai_impact||{},groups=ai.status==='possible_links'?(Array.isArray(ai.task_groups)?ai.task_groups:legacyTaskGroups(ai.links)):[];
  const h=[];
  h.push('<a class="ft-back" href="/career">&larr; Find a Career</a>');
  h.push('<div class="cr-head"><h1 class="ft-h1">'+esc(o.label)+'</h1><button type="button" class="ft-info" id="cr-info" aria-expanded="'+infoOpen+'" aria-controls="cr-info-panel" aria-label="Career details">i</button></div>');
  h.push('<div id="cr-info-panel" class="ft-card" '+(infoOpen?'':'hidden')+' style="margin-bottom:12px"><p>'+esc(o.description||'No description is available.')+'</p><p class="ft-note">'+esc(D.why||'')+' This is a starting point for exploration, not a readiness or hiring score.</p></div>');
  h.push('<div class="ft-actions" style="margin-bottom:6px"><button type="button" class="btn btn-primary" id="cr-save" aria-pressed="'+saved+'">'+(saved?'Saved':'Save Career')+'</button><button type="button" class="btn btn-ghost" id="cr-goal" aria-pressed="'+goal+'">'+(goal?'My Goal':'Set as My Goal')+'</button>'+(exp?'<a class="btn btn-ghost" id="cr-exp" href="/my-future?career='+encodeURIComponent(uri)+'&mode=exp">Try Experience</a>':'')+'</div><div id="cr-msg"></div>');
  h.push('<section class="ft-sec" aria-labelledby="ms-h"><h2 id="ms-h">Matching Skills</h2><div class="ft-card" style="margin-top:10px">'+(matched.length?'<div class="ft-tags">'+matched.slice(0,10).map(s=>'<span class="ft-tag sage">'+esc(s.label)+'</span>').join('')+(matched.length>10?'<span class="ft-tag plain">+'+(matched.length-10)+'</span>':'')+'</div>':'<div class="ft-goal"><span>None of your confirmed skills are linked to this career yet.</span><a class="btn btn-ghost btn-sm" href="/my-career">Add Skill</a></div>')+'</div></section>');
  const rows=miss.slice(0,skillsShown).map(s=>'<div class="ft-skill-row"><span>'+esc(s.label)+'</span><div class="ft-actions"><button type="button" class="btn '+(inPlan.has(s.uri)?'btn-ghost':'btn-primary')+' btn-sm" data-plan="'+esc(s.uri)+'" aria-pressed="'+inPlan.has(s.uri)+'" aria-label="'+(inPlan.has(s.uri)?'Remove '+esc(s.label)+' from plan':'Add '+esc(s.label)+' to plan')+'">'+(inPlan.has(s.uri)?'In Plan':'Add to Plan')+'</button></div></div>').join('');
  h.push('<section class="ft-sec" aria-labelledby="sl-h"><div class="ft-sec-head"><h2 id="sl-h">Skills to Learn</h2>'+(inPlan.size?'<a class="btn btn-ghost btn-sm" href="/my-future?career='+encodeURIComponent(uri)+'">View Plan</a>':'')+'</div><div class="ft-card">'+(rows||'<span class="ft-note">No unconfirmed skills are listed for this career.</span>')+(miss.length>skillsShown?'<button type="button" class="btn btn-ghost btn-sm ft-more" id="cr-allskills">See All Skills ('+(miss.length-skillsShown)+' more)</button>':'')+(skillsShown>3&&miss.length<=skillsShown?'<button type="button" class="btn btn-ghost btn-sm ft-more" id="cr-fewskills">Show Fewer</button>':'')+'</div></section>');
  h.push('<section class="ft-sec" aria-labelledby="ai-tasks-h"><h2 id="ai-tasks-h">AI Tasks</h2><div class="ft-card" style="margin-top:10px">'+
    (groups.length?'':'<p class="ft-note" style="color:var(--ink2)">'+(ai.status==='unavailable'?'AI impact evidence could not be loaded.':'Not enough evidence to show AI impact for this career.')+'</p>')+
    '<div id="cr-exposure"></div><div class="ft-actions" style="margin-top:6px"><button type="button" class="btn btn-ghost btn-sm" id="cr-ai" aria-expanded="'+aiOpen+'" aria-controls="cr-ai-panel">'+(aiOpen?'Hide AI Impact':'View AI Impact')+'</button></div><div id="cr-ai-panel" '+(aiOpen?'':'hidden')+' class="ft-panel"></div></div></section>');
  h.push('<section class="ft-sec" aria-labelledby="map-h"><div class="ft-sec-head"><h2 id="map-h">Career Map</h2><div class="ft-actions" style="margin:0"><a class="btn btn-ghost btn-sm" href="/my-future?career='+encodeURIComponent(uri)+'&mode=sim">Try Scenarios</a><a class="btn btn-ghost btn-sm" id="cr-map" href="/my-future?career='+encodeURIComponent(uri)+'&mode=map">Open in My Future</a></div></div><div class="pg" id="cr-map-host" style="margin:0"></div></section>');
   h.push('<section class="ft-sec" aria-labelledby="cr-sdg-title"><div class="ft-sec-head"><h2 id="cr-sdg-title">Purpose &amp; SDGs</h2><a class="btn btn-ghost btn-sm" href="/purpose?occupation_uri='+encodeURIComponent(uri)+'">Explore connections</a></div><div id="cr-sdg-list" class="ft-grid"><p class="ft-note">Loading SDG links...</p></div></section>');
  $('cr-detail').innerHTML=ftTabify(h).join('');
  renderTaskExposure($('cr-exposure'),D.task_exposure);
   loadCareerPurpose(uri);
  fillRelated();wireTabs();
  wireDetail(groups);crMapRender();
}
function crMapRender(){
  const host=$('cr-map-host');if(!host||!D)return;
  const m=D.career_map;
  if(!m||!m.occupation){host.innerHTML='<div class="ft-empty"><strong>Career map not available</strong></div>';return}
  if(pg.sel&&!(m.skills||[]).some(s=>s.uri===pg.sel))pg.sel=null;
  const g=pgGraphSkills(m),total=(m.skills||[]).length,view=pg.view||(window.innerWidth<=640?'list':'graph');
  const nPick=[...pg.picked].filter(x=>!plan().includes(x)).length;
  host.innerHTML=pgMapBody(m,g,total,view,null,uri)+(nPick?'<div class="pg-bar"><span>'+nPick+' skill'+(nPick===1?'':'s')+' selected</span><button type="button" class="btn btn-primary btn-sm" data-cr-addpick>Add to Plan</button></div>':'')+'<div class="pg-sr" role="status" aria-live="polite" id="pg-live"></div>';
  const q=(sel,fn)=>host.querySelectorAll(sel).forEach(fn);
  const rr=(focus,msg)=>{pg.focus=focus;crMapRender();if(msg)pgLive(msg)};
  q('[data-pg-view]',b=>b.addEventListener('click',()=>{pg.view=b.dataset.pgView;rr('[data-pg-view="'+pg.view+'"]',pg.view==='graph'?'Map view':'List view')}));
  q('[data-pg-filter]',b=>b.addEventListener('click',()=>{pg.filter=b.dataset.pgFilter;pg.limit=12;rr('[data-pg-filter="'+pg.filter+'"]','Filter: '+b.textContent)}));
  const qi=host.querySelector('#pg-q');if(qi)qi.addEventListener('input',()=>{pg.q=qi.value;pg.limit=12;const p=qi.selectionStart;pg.focus='#pg-q';crMapRender();const n=$('pg-q');if(n)n.setSelectionRange(p,p)});
  q('[data-pg-skill]',b=>b.addEventListener('click',()=>{const u=b.dataset.pgSkill;pg.sel=pg.sel===u?null:u;const sk=(m.skills||[]).find(x=>x.uri===u),n=sk?pgAltConns(sk,m).length:0;rr('[data-pg-skill="'+CSS.escape(u)+'"]',pg.sel?(sk.label+' selected. Listed for '+n+' displayed alternative career'+(n===1?'':'s')+'.'):'Skill selection cleared.')}));
  q('[data-pg-center]',b=>b.addEventListener('click',()=>{pg.sel=null;rr('[data-pg-center]','Skill highlight cleared.')}));
  q('[data-pg-occ]',b=>b.addEventListener('click',()=>{pgLive('Loading '+(b.title||'career')+'.');window.location.href='/career?occupation_uri='+encodeURIComponent(b.dataset.pgOcc)}));
  q('[data-pg-more]',b=>b.addEventListener('click',()=>{pg.limit+=12;crMapRender();pgLive('More skills shown.')}));
  q('[data-pg-passport]',b=>b.addEventListener('click',()=>{window.location.href='/my-career?skill='+encodeURIComponent(b.dataset.pgPassport||'')}));
  q('[data-pg-pick]',b=>b.addEventListener('click',()=>{const u=b.dataset.pgPick;pg.picked.has(u)?pg.picked.delete(u):pg.picked.add(u);rr('[data-pg-pick="'+CSS.escape(u)+'"]',pg.picked.has(u)?'Skill selected.':'Skill unselected.')}));
  const add=host.querySelector('[data-cr-addpick]');
  if(add)add.addEventListener('click',async()=>{
    const picks=[...pg.picked].filter(x=>!plan().includes(x));add.disabled=true;
    try{await ftSave(p=>{p.roadmap_goals[uri]=[...new Set([...(p.roadmap_goals[uri]||[]),...picks])]});pg.picked.clear();renderDetail();ftLive(picks.length+' added to your plan.')}
    catch(e){add.disabled=false;pgLive('Could not save. '+e.message)}
  });
  if(pg.focus){const n=host.querySelector(pg.focus);if(n)n.focus();pg.focus=null}
}
function renderAiPanel(groups,ai){
  const p=$('cr-ai-panel');p.replaceChildren();
  p.appendChild(node('p','','Current benchmark results, not newly detected advances. New advances are tracked in AI Trends.'));
  if(!groups.length){p.appendChild(node('p','',ai.note||'No benchmark task links are available.'))}
  groups.slice(0,aiShown).forEach(g=>p.appendChild(renderImpactTaskGroup(g)));
  if(groups.length>aiShown){const b=node('button','btn btn-ghost btn-sm ft-more','Show More');b.type='button';b.addEventListener('click',()=>{aiShown+=3;renderAiPanel(groups,ai)});p.appendChild(b)}
  const dm=D.job_demand||{};
  if(dm.status==='broad_context'&&dm.group){p.appendChild(node('p','ft-note','Broad employment context: '+dm.group+(dm.employment_change_pct==null?'':' changed '+dm.employment_change_pct+'%')+'. Group-level change, not job openings.'))}
  const a=node('a','','View AI Trends');a.href='/trends';p.appendChild(a);
}
function wireDetail(groups){
  const msg=t=>{$('cr-msg').innerHTML=t?'<div class="ft-err" role="alert">'+esc(t)+'</div>':''};
  const ai=D.ai_impact||{};
  if(aiOpen)renderAiPanel(groups,ai);
  $('cr-info').addEventListener('click',()=>{infoOpen=!infoOpen;$('cr-info').setAttribute('aria-expanded',String(infoOpen));$('cr-info-panel').hidden=!infoOpen});
  $('cr-ai').addEventListener('click',()=>{aiOpen=!aiOpen;renderDetail();$('cr-ai').focus()});
  $('cr-save').addEventListener('click',async e=>{e.target.disabled=true;try{await ftToggleSave(uri);renderDetail();ftLive(ftSaved(uri)?'Career saved.':'Career removed.')}catch(err){msg(err.message);e.target.disabled=false}$('cr-save')&&$('cr-save').focus()});
  $('cr-goal').addEventListener('click',async e=>{e.target.disabled=true;try{await ftSetGoal(uri);renderDetail();ftLive('Career goal updated.')}catch(err){msg(err.message);e.target.disabled=false}$('cr-goal')&&$('cr-goal').focus()});
  document.querySelectorAll('[data-plan]').forEach(b=>b.addEventListener('click',async()=>{
    const su=b.dataset.plan;b.disabled=true;
    try{await ftSave(p=>{const g=new Set(p.roadmap_goals[uri]||[]);g.has(su)?g.delete(su):g.add(su);if(g.size)p.roadmap_goals[uri]=[...g];else delete p.roadmap_goals[uri];if(!p.saved_occupations.includes(uri)&&g.size){/* plan does not change saved careers */}});
      renderDetail();ftLive('Plan updated.')}
    catch(err){msg(err.message);b.disabled=false}
    const nb=document.querySelector('[data-plan="'+CSS.escape(su)+'"]');if(nb)nb.focus();
  }));
  const all=$('cr-allskills');if(all)all.addEventListener('click',()=>{skillsShown+=10;renderDetail();const n=document.querySelector('#cr-allskills')||document.querySelector('#cr-fewskills');if(n)n.focus()});
  const few=$('cr-fewskills');if(few)few.addEventListener('click',()=>{skillsShown=3;renderDetail();$('sl-h').scrollIntoView({block:'nearest'})});
}
async function loadDetail(){
  $('cr-error').hidden=true;const host=$('cr-detail');host.hidden=false;
  host.innerHTML='<div class="skel" style="height:34px;width:50%"></div><div class="skel" style="height:110px;margin-top:14px"></div><div class="skel" style="height:140px;margin-top:12px"></div>';
  try{
    const d=await ftReq('/api/my-future/career?uri='+encodeURIComponent(uri));
    D=d;renderDetail();document.title=d.occupation.label+' - FutureTwin AI';
  }catch(e){host.innerHTML='<a class="ft-back" href="/career">&larr; Find a Career</a>';showErr(e.message,loadDetail)}
}
async function boot(){
  try{await ftLoad()}catch(e){showErr(e.message,boot);if(!uri)$('cr-find').hidden=false;return}
  if(uri)loadDetail();else initFind();
}
boot();
})();
'''
