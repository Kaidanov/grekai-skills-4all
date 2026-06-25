#!/usr/bin/env node
/**
 * build-tutorial-page.mjs — generate a self-contained HTML "audio-slideshow" player for ONE
 * tutorial. NO ffmpeg: it plays the per-step mp3s (from synthesize-audio.mjs) in sync with the
 * step screenshots, with captions, a light/dark toggle, logo + accent from config, and controls.
 *
 * Usage:
 *   node build-tutorial-page.mjs --steps <out>/<slug>-steps.json \
 *        [--audio <out>/<slug>-audio.json] [--config tutorial.config.json] \
 *        [--out <out>/index.html]
 *
 * --steps  : the manifest (image + narration + title per step).
 * --audio  : optional <slug>-audio.json (audio file + duration per step) → enables sound.
 * Produces a single index.html next to the screenshots/audio (paths stay relative).
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';

function arg(n, fb) { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1] : fb; }
function esc(s = '') { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

const stepsPath = resolve(arg('steps'));
if (!existsSync(stepsPath)) { console.error(`ERROR: --steps not found: ${stepsPath}`); process.exit(2); }
const manifest = JSON.parse(readFileSync(stepsPath, 'utf8'));
const dir = dirname(stepsPath);

const audioPath = arg('audio', join(dir, `${manifest.slug}-audio.json`));
const audioData = existsSync(audioPath) ? JSON.parse(readFileSync(audioPath, 'utf8')) : null;

const cfgPath = arg('config');
const cfg = cfgPath && existsSync(resolve(cfgPath)) ? JSON.parse(readFileSync(resolve(cfgPath), 'utf8')) : {};
const brand = cfg.brand || {};
const accent = brand.accent || '#6aa3ff';
const accentDark = brand.accentDark || accent;
const theme = brand.defaultTheme === 'light' ? 'light' : 'dark';
const logo = brand.logo || '';

const steps = manifest.steps.map((s, idx) => {
  const a = audioData?.steps?.[idx];
  return { img: s.image, title: s.title || `Step ${idx + 1}`, caption: s.narration || '', audio: a?.file || null, duration: a?.durationSec || 0 };
});
const data = { title: manifest.title || manifest.slug, voice: (audioData?.voice || manifest.voice || ''), steps };
const out = resolve(arg('out', join(dir, 'index.html')));
mkdirSync(dirname(out), { recursive: true });

const json = JSON.stringify(data).replace(/</g, '\\u003c');

const html = `<!DOCTYPE html>
<html lang="en" data-theme="${theme}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>${esc(data.title)}</title>
<style>
  :root{--bg:#f6f8fb;--panel:#fff;--line:#dce3ec;--text:#18212f;--muted:#5a6675;--accent:${esc(accent)};--shadow:0 8px 30px rgba(20,30,50,.12)}
  :root[data-theme="dark"]{--bg:#0f1218;--panel:#171b24;--line:#2a3140;--text:#e7ebf2;--muted:#9aa6b8;--accent:${esc(accentDark)};--shadow:0 8px 30px rgba(0,0,0,.45)}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  header{display:flex;align-items:center;justify-content:space-between;gap:12px;max-width:980px;margin:0 auto;padding:18px 20px}
  .brand{display:flex;align-items:center;gap:10px}.brand img{height:26px}.brand b{font-size:16px}
  #toggle{background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:999px;width:36px;height:36px;font-size:17px;cursor:pointer}
  .player{max-width:980px;margin:0 auto;padding:0 20px 40px}
  .stage{position:relative;background:#000;border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:var(--shadow);aspect-ratio:${manifest.width || 16}/${manifest.height || 9}}
  .stage img{width:100%;height:100%;object-fit:contain;display:block;background:#0b0d12}
  .cc{position:absolute;left:0;right:0;bottom:0;padding:14px 18px;background:linear-gradient(transparent,rgba(0,0,0,.82));color:#fff;font-size:18px;line-height:1.4}
  .cc b{color:#9cc3ff;margin-right:8px}
  .bar{display:flex;gap:5px;margin:12px 0 6px}
  .bar i{flex:1;height:5px;border-radius:3px;background:var(--line);overflow:hidden;cursor:pointer}
  .bar i span{display:block;height:100%;width:0;background:var(--accent)}
  .bar i.done span{width:100%}
  .ctrls{display:flex;align-items:center;gap:10px;margin-top:8px}
  .ctrls button{background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:10px;padding:9px 14px;cursor:pointer;font-size:14px}
  .ctrls button:hover{border-color:var(--accent)}
  .ctrls .play{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600;min-width:96px}
  .ctrls .sp{flex:1}
  .ctrls .count{color:var(--muted);font-variant-numeric:tabular-nums}
  .meta{color:var(--muted);font-size:12.5px;margin-top:10px;text-align:center}
  a{color:var(--accent)}
</style>
</head>
<body>
<header>
  <div class="brand">${logo ? `<img src="${esc(logo)}" alt="" onerror="this.style.display='none'"/>` : ''}<b>${esc(data.title)}</b></div>
  <button id="toggle" title="Light / dark" aria-label="Toggle light/dark">◐</button>
</header>
<div class="player">
  <div class="stage">
    <img id="frame" alt="" />
    <div class="cc" id="cc"></div>
  </div>
  <div class="bar" id="bar"></div>
  <div class="ctrls">
    <button class="play" id="play">▶ Play</button>
    <button id="prev">◀ Prev</button>
    <button id="next">Next ▶</button>
    <button id="restart">↺ Restart</button>
    <button id="ccBtn">CC on</button>
    <span class="sp"></span>
    <span class="count" id="count"></span>
  </div>
  <p class="meta">Narrated with <b id="voice"></b> · built by the <a href="https://github.com/Kaidanov/grekai-skills-4all/tree/main/skills/tutorial">tutorial</a> skill</p>
</div>
<script type="application/json" id="data">${json}</script>
<script>
  const data = JSON.parse(document.getElementById('data').textContent);
  const root = document.documentElement, T = 'tutorial-theme';
  const saved = localStorage.getItem(T); if (saved) root.setAttribute('data-theme', saved);
  document.getElementById('toggle').onclick = () => { const n = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; root.setAttribute('data-theme', n); localStorage.setItem(T, n); };

  const frame = document.getElementById('frame'), cc = document.getElementById('cc'), bar = document.getElementById('bar'), count = document.getElementById('count');
  document.getElementById('voice').textContent = data.voice || 'neural voice';
  const audio = new Audio(); let i = 0, playing = false, ccOn = true;
  data.steps.forEach((_, n) => { const seg = document.createElement('i'); seg.innerHTML = '<span></span>'; seg.onclick = () => go(n, playing); bar.appendChild(seg); });
  const segs = [...bar.children];

  function render() {
    const s = data.steps[i];
    frame.src = s.img; frame.alt = s.title;
    cc.textContent = '';
    if (ccOn) { const b = document.createElement('b'); b.textContent = (i + 1); cc.appendChild(b); cc.appendChild(document.createTextNode(s.caption)); }
    count.textContent = (i + 1) + ' / ' + data.steps.length;
    segs.forEach((seg, n) => { seg.classList.toggle('done', n < i); seg.querySelector('span').style.width = n < i ? '100%' : '0%'; });
  }
  function go(n, resume) {
    i = Math.max(0, Math.min(data.steps.length - 1, n));
    render();
    const s = data.steps[i];
    audio.pause();
    if (s.audio) { audio.src = s.audio; audio.currentTime = 0; if (resume) audio.play().catch(() => {}); }
  }
  function setPlay(on) { playing = on; document.getElementById('play').textContent = on ? '⏸ Pause' : '▶ Play'; }
  document.getElementById('play').onclick = () => {
    const s = data.steps[i];
    if (playing) { audio.pause(); setPlay(false); }
    else { setPlay(true); if (s.audio) { if (!audio.src) audio.src = s.audio; audio.play().catch(() => {}); } else tick(); }
  };
  document.getElementById('prev').onclick = () => go(i - 1, playing);
  document.getElementById('next').onclick = () => go(i + 1, playing);
  document.getElementById('restart').onclick = () => { go(0, true); setPlay(true); };
  document.getElementById('ccBtn').onclick = (e) => { ccOn = !ccOn; e.target.textContent = ccOn ? 'CC on' : 'CC off'; render(); };

  audio.ontimeupdate = () => { if (audio.duration) segs[i].querySelector('span').style.width = (100 * audio.currentTime / audio.duration) + '%'; };
  audio.onended = () => { if (i < data.steps.length - 1) go(i + 1, true); else setPlay(false); };
  // silent fallback (no audio): advance on a timer using duration or 4s
  let timer = null;
  function tick() { clearTimeout(timer); const d = (data.steps[i].duration || 4) * 1000; timer = setTimeout(() => { if (playing && i < data.steps.length - 1) { go(i + 1, true); tick(); } else setPlay(false); }, d); }

  go(0, false);
</script>
</body>
</html>
`;
writeFileSync(out, html);
console.log(`OK  ${out}  (${steps.length} steps${audioData ? ', with audio' : ', silent'})`);
