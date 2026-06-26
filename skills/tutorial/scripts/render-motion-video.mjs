#!/usr/bin/env node
/**
 * render-motion-video.mjs — turn a RECORDED SESSION VIDEO (real motion of the app,
 * captured by Playwright's recordVideo) + a step manifest into a narrated MP4 with
 * WebVTT captions. This is the "real video" path: the viewer watches the actual app
 * move, with neural narration over it — not a screenshot slideshow.
 *
 * Drift-free by construction: the video is cut into one clip per step (using each
 * step's `atMs` start offset); if a step's narration is LONGER than its motion clip,
 * the clip's last frame is frozen to fill the gap, so narration never desyncs and is
 * always fully audible. Each segment's length = max(clipLength, narrationLength).
 *
 * Audio source (in priority order, so it runs WITHOUT edge-tts when pre-synthesized):
 *   1. --audio <slug>-audio.json   (from synthesize-audio.mjs: per-step mp3 + durationSec)
 *   2. step.audio in the manifest   (explicit mp3 path per step)
 *   3. edge-tts fallback            (synthesize on the fly; needs edge-tts on PATH)
 *
 * Requires: ffmpeg. Playwright already bundles one — point at it if you have no system ffmpeg:
 *   FFMPEG_BIN=/path/to/ffmpeg node render-motion-video.mjs ...
 * ffprobe is OPTIONAL — durations are read from audio.json, and the video length is parsed
 * from ffmpeg's own output when ffprobe is absent.
 *
 * Usage:
 *   node render-motion-video.mjs --manifest <out>/<slug>-steps.json \
 *       [--audio <out>/<slug>-audio.json] [--video <out>/<slug>.webm] --out <out> [--voice ...]
 */
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, mkdirSync, rmSync, existsSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve, isAbsolute } from 'node:path';

