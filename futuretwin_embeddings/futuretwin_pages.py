"""User-facing pages for FutureTwin AI (presentation only, no backend logic).

Pages: HOME_HTML (/), CAREER_HTML (/career), TRENDS_HTML (/trends).
Plain HTML/CSS/vanilla JS assembled from shared pieces.
"""
from __future__ import annotations

from futuretwin_site_ui import (
    CAREER_NEW_BODY, CAREER_NEW_CSS, CAREER_NEW_JS, FONT_IMPORT, FOOTER_HTML,
    HOME_DASH_BODY, HOME_DASH_CSS, HOME_DASH_JS, SITE_CSS, build_nav,
)
from futuretwin_playground_ui import CAREER_MAP_JS, PLAYGROUND_CSS as _PG_CSS
from futuretwin_voice_ui import VOICE_CSS, VOICE_JS, VOICE_PANELS_HTML, VOICE_TABS_HTML
from futuretwin_exposure_ui import EXPOSURE_CSS, EXPOSURE_JS

BASE_CSS = r'''
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&display=swap');
:root{
  --bg:#f5f2ea;--paper:#fffdf8;--paper2:#faf6ec;--ink:#14263a;--ink2:#34485c;--muted:#66778a;--faint:#94a1ad;
  --line:#e6dfd0;--line2:#efe9dc;
  --harbor:#1c4a6e;--harbor2:#163b59;--harbor-soft:#e3edf4;
  --sage:#2f7a62;--sage-soft:#e2f0e8;
  --amber:#b7741c;--amber-soft:#fbefd9;
  --clay:#a8483a;--clay-soft:#f8e6e1;
  --plum:#6b5394;--plum-soft:#eee8f6;
  --r:18px;--shadow:0 1px 2px #14263a0a,0 8px 28px #14263a0d;
  --display:'Fraunces',Georgia,serif;--body:'Plus Jakarta Sans',ui-sans-serif,system-ui,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;min-height:100dvh;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
body:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.35;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.85' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 .4 0 0 0 0 .35 0 0 0 0 .25 0 0 0 .06 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
body>*{position:relative;z-index:1}
a{color:var(--harbor)}
button,select,textarea{font:inherit}
button{cursor:pointer}
:focus-visible{outline:3px solid #8fb8d6;outline-offset:2px;border-radius:8px}
[hidden]{display:none!important}
.wrap{max-width:1160px;margin:0 auto;padding:0 28px}
/* nav */
.nav{position:sticky;top:0;z-index:20;background:#f5f2eacc;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;gap:28px;height:68px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700;letter-spacing:-.02em;font-size:17px}
.logo-mark{width:32px;height:32px;border-radius:10px;background:var(--harbor);display:grid;place-items:center;position:relative;overflow:hidden}
.logo-mark:before{content:"";width:14px;height:14px;border:2px solid #f5f2ea;border-radius:50%}
.logo-mark:after{content:"";position:absolute;width:2px;height:9px;background:#e6a64a;top:7px;left:15px;transform:rotate(35deg);transform-origin:bottom;border-radius:2px}
.logo span{color:var(--sage)}
.navlinks{display:flex;gap:4px;align-items:center;margin-left:8px}
.navlink{position:relative;text-decoration:none;color:var(--ink2);font-size:14px;font-weight:600;padding:8px 13px;border-radius:10px;transition:background .2s,color .2s;display:flex;align-items:center;gap:7px;white-space:nowrap}
a.navlink:hover{background:#ece6d8;color:var(--ink)}
.navlink.active{color:var(--harbor);background:var(--harbor-soft)}
.soon{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--amber);background:var(--amber-soft);padding:2px 7px;border-radius:99px}
.nav-cta{margin-left:auto}
.menu-btn{display:none;margin-left:auto;background:none;border:1px solid var(--line);border-radius:10px;padding:7px 12px;font-weight:600;color:var(--ink2)}
/* buttons */
.btn{display:inline-flex;align-items:center;gap:9px;border:0;border-radius:12px;padding:13px 20px;font-weight:600;font-size:15px;text-decoration:none;transition:transform .2s,box-shadow .2s,background .2s}
.btn-primary{background:var(--harbor);color:#fbf8f1;box-shadow:0 6px 18px #1c4a6e33}
.btn-primary:hover{background:var(--harbor2);transform:translateY(-1px);box-shadow:0 10px 24px #1c4a6e40}
.btn-ghost{background:var(--paper);color:var(--ink);border:1px solid var(--line)}
.btn-ghost:hover{border-color:#cfc5b0;transform:translateY(-1px)}
.btn-sm{padding:8px 13px;font-size:13px;border-radius:10px}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.arrow{transition:transform .2s}.btn:hover .arrow{transform:translateX(3px)}
/* type */
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--sage)}
h1,h2,h3{font-family:var(--display);font-weight:500;letter-spacing:-.02em;margin:0;color:var(--ink)}
.lead{font-size:18px;color:var(--ink2);line-height:1.65}
.muted{color:var(--muted)}
/* cards */
.card{background:var(--paper);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--shadow)}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;padding:4px 10px;border-radius:99px;white-space:nowrap}
.chip:before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.c-obs{color:var(--harbor);background:var(--harbor-soft)}
.c-pos{color:var(--plum);background:var(--plum-soft)}
.c-up{color:var(--sage);background:var(--sage-soft)}
.c-flat{color:var(--muted);background:#eeeae0}
.c-warn{color:var(--amber);background:var(--amber-soft)}
.c-clay{color:var(--clay);background:var(--clay-soft)}
details.ev{border-top:1px dashed var(--line);margin-top:14px;padding-top:10px}
details.ev summary{cursor:pointer;font-size:13px;font-weight:600;color:var(--harbor);list-style:none;display:flex;align-items:center;gap:6px}
details.ev summary::-webkit-details-marker{display:none}
details.ev summary:before{content:"+";display:inline-grid;place-items:center;width:18px;height:18px;border-radius:6px;background:var(--harbor-soft);font-size:13px;transition:transform .2s}
details.ev[open] summary:before{content:"\2212"}
.evbody{font-size:13px;color:var(--ink2);line-height:1.65;padding:10px 2px 2px}
.evbody table{width:100%;border-collapse:collapse;font-size:12.5px}
.evbody td,.evbody th{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line2);vertical-align:top}
.evbody th{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.num{font-variant-numeric:tabular-nums}
.skel{background:linear-gradient(90deg,#ece6d8 0%,#f5f0e4 50%,#ece6d8 100%);background-size:200% 100%;animation:sh 1.3s infinite linear;border-radius:12px}
@keyframes sh{to{background-position:-200% 0}}
.reveal{opacity:0;transform:translateY(14px);transition:opacity .7s cubic-bezier(.2,.7,.2,1),transform .7s cubic-bezier(.2,.7,.2,1)}
.reveal.in{opacity:1;transform:none}
.fade-in{animation:fi .5s cubic-bezier(.2,.7,.2,1) both}
@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.errbox{background:var(--clay-soft);border:1px solid #ecc9c0;color:var(--clay);border-radius:14px;padding:14px 16px;font-size:14px;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
/* footer */
.foot{border-top:1px solid var(--line);margin-top:80px;padding:34px 0 44px;font-size:13px;color:var(--muted)}
.foot .wrap{display:flex;gap:24px;justify-content:space-between;flex-wrap:wrap;align-items:flex-start}
.foot a{color:var(--muted);text-decoration:none;border-bottom:1px solid transparent}
.foot a:hover{color:var(--ink);border-color:var(--line)}
.research{display:flex;gap:14px;flex-wrap:wrap;align-items:center}
.research b{font-weight:600;color:var(--ink2);font-size:12px;letter-spacing:.08em;text-transform:uppercase}
@media(max-width:900px){
  .menu-btn{display:block}.nav-cta{display:none}
  .navlinks{display:none;position:absolute;top:68px;left:0;right:0;background:var(--paper);border-bottom:1px solid var(--line);flex-direction:column;align-items:stretch;padding:10px 18px 16px;margin:0}
  .nav.open .navlinks{display:flex}
}
@media(max-width:600px){.wrap{padding:0 18px}.lead{font-size:16px}}
'''
BASE_CSS += SITE_CSS


def _nav(active: str) -> str:
    return build_nav(active)


FOOTER = FOOTER_HTML


def _page(title: str, active: str, css: str, body: str, script: str = "") -> str:
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" />'
        '<meta name="viewport" content="width=device-width, initial-scale=1" />'
        '<meta name="color-scheme" content="light" />'
        '<link rel="icon" href="data:," />'
        f'<title>{title}</title><style>{BASE_CSS}{css}</style></head><body>'
        + _nav(active) + body + FOOTER
        + (f"<script>{script}</script>" if script else "")
        + "</body></html>"
    )


# ---------------------------------------------------------------- HOME
HOME_CSS = r'''
.home-hero{padding:70px 0 46px;background:linear-gradient(180deg,#edf3f1,var(--bg))}
.home-hero>.wrap{display:grid;grid-template-columns:.9fr 1.1fr;gap:48px;align-items:center}
.hero-copy h1{font-family:var(--body);font-size:clamp(38px,5.8vw,66px);font-weight:700;letter-spacing:-.065em;line-height:1.03;max-width:540px;margin:16px 0 20px}
.hero-copy .lead{max-width:440px;margin:0}
.hero-benefits{display:flex;gap:9px 18px;flex-wrap:wrap;margin-top:25px;color:var(--muted);font-size:13px}
.hero-benefits span:before{content:"";display:inline-block;width:6px;height:6px;margin:0 8px 2px 0;background:var(--sage);border-radius:50%}
.upload-card{padding:25px}
.upload-card h2,.career-card h2{font-family:var(--body);font-size:19px;font-weight:700;letter-spacing:-.03em}
.upload-card>p,.career-card>p{font-size:13px;color:var(--muted);margin:5px 0 18px}
.dropzone{border:1.5px dashed #b9cfc7;background:#f7faf8;border-radius:15px;padding:24px;text-align:center;transition:background .2s,border-color .2s}
.dropzone.drag,.dropzone:focus-within{border-color:var(--sage);background:var(--sage-soft)}
.dropzone strong{display:block;font-size:14px}.dropzone p{font-size:12px;color:var(--muted);margin:5px 0 13px}
.file-input{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.file-line{display:flex;align-items:center;gap:12px;background:var(--sage-soft);border-radius:11px;padding:10px 12px;margin-top:12px;font-size:13px}
.file-line span:first-child{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}
.file-line button{border:0;background:transparent;color:var(--ink2);font-size:13px;padding:5px 7px}
.consent{display:flex;align-items:flex-start;gap:10px;margin:16px 2px 4px;font-size:12px;line-height:1.6;color:var(--ink2)}
.consent input{accent-color:var(--harbor);margin-top:4px;flex:0 0 auto}
.state-message{min-height:22px;margin:10px 0 0;font-size:13px;color:var(--muted)}
.state-error{color:var(--clay)}
.home-hero .search-wrap{max-width:none}
.searchform{display:flex;max-width:650px;margin:auto;background:var(--paper);border:1px solid #cedbd7;border-radius:16px;padding:7px;box-shadow:0 14px 40px #14263a12}
.searchform input{min-width:0;flex:1;border:0;background:transparent;padding:13px 16px;font:inherit;color:var(--ink);outline:none}
.searchform button{flex:0 0 auto}
.home-links{padding:24px 0 55px;display:grid;grid-template-columns:1fr 1fr;gap:16px}
.home-link{padding:23px 25px;text-decoration:none;color:var(--ink);display:flex;justify-content:space-between;align-items:center;gap:18px}
.home-link:hover{border-color:#b8ccc5;transform:translateY(-2px)}
.home-link h2{font-family:var(--body);font-weight:700;font-size:18px;margin:0 0 4px}
.home-link p{margin:0;color:var(--muted);font-size:13px}
.home-link .arrow{font-size:22px;color:var(--harbor)}
.search-wrap{max-width:650px;margin:auto;position:relative;text-align:left}
.searchform{margin:0}
.searchform input{width:100%}
.suggestions{position:absolute;z-index:12;top:calc(100% + 8px);left:0;right:0;max-height:420px;overflow:auto;background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:0 16px 38px #14263a1c;text-align:left}
.suggestion{display:block;width:100%;border:0;border-bottom:1px solid var(--line2);background:transparent;text-align:left;padding:13px 16px;color:var(--ink);cursor:pointer}
.suggestion:last-child{border-bottom:0}.suggestion:hover,.suggestion[aria-selected="true"]{background:var(--harbor-soft)}
.suggestion strong{display:block;font-size:14px}.suggestion-meta{font-size:12px;color:var(--muted);display:block;margin-top:2px}
.suggestion-desc{display:block;font-size:12px;line-height:1.45;color:var(--ink2);margin-top:5px}
.search-retry{margin:0 8px 6px}
.popular{display:flex;justify-content:center;align-items:center;gap:9px;flex-wrap:wrap;margin:22px auto 0;max-width:720px}
.popular-label{font-size:12px;color:var(--muted);font-weight:600;margin-right:3px}
.popular button{border:1px solid var(--line);background:var(--paper);border-radius:99px;padding:7px 12px;color:var(--ink2);font-size:12px;font-weight:600}
.popular button:hover{border-color:var(--harbor);color:var(--harbor)}
/* My Career profile review */
.workspace{padding:35px 0 30px}.workspace-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:20px}.workspace-head h1{font-family:var(--body);font-size:clamp(30px,4vw,42px);font-weight:700;letter-spacing:-.055em;margin:6px 0}.workspace-head p{margin:0;color:var(--muted);font-size:14px}
.profile-card{padding:24px;margin-bottom:18px}.profile-category{padding:18px 0;border-top:1px solid var(--line2)}.profile-category h3{font-family:var(--body);font-size:15px;font-weight:700;margin-bottom:12px}.profile-entry{display:grid;grid-template-columns:1fr 1fr auto;gap:10px;align-items:start;margin:9px 0}.profile-entry input,.profile-entry select{width:100%;border:1px solid var(--line);background:#fffefa;border-radius:9px;padding:10px 11px;color:var(--ink);font:inherit;font-size:13px}.profile-entry button{border:1px solid var(--line);background:var(--paper);border-radius:9px;color:var(--clay);padding:9px 11px}
.profile-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.profile-empty{text-align:center;padding:50px 18px}.profile-empty h2{font-family:var(--body);font-size:22px;font-weight:700}.profile-empty p{color:var(--muted);max-width:430px;margin:8px auto 18px}.career-card{padding:22px 24px}.career-card-head .eyebrow{margin-bottom:6px}.loading-line{color:var(--muted);padding:20px 4px;font-size:14px}
@media(max-width:800px){.home-hero>.wrap{grid-template-columns:1fr;gap:25px}.hero-copy .lead{max-width:600px}.workspace-head{align-items:flex-start;flex-direction:column}}
@media(max-width:650px){.home-hero{padding:48px 0 34px}.home-links{grid-template-columns:1fr;padding:10px 0 38px}.home-hero>.wrap{gap:24px}.upload-card{padding:19px}.dropzone{padding:19px 12px}.searchform{margin:0 4px}.searchform .btn{padding:11px 13px}.profile-entry{grid-template-columns:1fr;gap:7px}.profile-card{padding:17px}.profile-actions .btn{width:100%;justify-content:center}}
@media(max-width:650px){.popular{gap:7px}.popular-label{width:100%}}
.skill-list{list-style:none;margin:0;padding:0}.skill-row{border-top:1px solid var(--line2);padding:16px 0}.skill-top{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:9px}.skill-title{font-weight:700;font-size:16px;margin-right:auto}.skill-fields{display:grid;grid-template-columns:1fr 1fr;gap:10px}.skill-fields label{display:block;font-size:11px;font-weight:700;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px}.skill-fields input,.skill-fields select,.skill-add input{width:100%;border:1px solid var(--line);background:#fffefa;border-radius:9px;padding:10px 11px;color:var(--ink);font:inherit;font-size:14px}.skill-btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.skill-btns .danger{color:var(--clay)}.skill-add{display:flex;gap:10px;margin-top:18px}.skill-add input{flex:1}.skill-note{font-size:13px;color:var(--muted);margin:0 0 6px}.skill-empty{color:var(--muted);font-size:14px;padding:14px 0}
.passport-summary{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 22px}.passport-count{display:inline-flex;align-items:center;gap:6px;background:var(--paper2);border:1px solid var(--line);border-radius:99px;padding:7px 12px;font-size:13px;color:var(--ink2)}.passport-count strong{font-size:14px;color:var(--ink)}
dialog.card{border:1px solid var(--line);margin:auto;max-width:380px;width:calc(100% - 32px);padding:24px;color:var(--ink);box-shadow:0 24px 70px #14263a35}dialog.card::backdrop{background:#14263a66}dialog.card h2{font:700 22px var(--body);margin:8px 0}dialog.card p{color:var(--ink2);font-size:14px;line-height:1.55}
.passport-section{margin:0 0 22px}.passport-section h2{font:700 16px var(--body);margin:0 0 10px}.passport-review-list{list-style:none;padding:0;margin:0;display:grid;gap:8px}.passport-review-card{border:1px solid var(--line);border-radius:13px;padding:12px 14px;background:var(--paper);box-shadow:0 1px 2px #14263a08}.passport-review-main{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.passport-original{font-weight:650;font-size:14px;color:var(--ink);overflow-wrap:anywhere}.passport-arrow{color:var(--muted);font-size:13px}.passport-proposed{font-size:13px;color:var(--ink2);overflow-wrap:anywhere}.passport-origin{font-size:11px}.passport-review-actions{display:flex;gap:8px;margin-left:auto;flex-shrink:0}.passport-review-actions .btn{padding:7px 11px}.passport-review-edit{padding-top:12px;margin-top:11px;border-top:1px solid var(--line2)}.passport-review-edit[hidden]{display:none}.passport-tags{display:flex;flex-wrap:wrap;align-items:flex-start;gap:9px;list-style:none;padding:0;margin:0}.passport-tag-item{max-width:100%}.passport-tag{position:relative;max-width:min(100%,420px);border:1px solid #cadbd2;border-radius:999px;background:#f3f8f4;color:var(--ink);transition:border-color .16s,box-shadow .16s,background .16s}.passport-tag[open]{border-radius:15px;background:var(--paper);border-color:#9cb9a7;box-shadow:0 6px 20px #14263a0d}.passport-tag>summary{display:flex;align-items:center;gap:7px;padding:8px 12px;cursor:pointer;list-style:none;font-size:13px;font-weight:650}.passport-tag>summary::-webkit-details-marker{display:none}.passport-tag>summary:focus-visible{outline:2px solid var(--harbor);outline-offset:2px;border-radius:99px}.passport-check{width:16px;height:16px;flex:0 0 16px;color:#25855c}.passport-label{overflow-wrap:anywhere}.passport-detail{padding:3px 13px 13px;min-width:min(270px,calc(100vw - 64px));max-width:390px}.passport-detail dl{display:grid;gap:8px;margin:5px 0 11px}.passport-detail dt{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}.passport-detail dd{font-size:13px;color:var(--ink2);margin:2px 0 0;overflow-wrap:anywhere}.passport-detail blockquote{border-left:2px solid var(--line);margin:8px 0;padding-left:9px;color:var(--ink2);font-size:13px}.passport-detail-actions{display:flex;gap:7px;flex-wrap:wrap}.passport-detail-actions .btn{padding:6px 10px}.passport-continue{margin:17px 0 6px}.passport-continue .skill-note{margin-top:8px}.passport-empty-review{font-size:13px;color:var(--muted)}
@media(max-width:650px){.skill-fields{grid-template-columns:1fr}.skill-add{flex-direction:column}.skill-btns .btn{flex:1;justify-content:center}}
@media(max-width:650px){.passport-review-card{padding:11px}.passport-review-actions{width:100%;margin:2px 0 0}.passport-review-actions .btn{flex:1}.passport-tag{max-width:100%}.passport-detail{max-width:calc(100vw - 66px)}.passport-summary{gap:7px}.passport-count{font-size:12px}.passport-section{margin-bottom:18px}}
'''

