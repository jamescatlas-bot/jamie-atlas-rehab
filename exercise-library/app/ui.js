// Library browser: search, preview, personalise, make the video, save or copy the message.
import { Stage, MiniMap } from './engine.js';

const EX = window.EXERCISES;
const LABEL = {
  quads: 'Quads', hamstrings: 'Hamstrings', glutes: 'Glutes', glute_med: 'Side glutes', adductors: 'Inner thighs',
  hip_flexors: 'Hip flexors', calves: 'Calves', pecs: 'Chest', lats: 'Lats', upper_back: 'Upper back', traps: 'Traps',
  delts: 'Shoulders', rear_delts: 'Rear shoulders', biceps: 'Biceps', triceps: 'Triceps', forearms: 'Forearms',
  abs: 'Abs', obliques: 'Obliques', lower_back: 'Lower back',
};
const $ = (s) => document.querySelector(s);
const store = {
  get(k, d) { try { const v = localStorage.getItem('exlib.' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem('exlib.' + k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
};

const state = {
  q: '', area: 'All', where: 'Any', rehab: false, demo: false, muscle: '',
  current: null, showMap: true, split: false, label: true,
  client: store.get('client', 'Sam'), sets: '', cue: '', recording: false, video: null,
};

// ---------------------------------------------------------------- list
function haystack(e) {
  return [e.name, e.area, e.where, ...e.muscles.map((m) => LABEL[m]), ...e.secondary.map((m) => LABEL[m]),
    ...e.equipment, ...e.cues, e.rehab ? 'rehab' : '', e.fault ? 'right wrong form demo' : ''].join(' ').toLowerCase();
}
EX.forEach((e) => { e._hay = haystack(e); });

function filtered() {
  const words = state.q.toLowerCase().split(/\s+/).filter(Boolean);
  return EX.filter((e) =>
    (state.area === 'All' || e.area === state.area) &&
    (state.where === 'Any' || e.where === state.where.toLowerCase() || e.where === 'both') &&
    (!state.rehab || e.rehab) && (!state.demo || e.fault) &&
    (!state.muscle || e.muscles.includes(state.muscle) || e.secondary.includes(state.muscle)) &&
    words.every((w) => e._hay.includes(w)));
}

function renderList() {
  const list = filtered();
  $('#count').textContent = `${list.length} of ${EX.length}`;
  const ul = $('#results');
  ul.replaceChildren();
  if (!list.length) {
    const li = document.createElement('li'); li.className = 'empty';
    li.textContent = 'No exercises match. Clear a filter or try a muscle name like "glutes".';
    ul.append(li); return;
  }
  for (const e of list) {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.className = 'row' + (state.current?.id === e.id ? ' on' : '');
    b.type = 'button';
    b.innerHTML = `<span class="rn"></span><span class="rm"></span><span class="rt"></span>`;
    b.querySelector('.rn').textContent = e.name;
    b.querySelector('.rm').textContent = e.muscles.map((m) => LABEL[m]).join(' · ');
    const tags = b.querySelector('.rt');
    const tag = (t, cls) => { const s = document.createElement('span'); s.className = 'tag ' + (cls || ''); s.textContent = t; tags.append(s); };
    tag(e.where === 'both' ? 'Home or gym' : e.where === 'home' ? 'Home' : 'Gym', e.where);
    if (e.equipment.length) tag(e.equipment[0]);
    if (e.fault) tag('Right vs wrong', 'demo');
    if (e.rehab) tag('Rehab', 'rehab');
    b.addEventListener('click', () => { select(e); if (matchMedia('(max-width: 899px)').matches) $('#preview').scrollIntoView({ behavior: 'smooth' }); });
    li.append(b); ul.append(li);
  }
}

function chips(el, values, key) {
  el.replaceChildren();
  for (const v of values) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'chip'; b.textContent = v;
    b.setAttribute('aria-pressed', state[key] === v);
    b.addEventListener('click', () => { state[key] = v; chips(el, values, key); renderList(); });
    el.append(b);
  }
}

// ---------------------------------------------------------------- preview
const W = 720, H = 1280;
let stage, mini, maps = null, clock = performance.now(), downloads = null;
const comp = $('#comp');
const ctx = comp.getContext('2d');

function select(e) {
  state.current = e;
  state.video = null;
  state.split = state.split && !!e.fault;
  state.sets = e.sets;
  state.cue = e.cues[0];
  try { history.replaceState(null, '', '#' + e.id); } catch { /* sandboxed */ }
  $('#ex-name').textContent = e.name;
  $('#ex-meta').textContent = `${e.area} · ${e.where === 'both' ? 'Home or gym' : e.where === 'home' ? 'Home' : 'Gym'} · Level ${e.level}`;
  $('#sets').value = e.sets;
  const sel = $('#cue');
  sel.replaceChildren(...e.cues.map((c) => new Option(c, c)));
  $('#cue-custom').value = '';
  $('#split').disabled = !e.fault;
  $('#split').checked = state.split;
  $('#split-note').textContent = e.fault ? `${window.FAULTS[e.fault].bad} vs ${window.FAULTS[e.fault].good.toLowerCase()}` : 'No right-vs-wrong demo for this one yet';
  const list = (id, items) => { const ul = $(id); ul.replaceChildren(...items.map((t) => { const li = document.createElement('li'); li.textContent = t; return li; })); };
  list('#cues', e.cues.map(cap));
  list('#mistakes', e.mistakes);
  $('#muscles').replaceChildren(
    ...e.muscles.map((m) => pill(LABEL[m], 'prime')),
    ...e.secondary.map((m) => pill(LABEL[m], 'second')));
  $('#equip').textContent = e.equipment.length ? e.equipment.join(', ') : 'None, just bodyweight';
  $('#video-out').hidden = true;
  $('#status').textContent = '';
  renderList();
  if (!stage) return;
  stage.load(e);
  applySize();
  maps = mini.render(e.muscles, e.secondary);
  clock = performance.now();
}
function pill(t, cls) { const s = document.createElement('span'); s.className = 'pill ' + cls; s.textContent = t; return s; }
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function applySize() {
  if (state.split) stage.setSize(W, H / 2); else stage.setSize(W, H);
  stage.frameCamera();
}

// ---------------------------------------------------------------- 2D overlays
function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }

function drawMap() {
  if (!maps) return;
  const x0 = 170, y0 = 30, tw = 120, th = 200, gap = 10;
  roundRect(x0 - 12, y0 - 8, tw * 3 + gap * 2 + 24, th + 16, 22);
  ctx.fillStyle = 'rgba(20,24,32,0.62)'; ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.08)'; ctx.lineWidth = 2; ctx.stroke();
  ['front', 'back', 'side'].forEach((v, i) => {
    const x = x0 + i * (tw + gap);
    ctx.drawImage(maps[v], 15, 10, 120, 230, x, y0, tw, th);
    if (v === maps.best) {
      ctx.save();
      ctx.shadowColor = '#ff3df2'; ctx.shadowBlur = 18;
      ctx.strokeStyle = '#ff5cf4'; ctx.lineWidth = 5;
      roundRect(x - 4, y0 - 2, tw + 8, th + 4, 14); ctx.stroke();
      ctx.restore();
    }
  });
}

function drawBadge(x, y, good) {
  ctx.save();
  ctx.shadowColor = good ? '#35e07a' : '#ff3b3b'; ctx.shadowBlur = 24;
  ctx.fillStyle = good ? '#1fa85a' : '#d8332f';
  ctx.beginPath(); ctx.arc(x, y, 34, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 8; ctx.lineCap = 'round'; ctx.beginPath();
  if (good) { ctx.moveTo(x - 15, y + 1); ctx.lineTo(x - 4, y + 12); ctx.lineTo(x + 16, y - 11); }
  else { ctx.moveTo(x - 12, y - 12); ctx.lineTo(x + 12, y + 12); ctx.moveTo(x + 12, y - 12); ctx.lineTo(x - 12, y + 12); }
  ctx.stroke();
}

function drawCaption(text, y, good) {
  ctx.font = '600 30px "Barlow Condensed", "Arial Narrow", sans-serif';
  const w = ctx.measureText(text).width + 36;
  roundRect(40, y, w, 50, 25);
  ctx.fillStyle = good ? 'rgba(20,90,50,0.8)' : 'rgba(120,24,22,0.82)'; ctx.fill();
  ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.fillText(text, 58, y + 26);
}

function wrap(text, maxW) {
  const words = text.split(' '); const lines = []; let line = '';
  for (const w of words) {
    const t = line ? line + ' ' + w : w;
    if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t;
  }
  if (line) lines.push(line);
  return lines;
}

function cueText() {
  const custom = $('#cue-custom').value.trim();
  const cue = custom || $('#cue').value;
  const name = $('#client').value.trim();
  return name ? `${name}, ${cue}` : cap(cue);
}

function drawLabel() {
  const e = state.current;
  const x = 28, w = W - 56;
  if (state.split) return drawCompactLabel(x);
  const y = H - 250;
  const g = ctx.createLinearGradient(0, y - 80, 0, H);
  g.addColorStop(0, 'rgba(8,10,14,0)'); g.addColorStop(0.4, 'rgba(8,10,14,0.7)'); g.addColorStop(1, 'rgba(8,10,14,0.92)');
  ctx.fillStyle = g; ctx.fillRect(0, y - 80, W, H - y + 80);
  ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = '#fff';
  fitFont(e.name.toUpperCase(), 700, 56, w);
  ctx.fillText(e.name.toUpperCase(), x, y + 52);
  const sets = $('#sets').value.trim();
  if (sets) {
    ctx.font = '600 32px "Barlow Condensed", "Arial Narrow", sans-serif';
    const sw = ctx.measureText(sets).width + 32;
    roundRect(x, y + 70, sw, 46, 10); ctx.fillStyle = '#ff6a2c'; ctx.fill();
    ctx.fillStyle = '#16100c'; ctx.fillText(sets, x + 16, y + 103);
  }
  ctx.font = '500 30px "Figtree", "Helvetica Neue", Arial, sans-serif';
  ctx.fillStyle = '#e8ecf2';
  wrap(cueText(), w).slice(0, 2).forEach((l, i) => ctx.fillText(l, x, y + 158 + i * 36));
  ctx.font = '600 20px "Figtree", "Helvetica Neue", Arial, sans-serif';
  ctx.fillStyle = 'rgba(232,236,242,0.55)';
  ctx.fillText('JAMIE ATLAS PERSONAL TRAINING', x, H - 26);
}

function fitFont(text, weight, size, maxW) {
  let s = size;
  do { ctx.font = `${weight} ${s}px "Barlow Condensed", "Arial Narrow", sans-serif`; s -= 2; } while (ctx.measureText(text).width > maxW && s > 20);
}

function drawCompactLabel(x) {
  const e = state.current, y = H - 118;
  const g = ctx.createLinearGradient(0, y - 30, 0, H);
  g.addColorStop(0, 'rgba(8,10,14,0)'); g.addColorStop(0.35, 'rgba(8,10,14,0.85)'); g.addColorStop(1, 'rgba(8,10,14,0.95)');
  ctx.fillStyle = g; ctx.fillRect(0, y - 30, W, H - y + 30);
  ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#fff';
  const title = e.name.toUpperCase();
  const sets = $('#sets').value.trim();
  ctx.font = '600 28px "Barlow Condensed", "Arial Narrow", sans-serif';
  const pillW = sets ? ctx.measureText(sets).width + 42 : 0;
  fitFont(title, 700, 44, W - 2 * x - pillW);
  ctx.fillText(title, x, y + 44);
  if (sets) {
    const tx = x + ctx.measureText(title).width + 16;
    ctx.font = '600 28px "Barlow Condensed", "Arial Narrow", sans-serif';
    const sw = ctx.measureText(sets).width + 26;
    roundRect(tx, y + 12, sw, 40, 9); ctx.fillStyle = '#ff6a2c'; ctx.fill();
    ctx.fillStyle = '#16100c'; ctx.fillText(sets, tx + 13, y + 41);
  }
  ctx.font = '600 20px "Figtree", "Helvetica Neue", Arial, sans-serif';
  ctx.fillStyle = 'rgba(232,236,242,0.55)';
  ctx.fillText('JAMIE ATLAS PERSONAL TRAINING', x, H - 26);
}

function frame(now) {
  requestAnimationFrame(frame);
  if (!stage || !state.current) return;
  if (document.hidden) return;
  const t = (now - clock) / 1000;
  if (state.split) {
    ctx.drawImage(stage.render(t, 'fault'), 0, 0);
    ctx.drawImage(stage.render(t, 'good'), 0, H / 2);
    ctx.fillStyle = 'rgba(255,255,255,0.14)'; ctx.fillRect(0, H / 2 - 2, W, 4);
    const f = window.FAULTS[state.current.fault];
    drawBadge(W - 70, 70, false); drawBadge(W - 70, H / 2 + 70, true);
    drawCaption(f.bad, 44, false); drawCaption(f.good, H / 2 + 44, true);
  } else {
    ctx.drawImage(stage.render(t, 'normal'), 0, 0);
    if (state.showMap) drawMap();
  }
  if (state.label) drawLabel();
}

// ---------------------------------------------------------------- video
function pickType() {
  const types = ['video/mp4;codecs=avc1.42E01E', 'video/mp4;codecs=avc1', 'video/mp4', 'video/webm;codecs=vp9', 'video/webm'];
  return types.find((t) => window.MediaRecorder && MediaRecorder.isTypeSupported(t));
}

async function makeVideo() {
  if (state.recording || !stage) return;
  const type = pickType();
  if (!type) { $('#status').textContent = 'This browser cannot record video. Try Chrome or Safari.'; return; }
  const loops = Math.max(state.current && stage.spec.cycles || 3, Math.ceil(5 / stage.cycle));
  const dur = loops * stage.cycle;
  const stream = comp.captureStream(30);
  const rec = new MediaRecorder(stream, { mimeType: type, videoBitsPerSecond: 5_000_000 });
  const chunks = [];
  rec.ondataavailable = (ev) => ev.data.size && chunks.push(ev.data);
  state.recording = true;
  $('#make').disabled = true;
  $('#video-out').hidden = true;
  clock = performance.now();
  rec.start(250);
  const t0 = performance.now();
  const tick = setInterval(() => {
    const s = (performance.now() - t0) / 1000;
    $('#status').textContent = `Recording ${Math.min(s, dur).toFixed(1)} of ${dur.toFixed(1)} s`;
    $('#bar').style.width = Math.min(100, (s / dur) * 100) + '%';
  }, 100);
  await new Promise((r) => setTimeout(r, dur * 1000 + 120));
  rec.stop();
  await new Promise((r) => { rec.onstop = r; });
  clearInterval(tick);
  stream.getTracks().forEach((t) => t.stop());
  const ext = type.includes('mp4') ? 'mp4' : 'webm';
  const blob = new Blob(chunks, { type: type.split(';')[0] });
  const client = $('#client').value.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-');
  state.video = { blob, ext, name: `${client ? client + '-' : ''}${state.current.id}${state.split ? '-right-vs-wrong' : ''}.${ext}` };
  const v = $('#video');
  if (v.src) URL.revokeObjectURL(v.src);
  v.src = URL.createObjectURL(blob);
  $('#video-out').hidden = false;
  $('#video-size').textContent = `${state.video.name} · ${(blob.size / 1e6).toFixed(1)} MB · ${dur.toFixed(1)} s`;
  $('#status').textContent = ext === 'mp4' ? 'Video ready.' : 'Video ready. This browser made a WebM file; Safari or recent Chrome make MP4, which WhatsApp prefers.';
  $('#bar').style.width = '0%';
  state.recording = false;
  $('#make').disabled = false;
}

async function saveVideo() {
  if (!state.video) return;
  const { blob, name } = state.video;
  if (downloads) {
    try { await downloads.save({ filename: name, data: blob }); $('#status').textContent = 'Saved. Attach it in WhatsApp or iMessage.'; }
    catch (err) { $('#status').textContent = err?.code === 'declined' ? 'Save cancelled.' : 'Could not save the video here.'; }
    return;
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = name; document.body.append(a); a.click(); a.remove();
  $('#status').textContent = 'Saved to your downloads.';
}

function message() {
  const e = state.current, name = $('#client').value.trim();
  const sets = $('#sets').value.trim();
  const custom = $('#cue-custom').value.trim() || $('#cue').value;
  return `${name ? 'Hi ' + name + '! ' : ''}Here's your ${e.name.toLowerCase()}${sets ? ': ' + sets : ''}. Key cue: ${custom}. Watch the video before you start. - Jamie`;
}
async function copyMessage() {
  const text = message();
  $('#msg').value = text;
  try { await navigator.clipboard.writeText(text); $('#status').textContent = 'Message copied.'; }
  catch { $('#msg').select(); $('#status').textContent = 'Select the message below and copy it.'; }
}

// ---------------------------------------------------------------- boot
function boot() {
  chips($('#area'), ['All', 'Legs', 'Push', 'Pull', 'Core', 'Mobility'], 'area');
  chips($('#where'), ['Any', 'Home', 'Gym'], 'where');
  const ms = $('#muscle');
  ms.append(new Option('Any muscle', ''), ...Object.entries(LABEL).map(([k, v]) => new Option(v, k)));
  ms.addEventListener('change', () => { state.muscle = ms.value; renderList(); });
  $('#q').addEventListener('input', (ev) => { state.q = ev.target.value; renderList(); });
  $('#rehab').addEventListener('change', (ev) => { state.rehab = ev.target.checked; renderList(); });
  $('#demo').addEventListener('change', (ev) => { state.demo = ev.target.checked; renderList(); });
  $('#map').addEventListener('change', (ev) => { state.showMap = ev.target.checked; });
  $('#labelon').addEventListener('change', (ev) => { state.label = ev.target.checked; });
  $('#split').addEventListener('change', (ev) => { state.split = ev.target.checked; if (stage) applySize(); });
  $('#client').value = state.client;
  $('#client').addEventListener('input', (ev) => store.set('client', ev.target.value));
  $('#make').addEventListener('click', makeVideo);
  $('#save').addEventListener('click', saveVideo);
  $('#copy').addEventListener('click', copyMessage);
  $('#back').addEventListener('click', () => $('#browse').scrollIntoView({ behavior: 'smooth' }));

  try {
    stage = new Stage(W, H);
    mini = new MiniMap();
  } catch (err) {
    $('#status').textContent = 'This device could not start 3D graphics, so previews are unavailable.';
  }
  const start = EX.find((e) => e.id === location.hash.slice(1)) || EX.find((e) => e.id === 'goblet-squat');
  select(start);
  addEventListener('hashchange', () => {
    const e = EX.find((x) => x.id === location.hash.slice(1));
    if (e && e !== state.current) select(e);
  });
  requestAnimationFrame(frame);
  window.claude?.use?.('downloads').then((d) => { downloads = d; }).catch(() => {});
  window.__ready = true;
}

(document.fonts?.ready || Promise.resolve()).then(boot);
