#!/usr/bin/env node
// 진짜 화면 캡처. 로그인한 GitHub 같은 실제 제품 화면과 로컬 HTML 포스터를 고해상도 스틸·스크롤 시퀀스로 찍는다.
//
// 사용법
//   node capture.mjs login  --profile <dir> --url <로그인 URL> --check <셀렉터> [--minutes 10]
//   node capture.mjs shots  <spec.json> --out <dir> [--profile <dir>]
//   node capture.mjs forget --profile <dir>
//
//   프로필 수명: mktemp -d 로 프로젝트 밖에 폴더를 만들고 → login(사용자가 직접 로그인) → shots → forget.
//   login 은 헤드 있는 Chrome 을 띄우고 2초마다 --check 를 확인해, 맞으면 창을 닫고 끝난다. 프로필에 표식 파일을 남긴다.
//   shots 는 --profile 이 있으면 그 로그인 상태로, 없으면 새 컨텍스트(로그아웃 상태)로 찍는다. login 이 만든 프로필만 받는다.
//   forget 은 표식이 있는 폴더만 지운다.
//
// 스펙(spec.json). 무엇을 찍었는지의 유일한 입력이자 기록
//   { "viewport": {"width": 1920, "height": 1080}, "scale": 2, "colorScheme": "dark", "locale": "en-US", "wait": 3000,
//     "check": "meta[name=\"user-login\"]", "redact": ["실명", "닉네임"],
//     "shots": [
//       {"name": "repo",   "url": "https://github.com/owner/repo", "full": true},
//       {"name": "readme", "url": "https://github.com/owner/repo", "scroll": {"to": "article.markdown-body", "offset": -80, "frames": 90}},
//       {"name": "poster", "url": "poster/poster.html?img=A", "viewport": {"width": 2400, "height": 3600}, "scale": 1, "wait": 0} ] }
//   위의 값은 기본값이다(check·redact 는 기본 없음). shot 의 viewport·scale·colorScheme·locale·wait·redact 는 최상위 값을 덮어쓴다.
//   url 이 스킴 없는 상대 경로면 스펙 파일 폴더 기준 로컬 파일(file://, 쿼리 유지)이다.
//   check   첫 shot 의 화면에서 이 셀렉터가 보여야 한다. 아니면 아무것도 찍지 않고 종료 코드 2.
//           meta 는 content 가 비면 일치로 치지 않는다(로그아웃 GitHub 도 content="" 인 user-login meta 를 내보낸다).
//   redact  모든 스틸·프레임 직전에 보이는 글자(텍스트 노드)에서 이 문자열을 같은 길이의 █ 로 바꾼다(대소문자 무시).
//           shot 마다 "가림 N곳 (redact[i]=n …)" 을 출력하니 0 이거나 모자라면 화면을 직접 열어 확인하라.
//           가려지지 않는 것: 이미지 안의 글자(아바타·스크린샷), input 값, 노드 경계를 가로지른 글자, shadow DOM·iframe.
//
// 산출물 (--out <dir>)
//   <name>_view_<scale>x.png      항상. 페이지 위쪽 viewport 한 화면
//   <name>_full_<scale>x.png      full: true 일 때. 전체 페이지(높이 20080 장치 픽셀까지 안 잘림을 확인했다. 더 길면 manifest 높이로 확인)
//   <name>_scroll/0001.jpg …      scroll 이 있을 때. scroll.to(셀렉터 또는 px)+offset 까지 내려가는 프레임 단위 이징 스크롤, 프레임마다 한 장
//   manifest.json                 기존 항목에 합친다. { "<--out 기준 상대 경로>": [픽셀 너비, 픽셀 높이] }
//                                 스크롤은 폴더 하나가 항목이다: "<name>_scroll/": [너비, 높이, 프레임 수]
//
// 종료 코드: 0 정상, 1 사용법·실행 오류·일부 shot 실패, 2 check 불일치(로그인 안 됨), 3 login 시간 초과 또는 창이 먼저 닫힘
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright-core')); }
catch { console.error('playwright-core 가 없다. 한 번만: cd ' + path.dirname(new URL(import.meta.url).pathname) + ' && npm install'); process.exit(1); }

const MARKER = '.lightplay-capture-profile';
const MASK = '█';
const DEFAULTS = { viewport: { width: 1920, height: 1080 }, scale: 2, colorScheme: 'dark', locale: 'en-US', wait: 3000, redact: [] };
// file:// 포스터가 ../reel/fonts 와 ../assets 를 다른 origin 으로 막히지 않고 읽게 한다
const CHROME_ARGS = ['--force-color-profile=srgb', '--allow-file-access-from-files'];