HOME_BODY = r'''
<main>
<section class="home-hero"><div class="wrap">
  <div class="hero-copy reveal">
    <div class="eyebrow">A clearer view of work and AI</div>
    <h1>Is Your Career Ready for <span style="color:var(--sage)">AI?</span></h1>
    <p class="lead">Explore a career or build your skills profile.</p>
  </div>
  <section id="skills-start-card" class="card upload-card reveal" data-d="100" aria-labelledby="upload-title">
      <h2 id="upload-title">Build your skills profile</h2>
@@TABS@@<div id="ft-panel-resume" class="ft-panel" role="tabpanel" aria-labelledby="ft-tab-resume">
    <div class="dropzone" id="resume-drop">
      <strong>Choose or drop your resume</strong><p>Your file is sent for text extraction only after you consent.</p>
      <button class="btn btn-ghost btn-sm" id="resume-browse" type="button">Choose file</button>
      <input id="resume-file" class="file-input" type="file" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" aria-label="Resume PDF or Word file">
    </div>
    <div id="resume-fileline" class="file-line" hidden><span id="resume-filename"></span><button id="resume-remove" type="button" aria-label="Remove selected resume">Remove</button></div>
    <label class="consent"><input type="checkbox" id="resume-consent"><span>I agree to process extracted resume text locally on FutureTwin's server to find skill mentions and activity-based suggestions. No external AI service receives it. Extraction may miss skills; I will review suggestions before saving. The original file is not retained.</span></label>
    <p class="skill-note">Separate from this consent: you can <a href="/my-career?manual=1" id="manual-esco-link">pick skills manually</a> from the ESCO list with local matching, without sending anything to a paid service.</p>
    <button class="btn btn-primary" id="extract-resume" type="button" disabled>Review my skills <span class="arrow" aria-hidden="true">&rarr;</span></button>
    <p class="state-message" id="resume-status" role="status" aria-live="polite"></p>
</div>
@@PANELS@@
  </section>
</div></section>
<section id="career-search-panel" class="wrap" style="padding-top:12px" aria-labelledby="career-choice">
  <div class="career-card card">
    <div class="career-card-head"><div><div class="eyebrow">No resume needed</div><h2 id="career-choice">Explore a Career</h2></div></div>
  <div class="search-wrap">
    <form class="searchform" id="occupation-search-form" action="/career" method="get" autocomplete="off">
        <input id="occupation-query" type="search" placeholder="Search a job..." aria-label="Search a job title" aria-autocomplete="list" aria-controls="occupation-suggestions" aria-expanded="false" required maxlength="100" />
      <button class="btn btn-primary" id="explore-submit" type="submit" disabled>Explore <span class="arrow">&rarr;</span></button>
    </form>
     <div class="suggestions" id="occupation-suggestions" role="listbox" aria-label="Job title suggestions" hidden></div>
     <button id="search-retry" class="btn btn-ghost btn-sm search-retry" type="button" hidden>Retry search</button>
  </div>
  <div class="popular reveal" data-d="210"><span class="popular-label">Popular titles</span>
    <button type="button" data-title="AI Engineer">AI Engineer</button><button type="button" data-title="Software Developer">Software Developer</button><button type="button" data-title="Accountant">Accountant</button><button type="button" data-title="Data Analyst">Data Analyst</button>
  </div>
</div></div></section>
<section class="wrap home-links" aria-label="More context">
  <a class="card home-link" href="/trends"><div><h2>AI Trends</h2><p>See observed AI and workforce context.</p></div><span class="arrow" aria-hidden="true">&rarr;</span></a>
  <a class="card home-link" href="/my-career"><div><h2>My Career</h2><p>Review and manage your skills profile.</p></div><span class="arrow" aria-hidden="true">&rarr;</span></a>
</section>
<section id="my-career-view" class="wrap workspace" hidden aria-labelledby="my-career-title">
  <div class="workspace-head"><div><div class="eyebrow">Your skills</div><h1 id="my-career-title">My Skills Passport</h1></div><a class="btn btn-ghost btn-sm" href="/">Back to explore</a></div>
  <div id="career-skills-options" style="margin-bottom:24px"></div>
  <div id="profile-loading" class="loading-line" role="status">Loading your profile…</div>
  <div id="profile-error" class="errbox" role="alert" hidden><span id="profile-error-text"></span><button class="btn btn-ghost btn-sm" type="button" id="profile-retry">Try again</button></div>
  <div id="profile-empty" class="card profile-empty" hidden><h2>No saved skills yet</h2><p>Choose a way to add skills above. You review every match.</p></div>
  <form id="profile-form" class="card profile-card" hidden>
    <p id="profile-legacy-note" class="skill-note" hidden>Older profile data is preserved privately. Delete profile removes all saved data.</p>
    <div class="passport-summary" id="passport-summary" aria-live="polite"></div>
    <section id="passport-review" class="passport-section" aria-labelledby="passport-review-title" hidden><h2 id="passport-review-title">Needs review</h2><ul id="passport-review-list" class="passport-review-list"></ul></section>
    <section id="passport-confirmed" class="passport-section" aria-labelledby="passport-confirmed-title"><h2 id="passport-confirmed-title">Confirmed skills</h2><ul id="passport-tag-list" class="passport-tags"></ul><p id="passport-no-skills" class="passport-empty-review" hidden>No skills yet. Add one below or start with your resume or experience.</p></section>
    <div class="passport-continue" id="passport-continue" hidden><button class="btn btn-primary" id="passport-continue-btn" type="button">Continue to My Future <span class="arrow" aria-hidden="true">&rarr;</span></button></div>
    <div class="skill-add"><input id="skill-new" type="text" maxlength="200" aria-label="Add a skill" placeholder="Add a skill"><button class="btn btn-ghost btn-sm" type="button" id="skill-add-btn">Add skill</button></div>
    <p id="profile-save-status" class="state-message" role="status" aria-live="polite"></p>
    <div class="profile-actions"><button class="btn btn-primary" type="submit" id="save-profile">Save changes</button><button class="btn btn-ghost" type="button" id="delete-profile">Delete profile</button></div>
  </form>
</section>
</main>
'''

