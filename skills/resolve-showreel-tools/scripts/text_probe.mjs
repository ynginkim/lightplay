#!/usr/bin/env node
// 읽는 시간 검사 — 화면에 뜬 글이 사람이 읽을 만큼 오래 완전히 보이는지 잰다. 영어판의 한글 섞임도 같은 스윕으로 찾는다.
//
// 사용법
//   node text_probe.mjs --dir <project>/reel [--step 0.1] [--from 0] [--to 60] [--rate-ko 6] [--rate-en 10]
//                       [--min-chars 2] [--base 0] [--groups] [--group-window 0.5] [--no-hangul] [--json out.json]
//
// 동작: step 초마다 window.__seek(t) 로 장면을 돌려, 보이는 글 블록을 모은다.
//   블록   = 글자가 든 가장 가까운 비인라인 조상(헤드라인 안의 강조 span 은 헤드라인과 한 블록). 요소 정체성으로 시각 사이를 잇는다.
//            같은 요소의 글이 서로 안 겹치는 문장으로 바뀌면(캡션 교체) 다른 블록으로 센다. 타자 효과는 글이 자라는 것이라 한 블록이다.
//   완전히 보임 = 요소와 조상의 누적 불투명도 ≥ 0.9, 글 상자의 95% 이상이 화면 안이면서 overflow 가 visible 이 아닌 조상(마스크 리빌의 래퍼 등)에 안 잘림, 크기 0 아님, 글이 그 블록이 낼 가장 긴 글과 같음(타자 중 제외)
//   판정   = 완전히 보인 가장 긴 연속 구간(초) ≥ 필요 시간 = 글자 수(공백 제외) / 속도 + base 이면 ✓, 아니면 ✗. 한글 음절이 하나라도 있으면 한글 속도
//   완전히 보인 적이 없는 블록(장식·반투명·화면 밖에 걸친 글)은 판정하지 않고 따로 센다.
//   읽는 묶음(--groups 일 때 출력) = 같은 장면에서 가장 긴 완전히 보인 구간이 --group-window 초 안에 시작하고 서로 겹치는 블록 둘 이상(줄마다 요소를 나눈 캡션). 묶음의 보임 = 구성원 구간의 겹침,
//            필요 = 구성원 글자 수 / 속도의 합 + base(같은 글은 한 번만 센다). 한 번에 읽을 글이라 블록 판정과 별도로 합산해 판정한다.
// --no-hangul: 영어판 검사. 보이는 DOM 글자(document.body.innerText)에 한글(음절·자모)이 든 시각을 모두 찾는다.
//
// 한계: 캡처 스크린샷·포스터 같은 이미지 속 글자는 DOM 이 아니라 재지 않는다. 묶음은 시작 시각과 겹침만 보므로 서로 다른 글(헤드라인과 라벨, 한꺼번에 뜨는 목업·콜라주)이 함께 뜨면 한 묶음으로 세어 필요 시간이 부풀려진다. 그래서 기본 출력에서 빼고, 2~3줄 캡션을 확인할 때 --groups 로 본다. 시간 해상도는 step.
// 종료 코드: 0 정상(✗ 가 있어도 0 — 건수를 출력한다), 1 사용법·실행 오류, 2 페이지 오류(pageerror), 3 --no-hangul 인데 한글 발견
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright-core')); }
catch { console.error('playwright-core 가 없다. 한 번만: cd ' + path.dirname(new URL(import.meta.url).pathname) + ' && npm install'); process.exit(1); }