const FFMPEG = process.env.FFMPEG_BIN || 'ffmpeg';
const FFPROBE = process.env.FFPROBE_BIN || 'ffprobe';
const DRY = process.argv.includes('--dry-run');   // print the ffmpeg plan, run nothing

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : fallback;
}
function run(cmd, args) {
  if (DRY) { console.log(`DRY  ${cmd} ${args.join(' ')}`); return Buffer.from(''); }
  try {
    return execFileSync(cmd, args, { stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (err) {
    const detail = (err.stderr || err.stdout || '').toString().trim().split('\n').slice(-4).join('\n');
    throw new Error(`\n[${cmd}] failed: ${err.message}\n${detail}\n` +
      `Is "${cmd}" installed and on PATH? Install ffmpeg, or set FFMPEG_BIN / FFPROBE_BIN. ` +
      `Playwright bundles an ffmpeg — see the skill README → Prerequisites.`);
  }
}
// ffmpeg writes "Duration: HH:MM:SS.ss" to stderr on -i; parse it so ffprobe is optional.
function probeWithFfmpeg(file) {
  try {
    execFileSync(FFMPEG, ['-i', file], { stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (err) {
    const s = (err.stderr || '').toString();
    const m = s.match(/Duration:\s*(\d\d):(\d\d):(\d\d(?:\.\d+)?)/);
    if (m) return (+m[1]) * 3600 + (+m[2]) * 60 + parseFloat(m[3]);
  }
  return 0;
}
function probeDuration(file) {
  try {
    const out = run(FFPROBE, ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', file]);
    const d = parseFloat(out.toString().trim());
    if (d > 0) return d;
  } catch { /* fall through */ }
  const d = probeWithFfmpeg(file);
  if (d > 0) return d;
  // last resort for edge-tts mp3 (48 kbps CBR → bytes*8/48000)
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
const outDir = resolve(arg('out', manifest.outDir || baseDir));
mkdirSync(outDir, { recursive: true });

const slug = manifest.slug;
if (!slug) { console.error('ERROR: manifest.slug is required'); process.exit(2); }
const W = Number(manifest.width) || 1920;
const H = Number(manifest.height) || 1080;
const tailPad = (manifest.tailPadMs ?? 600) / 1000;
const voice = arg('voice', manifest.voice || 'en-US-JennyNeural');
const steps = manifest.steps || [];
if (!steps.length) { console.error('ERROR: manifest has no steps'); process.exit(2); }

// Resolve the recorded session video.
const videoArg = arg('video', manifest.video);
if (!videoArg) {
  console.error('ERROR: no recorded video. Pass --video <slug>.webm or set "video" in the manifest.\n' +
    'Record one with Playwright recordVideo (see the skill README → motion video).');
  process.exit(2);
}
const videoPath = isAbsolute(videoArg) ? videoArg : resolve(baseDir, videoArg);
if (!DRY && !existsSync(videoPath)) { console.error(`ERROR: recorded video not found: ${videoPath}`); process.exit(2); }
// --video-dur overrides probing (handy when ffprobe is absent, and required under --dry-run).
const videoDurArg = arg('video-dur');
const videoDur = videoDurArg != null ? Number(videoDurArg) : probeDuration(videoPath);
if (!(videoDur > 0)) { console.error(`ERROR: could not read a duration from ${videoPath} (pass --video-dur <sec>)`); process.exit(1); }

// Optional pre-synthesized audio (from synthesize-audio.mjs) — keeps this ffprobe/edge-tts-free.
let audioMap = null;
const audioArg = arg('audio');
if (audioArg) {
  const aj = JSON.parse(readFileSync(resolve(audioArg), 'utf8'));
  const adir = dirname(resolve(audioArg));
  audioMap = (aj.steps || []).map((s) => ({
    file: isAbsolute(s.file) ? s.file : resolve(adir, s.file),
    dur: Number(s.durationSec) || 0,
  }));
}

// Per-step start offsets (ms). If absent, distribute evenly across the recording.
const haveTimeline = steps.every((s) => Number.isFinite(s.atMs));
if (!haveTimeline) {
  console.warn('WARN: steps lack `atMs` timestamps — distributing them evenly across the recording.');
}
function startAt(i) {
  if (haveTimeline) return Math.max(0, Math.min(videoDur, steps[i].atMs / 1000));
  return (videoDur * i) / steps.length;
}

const work = mkdtempSync(join(tmpdir(), `tutmv-${slug}-`));
const segments = [];
const cues = [];
let cursor = 0;

console.log(`Rendering MOTION video "${slug}" — ${steps.length} steps over ${videoDur.toFixed(1)}s of footage\n` +
  `  ffmpeg=${FFMPEG}  video=${videoPath}`);

steps.forEach((step, i) => {
  const n = String(i + 1).padStart(2, '0');

  // 1) narration audio + duration for this step
  let mp3, narrDur;
  if (audioMap && audioMap[i] && existsSync(audioMap[i].file)) {
    mp3 = audioMap[i].file;
    narrDur = audioMap[i].dur > 0 ? audioMap[i].dur : probeDuration(mp3) + tailPad;
  } else if (step.audio) {
    mp3 = isAbsolute(step.audio) ? step.audio : resolve(baseDir, step.audio);
    narrDur = probeDuration(mp3) + tailPad;
  } else {
    mp3 = join(work, `n-${n}.mp3`);
    run('edge-tts', ['--voice', voice, '--text', step.narration || step.title || '', '--write-media', mp3]);
    narrDur = probeDuration(mp3) + tailPad;
  }

  // 2) this step's window in the recorded footage
  const start = startAt(i);
  const end = i + 1 < steps.length ? startAt(i + 1) : videoDur;
  const clipLen = Math.max(0.3, end - start);
  const segLen = Math.max(clipLen, narrDur);
  const pad = segLen - clipLen;                       // freeze the last frame for this long

  // 3) one fixed-size segment: real motion for clipLen, last-frame freeze for `pad`,
  //    narration audio padded with silence to segLen so picture & voice stay locked.
  const vf = [
    `scale=${W}:${H}:force_original_aspect_ratio=decrease`,
    `pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2`,
    `setsar=1`,
    ...(pad > 0.02 ? [`tpad=stop_mode=clone:stop_duration=${pad.toFixed(3)}`] : []),
    `format=yuv420p`,
  ].join(',');
  const seg = join(work, `seg-${n}.mp4`);
  run(FFMPEG, ['-y', '-ss', start.toFixed(3), '-t', clipLen.toFixed(3), '-i', videoPath, '-i', mp3,
    '-filter_complex', `[0:v]${vf}[v];[1:a]apad[a]`,
    '-map', '[v]', '-map', '[a]', '-t', segLen.toFixed(3),
    '-c:v', 'libx264', '-preset', 'veryfast', '-r', '30',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', seg]);
  segments.push(seg);

  cues.push(`${vtt(cursor)} --> ${vtt(cursor + segLen)}\n${step.narration || step.title || ''}`);
  cursor += segLen;
  const tag = pad > 0.02 ? `motion ${clipLen.toFixed(1)}s + freeze ${pad.toFixed(1)}s` : `motion ${clipLen.toFixed(1)}s`;
  console.log(`  step ${n}  ${segLen.toFixed(1)}s  (${tag})  ${step.title || ''}`);
});

// concat (identical codecs across segments → safe stream copy)
const listFile = join(work, 'list.txt');
writeFileSync(listFile, segments.map((s) => `file '${s.replace(/'/g, "'\\''")}'`).join('\n'));
const outMp4 = join(outDir, `${slug}-motion.mp4`);
run(FFMPEG, ['-y', '-f', 'concat', '-safe', '0', '-i', listFile, '-c', 'copy', '-movflags', '+faststart', outMp4]);

const outVtt = join(outDir, `${slug}-narration.vtt`);
writeFileSync(outVtt, `WEBVTT\n\n${cues.join('\n\n')}\n`);

if (DRY) { rmSync(work, { recursive: true, force: true });
  console.log(`\nDRY-RUN OK  would write ${outMp4}\n            would write ${outVtt}\nTotal ${cursor.toFixed(1)}s`); process.exit(0); }

// never ship a silent video — verify there is an audio stream (skipped if ffprobe is absent)
let audio = 'audio';
try {
  audio = run(FFPROBE, ['-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'default=nw=1:nk=1', outMp4]).toString().trim();
} catch { console.warn('WARN: ffprobe unavailable — skipping the audio-stream check.'); }
rmSync(work, { recursive: true, force: true });
if (!audio.includes('audio')) { console.error('ERROR: rendered video has NO audio stream — aborting.'); process.exit(1); }

console.log(`\nOK  ${outMp4}\nOK  ${outVtt}\nTotal ${cursor.toFixed(1)}s`);