HOME_JS = r'''
(()=>{'use strict';
const input=document.getElementById('occupation-query'),form=document.getElementById('occupation-search-form'),list=document.getElementById('occupation-suggestions'),submit=document.getElementById('explore-submit');
let selected=null,items=[],active=-1,timer=0,controller=null;
const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function close(){list.hidden=true;input.setAttribute('aria-expanded','false');active=-1}
function choose(i){const item=items[i];if(!item)return;selected=item;input.value=item.label;submit.disabled=false;close()}
function render(data){items=Array.isArray(data.suggestions)?data.suggestions:[];list.replaceChildren();active=-1;
  document.getElementById('search-retry').hidden=true;
 if(!items.length){close();selected=null;submit.disabled=true;
    return}
 items.forEach((item,i)=>{const b=document.createElement('button');b.type='button';b.className='suggestion';b.id='occupation-option-'+i;b.setAttribute('role','option');b.setAttribute('aria-selected','false');
    b.innerHTML='<strong>'+esc(item.label)+'</strong><span class="suggestion-meta">'+esc(item.matched_as||'Job title match')+(item.matched_label&&item.matched_label.toLowerCase()!==item.label.toLowerCase()?' · '+esc(item.matched_label):'')+'</span>'+(item.description?'<span class="suggestion-desc">'+esc(item.description)+'</span>':'');
   b.addEventListener('mousedown',e=>e.preventDefault());b.addEventListener('click',()=>choose(i));list.appendChild(b)});
  list.hidden=false;input.setAttribute('aria-expanded','true');
}
  async function search(q){if(controller)controller.abort();controller=new AbortController();list.hidden=true;document.getElementById('search-retry').hidden=true;
 try{const r=await fetch('/api/occupations/search?q='+encodeURIComponent(q)+'&limit=10',{signal:controller.signal,headers:{'Accept':'application/json'}});if(!r.ok)throw new Error();const data=await r.json();render(data)}
   catch(e){if(e.name==='AbortError')return;close();items=[];selected=null;submit.disabled=true;document.getElementById('search-retry').hidden=false}}
 input.addEventListener('input',()=>{selected=null;submit.disabled=true;clearTimeout(timer);const q=input.value.trim();if(q.length<2){close();return}timer=setTimeout(()=>search(q),180)});
input.addEventListener('keydown',e=>{if(e.key==='ArrowDown'&&items.length){e.preventDefault();active=Math.min(active+1,items.length-1);list.querySelectorAll('[role=option]').forEach((n,i)=>{n.setAttribute('aria-selected',String(i===active))});input.setAttribute('aria-activedescendant','occupation-option-'+active)}
 else if(e.key==='ArrowUp'&&items.length){e.preventDefault();active=Math.max(active-1,0);list.querySelectorAll('[role=option]').forEach((n,i)=>n.setAttribute('aria-selected',String(i===active)));input.setAttribute('aria-activedescendant','occupation-option-'+active)}
 else if(e.key==='Enter'&&list&&!list.hidden&&active>=0){e.preventDefault();choose(active)}
 else if(e.key==='Escape')close()});
document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap'))close()});
document.querySelectorAll('.popular button[data-title]').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.title;input.dispatchEvent(new Event('input',{bubbles:true}));input.focus()}));
 form.addEventListener('submit',e=>{e.preventDefault();if(!selected){if(input.value.trim().length>=2)search(input.value.trim());input.focus();return}window.location.href='/career?occupation_uri='+encodeURIComponent(selected.uri)});
 document.getElementById('search-retry').addEventListener('click',()=>{if(input.value.trim().length>=2)search(input.value.trim());else input.focus()});

 const $=id=>document.getElementById(id), file=$('resume-file'), drop=$('resume-drop'), consent=$('resume-consent'), extract=$('extract-resume');
  const allowed=['pdf','doc','docx']; let csrfToken='',activeFile=null,pendingDraft=null;
 function setResumeStatus(message,isError=false){const node=$('resume-status');node.textContent=message;node.classList.toggle('state-error',isError)}
 function updateExtract(){extract.disabled=!(activeFile&&consent.checked)||extract.dataset.busy==='true'}
 function setFile(f){
  setResumeStatus('');
  const ext=(f.name.split('.').pop()||'').toLowerCase();
   if(!allowed.includes(ext)||f.size>10*1024*1024||!f.size){activeFile=null;file.value='';$('resume-fileline').hidden=true;setResumeStatus(allowed.includes(ext)?'The file must be 10 MB or smaller.':'Choose a PDF or Word document.',true);updateExtract();return}
  activeFile=f;$('resume-filename').textContent=f.name;$('resume-fileline').hidden=false;updateExtract()
 }
 $('resume-browse').addEventListener('click',()=>file.click());
 file.addEventListener('change',()=>{if(file.files&&file.files[0])setFile(file.files[0])});
 $('resume-remove').addEventListener('click',()=>{activeFile=null;file.value='';$('resume-fileline').hidden=true;setResumeStatus('');updateExtract()});
 consent.addEventListener('change',updateExtract);
 for(const eventName of ['dragenter','dragover'])drop.addEventListener(eventName,e=>{e.preventDefault();drop.classList.add('drag')});
 for(const eventName of ['dragleave','drop'])drop.addEventListener(eventName,e=>{e.preventDefault();drop.classList.remove('drag')});
 drop.addEventListener('drop',e=>{if(e.dataTransfer&&e.dataTransfer.files[0])setFile(e.dataTransfer.files[0])});
 async function readJson(response){let data={};try{data=await response.json()}catch{}if(!response.ok)throw new Error(typeof data.error==='string'?data.error:'Request could not be completed.');return data}
 async function apiProfile(){const response=await fetch('/api/profile',{headers:{'Accept':'application/json'},credentials:'same-origin'});const data=await readJson(response);csrfToken=data.csrf_token||csrfToken;return data.profile||null}
 function busy(button,on,label){button.disabled=on;if(on){button.dataset.oldText=button.textContent;button.textContent=label}else if(button.dataset.oldText){button.textContent=button.dataset.oldText;delete button.dataset.oldText}}
 extract.addEventListener('click',async()=>{
  if(!activeFile||!consent.checked)return;
  busy(extract,true,'Processing resume…');extract.dataset.busy='true';updateExtract();setResumeStatus('Processing resume text with AI…');
  try{
   if(!csrfToken){await apiProfile()}
   const body=new FormData();body.append('resume',activeFile);body.append('consent','true');
   const response=await fetch('/api/profile/extract',{method:'POST',body,headers:{'X-CSRF-Token':csrfToken,'Accept':'application/json'},credentials:'same-origin'});
   const data=await readJson(response);pendingDraft=data.draft||null;
    if(!pendingDraft)throw new Error('No editable profile was returned. Please try again.');
    activeFile=null;file.value='';$('resume-fileline').hidden=true;updateExtract();
    renderProfile(pendingDraft);dirty=true;$('profile-save-status').textContent='Unsaved draft. Review the skills and save when it looks right.';showCareerView(true);history.replaceState(null,'','/my-career');setResumeStatus('');
  }catch(err){setResumeStatus(err.message||'Resume extraction failed. Please try again.',true)}
  finally{extract.dataset.busy='false';busy(extract,false,'');updateExtract()}
 });

  const view=$('my-career-view'),homeHero=document.querySelector('.home-hero'),careerSearch=$('career-search-panel'),homeLinks=document.querySelector('.home-links');
   const skillsCard=$('skills-start-card'),skillsHome=skillsCard.parentElement;
   function showCareerView(show){view.hidden=!show;homeHero.hidden=show;careerSearch.hidden=show;homeLinks.hidden=show;(show?$('career-skills-options'):skillsHome).appendChild(skillsCard);if(show){view.scrollIntoView({block:'start'});}}
  let rows=[],dirty=false,savePromise=null,autosaveTimer=0,skillPrefillInProgress=false;
  const ORIGIN_TAG={explicit:['Named in resume','c-obs'],activity_suggestion:['Suggested from activity','c-warn'],user_added:['Added by you','c-flat'],legacy:['Earlier entry','c-flat']};
  function normRows(data){return Array.isArray(data&&data.skills)?data.skills.map(r=>{const candidates=Array.isArray(r.esco_candidates)?r.esco_candidates.filter(c=>c&&c.uri):[];const selected=r.selected_esco_uri||candidates[0]?.uri||null;return{value:String(r.value||''),evidence:String(r.evidence||''),origin:ORIGIN_TAG[r.origin]?r.origin:'legacy',source:r.source==='experience'?'experience':undefined,evidence_consent:r.source==='experience'?r.evidence_consent===true:undefined,esco_candidates:candidates,selected_esco_uri:selected,confirmed:!!(r.confirmed&&selected),editing:false}}):[]}
  function tagFor(r){return r.origin==='explicit'&&r.source==='experience'?['Named in experience','c-obs']:ORIGIN_TAG[r.origin]}
  function matchFor(r){return r.esco_candidates.find(x=>x.uri===r.selected_esco_uri)||r.esco_candidates[0]||null}
  function matchLabel(r){const c=r.esco_candidates.find(x=>x.uri===r.selected_esco_uri);return c?(c.label||c.uri):r.esco_candidates.length?'Choose from '+r.esco_candidates.length+' ESCO matches':'Choose a match'}
  function safeText(node,text){node.textContent=text||''}
  function setDirty(message='Unsaved changes.'){dirty=true;$('profile-save-status').classList.remove('state-error');safeText($('profile-save-status'),message)}
  function renderProfile(data){
    rows=normRows(data);drawRows();$('profile-legacy-note').hidden=!data.has_legacy_data;
    $('profile-loading').hidden=true;$('profile-error').hidden=true;$('profile-empty').hidden=true;$('profile-form').hidden=false;
  }
  function drawRows(){
    const review=$('passport-review-list'),tags=$('passport-tag-list');
    review.replaceChildren();tags.replaceChildren();
    const confirmed=rows.filter(r=>r.confirmed&&r.selected_esco_uri),pending=rows.filter(r=>!r.confirmed||!r.selected_esco_uri);
    $('passport-summary').replaceChildren();
    [[confirmed.length,'confirmed'],[pending.length,'need review']].forEach(([count,label])=>{const item=document.createElement('span');item.className='passport-count';const n=document.createElement('strong');n.textContent=String(count);item.append(n,document.createTextNode(' '+label));$('passport-summary').appendChild(item)});
    $('passport-review').hidden=pending.length===0;
    $('passport-confirmed').hidden=confirmed.length===0;
    $('passport-no-skills').hidden=rows.length>0;
    $('passport-continue').hidden=rows.length===0||pending.length>0;
    $('passport-continue-btn').disabled=!!savePromise;
    $('skill-new').disabled=!!savePromise;$('skill-add-btn').disabled=!!savePromise;$('delete-profile').disabled=!!savePromise;

    pending.forEach((r,reviewIndex)=>{
      const li=document.createElement('li');li.className='passport-review-card';li.dataset.passportIndex=String(reviewIndex);
      li.innerHTML='<div class="passport-review-main"><span class="passport-original"></span><span class="passport-arrow" aria-hidden="true">→</span><span class="passport-proposed"></span><span class="chip passport-origin"></span><div class="passport-review-actions"><button type="button" class="btn btn-ghost btn-sm passport-edit-btn">Edit</button><button type="button" class="btn btn-primary btn-sm passport-confirm-btn">Confirm</button></div></div><div class="passport-review-edit" hidden><div class="skill-fields"><div><label class="passport-word-label"></label><input type="text" maxlength="2000" class="skill-value"></div><div><label>ESCO match</label><select class="skill-select"></select></div></div><div class="skill-btns"><button type="button" class="btn btn-ghost btn-sm skill-edit-find">Find matches</button><button type="button" class="btn btn-ghost btn-sm passport-edit-close">Close edit</button><button type="button" class="btn btn-ghost btn-sm danger passport-remove-btn">Remove</button></div><p class="state-message skill-msg" role="status" aria-live="polite"></p></div>';
      safeText(li.querySelector('.passport-original'),r.value||'Untitled skill');
      safeText(li.querySelector('.passport-proposed'),matchLabel(r));
      const origin=li.querySelector('.passport-origin');origin.textContent=tagFor(r)[0];origin.className='chip passport-origin '+tagFor(r)[1];
      const edit=li.querySelector('.passport-review-edit'),input=li.querySelector('.skill-value'),select=li.querySelector('.skill-select');
      edit.hidden=!r.editing;input.value=r.value;input.setAttribute('aria-label','Edit original skill wording');
      li.querySelector('.passport-word-label').textContent=r.origin==='activity_suggestion'?'Original activity wording':'Original skill name';
      fillSelect(select,r);
      li.querySelector('.passport-edit-btn').hidden=!!r.editing;
      li.querySelector('.skill-edit-find').textContent=r.esco_candidates.length?'Search again':'Find matches';
      const confirm=li.querySelector('.passport-confirm-btn');confirm.disabled=!r.selected_esco_uri||!!r.stale||!!savePromise;
      li.querySelectorAll('.passport-edit-btn,.skill-value,.skill-select,.skill-edit-find,.passport-edit-close,.passport-remove-btn').forEach(control=>{control.disabled=!!savePromise});
      confirm.addEventListener('click',async()=>{
        if(!r.selected_esco_uri||r.stale||savePromise)return;
        clearTimeout(autosaveTimer);const before=JSON.stringify(rows);r.confirmed=true;r.editing=false;drawRows();
        if(!await saveProfileState('Skill confirmed and saved.')){rows=JSON.parse(before);drawRows()}
      });
      li.querySelector('.passport-edit-btn').addEventListener('click',async()=>{
        if(savePromise)return;
        if(r.confirmed){r.confirmed=false;r.editing=true;drawRows();await saveProfileState('Skill is ready for review. Choose a match and confirm again.',false)}
        else{r.editing=true;drawRows();$('passport-review-list').querySelector('[data-passport-index="'+reviewIndex+'"] .skill-value')?.focus()}
      });
      li.querySelector('.passport-edit-close').addEventListener('click',()=>{r.editing=false;drawRows()});
      li.querySelector('.passport-remove-btn').addEventListener('click',()=>removeRow(r));
      input.addEventListener('input',()=>{
        r.value=input.value;r.origin='user_added';r.confirmed=false;r.stale=true;r.selected_esco_uri=null;r.esco_candidates=[];
        safeText(li.querySelector('.passport-original'),r.value||'Untitled skill');safeText(li.querySelector('.passport-proposed'),'Find matches');
        fillSelect(select,r);confirm.disabled=true;setDirty('Editing a skill. Changes save as you review.');
        clearTimeout(autosaveTimer);autosaveTimer=setTimeout(()=>saveProfileState('Skill wording saved. Find matches and confirm to finish.',false),700);
      });
      select.addEventListener('change',async()=>{
        if(savePromise)return;r.selected_esco_uri=select.value||null;r.confirmed=false;r.stale=false;safeText(li.querySelector('.passport-proposed'),matchLabel(r));
        setDirty('Saving your proposed match…');await saveProfileState('Match choice saved. Confirm to finish.',false);
      });
      li.querySelector('.skill-edit-find').addEventListener('click',e=>{
        refreshSkillMatches(r,li,e.currentTarget);
      });
      review.appendChild(li);
      if(r.evidence){const evidence=document.createElement('details');evidence.className='ev';evidence.innerHTML='<summary>Why this skill?</summary><div class="evbody passport-pending-evidence"></div>';evidence.querySelector('.passport-pending-evidence').textContent=r.evidence;li.querySelector('.passport-review-edit').appendChild(evidence)}
    });

    confirmed.forEach(r=>{
      const li=document.createElement('li');li.className='passport-tag-item';
      li.innerHTML='<details class="passport-tag"><summary><svg class="passport-check" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m4 10 4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><span class="passport-label"></span></summary><div class="passport-detail"><dl><div><dt>Original term</dt><dd class="passport-term"></dd></div><div><dt>Matched ESCO skill</dt><dd class="passport-esco"></dd></div></dl><blockquote class="passport-evidence"></blockquote><div class="passport-detail-actions"><button type="button" class="btn btn-ghost btn-sm passport-detail-edit">Edit</button><button type="button" class="btn btn-ghost btn-sm danger passport-detail-remove">Remove</button></div></div></details>';
      const tag=li.querySelector('.passport-tag'),match=matchFor(r),label=match?(match.label||match.uri):r.value;
      safeText(li.querySelector('.passport-label'),label);safeText(li.querySelector('.passport-term'),r.value);
      safeText(li.querySelector('.passport-esco'),label);const evidence=li.querySelector('.passport-evidence');
      safeText(evidence,r.evidence);evidence.hidden=!r.evidence;
      li.querySelectorAll('.passport-detail-edit,.passport-detail-remove').forEach(control=>{control.disabled=!!savePromise});
      tag.setAttribute('aria-label',label+' confirmed; open for details');
      li.querySelector('.passport-detail-edit').addEventListener('click',async()=>{
        if(savePromise)return;r.confirmed=false;r.editing=true;drawRows();
        if(!await saveProfileState('Skill is ready for review. Choose a match and confirm again.',false)){$('profile-save-status').scrollIntoView({block:'nearest'})}
      });
      li.querySelector('.passport-detail-remove').addEventListener('click',()=>removeRow(r));
      tags.appendChild(li);
    });
    $('save-profile').disabled=!!savePromise||!dirty;
  }
  function fillSelect(select,r){
    select.replaceChildren();const none=document.createElement('option');none.value='';none.textContent=r.esco_candidates.length?'Choose a match':'Find matches';select.appendChild(none);
    r.esco_candidates.forEach(candidate=>{const option=document.createElement('option');option.value=candidate.uri;option.textContent=candidate.label||candidate.uri;select.appendChild(option)});
    if(r.selected_esco_uri&&!r.esco_candidates.some(candidate=>candidate.uri===r.selected_esco_uri)){const option=document.createElement('option');option.value=r.selected_esco_uri;option.textContent='Selected match';select.appendChild(option)}
    select.value=r.selected_esco_uri||'';
  }
  async function refreshSkillMatches(r,li,button){
    if(savePromise)return;
    clearTimeout(autosaveTimer);autosaveTimer=0;
    const msg=li.querySelector('.skill-msg'),value=r.value.trim();
    if(!value){safeText(msg,'Enter a skill or activity first.');return}
    button.disabled=true;msg.classList.remove('state-error');safeText(msg,'Finding ESCO matches…');
    try{
      if(!csrfToken)await apiProfile();
      const response=await fetch('/api/profile/match',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken,'Accept':'application/json'},credentials:'same-origin',body:JSON.stringify({value})});
      const data=await readJson(response);
      if(r.value.trim()!==value||!rows.includes(r)){safeText(msg,'Wording changed. Find matches again.');return}
      r.esco_candidates=Array.isArray(data.esco_candidates)?data.esco_candidates.filter(c=>c&&c.uri):[];
      r.selected_esco_uri=null;r.confirmed=false;r.stale=false;
      const select=li.querySelector('.skill-select');
      if(select)fillSelect(select,r);
      safeText(li.querySelector('.passport-proposed'),matchLabel(r));
      const saved=await saveProfileState(r.esco_candidates.length?'Matches found. Choose one, then confirm.':'No matches found. Try different wording.',false);
      if(saved){
        const reviewIndex=rows.filter(item=>!item.confirmed||!item.selected_esco_uri).indexOf(r);
        const currentLi=$('passport-review-list').querySelector('[data-passport-index="'+reviewIndex+'"]');
        const currentMsg=currentLi?.querySelector('.skill-msg');
        if(currentMsg)safeText(currentMsg,r.esco_candidates.length?'Matches found. Choose one, then confirm.':'No matches found. Try different wording.');
      }
    }catch(err){msg.classList.add('state-error');safeText(msg,err.message||'Matches could not be refreshed.')}
    finally{if(button.isConnected)button.disabled=!!savePromise}
  }
  async function saveProfileState(message='Your skills profile is saved.',render=true){
    if(savePromise)return false;
    const form=$('profile-form'),button=$('save-profile'),status=$('profile-save-status');
    const submitted={schema_version:2,skills:rows.filter(r=>r.value.trim()).map(r=>({
      value:r.value.trim(),evidence:r.evidence,origin:r.origin,selected_esco_uri:r.selected_esco_uri||null,
      confirmed:!!(r.confirmed&&r.selected_esco_uri),
      ...(r.source==='experience'?{source:'experience',evidence_consent:r.evidence_consent===true}:{}),
    }))};
    const task=(async()=>{
      button.disabled=true;button.textContent='Saving…';form.setAttribute('aria-busy','true');
      try{
        if(!csrfToken)await apiProfile();
        const response=await fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken,'Accept':'application/json'},credentials:'same-origin',body:JSON.stringify(submitted)});
        const data=await readJson(response);if(!data.profile)throw new Error('Your skills profile could not be saved.');
        dirty=false;status.classList.remove('state-error');
        if(render)renderProfile(data.profile);
        safeText(status,message);return true;
      }catch(err){
        dirty=true;status.classList.add('state-error');safeText(status,err.message||'Your changes could not be saved. Please try again.');return false;
      }finally{
        form.removeAttribute('aria-busy');button.textContent='Save changes';savePromise=null;button.disabled=!dirty;drawRows();
      }
    })();
    savePromise=task;drawRows();return task;
  }
  async function removeRow(row){
    if(savePromise)return;clearTimeout(autosaveTimer);const before=JSON.stringify(rows);
    rows=rows.filter(item=>item!==row);dirty=true;drawRows();
    if(!await saveProfileState('Skill removed from your saved passport.')){rows=JSON.parse(before);drawRows()}
  }
  async function addSkill(){
    const inp=$('skill-new'),v=inp.value.trim();if(!v){inp.focus();return}
    if(savePromise)return;
    if(autosaveTimer){clearTimeout(autosaveTimer);autosaveTimer=0;await saveProfileState('Skill wording saved.',false)}
    const r={value:v,evidence:'',origin:'user_added',esco_candidates:[],selected_esco_uri:null,confirmed:false,stale:true,editing:true};
    rows.push(r);inp.value='';setDirty('Skill added. Finding ESCO matches…');drawRows();
    const reviewIndex=rows.filter(item=>!item.confirmed||!item.selected_esco_uri).indexOf(r);
    const li=$('passport-review-list').querySelector('[data-passport-index="'+reviewIndex+'"]');
    if(!li)return;
    li.querySelector('.skill-value')?.focus();
    const button=li.querySelector('.skill-edit-find');
    if(button)refreshSkillMatches(r,li,button);
  }
 $('skill-add-btn').addEventListener('click',addSkill);
 $('skill-new').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();addSkill()}});
 async function loadCareer(){
  showCareerView(true);
  if(pendingDraft||dirty){$('profile-loading').hidden=true;$('profile-error').hidden=true;$('profile-empty').hidden=true;$('profile-form').hidden=false;try{await apiProfile()}catch{}return}
  $('profile-form').hidden=true;$('profile-empty').hidden=true;$('profile-error').hidden=true;$('profile-loading').hidden=false;
  try{const profile=await apiProfile();
   if(profile)renderProfile(profile);
   else{$('profile-loading').hidden=true;$('profile-empty').hidden=false}
   }catch(err){console.error('FutureTwin profile load failed:',err);$('profile-loading').hidden=true;$('profile-error').hidden=false;$('profile-error-text').textContent='Your skills profile could not be loaded. Please try again.'}
 }
  $('profile-retry').addEventListener('click',()=>syncCareerRoute());
   $('passport-continue-btn').addEventListener('click',()=>{
     window.location.href='/my-future';
   });
  $('profile-form').addEventListener('submit',async e=>{
   e.preventDefault();clearTimeout(autosaveTimer);await saveProfileState('Your skills passport is saved.',true);
  });
 $('delete-profile').addEventListener('click',async()=>{
  if(!window.confirm('Delete your saved profile? This cannot be undone.'))return;
  const button=$('delete-profile');busy(button,true,'Deleting…');
   try{clearTimeout(autosaveTimer);if(!csrfToken)await apiProfile();const response=await fetch('/api/profile',{method:'DELETE',headers:{'X-CSRF-Token':csrfToken,'Accept':'application/json'},credentials:'same-origin'});await readJson(response);pendingDraft=null;dirty=false;rows=[];$('profile-form').hidden=true;$('profile-empty').hidden=false}
   catch(err){$('profile-save-status').textContent=err.message||'The profile could not be deleted. Please try again.';$('profile-save-status').classList.add('state-error')}
  finally{busy(button,false,'')}
 });
   async function loadCareerWithSkillPrefill(){
    const params=new URLSearchParams(location.search),raw=params.get('skill');
    if(!raw||skillPrefillInProgress){await loadCareer();return}
    skillPrefillInProgress=true;
    try{
     await loadCareer();
     if(!$('profile-error').hidden)return;
     const label=raw.trim().slice(0,200);
     if(!label)return;
     if($('profile-form').hidden)renderProfile({skills:[]});
     const existing=rows.find(row=>String(row.value||'').trim().toLocaleLowerCase()===label.toLocaleLowerCase());
     if(!existing){
      $('skill-new').value=label;addSkill();
      safeText($('profile-save-status'),'Review the ESCO suggestion and confirm it before saving.');
     }else{
      safeText($('profile-save-status'),'This skill is already in your Passport. Review its existing match.');
     }
     history.replaceState(null,'','/my-career');
     $('profile-form').scrollIntoView({block:'start',behavior:'smooth'});
    }finally{skillPrefillInProgress=false}
   }
   function syncCareerRoute(){const isCareer=location.hash==='#my-career'||location.pathname==='/my-career';showCareerView(isCareer);if(isCareer){if(new URLSearchParams(location.search).has('skill'))loadCareerWithSkillPrefill();else loadCareer()}}
 window.ftProfileDirty=()=>dirty;
 window.addEventListener('ft:experience-saved',e=>{const d=e.detail||{};pendingDraft=null;dirty=false;renderProfile(d.profile||{});showCareerView(true);history.replaceState(null,'','/my-career');const st=$('profile-save-status');st.classList.remove('state-error');st.textContent=(d.added_count||0)+' skill'+(d.added_count===1?'':'s')+' added'+(d.duplicate_count?', '+d.duplicate_count+' already saved':'')+'. Your profile is saved.';$('profile-form').scrollIntoView({block:'start',behavior:'smooth'})});
 window.addEventListener('ft:manual',async()=>{history.replaceState(null,'','/my-career');await loadCareer();if($('profile-form').hidden)renderProfile({skills:[]});$('skill-new').focus()});
 window.addEventListener('hashchange',syncCareerRoute);
 syncCareerRoute();
})();
'''
HOME_BODY = HOME_BODY.replace('@@TABS@@', VOICE_TABS_HTML).replace('@@PANELS@@', VOICE_PANELS_HTML)
HOME_CSS += VOICE_CSS
HOME_JS += VOICE_JS
HOME_HTML = _page("FutureTwin AI", "home", HOME_DASH_CSS, HOME_DASH_BODY, HOME_DASH_JS)

