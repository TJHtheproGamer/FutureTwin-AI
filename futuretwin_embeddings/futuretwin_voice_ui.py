"""Frontend constants for FutureTwin My Skills choices (experience + manual)."""
from __future__ import annotations

VOICE_CSS = r'''
.ft-tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;background:var(--paper2);border:1px solid var(--line);border-radius:14px;padding:5px;margin:0 0 18px}
.ft-tab{border:0;background:transparent;border-radius:10px;padding:10px 8px;font-size:13px;font-weight:600;color:var(--ink2);line-height:1.3;transition:background .2s,color .2s,box-shadow .2s}
.ft-tab:hover{background:#ece6d8}
.ft-tab[aria-selected="true"]{background:var(--paper);color:var(--harbor);box-shadow:0 1px 3px #14263a1f}
.ft-panel>p.ft-sub{font-size:13px;color:var(--muted);margin:0 0 14px}
.ft-notice{background:var(--amber-soft);border:1px solid #ecd9b4;color:#7a4c0d;border-radius:12px;padding:11px 13px;font-size:13px;line-height:1.55;margin:0 0 14px}
.ft-block{border:1px solid var(--line);border-radius:14px;padding:14px;margin:0 0 14px;background:#fffefa}
.ft-block h3{font-family:var(--body);font-size:14px;font-weight:700;margin:0 0 8px}
.ft-rec-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:12px}
.ft-timer{font-variant-numeric:tabular-nums;font-weight:700;font-size:15px;color:var(--ink2);min-width:92px}
.ft-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--clay);margin-right:7px;animation:ftpulse 1.2s ease-in-out infinite}
@keyframes ftpulse{50%{opacity:.25}}
@media(prefers-reduced-motion:reduce){.ft-dot{animation:none}}
.ft-block audio{width:100%;margin-top:12px}
.ft-language-row{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-top:12px}
.ft-language-row label{font-size:12px;font-weight:700;color:var(--muted)}
.ft-language-row select{min-width:150px;border:1px solid var(--line);border-radius:9px;padding:8px 10px;background:#fffefa;color:var(--ink);font-size:13px}
.ft-server-consent{margin:10px 0 2px}
.ft-text{width:100%;min-height:170px;resize:vertical;border:1px solid var(--line);background:#fffefa;border-radius:12px;padding:12px 13px;color:var(--ink);font-size:14px;line-height:1.6}
.ft-count{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin:6px 2px 0}
.ft-link{border:0;background:none;color:var(--harbor);font-weight:600;font-size:13px;padding:4px 2px;text-decoration:underline}
.ft-review-head{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.ft-review-head h3{font-family:var(--body);font-size:16px;font-weight:700;margin:0}
.ft-row{border-top:1px solid var(--line2);padding:14px 0;transition:opacity .25s}
.ft-row.is-rejected{opacity:.45}
.ft-row.is-confirmed{background:linear-gradient(90deg,var(--sage-soft),transparent 60%)}
.ft-row-top{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.ft-row-top b{margin-right:auto;font-size:15px}
.ft-row label.ft-lab{display:block;font-size:11px;font-weight:700;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin:8px 0 4px}
.ft-row input[type=text],.ft-row select{width:100%;border:1px solid var(--line);background:#fffefa;border-radius:9px;padding:10px 11px;color:var(--ink);font-size:14px}
.ft-btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.ft-btns .danger{color:var(--clay)}
.ft-done{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
@media(max-width:650px){.ft-tabs{grid-template-columns:1fr}.ft-tab{text-align:left;padding:11px 12px}.ft-done .btn,.ft-btns .btn{flex:1;justify-content:center}}
'''

