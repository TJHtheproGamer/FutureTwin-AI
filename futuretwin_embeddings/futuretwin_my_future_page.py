"""My Future page: presentation-only Flask HTML, CSS and vanilla JavaScript."""

from futuretwin_pages import BASE_CSS, _page
from futuretwin_intel_ui import INTEL_CSS, INTEL_JS
from futuretwin_playground_ui import PLAYGROUND_CSS, PLAYGROUND_JS


MY_FUTURE_CSS = r'''
.myf-hero{padding:22px 0 0}
.myf-hero-inner{display:flex;justify-content:space-between;align-items:center;gap:20px}
.myf-hero h1{font-size:28px;line-height:1.2;margin:0}
.myf-hero p{margin:0;color:var(--ink2);font-size:15px}
.myf-hero-tools{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.myf-passport-mini{display:flex;flex-direction:column;justify-content:center;gap:1px;min-width:190px;padding:7px 11px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:var(--ink);text-decoration:none;box-shadow:var(--shadow);transition:border-color .15s,background .15s}
.myf-passport-mini:hover{border-color:#9bbbdd;background:var(--paper2)}
.myf-passport-mini-label{font-size:11px;color:var(--muted)}
.myf-passport-mini-bottom{display:flex;align-items:baseline;justify-content:space-between;gap:10px}
.myf-passport-mini-count{font-size:12px;color:var(--ink2);white-space:nowrap}
.myf-passport-mini-count strong{display:inline;font-size:14px;color:var(--ink);margin:0}
.myf-passport-mini-cta{font-size:11px;font-weight:700;color:var(--harbor);white-space:nowrap}
.myf-main{padding-top:20px;padding-bottom:44px}
.myf-summary{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:14px 17px;margin-bottom:15px}
.myf-summary-label{font-size:12px;color:var(--muted)}
.myf-summary strong{display:block;font-size:18px;color:var(--ink);margin-top:2px}
.myf-goal-summary{padding:12px 16px;margin-top:0;background:var(--paper);border-color:var(--line)}.myf-hub{flex-direction:column;align-items:stretch;gap:10px}.myf-hub-top{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}.myf-hub-actions{display:flex;gap:8px;flex-wrap:wrap}@media(max-width:600px){.myf-hub-actions .btn{flex:1 1 44%;justify-content:center}}
.myf-goal-summary strong{font-size:14px}
.myf-tabs{display:flex;gap:5px;padding:4px;background:#eeeae0;border-radius:12px;margin-bottom:16px;overflow:auto}
.myf-tabs button{border:0;background:transparent;color:var(--muted);font-weight:700;font-size:13px;border-radius:9px;padding:9px 13px;white-space:nowrap}
.myf-tabs button[aria-selected="true"]{background:var(--paper);color:var(--harbor);box-shadow:0 1px 4px #14263a12}
.myf-panel{padding:20px}
.myf-panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:14px}
.myf-panel-head h2{font:700 20px var(--body);letter-spacing:-.03em}
.myf-panel-head p{font-size:12px;color:var(--muted);margin:4px 0 0}
.myf-toolbar{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.myf-search{position:relative;flex:1;min-width:min(300px,100%)}
.myf-search input,.myf-field input{width:100%;border:1px solid var(--line);background:#fffefa;border-radius:10px;padding:10px 12px;color:var(--ink);font:inherit;font-size:14px}
.myf-search-results{position:absolute;z-index:12;top:calc(100% + 6px);left:0;right:0;max-height:280px;overflow:auto;background:var(--paper);border:1px solid var(--line);border-radius:12px;box-shadow:0 14px 34px #14263a1a}
.myf-search-results button{display:block;width:100%;text-align:left;border:0;border-bottom:1px solid var(--line2);background:none;padding:10px 12px;color:var(--ink)}
.myf-search-results button:hover,.myf-search-results button[aria-selected="true"]{background:var(--harbor-soft)}
.myf-search-results strong,.myf-search-results small{display:block}.myf-search-results strong{font-size:13px}.myf-search-results small{color:var(--muted);font-size:11px;margin-top:2px}
.myf-status{min-height:20px;color:var(--muted);font-size:12px;margin:8px 0}
.myf-error{background:var(--clay-soft);border:1px solid #ecc9c0;color:var(--clay);border-radius:11px;padding:11px 13px;font-size:13px}
.myf-recs{display:grid;gap:9px;margin-top:12px}
.myf-rec{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:start;gap:12px;border:1px solid var(--line2);border-radius:13px;padding:14px;background:var(--paper);transition:border-color .18s,transform .18s}
.myf-rec:hover{border-color:#b7c9c0;transform:translateY(-1px)}
.myf-rec h3{font:700 16px var(--body);letter-spacing:-.025em}
.myf-rec p{margin:4px 0 0;color:var(--muted);font-size:12px;line-height:1.5}
.myf-reason{color:#526b5e!important;font-size:11px!important;margin-top:8px!important}
.myf-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.myf-chip{display:inline-flex;align-items:center;border-radius:99px;padding:5px 9px;background:var(--sage-soft);color:#35624d;font-size:11px;font-weight:600}
.myf-chip.optional{background:var(--harbor-soft);color:var(--harbor)}
.myf-interest-match{margin-top:10px;padding:8px 10px;border-left:3px solid var(--harbor);border-radius:0 10px 10px 0;background:#eef5f8}
.myf-interest-match-label{display:block;color:var(--harbor);font-size:10px;font-weight:700}
.myf-interest-match .myf-interest-chips{margin-top:4px}
.myf-rec-actions{display:flex;align-items:center;gap:7px}
.myf-icon-btn{width:34px;height:34px;border:1px solid var(--line);border-radius:9px;background:#fffefa;color:var(--harbor);font-size:17px}
.myf-icon-btn[aria-pressed="true"]{background:var(--harbor-soft)}
.myf-link{border:0;background:none;color:var(--harbor);font-weight:700;font-size:12px;padding:6px}
.myf-interest-bar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:12px 0 0;padding-top:12px;border-top:1px solid var(--line2)}
.myf-interest-bar.myf-interest-header{flex:0 1 250px;min-width:165px;max-width:250px;margin:0;padding:7px 10px;border:1px solid var(--line);border-radius:10px;background:var(--paper);box-shadow:var(--shadow)}
.myf-interest-header>div{min-width:0}
.myf-interest-header .myf-interest-chips{margin-top:2px}
.myf-interest-purpose{display:inline-block;max-width:100%;padding:4px 0 0;font-size:11px;line-height:1.25;text-decoration:none}
.myf-interest-chips{display:flex;flex-wrap:wrap;gap:5px;margin-top:5px}
.myf-interest-note{font-size:11px;color:var(--muted);margin-top:7px}
.myf-empty{padding:20px 14px;background:var(--paper2);border:1px dashed #d9d0bd;border-radius:12px;color:var(--ink2);font-size:13px}
.myf-empty strong{display:block;color:var(--ink);margin-bottom:3px}
.myf-saved-list{display:grid;gap:8px}
.myf-saved-row{display:flex;justify-content:space-between;align-items:center;gap:12px;border:1px solid var(--line2);border-radius:11px;padding:11px 13px}
.myf-saved-row p{font-size:12px;color:var(--muted);margin:3px 0 0}
.myf-goal-mark{font-size:10px;font-weight:700;color:#35624d;background:var(--sage-soft);padding:4px 8px;border-radius:99px}
.myf-detail{margin-top:0}
.myf-detail-top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.myf-detail-top h2{font-size:clamp(25px,3vw,34px);margin:4px 0}
.myf-detail-copy{max-width:760px;color:var(--ink2);font-size:14px;margin:6px 0 0}
.myf-detail-actions{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}
.myf-detail-section{border-top:1px solid var(--line2);padding-top:15px;margin-top:16px}
.myf-detail-section h3{font:700 15px var(--body);margin:0 0 8px}
.myf-matches{display:flex;flex-wrap:wrap;gap:6px}
.myf-skill-row{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:10px;border-top:1px solid var(--line2);padding:9px 0}
.myf-skill-name{font-size:13px;color:var(--ink2)}
.myf-skill-meta{display:block;font-size:10px;color:var(--muted);margin-top:2px}
.myf-skill-actions{display:flex;gap:6px;flex-wrap:wrap}
.myf-skill-actions .btn{padding:6px 9px;font-size:11px}
.myf-disclaimer{font-size:11px;color:var(--muted);margin:8px 0 0}
.myf-disclosure{border-top:1px solid var(--line2);margin-top:15px;padding-top:12px}
.myf-disclosure summary{cursor:pointer;color:var(--harbor);font-size:12px;font-weight:700}
.myf-disclosure-body{padding-top:10px;color:var(--ink2);font-size:12px}
.myf-disclosure-body p{margin:5px 0}
.myf-skill-columns{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.myf-context{background:var(--paper2);border-radius:11px;padding:12px 13px;color:var(--ink2);font-size:12px}
.myf-benchmark-list{display:grid;gap:8px;margin-top:10px}
.myf-benchmark-task{border:1px solid var(--line2);border-radius:10px;background:#fffefa;padding:11px}
.myf-benchmark-task h4{font:700 12px var(--body);margin:0 0 6px;line-height:1.45}
.myf-benchmark-meta{display:flex;flex-wrap:wrap;gap:5px;margin:6px 0}
.myf-benchmark-meta span{font-size:10px;color:var(--ink2);background:var(--paper2);border-radius:6px;padding:4px 6px}
.myf-benchmark-skills{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
.myf-benchmark-skills span{font-size:10px;color:#526b5e;background:var(--sage-soft);border-radius:99px;padding:4px 7px}
.myf-benchmark-source{font-size:10px;color:var(--harbor);font-weight:700}
.myf-roadmap{display:grid;gap:7px;margin-top:9px}
.myf-roadmap-row{display:flex;align-items:flex-start;gap:9px;border-top:1px solid var(--line2);padding:9px 2px;font-size:12px;color:var(--ink2)}
.myf-roadmap-row input{accent-color:var(--sage);margin-top:3px}
.myf-roadmap-row.done span{text-decoration:line-through;color:var(--muted)}
.myf-roadmap-row small{display:block;font-size:10px;color:var(--muted)}
.myf-plan-controls{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.myf-plan-controls select{max-width:100%;border:1px solid var(--line);border-radius:9px;background:#fffefa;color:var(--ink);padding:8px 10px;font:inherit;font-size:12px}
.myf-modal-backdrop{position:fixed;inset:0;z-index:50;background:#14263a66;display:grid;place-items:center;padding:18px}
.myf-modal{width:min(600px,100%);max-height:min(88vh,780px);overflow:auto;background:var(--paper);border:1px solid var(--line);border-radius:17px;padding:22px;box-shadow:0 18px 60px #14263a33}
.myf-modal-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.myf-modal-head h2{font:700 20px var(--body)}
.myf-modal-head p{font-size:12px;color:var(--muted);margin:5px 0 0;max-width:490px}
.myf-close{width:34px;height:34px;border:1px solid var(--line);border-radius:9px;background:#fffefa;color:var(--ink2);font-size:18px}
.myf-interest-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:15px 0}
.myf-interest-option{display:flex;gap:8px;align-items:center;border:1px solid var(--line2);border-radius:10px;padding:9px;font-size:12px;color:var(--ink2)}
.myf-interest-option:has(input:checked){border-color:#a7bdaf;background:#f1f6f1;color:#365b46}
.myf-interest-option input,.myf-open-option input{accent-color:var(--sage)}
.myf-open-option{display:flex;gap:9px;align-items:center;border-block:1px solid var(--line2);padding:10px 1px;font-size:12px;font-weight:700}
.myf-group-map{font-size:11px}
.myf-field{display:grid;gap:6px;margin-top:13px;font-size:12px;font-weight:700;color:var(--ink2)}
.myf-field input{font-size:13px}
.myf-modal-actions{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:17px}
.myf-modal-actions>div{display:flex;gap:7px}
.myf-toast{font-size:12px;color:var(--sage);margin-top:9px}
.myf-detail-error{margin:12px 0}
.myf-recommendation-more{margin-top:12px}
.myf-best-match{margin-top:11px;padding:10px;border:1px solid var(--line2);border-radius:11px;background:#fafbf9}
.myf-evidence-score{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.myf-evidence-score strong{font-size:15px;color:var(--ink)}
.myf-evidence-score span{font-size:11px;color:var(--muted)}
.myf-evidence-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:6px;margin-top:9px}
.myf-evidence-item{min-width:0;border:1px solid var(--line2);border-radius:8px;padding:7px;background:var(--paper)}
.myf-evidence-label{display:block;font-size:10px;color:var(--muted);font-weight:700}
.myf-evidence-value{display:block;margin-top:3px;font-size:11px;color:var(--ink2);line-height:1.35}
.myf-evidence-details{margin-top:9px;padding-top:8px;border-top:1px solid var(--line2)}
.myf-evidence-details summary{cursor:pointer;color:var(--harbor);font-size:11px;font-weight:700}
.myf-evidence-detail-body{padding-top:7px;color:var(--ink2);font-size:11px;line-height:1.5}
.myf-evidence-detail-body p{margin:5px 0}
.myf-evidence-detail-body ul{margin:5px 0;padding-left:17px}
.myf-recommendation-method{margin-top:10px;padding:9px 11px;border:1px solid var(--line2);border-radius:10px;background:#fafbf9}
.myf-recommendation-method summary{cursor:pointer;color:var(--harbor);font-size:12px;font-weight:700}
.myf-recommendation-method p,.myf-recommendation-method li{font-size:11px;line-height:1.5;color:var(--ink2)}
.myf-recommendation-method ul{padding-left:18px}
.myf-method-details,.myf-scenario-details{margin-top:14px;padding-top:12px;border-top:1px solid var(--line2)}
.myf-method-details summary,.myf-scenario-details summary{cursor:pointer;color:var(--harbor);font-size:12px;font-weight:700}
.myf-scenario-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.myf-scenario-tabs button{border:1px solid var(--line);background:var(--paper);color:var(--ink2);border-radius:99px;padding:6px 10px;font-size:11px;font-weight:700}
.myf-scenario-tabs button[aria-pressed="true"]{background:var(--harbor);border-color:var(--harbor);color:#fbf8f1}
.myf-scenario-copy{background:#edf3f1;border-left:3px solid var(--harbor);padding:11px 13px;border-radius:0 10px 10px 0;font-size:12px;color:var(--ink2)}
.myf-stress-list{margin:6px 0;padding-left:18px;font-size:13px;color:var(--ink2);line-height:1.55}
.myf-method-details h4{font:700 12px var(--body);margin:12px 0 4px}
.myf-wf{margin:8px 0;padding-left:20px;font-size:13px;color:var(--ink2)}.myf-wf li{margin-bottom:8px}.myf-wf p{margin:2px 0}.myf-ins-group{margin-top:14px}.myf-ins-group h3{font:700 14px var(--body);margin:0 0 4px}.myf-ins-card{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;border:1px solid var(--line2);border-radius:11px;padding:11px 13px;margin-top:8px;background:var(--paper)}.myf-ins-card h4{font:700 14px var(--body);margin:0}.myf-cmp-chip{gap:6px}.myf-cmp-chip .myf-link{padding:0 2px;font-size:11px}
@media(max-width:600px){.myf-ins-card{grid-template-columns:1fr}}
@media(max-width:800px){.myf-hero-inner{align-items:flex-start;flex-direction:column}.myf-hero-tools{width:100%;justify-content:flex-start}.myf-skill-columns{grid-template-columns:1fr}}
 @media(max-width:460px){.myf-hero-tools{width:100%;display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);align-items:stretch}.myf-interest-header{min-width:0;max-width:none}.myf-passport-mini{min-width:0}.myf-hero-tools #saved-shortcut{grid-column:1/-1;justify-self:start}}
@media(max-width:600px){.myf-hero{padding:27px 0 18px}.myf-panel{padding:15px}.myf-summary{align-items:flex-start}.myf-tabs{margin-inline:-1px}.myf-rec{grid-template-columns:1fr}.myf-rec-actions{justify-content:space-between}.myf-search{min-width:100%}.myf-toolbar>.btn{flex:1;justify-content:center}.myf-detail-top{flex-direction:column}.myf-skill-row{grid-template-columns:1fr}.myf-skill-actions{justify-content:flex-start}.myf-interest-grid{grid-template-columns:1fr}.myf-modal{padding:17px}.myf-modal-actions{align-items:flex-start;flex-direction:column-reverse}.myf-modal-actions>div{width:100%}.myf-modal-actions>div .btn{flex:1;justify-content:center}}
'''


