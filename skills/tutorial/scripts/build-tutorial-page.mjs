#!/usr/bin/env node
/**
 * build-tutorial-page.mjs — generate a self-contained HTML "audio-slideshow" player for ONE
 * tutorial. NO ffmpeg: it plays the per-step mp3s (from synthesize-audio.mjs) in sync with the
 * step screenshots, with captions, a clickable steps list, an acceptance-criteria panel, a
 * light/dark toggle, logo + accent from config, controls, and an optional MP4 download.
 *
 * Robust to deploy quirks: injects a runtime <base> so relative images/audio/mp4 resolve whether
 * the page is opened as `/dir/`, `/dir` (no trailing slash, e.g. Vercel clean URLs), or `/dir/index.html`.
 *
 * Usage:
 *   node build-tutorial-page.mjs --steps <out>/<slug>-steps.json \
 *        [--audio <out>/<slug>-audio.json] [--config tutorial.config.json] [--out <out>/index.html]
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
const data = { title: manifest.title || manifest.slug, voice: (audioData?.voice || manifest.voice || ''), steps, acceptance: manifest.acceptance || [] };
const mp4 = existsSync(join(dir, `${manifest.slug}-jenny.mp4`)) ? `${manifest.slug}-jenny.mp4` : '';
const vtt = existsSync(join(dir, `${manifest.slug}-narration.vtt`)) ? `${manifest.slug}-narration.vtt` : '';
const poster = steps[0]?.img || '';
const out = resolve(arg('out', join(dir, 'index.html')));
mkdirSync(dirname(out), { recursive: true });

const json = JSON.stringify(data).replace(/</g, '\\u003c');

const html = `<!DOCTYPE html>
<html lang="en" data-theme="${theme}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script>/* resolve relative assets whether opened as /dir/, /dir, or /dir/index.html */
(function(){var p=location.pathname;if(p.endsWith('.html')){p=p.replace(/[^/]*$/,'');}else if(!p.endsWith('/')){p+='/';}var b=document.createElement('base');b.setAttribute('href',p);document.head.appendChild(b);})();</script>
<title>${esc(data.title)}</title>
<style>
  :root{--bg:#f4f6fb;--panel:#ffffff;--panel2:#eef2f8;--line:#d8e0ea;--text:#16202e;--muted:#5a6675;--accent:${esc(accent)};--good:#15803d;--shadow:0 10px 34px rgba(20,30,50,.14)}
  :root[data-theme="dark"]{--bg:#0f1218;--panel:#171b24;--panel2:#1d222d;--line:#2a3140;--text:#e7ebf2;--muted:#9aa6b8;--accent:${esc(accentDark)};--good:#3ecf8e;--shadow:0 10px 34px rgba(0,0,0,.5)}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  header{display:flex;align-items:center;justify-content:space-between;gap:12px;max-width:1000px;margin:0 auto;padding:18px 20px}
  .brand{display:flex;align-items:center;gap:10px}.brand img{height:26px}.brand b{font-size:16px}
  #toggle{background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:999px;height:38px;padding:0 14px;font-size:14px;cursor:pointer}
  #toggle:hover{border-color:var(--accent)}
  .wrap{max-width:1000px;margin:0 auto;padding:0 20px 50px}
  .modebar{display:flex;justify-content:center;gap:6px;margin:0 auto 14px}
  .modebar button{background:var(--panel);border:1px solid var(--line);color:var(--muted);border-radius:999px;padding:7px 16px;font-size:13.5px;cursor:pointer}
  .modebar button:hover{border-color:var(--accent)}
  .modebar button.active{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
  .stage video{width:100%;height:100%;display:block;background:#000;object-fit:contain}
  .stage{position:relative;background:#0b0d12;border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:var(--shadow);aspect-ratio:${manifest.width || 16}/${manifest.height || 9}}
  .stage img{width:100%;height:100%;object-fit:contain;display:block;background:#0b0d12}
  .cc{position:absolute;left:0;right:0;bottom:0;padding:14px 18px;background:linear-gradient(transparent,rgba(0,0,0,.85));color:#fff;font-size:17px;line-height:1.4}
  .cc b{color:#9cc3ff;margin-right:8px}
  .bar{display:flex;gap:5px;margin:12px 0 6px}
  .bar i{flex:1;height:6px;border-radius:3px;background:var(--line);overflow:hidden;cursor:pointer}
  .bar i span{display:block;height:100%;width:0;background:var(--accent)}
  .bar i.done span{width:100%}
  .ctrls{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  .ctrls button{background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:10px;padding:9px 14px;cursor:pointer;font-size:14px}
  .ctrls button:hover{border-color:var(--accent)}
  .ctrls .play{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600;min-width:96px}
  .ctrls .sp{flex:1}.ctrls .count{color:var(--muted);font-variant-numeric:tabular-nums}
  .panels{display:grid;grid-template-columns:1.2fr 1fr;gap:16px;margin-top:22px}
  @media(max-width:760px){.panels{grid-template-columns:1fr}}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
  .card h3{margin:0 0 10px;font-size:15px}
  ol.steps{list-style:none;counter-reset:s;margin:0;padding:0}
  ol.steps li{counter-increment:s;display:flex;gap:10px;align-items:flex-start;padding:9px 10px;border-radius:9px;cursor:pointer;border:1px solid transparent}
  ol.steps li:hover{background:var(--panel2)}
  ol.steps li.active{border-color:var(--accent);background:var(--panel2)}
  ol.steps li::before{content:counter(s);flex:0 0 auto;width:22px;height:22px;border-radius:50%;background:var(--accent);color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}
  ol.steps .t{font-weight:600}ol.steps .d{color:var(--muted);font-size:13px}
  ul.ac{list-style:none;margin:0;padding:0}
  ul.ac li{display:flex;gap:9px;align-items:flex-start;padding:7px 0;color:var(--muted);font-size:14px}
  ul.ac li::before{content:"✓";color:var(--good);font-weight:800;flex:0 0 auto}
  .meta{color:var(--muted);font-size:12.5px;margin-top:18px;text-align:center}
  a{color:var(--accent)}
</style>
</head>
<body>
<header>
  <div class="brand">${logo ? `<img src="${esc(logo)}" alt="" onerror="this.style.display='none'"/>` : ''}<b>${esc(data.title)}</b></div>
  <button id="toggle" aria-label="Toggle light/dark">◑ Theme</button>
</header>
<div class="wrap">
  ${mp4 ? `<div class="modebar" id="modebar">
    <button data-mode="pics" class="active">🖼 Step-by-step</button>
    <button data-mode="video">🎬 Video</button>
  </div>` : ''}
  <div class="stage">
    <img id="frame" alt="" />
    ${mp4 ? `<video id="video" controls preload="metadata" playsinline hidden${poster ? ` poster="${esc(poster)}"` : ''}><source src="${esc(mp4)}" type="video/mp4" />${vtt ? `<track kind="captions" src="${esc(vtt)}" srclang="en" label="English" default />` : ''}</video>` : ''}
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
  <div class="panels">
    <section class="card"><h3>Steps</h3><ol class="steps" id="steps"></ol></section>
    ${data.acceptance.length ? `<section class="card"><h3>Acceptance criteria</h3><ul class="ac" id="ac"></ul></section>` : ''}
  </div>
  <p class="meta">Narrated with <b id="voice"></b>${mp4 ? ` · <a href="${esc(mp4)}" download>⬇ Download MP4</a>` : ''} · built by the <a href="https://github.com/Kaidanov/grekai-skills-4all/tree/main/skills/tutorial">tutorial</a> skill · <a href="https://set4u.biz">Set4u</a></p>
</div>
<script type="application/json" id="data">${json}</script>
<script>
  const data = JSON.parse(document.getElementById('data').textContent);
  const root = document.documentElement, T = 'tutorial-theme';
  const saved = localStorage.getItem(T); if (saved) root.setAttribute('data-theme', saved);
  document.getElementById('toggle').onclick = () => { const n = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; root.setAttribute('data-theme', n); localStorage.setItem(T, n); };

  const frame = document.getElementById('frame'), cc = document.getElementById('cc'), bar = document.getElementById('bar'), count = document.getElementById('count');
  const stepsEl = document.getElementById('steps'), acEl = document.getElementById('ac');
  document.getElementById('voice').textContent = data.voice || 'a neural voice';
  const audio = new Audio(); let i = 0, playing = false, ccOn = true;

  data.steps.forEach((s, n) => {
    const seg = document.createElement('i'); seg.innerHTML = '<span></span>'; seg.onclick = () => go(n, playing); bar.appendChild(seg);
    const li = document.createElement('li'); li.onclick = () => go(n, playing);
    const t = document.createElement('div'); t.className = 't'; t.textContent = s.title;
    const d = document.createElement('div'); d.className = 'd'; d.textContent = s.caption;
    const box = document.createElement('div'); box.appendChild(t); box.appendChild(d); li.appendChild(box); stepsEl.appendChild(li);
  });
  const segs = [...bar.children], items = [...stepsEl.children];
  if (acEl) data.acceptance.forEach((a) => { const li = document.createElement('li'); li.textContent = a; acEl.appendChild(li); });

  function render() {
    const s = data.steps[i];
    frame.src = s.img; frame.alt = s.title;
    cc.textContent = '';
    if (ccOn) { const b = document.createElement('b'); b.textContent = (i + 1); cc.appendChild(b); cc.appendChild(document.createTextNode(s.caption)); }
    count.textContent = (i + 1) + ' / ' + data.steps.length;
    segs.forEach((seg, n) => { seg.classList.toggle('done', n < i); seg.querySelector('span').style.width = n < i ? '100%' : '0%'; });
    items.forEach((li, n) => li.classList.toggle('active', n === i));
  }
  function go(n, resume) {
    i = Math.max(0, Math.min(data.steps.length - 1, n)); render();
    const s = data.steps[i]; audio.pause();
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
  document.getElementById('restart').onclick = () => { setPlay(true); go(0, true); };
  document.getElementById('ccBtn').onclick = (e) => { ccOn = !ccOn; e.target.textContent = ccOn ? 'CC on' : 'CC off'; render(); };

  audio.ontimeupdate = () => { if (audio.duration) segs[i].querySelector('span').style.width = (100 * audio.currentTime / audio.duration) + '%'; };
  audio.onended = () => { if (i < data.steps.length - 1) go(i + 1, true); else setPlay(false); };
  let timer = null;
  function tick() { clearTimeout(timer); const d = (data.steps[i].duration || 4) * 1000; timer = setTimeout(() => { if (playing && i < data.steps.length - 1) { go(i + 1, true); tick(); } else setPlay(false); }, d); }

  go(0, false);

  // Pics vs Video mode (only when an MP4 is present)
  const videoEl = document.getElementById('video');
  const modebar = document.getElementById('modebar');
  if (modebar && videoEl) {
    const ctrlsEl = document.querySelector('.ctrls');
    const MKEY = 'tutorial-mode';
    function setMode(m, userInitiated) {
      const isVideo = m === 'video';
      frame.hidden = isVideo; videoEl.hidden = !isVideo;
      cc.style.display = isVideo ? 'none' : '';
      bar.style.display = isVideo ? 'none' : '';
      if (ctrlsEl) ctrlsEl.style.display = isVideo ? 'none' : '';
      if (isVideo) { audio.pause(); setPlay(false); } else { videoEl.pause(); }
      [...modebar.children].forEach((b) => b.classList.toggle('active', b.dataset.mode === m));
      localStorage.setItem(MKEY, m);
    }
    [...modebar.children].forEach((b) => { b.onclick = () => setMode(b.dataset.mode); });
    setMode(localStorage.getItem(MKEY) || 'pics');
  }
</script>
</body>
</html>
`;
writeFileSync(out, html);
console.log(`OK  ${out}  (${steps.length} steps${audioData ? ', with audio' : ', silent'}${data.acceptance.length ? ', +AC' : ''}${mp4 ? ', +MP4' : ''})`);
