// Browser-API simulations only; these do not claim real microphone coverage.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { spawnSync } = require('node:child_process');
const vm = require('node:vm');
const path = require('node:path');

const extracted = spawnSync('python3', ['-c', 'from futuretwin_voice_ui import VOICE_JS; print(VOICE_JS)'], {
  cwd: path.resolve(__dirname, '..'), encoding: 'utf8',
});
assert.equal(extracted.status, 0, extracted.stderr);
const source = extracted.stdout;

function setup(getUserMedia, fetcher, options = {}) {
  const nodes = new Map();
  const forms = [];
  const requests = [];
  class FormDataStub {
    constructor() { this.entries = []; forms.push(this); }
    append(...args) { this.entries.push(args); }
  }
  function node(id) {
    if (!nodes.has(id)) {
      const listeners = {};
      nodes.set(id, {
        id, listeners, dataset: {}, value: '', textContent: '', checked: false,
        hidden: false, disabled: false,
        classList: { toggle() {}, add() {}, remove() {} },
        addEventListener(type, fn) { (listeners[type] ||= []).push(fn); },
        async emit(type, event = {}) {
          for (const fn of listeners[type] || []) await fn({ target: this, ...event });
        },
        setAttribute() {}, removeAttribute(name) { delete this[name]; },
        focus() {}, pause() {}, load() {}, replaceChildren() {},
      });
    }
    return nodes.get(id);
  }
  const tabs = ['resume', 'exp', 'manual'].map(key => {
    const tab = node(`ft-tab-${key}`);
    tab.dataset.ftTab = key;
    return tab;
  });
  const windowEvents = {};
  const tracks = [{ stopped: false, stop() { this.stopped = true; } }];
  const stream = { getTracks: () => tracks };
  const urls = new Set();
  class Recorder {
    constructor() { this.state = 'inactive'; this.mimeType = 'audio/webm'; }
    start() { this.state = 'recording'; }
    stop() {
      this.state = 'inactive';
      if (this.ondataavailable) this.ondataavailable({ data: new Blob(['synthetic audio']) });
      if (this.onstop) this.onstop();
    }
  }
  const fetchImpl = async (url, init = {}) => {
    requests.push({ url, init });
    if (fetcher) return fetcher(url, init);
    throw new Error('Unexpected network request');
  };
  const context = {
    document: { getElementById: node, querySelectorAll: () => tabs, addEventListener() {} },
    window: { isSecureContext: options.secure !== false, addEventListener(name, fn) { windowEvents[name] = fn; } },
    navigator: { mediaDevices: { getUserMedia: getUserMedia || (async () => stream) } },
    MediaRecorder: options.unsupportedRecorder ? undefined : Recorder, Blob, FormData: FormDataStub, AbortController,
    Date, setInterval, clearInterval, fetch: fetchImpl,
    URL: {
      createObjectURL() { urls.add('blob:synthetic'); return 'blob:synthetic'; },
      revokeObjectURL(url) { urls.delete(url); },
    },
  };
  node('ft-language').value = 'en';
  vm.runInNewContext(source, context);
  return {
    node, tracks, stream, urls, forms, requests,
    async start({ transcribeConsent = false } = {}) {
      node('ft-rec-consent').checked = true;
      await node('ft-rec-consent').emit('change');
      node('ft-transcribe-consent').checked = transcribeConsent;
      await node('ft-transcribe-consent').emit('change');
      await node('ft-rec-start').emit('click');
    },
    cleanup() { windowEvents.pagehide(); },
  };
}

test('recording stays local until server-transcription consent is given', async () => {
  const app = setup();
  try {
    await app.start();
    assert.equal(app.tracks[0].stopped, false);
    await app.node('ft-rec-stop').emit('click');
    assert.equal(app.node('ft-rec-audio').hidden, false);
    assert.equal(app.urls.size, 1);
    assert.equal(app.tracks[0].stopped, true);
    assert.equal(app.node('ft-rec-transcribe').disabled, true);
    assert.equal(app.requests.length, 0);
    await app.node('ft-rec-continue').emit('click');
    assert.equal(app.urls.size, 0);
    assert.equal(app.node('ft-rec-audio').hidden, true);
    assert.equal(app.node('ft-text-block').hidden, false);
    assert.match(app.node('ft-status').textContent, /Recording deleted/);
  } finally { app.cleanup(); }
});

