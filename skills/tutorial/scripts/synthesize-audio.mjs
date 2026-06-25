#!/usr/bin/env node
/**
 * synthesize-audio.mjs — generate real neural narration (edge-tts) for a tutorial,
 * WITHOUT ffmpeg. Produces one mp3 per step + a combined WebVTT + an <slug>-audio.json.
 * This is the ffmpeg-free path: pair it with build-tutorial-page.mjs (HTML player).
 *
 * Requires on PATH:  edge-tts  (pip install edge-tts). NO ffmpeg needed.
 *
 * Usage:
 *   node synthesize-audio.mjs --manifest <out>/<slug>-steps.json --out <out> [--voice en-US-JennyNeural]
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';

function arg(n, fb) { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1] : fb; }
function run(cmd, args) {
  try { return execFileSync(cmd, args, { stdio: ['ignore', 'pipe', 'pipe'] }); }
  catch (e) { throw new Error(`[${cmd}] failed: ${e.message}\nIs edge-tts installed and on PATH?  pip install edge-tts`); }
}
function lastTs(vtt) {
  // edge-tts writes SRT (HH:MM:SS,mmm); accept both ',' and '.' separators.
  const m = [...vtt.matchAll(/(\d\d):(\d\d):(\d\d)[.,](\d\d\d)/g)];
  if (!m.length) return 0;
  const t = m[m.length - 1];
  return (+t[1]) * 3600 + (+t[2]) * 60 + (+t[3]) + (+t[4]) / 1000;
}
function vttTime(s) {
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${x.toFixed(3).padStart(6, '0')}`;
}

const manifestPath = arg('manifest');
if (!manifestPath) { console.error('ERROR: --manifest <path> is required'); process.exit(2); }
const manifest = JSON.parse(readFileSync(resolve(manifestPath), 'utf8'));
const outDir = resolve(arg('out', dirname(resolve(manifestPath))));
const voice = arg('voice', manifest.voice || 'en-US-JennyNeural');
const slug = manifest.slug;
const steps = manifest.steps || [];
if (!slug || !steps.length) { console.error('ERROR: manifest needs slug + steps'); process.exit(2); }

const audioDir = join(outDir, 'audio');
mkdirSync(audioDir, { recursive: true });
const tailPad = (manifest.tailPadMs ?? 500) / 1000;

const audio = [], cues = [];
let cursor = 0;
console.log(`Synthesizing ${steps.length} steps with ${voice} (no ffmpeg) ...`);
steps.forEach((step, i) => {
  const n = String(i + 1).padStart(2, '0');
  const mp3 = join(audioDir, `step-${n}.mp3`);
  const subs = join(audioDir, `step-${n}.vtt`);
  run('edge-tts', ['--voice', voice, '--text', step.narration, '--write-media', mp3, '--write-subtitles', subs]);
  const dur = lastTs(readFileSync(subs, 'utf8')) + tailPad;
  rmSync(subs, { force: true });
  audio.push({ index: i + 1, file: `audio/step-${n}.mp3`, title: step.title || `Step ${i + 1}`, narration: step.narration, durationSec: +dur.toFixed(3) });
  cues.push(`${vttTime(cursor)} --> ${vttTime(cursor + dur)}\n${step.narration}`);
  cursor += dur;
  console.log(`  step ${n}  ${dur.toFixed(1)}s  ${step.title || ''}`);
});

writeFileSync(join(outDir, `${slug}-narration.vtt`), `WEBVTT\n\n${cues.join('\n\n')}\n`);
writeFileSync(join(outDir, `${slug}-audio.json`), JSON.stringify({ slug, voice, totalSec: +cursor.toFixed(3), steps: audio }, null, 2));
console.log(`\nOK  ${audioDir}\\  (${steps.length} mp3)\nOK  ${slug}-narration.vtt\nOK  ${slug}-audio.json   total ${cursor.toFixed(1)}s`);