VOICE_TABS_HTML = r'''
<div class="ft-tabs" role="tablist" aria-label="How to build your skills profile">
  <button class="ft-tab" type="button" role="tab" id="ft-tab-resume" data-ft-tab="resume" aria-selected="true" aria-controls="ft-panel-resume">Upload Resume</button>
  <button class="ft-tab" type="button" role="tab" id="ft-tab-exp" data-ft-tab="exp" aria-selected="false" aria-controls="ft-panel-exp" tabindex="-1">Talk About Your Experience</button>
  <button class="ft-tab" type="button" role="tab" id="ft-tab-manual" data-ft-tab="manual" aria-selected="false" aria-controls="ft-panel-manual" tabindex="-1">Enter Skills Manually</button>
</div>
<p class="state-message" id="ft-tab-msg" role="status" aria-live="polite"></p>
'''

VOICE_PANELS_HTML = r'''
<div id="ft-panel-manual" class="ft-panel" role="tabpanel" aria-labelledby="ft-tab-manual" hidden>
  <p class="ft-sub">Type the skills you have. You choose the matches and confirm each one.</p>
  <button class="btn btn-primary" id="ft-manual-go" type="button">Open skills editor <span class="arrow" aria-hidden="true">&rarr;</span></button>
</div>
<div id="ft-panel-exp" class="ft-panel" role="tabpanel" aria-labelledby="ft-tab-exp" hidden>
  <div id="ft-capture">
    <p class="ft-sub">Describe what you do or have done. Up to 12,000 characters.</p>
    <div class="ft-notice" role="note"><strong>Record, transcribe, then review.</strong> With your permission, the audio is processed on FutureTwin's server using self-hosted speech recognition. The raw audio is deleted after processing and is not sent to OpenAI. Your transcript stays here until you review it and choose to find skills.</div>
    <div class="ft-block" id="ft-rec-block">
      <h3>Record your experience</h3>
      <label class="consent" style="margin:0 0 4px"><input type="checkbox" id="ft-rec-consent"><span>I agree to record with my microphone. Recording stays on this page until transcribed or deleted, up to 2 minutes.</span></label>
      <label class="consent ft-server-consent"><input type="checkbox" id="ft-transcribe-consent"><span>I agree to send the recording to FutureTwin's server for transcription. The server deletes the raw audio after processing.</span></label>
      <div class="ft-language-row"><label for="ft-language">Speech language</label><select id="ft-language" aria-label="Speech language"><option value="en">English</option><option value="auto">Auto-detect</option><option value="ms">Malay</option><option value="zh">Mandarin</option></select></div>
      <div class="ft-rec-row">
        <button class="btn btn-ghost btn-sm" id="ft-rec-start" type="button" disabled>Start recording</button>
        <button class="btn btn-primary btn-sm" id="ft-rec-stop" type="button" hidden>Stop</button>
        <span class="ft-timer" id="ft-rec-timer" aria-hidden="true">0:00 / 2:00</span>
      </div>
      <audio id="ft-rec-audio" controls hidden aria-label="Your recording"></audio>
      <div class="ft-rec-row" id="ft-rec-after" hidden>
        <button class="btn btn-ghost btn-sm" id="ft-rec-redo" type="button">Re-record</button>
        <button class="btn btn-primary btn-sm" id="ft-rec-transcribe" type="button" disabled>Transcribe recording</button>
        <button class="btn btn-ghost btn-sm" id="ft-rec-continue" type="button">Discard &amp; type instead</button>
      </div>
      <p class="state-message" id="ft-rec-status" role="status" aria-live="polite"></p>
      <button class="ft-link" id="ft-skip-rec" type="button">Skip recording and type instead</button>
    </div>
    <div id="ft-text-block" hidden>
      <label for="ft-text" class="ft-lab" style="font-size:13px;font-weight:700;display:block;margin-bottom:6px">Review your transcript</label>
      <p class="skill-note" id="ft-text-help">Correct anything that looks wrong before finding skills. You can also type or paste your experience.</p>
      <textarea id="ft-text" class="ft-text" maxlength="12000" aria-describedby="ft-text-help ft-count" placeholder="For example: I run weekly stock counts, train new staff on the till, and handle supplier orders."></textarea>
      <div class="ft-count"><span id="ft-count" aria-live="off">0 / 12,000</span></div>
      <label class="consent"><input type="checkbox" id="ft-proc-consent"><span>I agree to process this edited text locally on FutureTwin's server to find skill mentions and activity-based suggestions. No external AI service receives it. I will review suggestions; quotes are saved only if I choose.</span></label>
      <button class="btn btn-primary" id="ft-extract" type="button" disabled>Find skills <span class="arrow" aria-hidden="true">&rarr;</span></button>
    </div>
    <p class="state-message" id="ft-status" role="status" aria-live="polite"></p>
  </div>
  <div id="ft-review" hidden>
    <div class="ft-review-head"><h3 id="ft-review-title" tabindex="-1">Review skills from your experience</h3><span class="chip c-warn">Not saved yet</span></div>
    <p class="skill-note" id="ft-notice"></p>
    <p class="skill-note">Choose a match, then confirm each skill you want. Only confirmed skills are saved, added to your existing profile.</p>
    <div id="ft-rows"></div>
    <label class="consent"><input type="checkbox" id="ft-save-quotes"><span>Save supporting quotes with confirmed skills. Your full text is never saved.</span></label>
    <p class="state-message" id="ft-save-status" role="status" aria-live="polite"></p>
    <div class="ft-done"><button class="btn btn-primary" id="ft-save" type="button" disabled>Save confirmed skills</button><button class="btn btn-ghost" id="ft-discard" type="button">Discard draft</button></div>
  </div>
</div>
'''

