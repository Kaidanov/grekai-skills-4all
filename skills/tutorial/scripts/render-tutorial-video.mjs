#!/usr/bin/env node
/**
 * render-tutorial-video.mjs — turn a step manifest (screenshots + narration) into a
 * narrated MP4 + WebVTT captions. Drift-free: every slide is held for exactly its
 * narration audio length (+ a tail pad), so audio never desyncs from the picture.
 *
 * Requires on PATH:  ffmpeg, ffprobe, and edge-tts  (pip install edge-tts)
 *
 * Usage:
 *   node render-tutorial-video.mjs --manifest <out>/<slug>-steps.json --out <outputDir>
 *   optional: --voice en-US-JennyNeural
 *
 * Manifest shape (written by templates/test-helpers.ts publishManifest):
 *   { "slug": "...", "title": "...", "voice": "en-US-JennyNeural",
 *     "width": 1920, "height": 1080, "tailPadMs": 600,
 *     "steps": [ { "image": "<abs-or-rel>.png", "narration": "spoken text", "title": "..." } ] }
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve, isAbsolute } from 'node:path';

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : fallback;
}
function run(cmd, args) {
  try {
    return execFileSync(cmd, args, { stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (err) {
    const detail = (err.stderr || err.stdout || '').toString().trim().split('\n').slice(-3).join('\n');
    throw new Error(`\n[${cmd}] failed: ${err.message}\n${detail}\n` +
      `Is "${cmd}" installed and on PATH? See the skill README → Prerequisites.`);
  }
}
function probeDuration(file) {
  const out = run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', file]);
  return parseFloat(out.toString().trim()) || 0;
}
function vtt(sec) {
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${s.toFixed(3).padStart(6, '0')}`;
}

const manifestPath = arg('manifest');
if (!manifestPath) { console.error('ERROR: --manifest <path> is required'); process.exit(2); }

const manifest = JSON.parse(readFileSync(resolve(manifestPath), 'utf8'));
const baseDir = dirname(resolve(manifestPath));
const outDir = resolve(arg('out', manifest.outDir || '.'));
mkdirSync(outDir, { recursive: true });

const slug = manifest.slug;
if (!slug) { console.error('ERROR: manifest.slug is required'); process.exit(2); }
const voice = arg('voice', manifest.voice || 'en-US-JennyNeural');
const W = Number(manifest.width) || 1920;
const H = Number(manifest.height) || 1080;
const tailPad = (manifest.tailPadMs ?? 600) / 1000;
const steps = manifest.steps || [];
if (!steps.length) { console.error('ERROR: manifest has no steps'); process.exit(2); }

const work = mkdtempSync(join(tmpdir(), `tut-${slug}-`));
const segments = [];
const cues = [];
let cursor = 0;

console.log(`Rendering "${slug}" — ${steps.length} steps, voice ${voice} ...`);
steps.forEach((step, i) => {
  const n = String(i + 1).padStart(2, '0');
  const img = isAbsolute(step.image) ? step.image : resolve(baseDir, step.image);
  const mp3 = join(work, `n-${n}.mp3`);

  // 1) synthesize the narration for this step
  run('edge-tts', ['--voice', voice, '--text', step.narration, '--write-media', mp3]);
  const dur = probeDuration(mp3) + tailPad;

  // 2) one fixed-size segment: hold the screenshot for `dur`, pad the audio with silence to match
  const seg = join(work, `seg-${n}.mp4`);
  run('ffmpeg', ['-y', '-loop', '1', '-i', img, '-i', mp3,
    '-t', dur.toFixed(3),
    '-vf', `scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p`,
    '-af', 'apad',
    '-c:v', 'libx264', '-preset', 'veryfast', '-r', '30',
    '-c:a', 'aac', '-b:a', '192k', seg]);
  segments.push(seg);

  // 3) caption cue
  cues.push(`${vtt(cursor)} --> ${vtt(cursor + dur)}\n${step.narration}`);
  cursor += dur;
  console.log(`  step ${n}  ${dur.toFixed(1)}s  ${step.title || ''}`);
});

// concat (identical codecs across segments → safe stream copy)
const listFile = join(work, 'list.txt');
writeFileSync(listFile, segments.map((s) => `file '${s.replace(/'/g, "'\\''")}'`).join('\n'));
const outMp4 = join(outDir, `${slug}-jenny.mp4`);
run('ffmpeg', ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c', 'copy', '-movflags', '+faststart', outMp4]);

// captions
const outVtt = join(outDir, `${slug}-narration.vtt`);
writeFileSync(outVtt, `WEBVTT\n\n${cues.join('\n\n')}\n`);

// verify there is an audio stream — never ship a silent video
const audio = run('ffprobe', ['-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'default=nw=1:nk=1', outMp4]).toString().trim();
rmSync(work, { recursive: true, force: true });
if (!audio.includes('audio')) { console.error('ERROR: rendered video has NO audio stream — aborting.'); process.exit(1); }

console.log(`\nOK  ${outMp4}\nOK  ${outVtt}\nTotal ${cursor.toFixed(1)}s`);