test('a permitted recording is transcribed into an editable transcript automatically', async () => {
  const app = setup(undefined, async (url, init) => {
    if (url === '/api/profile') return { ok: true, async json() { return { csrf_token: 'synthetic-csrf' }; } };
    if (url === '/api/profile/voice') return {
      ok: true,
      async json() { return { transcript: 'I trained new staff on the till.', language: 'en', audio_retained: false }; },
    };
    throw new Error('Unexpected request path');
  });
  try {
    await app.start({ transcribeConsent: true });
    await app.node('ft-rec-stop').emit('click');
    for (let i = 0; i < 20 && !app.node('ft-text').value; i++) {
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    assert.equal(app.node('ft-text').value, 'I trained new staff on the till.');
    assert.equal(app.node('ft-text-block').hidden, false);
    assert.match(app.node('ft-rec-status').textContent, /Transcript ready \(English\)/);
    assert.equal(app.urls.size, 0);
    assert.equal(app.node('ft-transcribe-consent').checked, false, 'server consent is specific to one recording');
    assert.equal(app.node('ft-extract').disabled, true, 'text extraction still requires its separate consent');
    const upload = app.requests.find(r => r.url === '/api/profile/voice');
    assert.ok(upload);
    assert.equal(upload.init.headers['X-CSRF-Token'], 'synthetic-csrf');
    assert.equal(app.forms[0].entries.find(x => x[0] === 'consent')[1], 'true');
    assert.equal(app.forms[0].entries.find(x => x[0] === 'language')[1], 'en');
    assert.equal(app.forms[0].entries.find(x => x[0] === 'audio')[2], 'recording.webm');
  } finally { app.cleanup(); }
});

test('a microphone permission denial exposes the manual text fallback', async () => {
  const denied = Object.assign(new Error('denied'), { name: 'NotAllowedError' });
  const app = setup(() => Promise.reject(denied));
  try {
    await app.start();
    assert.match(app.node('ft-rec-status').textContent, /permission was denied/i);
    assert.equal(app.node('ft-text-block').hidden, false);
    assert.equal(app.node('ft-rec-audio').hidden, true);
  } finally { app.cleanup(); }
});

test('unsupported recording browsers can continue with typed experience', async () => {
  const app = setup(undefined, undefined, { unsupportedRecorder: true });
  try {
    await app.start();
    assert.match(app.node('ft-rec-status').textContent, /not supported in this browser/i);
    assert.equal(app.node('ft-text-block').hidden, false);
    assert.equal(app.requests.length, 0);
  } finally { app.cleanup(); }
});

test('transcription errors keep audio retryable and discard clears consent', async () => {
  const app = setup(undefined, async url => {
    if (url === '/api/profile') return { ok: true, async json() { return { csrf_token: 'synthetic-csrf' }; } };
    if (url === '/api/profile/voice') return {
      ok: false, status: 503,
      async json() { return { error: 'Speech recognition is temporarily unavailable.' }; },
    };
    throw new Error('Unexpected request path');
  });
  try {
    await app.start({ transcribeConsent: true });
    await app.node('ft-rec-stop').emit('click');
    for (let i = 0; i < 20 && !/temporarily unavailable/i.test(app.node('ft-rec-status').textContent); i++) {
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    assert.match(app.node('ft-rec-status').textContent, /temporarily unavailable/i);
    assert.equal(app.node('ft-rec-audio').hidden, false, 'failed uploads retain only the page-local retry copy');
    assert.equal(app.node('ft-rec-transcribe').disabled, false);
    await app.node('ft-rec-continue').emit('click');
    assert.equal(app.node('ft-rec-audio').hidden, true);
    assert.equal(app.node('ft-transcribe-consent').checked, false);
    assert.equal(app.node('ft-text-block').hidden, false);
  } finally { app.cleanup(); }
});

test('switching tabs stops the microphone and clears Recording status', async () => {
  const app = setup();
  try {
    await app.start();
    assert.match(app.node('ft-rec-status').textContent, /Recording/);
    await app.node('ft-tab-resume').emit('click');
    assert.equal(app.tracks[0].stopped, true);
    assert.equal(app.node('ft-rec-status').textContent, '');
    assert.equal(app.urls.size, 0);
  } finally { app.cleanup(); }
});

test('leaving while permission is pending stops any late microphone stream', async () => {
  let grant;
  const app = setup(() => new Promise(resolve => { grant = resolve; }));
  try {
    const starting = app.start();
    for (let i = 0; i < 20 && !grant; i++) {
      await new Promise(resolve => setImmediate(resolve));
    }
    assert.equal(typeof grant, 'function', 'microphone permission request should be pending');
    app.cleanup();
    grant(app.stream);
    await starting;
    assert.equal(app.tracks[0].stopped, true);
    assert.equal(app.urls.size, 0);
  } finally { app.cleanup(); }
});

test('withdrawing recording consent immediately releases the active microphone', async () => {
  const app = setup();
  try {
    await app.start();
    app.node('ft-rec-consent').checked = false;
    await app.node('ft-rec-consent').emit('change');
    assert.equal(app.tracks[0].stopped, true);
    assert.equal(app.node('ft-rec-start').disabled, true);
    assert.equal(app.urls.size, 0);
    assert.equal(app.node('ft-rec-after').hidden, true, 'late recorder events cannot restore withdrawn audio');
  } finally { app.cleanup(); }
});
