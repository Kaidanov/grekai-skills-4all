#!/usr/bin/env node
/**
 * render-tutorial-video.mjs — turn a step manifest (screenshots + narration) into a
 * narrated MP4 + WebVTT captions. Drift-free: every slide is held for exactly its
 * narration audio length (+ a tail pad), so audio never desyncs from the picture.
 *
 * Requires:  ffmpeg  (and ideally ffprobe) + edge-tts (pip install edge-tts).
 *   - Install ffmpeg: Windows `winget install Gyan.FFmpeg` · macOS `brew install ffmpeg` · Linux `apt install ffmpeg`.
 *   - No system install? Point the script at any ffmpeg/ffprobe binary:
 *       FFMPEG_BIN=/path/to/ffmpeg  FFPROBE_BIN=/path/to/ffprobe  node render-tutorial-video.mjs ...
 *     (e.g. reuse a project's node_modules/ffmpeg-static/ffmpeg.exe). If ffprobe is missing, the
 *     script estimates each clip's length from the edge-tts mp3 (48 kbps CBR) instead of failing.
 *
 * Usage:
 *   node render-tutorial-video.mjs --manifest <out>/<slug>-steps.json --out <outputDir>
 *   optional: --voice en-US-JennyNeural
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, mkdirSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve, isAbsolute } from 'node:path';

const FFMPEG = process.env.FFMPEG_BIN || 'ffmpeg';
const FFPROBE = process.env.FFPROBE_BIN || 'ffprobe';

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
      `Is "${cmd}" installed and on PATH? Install ffmpeg, or set FFMPEG_BIN / FFPROBE_BIN. See the skill README → Prerequisites.`);
  }
}
function probeDuration(file) {
  // Prefer ffprobe; if it's unavailable, estimate from the edge-tts mp3 (48 kbps CBR → bytes*8/48000).
  try {
    const out = run(FFPROBE, ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', file]);
    const d = parseFloat(out.toString().trim());
    if (d > 0) return d;
  } catch { /* fall through to size estimate */ }
  return (statSync(file).size * 8) / 48000;
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

console.log(`Rendering "${slug}" — ${steps.length} steps, voice ${voice}\n  ffmpeg=${FFMPEG}  ffprobe=${FFPROBE}`);
steps.forEach((step, i) => {
  const n = String(i + 1).padStart(2, '0');
  const img = isAbsolute(step.image) ? step.image : resolve(baseDir, step.image);
  const mp3 = join(work, `n-${n}.mp3`);

  // 1) synthesize the narration for this step
  run('edge-tts', ['--voice', voice, '--text', step.narration, '--write-media', mp3]);
  const dur = probeDuration(mp3) + tailPad;

  // 2) one fixed-size segment: hold the screenshot for `dur`, pad the audio with silence to match
  const seg = join(work, `seg-${n}.mp4`);
  run(FFMPEG, ['-y', '-loop', '1', '-i', img, '-i', mp3,
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
run(FFMPEG, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c', 'copy', '-movflags', '+faststart', outMp4]);

// captions
const outVtt = join(outDir, `${slug}-narration.vtt`);
writeFileSync(outVtt, `WEBVTT\n\n${cues.join('\n\n')}\n`);

// verify there is an audio stream — never ship a silent video (skipped if ffprobe is unavailable)
let audio = 'audio';
try {
  audio = run(FFPROBE, ['-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'default=nw=1:nk=1', outMp4]).toString().trim();
} catch { console.warn('WARN: ffprobe unavailable — skipping the audio-stream check.'); }
rmSync(work, { recursive: true, force: true });
if (!audio.includes('audio')) { console.error('ERROR: rendered video has NO audio stream — aborting.'); process.exit(1); }

console.log(`\nOK  ${outMp4}\nOK  ${outVtt}\nTotal ${cursor.toFixed(1)}s`);