MY_FUTURE_CSS += PLAYGROUND_CSS + INTEL_CSS


MY_FUTURE_BODY = r'''
<main>
 <section class="myf-hero"><div class="wrap myf-hero-inner"><h1>My Future</h1>
    <div class="myf-hero-tools">
      <a class="myf-passport-mini" href="/my-career" aria-label="Open My Skills Passport">
        <span class="myf-passport-mini-label">My Skills Passport</span>
        <span class="myf-passport-mini-bottom"><span class="myf-passport-mini-count"><strong id="confirmed-skill-count">…</strong> confirmed skills</span><span class="myf-passport-mini-cta">View Passport</span></span>
      </a>
      <div class="myf-interest-bar myf-interest-header"><div><strong style="font-size:12px">Your interests</strong><div id="interest-chips" class="myf-interest-chips"></div></div><button class="myf-link" id="clear-interest-filters" type="button" hidden>Clear filters</button></div>
      <button class="btn btn-ghost btn-sm" id="saved-shortcut" type="button">Saved Careers <span id="saved-count">0</span></button>
    </div>
  </div></section>
 <section class="wrap myf-main">
   <div id="page-error" class="myf-error" role="alert" hidden><span id="page-error-text"></span> <button id="page-retry" class="btn btn-ghost btn-sm" type="button">Try again</button></div>
   <div id="initial-loading" aria-label="Loading My Future">
     <div class="card myf-panel"><div class="skel" style="height:22px;width:42%"></div><div class="skel" style="height:90px;margin-top:16px"></div><div class="skel" style="height:80px;margin-top:10px"></div></div>
   </div>
   <div id="workspace" hidden>
     <section id="goal-summary" class="card myf-summary myf-goal-summary myf-hub" aria-label="My Career Goal" hidden>
        <div class="myf-hub-top"><div><span class="myf-summary-label">My Career Goal</span><strong id="goal-summary-title"></strong></div><button class="btn btn-ghost btn-sm" id="goal-change" type="button">Change Career</button></div>
      </section>
     <p id="action-status" class="myf-status" role="status" aria-live="polite" hidden></p>
     <div id="dashboard-area">
       <div class="myf-tabs" role="tablist" aria-label="My Future">
         <button type="button" role="tab" id="tab-discover" data-tab="discover" aria-selected="true">Discover</button>
         <button type="button" role="tab" id="tab-saved" data-tab="saved" aria-selected="false">Saved <span id="saved-tab-count"></span></button>
         <button type="button" role="tab" id="tab-learning" data-tab="learning" aria-selected="false">Plan</button>
       </div>
       <section id="view-discover" class="card myf-panel" role="tabpanel" aria-labelledby="tab-discover">
         <div class="myf-panel-head"><div><div class="eyebrow">Explore</div><h2>Jobs for You</h2><p id="rec-summary" hidden></p></div></div>
         <p id="recommendation-state" class="myf-status" role="status" aria-live="polite">Loading career ideas…</p>
         <div id="recommendation-error" class="myf-error" hidden><span id="recommendation-error-text"></span> <button id="retry-recommendations" class="btn btn-ghost btn-sm" type="button">Try again</button></div>
         <div id="mf-sort"></div><div id="recommendations" class="myf-recs"></div>
         <button class="btn btn-ghost btn-sm myf-recommendation-more" id="explore-more" type="button" hidden>See more matches</button>
       </section>
       <section id="view-saved" class="card myf-panel" role="tabpanel" aria-labelledby="tab-saved" hidden>
         <div class="myf-panel-head"><div><div class="eyebrow">Your shortlist</div><h2>Saved Careers</h2></div><button class="btn btn-ghost btn-sm" type="button" data-open-tab="discover">Find Careers</button></div>
         <div id="saved-empty" class="myf-empty" hidden><strong>No saved careers yet</strong></div>
         <div id="saved-list" class="myf-saved-list"></div>
       </section>
       <section id="view-learning" class="card myf-panel" role="tabpanel" aria-labelledby="tab-learning" hidden>
         <div class="myf-panel-head"><div><div class="eyebrow">Your next steps</div><h2>My Learning Plan</h2></div><button class="btn btn-ghost btn-sm" id="learning-change-target" type="button">Change career</button></div>
         <div id="learning-target" class="myf-context"></div>
         <div id="learning-state" class="myf-status" role="status" aria-live="polite"></div>
         <div id="learning-error" class="myf-error" hidden><span id="learning-error-text"></span> <button id="learning-retry" class="btn btn-ghost btn-sm" type="button">Try again</button></div>
         <div id="learning-active-section" class="myf-detail-section" hidden><h3>Active goals</h3><div id="learning-active-list" class="myf-roadmap"></div><button id="learning-show-more" class="myf-link" type="button" hidden>Show all goals</button></div>
         <div id="learning-completed-section" class="myf-detail-section" hidden><h3>Completed steps</h3><div id="learning-completed-list" class="myf-roadmap"></div></div>
         <div id="learning-add-section" class="myf-detail-section" hidden><h3>Add a goal</h3><p class="myf-disclaimer">Examples from occupation data, not required hiring skills or a ranking.</p><div class="myf-plan-controls"><select id="learning-skill-select" aria-label="Choose a skill goal"><option value="">Choose a skill</option></select><button class="btn btn-primary btn-sm" id="learning-add-goal" type="button" disabled>Add to plan</button></div></div>
         <div id="learning-empty" class="myf-empty" hidden><strong>Choose a career to start</strong><div style="margin-top:10px"><button class="btn btn-primary btn-sm" id="learning-choose-career" type="button">Find a career</button></div></div>
         <p class="myf-disclaimer">Completing a step does not confirm a skill in your Passport. Confirm skills separately when you’re ready.</p>
       </section>
     </div>
     <section id="career-detail" class="card myf-panel myf-detail" aria-live="polite" hidden></section>
   </div>
 </section>
 <div id="interests-dialog" class="myf-modal-backdrop" role="presentation" hidden>
   <section class="myf-modal" role="dialog" aria-modal="true" aria-labelledby="interests-title">
     <div class="myf-modal-head"><div><div class="eyebrow">Your direction</div><h2 id="interests-title">My Interests</h2><p>These broad guides can shape which careers you see. Some relevant careers may be hidden; clear filters anytime.</p></div><button class="myf-close" id="close-interests" type="button" aria-label="Close interests">×</button></div>
     <div id="interest-options" class="myf-interest-grid"></div>
     <details class="myf-disclosure"><summary>How these interests guide results</summary><div id="interest-mapping-copy" class="myf-disclosure-body myf-group-map"></div></details>
     <label class="myf-open-option"><input id="open-to-explore" type="checkbox"> I’m open to exploring</label>
     <div class="myf-field"><label for="other-interest-input">Other interests (optional)</label><div class="myf-toolbar"><input id="other-interest-input" type="text" maxlength="80" placeholder="Add an interest"><button class="btn btn-ghost btn-sm" id="add-other-interest" type="button">Add</button></div><div id="other-interest-chips" class="myf-interest-chips"></div></div>
     <div class="myf-field"><label for="career-goal-search">Optional career goal</label><div class="myf-search"><input id="career-goal-search" type="search" maxlength="100" placeholder="Search a career title" aria-label="Search a career goal" aria-autocomplete="list" aria-expanded="false" aria-controls="career-goal-results"><div id="career-goal-results" class="myf-search-results" role="listbox" hidden></div></div><div id="goal-search-status" class="myf-status" role="status" aria-live="polite"></div><div id="target-display" class="myf-interest-note">No career goal selected.</div><button id="clear-target" class="myf-link" type="button">Clear career goal</button> <button id="target-stress" class="myf-link" type="button">Explore My Future for this goal</button></div>
     <p id="save-status" class="myf-toast" role="status" aria-live="polite"></p>
     <div class="myf-modal-actions"><button class="myf-link" id="clear-all-interests" type="button">Clear interests and filters</button><div><button class="btn btn-ghost btn-sm" id="cancel-interests" type="button">Cancel</button><button class="btn btn-primary btn-sm" id="save-preferences" type="button">Save</button></div></div>
   </section>
 </div>
</main>
'''