# ---- My Profile: reuses the existing skills extraction interface and handlers.
_card_a = HOME_BODY.index('<section id="skills-start-card"')
_card_b = HOME_BODY.index('</div></section>\n<section id="career-search-panel"')
_SKILLS_CARD = HOME_BODY[_card_a:_card_b].replace("Build your skills profile", "Add skills")
_view_rest = HOME_BODY[HOME_BODY.index('  <div id="profile-loading"'):]
_view_rest = _view_rest.replace("<h2 id=\"passport-confirmed-title\">Confirmed skills</h2>", "<h2 id=\"passport-confirmed-title\">Confirmed</h2>")
_view_rest = _view_rest[:_view_rest.rindex("</section>\n</main>")]
PROFILE_BODY = (
    '<main><section id="my-career-view" class="pf-main" hidden aria-labelledby="my-career-title">'
    '<h1 class="ft-h1" id="my-career-title">My Profile</h1>'
    '<section class="card pf-sec" id="pf-about" aria-labelledby="pf-about-h"><div class="pf-about"><span class="avatar pf-avatar" aria-hidden="true">Me</span><div style="flex:1;min-width:0">'
    '<div class="pf-sec-head" style="margin-bottom:0"><h2 id="pf-about-h">About Me</h2><a class="btn btn-ghost btn-sm" href="/my-future?edit=interests" id="pf-edit-about">Edit</a></div>'
    '<dl id="pf-about-dl"><dt>Profile</dt><dd>My Profile</dd><dt>Interests</dt><dd id="pf-interests">Loading</dd><dt>Target career</dt><dd id="pf-goal">Loading</dd></dl>'
    '<p class="ft-note" style="margin-top:8px">Saved to this browser session only.</p></div></div></section>'
    '<div class="pf-sec-head" style="margin:18px 0 8px"><h2 style="font:700 18px var(--body);margin:0">My Skills</h2>'
    '<div class="ft-actions" style="margin:0"><button type="button" class="btn btn-ghost btn-sm" id="pf-add">Add Skill</button><button type="button" class="btn btn-ghost btn-sm" id="pf-edit" aria-pressed="false">Edit Skills</button></div></div>'
    + _view_rest +
    '<section class="card pf-sec" id="pf-resume" aria-labelledby="pf-resume-h"><div class="pf-sec-head"><h2 id="pf-resume-h">My Resume</h2>'
    '<button type="button" class="btn btn-primary btn-sm" id="pf-resume-btn" aria-expanded="false" aria-controls="career-skills-options">Upload Resume</button></div>'
    '<div id="career-skills-options" hidden>' + _SKILLS_CARD + '</div></section>'
    '<section class="card pf-sec" id="pf-exp" aria-labelledby="pf-exp-h" hidden><div class="pf-sec-head"><h2 id="pf-exp-h">Experience</h2></div>'
    '<ul class="pf-exp" id="pf-exp-list"></ul><button type="button" class="btn btn-ghost btn-sm ft-more" id="pf-exp-more" hidden>Show All</button></section>'
    '</section></main>'
)

PROFILE_JS = HOME_JS
_s0 = PROFILE_JS.index("const input=document.getElementById('occupation-query')")
_s1 = PROFILE_JS.index(" const $=id=>document.getElementById(id), file=")
PROFILE_JS = PROFILE_JS[:_s0] + PROFILE_JS[_s1:]
PROFILE_JS = PROFILE_JS.replace(
    ",homeHero=document.querySelector('.home-hero'),careerSearch=$('career-search-panel'),homeLinks=document.querySelector('.home-links');", ";", 1)
PROFILE_JS = PROFILE_JS.replace(
    "view.hidden=!show;homeHero.hidden=show;careerSearch.hidden=show;homeLinks.hidden=show;(show?$('career-skills-options'):skillsHome).appendChild(skillsCard);if(show){view.scrollIntoView({block:'start'});}",
    "view.hidden=!show;", 1)
PROFILE_JS = PROFILE_JS.replace("renderProfile(pendingDraft);dirty=true;", "renderProfile(keepConfirmed(pendingDraft));dirty=true;", 1)
PROFILE_JS = PROFILE_JS.replace("  function renderProfile(data){", """  function keepConfirmed(d){
    const keep=rows.filter(r=>r.confirmed&&r.selected_esco_uri).map(r=>({value:r.value,evidence:r.evidence,origin:r.origin,source:r.source,evidence_consent:r.evidence_consent,esco_candidates:r.esco_candidates,selected_esco_uri:r.selected_esco_uri,confirmed:true}));
    const ids=new Set(keep.map(r=>r.selected_esco_uri)),names=new Set(keep.map(r=>r.value.trim().toLowerCase()));
    const fresh=(d.skills||[]).filter(r=>!ids.has(r.selected_esco_uri)&&!names.has(String(r.value||'').trim().toLowerCase()));
    return {...d,skills:[...keep,...fresh]};
  }
  function renderProfile(data){""", 1)
PROFILE_JS = PROFILE_JS.replace("    $('save-profile').disabled=!!savePromise||!dirty;\n  }\n  function fillSelect",
 "    $('save-profile').disabled=!!savePromise||!dirty;\n    drawExperience();\n  }\n  function fillSelect", 1)
PROFILE_JS = PROFILE_JS.replace("  function fillSelect(select,r){", """  let expShown=5,editAll=false;
  function experienceRows(){
    return rows.filter(r=>r.confirmed&&r.selected_esco_uri&&r.evidence&&(r.origin==='activity_suggestion'||r.source==='experience'));
  }
  function drawExperience(){
    const host=$('pf-exp-list'),sec=$('pf-exp');if(!host)return;host.replaceChildren();
    $('pf-resume-btn').textContent=rows.length?'Replace Resume':'Upload Resume';
    if(editAll)document.querySelectorAll('.passport-tag').forEach(d=>{d.open=true});
    const list=experienceRows();
    sec.hidden=!list.length;
    list.slice(0,expShown).forEach(r=>{
      const li=document.createElement('li'),box=document.createElement('div'),b=document.createElement('strong'),q=document.createElement('q'),ed=document.createElement('button');
      b.textContent=(matchFor(r)||{}).label||r.value;q.textContent=r.evidence;box.append(b,q);
      ed.type='button';ed.className='btn btn-ghost btn-sm';ed.textContent='Edit';ed.setAttribute('aria-label','Edit '+b.textContent);
      ed.addEventListener('click',async()=>{if(savePromise)return;r.confirmed=false;r.editing=true;drawRows();await saveProfileState('Skill is ready for review. Choose a match and confirm again.',false);const rv=$('passport-review');if(rv&&!rv.hidden)rv.scrollIntoView({block:'nearest'})});
      li.append(box,ed);host.appendChild(li);
    });
    $('pf-exp-more').hidden=list.length<=expShown;
  }
  function fillSelect(select,r){""", 1)
PROFILE_JS = PROFILE_JS.replace(" window.ftProfileDirty=()=>dirty;", """ window.ftProfileDirty=()=>dirty;
 $('pf-exp-more').addEventListener('click',()=>{expShown=1000;drawExperience()});
 $('pf-add').addEventListener('click',()=>window.dispatchEvent(new CustomEvent('ft:manual')));
 if(new URLSearchParams(location.search).get('manual')==='1')setTimeout(()=>window.dispatchEvent(new CustomEvent('ft:manual')),0);
 $('pf-edit').addEventListener('click',()=>{editAll=!editAll;$('pf-edit').setAttribute('aria-pressed',String(editAll));$('pf-edit').textContent=editAll?'Done':'Edit Skills';document.querySelectorAll('.passport-tag').forEach(d=>{d.open=editAll})});
 $('pf-resume-btn').addEventListener('click',()=>{const o=$('career-skills-options');o.hidden=!o.hidden;$('pf-resume-btn').setAttribute('aria-expanded',String(!o.hidden));if(!o.hidden)$('resume-browse').focus()});""", 1)
assert "keepConfirmed(pendingDraft)" in PROFILE_JS and "drawExperience();\n  }" in PROFILE_JS and "pf-add" in PROFILE_JS and "homeHero" not in PROFILE_JS and "occupation-query" not in PROFILE_JS

PROFILE_ABOUT_JS = r'''
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function load(){
  try{
    const r=await fetch('/api/my-future',{credentials:'same-origin',headers:{Accept:'application/json'}});
    const d=await r.json();if(!r.ok)throw new Error();
    const names=(d.preferences&&d.preferences.interests)||[];
    $('pf-interests').innerHTML=names.length?'<span class="ft-tags">'+names.map(n=>'<span class="ft-tag">'+esc(n)+'</span>').join('')+'</span>':'None chosen';
    const g=d.preferences&&d.preferences.target_occupation_uri,c=(d.saved_careers||[]).find(x=>x.uri===g);
    $('pf-goal').innerHTML=g&&c?'<a href="/my-future?career='+encodeURIComponent(g)+'">'+esc(c.label)+'</a>':'None selected';
  }catch(e){
    $('pf-interests').innerHTML='Could not load <button type="button" class="myf-link" id="pf-about-retry">Try again</button>';$('pf-goal').textContent='';
    $('pf-about-retry').addEventListener('click',load);
  }
}
load();
})();
'''

PROFILE_JS_ALL = PROFILE_JS + PROFILE_ABOUT_JS

MY_CAREER_HTML = _page("My Profile - FutureTwin AI", "profile", HOME_CSS, PROFILE_BODY, PROFILE_JS_ALL)