const argv = process.argv.slice(2);
const opt = {};
for (let i = 0; i < argv.length; i++) {
  const k = argv[i];
  if (!k.startsWith('--')) continue;
  const v = argv[i + 1] !== undefined && !argv[i + 1].startsWith('--') ? argv[++i] : 'true';
  opt[k.slice(2)] = v;
}
if (!opt.dir) { console.error('사용법: node text_probe.mjs --dir <reel 폴더> [--step 0.1] [--from s] [--to s] [--rate-ko 6] [--rate-en 10] [--min-chars 2] [--base 0] [--groups] [--group-window 0.5] [--no-hangul] [--json out.json]'); process.exit(1); }
const dir = path.resolve(opt.dir);
const root = path.resolve(opt.root || path.dirname(dir));
const pagePath = '/' + path.relative(root, path.join(dir, 'index.html')).split(path.sep).join('/');
const num = (k, d) => (opt[k] === undefined ? d : Number(opt[k]));
const step = num('step', 0.1), rate = { ko: num('rate-ko', 6), en: num('rate-en', 10) }, minChars = num('min-chars', 2), base = num('base', 0), groupWindow = num('group-window', 0.5);
if (![step, rate.ko, rate.en].every(x => x > 0) || !(minChars >= 0) || !(base >= 0) || !(groupWindow >= 0)) { console.error('--step, --rate-ko, --rate-en 은 0 보다 큰 수, --min-chars, --base, --group-window 는 0 이상의 수여야 한다'); process.exit(1); }
const wantHangul = !!opt['no-hangul'];

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.ttf': 'font/ttf',
  '.otf': 'font/otf', '.woff': 'font/woff', '.woff2': 'font/woff2',
};

function serve(rootDir) {
  const server = http.createServer((req, res) => {
    const p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (p === '/favicon.ico') { res.writeHead(204); return res.end(); }
    const file = path.join(rootDir, p === '/' ? pagePath : p);
    if (!file.startsWith(rootDir)) { res.writeHead(403); return res.end(); }
    fs.stat(file, (err, st) => {
      if (err || !st.isFile()) { res.writeHead(404); return res.end('not found'); }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': st.size, 'Cache-Control': 'no-store' });
      fs.createReadStream(file).pipe(res);
    });
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => r(server)));
}

async function launch() {
  const args = ['--hide-scrollbars', '--font-render-hinting=none', '--disable-lcd-text',
    '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows'];
  const exe = process.env.REEL_CHROME_PATH;
  const tries = exe ? [{ executablePath: exe }] : [{ channel: process.env.REEL_CHROME_CHANNEL || 'chrome' }, { channel: 'chromium' }, {}];
  let last;
  for (const t of tries) {
    try { return await chromium.launch({ headless: true, args, ...t }); } catch (e) { last = e; }
  }
  console.error('브라우저를 띄우지 못했다. Google Chrome 을 설치하거나 REEL_CHROME_PATH 로 Chromium 실행 파일을 지정하라.\n' + last);
  process.exit(1);
}

