// Lottie player page for render.mjs (--dir <folder with this page> --root <asset project>).
// Config: window.PLAYER_CFG, overridden by the query string.
//   src       Lottie source path: .json, or .lottie (dotlottie only). Required.
//   player    dotlottie (default) | lottieweb
//   theme     theme id inside the .lottie                       (dotlottie only)
//   themeData path of a theme JSON                              (dotlottie only)
//   bg        transparent (default) | #rrggbb
//   renderer  svg (default) | canvas                            (lottieweb only)
//   lib       folder with dotlottie-web/ (the package's dist) and lottie.min.js. Default /lib/
//   fonts     folder with fonts.json [{id, family, weight, file}] and the font files. Default /fonts/
// Page contract: __ready (true | 'error' with __errors), __seek(t), __seekFrame(n), __meta.
const q = Object.assign({ lib: '/lib/', fonts: '/fonts/' }, window.PLAYER_CFG, Object.fromEntries(new URLSearchParams(location.search)));
const { player = 'dotlottie', src, bg = 'transparent', renderer = 'svg', lib, fonts: fontBase } = q;
const stage = document.getElementById('stage');
window.__ready = false;
window.__errors = [];
const fail = (m) => { window.__errors.push(String(m)); console.error('[player] ' + m); };

const nextPaint = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));

async function fetchOk(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`not found: ${url} (${res.status})`);
  return res;
}

async function loadFonts() {
  const res = await fetch(fontBase + 'fonts.json');
  if (!res.ok) return [];
  const declared = await res.json();
  const css = declared.map(f => [f.id, f.family].map(name =>
    `@font-face{font-family:'${name}';src:url('${fontBase}${f.file}') format('truetype');font-weight:${f.weight};}`).join('')).join('\n');
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  const loaded = await Promise.all(declared.map(async f => (await document.fonts.load(`${f.weight} 16px '${f.id}'`, '가A')).length > 0));
  declared.forEach((f, i) => { if (!loaded[i]) fail('font not loaded: ' + f.id); });
  return declared.filter((f, i) => loaded[i]);
}

function loadScript(url) {
  return new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = url; s.onload = res; s.onerror = () => rej(new Error('not found: ' + url));
    document.head.appendChild(s);
  });
}

async function main() {
  if (!src) throw new Error('missing src (PLAYER_CFG.src or ?src=)');
  let fonts = await loadFonts();
  const json = src.endsWith('.lottie') ? null : await (await fetchOk(src)).json();

  if (player === 'dotlottie') {
    const { DotLottie } = await import(lib + 'dotlottie-web/index.js');
    DotLottie.setWasmUrl(lib + 'dotlottie-web/dotlottie-player.wasm');
    const registered = [];
    for (const f of fonts) {
      let ok = false;
      try { ok = await DotLottie.registerFont(f.id, fontBase + f.file); } catch (e) { fail('registerFont ' + f.id + ': ' + e); continue; }
      if (ok) registered.push(f); else fail('registerFont failed: ' + f.id);
    }
    fonts = registered;
    const canvas = document.createElement('canvas');
    stage.appendChild(canvas);
    if (json) { canvas.width = json.w; canvas.height = json.h; canvas.style.width = json.w + 'px'; canvas.style.height = json.h + 'px'; }
    const dl = new DotLottie({
      canvas, autoplay: false, loop: false, useFrameInterpolation: false,
      ...(json ? { data: JSON.stringify(json) } : { src }),
      ...(bg !== 'transparent' ? { backgroundColor: bg } : {}),
      renderConfig: { devicePixelRatio: 1, autoResize: false, freezeOnOffscreen: false },
    });
    await new Promise((res, rej) => { dl.addEventListener('load', res); dl.addEventListener('loadError', e => rej(new Error(`loadError ${src} ${e.error || ''}`))); });
    dl.addEventListener('renderError', e => fail('renderError ' + (e.error || '')));
    if (!json) {
      const size = dl.animationSize();
      canvas.width = size.width; canvas.height = size.height;
      canvas.style.width = size.width + 'px'; canvas.style.height = size.height + 'px';
      dl.resize();
    }
    if (q.theme && !dl.setTheme(q.theme)) fail('setTheme failed: ' + q.theme);
    if (q.themeData && !dl.setThemeData(await (await fetchOk(q.themeData)).text())) fail('setThemeData failed: ' + q.themeData);
    const fps = json ? json.fr : dl.totalFrames / dl.duration;
    const frames = json ? Math.round(json.op - json.ip) : Math.round(dl.totalFrames);
    window.__meta = { player, src, fps, frames, duration: frames / fps, width: canvas.width, height: canvas.height };
    window.__seekFrame = async (n) => { dl.setFrame(n); await nextPaint(); };
  } else if (player === 'lottieweb') {
    if (!json) throw new Error('lottieweb needs a .json src');
    await loadScript(lib + 'lottie.min.js');
    stage.style.width = json.w + 'px'; stage.style.height = json.h + 'px';
    if (bg !== 'transparent') stage.style.background = bg;
    const anim = window.lottie.loadAnimation({
      container: stage, renderer, loop: false, autoplay: false, animationData: json,
      rendererSettings: { preserveAspectRatio: 'xMidYMid meet', clearCanvas: true, progressiveLoad: false },
    });
    await new Promise((res) => { if (anim.isLoaded) res(); else anim.addEventListener('DOMLoaded', res); });
    const frames = Math.round(json.op - json.ip);
    window.__meta = { player, renderer, src, fps: json.fr, frames, duration: frames / json.fr, width: json.w, height: json.h };
    window.__seekFrame = async (n) => { anim.goToAndStop(n, true); await nextPaint(); };
  } else {
    throw new Error('unknown player ' + player);
  }
  window.__meta.scenes = [{ id: 'lottie', start: 0, end: window.__meta.duration }];
  window.__meta.fonts = fonts.map(f => f.id);
  window.__seek = (t) => window.__seekFrame(t * window.__meta.fps);
  await window.__seekFrame(0);
  if (window.__errors.length) throw new Error(window.__errors.join('\n'));
  window.__ready = true;
}

main().catch(e => { fail(e && e.message || e); window.__ready = 'error'; });