VOICE_JS = r'''
(()=>{'use strict';
const $=id=>document.getElementById(id);
if(!$('ft-panel-exp'))return;
const MAXSEC=120,MAXBYTES=8*1024*1024,MAXCHARS=12000;
let rec=null,stream=null,timer=0,chunks=[],bytes=0,blob=null,url='',startedAt=0,rows=[],draftNotice='',csrf='',recEpoch=0,transcribeController=null,transcribing=false;
const tabs=[...document.querySelectorAll('[data-ft-tab]')];
const panels={resume:$('ft-panel-resume'),exp:$('ft-panel-exp'),manual:$('ft-panel-manual')};
const say=(id,t,err)=>{const n=$(id);n.textContent=t;n.classList.toggle('state-error',!!err)};
const dirty=()=>typeof window.ftProfileDirty==='function'&&window.ftProfileDirty();
function fmt(s){return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}
function updateTranscribeButton(){
  const b=$('ft-rec-transcribe');if(!b)return;
  b.disabled=!blob||!$('ft-transcribe-consent').checked||transcribing;
  b.textContent=transcribing?'Transcribing…':'Transcribe recording';
}
function releaseAudio(){
  recEpoch++;
  if(transcribeController){transcribeController.abort();transcribeController=null}
  transcribing=false;
  clearInterval(timer);timer=0;
  if(rec){rec.onstop=null;rec.ondataavailable=null;rec.onerror=null;if(rec.state!=='inactive'){try{rec.stop()}catch{}}}
  rec=null;if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}
  const a=$('ft-rec-audio');a.pause();a.removeAttribute('src');a.load();a.hidden=true;
  if(url){URL.revokeObjectURL(url);url=''}
  chunks=[];bytes=0;blob=null;
  say('ft-rec-status','');
  $('ft-rec-start').hidden=false;$('ft-rec-stop').hidden=true;$('ft-rec-after').hidden=true;$('ft-rec-timer').textContent='0:00 / 2:00';
  $('ft-rec-start').disabled=!$('ft-rec-consent').checked;
  updateTranscribeButton();
}
function selectTab(key,focus){
  if(key==='exp'&&dirty()){say('ft-tab-msg','You have unsaved profile edits. Save or discard them in My Career first.',true);return false}
  say('ft-tab-msg','');
  tabs.forEach(t=>{const on=t.dataset.ftTab===key;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;if(on&&focus)t.focus()});
  Object.entries(panels).forEach(([k,p])=>{if(p)p.hidden=k!==key});
  if(key!=='exp'){releaseAudio();$('ft-transcribe-consent').checked=false}
  return true;
}
tabs.forEach((t,i)=>{
  t.addEventListener('click',()=>selectTab(t.dataset.ftTab));
  t.addEventListener('keydown',e=>{const d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;if(!d)return;e.preventDefault();const n=tabs[(i+d+tabs.length)%tabs.length];selectTab(n.dataset.ftTab,true)});
});
$('ft-manual-go').addEventListener('click',()=>{if(dirty()){say('ft-tab-msg','You have unsaved profile edits. Open My Career to save them.',true)}window.dispatchEvent(new CustomEvent('ft:manual'))});

/* ---- local recording and self-hosted transcription ---- */
function showText(focus){$('ft-text-block').hidden=false;if(focus)$('ft-text').focus()}
$('ft-rec-consent').addEventListener('change',e=>{if(!e.target.checked){releaseAudio();$('ft-transcribe-consent').checked=false;say('ft-rec-status','Recording consent withdrawn. Audio deleted.')}else $('ft-rec-start').disabled=!!rec});
$('ft-skip-rec').addEventListener('click',()=>{releaseAudio();$('ft-transcribe-consent').checked=false;say('ft-rec-status','');showText(true)});
function failRec(msg){releaseAudio();say('ft-rec-status',msg+' You can type or paste your experience instead.',true);showText(false)}
function audioExtension(mime){
  const t=(mime||'audio/webm').split(';')[0].toLowerCase();
  return ({'audio/webm':'webm','audio/mp4':'mp4','audio/ogg':'ogg','audio/wav':'wav','audio/x-wav':'wav','audio/mpeg':'mp3','audio/aac':'aac','audio/x-m4a':'m4a','audio/m4a':'m4a'})[t]||'webm';
}
async function transcribeRecording(){
  if(!blob||!$('ft-transcribe-consent').checked||transcribing)return;
  const epoch=recEpoch,recording=blob,controller=new AbortController();transcribing=true;transcribeController=controller;updateTranscribeButton();
  say('ft-rec-status','Sending audio securely to FutureTwin for local transcription. The server deletes the audio after processing.');
  try{
    const csrfToken=await token();if(epoch!==recEpoch)return;
    const form=new FormData();
    form.append('audio',recording,'recording.'+audioExtension(recording.type));
    form.append('consent','true');form.append('language',$('ft-language').value||'en');
    const response=await fetch('/api/profile/voice',{method:'POST',headers:{'X-CSRF-Token':csrfToken,'Accept':'application/json'},credentials:'same-origin',cache:'no-store',body:form,signal:controller.signal});
    const data=await json(response);if(epoch!==recEpoch)return;
    const transcript=typeof data.transcript==='string'?data.transcript.trim():'';
    if(!transcript)throw new Error('No clear speech was detected. Try again or type instead.');
    const detected={en:'English',ms:'Malay',zh:'Mandarin'}[data.language]||data.language||'your selected language';
    transcribeController=null;transcribing=false;releaseAudio();$('ft-transcribe-consent').checked=false;
    $('ft-text').value=transcript;updText();showText(true);
    say('ft-rec-status','Transcript ready ('+detected+'). Correct it below before finding skills.');
  }catch(err){
    if(controller.signal.aborted||epoch!==recEpoch)return;
    say('ft-rec-status',err.message||'Transcription failed. Your audio remains only on this page. Retry or discard it and type instead.',true);
  }finally{
    if(transcribeController===controller){transcribeController=null;transcribing=false;updateTranscribeButton()}
  }
}
$('ft-transcribe-consent').addEventListener('change',e=>{
  if(!e.target.checked&&transcribing){releaseAudio();say('ft-rec-status','Transcription cancelled. The local recording was deleted.')}
  else if(e.target.checked&&blob&&!transcribing)void transcribeRecording();
  else if(!e.target.checked&&blob)say('ft-rec-status','Recording stays on this page. Agree to server transcription or discard it and type instead.');
  updateTranscribeButton();
});
async function startRec(){
  if(!$('ft-rec-consent').checked)return;
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia||typeof MediaRecorder==='undefined'){failRec('Recording is not supported in this browser.');return}
  if(window.isSecureContext===false){failRec('Microphone access requires a secure page. Open FutureTwin in Replit Preview or type instead.');return}
  releaseAudio();say('ft-rec-status','Waiting for microphone permission…');$('ft-rec-start').disabled=true;
  const epoch=recEpoch;
  try{const acquired=await navigator.mediaDevices.getUserMedia({audio:true});if(epoch!==recEpoch){acquired.getTracks().forEach(t=>t.stop());return}stream=acquired}
  catch(e){
    if(epoch!==recEpoch)return;
    const messages={NotFoundError:'No microphone was found.',DevicesNotFoundError:'No microphone was found.',NotAllowedError:'Microphone permission was denied. Allow it in your browser settings or type instead.',PermissionDeniedError:'Microphone permission was denied. Allow it in your browser settings or type instead.',NotReadableError:'The microphone is busy in another app.',SecurityError:'Microphone access requires a secure page.'};
    failRec(messages[e&&e.name]||'Microphone access is unavailable. Check your browser permission or type instead.');return
  }
  try{
    const formats=['audio/webm;codecs=opus','audio/mp4;codecs=mp4a.40.2','audio/webm','audio/mp4'];
    const mime=typeof MediaRecorder.isTypeSupported==='function'?formats.find(t=>MediaRecorder.isTypeSupported(t)):'';
    rec=mime?new MediaRecorder(stream,{mimeType:mime}):new MediaRecorder(stream)
  }catch{failRec('Recording could not start in this browser.');return}
  chunks=[];bytes=0;
  rec.ondataavailable=e=>{if(epoch!==recEpoch)return;if(e.data&&e.data.size){chunks.push(e.data);bytes+=e.data.size;if(bytes>=MAXBYTES&&rec&&rec.state==='recording'){say('ft-rec-status','Reached the 8 MB limit. Recording stopped.');stopRec()}}};
  rec.onstop=()=>{
    if(epoch!==recEpoch)return;
    clearInterval(timer);timer=0;if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}
    if(!bytes||!chunks.length){failRec('Nothing was recorded.');return}
    blob=new Blob(chunks,{type:(rec&&rec.mimeType)||'audio/webm'});chunks=[];
    if(blob.size>MAXBYTES){failRec('The recording is larger than 8 MB.');return}
    url=URL.createObjectURL(blob);const a=$('ft-rec-audio');a.src=url;a.hidden=false;
    $('ft-rec-stop').hidden=true;$('ft-rec-start').hidden=true;$('ft-rec-after').hidden=false;
    say('ft-rec-status','Recording finished. Transcription starts automatically with your permission.');updateTranscribeButton();
    if($('ft-transcribe-consent').checked)void transcribeRecording();else $('ft-rec-transcribe').focus();
  };
  rec.onerror=()=>{if(epoch===recEpoch)failRec('Recording stopped unexpectedly.')};
  try{rec.start(1000)}catch{failRec('Recording could not start in this browser.');return}startedAt=Date.now();
  $('ft-rec-start').hidden=true;$('ft-rec-stop').hidden=false;$('ft-rec-stop').focus();
  say('ft-rec-status','Recording. Select Stop when you are done.');
  $('ft-rec-timer').innerHTML='<span class="ft-dot" aria-hidden="true"></span>0:00 / 2:00';
  timer=setInterval(()=>{const s=Math.min(MAXSEC,Math.floor((Date.now()-startedAt)/1000));$('ft-rec-timer').innerHTML='<span class="ft-dot" aria-hidden="true"></span>'+fmt(s)+' / 2:00';if(s>=MAXSEC){say('ft-rec-status','Reached the 2 minute limit. Recording stopped.');stopRec()}},250);
}
function stopRec(){if(rec&&rec.state==='recording'){clearInterval(timer);timer=0;rec.stop()}}
$('ft-rec-start').addEventListener('click',startRec);
$('ft-rec-stop').addEventListener('click',stopRec);
$('ft-rec-transcribe').addEventListener('click',()=>void transcribeRecording());
$('ft-rec-redo').addEventListener('click',()=>{releaseAudio();$('ft-transcribe-consent').checked=false;say('ft-rec-status','Previous recording deleted.');$('ft-rec-start').focus()});
$('ft-rec-continue').addEventListener('click',()=>{releaseAudio();$('ft-transcribe-consent').checked=false;showText(true);say('ft-status','Recording deleted. Type or paste your experience, then find skills.')});

/* ---- text + extraction ---- */
const ta=$('ft-text'),ex=$('ft-extract');
function updText(){const n=ta.value.length;$('ft-count').textContent=n.toLocaleString('en-US')+' / 12,000';ex.disabled=!(ta.value.trim()&&n<=MAXCHARS&&$('ft-proc-consent').checked)||ex.dataset.busy==='true'}
ta.addEventListener('input',updText);$('ft-proc-consent').addEventListener('change',updText);
async function json(r){let d={};try{d=await r.json()}catch{}if(!r.ok)throw new Error(typeof d.error==='string'?d.error:'Request could not be completed.');return d}
async function token(){const r=await fetch('/api/profile',{headers:{'Accept':'application/json'},credentials:'same-origin',cache:'no-store'});const d=await json(r);csrf=d.csrf_token||'';if(!csrf)throw new Error('Could not start a secure request. Try again.');return csrf}
async function post(path,body){const t=await token();const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':t,'Accept':'application/json'},credentials:'same-origin',cache:'no-store',body:JSON.stringify(body)});return json(r)}
ex.addEventListener('click',async()=>{
  if(dirty()){say('ft-status','You have unsaved profile edits. Save or discard them in My Career first.',true);return}
  const text=ta.value.trim();if(!text||text.length>MAXCHARS||!$('ft-proc-consent').checked)return;
  ex.dataset.busy='true';updText();ex.textContent='Finding skills…';say('ft-status','Reading your text. This can take a moment.');
  releaseAudio();$('ft-transcribe-consent').checked=false;say('ft-rec-status','');
  try{
    const d=await post('/api/profile/experience',{transcript:text,consent:true});
    const sk=d&&d.draft&&Array.isArray(d.draft.skills)?d.draft.skills:null;if(!sk)throw new Error('No skills came back. Try again.');
    rows=sk.map(r=>({value:String(r.value||''),evidence:String(r.evidence||''),origin:r.origin==='explicit'?'explicit':'activity_suggestion',source:'experience',evidence_consent:false,esco_candidates:Array.isArray(r.esco_candidates)?r.esco_candidates.filter(c=>c&&c.uri):[],selected_esco_uri:null,confirmed:false,rejected:false,stale:false}));
    draftNotice=typeof d.notice==='string'?d.notice:'';
    ta.value='';updText();say('ft-status','');openReview();
  }catch(err){say('ft-status',err.message||'Skills could not be found. Your text is still here. Try again.',true)}
  finally{ex.dataset.busy='false';ex.innerHTML='Find skills <span class="arrow" aria-hidden="true">&rarr;</span>';updText()}
});

/* ---- draft review (separate from saved profile editor) ---- */
function openReview(){$('ft-capture').hidden=true;$('ft-review').hidden=false;$('ft-notice').textContent=draftNotice||'';drawRows();$('ft-review-title').focus()}
function closeReview(){rows=[];draftNotice='';$('ft-review').hidden=true;$('ft-capture').hidden=false;$('ft-rows').replaceChildren();say('ft-save-status','');$('ft-save-quotes').checked=false}
function updSave(){const n=rows.filter(r=>r.confirmed&&r.selected_esco_uri&&!r.rejected).length;const b=$('ft-save');b.disabled=!n||b.dataset.busy==='true';b.textContent=n?'Save '+n+' confirmed '+(n===1?'skill':'skills'):'Save confirmed skills'}
function fill(sel,r){sel.replaceChildren();const o=document.createElement('option');o.value='';o.textContent=r.esco_candidates.length?'Choose a match':'No matches. Edit wording and find again.';sel.appendChild(o);r.esco_candidates.forEach(c=>{const p=document.createElement('option');p.value=c.uri;p.textContent=c.label||c.uri;sel.appendChild(p)});sel.value=r.selected_esco_uri||''}
function drawRows(){
  const t=$('ft-rows');t.replaceChildren();
  if(!rows.length){const p=document.createElement('p');p.className='skill-empty';p.textContent='No skills were found in that text. Go back and add more detail, or enter skills manually.';t.appendChild(p);updSave();return}
  rows.forEach((r,i)=>{
    const named=r.origin==='explicit';
    const li=document.createElement('div');li.className='ft-row';
    li.innerHTML='<div class="ft-row-top"><b></b><span class="chip"></span><span class="chip ft-state"></span></div><label class="ft-lab"></label><input type="text" maxlength="2000"><label class="ft-lab">Skill match</label><select></select><div class="ft-btns"><button type="button" class="btn btn-ghost btn-sm ft-find">Find matches</button><button type="button" class="btn btn-primary btn-sm ft-ok">Confirm match</button><button type="button" class="btn btn-ghost btn-sm danger ft-rej"></button></div><p class="state-message ft-msg" role="status" aria-live="polite"></p>';
    const [title,tag,st]=li.querySelectorAll('.ft-row-top>*'),labs=li.querySelectorAll('label'),inp=li.querySelector('input'),sel=li.querySelector('select'),find=li.querySelector('.ft-find'),ok=li.querySelector('.ft-ok'),rej=li.querySelector('.ft-rej'),msg=li.querySelector('.ft-msg');
    const nm=()=>r.value||'skill';
    function sync(){
      title.textContent=r.value||'Untitled skill';
      const n=r.origin==='explicit';tag.textContent=n?'Named by you':r.origin==='user_added'?'Edited by you':'Suggested from activity';tag.className='chip '+(n?'c-obs':'c-warn');
      st.textContent=r.rejected?'Rejected':r.confirmed?'Confirmed match':'Pending';st.className='chip ft-state '+(r.rejected?'c-clay':r.confirmed?'c-up':'c-flat');
      li.classList.toggle('is-rejected',r.rejected);li.classList.toggle('is-confirmed',r.confirmed&&!r.rejected);
      ok.disabled=r.rejected||!r.selected_esco_uri||r.confirmed||r.stale;ok.textContent=r.confirmed?'Confirmed':'Confirm match';
      rej.textContent=r.rejected?'Restore':'Reject';
      inp.disabled=sel.disabled=find.disabled=r.rejected;
      ok.setAttribute('aria-label','Confirm match for '+nm());rej.setAttribute('aria-label',(r.rejected?'Restore ':'Reject ')+nm());find.setAttribute('aria-label','Find matches for '+nm());
      inp.setAttribute('aria-label','Wording for '+nm());sel.setAttribute('aria-label','Choose match for '+nm());updSave();
    }
    labs[0].textContent=named?'Skill you named':'Your wording';inp.value=r.value;fill(sel,r);
    if(r.evidence){const d=document.createElement('details');d.className='ev';d.innerHTML='<summary>Why this skill?</summary><div class="evbody"></div>';d.querySelector('.evbody').textContent=r.evidence;li.appendChild(d)}
    inp.addEventListener('input',()=>{r.value=inp.value;r.origin='user_added';r.evidence='';li.querySelector('.ev')?.remove();r.confirmed=false;r.stale=true;r.selected_esco_uri=null;r.esco_candidates=[];fill(sel,r);msg.textContent='Wording changed. Find matches again.';msg.classList.remove('state-error');sync()});
    sel.addEventListener('change',()=>{r.selected_esco_uri=sel.value||null;r.confirmed=false;sync()});
    ok.addEventListener('click',()=>{if(!r.selected_esco_uri||r.stale)return;r.confirmed=true;msg.textContent='';sync()});
    rej.addEventListener('click',()=>{r.rejected=!r.rejected;if(r.rejected)r.confirmed=false;sync()});
    find.addEventListener('click',async()=>{
      const v=r.value.trim();if(!v){msg.textContent='Enter wording first.';return}
      find.disabled=true;msg.classList.remove('state-error');msg.textContent='Finding matches…';
      try{const d=await post('/api/profile/match',{value:v});
        if(r.value.trim()!==v||!rows.includes(r)){msg.textContent='Wording changed. Find matches again.';return}
        r.esco_candidates=Array.isArray(d.esco_candidates)?d.esco_candidates.filter(c=>c&&c.uri):[];r.selected_esco_uri=null;r.confirmed=false;r.stale=false;fill(sel,r);
        msg.textContent=r.esco_candidates.length?'Matches updated. Choose one to confirm.':'No matches found. Try other wording.'}
      catch(e){msg.classList.add('state-error');msg.textContent=e.message||'Matches could not be refreshed.'}
      finally{find.disabled=false;sync()}
    });
    sync();t.appendChild(li);
  });
  updSave();
}
$('ft-discard').addEventListener('click',()=>{if(rows.some(r=>r.confirmed)&&!window.confirm('Discard this draft? Nothing from it has been saved.'))return;closeReview();ta.value='';updText();showText(true);say('ft-status','Draft discarded. Nothing was saved.')});
$('ft-save').addEventListener('click',async()=>{
  if(dirty()){say('ft-save-status','Save your existing profile edits before adding these skills.',true);return}
  const b=$('ft-save'),keep=rows.filter(r=>r.confirmed&&r.selected_esco_uri&&!r.rejected&&!r.stale&&r.value.trim());
  if(!keep.length)return;
  b.dataset.busy='true';b.disabled=true;b.textContent='Saving…';say('ft-save-status','');
  const q=$('ft-save-quotes').checked;
  try{
    const d=await post('/api/profile/experience/save',{skills:keep.map(r=>({value:r.value.trim(),evidence:r.evidence,origin:r.origin,source:'experience',evidence_consent:q,esco_candidates:r.esco_candidates,selected_esco_uri:r.selected_esco_uri,confirmed:true})),save_quotes:q,consent:true});
    if(!d.profile)throw new Error('Your skills could not be saved. Try again.');
    const detail={profile:d.profile,added_count:d.added_count||0,duplicate_count:d.duplicate_count||0};
    closeReview();ta.value='';updText();$('ft-proc-consent').checked=false;
    window.dispatchEvent(new CustomEvent('ft:experience-saved',{detail}));
  }catch(e){say('ft-save-status',e.message||'Your skills could not be saved. Your draft is still here.',true)}
  finally{b.dataset.busy='false';updSave()}
});
window.addEventListener('pagehide',()=>{releaseAudio();closeReview();ta.value='';$('ft-proc-consent').checked=false;$('ft-rec-consent').checked=false;$('ft-transcribe-consent').checked=false;updText()});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&rec&&rec.state==='recording')stopRec()});
updText();
})();
'''