function measure([t, hangul]) {
  window.__seek(t);
  const W = window.__meta.width, H = window.__meta.height;
  const ids = (window.__tpIds ||= { map: new WeakMap(), n: 0 });
  const opCache = new Map(), blockCache = new Map();
  const opOf = el => {
    let v = opCache.get(el);
    if (v === undefined) { v = (el.parentElement ? opOf(el.parentElement) : 1) * Number(getComputedStyle(el).opacity); opCache.set(el, v); }
    return v;
  };
  const blockOf = el => {
    let b = blockCache.get(el);
    if (!b) {
      if (el instanceof SVGElement) b = el.closest('text') || el;
      else {
        const d = getComputedStyle(el).display;
        b = (d.startsWith('inline') || d === 'contents') && el.parentElement ? blockOf(el.parentElement) : el;
      }
      blockCache.set(el, b);
    }
    return b;
  };
  const clipCache = new Map();
  const clipOf = el => {
    let c = clipCache.get(el);
    if (!c) {
      c = el === document.body ? [-Infinity, -Infinity, Infinity, Infinity] : [...clipOf(el.parentElement)];
      const s = getComputedStyle(el), cx = s.overflowX !== 'visible', cy = s.overflowY !== 'visible';
      if (cx || cy) {
        const r = el.getBoundingClientRect();
        if (cx) { c[0] = Math.max(c[0], r.left); c[2] = Math.min(c[2], r.right); }
        if (cy) { c[1] = Math.max(c[1], r.top); c[3] = Math.min(c[3], r.bottom); }
      }
      clipCache.set(el, c);
    }
    return c;
  };
  const blocks = new Map();
  const range = document.createRange();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = walker.nextNode());) {
    const p = n.parentElement;
    if (!p || !/\S/.test(n.data) || /^(SCRIPT|STYLE|NOSCRIPT)$/.test(p.tagName)) continue;
    range.selectNodeContents(n);
    const rects = [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0);
    if (!rects.length || getComputedStyle(p).visibility !== 'visible') continue;
    const op = opOf(p);
    if (op < 0.05) continue;
    const b = blockOf(p);
    let e = blocks.get(b);
    if (!e) blocks.set(b, e = { text: '', solid: '', last: null, x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity, cx0: Infinity, cy0: Infinity, cx1: -Infinity, cy1: -Infinity });
    const h = rects[0].height;
    if (e.last && (rects[0].top > e.last.bottom - h * 0.5 || rects[0].left - e.last.right > h * 0.1)) e.text += ' ';
    e.text += n.data;
    e.last = rects.at(-1);
    if (op >= 0.9) e.solid += n.data;
    const clip = clipOf(p);
    for (const r of rects) {
      e.x0 = Math.min(e.x0, r.left); e.y0 = Math.min(e.y0, r.top); e.x1 = Math.max(e.x1, r.right); e.y1 = Math.max(e.y1, r.bottom);
      const x0 = Math.max(r.left, clip[0]), y0 = Math.max(r.top, clip[1]), x1 = Math.min(r.right, clip[2]), y1 = Math.min(r.bottom, clip[3]);
      if (x1 > x0 && y1 > y0) { e.cx0 = Math.min(e.cx0, x0); e.cy0 = Math.min(e.cy0, y0); e.cx1 = Math.max(e.cx1, x1); e.cy1 = Math.max(e.cy1, y1); }
    }
  }
  const flat = s => s.replace(/\s+/g, ' ').trim(), key = s => s.replace(/\s+/g, '');
  const out = [];
  for (const [el, e] of blocks) {
    const text = flat(e.text);
    if (!text) continue;
    if (!ids.map.has(el)) ids.map.set(el, ++ids.n);
    const inW = Math.max(0, Math.min(e.cx1, W) - Math.max(e.cx0, 0)), inH = Math.max(0, Math.min(e.cy1, H) - Math.max(e.cy0, 0));
    out.push({ id: ids.map.get(el), scene: el.closest('.scene')?.id || '-', text, key: key(text), solid: key(e.solid), inside: (inW * inH) / ((e.x1 - e.x0) * (e.y1 - e.y0)) });
  }
  const ko = hangul ? [...new Set(document.body.innerText.match(/[가-힣ㄱ-ㅎㅏ-ㅣ]+/g) || [])] : null;
  return { blocks: out, ko };
}

const server = await serve(root);
const browser = await launch();
const pageErrors = [], consoleErrors = new Set();
let meta, insts = [], hangulHits = [], times = [], fatal = false;
try {
  const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 } })).newPage();
  page.on('pageerror', e => { pageErrors.push(String(e)); console.error('[pageerror]', String(e)); });
  page.on('console', m => { if (m.type() === 'error') consoleErrors.add(m.text()); });
  const url = `http://127.0.0.1:${server.address().port}${pagePath}?render=1`;
  const res = await page.goto(url, { waitUntil: 'load' });
  if (!res.ok()) throw new Error(`페이지를 열지 못했다(${res.status()}): ${url} — --dir 경로와 index.html 을 확인하라`);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });
  meta = await page.evaluate(() => window.__meta);
  await page.setViewportSize({ width: meta.width, height: meta.height });
  console.log(`페이지: ${meta.width}x${meta.height} ${meta.fps}fps ${meta.duration}s · 장면 ${meta.scenes.length}개 · 간격 ${step}s · 속도 한글 ${rate.ko}자/초, 영어 ${rate.en}자/초${base ? `, +${base}s` : ''}`);

  const from = num('from', 0), to = num('to', meta.duration);
  for (let t = from; t < to - 1e-9; t = from + times.length * step) times.push(Number(t.toFixed(3)));

  const cur = new Map();
  const related = (a, b) => a.includes(b) || b.includes(a);
  for (let i = 0; i < times.length; i++) {
    const r = await page.evaluate(measure, [times[i], wantHangul]);
    if (r.ko?.length) hangulHits.push({ i, t: times[i], words: r.ko });
    for (const b of r.blocks) {
      let x = cur.get(b.id);
      if (!x || !related(x.key, b.key)) { x = { scene: b.scene, first: times[i], key: b.key, text: b.text, rows: [] }; insts.push(x); cur.set(b.id, x); }
      if (b.key.length > x.key.length) { x.key = b.key; x.text = b.text; }
      x.rows.push([i, b.solid, b.inside]);
    }
  }
} catch (e) {
  console.error('실행 오류: ' + String(e.message).split('\n')[0]);
  fatal = true;
} finally {
  await browser.close();
  server.close();
}
if (fatal) process.exit(pageErrors.length ? 2 : 1);