# ---------------------------------------------------------------- CAREER
CAREER_CSS = r'''
.phead{padding:42px 0 24px}.phead h1{font-family:var(--body);font-size:clamp(34px,5vw,54px);font-weight:700;letter-spacing:-.055em;line-height:1.05;margin:9px 0 12px}.phead p{max-width:690px;margin:0}
.occupation-meta{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-top:16px}
.group-tag{font-size:12px;color:var(--harbor);background:var(--harbor-soft);padding:5px 10px;border-radius:99px;font-weight:700}
.desc{font-size:14px;color:var(--ink2);max-width:760px;margin:9px 0 0}
.occupation-details{margin-top:8px;font-size:13px;color:var(--muted)}
.occupation-details summary{cursor:pointer;color:var(--harbor);font-weight:600}
.load{display:grid;gap:12px;padding:10px 0 30px}.skeleton-card{height:210px}
.insights{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;align-items:stretch;margin:14px 0 24px}
.insight{padding:22px;min-height:230px;display:flex;flex-direction:column}
.insight-head{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:13px}
.insight h2{font-family:var(--body);font-size:18px;font-weight:700;letter-spacing:-.02em}
.insight p{font-size:14px;color:var(--ink2);margin:0;line-height:1.65}
.insight .note-line{font-size:12px;color:var(--muted);margin-top:14px}
.insight .ev{margin-top:auto;padding-top:12px}
.insight-body{font-size:14px;color:var(--ink2);line-height:1.65}
.evidence-list{display:grid;gap:9px;margin-top:14px}
.evidence-item{padding:11px 12px;background:var(--paper2);border-radius:11px;font-size:13px}
.evidence-item b{display:block;color:var(--ink);font-size:13px}.evidence-item span{display:block;color:var(--muted);margin-top:3px}
.impact-context{margin-bottom:12px!important}
.impact-groups{display:grid;gap:10px}
.impact-task{padding:13px;background:var(--paper2);border:1px solid var(--line2);border-radius:13px}
.impact-task-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.impact-task h3{font:700 14px/1.45 var(--body);margin:0}
.impact-rel-tag{flex:none;color:var(--harbor);background:var(--harbor-soft);border-radius:99px;padding:3px 8px;font-size:10px;font-weight:700;line-height:1.5}
.impact-measure-line,.impact-model-line{margin-top:5px;color:var(--muted);font-size:10px;line-height:1.45;overflow-wrap:anywhere}
.impact-model-line{color:var(--ink2)}
.impact-skills{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.impact-skill{display:inline-flex;max-width:100%;padding:4px 9px;border:1px solid var(--line);border-radius:99px;background:var(--paper);font-size:11px;line-height:1.45;color:var(--ink2)}
.impact-skills-label{margin-top:9px;color:var(--muted);font-size:10px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.impact-more-skills{align-self:center;color:var(--muted);font-size:10px}
.impact-evidence{margin-top:10px;border-top:1px solid var(--line2);padding-top:8px}
.impact-evidence summary{cursor:pointer;color:var(--harbor);font-size:11px;font-weight:700;list-style:none}
.impact-evidence summary::-webkit-details-marker{display:none}
.impact-evidence summary:after{content:" +";color:var(--muted)}
.impact-evidence[open] summary:after{content:" −"}
.impact-evidence-body{padding-top:8px;font-size:11px}
.impact-meta-row{display:grid;grid-template-columns:94px minmax(0,1fr);gap:8px;padding:4px 0;border-bottom:1px solid var(--line2);overflow-wrap:anywhere}
.impact-meta-row b{color:var(--muted);font-weight:600}
.impact-candidates{margin:8px 0 0;padding-left:18px}
.impact-candidates li{margin:4px 0;overflow-wrap:anywhere}
.impact-source{display:inline-block;margin-top:8px;font-weight:700}
.skills-groups{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:18px}
.skills-groups h3{font-family:var(--body);font-size:14px;font-weight:700;margin:0 0 8px}
.skill-list{margin:0;padding:0;list-style:none;display:grid;gap:6px}
.skill-list li{padding:7px 9px;background:var(--paper2);border-radius:8px;font-size:12px;color:var(--ink2)}
.empty{text-align:center;padding:50px 20px}.empty h2{font-size:23px;margin-bottom:7px}.empty p{color:var(--muted);max-width:470px;margin:0 auto 17px;font-size:14px}
.caveat{margin:22px 0;background:var(--amber-soft);color:#7a4f14;border-radius:13px;padding:13px 16px;font-size:13px;line-height:1.6}
@media(max-width:850px){.insights{grid-template-columns:1fr}.insight{min-height:0}.skills-groups{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.phead{padding-top:30px}.insight{padding:18px}.skills-groups{grid-template-columns:1fr}.impact-task-head{display:grid}.impact-rel-tag{justify-self:start}.impact-meta-row{grid-template-columns:1fr;gap:1px}}
'''

CAREER_BODY = r'''
<main class="wrap">
<section class="phead"><div class="eyebrow reveal">Career explorer</div><h1 id="occupation-title" class="reveal" data-d="60">Explore a career</h1><p id="occupation-intro" class="lead reveal" data-d="120">Choose a job title to see available evidence.</p><div id="occupation-meta" class="occupation-meta" hidden></div><details id="occupation-details" class="occupation-details" hidden><summary>About this career</summary><p id="occupation-description" class="desc"></p></details></section>
 <div id="loading" class="load" aria-label="Loading career insights" hidden><div class="skel skeleton-card"></div><div class="skel skeleton-card"></div><div class="skel skeleton-card"></div></div>
<div id="error" class="errbox" role="alert" hidden><span id="errmsg"></span><button class="btn btn-ghost btn-sm" type="button" id="retry">Try again</button></div>
 <section id="empty" class="card empty"><h2>Select a career to begin</h2><p>Start with a job title.</p><a class="btn btn-primary" href="/">Search jobs <span class="arrow">&rarr;</span></a></section>
<section id="occupation-results" aria-live="polite" hidden>
 <div class="insights">
  <article class="card insight"><div class="insight-head"><h2>AI Impact</h2><span id="ai-status" class="chip c-flat">Evidence pending</span></div><div id="ai-content" class="insight-body"></div><details class="ev"><summary>Why?</summary><div id="ai-why" class="evbody"></div></details></article>
  <article class="card insight"><div class="insight-head"><h2>Job Demand</h2><span id="demand-status" class="chip c-flat">Evidence pending</span></div><div id="demand-content" class="insight-body"></div><details class="ev"><summary>Why?</summary><div id="demand-why" class="evbody"></div></details></article>
   <article class="card insight"><div class="insight-head"><h2>Skills to Learn</h2><span id="skills-status" class="chip c-flat">General guidance</span></div><div id="skills-content" class="insight-body"></div><details class="ev"><summary>Why?</summary><div id="skills-why" class="evbody"></div></details></article>
 </div>
  <div class="caveat">These signals describe available evidence, not an individual forecast.</div>
</section>
</main>
'''

CAREER_JS = r'''
(()=>{'use strict';
const $=id=>document.getElementById(id);
const loading=$('loading'),empty=$('empty'),results=$('occupation-results'),error=$('error');
let occupationUri=new URLSearchParams(location.search).get('occupation_uri')||'';
function node(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n}
function showError(message){loading.hidden=true;error.hidden=false;$('errmsg').textContent=message;empty.hidden=true}
function appendSkillList(target,rows,emptyText,limit=5){target.replaceChildren();if(!Array.isArray(rows)||!rows.length){target.appendChild(node('li','',emptyText));return}
 rows.slice(0,limit).forEach(skill=>target.appendChild(node('li','',skill.label||'')));
 if(rows.length>limit)target.appendChild(node('li','skill-more',(rows.length-limit)+' more in “Why?”'))}
function statusChip(id,label,tone){const n=$(id);n.textContent=label;n.className='chip '+tone}
function legacyTaskGroups(links){const grouped=new Map();(Array.isArray(links)?links:[]).forEach(link=>{
 const key=JSON.stringify([link.source||'',link.benchmark||'',link.benchmark_version||'',link.task||'']);
 let group=grouped.get(key);if(!group){group={...link,skills:[],relationship_type:'semantic_candidate',independently_verified:false};grouped.set(key,group)}
 group.skills.push({skill:link.skill,skill_uri:link.skill_uri,relation:link.relation,similarity:link.similarity,relationship_type:'semantic_candidate',independently_verified:false})
 });return Array.from(grouped.values())}
function addImpactMeta(parent,label,value){const row=node('div','impact-meta-row');row.appendChild(node('b','',label));row.appendChild(node('span','',value||'Not recorded'));parent.appendChild(row)}
function renderImpactEvidence(group){
 const details=node('details','impact-evidence');details.appendChild(node('summary','','View Details'));
 const body=node('div','impact-evidence-body');
 addImpactMeta(body,'Benchmark',(group.benchmark||'Not recorded')+(group.benchmark_version?' · '+group.benchmark_version:''));
 if(group.benchmark_task_id)addImpactMeta(body,'Task ID',group.benchmark_task_id);
 addImpactMeta(body,'Source',group.source||'Not recorded');
 addImpactMeta(body,'Evaluated model',group.model||'Not recorded');
 let measurement='Not recorded';
 if(group.score!==undefined&&group.score!==null&&Number.isFinite(Number(group.score))){
  const n=Number(group.score),unit=String(group.score_unit||'');
  measurement=n.toLocaleString(undefined,{maximumFractionDigits:3})+(unit.toLowerCase()==='percent'||unit==='%'?'%':unit?' '+unit:'');
  const direction=group.score_direction==='higher_better'?'higher is better':group.score_direction==='lower_better'?'lower is better':'direction not recorded';
  measurement+=' · '+direction;
 }
 addImpactMeta(body,'Measurement',measurement);
 addImpactMeta(body,group.date_label||'Date',group.date_value||'Not recorded');
 addImpactMeta(body,'Relationship','MiniLM semantic candidate; not independently verified.');
 const candidates=node('ul','impact-candidates');
 (Array.isArray(group.skills)?group.skills:[]).forEach(skill=>{
  const detailsText=(skill.skill||'ESCO skill')+
   (skill.relation?' · ESCO occupation relation: '+skill.relation:'')+
   (skill.similarity==null?'':' · MiniLM relevance: '+String(skill.similarity)+' (not an impact probability)');
  candidates.appendChild(node('li','',detailsText));
 });
 if(candidates.childNodes.length){addImpactMeta(body,'Matched skills','');body.appendChild(candidates)}
 const sourceUrl=group.source_url;
 if(sourceUrl){try{const url=new URL(sourceUrl);if(url.protocol==='https:'||url.protocol==='http:'){const a=node('a','impact-source','Open benchmark source ↗');a.href=url.href;a.target='_blank';a.rel='noopener noreferrer';body.appendChild(a)}}catch(e){}}
 details.appendChild(body);return details
}
function renderImpactTaskGroup(group){
 const card=node('article','impact-task');const head=node('div','impact-task-head');
 head.appendChild(node('h3','',group.task||'Benchmark task description unavailable'));
 head.appendChild(node('span','impact-rel-tag','Possible task relationship'));
 card.appendChild(head);
 card.appendChild(node('div','impact-skills-label','Potential ESCO skills · semantic candidates'));
 const skills=node('div','impact-skills');
 const candidates=Array.isArray(group.skills)?group.skills:[];
 candidates.slice(0,5).forEach(skill=>skills.appendChild(node('span','impact-skill',skill.skill||'ESCO skill candidate')));
 if(candidates.length>5)skills.appendChild(node('span','impact-more-skills','+'+(candidates.length-5)+' more · open evidence'));
 if(skills.childNodes.length)card.appendChild(skills);
 card.appendChild(renderImpactEvidence(group));return card
}
function renderOccupation(data){const occ=data.occupation||{},ai=data.ai_impact||{},demand=data.job_demand||{},future=data.future_skills||{},skills=data.skills||{};
 $('occupation-title').textContent=occ.label||'Career overview';document.title='FutureTwin AI · '+(occ.label||'Career');
  $('occupation-intro').textContent='A quick view of available evidence.';
 const meta=$('occupation-meta');meta.replaceChildren();if(occ.isco_group_label)meta.appendChild(node('span','group-tag',occ.isco_group_label));meta.hidden=!meta.childNodes.length;
 const desc=$('occupation-description');desc.textContent=occ.description||'';$('occupation-details').hidden=!occ.description;
 const aiBox=$('ai-content'),aiWhy=$('ai-why');aiBox.replaceChildren();aiWhy.replaceChildren();
   aiWhy.appendChild(node('p','',ai.note||'AI evidence is not available for this occupation.'));
   if(ai.status==='possible_links'){statusChip('ai-status','Current baseline','c-obs');
  aiBox.appendChild(node('p','impact-context','Current benchmark results, not newly detected advances. New advances are tracked separately in AI Trends.'));
  const groups=Array.isArray(ai.task_groups)?ai.task_groups:legacyTaskGroups(ai.links);
  const list=node('div','impact-groups');
  groups.forEach(group=>list.appendChild(renderImpactTaskGroup(group)));
  if(groups.length)aiBox.appendChild(list);else aiBox.appendChild(node('p','','Benchmark records are available, but no task groups could be displayed.'))}
 else if(ai.status==='unavailable'){statusChip('ai-status','Unavailable','c-warn');aiBox.appendChild(node('p','','AI impact evidence could not be loaded for this occupation.'))}
  else{statusChip('ai-status','Not enough data','c-flat');aiBox.appendChild(node('p','','Not enough evidence to assess AI impact.'))}
  const db=$('demand-content'),dw=$('demand-why');db.replaceChildren();dw.textContent=demand.note||'Employment context is not available.';
  if(demand.status==='broad_context'){statusChip('demand-status','Broad context','c-obs');const p=node('p','',demand.group?demand.group+' employment changed '+(demand.employment_change_pct==null?'':String(demand.employment_change_pct)+'%')+'.':'Broad employment data is available.');db.appendChild(p);db.appendChild(node('p','note-line','Group-level change, not job openings.'+(demand.latest_date?' Latest period: '+demand.latest_date+'.':'')))}
 else if(demand.status==='unavailable'){statusChip('demand-status','Unavailable','c-warn');db.appendChild(node('p','','Broad employment context could not be loaded.'))}
 else{statusChip('demand-status','Not enough data','c-flat');db.appendChild(node('p','',demand.note||'No recent broad-group employment figure is available.'))}
  statusChip('skills-status','General guidance','c-up');const sb=$('skills-content');sb.replaceChildren();sb.appendChild(node('p','','Common skills for this job—not a personal skills-gap analysis.'));
 const groups=node('div','skills-groups');const essential=node('section'),optional=node('section');essential.appendChild(node('h3','','Essential skills'));optional.appendChild(node('h3','','Optional skills'));const elist=node('ul','skill-list'),olist=node('ul','skill-list');appendSkillList(elist,skills.essential,'No essential skills listed.');appendSkillList(olist,skills.optional,'No optional skills listed.');essential.appendChild(elist);optional.appendChild(olist);groups.appendChild(essential);groups.appendChild(optional);sb.appendChild(groups);
   const why=$('skills-why');why.replaceChildren();why.appendChild(node('p','',future.note||'These are general career references, not a personal assessment.'));
  [['essential','Essential skills'],['optional','Optional skills']].forEach(([key,title])=>{const section=node('section');section.appendChild(node('b','',title));const ul=node('ul');(skills[key]||[]).forEach(skill=>ul.appendChild(node('li','',skill.label||'')));section.appendChild(ul);why.appendChild(section)});
 loading.hidden=true;error.hidden=true;empty.hidden=true;results.hidden=false}
async function loadOccupation(){if(!occupationUri){loading.hidden=true;error.hidden=true;results.hidden=true;empty.hidden=false;return}
 loading.hidden=false;error.hidden=true;empty.hidden=true;results.hidden=true;
 try{const response=await fetch('/api/occupations/explore?uri='+encodeURIComponent(occupationUri),{headers:{'Accept':'application/json'}});if(!response.ok)throw new Error();const data=await response.json();if(!data||!data.occupation)throw new Error();renderOccupation(data)}
 catch(e){showError('We could not load this occupation right now. Please try again or search for another title.')}}
 $('retry').addEventListener('click',loadOccupation);
loadOccupation();
})();
'''

# Find a Career / career detail (redesigned). The legacy explorer constants above
# stay for compatibility; the impact-task renderers are reused from them.
_ci0 = CAREER_JS.index("function legacyTaskGroups")
_ci1 = CAREER_JS.index("\nfunction ", CAREER_JS.index("function renderImpactTaskGroup") + 10)
_IMPACT_JS = CAREER_JS[_ci0:_ci1]
CAREER_HTML = _page(
    "Find a Career - FutureTwin AI", "explore", CAREER_NEW_CSS + _PG_CSS + EXPOSURE_CSS, CAREER_NEW_BODY,
    CAREER_NEW_JS.replace("/*__IMPACT__*/", _IMPACT_JS + EXPOSURE_JS).replace("/*__MAP__*/", CAREER_MAP_JS),
)