MY_FUTURE_JS = r'''
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
'''+INTEL_JS+r'''
const INTEREST_OPTIONS=[
 {label:'Technology & AI',areas:['2','3'],groups:['Professionals','Technicians and associate professionals']},
 {label:'Healthcare',areas:['2','3','5'],groups:['Professionals','Technicians and associate professionals','Service and sales workers']},
 {label:'Business & Finance',areas:['1','2','3','4'],groups:['Managers','Professionals','Technicians and associate professionals','Clerical support workers']},
 {label:'Engineering',areas:['2','3','7','8'],groups:['Professionals','Technicians and associate professionals','Craft and related trades workers','Plant and machine operators']},
 {label:'Education',areas:['2','3'],groups:['Professionals','Technicians and associate professionals']},
 {label:'Creative Work',areas:['2','3','7'],groups:['Professionals','Technicians and associate professionals','Craft and related trades workers']},
 {label:'Science & Research',areas:['2','3'],groups:['Professionals','Technicians and associate professionals']},
 {label:'Environment & Sustainability',areas:['2','3','6','7','8'],groups:['Professionals','Technicians and associate professionals','Agricultural, forestry and fishery workers','Craft and related trades workers','Plant and machine operators']},
];
const INTEREST_LABELS=new Set(INTEREST_OPTIONS.map(item=>item.label));
const state={preferences:{career_areas:[],interests:[],target_occupation_uri:null},saved_occupations:[],saved_careers:[],roadmap_progress:{},roadmap_goals:{},insurance_alternatives:{},career_areas:[],confirmed_skills:[],csrf_token:'',details:null,detailsByUri:{},recommendations:[],recommendationsExpanded:false,activeTab:'discover',previousTab:'discover',learningCareerUri:null,learningDetails:null,learningExpanded:false,draft:null,stress:{open:false,scenario:'slower_adoption',evidence:false,prompt:false}};

async function request(url,options={}){
 const headers={Accept:'application/json',...(options.body?{'Content-Type':'application/json'}:{}),...(options.headers||{})};
 const response=await fetch(url,{...options,credentials:'same-origin',headers});
 let data={};try{data=await response.json()}catch(_e){}
 if(!response.ok)throw new Error(data.error||'This information could not be loaded.');
 return data;
}
function persistStatus(text,error=false){const node=$('save-status');if(node){node.textContent=text;node.style.color=error?'var(--clay)':'var(--sage)'}const global=$('action-status');if(global){global.textContent=text;global.hidden=!text;global.style.color=error?'var(--clay)':'var(--sage)'}}
function normalizedState(){return {purpose:state.purpose||{goals:[],skill_weight:70,purpose_weight:30,demand_weight:0},preferences:{career_areas:[...state.preferences.career_areas],interests:[...state.preferences.interests],target_occupation_uri:state.preferences.target_occupation_uri},saved_occupations:[...state.saved_occupations],roadmap_progress:Object.fromEntries(Object.entries(state.roadmap_progress).map(([uri,items])=>[uri,[...items]])),roadmap_goals:Object.fromEntries(Object.entries(state.roadmap_goals).map(([uri,items])=>[uri,[...items]])),insurance_alternatives:Object.fromEntries(Object.entries(state.insurance_alternatives||{}).map(([uri,items])=>[uri,[...items]]))}}
async function saveState(message='Changes saved.'){
 persistStatus('Saving…');
 try{
  const data=await request('/api/my-future',{method:'POST',headers:{'X-CSRF-Token':state.csrf_token},body:JSON.stringify(normalizedState())});
   state.preferences=data.preferences;state.purpose=data.purpose||state.purpose;state.saved_occupations=data.saved_occupations;state.saved_careers=data.saved_careers;state.roadmap_progress=data.roadmap_progress||{};state.roadmap_goals=data.roadmap_goals||{};state.insurance_alternatives=data.insurance_alternatives||{};state.csrf_token=data.csrf_token||state.csrf_token;
  persistStatus(message);renderPreferences();renderSaved();renderSummary();return true;
 }catch(error){persistStatus(error.message,true);return false}
}
function areaLabelsFor(codes){return (codes||[]).map(code=>state.career_areas.find(area=>area.code===code)?.label||('Group '+code))}
function mappedAreas(categories){return [...new Set((categories||[]).flatMap(label=>INTEREST_OPTIONS.find(item=>item.label===label)?.areas||[]))]}
function selectedCategories(){return state.preferences.interests.filter(item=>INTEREST_LABELS.has(item))}
function customInterests(){return state.preferences.interests.filter(item=>!INTEREST_LABELS.has(item))}
function careerLabel(uri){return state.saved_careers.find(item=>item.uri===uri)?.label||state.detailsByUri[uri]?.occupation?.label||''}
function renderSummary(){
 $('confirmed-skill-count').textContent=String(state.confirmed_skills.length);
 const target=state.preferences.target_occupation_uri,goal=$('goal-summary');
 goal.hidden=!target;$('goal-summary-title').textContent=target?(careerLabel(target)||'Selected career'):'';hubRefresh();
}
function renderPreferences(){
 const host=$('interest-chips');host.replaceChildren();
 const names=state.preferences.interests||[];
 if(!names.length&&!(state.preferences.career_areas||[]).length){const chip=document.createElement('span');chip.className='myf-chip';chip.textContent='Open to exploring';host.appendChild(chip)}
 names.forEach(name=>{const chip=document.createElement('span');chip.className='myf-chip';chip.textContent=name;host.appendChild(chip)});
 $('clear-interest-filters').hidden=!(names.length||(state.preferences.career_areas||[]).length);
 const target=state.preferences.target_occupation_uri;
 $('target-display').textContent=target?'Selected: '+(careerLabel(target)||'Career goal'):'No career goal selected.';
 $('saved-count').textContent=String(state.saved_careers.length);
 $('saved-tab-count').textContent=state.saved_careers.length?'('+state.saved_careers.length+')':'';
 renderSummary();
}
function renderSaved(){
 const host=$('saved-list');host.replaceChildren();$('saved-empty').hidden=state.saved_careers.length>0;
 state.saved_careers.forEach(career=>{
  const row=document.createElement('article');row.className='myf-saved-row';
  const main=document.createElement('div');
  const open=document.createElement('button');open.type='button';open.className='myf-link';open.style.padding='0';open.textContent=career.label;open.addEventListener('click',()=>loadDetails(career.uri));
  main.appendChild(open);
  if(career.target){const badge=document.createElement('span');badge.className='myf-goal-mark';badge.style.marginLeft='8px';badge.textContent='My Career Goal';main.appendChild(badge)}
  if(career.description){const desc=document.createElement('p');desc.textContent=career.description;main.appendChild(desc)}
  const actions=document.createElement('div');actions.className='myf-rec-actions';
   if(!career.target){const goal=document.createElement('button');goal.type='button';goal.className='btn btn-ghost btn-sm';goal.textContent='Set as goal';goal.addEventListener('click',()=>setTarget(career.uri,false,true));actions.appendChild(goal)}
  const remove=document.createElement('button');remove.type='button';remove.className='myf-link';remove.textContent='Remove';remove.setAttribute('aria-label','Remove '+career.label+' from saved careers');remove.addEventListener('click',()=>toggleSaved(career.uri));actions.appendChild(remove);
  row.append(main,actions);host.appendChild(row);
 });
}
function setTab(tab){
 state.activeTab=tab;
 ['discover','saved','learning'].forEach(name=>{const section=$('view-'+name),button=$('tab-'+name);section.hidden=name!==tab;button.setAttribute('aria-selected',String(name===tab));button.tabIndex=name===tab?0:-1});
 state.stress.open=false;$('career-detail').hidden=true;$('dashboard-area').hidden=false;
 if(tab==='saved')renderSaved();
 if(tab==='learning')loadLearning();
}
function recommendationMessage(data){
 if(data.status==='no_confirmed_skills')return 'Confirm a few skills in My Skills Passport to see career links.';
 if(data.status==='no_occupation_links')return 'There are no occupation links for these skills yet. You can still search careers.';
 if(data.status==='skills_too_broad')return 'These skills do not narrow career links yet. Add a specific skill or search.';
 if(data.status==='no_matches')return 'No career matches under these filters. Clear filters or search any career.';
  if(data.ranking?.effective==='best_match'&&data.ranking.best_match?.profile?.status==='early')return '';
 if(data.limited)return 'Early ideas based on confirmed skills. Add more confirmed skills to broaden the list.';
 return '';
}
function bmText(parent,tag,text,className=''){
 const node=document.createElement(tag);node.textContent=text;if(className)node.className=className;parent.appendChild(node);return node;
}
function bmMetric(parent,label,value){
 const item=document.createElement('div');item.className='myf-evidence-item';
 bmText(item,'span',label,'myf-evidence-label');bmText(item,'span',value,'myf-evidence-value');parent.appendChild(item);
}
function bestMatchCard(career,method){
 const result=career.best_match;if(!result)return null;
 const parts=result.components||{},skill=parts.skill_compatibility||{},task=parts.ai_task_exposure||{},bench=parts.ai_benchmark_evidence||{};
 const box=document.createElement('section');box.className='myf-best-match';box.setAttribute('aria-label','Best Match evidence');
 const scoreRow=document.createElement('div');scoreRow.className='myf-evidence-score';
 bmText(scoreRow,'strong',result.score===null?'Not enough evidence':`${result.score} points`);
 bmText(scoreRow,'span',`${result.component_coverage?.available||0} of ${result.component_coverage?.total||3} factors supported`);
 box.appendChild(scoreRow);
 const grid=document.createElement('div');grid.className='myf-evidence-grid';
 const matched=career.skill_coverage||{};
 bmMetric(grid,'Skill links',`${matched.matched_count||0} of ${matched.total_count||0} exact ESCO links`);
 bmMetric(grid,'AI task exposure',task.status==='available'?`${task.exposure_share}% E1+E2 · ${task.numerator}/${task.denominator} tasks`:'Not enough verified data');
 bmMetric(grid,'AI benchmark evidence','Not linked to career tasks');
 box.appendChild(grid);
 const details=document.createElement('details');details.className='myf-evidence-details';
 bmText(details,'summary','Why this career?');
 const body=document.createElement('div');body.className='myf-evidence-detail-body';
 const group=result.evidence_group||{};
 bmText(body,'p',`Compared within “${group.label||'this evidence group'}” only. ${result.profile_note||''}`);
 bmText(body,'p','Points summarize the available evidence. They are not a probability, qualification, proficiency or employment prediction.');
 const list=document.createElement('ul');
 for(const [key,label] of [['skill_compatibility','Skill compatibility'],['ai_task_exposure','AI task exposure'],['ai_benchmark_evidence','AI benchmark evidence']]){
  const part=parts[key]||{},li=document.createElement('li');
  let text=`${label}: `;
  if(part.status==='available'){
   if(key==='skill_compatibility'){
    const rel=(part.relation_coverage||[]).map(r=>`${r.relation} ${r.matched_count}/${r.total_count}`).join(', ');
    text+=`${rel||'ESCO skill links'}; score weight ${Number(part.applied_weight||0).toFixed(1)}%.`;
   }else if(key==='ai_task_exposure'){
    text+=`${part.exposure_share}% predicted E1+E2 task share (${part.numerator}/${part.denominator}); ${part.source||'verified task inventory'}. This is not replacement probability.`;
   }else text+=`included at ${Number(part.applied_weight||0).toFixed(1)}%.`;
  }else{
   text+=part.reason||'Not available; omitted rather than treated as zero.';
  }
  if(part.status==='available'&&Number(part.effective_weight)===0)text+=' Supported, but not weighted by the current configuration.';
  li.textContent=text;list.appendChild(li);
 }
 body.appendChild(list);
 details.appendChild(body);box.appendChild(details);
 return box;
}
let mfSort='best_match';
function mfDrawSort(rank){
 const host=$('mf-sort');host.replaceChildren();if(!rank)return;
 const grp=document.createElement('div');grp.className='ft-sort';grp.setAttribute('role','group');grp.setAttribute('aria-label','Sort jobs');
 const order=['best_match','lower_exposure'];
 const options=(rank.options||[]).filter(o=>order.includes(o.id))
  .sort((a,b)=>order.indexOf(a.id)-order.indexOf(b.id));
 options.forEach(o=>{const b=document.createElement('button');b.type='button';b.textContent=o.label;b.setAttribute('aria-pressed',String(o.id===rank.effective));if(!o.available){b.disabled=true;b.setAttribute('aria-describedby','mf-reason-'+o.id)}else b.addEventListener('click',()=>{mfSort=o.id;state.recommendationsExpanded=false;loadRecommendations()});grp.appendChild(b)});
 host.appendChild(grp);
 options.filter(o=>!o.available).forEach(o=>{const p=document.createElement('p');p.className='ft-reason';p.id='mf-reason-'+o.id;p.textContent=o.label+' unavailable: '+(o.reason||'required evidence is not available.');host.appendChild(p)});
 if(rank.fallback_reason){const p=document.createElement('p');p.className='ft-reason';p.textContent='Showing Best Match. '+rank.fallback_reason;host.appendChild(p)}
  if(rank.effective==='best_match'&&rank.best_match){
   const meta=rank.best_match,details=document.createElement('details');details.className='myf-recommendation-method';
   bmText(details,'summary','How Best Match works');
   const body=document.createElement('div'),w=meta.effective_weights||{};
   bmText(body,'p',`Current weights: Skills ${Number(w.skill_compatibility||0).toFixed(1)} · AI task exposure ${Number(w.ai_task_exposure||0).toFixed(1)} · benchmark evidence ${Number(w.ai_benchmark_evidence||0).toFixed(1)}.`);
   bmText(body,'p','Best Match uses only these three factors. Missing evidence is omitted, never counted as zero. Scores compare only within groups using the same factors.');
   const list=document.createElement('ul');(meta.methodology||[]).forEach(line=>bmText(list,'li',line));body.appendChild(list);
   bmText(body,'p','Measured model benchmarks stay in AI Trends until independently linked to career tasks and human-versus-AI evidence.');
   details.appendChild(body);host.appendChild(details);
  }
}
function renderRecommendations(data){
 $('recommendations').setAttribute('aria-busy','false');
 mfDrawSort(data.ranking);
 state.recommendations=Array.isArray(data.recommendations)?data.recommendations:[];
 $('recommendation-error').hidden=true;
 const statusNode=$('recommendation-state'),statusMessage=recommendationMessage(data);
 statusNode.textContent=statusMessage;statusNode.hidden=!statusMessage;
  const hasInterests=state.preferences.interests.length>0;
  $('rec-summary').hidden=!hasInterests;
   $('rec-summary').textContent='Matched interests are shown as context; they do not add to the Best Match score.';
 const host=$('recommendations');host.replaceChildren();
 if(!state.recommendations.length){
  const box=document.createElement('div');box.className='myf-empty';
  const strong=document.createElement('strong');strong.textContent=data.status==='no_confirmed_skills'?'Start with your Skills Passport':data.status==='no_matches'?'No matches yet':'Keep exploring';box.appendChild(strong);
  const message=document.createElement('span');message.textContent=data.status==='no_confirmed_skills'?'Confirm skills to see occupations linked to your profile.':'Search all career titles, or adjust your interests.';box.appendChild(message);
  if(data.status==='no_confirmed_skills'){const link=document.createElement('a');link.href='/my-career';link.className='btn btn-primary btn-sm';link.style.marginTop='10px';link.textContent='Open My Skills Passport';box.appendChild(document.createElement('br'));box.appendChild(link)}
  if(state.preferences.career_areas.length||state.preferences.interests.length){const clear=document.createElement('button');clear.type='button';clear.className='myf-link';clear.style.marginTop='8px';clear.textContent='Clear interest filters';clear.addEventListener('click',clearFilters);box.appendChild(document.createElement('br'));box.appendChild(clear)}
  host.appendChild(box);$('explore-more').hidden=true;return;
 }
   const visible=state.recommendationsExpanded?state.recommendations:state.recommendations.slice(0,3);
 visible.forEach(career=>{
  const card=document.createElement('article');card.className='myf-rec';
  const main=document.createElement('div');const title=document.createElement('h3');title.textContent=career.title;main.appendChild(title);
  const chips=document.createElement('div');chips.className='myf-chips';
  (career.matched_skills||[]).slice(0,2).forEach(skill=>{const chip=document.createElement('span');chip.className='myf-chip'+(skill.relation==='optional'?' optional':'');chip.textContent=skill.label;chips.appendChild(chip)});

  main.appendChild(chips);
   const interestMatches=Array.isArray(career.interest_matches)?career.interest_matches:[];
   if(interestMatches.length){
    const interestMatch=document.createElement('div');interestMatch.className='myf-interest-match';
    const interestLabel=document.createElement('span');interestLabel.className='myf-interest-match-label';interestLabel.textContent=interestMatches.length===1?'Matched interest':'Matched interests';
    const interestChips=document.createElement('div');interestChips.className='myf-interest-chips';
    interestMatches.forEach(interest=>{const chip=document.createElement('span');chip.className='myf-chip optional';chip.textContent=interest;interestChips.appendChild(chip)});
    interestMatch.append(interestLabel,interestChips);main.appendChild(interestMatch);
   }
  main.appendChild(ftCoverageEl(career));
   if(data.ranking?.effective==='best_match'){
    const best=bestMatchCard(career,data.ranking.best_match);
    if(best)main.appendChild(best);
   }
  if(0){
   const evidence=career.task_exposure,hasData=['available','uncertain_mapping'].includes(evidence.status);
   const note=document.createElement(hasData?'a':'p');note.className='ft-note';note.style.fontSize='12px';
   note.textContent=evidence.status==='available'?'O*NET tasks: '+evidence.classified_task_count+' assessed · exact link':evidence.status==='uncertain_mapping'?'O*NET tasks: possible mapping · inspect evidence':'O*NET tasks: not enough data';
   if(hasData)note.href='/career?occupation_uri='+encodeURIComponent(career.uri);
   main.appendChild(note);
  }
  const actions=document.createElement('div');actions.className='myf-rec-actions';
  const save=document.createElement('button');save.type='button';save.className='myf-icon-btn';const isSaved=state.saved_occupations.includes(career.uri);save.setAttribute('aria-pressed',String(isSaved));save.setAttribute('aria-label',(isSaved?'Remove':'Save')+' '+career.title);save.textContent=isSaved?'✓':'+';save.addEventListener('click',()=>toggleSaved(career.uri));actions.appendChild(save);
  const open=document.createElement('button');open.type='button';open.className='btn btn-primary btn-sm';open.textContent='View Career';open.addEventListener('click',()=>loadDetails(career.uri));actions.appendChild(open);
  card.append(main,actions);host.appendChild(card);
 });
 const more=$('explore-more');more.hidden=state.recommendations.length<=3;more.textContent=state.recommendationsExpanded?'Show fewer':'See more matches';
}
async function loadRecommendations(){
 const status=$('recommendation-state'),host=$('recommendations');
 status.textContent='Loading career ideas…';status.hidden=false;
 $('recommendation-error').hidden=true;host.setAttribute('aria-busy','true');
 const buttons=[...document.querySelectorAll('#mf-sort button')],previousDisabled=buttons.map(button=>[button,button.disabled]);
 buttons.forEach(button=>{button.disabled=true});
 try{renderRecommendations(await request('/api/my-future/recommendations?limit=12&sort='+encodeURIComponent(mfSort)))}
 catch(error){$('recommendation-state').textContent='';$('recommendation-error-text').textContent=error.message;$('recommendation-error').hidden=false}
 finally{host.setAttribute('aria-busy','false');previousDisabled.forEach(([button,disabled])=>{if(button.isConnected)button.disabled=disabled})}
}
function clearFilters(){
 const previous={preferences:JSON.parse(JSON.stringify(state.preferences))};
 state.preferences.career_areas=[];state.preferences.interests=[];
 saveState('Filters cleared.').then(ok=>{if(ok)loadRecommendations();else{state.preferences=previous.preferences;renderPreferences()}});
}
function benchmarkGroups(ai){
 const groups=new Map();
 (Array.isArray(ai?.links)?ai.links:[]).forEach(link=>{
  let task=String(link.task||'').trim();
  if(task.startsWith('(')&&task.endsWith(')'))task=task.slice(1,-1).trim();
  if((task.startsWith('"')&&task.endsWith('"'))||(task.startsWith("'")&&task.endsWith("'")))task=task.slice(1,-1).trim();
  const key=task.toLocaleLowerCase().replace(/\s+/g,' ')||[link.benchmark,link.benchmark_task_id,link.model].join('|');
  if(!groups.has(key))groups.set(key,{task:task||'Task description not provided by the benchmark record.',records:[],skills:[]});
  const group=groups.get(key);group.records.push(link);
  const skillUri=link.skill_uri||'';
  if(skillUri&&!group.skills.some(skill=>skill.uri===skillUri))group.skills.push({uri:skillUri,label:link.skill||skillUri,relation:link.relation||''});
 });
 if(groups.size)return [...groups.values()];
 (Array.isArray(ai?.task_groups)?ai.task_groups:[]).forEach(group=>groups.set([group.benchmark,group.benchmark_task_id,group.model].join('|'),{task:group.task||'Task description not provided by the benchmark record.',records:[group],skills:(group.skills||[]).map(skill=>({uri:skill.skill_uri||'',label:skill.skill||skill.skill_uri||'ESCO skill',relation:skill.relation||''}))}));
 return [...groups.values()];
}
function renderBenchmarkEvidence(ai){
 const groups=benchmarkGroups(ai),note=ai?.note||'Current benchmark baseline; separate from new benchmark advancements.';
 if(!groups.length)return '<section class="myf-detail-section"><h3>AI Career Outlook</h3><div class="myf-context"><strong>Not enough data</strong><p>'+esc(note)+'</p><p>New benchmark advancements are shown separately in <a href="/trends">AI Trends</a>.</p></div></section>';
 const taskHtml=groups.map(group=>{
  const relationships=group.records.map(record=>{
   const verified=record.independently_verified===true;
   const relation=verified?'Independently verified task relationship':record.relationship_type==='semantic_candidate'?'Possible task/skill link · semantic candidate':'Possible relationship · not independently verified';
   const score=record.score!==null&&record.score!==undefined&&record.score!==''?String(record.score)+(record.score_unit?' '+record.score_unit:''):'Not reported';
   const date=record.date_value||record.evaluation_date||record.collected_at||'Not reported';
   const dateLabel=record.date_label||'Date';
   const source=record.source_url&&/^https?:\/\//i.test(record.source_url)?'<a class="myf-benchmark-source" href="'+esc(record.source_url)+'" target="_blank" rel="noopener noreferrer">'+esc(record.benchmark||record.source||'Benchmark source')+' ↗</a>':'<span class="myf-benchmark-source">'+esc(record.benchmark||record.source||'Benchmark source not reported')+'</span>';
   return '<div class="myf-benchmark-meta">'+source+(record.model?'<span>Model · '+esc(record.model)+'</span>':'')+'<span>Result · '+esc(score)+'</span><span>'+esc(dateLabel)+' · '+esc(date)+'</span>'+(record.capability?'<span>Capability · '+esc(record.capability)+'</span>':'')+'<span>'+esc(relation)+'</span></div>';
  }).join('');
  const skillList=group.skills.length?'<div class="myf-benchmark-skills">'+group.skills.map(skill=>'<span>'+esc(skill.label)+(skill.relation?' · '+esc(skill.relation):'')+'</span>').join('')+'</div>':'<p class="myf-disclaimer">No occupation skills are linked to this task record.</p>';
  return '<article class="myf-benchmark-task"><h4>'+esc(group.task)+'</h4>'+relationships+'<div><small>Associated skills</small>'+skillList+'</div></article>';
 }).join('');
 return '<section class="myf-detail-section"><h3>AI Career Outlook</h3><div class="myf-context"><p>'+esc(note)+'</p><p>These benchmark results describe model performance on named tasks, not the likelihood of automating this career. Possible semantic matches are not verified workplace impacts.</p><p>New benchmark advancements are separate in <a href="/trends">AI Trends</a>.</p></div><details class="myf-disclosure"><summary>View supporting research · '+groups.length+' task groups</summary><div class="myf-disclosure-body"><div class="myf-benchmark-list">'+taskHtml+'</div></div></details></section>';
}
function renderWorkforceContext(context){
 if(!context)return '';
 let detail='';
 if(context.status==='broad_context'&&context.employment_change_pct!==null&&context.employment_change_pct!==undefined)detail='<p><strong>'+esc(context.group||'Broad occupational group')+'</strong> · '+esc(context.employment_change_pct)+'% change'+(context.latest_date?' · '+esc(context.latest_date):'')+'</p>';
 else detail='<p><strong>Not enough data</strong></p>';
 return '<section class="myf-detail-section"><h3>Workforce context</h3><div class="myf-context">'+detail+'<p>'+esc(context.note||'Broad group context only; not an exact-career hiring trend or forecast.')+'</p></div></section>';
}
function skillRow(skill,relation,occupationUri,includeActions=true){
 const uri=skill.uri||'',label=skill.label||'Occupation skill',isGoal=(state.roadmap_goals[occupationUri]||[]).includes(uri);
 const actions=includeActions?'<div class="myf-skill-actions"><button class="btn btn-ghost btn-sm" type="button" data-action="known" data-label="'+esc(label)+'">I already know this</button><button class="btn btn-ghost btn-sm" type="button" data-action="plan" data-uri="'+esc(uri)+'" data-career="'+esc(occupationUri)+'">'+(isGoal?'Remove from plan':'Add to plan')+'</button></div>':'';
 return '<div class="myf-skill-row"><div class="myf-skill-name">'+esc(label)+'<small class="myf-skill-meta">'+esc(relation==='essential'?'Core occupation association':'Additional occupation association')+'</small></div>'+actions+'</div>';
}
function renderDetailBase(detail){
 state.details=detail;state.detailsByUri[detail.occupation.uri]=detail;
 const host=$('career-detail'),occupation=detail.occupation,uri=occupation.uri;
 const matched=[...(detail.matched_essential||[]),...(detail.matched_optional||[])];
 const missing=[...(detail.missing_essential||[]).map(item=>({...item,relation:'essential'})),...(detail.missing_optional||[]).map(item=>({...item,relation:'optional'}))];
 const allSkills=[...matched.map(item=>({...item,relation:(detail.matched_essential||[]).some(s=>s.uri===item.uri)?'essential':'optional',confirmed:true})),...missing];
 const byUri=new Map(allSkills.map(item=>[item.uri,item]));
 const goals=state.roadmap_goals[uri]||detail.roadmap_goals||[];
 const matchCount=Number(detail.skill_coverage?.matched_count||0),totalCount=Number(detail.skill_coverage?.total_count||0);
 const matchText=matchCount?matchCount+' confirmed skill'+(matchCount===1?' is':'s are')+' also listed for this career.':'No confirmed skills match the listed skills yet.';
 const matchedPills=matched.length?'<div class="myf-matches">'+matched.slice(0,6).map(item=>'<span class="myf-chip">'+esc(item.label)+'</span>').join('')+(matched.length>6?'<span class="myf-chip optional">+'+(matched.length-6)+' more</span>':'')+'</div>':'<p class="myf-disclaimer">No matching confirmed skills yet. This does not assess your overall fit.</p>';
 const initialRows=missing.slice(0,4).map(item=>skillRow(item,item.relation,uri)).join('');
 const fullRows=missing.map(item=>skillRow(item,item.relation,uri)).join('');
 const goalItems=goals.map(skillUri=>byUri.get(skillUri)).filter(Boolean);
 host.hidden=false;
 host.innerHTML='<div class="myf-detail-top"><div><div class="eyebrow">Career overview</div><h2>'+esc(occupation.label)+'</h2><p class="myf-detail-copy">'+esc(occupation.description||'A short description is not available for this career.')+'</p></div><button type="button" class="myf-link" id="close-detail">Back to '+(state.previousTab==='saved'?'Saved Careers':state.previousTab==='learning'?'My Learning Plan':'Discover')+'</button></div>'+
  '<section class="myf-detail-section"><h3>Matching Skills</h3><p>'+esc(matchText)+'</p>'+matchedPills+'<details class="myf-disclosure"><summary>How was this matched?</summary><div class="myf-disclosure-body"><p>'+esc(detail.why||'Matching uses exact confirmed ESCO skill IDs and occupation-skill relations.')+'</p><p>'+(totalCount?esc(String(matchCount)+' exact matches among '+String(totalCount)+' listed occupation skills. This is not a readiness or employment score.'):'Not enough occupation-skill data to calculate overlap.')+'</p><p>Interest choices guide exploration but do not create a match.</p></div></details></section>'+
  '<section class="myf-detail-section"><h3>Skills to Learn</h3><p class="myf-disclaimer">These are associated with the occupation and are not confirmed in your Passport. That does not mean you lack them.</p>'+
  (initialRows||'<div class="myf-empty"><strong>No unconfirmed skills listed</strong>You can still explore the career and review its evidence.</div>')+
  (missing.length>4?'<details class="myf-disclosure"><summary>View all occupation skills</summary><div class="myf-disclosure-body"><h4>More skills associated with this career</h4>'+fullRows+'</div></details>':'')+
   '</section>'+
  '<details class="myf-disclosure"><summary>View all skill associations</summary><div class="myf-disclosure-body"><div class="myf-skill-columns"><section><h3>Skills you’ve confirmed</h3>'+matched.map(item=>'<span class="myf-chip">'+esc(item.label)+'</span>').join('')+'</section><section><h3>More skills associated with this career</h3>'+fullRows+'</section></div><p class="myf-disclaimer">Occupation skill labels are general associations, not a complete hiring checklist.</p></div></details>'+
  '<section class="myf-detail-section"><h3>My Learning Plan</h3><p class="myf-disclaimer">'+(goalItems.length?goalItems.length+' selected goal'+(goalItems.length===1?'':'s')+' for this career.':'Choose a few occupation skills to focus on.')+' Progress is saved separately from your Passport.</p><button class="btn btn-ghost btn-sm" type="button" id="detail-add-plan">Choose learning goals</button></section>'+
  renderBenchmarkEvidence(detail.ai_impact)+renderWorkforceContext(detail.job_demand);
 $('close-detail').addEventListener('click',()=>{host.hidden=true;$('dashboard-area').hidden=false;setTab(state.previousTab);history.replaceState(null,'',location.pathname)});
 $('detail-add-plan').addEventListener('click',()=>{state.learningCareerUri=uri;setTab('learning')});
 host.querySelectorAll('[data-action="known"]').forEach(button=>button.addEventListener('click',()=>{window.location.href='/my-career?skill='+encodeURIComponent(button.dataset.label||'')}));
 host.querySelectorAll('[data-action="plan"]').forEach(button=>button.addEventListener('click',()=>toggleRoadmapGoal(button.dataset.career,button.dataset.uri)));
}
function stressChips(items){return (items||[]).map(i=>'<span class="myf-chip optional">'+esc(i.label)+'</span>').join('')}
function stressList(items){return items&&items.length?'<ul class="myf-stress-list">'+items.map(i=>'<li>'+esc(i)+'</li>').join('')+'</ul>':'<p class="myf-disclaimer">Nothing listed for this scenario.</p>'}
function renderDetail(detail){
 renderDetailBase(detail);
 if(state.stress.open&&state.preferences.target_occupation_uri===uri)renderStress(detail);else{if(state.stress.open)state.stress.open=false;pgMount(detail)}
}
function openStress(uri){
 state.stress.prompt=false;state.stress.open=false;pg.mode='sim';pg.simIntent=true;
 $('dashboard-area').hidden=true;$('career-detail').hidden=false;
 if(state.details?.occupation.uri===uri){renderDetail(state.details);const b=$('playground');if(b)b.scrollIntoView({block:'start'})}else loadDetails(uri);
}
function insuranceSkill(p,goals,done,uri,group){
  const inPlan=goals.includes(p.uri),isDone=done.includes(p.uri),why=p.why||{};
  const list=(a)=>(a&&a.length)?a.map(esc).join(', '):'None found';
  const others=(p.other_careers||[]).length?'<div class="myf-chips">'+stressChips(p.other_careers)+'</div>':'<p>No other listed careers.</p>';
  const detailsHtml='<details class="myf-disclosure"><summary>Why this recommendation?</summary><div class="myf-disclosure-body">'+(p.description?'<p><strong>Official ESCO description:</strong> '+esc(p.description)+'</p>':'<p>No official ESCO description is available.</p>')+'<p>Relation in occupation data: '+esc(p.relation==='optional'?'optional':'essential')+'. This is not a mandatory employer requirement.</p><p>Heuristic theme: '+esc(p.theme||'Not assigned')+' (a grouping rule, not an ESCO category).</p><p>Label word overlap: '+list(why.label_overlap)+'</p><p>Description word overlap: '+list(why.description_overlap)+'</p>'+(why.diversity_note?'<p>'+esc(why.diversity_note)+'</p>':'')+'<p>Shared with '+Number(p.shared_career_count||0)+' of '+Number(p.comparison_denominator||0)+' compared careers.</p>'+others+'</div></details>';
  return '<article class="myf-ins-card"><div><h4>'+esc(p.label)+'</h4><div class="myf-chips"><span class="myf-chip optional">Not yet confirmed</span>'+(inPlan?'<span class="myf-chip">'+(isDone?'Step completed':'In your learning plan')+'</span>':'')+'</div>'+(p.reason?'<p class="myf-reason">'+esc(p.reason)+'</p>':'')+detailsHtml+'</div><div class="myf-skill-actions"><button type="button" class="btn '+(inPlan?'btn-ghost':'btn-primary')+' btn-sm" data-ins="'+esc(p.uri)+'" aria-pressed="'+inPlan+'">'+(inPlan?'Remove from plan':'Add to plan')+'</button><button type="button" class="btn btn-ghost btn-sm" data-known="'+esc(p.label)+'">I already have this skill</button></div></article>';
}
function insuranceGroup(title,sub,items,goals,done,uri,key,comparisonCount=0){
  const list=(items||[]).slice(0,3);
  return '<section class="myf-ins-group" aria-label="'+esc(title)+'"><h3>'+esc(title)+'</h3><p class="myf-disclaimer">'+esc(sub)+'</p>'+(list.length?list.map(p=>insuranceSkill(p,goals,done,uri,key)).join(''):'<div class="myf-empty"><strong>Nothing to suggest here</strong>'+(key==='options'?(comparisonCount?'No not-yet-confirmed target skills are shared with these comparison careers.':'No careers are selected for comparison.'):'This career has no not-yet-confirmed skills listed in occupation data.')+'</div>')+'</section>';
}
function insuranceComparison(ins,uri){
  const c=ins.comparison||{},alts=c.alternatives||[],sugg=(c.suggestions||[]).filter(x=>!alts.some(a=>a.uri===x.uri));
  const chips=alts.length?alts.map((a,i)=>'<span class="myf-chip optional myf-cmp-chip">'+esc(a.label)+'<button type="button" class="myf-link" data-cmp-replace="'+i+'" aria-label="Replace '+esc(a.label)+'">Replace</button><button type="button" class="myf-link" data-cmp-remove="'+esc(a.uri)+'" aria-label="Remove '+esc(a.label)+' from comparison">Remove</button></span>').join(''):'<p class="myf-disclaimer">No careers selected. Skill sharing is not compared.</p>';
  const sg=(alts.length?'<details class="myf-disclosure"><summary>Why these comparison careers?</summary><div class="myf-disclosure-body">'+alts.map(a=>'<p><strong>'+esc(a.label)+'</strong> shares '+Number(a.shared_skill_count||0)+' of your target’s '+Number(a.target_skill_count||0)+' listed ESCO skills. '+(a.shared_skill_count?'':'No exact overlap was found. ')+'Selection basis: '+esc((a.source||'esco_overlap').replaceAll('_',' '))+'.'+((a.interest_matches||[]).length?' Matching interest text: '+a.interest_matches.map(esc).join(', ')+'.':'')+'</p>').join('')+'<p>Exact occupation-skill overlap is not a prediction of an achievable career transition or future demand.</p></div></details>':'')+(sugg.length?'<p class="myf-disclaimer">Suggested careers to compare</p><div class="myf-chips">'+sugg.slice(0,5).map(x=>'<button type="button" class="btn btn-ghost btn-sm" data-cmp-add="'+esc(x.uri)+'" data-label="'+esc(x.label)+'"'+(alts.length>=5?' disabled':'')+'>Add '+esc(x.label)+'</button>').join('')+'</div>':'');
  return '<section class="myf-ins-group" id="ins-compare"><h3>Careers compared</h3><p class="myf-disclaimer">'+(c.mode==='user_selected'?'You chose these careers.':'This is a provisional starting set, not the best paths for you.')+' Compared against '+Number(c.denominator||alts.length)+' career'+(Number(c.denominator||alts.length)===1?'':'s')+' (max 5).'+(c.note?' '+esc(c.note):'')+'</p><div class="myf-chips" id="insurance-selected">'+chips+'</div>'+sg+'<div class="myf-search" style="margin-top:10px"><label class="myf-skill-meta" for="insurance-career-search">Search ESCO careers to add or replace</label><input id="insurance-career-search" type="search" maxlength="100" placeholder="Search career titles" aria-autocomplete="list" aria-expanded="false" aria-controls="insurance-career-results"><div id="insurance-career-results" class="myf-search-results" role="listbox" hidden></div></div><p id="insurance-career-status" class="myf-status" role="status" aria-live="polite"></p>'+(c.mode==='user_selected'?'<button type="button" class="myf-link" id="insurance-reset">Reset to suggested</button>':'')+((ins.methodology||[]).length?'<details class="myf-disclosure"><summary>Methodology</summary><div class="myf-disclosure-body">'+stressList(ins.methodology)+'</div></details>':'')+'</section>';
}
let insuranceBusy=false,insuranceReplace=-1;
async function saveInsuranceSelection(uri,next){
  if(insuranceBusy)return;insuranceBusy=true;
  const had=Object.prototype.hasOwnProperty.call(state.insurance_alternatives,uri),old=had?[...state.insurance_alternatives[uri]]:null;
  if(next===null)delete state.insurance_alternatives[uri];else state.insurance_alternatives[uri]=next;
  const ok=await saveState(next===null?'Comparison reset to suggested.':'Comparison saved.');
  insuranceBusy=false;
  if(ok){loadDetails(uri)}
  else{if(had)state.insurance_alternatives[uri]=old;else delete state.insurance_alternatives[uri];if(state.details?.occupation.uri===uri)renderDetail(state.details)}
}
function wireInsuranceComparison(detail,ins){
  const uri=detail.occupation.uri,host=$('career-detail'),alts=(ins.comparison||{}).alternatives||[];
  insuranceReplace=-1;
  if(!$('insurance-career-search'))return;
  const current=()=>{const saved=state.insurance_alternatives[uri];return Array.isArray(saved)?[...saved]:alts.map(a=>a.uri)};
  const status=t=>{$('insurance-career-status').textContent=t};
  host.querySelectorAll('[data-cmp-remove]').forEach(b=>b.addEventListener('click',()=>saveInsuranceSelection(uri,current().filter(x=>x!==b.dataset.cmpRemove))));
  host.querySelectorAll('[data-cmp-replace]').forEach(b=>b.addEventListener('click',()=>{insuranceReplace=Number(b.dataset.cmpReplace);status('Search for a career to replace '+(alts[insuranceReplace]?.label||'this one')+'.');$('insurance-career-search').focus()}));
  const add=(u)=>{
   const list=current();
   if(u===uri){status('This is your goal career; choose a different one.');return}
   if(list.includes(u)){status('Already in the comparison.');return}
   if(insuranceReplace>=0&&insuranceReplace<list.length){list[insuranceReplace]=u}
   else if(list.length>=5){status('Up to 5 careers. Remove or replace one first.');return}
   else list.push(u);
   insuranceReplace=-1;saveInsuranceSelection(uri,list);
  };
  host.querySelectorAll('[data-cmp-add]').forEach(b=>b.addEventListener('click',()=>add(b.dataset.cmpAdd)));
  const reset=$('insurance-reset');if(reset)reset.addEventListener('click',()=>saveInsuranceSelection(uri,null));
  wireOccupationSearch('insurance-career-search','insurance-career-results','insurance-career-status',item=>{$('insurance-career-search').value='';add(item.uri)});
}
function taskExamples(sc){
 const ex=Array.isArray(sc.occupational_task_examples)?sc.occupational_task_examples:[];
 if(!ex.length)return '<p class="myf-disclaimer">No exact-linked occupational task examples are available for this scenario.</p>';
 return '<details class="myf-method-details"><summary>Occupational task context ('+ex.length+')</summary><p class="myf-disclaimer">Source task examples for context only. They are not declared automatable by their E0/E1/E2 class, and no future outcome is estimated.</p>'+ex.slice(0,6).map(t=>'<div class="myf-benchmark-task"><h4>'+esc(t.text)+'</h4><div class="myf-benchmark-meta"><span>Class '+esc(t.predicted_class||'unlabelled')+' (model output)</span><span>O*NET-SOC '+esc(t.onet_soc_code)+'</span><span>Task '+esc(t.task_id)+'</span>'+(t.relationship?'<span>'+esc(t.relationship)+'</span>':'')+'</div>'+(t.source?'<p class="myf-disclaimer">Source: '+esc(t.source)+'</p>':'')+'</div>').join('')+'</details>';
}
function renderStress(detail){
 renderStressBase(detail);
 const host=$('career-detail'),te=detail.task_exposure,box=document.createElement('div');box.className='myf-context';box.style.margin='10px 0';
 const L=['E0','E1','E2'];
 if(te&&te.status==='available'&&te.distribution)box.textContent='Task evidence: '+L.map(l=>l+' '+te.distribution[l].count+' of '+te.sample_task_count).join(', ')+' classified O*NET tasks (unweighted counts, three unordered classes). Scenarios below are assumptions to explore; no future numbers are predicted here.';
 else box.textContent='Task evidence: not enough exact task data for this career. Scenarios below are assumptions, not forecasts.';
 const first=host.querySelector('.myf-detail-top');if(first)first.after(box);else host.prepend(box);
}
function renderStressBase(detail){
 const host=$('career-detail'),st=detail.stress_test,uri=detail.occupation.uri,label=detail.occupation.label;
 host.hidden=false;
 const back='<button type="button" class="myf-link" id="stress-back">Back to career overview</button>';
 if(!st||!Array.isArray(st.scenarios)||!st.scenarios.length){host.innerHTML='<div class="myf-detail-top"><div><div class="eyebrow">Career Stress Test</div><h2>'+esc(label)+'</h2></div>'+back+'</div><div class="myf-empty"><strong>Stress test not available</strong>Scenario details could not be loaded for this career.</div>';
  host.querySelector('#stress-back').addEventListener('click',()=>{state.stress.open=false;renderDetail(detail)});return}
 let sc=st.scenarios.find(x=>x.id===state.stress.scenario);if(!sc){sc=st.scenarios[0];state.stress.scenario=sc.id}
 const goals=state.roadmap_goals[uri]||[],done=state.roadmap_progress[uri]||[];
 const tabs=st.scenarios.map(x=>'<button type="button" data-sc="'+esc(x.id)+'" aria-pressed="'+(x.id===sc.id)+'">'+esc(x.label)+'</button>').join('');
 const wf=sc.workflow||{},steps=Array.isArray(wf.steps)?wf.steps:[];
 const wfHtml=steps.length?'<ol class="myf-wf">'+steps.map(x=>'<li><strong>'+esc(x.label)+'</strong><p>'+esc(x.assistance||'')+'</p><p class="myf-disclaimer">Review: '+esc(x.review||'Check the result yourself before using it.')+'</p></li>').join('')+'</ol>':'<p class="myf-disclaimer">No practice workflow steps are available for this scenario.</p>';
 const wfNote='<p class="myf-disclaimer">'+esc(wf.note||'Hypothetical practice workflow, not an observed job workflow or measured adoption.')+(sc.assistance_summary?' '+esc(sc.assistance_summary):'')+'</p>';
 const changes=(sc.changes||[]).length?(sc.changes).map(c=>'<div class="myf-benchmark-task"><h4>'+esc(c.task)+'</h4><p class="myf-disclaimer">Candidate link, not verified: '+esc(c.relationship)+'</p>'+((c.skills||[]).length?'<div class="myf-benchmark-skills">'+c.skills.map(k=>'<span>'+esc(k.label)+'</span>').join('')+'</div>':'')+'</div>').join(''):'<p class="myf-disclaimer">No linked task examples were identified for this scenario.</p>';
 const wfDetail='<details class="myf-disclosure"><summary>Candidate task examples ('+(sc.changes||[]).length+')</summary><div class="myf-disclosure-body"><p>Unverified candidate links to benchmark task descriptions. They do not show what any tool can do in this career.</p><div class="myf-benchmark-list">'+changes+'</div></div></details>';
 const confirmedValuable=(sc.valuable||[]).filter(v=>state.confirmed_skills.some(c=>c.uri&&c.uri===v.uri));
 const valuable=(confirmedValuable.length?confirmedValuable.map(v=>'<div class="myf-skill-row"><div class="myf-skill-name">'+esc(v.label)+'<small class="myf-skill-meta">Confirmed in your Passport'+(Number(v.shared_career_count)?' · also listed for '+Number(v.shared_career_count)+' other career'+(Number(v.shared_career_count)===1?'':'s'):'')+'</small></div></div>').join(''):'<p class="myf-disclaimer">None of the skills listed here are confirmed in your Passport yet. Skills not recorded are not absent from your experience.</p>')+'<p class="myf-disclaimer">Core learning options below stay consistent across scenarios.</p>';
 const wfEvidence=steps.length||sc.profile?'<h4>Scenario workflow details</h4>'+(sc.profile?'<p>Profile: '+esc(sc.profile.scope||'')+' Up to '+Number(sc.profile.max_workflow_steps||0)+' workflow steps and '+Number(sc.profile.max_task_examples||0)+' task examples. This is a display setting, not a measurement.</p>':'')+steps.map(x=>'<details class="myf-disclosure"><summary>'+esc(x.label)+' · official ESCO '+esc(x.relation==='optional'?'optional':'essential')+' skill</summary><div class="myf-disclosure-body"><p>'+esc(x.description||'No official description available.')+'</p>'+((x.linked_tasks||[]).length?'<p>Unverified candidate task links:</p>'+x.linked_tasks.map(t=>'<p>'+esc(t.task)+' · '+esc(t.relationship||'')+'</p>').join(''):'')+'</div></details>').join(''):'';
 const ins=st.insurance||{};const groupsHtml=insuranceGroup('Prepare for My Career','Skills linked to this career in occupation data.',ins.prepare,goals,done,uri,'prepare')+insuranceGroup('Keep My Options Open','Skills that also appear across related careers.',ins.options,goals,done,uri,'options',ins.comparison?.denominator||0);
 const ev=st.evidence||{},lm=(ev.labour_market||[]).map(x=>'<p><strong>'+esc(x.label)+'</strong>: '+esc(x.status==='unavailable'?'Data not available':x.status)+'. '+esc(x.note)+'</p>').join('');
 const evidence='<details class="myf-method-details" id="stress-evidence"'+(state.stress.evidence?' open':'')+'><summary>View Evidence</summary><div class="myf-disclosure-body"><p><strong>Official ESCO relations:</strong> occupation-skill links and skill descriptions come from ESCO.</p><p><strong>Measured benchmark results:</strong> scores describe model performance on named benchmark tasks only.</p><p><strong>Unverified MiniLM links:</strong> task-to-skill matches from a text-similarity model are candidates, not verified.</p><p><strong>Hypothetical scenarios:</strong> assumptions and practice workflows to explore, not forecasts or observed workflows.</p><p><strong>Broad-group labour context:</strong> group-level data, not an exact-career trend.</p><p><strong>No verified outcomes:</strong> nothing here verifies hiring, pay, or employment results.</p>'+wfEvidence+'<h4>Methodology</h4>'+stressList(ev.methodology)+(ev.scenario_assumptions_source?'<p>Scenario assumptions: '+esc(ev.scenario_assumptions_source)+'</p>':'')+'<h4>Labour market evidence</h4>'+(lm||'<p>No labour market evidence is available.</p>')+((ev.related_careers||[]).length?'<h4>Related careers</h4><div class="myf-chips">'+stressChips(ev.related_careers)+'</div>':'')+'</div>'+renderBenchmarkEvidence(ev.benchmark_baseline||detail.ai_impact)+renderWorkforceContext(ev.workforce_context||detail.job_demand)+'</details>';
 host.innerHTML='<div class="myf-detail-top"><div><div class="eyebrow">Career Stress Test</div><h2>'+esc(label)+'</h2><p class="myf-detail-copy">'+esc(st.notice||'Hypothetical scenarios for exploration, not predictions.')+'</p></div>'+back+'</div>'+
 '<div class="myf-scenario-tabs" role="group" aria-label="Scenario">'+tabs+'</div><div class="myf-scenario-copy"><strong>'+esc(sc.label)+'</strong><br>'+esc(sc.assumption)+'</div>'+taskExamples(sc)+
 '<section class="myf-detail-section"><h3>What could change?</h3>'+wfHtml+wfNote+wfDetail+'</section>'+
 '<section class="myf-detail-section"><h3>What might remain useful?</h3>'+valuable+'</section>'+
 '<section class="myf-detail-section"><h3>What can I do to prepare?</h3>'+stressList((sc.prepare||[]).slice(0,4))+'</section>'+
 '<section class="myf-detail-section"><h3>My Career Insurance Plan</h3><p class="myf-disclaimer">'+esc(st.insurance?.notice||'')+' This is learning preparation only. It is not a financial product or a guarantee.</p>'+groupsHtml+insuranceComparison(ins,uri)+'<div class="myf-detail-actions"><button type="button" class="btn btn-ghost btn-sm" id="stress-plan">Open My Learning Plan</button></div></section>'+
 '<details class="myf-method-details"><summary>Where evidence is insufficient</summary>'+stressList(sc.limitations)+'</details>'+evidence;
 host.querySelector('#stress-back').addEventListener('click',()=>{state.stress.open=false;renderDetail(detail)});
 host.querySelectorAll('[data-sc]').forEach(b=>b.addEventListener('click',()=>{state.stress.scenario=b.dataset.sc;renderStress(detail)}));
  host.querySelectorAll('[data-known]').forEach(b=>b.addEventListener('click',()=>{window.location.href='/my-career?skill='+encodeURIComponent(b.dataset.known||'')}));
  wireInsuranceComparison(detail,ins);
  host.querySelectorAll('[data-ins]').forEach(b=>b.addEventListener('click',()=>{b.disabled=true;toggleRoadmapGoal(uri,b.dataset.ins)}));
 host.querySelector('#stress-plan').addEventListener('click',()=>{state.learningCareerUri=uri;setTab('learning')});
 host.querySelector('#stress-evidence').addEventListener('toggle',e=>{state.stress.evidence=e.target.open});
}
async function loadDetails(uri){
 state.previousTab=state.activeTab;$('dashboard-area').hidden=true;
 const host=$('career-detail');host.hidden=false;host.innerHTML='<div class="skel" style="height:24px;width:45%"></div><div class="skel" style="height:90px;margin-top:15px"></div>';
 try{const data=await request('/api/my-future/career?uri='+encodeURIComponent(uri));renderDetail(data);history.replaceState(null,'',location.pathname+'?career='+encodeURIComponent(uri))}
 catch(error){host.innerHTML='<div class="myf-error myf-detail-error">'+esc(error.message)+' <button type="button" class="btn btn-ghost btn-sm" id="detail-retry">Try again</button> <button type="button" class="btn btn-ghost btn-sm" id="detail-back">Back</button></div>';host.querySelector('#detail-retry').addEventListener('click',()=>loadDetails(uri));host.querySelector('#detail-back').addEventListener('click',()=>{host.hidden=true;$('dashboard-area').hidden=false;history.replaceState(null,'',location.pathname);setTab(state.previousTab)})}
}
async function toggleSaved(uri,reloadDetail=false){
 const old=[...state.saved_occupations],oldTarget=state.preferences.target_occupation_uri;
 const next=new Set(state.saved_occupations);next.has(uri)?next.delete(uri):next.add(uri);state.saved_occupations=[...next];
 if(!state.saved_occupations.includes(uri)&&state.preferences.target_occupation_uri===uri)state.preferences.target_occupation_uri=null;
 if(await saveState(state.saved_occupations.includes(uri)?'Career saved.':'Career removed.')){loadRecommendations();if(reloadDetail)loadDetails(uri)}
 else{state.saved_occupations=old;state.preferences.target_occupation_uri=oldTarget;renderSaved();renderPreferences()}
}
async function setTarget(uri,reloadDetail=false,navigateToPlan=false){
 const old=[...state.saved_occupations],oldTarget=state.preferences.target_occupation_uri;
 state.preferences.target_occupation_uri=uri;state.saved_occupations=[...new Set([...state.saved_occupations,uri])];state.learningCareerUri=uri;
  if(await saveState('Career goal updated.')){loadRecommendations();if(reloadDetail)loadDetails(uri);if(navigateToPlan)setTab('learning');else if(state.activeTab==='learning')loadLearningCareer(uri)}
 else{state.saved_occupations=old;state.preferences.target_occupation_uri=oldTarget;renderSaved();renderPreferences()}
}
let roadmapBusy=false;
async function toggleRoadmapGoal(occupationUri,skillUri){
 if(!occupationUri||!skillUri||roadmapBusy)return;
 roadmapBusy=true;
 const oldProgress=JSON.parse(JSON.stringify(state.roadmap_progress)),old=JSON.parse(JSON.stringify(state.roadmap_goals)),goals=new Set(state.roadmap_goals[occupationUri]||[]);
 try{
 if(goals.has(skillUri)){goals.delete(skillUri);state.roadmap_progress[occupationUri]=(state.roadmap_progress[occupationUri]||[]).filter(uri=>uri!==skillUri)}else goals.add(skillUri);
 state.roadmap_goals[occupationUri]=[...goals];
 if(await saveState('Learning plan updated.')){roadmapBusy=false;if(state.details?.occupation.uri===occupationUri)loadDetails(occupationUri);if(state.learningCareerUri===occupationUri)loadLearningCareer(occupationUri)}
 else{state.roadmap_goals=old;state.roadmap_progress=oldProgress;if(state.details?.occupation.uri===occupationUri)renderDetail(state.details);if(state.learningCareerUri===occupationUri&&state.learningDetails)renderLearning(state.learningDetails)}
 }finally{roadmapBusy=false}
}
async function toggleProgress(occupationUri,skillUri,complete){
 const old=JSON.parse(JSON.stringify(state.roadmap_progress)),steps=new Set(state.roadmap_progress[occupationUri]||[]);
 complete?steps.add(skillUri):steps.delete(skillUri);state.roadmap_progress[occupationUri]=[...steps];
 if(await saveState(complete?'Progress saved.':'Step reopened.'))loadLearningCareer(occupationUri);
 else{state.roadmap_progress=old;if(state.learningDetails)renderLearning(state.learningDetails)}
}
function renderPlanRow(skill,occupationUri,complete,confirmed=false){
 const row=document.createElement('div');row.className='myf-roadmap-row'+(complete?' done':'');
 if(confirmed){const text=document.createElement('span');text.textContent=skill.label+' · Already in your Passport';row.append(text)}
 else{
  const check=document.createElement('input');check.type='checkbox';check.checked=complete;check.setAttribute('aria-label',(complete?'Reopen ':'Mark ')+skill.label+' as complete');check.addEventListener('change',()=>toggleProgress(occupationUri,skill.uri,check.checked));
  const text=document.createElement('span');text.textContent=skill.label;
  row.append(check,text);
 }
 const remove=document.createElement('button');remove.type='button';remove.className='myf-link';remove.textContent='Remove';remove.setAttribute('aria-label','Remove '+skill.label+' from learning plan');remove.addEventListener('click',()=>toggleRoadmapGoal(occupationUri,skill.uri));
 row.appendChild(remove);return row;
}
function renderLearning(detail){
 state.learningDetails=detail;
 const uri=detail?.occupation?.uri;
 if(!uri){$('learning-empty').hidden=false;$('learning-target').textContent='No career goal selected.';$('learning-active-section').hidden=true;$('learning-completed-section').hidden=true;$('learning-add-section').hidden=true;$('learning-state').textContent='';return}
 $('learning-empty').hidden=true;
 $('learning-target').innerHTML='<strong>My Career Goal</strong> · '+esc(detail.occupation.label)+' <button type="button" class="myf-link" id="learning-view-career">View career</button>';
 $('learning-state').textContent='';
 const all=[...(detail.matched_essential||[]).map(s=>({...s,relation:'essential',confirmed:true})),...(detail.matched_optional||[]).map(s=>({...s,relation:'optional',confirmed:true})),...(detail.learning_roadmap||[])];
 const byUri=new Map(all.map(skill=>[skill.uri,skill]));
 const selected=state.roadmap_goals[uri]||detail.roadmap_goals||[];
 const completed=new Set(state.roadmap_progress[uri]||[]);
 const active=selected.filter(skillUri=>!completed.has(skillUri)).map(skillUri=>byUri.get(skillUri)).filter(Boolean);
 const done=selected.filter(skillUri=>completed.has(skillUri)).map(skillUri=>byUri.get(skillUri)).filter(Boolean);
 const activeHost=$('learning-active-list');activeHost.replaceChildren();
 const visible=state.learningExpanded?active:active.slice(0,5);
 visible.forEach(skill=>activeHost.appendChild(renderPlanRow(skill,uri,false,!!skill.confirmed)));
 $('learning-active-section').hidden=active.length===0;
 $('learning-show-more').hidden=active.length<=5;$('learning-show-more').textContent=state.learningExpanded?'Show fewer':'Show all goals';
 const doneHost=$('learning-completed-list');doneHost.replaceChildren();done.forEach(skill=>doneHost.appendChild(renderPlanRow(skill,uri,true,!!skill.confirmed)));
 $('learning-completed-section').hidden=done.length===0;
 const select=$('learning-skill-select');select.replaceChildren();const first=document.createElement('option');first.value='';first.textContent='Choose a skill';select.appendChild(first);
 (detail.learning_roadmap||[]).filter(skill=>!selected.includes(skill.uri)).forEach(skill=>{const option=document.createElement('option');option.value=skill.uri;option.textContent=skill.label;select.appendChild(option)});
 $('learning-add-section').hidden=select.options.length<=1;
 $('learning-add-goal').disabled=!select.value;
 $('learning-view-career').addEventListener('click',()=>loadDetails(uri));
}
async function loadLearningCareer(uri){
 if(!uri){$('learning-empty').hidden=false;$('learning-target').textContent='No career goal selected.';$('learning-active-section').hidden=true;$('learning-completed-section').hidden=true;$('learning-add-section').hidden=true;return}
 state.learningCareerUri=uri;$('learning-error').hidden=true;$('learning-state').textContent='Loading your plan…';
 try{const detail=await request('/api/my-future/career?uri='+encodeURIComponent(uri));state.detailsByUri[uri]=detail;renderLearning(detail)}
 catch(error){$('learning-state').textContent='';$('learning-error-text').textContent=error.message;$('learning-error').hidden=false}
}
function loadLearning(){const uri=state.learningCareerUri||state.preferences.target_occupation_uri;if(!uri){$('learning-empty').hidden=false;$('learning-target').textContent='No career goal selected.';$('learning-active-section').hidden=true;$('learning-completed-section').hidden=true;$('learning-add-section').hidden=true;return}loadLearningCareer(uri)}
async function addLearningGoal(){
 const skillUri=$('learning-skill-select').value,uri=state.learningCareerUri;
 if(!skillUri||!uri)return;
 const old=JSON.parse(JSON.stringify(state.roadmap_goals)),goals=new Set(state.roadmap_goals[uri]||[]);goals.add(skillUri);state.roadmap_goals[uri]=[...goals];
 $('learning-add-goal').disabled=true;
 if(await saveState('Learning goal added.'))loadLearningCareer(uri);else{state.roadmap_goals=old;if(state.learningDetails)renderLearning(state.learningDetails)}
}
let interestsOpener=null;
function openInterests(focusGoal=false){
 interestsOpener=document.activeElement;
 const categories=selectedCategories(),custom=customInterests();
 state.draft={categories:[...categories],custom:[...custom],areas:[...(state.preferences.career_areas||[])],areasTouched:false,target:state.preferences.target_occupation_uri,targetLabel:careerLabel(state.preferences.target_occupation_uri)};
 $('save-status').textContent='';$('career-goal-search').value='';renderInterestDialog();
 $('interests-dialog').hidden=false;
 (focusGoal?$('career-goal-search'):$('close-interests')).focus();
}
function closeInterests(){
 $('interests-dialog').hidden=true;
 const target=interestsOpener&&interestsOpener.isConnected?interestsOpener:$('tab-discover');
 interestsOpener=null;
 if(target&&typeof target.focus==='function')target.focus();
}
function renderInterestDialog(){
 const host=$('interest-options');host.replaceChildren();
 $('legacy-area-note')?.remove();
 INTEREST_OPTIONS.forEach(item=>{
  const label=document.createElement('label');label.className='myf-interest-option';
  const input=document.createElement('input');input.type='checkbox';input.checked=state.draft.categories.includes(item.label);input.value=item.label;
  input.addEventListener('change',()=>{
   state.draft.categories=input.checked?[...new Set([...state.draft.categories,item.label])]:state.draft.categories.filter(value=>value!==item.label);
   state.draft.areasTouched=true;$('legacy-area-note')?.remove();$('open-to-explore').checked=false;renderOtherInterestChips();renderPreferencesPreview();
  });
  const text=document.createElement('span');text.textContent=item.label;label.append(input,text);host.appendChild(label);
 });
 const mapping=$('interest-mapping-copy');
 mapping.innerHTML=INTEREST_OPTIONS.map(item=>'<p><strong>'+esc(item.label)+'</strong> explores '+esc(item.groups.join('; '))+'.</p>').join('')+'<p>These broad groups are guides, not a one-to-one definition of an interest. The career list still depends on confirmed skill links.</p>';
 $('open-to-explore').checked=state.draft.categories.length===0&&state.draft.custom.length===0&&state.draft.areas.length===0;
 renderOtherInterestChips();
 const current=state.draft.targetLabel||careerLabel(state.draft.target);$('target-display').textContent=state.draft.target?'Selected: '+(current||'Career goal'):'No career goal selected.';
 if(state.draft.areas.length&&!state.draft.categories.length){const note=document.createElement('p');note.className='myf-disclaimer';note.id='legacy-area-note';note.textContent='A previous broad career filter is still active. Choose an interest or clear filters to replace it.';host.parentElement.insertBefore(note,host.nextSibling)}
}
function renderOtherInterestChips(){
 const host=$('other-interest-chips');host.replaceChildren();
 (state.draft?.custom||[]).forEach((value,index)=>{const chip=document.createElement('span');chip.className='myf-chip optional';chip.textContent=value;const remove=document.createElement('button');remove.type='button';remove.className='myf-link';remove.textContent='×';remove.setAttribute('aria-label','Remove '+value);remove.addEventListener('click',()=>{state.draft.custom.splice(index,1);renderOtherInterestChips();renderPreferencesPreview()});chip.appendChild(remove);host.appendChild(chip)});
}
function renderPreferencesPreview(){
 const target=state.draft.targetLabel||careerLabel(state.draft.target);$('target-display').textContent=state.draft.target?'Selected: '+(target||'Career goal'):'No career goal selected.';
}
function addOtherInterest(){
 const input=$('other-interest-input'),value=input.value.trim();if(!value)return;
 if(state.draft.categories.length+state.draft.custom.length>=8){persistStatus('Choose up to 8 interests. ',true);return}
 if(![...state.draft.categories,...state.draft.custom].some(item=>item.toLocaleLowerCase()===value.toLocaleLowerCase()))state.draft.custom.push(value);
 input.value='';$('open-to-explore').checked=false;renderOtherInterestChips();renderPreferencesPreview();
}
async function savePreferences(){
 const draft=state.draft;if(!draft)return;
 const categories=draft.categories,areas=(draft.areasTouched||categories.length)?mappedAreas(categories):draft.areas;
 const previous=JSON.parse(JSON.stringify(state.preferences));
 state.preferences={career_areas:areas,interests:[...categories,...draft.custom],target_occupation_uri:draft.target};
 if(await saveState('Interests saved.')){closeInterests();loadRecommendations();if(state.activeTab==='learning')loadLearning()}
 else{state.preferences=previous;renderPreferences()}
}
async function clearAllInterests(){
 state.draft.categories=[];state.draft.custom=[];state.draft.areas=[];state.draft.areasTouched=true;
 $('open-to-explore').checked=true;
 renderInterestDialog();
}
function wireOccupationSearch(inputId,resultsId,statusId,onChoose){
 const input=$(inputId),box=$(resultsId);let timer=0,controller=null,items=[],active=-1;
 function hide(){box.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant')}
 function choose(index){const item=items[index];if(!item)return;hide();onChoose(item)}
 function draw(suggestions){
  items=suggestions;active=-1;box.replaceChildren();
  suggestions.forEach((item,index)=>{const button=document.createElement('button');button.type='button';button.id=resultsId+'-option-'+index;button.setAttribute('role','option');button.setAttribute('aria-selected','false');const title=document.createElement('strong');title.textContent=item.label;const group=document.createElement('small');group.textContent=item.isco_group_label||'Career title';button.append(title,group);button.addEventListener('mousedown',event=>event.preventDefault());button.addEventListener('click',()=>choose(index));box.appendChild(button)});
  box.hidden=!suggestions.length;input.setAttribute('aria-expanded',String(suggestions.length>0));
 }
 input.addEventListener('input',()=>{
  const query=input.value.trim();clearTimeout(timer);if(controller)controller.abort();
  if(query.length<2){hide();$(statusId).textContent='Enter at least two characters.';return}
  timer=setTimeout(async()=>{
   controller=new AbortController();$(statusId).textContent='Searching careers…';
   try{const data=await request('/api/occupations/search?q='+encodeURIComponent(query)+'&limit=10',{signal:controller.signal});draw(data.suggestions||[]);$(statusId).textContent=items.length?'Choose a matching career title.':'No titles matched. Try another search.'}
   catch(error){if(error.name!=='AbortError')$(statusId).textContent=error.message}
  },220);
 });
 input.addEventListener('keydown',event=>{
  if(event.key==='Escape'){hide();return}
  if(!items.length)return;
  if(event.key==='ArrowDown'){event.preventDefault();active=Math.min(active+1,items.length-1)}
  else if(event.key==='ArrowUp'){event.preventDefault();active=Math.max(active-1,0)}
  else if(event.key==='Enter'&&active>=0){event.preventDefault();choose(active);return}else return;
  box.querySelectorAll('[role=option]').forEach((option,index)=>option.setAttribute('aria-selected',String(index===active)));
  if(active>=0){input.setAttribute('aria-activedescendant',resultsId+'-option-'+active);box.children[active]?.scrollIntoView({block:'nearest'})}
 });
 document.addEventListener('click',event=>{if(!event.target.closest('#'+inputId)?.parentElement?.contains(event.target))hide()});
 return {hide};
}

wireOccupationSearch('career-goal-search','career-goal-results','goal-search-status',item=>{
 if(!state.draft)return;state.draft.target=item.uri;state.draft.targetLabel=item.label;$('career-goal-search').value=item.label;$('goal-search-status').textContent='Career goal selected.';renderPreferencesPreview();
});
$('close-interests').addEventListener('click',closeInterests);$('cancel-interests').addEventListener('click',closeInterests);
$('interests-dialog').addEventListener('click',event=>{if(event.target===$('interests-dialog'))closeInterests()});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!$('interests-dialog').hidden)closeInterests()});
$('open-to-explore').addEventListener('change',event=>{if(event.target.checked){state.draft.categories=[];state.draft.custom=[];state.draft.areas=[];state.draft.areasTouched=true;renderInterestDialog()}});
$('add-other-interest').addEventListener('click',addOtherInterest);$('other-interest-input').addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();addOtherInterest()}});
$('clear-all-interests').addEventListener('click',clearAllInterests);
$('clear-target').addEventListener('click',()=>{state.draft.target=null;state.draft.targetLabel='';$('career-goal-search').value='';$('goal-search-status').textContent='Career goal cleared.';renderPreferencesPreview()});
$('save-preferences').addEventListener('click',savePreferences);
$('clear-interest-filters').addEventListener('click',clearFilters);
$('saved-shortcut').addEventListener('click',()=>setTab('saved'));
document.querySelectorAll('[data-tab]').forEach(button=>button.addEventListener('click',()=>setTab(button.dataset.tab)));
document.querySelectorAll('[data-open-tab]').forEach(button=>button.addEventListener('click',()=>setTab(button.dataset.openTab)));
$('explore-more').addEventListener('click',()=>{state.recommendationsExpanded=!state.recommendationsExpanded;renderRecommendations({recommendations:state.recommendations,status:'ok',limited:false})});
$('retry-recommendations').addEventListener('click',loadRecommendations);
$('page-retry').addEventListener('click',init);
$('learning-change-target').addEventListener('click',()=>openInterests(true));
$('learning-choose-career').addEventListener('click',()=>{setTab('discover');$('recommendations').scrollIntoView({behavior:'smooth',block:'start'})});
$('learning-retry').addEventListener('click',()=>loadLearningCareer(state.learningCareerUri));
$('learning-show-more').addEventListener('click',()=>{state.learningExpanded=!state.learningExpanded;if(state.learningDetails)renderLearning(state.learningDetails)});
$('learning-skill-select').addEventListener('change',()=>{$('learning-add-goal').disabled=!$('learning-skill-select').value});
$('learning-add-goal').addEventListener('click',addLearningGoal);

async function init(){
 $('page-error').hidden=true;$('initial-loading').hidden=false;$('workspace').hidden=true;
 try{
  const data=await request('/api/my-future');Object.assign(state,data);
  state.preferences=data.preferences||{career_areas:[],interests:[],target_occupation_uri:null};
  state.saved_careers=data.saved_careers||[];state.saved_occupations=data.saved_occupations||[];
  state.roadmap_progress=data.roadmap_progress||{};state.roadmap_goals=data.roadmap_goals||{};state.insurance_alternatives=data.insurance_alternatives||{};state.csrf_token=data.csrf_token||'';
  state.career_areas=data.career_areas||[];state.confirmed_skills=data.confirmed_skills||[];
  state.learningCareerUri=state.preferences.target_occupation_uri||null;
  $('initial-loading').hidden=true;$('workspace').hidden=false;
  renderPreferences();renderSaved();loadRecommendations();
  const qs=new URLSearchParams(location.search),uri=qs.get('career'),mode=qs.get('mode');
  if(uri){if(['map','insurance','sim','exp'].includes(mode)){pg.mode=mode;pg.simIntent=true;pg.uri=null}loadDetails(uri)}
  if(qs.get('edit')==='interests')openInterests(false);
 }catch(error){$('initial-loading').hidden=true;$('page-error-text').textContent=error.message;$('page-error').hidden=false}
}
$('target-stress').addEventListener('click',()=>{const u=state.preferences.target_occupation_uri;if(!u){$('goal-search-status').textContent='Save a career goal first, then open Explore My Future.';return}closeInterests();state.previousTab=state.activeTab;openStress(u)});
/*__PLAYGROUND_JS__*/
const hub={};
function hubRefresh(){
 const t=state.preferences.target_occupation_uri;
 if(!t)return;
 const show=d=>{const g=$('goal-summary-title');if(g&&state.preferences.target_occupation_uri===t&&d&&d.occupation)g.textContent=d.occupation.label};
 if(state.detailsByUri[t]){show(state.detailsByUri[t]);return}
 if(hub.loading===t)return;hub.loading=t;
 request('/api/my-future/career?uri='+encodeURIComponent(t)).then(d=>{state.detailsByUri[t]=d;hub.loading=null;show(d);const g=$('goal-summary-title');if(g&&state.preferences.target_occupation_uri===t)g.textContent=d.occupation.label}).catch(()=>{hub.loading=null});
}
$('goal-change').addEventListener('click',()=>openInterests(true));
init();
})();'''
MY_FUTURE_JS = MY_FUTURE_JS.replace('/*__PLAYGROUND_JS__*/', PLAYGROUND_JS)


MY_FUTURE_HTML = _page(
    "FutureTwin AI · My Future",
    "future",
    MY_FUTURE_CSS,
    MY_FUTURE_BODY,
    MY_FUTURE_JS,
)