const r3 = v => Number(v.toFixed(3));
const results = insts.map(x => {
  const chars = x.key.length;
  const lang = /[가-힣]/.test(x.key) ? 'ko' : 'en';
  const need = chars / rate[lang] + base;
  let run = 0, best = 0, bestAt = 0, prev = -2, full = false;
  for (const [i, solid, inside] of x.rows) {
    if (solid !== x.key || inside < 0.95) continue;
    run = i === prev + 1 ? run + 1 : 1; prev = i; full = true;
    if (run > best) { best = run; bestAt = times[i - run + 1]; }
  }
  const longest = r3(best * step);
  return { scene: x.scene, first: x.first, seen: r3(x.rows.length * step), fullFrom: full ? bestAt : null, run: longest, chars, lang, need: r3(need), ok: !full ? null : longest + 1e-6 >= need, text: x.text };
}).sort((a, b) => a.first - b.first);

const judged = results.filter(r => r.chars >= minChars && r.ok !== null);
const bad = judged.filter(r => !r.ok);
const never = results.filter(r => r.chars >= minChars && r.ok === null);
const skipped = results.filter(r => r.chars < minChars);

const groups = [], open = new Map();
for (const r of [...judged].sort((a, b) => a.fullFrom - b.fullFrom)) {
  const end = r3(r.fullFrom + r.run);
  let g = open.get(r.scene);
  const from = g ? Math.max(g.from, r.fullFrom) : r.fullFrom, to = g ? Math.min(g.to, end) : end;
  if (g && r.fullFrom - g.anchor <= groupWindow + 1e-6 && to - from > 1e-6) { g.from = from; g.to = to; }
  else { g = { scene: r.scene, anchor: r.fullFrom, from: r.fullFrom, to: end, members: [] }; groups.push(g); open.set(r.scene, g); }
  g.members.push(r);
}
const grouped = groups.filter(g => g.members.length > 1).map(g => {
  const uniq = [...new Map(g.members.map(m => [m.text, m])).values()];
  const run = r3(g.to - g.from), need = r3(uniq.reduce((n, m) => n + m.chars / rate[m.lang], 0) + base);
  return { scene: g.scene, from: g.from, run, need, chars: g.members.reduce((n, m) => n + m.chars, 0), members: g.members.length, ok: run + 1e-6 >= need, text: g.members.map(m => m.text).join(' | ') };
}).sort((a, b) => a.from - b.from);
const badGroups = grouped.filter(g => !g.ok);

const wid = s => [...s].reduce((n, c) => n + (c.codePointAt(0) > 0x2e7f ? 2 : 1), 0);
const pad = (s, n, left) => { const sp = ' '.repeat(Math.max(0, n - wid(s))); return left ? sp + s : s + sp; };
const cut = (s, n) => { if (wid(s) <= n) return s; let o = ''; for (const c of s) { if (wid(o + c) > n - 1) break; o += c; } return o + '…'; };
const line = (r, mark) => `${pad(r.first.toFixed(1), 6, 1)}  ${pad(r.scene, 6)} ${pad(r.run.toFixed(1) + 's', 6, 1)} ${pad(r.need.toFixed(1) + 's', 6, 1)} ${pad(String(r.chars), 4, 1)}  ${r.lang}  ${mark}   ${cut(r.text, 60)}`;