class Exit extends Error {
  constructor(message, code = 1) { super(message); this.code = code; }
}

const sleep = ms => new Promise(r => setTimeout(r, ms));
const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const isProfile = dir => fs.existsSync(path.join(dir, MARKER));

const [cmd, ...rest] = process.argv.slice(2);
const opt = {};
const pos = [];
for (let i = 0; i < rest.length; i++) {
  if (rest[i].startsWith('--')) opt[rest[i].slice(2)] = rest[++i];
  else pos.push(rest[i]);
}

function profileArg() {
  if (!opt.profile) throw new Exit('--profile <폴더> 가 필요하다');
  return path.resolve(opt.profile);
}

// 로그아웃 GitHub 도 content="" 인 user-login meta 를 내보내므로, meta 는 content 가 비어 있으면 일치로 치지 않는다
const matches = (page, selector) => page.evaluate(sel => {
  const el = document.querySelector(sel);
  return !!el && !(el.tagName === 'META' && !el.content);
}, selector);

// 이미지 폭·높이를 파일 헤더에서 직접 읽는다(PNG IHDR, JPEG SOFn).
function imageSize(b) {
  if (b[0] === 0x89) return [b.readUInt32BE(16), b.readUInt32BE(20)];
  for (let i = 2; i < b.length; i += 2 + b.readUInt16BE(i + 2)) {
    const m = b[i + 1];
    if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return [b.readUInt16BE(i + 7), b.readUInt16BE(i + 5)];
  }
  throw new Error('이미지 크기를 읽지 못했다');
}