# ---------------------------------------------------------------- TRENDS
TRENDS_CSS = r'''
.phead{padding:22px 0 4px!important;display:block!important}.phead h1{font-size:28px!important;margin:0!important}
.tsec-head .chip,.capability-description{display:none!important}
details.tsec{padding:14px 18px!important;margin-top:14px}details.tsec>summary{font-size:15px}.toc{display:none!important}
.tsec{padding-top:22px!important}.toc{background:#f2f5f9ee!important;top:58px!important}
.phead{padding:52px 0 18px;display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:end}
.phead h1{font-size:clamp(34px,4.4vw,52px);line-height:1.06;margin:10px 0 12px}
.legend{padding:20px 22px;display:grid;gap:12px;font-size:14px;color:var(--ink2)}
.legend div{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:start}
.toc{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 8px;position:sticky;top:68px;z-index:5;background:#f5f2eaee;padding:10px 0;backdrop-filter:blur(8px)}
.toc a{text-decoration:none;font-size:13px;font-weight:600;color:var(--ink2);border:1px solid var(--line);background:var(--paper);padding:7px 13px;border-radius:99px;transition:all .2s}
.toc a:hover{border-color:var(--harbor);color:var(--harbor)}
.tsec{padding:44px 0 10px;scroll-margin-top:130px}
.tsec-head{display:flex;justify-content:space-between;align-items:end;gap:20px;flex-wrap:wrap;margin-bottom:20px}
.tsec-head h2{font-size:clamp(26px,3vw,36px);line-height:1.12;margin:8px 0 6px}
.tsec-head p{margin:0;color:var(--muted);max-width:620px}
.callout{padding:18px 20px;border-radius:16px;font-size:15px;display:flex;gap:14px;align-items:flex-start;margin-bottom:18px;background:var(--harbor-soft);color:var(--harbor2)}
.callout b{display:block}
.callout .dot{flex:0 0 10px;height:10px;border-radius:50%;background:var(--harbor);margin-top:7px}
.caps{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}
.cap{text-align:left;padding:18px;border:1px solid var(--line);background:var(--paper);border-radius:16px;transition:transform .25s,border-color .25s,box-shadow .25s;color:var(--ink);display:flex;flex-direction:column;gap:10px}
.cap:hover{transform:translateY(-2px);border-color:#cfc5b0;box-shadow:var(--shadow)}
.cap.active{border-color:var(--harbor);box-shadow:0 0 0 3px var(--harbor-soft)}
.cap-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.cap h3{font-family:var(--body);font-size:16px;font-weight:700;letter-spacing:-.01em}
.score{font-family:var(--display);font-size:30px;line-height:1}
.score small{font-family:var(--body);font-size:12px;color:var(--muted);margin-left:4px}
.bar{height:6px;background:#ece6d8;border-radius:99px;overflow:hidden}.bar i{display:block;height:100%;background:var(--harbor);border-radius:99px;transform-origin:left;animation:grow 1s cubic-bezier(.2,.7,.2,1) both}
@keyframes grow{from{transform:scaleX(0)}}
.cap .sm{font-size:12.5px;color:var(--muted)}
.detail{margin-top:18px;padding:26px}
.detail h3{font-size:24px;margin-bottom:6px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:18px}
.list{display:grid;gap:10px}
.item{border:1px solid var(--line2);background:var(--paper2);border-radius:14px;padding:14px 16px}
.item-top{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}
.item-top b{font-size:15px}
.item p{margin:6px 0 0;font-size:13.5px;color:var(--ink2)}
.honest-empty{border:1px dashed #cfc5b0;border-radius:16px;padding:22px;background:var(--paper2);color:var(--ink2)}
.honest-empty b{display:block;font-family:var(--display);font-weight:500;font-size:20px;color:var(--ink);margin-bottom:6px}
.advance-note{margin:0 0 10px;padding:10px 13px;background:var(--paper2);border:1px solid var(--line);border-radius:11px;color:var(--ink2);font-size:12px;line-height:1.55}
.baseline-domain{display:flex;flex-direction:column;gap:9px}
.baseline-domain h3{font:700 14px/1.4 var(--body)}
.baseline-count,.baseline-meta{font-size:11px;color:var(--muted);line-height:1.5}
.baseline-result{padding:11px 12px;border:1px solid var(--line2);background:var(--paper2);border-radius:11px}
.baseline-result b{display:block;font-size:12px}
.baseline-result p{margin:5px 0 0;font-size:11px;line-height:1.5;color:var(--ink2);overflow-wrap:anywhere}
.baseline-task{color:var(--muted)!important}
.baseline-source{display:inline-block;margin-top:6px;font-size:11px;font-weight:700}
.baseline-series-list{display:grid;gap:8px;margin-top:12px}
.baseline-series-item{padding:10px 12px;border:1px solid var(--line2);border-radius:10px;background:var(--paper2)}
.baseline-series-item summary{cursor:pointer;color:var(--ink2);font-size:12px;font-weight:700}
.baseline-series-details{padding-top:8px;font-size:11px}
.baseline-history{margin:8px 0 0;padding-left:18px;color:var(--ink2)}
.baseline-history li{padding:3px 0}
.baseline-history-note{margin:8px 0 0;color:var(--muted);font-size:10px}
.baseline-record-group{margin-top:14px}
.baseline-record-group h3{font:700 13px/1.4 var(--body);margin-bottom:7px}
.capability-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.capability-card{border:1px solid var(--line);border-radius:16px;background:var(--paper);padding:18px;display:flex;flex-direction:column;min-width:0;transition:border-color .2s,box-shadow .2s}
.capability-card:hover{border-color:#cfc5b0;box-shadow:var(--shadow)}
.capability-card[hidden],.capability-details[hidden],.capability-show-more[hidden]{display:none!important}
.capability-card-head{display:flex;align-items:center;gap:12px}
.capability-icon{width:42px;height:42px;border-radius:13px;display:grid;place-items:center;flex:0 0 42px;background:var(--harbor-soft);color:var(--harbor);font-size:20px;font-weight:700}
.capability-card h3{margin:0;font:700 16px/1.3 var(--body);letter-spacing:-.02em}
.capability-description{margin:12px 0 14px;color:var(--ink2);font-size:13px;line-height:1.55;min-height:40px}
.capability-explore{margin-top:auto;align-self:flex-start;display:inline-flex;align-items:center;gap:7px;border:0;border-radius:8px;padding:7px 10px;background:var(--harbor-soft);color:var(--harbor);font:700 12px var(--body);cursor:pointer}
.capability-explore:hover{background:var(--harbor);color:var(--paper)}
.capability-explore:focus-visible,.capability-show-more:focus-visible,.capability-more-examples:focus-visible{outline:3px solid #8db4d0;outline-offset:2px}
.capability-details{margin-top:14px;padding-top:14px;border-top:1px solid var(--line2)}
.capability-details h4{margin:0 0 8px;font:700 12px var(--body);color:var(--ink)}
.capability-example-list{display:grid}
.capability-task{display:grid;grid-template-columns:30px minmax(0,1fr);gap:11px;padding:12px 0;border-bottom:1px solid var(--line2)}
.capability-task-mark{width:28px;height:28px;display:grid;place-items:center;border:1px solid var(--line);border-radius:9px;background:var(--paper);color:var(--harbor);font-size:10px;font-weight:700}
.capability-task-copy{min-width:0}
.capability-task-copy h5{margin:0;color:var(--ink);font:700 12px/1.4 var(--body)}
.capability-task-copy>p{margin:4px 0 0;color:var(--ink2);font-size:11px;line-height:1.5}
.capability-task-research{margin-top:8px}
.capability-task-research>summary,.research-history>summary{cursor:pointer;color:var(--harbor);font-size:11px;font-weight:700;list-style:none}
.capability-task-research>summary::-webkit-details-marker,.research-history>summary::-webkit-details-marker{display:none}
.capability-task-research>summary:after{content:"＋";margin-left:5px}
.capability-task-research[open]>summary:after{content:"−"}
.capability-task-evidence{margin-top:8px;padding:10px;border:1px solid var(--line2);border-radius:10px;background:var(--paper2)}
.research-original{margin:0 0 10px;color:var(--ink2);font-size:11px;line-height:1.5}
.research-original b{display:block;margin-bottom:3px;color:var(--ink);font-size:10px}
.research-record{padding:9px 0;border-top:1px solid var(--line)}
.research-record h5{margin:0 0 7px;color:var(--ink);font:700 11px/1.4 var(--body)}
.research-fields{display:grid;grid-template-columns:minmax(105px,.7fr) minmax(0,1.3fr);gap:5px 10px;margin:0;font-size:10px;line-height:1.45}
.research-fields div{display:contents}
.research-fields dt{color:var(--muted)}
.research-fields dd{margin:0;color:var(--ink2);overflow-wrap:anywhere}
.research-history{margin-top:8px}
.research-history ul{display:grid;gap:5px;margin:7px 0 0;padding:0;list-style:none;font-size:10px}
.research-history li{display:flex;justify-content:space-between;gap:10px;color:var(--ink2)}
.research-caveat,.research-unavailable{margin:8px 0 0;color:var(--muted);font-size:10px;line-height:1.45}
.capability-tech{margin-top:7px}
.capability-tech summary{cursor:pointer;color:var(--harbor);font-size:11px;font-weight:700}
.capability-more-examples{display:block;margin:12px auto 0;border:1px solid var(--line);border-radius:99px;background:var(--paper);color:var(--harbor);font:700 11px var(--body);padding:7px 13px;cursor:pointer}
.capability-more-examples:hover{border-color:var(--harbor);background:var(--harbor-soft)}
.capability-show-more{display:block;margin:16px auto 0;border:1px solid var(--line);border-radius:99px;background:var(--paper);color:var(--harbor);font:700 13px var(--body);padding:9px 17px;cursor:pointer}
.capability-show-more:hover{border-color:var(--harbor);background:var(--harbor-soft)}
.latest-advances{margin-top:26px;padding:17px 19px;border:1px solid var(--line);border-radius:15px;background:var(--paper)}
.latest-advances h3{margin:0 0 5px;font:700 16px var(--body)}
.latest-advances>p{margin:0 0 10px;color:var(--muted);font-size:12px}
.benchmark-tracking{display:grid;grid-template-columns:minmax(200px,1fr) auto;align-items:center;gap:18px;margin:14px 0;padding:14px 16px;border:1px solid #c7d8e5;border-radius:13px;background:linear-gradient(110deg,#edf5fa,#f8fbfd)}
.benchmark-tracking-lead{display:flex;align-items:center;gap:11px;min-width:0}
.benchmark-tracking-icon{width:36px;height:36px;flex:0 0 36px;display:grid;place-items:center;border-radius:11px;background:var(--harbor);color:white;font-size:18px;font-weight:800}
.benchmark-tracking-lead strong{display:block;color:var(--ink);font:700 14px var(--body)}
.benchmark-tracking-lead p{margin:3px 0 0;color:var(--muted);font-size:11px;line-height:1.4}
.benchmark-tracking-stats{display:grid;grid-template-columns:repeat(3,minmax(82px,auto));gap:16px}
.benchmark-tracking-stats>div{min-width:0}
.benchmark-tracking-stats strong{display:block;color:var(--ink);font:700 18px var(--body);white-space:nowrap}
.benchmark-tracking-stats span{display:block;margin-top:3px;color:var(--muted);font-size:10px;line-height:1.35}
@media(max-width:700px){.benchmark-tracking{grid-template-columns:1fr}.benchmark-tracking-stats{justify-content:space-between}}
@media(max-width:420px){.benchmark-tracking-stats{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}
.benchmark-evidence{margin-top:16px}
.benchmark-evidence>summary{cursor:pointer;font-weight:700;color:var(--ink2)}
.benchmark-evidence[open]>summary{margin-bottom:12px}
.benchmark-evidence .evidence-note{font-size:12px;color:var(--muted);line-height:1.5}
.bench{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.bench button{border:1px solid var(--line);background:var(--paper);border-radius:99px;padding:8px 14px;font-size:13px;font-weight:600;color:var(--ink2);transition:all .2s}
.bench button:hover{border-color:var(--harbor)}
.bench button.active{background:var(--harbor);color:#fbf8f1;border-color:var(--harbor)}
.skills{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.cl-potential_automation_exposure{color:var(--clay);background:var(--clay-soft)}.cl-ai_augmentation_opportunity{color:var(--sage);background:var(--sage-soft)}.cl-complementary_or_emerging{color:var(--plum);background:var(--plum-soft)}.cl-unknown_impact{color:var(--muted);background:#eeeae0}
.pad{padding:24px}
@media(max-width:900px){.phead,.cols,.skills{grid-template-columns:1fr}.toc{top:68px}}
@media(max-width:900px){.capability-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.phead{grid-template-columns:1fr;padding:34px 0 10px}.phead h1{font-family:var(--body);font-weight:700;letter-spacing:-.05em}
.tsec{padding:28px 0 8px}.tsec-head h2{font-family:var(--body);font-size:24px;font-weight:700;letter-spacing:-.035em}
.tsec-head p{font-size:14px}.toc{position:static;margin:14px 0 0}
@media(max-width:600px){.toc a{font-size:12px;padding:6px 10px}}
@media(max-width:560px){.capability-grid{grid-template-columns:1fr}.capability-card{padding:16px}.capability-description{min-height:0}}
@media(max-width:560px){.research-fields{grid-template-columns:92px minmax(0,1fr)}}
'''

TRENDS_BODY = r'''
<main class="wrap">
<section class="phead">
  <div><h1>AI Trends</h1></div>
</section>


<section class="tsec" id="ai">
  <div class="tsec-head"><div><h2>Current AI Capabilities</h2></div></div>
  <div id="capability-grid" class="capability-grid" aria-live="polite"><div class="skel" style="height:160px"></div><div class="skel" style="height:160px"></div><div class="skel" style="height:160px"></div></div>
  <button id="capability-show-more" class="capability-show-more" type="button" hidden>Show More</button>
  <section class="latest-advances" aria-labelledby="latest-advances-title">
    <h3 id="latest-advances-title">Latest AI Advances</h3>
    <p>Improvements from comparable benchmark snapshots only.</p>
    <div class="benchmark-tracking" id="benchmark-tracking" role="status" aria-live="polite">
      <div class="benchmark-tracking-lead">
        <span class="benchmark-tracking-icon" aria-hidden="true">↗</span>
        <div>
          <strong>FutureTwin tracks AI model benchmarks</strong>
          <p id="benchmark-tracking-note">Checking stored benchmark coverage…</p>
        </div>
      </div>
      <div class="benchmark-tracking-stats">
        <div><strong id="tracked-benchmark-count">—</strong><span>benchmark sets</span></div>
        <div><strong id="tracked-model-count">—</strong><span>AI models</span></div>
        <div><strong id="latest-benchmark-collected">—</strong><span>latest result collected</span></div>
      </div>
    </div>
    <div id="ai-callout" aria-live="polite"><p class="advance-note">Checking comparable benchmark snapshots…</p></div>
    <div id="caps" class="caps"></div>
    <details class="ev card pad benchmark-evidence" id="benchmark-evidence" aria-labelledby="latest-advances-title benchmark-evidence-label">
      <summary id="benchmark-evidence-label">Research details for Latest AI Advances</summary>
      <div class="evbody">
        <p class="evidence-note">Source measurements and historical records are shown as stored. Results are not compared across different benchmarks, versions, tasks, score units or directions.</p>
        <div id="baseline-summary" class="muted">Loading benchmark coverage...</div>
        <div id="baseline-series"></div>
        <details class="ev" style="margin-top:18px" id="frontier-wrap"><summary>Recent record-breaking results</summary><div class="evbody" id="frontier"><p class="muted">Loading...</p></div></details>
      </div>
    </details>
  </section>
  <div id="advancement-impact" hidden>
    <div id="cap-detail"></div>
    <div class="tsec-head" style="margin-top:22px"><div><span class="chip c-pos">Possible links</span><h2>Related occupations</h2></div></div>
    <div id="occlist"></div>
  </div>
</section>

<details class="tsec ev card pad" id="skills"><summary>Skills Related to AI Capabilities</summary><div class="evbody"><div class="bench" id="bench"><div class="skel" style="height:36px;width:320px"></div></div>
  <div id="skilllist" class="skills"></div>
</div></details>

</main>
'''