console.log(`\n${pad('시작', 6, 1)}  ${pad('장면', 6)} ${pad('최장', 6, 1)} ${pad('필요', 6, 1)} ${pad('글자', 4, 1)}  언어  판정  글`);
for (const r of judged) console.log(line(r, r.ok ? '✓' : '✗'));
console.log(`\n읽는 시간: 판정 ${judged.length}블록 중 ✗ ${bad.length}건`);
if (never.length) console.log(`완전히 보인 적 없는 블록 ${never.length}건(판정 제외 — 장식·반투명·화면 밖에 걸친 글일 수 있다): ` + never.slice(0, 5).map(r => `${r.first.toFixed(1)}s "${cut(r.text, 24)}"`).join(', ') + (never.length > 5 ? ' …' : ''));
if (skipped.length) console.log(`글자 수 < ${minChars} 라 건너뜀 ${skipped.length}건`);
if (bad.length) {
  console.log('가장 모자란 순:');
  for (const r of [...bad].sort((a, b) => (b.need - b.run) - (a.need - a.run)).slice(0, 5)) {
    console.log(`  -${(r.need - r.run).toFixed(1)}s  ${r.first.toFixed(1)}s ${r.scene}  ${r.run.toFixed(1)}s 보임 / ${r.need.toFixed(1)}s 필요 (${r.chars}자 ${r.lang})  "${cut(r.text, 50)}"`);
  }
}

const groupLine = g => `${pad(g.from.toFixed(1), 6, 1)}  ${pad(g.scene, 6)} ${pad(g.run.toFixed(1) + 's', 6, 1)} ${pad(g.need.toFixed(1) + 's', 6, 1)} ${pad(String(g.chars), 4, 1)}  ${pad(g.members + '개', 4)}  ${g.ok ? '✓' : '✗'}   ${cut(g.text, 60)}`;
if (opt.groups) {
  console.log(`\n함께 읽는 묶음(같은 장면에서 ${groupWindow}s 안에 완전히 보이기 시작한 블록 2개 이상, 겹친 구간 안에 다 읽혀야 한다)`);
  if (grouped.length) {
    console.log(`${pad('시작', 6, 1)}  ${pad('장면', 6)} ${pad('겹침', 6, 1)} ${pad('필요', 6, 1)} ${pad('글자', 4, 1)}  개수  판정  글`);
    for (const g of grouped) console.log(groupLine(g));
  }
  console.log(`읽는 묶음: ${grouped.length}묶음 중 ✗ ${badGroups.length}건`);
}

if (wantHangul) {
  console.log('');
  const spans = [];
  for (const h of hangulHits) {
    const l = spans.at(-1);
    if (l && h.i === l.i1 + 1) { l.i1 = h.i; l.t1 = h.t; h.words.forEach(w => l.words.add(w)); } else spans.push({ t: h.t, i1: h.i, t1: h.t, words: new Set(h.words) });
  }
  for (const s of spans.slice(0, 40)) console.log(`한글 ${s.t.toFixed(2)}${s.t1 > s.t ? '–' + s.t1.toFixed(2) : ''}s : ${[...s.words].slice(0, 6).join(' ')}`);
  if (spans.length > 40) console.log(`… 구간 ${spans.length - 40}개 더`);
  console.log(hangulHits.length ? `한글 발견: ${hangulHits.length}개 시각(${spans.length}개 구간) / 검사 ${times.length}개 시각` : `한글 없음: 보이는 DOM 글자에 한글이 없다(${times.length}개 시각 검사)`);
}

if (opt.json && opt.json !== 'true') {
  fs.mkdirSync(path.dirname(path.resolve(opt.json)), { recursive: true });
  fs.writeFileSync(opt.json, JSON.stringify({ dir, step, rate, base, minChars, groupWindow, blocks: results, groups: grouped, hangul: wantHangul ? hangulHits : undefined }, null, 1));
  console.log(`JSON → ${path.resolve(opt.json)}`);
}
if (consoleErrors.size) console.error(`콘솔 오류 ${consoleErrors.size}종(예: ${[...consoleErrors][0].slice(0, 120)})`);
if (pageErrors.length) {
  console.error(`페이지 오류 ${pageErrors.length}건 — 해당 장면의 코드를 고치고 결과를 다시 확인하라.`);
  process.exit(2);
}
if (hangulHits.length) process.exit(3);