function toHref(url, dir) {
  if (/^[a-z][a-z0-9+.-]+:/i.test(url)) return url;
  const [, file, tail] = url.match(/^([^?#]*)(.*)$/);
  return pathToFileURL(path.resolve(dir, file)).href + tail;
}

// 스펙을 읽어 shot 마다 기본값을 합친 실행 계획으로 만든다. 잘못된 입력은 여기서 멈춘다.
function loadSpec(file) {
  let spec;
  try { spec = JSON.parse(fs.readFileSync(file, 'utf8')); }
  catch (e) { throw new Exit(`스펙을 읽지 못했다: ${file} (${e.message.split('\n')[0]})`); }
  if (!Array.isArray(spec.shots) || !spec.shots.length) throw new Exit('스펙 오류: shots 가 비었다');
  const top = { ...DEFAULTS };
  for (const k of Object.keys(DEFAULTS)) if (k in spec) top[k] = spec[k];
  const names = new Set();
  const plan = spec.shots.map((s, i) => {
    const bad = msg => { throw new Exit(`스펙 오류: shots[${i}] ${msg}`); };
    if (typeof s.name !== 'string' || !s.name || s.name.startsWith('.') || /[\/\\]/.test(s.name)) bad('name 은 / 나 \\ 없는 비지 않은 문자열이어야 한다');
    if (names.has(s.name)) bad(`name '${s.name}' 이 겹친다`);
    names.add(s.name);
    if (typeof s.url !== 'string' || !s.url) bad('url 이 필요하다');
    const r = { ...top, ...s, viewport: { ...top.viewport, ...s.viewport }, href: toHref(s.url, path.dirname(file)) };
    if (!(r.viewport.width > 0 && r.viewport.height > 0)) bad('viewport 는 양수여야 한다');
    if (!(r.scale > 0)) bad('scale 은 양수여야 한다');
    if (!(r.wait >= 0)) bad('wait 는 0 이상이어야 한다');
    if (!Array.isArray(r.redact) || r.redact.some(w => typeof w !== 'string' || !w)) bad('redact 는 비지 않은 문자열 배열이어야 한다');
    if (r.scroll) {
      if (r.scroll.to === undefined) bad('scroll.to 가 필요하다');
      if (r.scroll.frames !== undefined && !(Number.isInteger(r.scroll.frames) && r.scroll.frames >= 2)) bad('scroll.frames 는 2 이상 정수여야 한다');
    }
    return r;
  });
  return { spec, plan };
}

function writeManifest(out, entries) {
  const file = path.join(out, 'manifest.json');
  let all = {};
  if (fs.existsSync(file)) {
    try { all = JSON.parse(fs.readFileSync(file, 'utf8')); }
    catch { throw new Exit(`${file} 를 읽지 못했다. 깨졌다면 지우고 다시 실행하라`); }
  }
  Object.assign(all, entries);
  const lines = Object.keys(all).sort().map(k => ` ${JSON.stringify(k)}: ${JSON.stringify(all[k])}`);
  fs.writeFileSync(file, `{\n${lines.join(',\n')}\n}\n`);
}

// 폰트와 이미지 디코딩이 끝나길 기다린다. 아직 요청도 안 된 lazy 이미지는 기다리지 않고, 멈춘 이미지 하나가 전체를 잡지 못하게 10초로 끊는다.
const settle = page => page.evaluate(() => Promise.race([
  document.fonts.ready.then(() => Promise.all([...document.images].map(i => (i.loading === 'lazy' && !i.complete ? null : i.decode().catch(() => null))))),
  new Promise(r => setTimeout(r, 10000)),
]));

// 보이는 텍스트 노드의 redact 문자열을 같은 길이의 █ 로 바꾸고, redact 순서대로 바꾼 횟수를 돌려준다. 긴 것부터 바꿔 겹치는 이름을 놓치지 않는다.
const mask = (page, words) => (words.length ? page.evaluate(([words, MASK]) => {
  const res = words.map(w => new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'));
  const order = words.map((_, i) => i).sort((a, b) => words[b].length - words[a].length);
  const counts = words.map(() => 0);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  for (let n = walker.nextNode(); n; n = walker.nextNode()) if (!n.parentElement?.closest('script,style,noscript')) nodes.push(n);
  for (const n of nodes) {
    let t = n.nodeValue;
    for (const i of order) t = t.replace(res[i], m => { counts[i]++; return MASK.repeat(m.length); });
    if (t !== n.nodeValue) n.nodeValue = t;
  }
  return counts;
}, [words, MASK]) : []);

async function captureShot(page, s, out, check) {
  const hits = s.redact.map(() => 0);
  const entries = {};
  const shoot = async (file, o) => {
    (await mask(page, s.redact)).forEach((n, i) => { hits[i] += n; });
    return imageSize(await page.screenshot({ path: path.join(out, file), ...o }));
  };

  await page.setViewportSize(s.viewport);
  const res = await page.goto(s.href, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(s.wait);
  await settle(page);
  if (check && !(await matches(page, check))) {
    throw new Exit(`로그인 확인 실패: 첫 화면에서 '${check}' 에 일치하는 것이 없다. 아무것도 찍지 않았다. `
      + (opt.profile ? '프로필의 로그인이 풀렸다. login 으로 다시 로그인하라.' : '--profile 없이 실행했다. login 으로 프로필을 만들고 --profile 을 붙여라.'), 2);
  }
  if (res && res.status() >= 400) throw new Error(`HTTP ${res.status()}`);

  // 대상을 못 찾으면 아무 파일도 쓰기 전에 실패하도록 스틸보다 먼저 푼다
  const { to, offset = 0, frames = 90 } = s.scroll || {};
  let end = 0;
  if (s.scroll) {
    const top = typeof to === 'number' ? to : await page.evaluate(sel => {
      const el = document.querySelector(sel);
      return el && el.getBoundingClientRect().top + window.scrollY;
    }, to);
    if (top === null) throw new Error(`scroll.to 대상 '${to}' 를 찾지 못했다`);
    end = Math.max(0, Math.round(top + offset));
  }

  const tag = `${s.scale}x`;
  entries[`${s.name}_view_${tag}.png`] = await shoot(`${s.name}_view_${tag}.png`);
  if (s.full) entries[`${s.name}_full_${tag}.png`] = await shoot(`${s.name}_full_${tag}.png`, { fullPage: true });
  if (s.scroll) {
    const dir = `${s.name}_scroll`;
    fs.rmSync(path.join(out, dir), { recursive: true, force: true });
    let size;
    for (let f = 0; f < frames; f++) {
      // behavior: 'instant' 로 페이지의 scroll-behavior: smooth 가 프레임 사이를 보간하지 못하게 한다
      await page.evaluate(y => window.scrollTo({ top: y, behavior: 'instant' }), Math.round(end * ease(f / (frames - 1))));
      size = await shoot(`${dir}/${String(f + 1).padStart(4, '0')}.jpg`, { type: 'jpeg', quality: 92 });
    }
    entries[`${dir}/`] = [...size, frames];
  }

  writeManifest(out, entries);
  const files = Object.entries(entries).map(([k, v]) => `${k} ${v[0]}x${v[1]}${v[2] ? ` ${v[2]}프레임` : ''}`).join(', ');
  const total = hits.reduce((a, b) => a + b, 0);
  console.log(`ok ${s.name}: ${files}` + (s.redact.length ? ` · 가림 ${total}곳 (${hits.map((n, i) => `redact[${i}]=${n}`).join(', ')})` : ''));
  if (s.redact.length && !total) console.error(`경고: ${s.name} 에서 redact 대상을 하나도 찾지 못했다. 이 화면에 없거나 이미지 안의 글자일 수 있다.`);
}

async function shots() {
  const [specFile] = pos;
  if (!specFile || !opt.out) throw new Exit('사용법: node capture.mjs shots <spec.json> --out <폴더> [--profile <폴더>]');
  const { spec, plan } = loadSpec(path.resolve(specFile));
  const out = path.resolve(opt.out);
  const profile = opt.profile && path.resolve(opt.profile);
  if (profile && !isProfile(profile)) throw new Exit(`${profile} 는 login 으로 만든 캡처 프로필이 아니다(표식 ${MARKER} 없음)`);
  fs.mkdirSync(out, { recursive: true });

  const browser = profile ? null : await chromium.launch({ channel: 'chrome', headless: true, args: CHROME_ARGS });
  let cur = null;   // 배율·색상·언어는 컨텍스트 단위라서, 이 셋이 바뀔 때만 컨텍스트를 새로 연다
  const failed = [];
  try {
    for (const [i, s] of plan.entries()) {
      const key = [s.scale, s.colorScheme, s.locale].join('|');
      if (cur?.key !== key) {
        await cur?.ctx.close();
        const o = { viewport: s.viewport, deviceScaleFactor: s.scale, colorScheme: s.colorScheme, locale: s.locale };
        const ctx = profile
          ? await chromium.launchPersistentContext(profile, { channel: 'chrome', headless: true, args: CHROME_ARGS, ...o })
          : await browser.newContext(o);
        cur = { key, ctx, page: ctx.pages()[0] || await ctx.newPage() };
      }
      try { await captureShot(cur.page, s, out, i === 0 && spec.check); }
      catch (e) {
        if (e instanceof Exit) throw e;
        failed.push(s.name);
        console.error(`실패 ${s.name}: ${e.message.split('\n')[0]}`);
      }
    }
  } finally {
    await cur?.ctx.close().catch(() => {});
    await browser?.close();
  }
  if (failed.length) throw new Exit(`${failed.length}장 실패: ${failed.join(', ')}`);
}

async function login() {
  const profile = profileArg();
  const minutes = Number(opt.minutes || 10);
  if (!opt.url || !opt.check || !(minutes > 0)) throw new Exit('사용법: node capture.mjs login --profile <폴더> --url <로그인 URL> --check <셀렉터> [--minutes 10]');
  fs.mkdirSync(profile, { recursive: true });
  if (!isProfile(profile) && fs.readdirSync(profile).length) throw new Exit(`${profile} 는 비어 있지 않고 캡처 프로필도 아니다. 평소 쓰는 브라우저 프로필일 수 있으니 mktemp -d 로 새 폴더를 만들어 써라`);
  fs.writeFileSync(path.join(profile, MARKER), 'lightplay capture profile\n');

  const ctx = await chromium.launchPersistentContext(profile, { channel: 'chrome', headless: false, viewport: null, locale: 'en-US', args: ['--window-size=1280,900'] });
  let closed = false;
  ctx.on('close', () => { closed = true; });
  try {
    const page = ctx.pages()[0] || await ctx.newPage();
    await page.goto(opt.url);
    console.log(`로그인 창이 열렸다. 로그인이 확인되면 자동으로 닫힌다(최대 ${minutes}분).`);
    const until = Date.now() + minutes * 60000;
    while (!closed && Date.now() < until) {
      for (const p of ctx.pages()) {
        if (await matches(p, opt.check).catch(() => false)) {   // 페이지 이동 중에는 evaluate 가 던진다
          console.log('로그인 확인. 쿠키는 프로필 폴더에 남았다.');
          await sleep(1500);   // 쿠키가 디스크에 쓰이길 기다린다
          return;
        }
      }
      await sleep(2000);
    }
    throw new Exit(closed ? '로그인하기 전에 창이 닫혔다' : `${minutes}분 안에 로그인하지 않았다`, 3);
  } finally {
    await ctx.close().catch(() => {});
  }
}

async function forget() {
  const profile = profileArg();
  if (!fs.existsSync(profile)) throw new Exit(`${profile} 폴더가 없다`);
  if (!isProfile(profile)) throw new Exit(`${profile} 에 표식 ${MARKER} 가 없다. 캡처 프로필이 아니라서 지우지 않는다`);
  fs.rmSync(profile, { recursive: true, force: true });
  console.log(`프로필 삭제: ${profile}`);
}

const commands = { login, shots, forget };
if (!commands[cmd]) {
  console.error('사용법: node capture.mjs <login|shots|forget> ...  (자세한 내용은 이 파일 맨 위 주석)');
  process.exit(1);
}
commands[cmd]().catch(e => {
  console.error(e instanceof Exit ? e.message : String(e.stack || e).split('\n').slice(0, 4).join('\n'));
  process.exitCode = e.code ?? 1;
});