TRENDS_JS = r'''
(()=>{'use strict';
const $=id=>document.getElementById(id);
function el(t,c,x){const n=document.createElement(t);if(c)n.className=c;if(x!==undefined&&x!==null)n.textContent=String(x);return n}
function add(p,c){p.appendChild(c);return c}
async function getJSON(u){const r=await fetch(u);let d;try{d=await r.json()}catch{throw new Error('Unexpected server response')}if(!r.ok)throw new Error(d&&d.error||('HTTP '+r.status));return d}
function errBox(target,msg,retry){target.replaceChildren();const b=add(target,el('div','errbox'));add(b,el('span','',msg));const btn=add(b,el('button','btn btn-ghost btn-sm','Try again'));btn.type='button';btn.onclick=retry}
function fmt(n,d){n=Number(n);return Number.isFinite(n)?n.toFixed(d==null?1:d):'n/a'}
function ev(parent,title){const d=add(parent,el('details','ev'));add(d,el('summary','',title));return add(d,el('div','evbody'))}
function table(parent,heads,rows){const t=add(parent,el('table'));const h=add(add(t,el('thead')),el('tr'));heads.forEach(x=>add(h,el('th','',x)));const b=add(t,el('tbody'));rows.forEach(r=>{const tr=add(b,el('tr'));r.forEach(c=>add(tr,el('td','num',c)))});return t}

/* ---- Current benchmark evidence, independent of latest snapshot changes ---- */
const FEATURED_CAPABILITIES=['Coding','Reasoning','Mathematics','Data Analysis','Language'];
const CAPABILITY_ICONS={
 coding:'</>',reasoning:'◎',mathematics:'∑','data analysis':'▥',
 language:'Aa','instruction following':'✓',economics:'↗',strategy:'◇',
 legal:'§',finance:'$',engineering:'⚙',agentic:'↗',healthcare:'＋'
};
let capabilityCards=[],capabilityGroups=[],showAllCapabilities=false,advancementDataPromise=null;
let baselineEvidenceRows=[];
function iconForCapability(name){return CAPABILITY_ICONS[String(name||'').toLowerCase()]||'✦'}
function capabilityDescription(records){
 const described=(records||[]).filter(r=>String(r.task_text||'').trim());
 if(!described.length)return 'Task descriptions are not available yet.';
 const broad=described.find(r=>String(r.source||'').toLowerCase()==='artificial_analysis'&&/index/i.test(r.benchmark_name||''));
  return capabilityTaskCopy((broad||described[0]).task_text,(broad||described[0]).domain).description;
}
function getAdvancementData(){
 if(!advancementDataPromise)advancementDataPromise=getJSON('/api/advancements').catch(error=>{advancementDataPromise=null;throw error});
 return advancementDataPromise;
}
const TASK_COPY_RULES=[
 {match:/Solve programming problems: write, complete, debug and explain/i,title:'Solve coding challenges',description:'AI is tested on writing, finishing, fixing, or explaining code.'},
 {match:/Complete partial source code/i,title:'Finish incomplete code',description:'AI completes missing code and checks whether it passes tests.'},
 {match:/Generate correct programs from problem statements/i,title:'Write code from a prompt',description:'AI writes a program to solve a problem within a time limit.'},
 {match:/Write and repair JavaScript code/i,title:'Repair JavaScript code',description:'AI works through several steps to write and fix JavaScript.'},
 {match:/Write and repair Python code/i,title:'Repair Python code',description:'AI works through several steps to write and fix Python.'},
 {match:/Write and repair TypeScript code/i,title:'Repair TypeScript code',description:'AI works through several steps to write and fix TypeScript.'},
 {match:/Resolve GitHub issues that include screenshots or other visual artifacts/i,title:'Fix an issue using screenshots',description:'AI uses screenshots and code changes to help address a software issue.'},
 {match:/Resolve GitHub issues in the SWE-bench test split/i,title:'Fix a software issue',description:'AI creates a code change to fix an issue in a software project.'},
 {match:/Resolve real, human-validated GitHub issues/i,title:'Find and fix a code defect',description:'AI reads an issue, finds the problem in a codebase, and proposes a patch.'},
 {match:/Resolve real GitHub issues \(lite subset\).*open-source Python repositories/i,title:'Patch Python project issues',description:'AI generates code patches for real issues in open-source Python projects.'},
 {match:/Resolve real GitHub issues across multiple programming languages/i,title:'Patch issues across languages',description:'AI generates code patches for real project issues in several languages.'},
 {match:/Resolve real GitHub issues/i,title:'Fix a real code issue',description:'AI makes code changes to address an issue in a software project.'},
 {match:/logic grid.*puzzles|zebra.*puzzles/i,title:'Solve a logic puzzle',description:'AI uses clues to work out a grid-based puzzle.'},
 {match:/spatial reasoning problems/i,title:'Solve a spatial problem',description:'AI answers questions about spatial relationships.'},
 {match:/beliefs and intentions of others/i,title:'Understand what people think',description:'AI answers questions about other people’s beliefs and intentions.'},
 {match:/logical instructions involving navigation/i,title:'Follow directions',description:'AI follows a sequence of navigation instructions.'},
 {match:/competition-style mathematics|mathematics competition problems/i,title:'Solve a math problem',description:'AI works through advanced mathematics questions.'},
 {match:/olympiad-level mathematics.*proof/i,title:'Work through a math proof',description:'AI solves a multi-step mathematics problem that requires a proof.'},
 {match:/Compute integrals and solve quantitative puzzles/i,title:'Solve calculations and puzzles',description:'AI solves integration questions and quantitative puzzles.'},
 {match:/Join and reconcile data tables/i,title:'Work with data tables',description:'AI combines information in tables to answer questions.'},
 {match:/Reformat and transform tabular data/i,title:'Reshape table data',description:'AI changes the format of tabular data accurately.'},
 {match:/sequences of events in structured data/i,title:'Follow events in data',description:'AI reasons about the order of events in structured data.'},
 {match:/latent connections between words or concepts/i,title:'Connect related words',description:'AI finds links between words or ideas.'},
 {match:/scrambled plot or logic statements/i,title:'Put statements in order',description:'AI rebuilds the order of mixed-up story or logic statements.'},
 {match:/typographical errors/i,title:'Spot writing mistakes',description:'AI finds and corrects typos in text.'},
 {match:/Paraphrase text while preserving meaning/i,title:'Rewrite without changing meaning',description:'AI rephrases text while keeping its meaning.'},
 {match:/Simplify text while preserving meaning/i,title:'Make text easier to understand',description:'AI simplifies writing without losing its meaning.'},
 {match:/Write coherent stories following constraints/i,title:'Follow story instructions',description:'AI writes stories that meet a set of rules.'},
 {match:/Summarize documents accurately/i,title:'Summarize a document',description:'AI condenses a document while keeping its meaning.'},
 {match:/economics questions, interpret economic indicators/i,title:'Understand economic information',description:'AI answers economics questions and interprets indicators, markets, or policy.'},
 {match:/engineering problems, analyze technical systems/i,title:'Solve engineering problems',description:'AI answers engineering questions and evaluates designs.'},
 {match:/medical questions, interpret clinical information/i,title:'Answer health questions',description:'AI interprets clinical information and reasons about diagnoses or treatments.'},
 {match:/financial statements, apply accounting standards/i,title:'Work with financial statements',description:'AI analyzes financial reports and interprets financial information.'},
 {match:/Plan and execute multi-step tasks using digital tools/i,title:'Complete multi-step tasks',description:'AI plans and uses digital tools to finish a sequence of tasks.'},
 {match:/legal documents, apply statutes and case law/i,title:'Review legal questions',description:'AI reads legal materials and builds a legal argument.'},
 {match:/business operations, develop strategies/i,title:'Plan business decisions',description:'AI analyzes operations and develops strategies.'}
];
function capabilityTaskCopy(taskText){
 const text=String(taskText||'').replace(/\s+/g,' ').trim();
 const match=TASK_COPY_RULES.find(rule=>rule.match.test(text));
 return match?{title:match.title,description:match.description}:
  {title:'Benchmark task',description:'A plain-language summary is not available yet. Open the research evidence to see the original task.'};
}
function groupCapabilityTasks(records){
 const grouped=new Map();
 (records||[]).forEach(record=>{
  const original=String(record.task_text||'').replace(/\s+/g,' ').trim();
  if(!original)return;
  const key=original.normalize('NFKC').toLocaleLowerCase();
  if(!grouped.has(key))grouped.set(key,{taskText:original,records:[]});
  grouped.get(key).records.push(record);
 });
 return Array.from(grouped.values()).map(task=>({...task,...capabilityTaskCopy(task.taskText)}));
}
function researchDate(record){
 const evaluation=record.evaluation_date||(record.date_label==='Evaluation date'?record.date_value:'');
 if(evaluation)return 'Evaluation date: '+evaluation;
 const collected=record.collected_at||(record.date_label==='Record collected'?record.date_value:'');
 if(collected)return formatBaselineDate('Record collected',collected);
 return 'Date not recorded';
}
function appendResearchHistory(parent,record){
 const history=Array.isArray(record.history)?record.history:[];
 if(!history.length)return;
 const details=add(parent,el('details','research-history'));
 add(details,el('summary','', 'Other stored model results in this series ('+history.length+')'));
 const list=add(details,el('ul'));
 history.forEach(item=>{
  const row=add(list,el('li'));
  const date=researchDate(item);
  add(row,el('span','',(item.model_name||'Model not recorded')+' · '+(date!=='Date not recorded'?date:'')));
  add(row,el('b','',baselineScore(item)));
  appendTechnicalMetadata(row,item);
 });
 add(details,el('p','baseline-history-note','These results share the same source, benchmark version, task, unit and score direction.'));
}
function renderTaskResearch(target,task){
 target.replaceChildren();
 const original=add(target,el('p','research-original'));
 add(original,el('b','', 'Original task wording'));
 add(original,el('span','',task.taskText));
 task.records.forEach(record=>{
  const section=add(target,el('section','research-record'));
  const title=(record.benchmark_name||'Benchmark')+(record.benchmark_version?' · '+record.benchmark_version:'');
  add(section,el('h5','',title));
  const fields=add(section,el('dl','research-fields'));
  const pair=(label,value)=>{const line=add(fields,el('div'));add(line,el('dt','',label));add(line,el('dd','',value||'Not recorded'))};
  const explanation=[record.metric_explanation,record.metric_definition,record.score_definition,record.measurement_description].find(value=>String(value||'').trim());
  pair('Benchmark source',baselineSourceName(record.source));
  pair('Evaluated model',record.model_name||'Not recorded');
  pair('Measurement',baselineScore(record));
  pair('Date',researchDate(record));
  pair('Metric explanation',explanation||'Not provided by the source');
  addBaselineSource(section,record);
  appendResearchHistory(section,record);
 });
 add(target,el('p','research-caveat','Scores retain their source units and are not measures of workplace automation or general ability.'));
}
function renderTaskExample(task,index){
 const item=el('article','capability-task');
 const mark=add(item,el('span','capability-task-mark',String(index+1).padStart(2,'0')));
 mark.setAttribute('aria-hidden','true');
 const copy=add(item,el('div','capability-task-copy'));
 add(copy,el('h5','',task.title));
 add(copy,el('p','',task.description));
 const details=add(copy,el('details','capability-task-research'));
 add(details,el('summary','','View research evidence'));
 const evidence=add(details,el('div','capability-task-evidence'));
 details.addEventListener('toggle',()=>{
  if(!details.open||details.dataset.loaded==='true')return;
  details.dataset.loaded='true';
  renderTaskResearch(evidence,task);
 });
 return item;
}
function renderCapabilityDetails(panel,group){
 panel.replaceChildren();
 add(panel,el('h4','','What is AI being tested on?'));
 const examples=groupCapabilityTasks(group.records);
 if(!examples.length){add(panel,el('p','muted','Not enough task data is available for this field.'));return}
 const list=add(panel,el('div','capability-example-list'));
 list.id=panel.id+'-examples';
 const appendBatch=(start,end)=>{
  examples.slice(start,end).forEach((task,index)=>list.appendChild(renderTaskExample(task,start+index)));
 };
 let visible=Math.min(3,examples.length);
 appendBatch(0,visible);
 if(examples.length>visible){
  const more=add(panel,el('button','capability-more-examples','See more examples'));
  more.type='button';more.setAttribute('aria-controls',list.id);
  more.addEventListener('click',()=>{
   const next=Math.min(visible+3,examples.length);
   appendBatch(visible,next);visible=next;
   if(visible>=examples.length)more.hidden=true;
  });
 }
}
function buildCapabilityCard(group,index){
 const card=el('article','capability-card');card.hidden=index>=5&&!showAllCapabilities;
 const head=add(card,el('div','capability-card-head'));
 const icon=add(head,el('span','capability-icon',iconForCapability(group.domain)));icon.setAttribute('aria-hidden','true');
 add(head,el('h3','',group.domain));
 add(card,el('p','capability-description',capabilityDescription(group.records)));
 const panel=add(card,el('div','capability-details'));panel.hidden=true;panel.id='cap-details-'+index;
 const button=add(card,el('button','capability-explore','Explore'));button.type='button';
 button.setAttribute('aria-controls',panel.id);button.setAttribute('aria-expanded','false');
 button.addEventListener('click',()=>{
  const opening=panel.hidden;
  document.querySelectorAll('.capability-details').forEach(item=>{item.hidden=true});
  document.querySelectorAll('.capability-explore[aria-expanded="true"]').forEach(item=>{item.setAttribute('aria-expanded','false');item.textContent='Explore'});
  if(opening){panel.hidden=false;button.setAttribute('aria-expanded','true');button.textContent='Close details';renderCapabilityDetails(panel,group)}
 });
 return card
}
function updateCapabilityVisibility(){
 capabilityCards.forEach((card,index)=>{card.hidden=index>=5&&!showAllCapabilities});
 const button=$('capability-show-more');button.hidden=capabilityCards.length<=5;
 button.textContent=showAllCapabilities?'Show fewer':'Show More';
 button.setAttribute('aria-expanded',String(showAllCapabilities));
}
function baselineScore(record){
 const value=Number(record.score);if(!Number.isFinite(value))return 'Score not recorded';
 const unit=String(record.score_unit||'');
 const amount=value.toLocaleString(undefined,{maximumFractionDigits:4})+
  (unit.toLowerCase()==='percent'||unit==='%'?'%':unit?' '+unit:'');
 const direction=record.score_direction==='higher_better'?' · higher is better':
  record.score_direction==='lower_better'?' · lower is better':'';
 return amount+direction;
}
function formatBaselineDate(label,value){
 if(label==='Record collected'){
  const parsed=new Date(value);
  if(!Number.isNaN(parsed.getTime()))return 'Record collected (UTC): '+parsed.toISOString().slice(0,10);
 }
 return label+': '+value;
}
function appendTechnicalMetadata(parent,record){
 if(!record.model_id&&!record.collected_at)return;
 const details=add(parent,el('details','capability-tech'));
 add(details,el('summary','', 'Technical identifiers and collection time'));
 if(record.model_id)add(details,el('p','', 'Model ID: '+record.model_id));
 if(record.collected_at)add(details,el('p','', 'Collection timestamp (as stored): '+record.collected_at));
}
function baselineDates(record){
 const dates=[
  ['Evaluation date',record.evaluation_date],
  ['Model release date',record.model_release_date],
  ['Record collected',record.collected_at]
 ].filter(item=>item[1]);
 if(!dates.length&&record.date_value)dates.push([record.date_label||'Date',record.date_value]);
 return dates.length?dates.map(item=>formatBaselineDate(item[0],item[1])).join(' · '):'Date not recorded';
}
function baselineSourceName(value){
 const labels={artificial_analysis:'Artificial Analysis',livebench:'LiveBench',lmarena:'LMArena',worldbank:'World Bank'};
 const raw=String(value||'').trim();
 return labels[raw.toLowerCase()]||raw.replace(/[_-]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase())||'Not recorded';
}
function addBaselineSource(parent,record){
 if(!record.source_url)return;
 try{const url=new URL(record.source_url);if(url.protocol==='http:'||url.protocol==='https:'){
  const link=add(parent,el('a','baseline-source','Benchmark source ↗'));link.href=url.href;link.target='_blank';link.rel='noopener noreferrer'
 }}catch(e){}
}
function renderBaselineResult(record){
 const card=el('div','baseline-result');
 const benchmark=(record.benchmark_name||'Benchmark')+(record.benchmark_version?' · '+record.benchmark_version:'');
 add(card,el('b','',benchmark));
 if(record.task_text)add(card,el('p','baseline-task',record.task_text));
 else if(record.task)add(card,el('p','baseline-task','Task ID: '+record.task));
 add(card,el('p','', 'Benchmark source: '+baselineSourceName(record.source)));
 add(card,el('p','', 'Evaluated model: '+(record.model_name||'Not recorded')));
 add(card,el('p','', 'Benchmark score: '+baselineScore(record)));
 add(card,el('p','baseline-meta',baselineDates(record)));
 appendTechnicalMetadata(card,record);
 addBaselineSource(card,record);
 return card
}
function renderBaselineSeries(record){
 const detail=el('details','baseline-series-item');
 const label=(record.domain?record.domain+' · ':'')+
  (record.benchmark_name||'Benchmark')+(record.benchmark_version?' · '+record.benchmark_version:'')+
  ' · '+(record.task_text||record.task||'Task not specified');
 add(detail,el('summary','',label));
 const body=add(detail,el('div','baseline-series-details'));
 body.appendChild(renderBaselineResult(record));
 const history=Array.isArray(record.history)?record.history:[];
 if(history.length){
  add(body,el('p','baseline-history-note','Other stored model results from this same source, benchmark version, task, score unit and direction. These are not a repeated time series for one model.'));
  const list=add(body,el('ul','baseline-history'));
  history.forEach(item=>{
   const score=baselineScore(item);
   const dateText=baselineDates(item);
   const row=add(list,el('li'));
   add(row,el('span','',(dateText!=='Date not recorded'?dateText+' · ':'')+
    (item.model_name||'Model not recorded')+' · '+score));
   appendTechnicalMetadata(row,item);
  });
 }else add(body,el('p','baseline-history-note','No other model results are stored for this exact series.'));
 return detail
}
async function loadBaseline(){
 const summary=$('baseline-summary'),series=$('baseline-series'),grid=$('capability-grid');
 try{
  const d=await getJSON('/api/benchmarks/overview');
  const ds=Array.isArray(d.domains)?d.domains:[];
  const bs=Array.isArray(d.benchmarks)?d.benchmarks:[];
   const measurements=Array.isArray(d.current_measurements)?d.current_measurements:[];
    const collectedDates=measurements.map(m=>new Date(m.collected_at||'')).filter(date=>!Number.isNaN(date.getTime()));
    const latestCollected=collectedDates.reduce((latest,date)=>date>latest?date:latest,null);
    $('tracked-benchmark-count').textContent=bs.length.toLocaleString('en-SG');
    $('tracked-model-count').textContent=Number(d.models_total||0).toLocaleString('en-SG');
    $('latest-benchmark-collected').textContent=latestCollected
      ?latestCollected.toLocaleDateString('en-SG',{day:'numeric',month:'short',year:'numeric'})
      :'Not recorded';
    $('benchmark-tracking-note').textContent=measurements.length
      ?'Coverage and collection date are based on stored benchmark results.'
      :'No benchmark results are stored yet.';
   grid.replaceChildren();series.replaceChildren();
   summary.textContent=measurements.length+' benchmark task series · '+Number(d.models_total||0)+' stored models · '+ds.length+' domains · '+bs.length+' benchmark families. Results are grouped by source, version, task, unit and score direction; detailed metric definitions are not available for every source.';
   const byDomain=new Map();
   measurements.forEach(m=>{const key=m.domain||'Unspecified domain';if(!byDomain.has(key))byDomain.set(key,[]);byDomain.get(key).push(m)});
   const featured=FEATURED_CAPABILITIES.filter(name=>byDomain.has(name));
   const domainOrder=[...featured,...Array.from(byDomain.keys()).filter(name=>!featured.includes(name)).sort((a,b)=>a.localeCompare(b))];
   capabilityGroups=domainOrder.map(domain=>({domain,records:byDomain.get(domain)||[]}));
    baselineEvidenceRows=Array.from(byDomain.entries()).sort((a,b)=>a[0].localeCompare(b[0]));
   showAllCapabilities=false;
   capabilityCards=capabilityGroups.map((group,index)=>buildCapabilityCard(group,index));
   capabilityCards.forEach(card=>grid.appendChild(card));
   updateCapabilityVisibility();
   $('capability-show-more').onclick=()=>{
    showAllCapabilities=!showAllCapabilities;updateCapabilityVisibility();
    if(!showAllCapabilities){
     capabilityCards.slice(5).forEach(card=>{
      const panel=card.querySelector('.capability-details'),button=card.querySelector('.capability-explore');
      if(panel)panel.hidden=true;if(button){button.setAttribute('aria-expanded','false');button.textContent='Explore'}
     });
    }
   };
   if(!capabilityCards.length)add(grid,el('p','muted','Not enough benchmark data to show capabilities yet.'));
    const disclosure=$('benchmark-evidence');
    disclosure.dataset.loaded='false';
    if(disclosure.dataset.lazyBound!=='true'){
     disclosure.addEventListener('toggle',()=>{
      if(!disclosure.open||disclosure.dataset.loaded==='true')return;
      disclosure.dataset.loaded='true';
      renderAllBaselineEvidence(series);
     });
     disclosure.dataset.lazyBound='true';
    }
    if(disclosure.open){disclosure.dataset.loaded='true';renderAllBaselineEvidence(series)}
  }catch(e){errBox(grid,'Capability information could not be loaded: '+e.message,loadBaseline);summary.textContent='Benchmark evidence is temporarily unavailable.';$('benchmark-tracking-note').textContent='Benchmark tracking data is temporarily unavailable.';}
}
function renderAllBaselineEvidence(target){
 target.replaceChildren();
 add(target,el('p','baseline-history-note','Stored model results are grouped only within the same source, benchmark version, task, score unit and direction. Collection dates are not shown as evaluation dates.'));
 baselineEvidenceRows.forEach(([name,rows])=>{
  const group=add(target,el('section','baseline-record-group'));
  add(group,el('h3','',name+' · '+rows.length+' series'));
  const list=add(group,el('div','baseline-series-list'));
  rows.forEach(record=>list.appendChild(renderBaselineSeries(record)));
 });
}

/* ---- AI progress ---- */
let comparisons=[],activeCap=null;
async function loadCaps(){const box=$('caps');
 try{const d=await getAdvancementData();comparisons=d.comparisons||[];
  const advancements=Array.isArray(d.advancements)?d.advancements.filter(a=>a.comparable&&Number(a.change)>=0.5):[];
  box.replaceChildren();const call=$('ai-callout');call.replaceChildren();$('advancement-impact').hidden=true;
  if(d.status==='insufficient_snapshots'||!comparisons.length){
   add(call,el('p','advance-note','Not enough comparable snapshots yet.'));
  }else if(!advancements.length){
   add(call,el('p','advance-note','No new comparable improvements in the latest snapshot.'));
  }else{
   add(call,el('p','advance-note',advancements.length+' new comparable improvement'+(advancements.length===1?'':'s')+' detected.'));
  }
  $('cap-detail').replaceChildren();$('occlist').replaceChildren();activeCap=null;
  if(!advancements.length)return;
  $('advancement-impact').hidden=false;
  advancements.forEach((cp,i)=>{const b=add(box,el('button','cap fade-in'));b.type='button';b.style.animationDelay=(i*50)+'ms';
   const top=add(b,el('div','cap-top'));add(top,el('h3','',cp.capability));
   add(top,el('span','chip c-up','+'+fmt(cp.change,2)+' pts'));
   if(cp.latest_best!=null){add(b,el('div','score',fmt(cp.latest_best,2)));add(b,el('div','sm','Latest measured index points'+(cp.leading_model?' · '+cp.leading_model:'')));}
   if(Array.isArray(cp.benchmark_version)&&cp.benchmark_version.length)add(b,el('div','sm','Comparable benchmark version: '+cp.benchmark_version.join(', ')));
   b.onclick=()=>{document.querySelectorAll('.cap').forEach(x=>x.classList.remove('active'));b.classList.add('active');loadImpact(cp.capability)}});
  const first=advancements[0];if(first){box.children[0].classList.add('active');loadImpact(first.capability)}
 }catch(e){errBox(box,'We could not load AI progress data. '+e.message,loadCaps)}}

async function loadImpact(cap){activeCap=cap;const box=$('cap-detail'),occ=$('occlist');
 box.replaceChildren();const sk0=add(box,el('div','skel'));sk0.style.cssText='height:160px;margin-top:18px';
 occ.replaceChildren();const sk=add(occ,el('div','skel'));sk.style.height='120px';
 let d;try{d=await getJSON('/api/advancements/impact?capability='+encodeURIComponent(cap)+'&top_k=8')}catch(e){errBox(box,'We could not load details for '+cap+'. '+e.message,()=>loadImpact(cap));occ.replaceChildren();return}
 if(activeCap!==cap)return;
 box.replaceChildren();const card=add(box,el('div','card detail fade-in'));
 const head=add(card,el('div','item-top'));add(head,el('h3','',cap));
 const none=d.advancement_status==='no_meaningful_advancement';
 add(head,el('span','chip '+(none?'c-flat':'c-up'),none?'No measured improvement':'Measured improvement'));
  if(none){add(card,el('p','muted','No new measurable improvement in the latest comparable snapshots. This does not mean the evaluated AI capability is absent.'))}
  else{add(card,el('p','muted','A public AI test improved. Related skills and jobs are possibilities, not confirmed workplace effects.'))}
 const cmp=d.comparison||{};const evb=ev(card,'Evidence: how this was measured');
 add(evb,el('p','','Latest snapshot: '+(cmp.latest_time||cmp.latest_snapshot||'n/a')+'. Minimum change counted as meaningful: '+(cmp.min_change_threshold!=null?cmp.min_change_threshold+' points':'n/a')+'.'+(cmp.note?' '+cmp.note:'')));
 const rows=(cmp.comparisons||[]).filter(r=>r.capability===cap);
 if(rows.length)table(evb,['Test version','Previous best','Latest best','Change'],rows.map(r=>[(r.benchmark_version||[]).join(', ')||'n/a',fmt(r.previous_best),fmt(r.latest_best),fmt(r.change)]));
 if((d.capability_tasks||[]).length){add(evb,el('p','','Example tasks this area covers:'));const ul=add(evb,el('ul'));d.capability_tasks.slice(0,5).forEach(t=>add(ul,el('li','',t.task_text)))}
 renderOcc(d,none,cap)}

function renderOcc(d,none,cap){const box=$('occlist');box.replaceChildren();const occs=d.occupations||[];
  if(none||!occs.length){const e=add(box,el('div','honest-empty fade-in'));add(e,el('b','',none?'No new snapshot-linked occupation changes':'Not enough evidence for new occupation links'));add(e,el('span','',none?'The advancement-only view has no new links. Explore Careers separately examines current benchmark capabilities and related skills.':'No supported new occupation links are available for '+cap+'.'));return}
 const list=add(box,el('div','skills'));
 occs.slice(0,8).forEach((o,i)=>{const it=add(list,el('div','item fade-in'));it.style.animationDelay=(i*40)+'ms';const t=add(it,el('div','item-top'));add(t,el('b','',o.occupation));add(t,el('span','chip c-pos','Possible'));
  add(it,el('p','',o.matched_skills+' of its '+o.total_esco_skills+' listed skills overlap with this AI area ('+o.essential_matches+' essential, '+o.optional_matches+' optional).'));
  const evb=ev(it,'Evidence');table(evb,['Skill','Relation','Similarity'],(o.evidence||[]).map(x=>[x.skill,x.relation,fmt(x.cosine_similarity,3)]));add(evb,el('p','muted','Relevance score '+fmt(o.relevance_score,3)+'. Similarity is not an automation probability.'))})}

async function loadFrontier(){const box=$('frontier');
 try{const d=await getJSON('/api/benchmarks/frontier');box.replaceChildren();const rows=(Array.isArray(d)?d:[]).slice(0,8);
  if(!rows.length){add(box,el('p','','No record-breaking results recorded yet.'));return}
  add(box,el('p','','Each row is a moment when an AI system beat the previous best score on a public test.'));
  table(box,['Date','Test','New best','Previous','Gain','Model'],rows.map(r=>[r.evaluation_date||'',r.benchmark_name+(r.benchmark_version?' '+r.benchmark_version:''),fmt(r.new_best,2),fmt(r.previous_best,2),'+'+fmt(r.improvement,2),r.model_name||'']))
 }catch(e){errBox(box,'Could not load records. '+e.message,loadFrontier)}}

/* ---- Skills ---- */
async function loadBench(){const box=$('bench');
 try{const d=await getJSON('/api/benchmarks/overview');const seen=new Set();const list=(d.benchmarks||[]).filter(b=>{if(seen.has(b.benchmark_name))return false;seen.add(b.benchmark_name);return true}).slice(0,8);
  box.replaceChildren();if(!list.length){add(box,el('p','muted','Not enough data: no AI tests are available yet.'));return}
   list.forEach((b,i)=>{const btn=add(box,el('button','',b.domain||b.benchmark_name.replace(/^Artificial Analysis /,'').replace(/ Index$/,'')));btn.type='button';btn.title='Explore related skills';btn.onclick=()=>{box.querySelectorAll('button').forEach(x=>x.classList.remove('active'));btn.classList.add('active');loadSkills(b.benchmark_name,b.domain)};if(i===0)btn.click()})
 }catch(e){errBox(box,'Could not load the list of AI tests. '+e.message,loadBench)}}
let activeBench=null;
async function loadSkills(name,domain){activeBench=name;const box=$('skilllist');box.replaceChildren();for(let i=0;i<4;i++){const s=add(box,el('div','skel'));s.style.height='110px'}
 let d;try{d=await getJSON('/api/benchmarks/skills?benchmark='+encodeURIComponent(name))}catch(e){errBox(box,'Could not load skills for '+name+'. '+e.message,()=>loadSkills(name,domain));return}
 if(activeBench!==name)return;box.replaceChildren();const skills=(d.skills||[]).slice(0,8);
  if(!skills.length){const e=add(box,el('div','honest-empty'));add(e,el('b','','Not enough data for close skill matches'));add(e,el('span','','No related candidates are available for '+name+'.'));return}
  skills.forEach((s,i)=>{const it=add(box,el('div','item fade-in'));it.style.animationDelay=(i*40)+'ms';const t=add(it,el('div','item-top'));add(t,el('b','',s.skill));add(t,el('span','chip c-pos','Possible task link'));
    const evb=ev(it,'Why?');if(s.description)add(evb,el('p','',s.description));
   if((s.matched_tasks||[]).length){add(evb,el('p','','Closest test tasks:'));table(evb,['Task','Similarity'],s.matched_tasks.slice(0,3).map(m=>[m.task_text||m.task,fmt(m.cosine_similarity,3)]))}
   add(evb,el('p','muted','MiniLM similarity ranks possible text matches; it is not automation probability. These task-to-skill links are not independently verified workplace impacts. Overall relevance '+fmt(s.cosine_similarity,3)+' (rank '+s.rank+').'))})}

 loadBaseline();loadCaps();loadFrontier();loadBench();
})();
'''

TRENDS_HTML = _page("FutureTwin AI · AI & Career Trends", "trends", TRENDS_CSS, TRENDS_BODY, TRENDS_JS)
