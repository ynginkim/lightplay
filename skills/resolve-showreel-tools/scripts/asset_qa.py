#!/usr/bin/env python3
"""에셋 프레임 폴더 검수. 프레임은 render.mjs --frames 가 쓴 f00000.png … 이다. 시트는 반드시 Read 로 직접 열어 본다.

사용법
  asset_qa.py players A B [--sheet out.png]      두 플레이어(dotlottie / lottie-web) 렌더 차이
  asset_qa.py routes  A B [--grid 8] [--sheet out.png]   두 경로(Lottie / 엔진) 차이와 영역별 채도·밝기 차이(A-B)
  asset_qa.py loop    DIR                        마지막→처음 이음새와 프레임 간 중앙 변화의 비
  asset_qa.py ink     DIR [--lottie X]           빈 프레임, 빈 프레임만 나오는 깨진 Lottie
  asset_qa.py motion  DIR [--first N --last M] [--fps 60]   멈춘 구간(프레임 번호로 잰다)
  asset_qa.py markers --lottie X.json|X.lottie DIR [--loop idle]   마커 경계 포즈 차이
  asset_qa.py themes  light=DIR dark=DIR … [--out sheet.png]   테마별 행 시트와 테마 간 차이(이름=폴더 두 개 이상)
  asset_qa.py sheet   DIR --out sheet.png [--count 12 --cols 6 --width 360]      시트 경로와 프레임 번호를 JSON 으로 출력
  asset_qa.py report  --dir DIR [--lottie X] [--lottie-web DIR] [--engine DIR] [--theme name=DIR …] [--loop] [--common] [--fps 60] [--out qa/report.txt] [--json qa/report.json] [--sheet-dir qa]

판정
  화소 수치는 회색 128 위에 합성한 채널 최대 절대차(0-255)다. 판정은 그림이 있는 영역(알파가 있는 화소, 불투명 캡처는 배경색과 다른 화소)에서
  가장 나쁜 프레임으로 정한다. JSON 의 mean_abs_diff 는 스파이크 harness/measure.py 와 같은 전체 화면 평균이라 비교할 수 있다.
  loop 의 비는 이음새 / max(중앙 변화, 0.05) 다(measure.py 는 하한이 없다).
  report 는 --theme 시트를 --sheet-dir 에, 없으면 --out/--json 이 있는 폴더에 쓴다(둘 다 없으면 오류). 줄에 시트 경로를 적는다.
  경계값(LIMITS): 플레이어 비교는 그림 영역 최악 프레임의 32 초과 화소 5% 초과가 ✗, 1.5% 또는 평균 5.0 초과가 △. 경로 비교는 20% 초과가 ✗,
  평균 3.0 초과나 가장자리 채도 차이 0.01 초과가 △. 두 폴더의 배경색(불투명 캡처)이 24 넘게 다르면 ✗. 루프·마커 이음새 비는 1.5 초과가 △(마커는 3.0 초과 ✗, 루프는 ✗).
  report 의 루프 줄은 --loop 이거나 dotLottie manifest 가 loop 이면 건다. 아니면 "-" 로 두고, 마커 구간의 루프 이음새는 markers 줄이 본다.
  두 폴더의 프레임 번호가 다르면 ✗ 다. 듬성하게 캡처한 쪽(예: lottie-web 120프레임)과 비교하려면 players·routes·report 에 --common 을 붙인다. 줄에 비교한 개수를 적는다.
종료 코드
  0 정상, 1 ✗ 판정이 있다, 2 도구 오류(폴더 없음, 읽을 수 없는 프레임, 잘못된 JSON, 크기가 다른 프레임). ✗ 이든 △ 이든 고칠 것을 함께 출력한다.
  players·routes·loop·ink·motion·markers·themes 는 한 줄 판정과 JSON 상세를 출력한다.
"""
import argparse
import json
import os
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("numpy 와 Pillow 가 필요하다: python3 -m pip install numpy pillow")

OK, WARN, FAIL, SKIP = "ok", "warn", "fail", "skip"
MARK = {OK: "✓", WARN: "△", FAIL: "✗", SKIP: "-"}
STATIC_STEP = 0.05
ALPHA_SHARE = 0.005
GRID_SAMPLES = 24
LIMITS = {
    "players_fail_pct32": 5.0, "players_warn_pct32": 1.5, "players_warn_mean": 5.0,
    "routes_warn_mean": 3.0, "routes_warn_gap": 0.01,
    "loop_ok": 1.5, "loop_warn": 3.0,
    "ink_min": 0.0005,
    "motion_fail_static": 0.95,
    "marker_ok": 1.0, "marker_warn": 3.0,
    "themes_same_px": 4, "bg_diff": 24.0, "routes_fail_pct32": 20.0,
}


class ToolError(Exception):
    pass


@dataclass
class Row:
    check: str
    status: str
    line: str
    fix: str = ""

    def __post_init__(self):
        if self.status in (WARN, FAIL) and not self.fix:
            self.fix = "위 줄의 원인을 확인한다"


def frame_set(d):
    p = Path(d)
    if not p.is_dir():
        raise ToolError(f"폴더가 없다: {d}")
    fs = sorted(p.glob("f*.png")) or sorted(p.glob("f*.jpeg"))
    out = {int(f.stem[1:]): f for f in fs if f.stem[1:].isdigit()}
    if not out:
        raise ToolError(f"프레임이 없다: {d}")
    first = None
    for i in sorted(out):
        try:
            with Image.open(out[i]) as im:
                size = im.size
        except OSError as e:
            raise ToolError(f"프레임을 읽을 수 없다: {out[i]} ({e})")
        first = first or (i, size)
        if size != first[1]:
            raise ToolError(f"프레임 크기가 다르다: f{first[0]} {first[1][0]}x{first[1][1]}, f{i} {size[0]}x{size[1]} ({d})")
    return out


def size_of(F):
    with Image.open(next(iter(F.values()))) as im:
        return im.size


def rgba(path):
    try:
        with Image.open(path) as im:
            return np.asarray(im.convert("RGBA"))
    except OSError as e:
        raise ToolError(f"프레임을 읽을 수 없다: {path} ({e})")


def composite(a, grey=128):
    alpha = a[..., 3:4].astype(np.float32) / 255.0
    return a[..., :3].astype(np.float32) * alpha + grey * (1 - alpha)


def has_alpha(a):
    return float((a[..., 3] < 255).mean()) >= ALPHA_SHARE


def background(a):
    return None if has_alpha(a) else np.median(a[::16, ::16, :3].reshape(-1, 3), axis=0)


def ink_mask(a):
    if has_alpha(a):
        return a[..., 3] > 16
    return np.abs(a[..., :3].astype(np.int16) - background(a)).max(axis=2) > 24


def saturation(x):
    mx, mn = x.max(axis=2), x.min(axis=2)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)


def checker(w, h, s=16):
    y, x = np.mgrid[0:h, 0:w]
    base = np.where((((x // s) + (y // s)) % 2)[..., None] == 1, 205, 245).astype(np.uint8)
    return Image.fromarray(np.repeat(base, 3, axis=2), "RGB")


def thumb(f, width):
    with Image.open(f) as src:
        im = src.convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    bg = checker(*im.size).convert("RGBA")
    bg.alpha_composite(im)
    return bg.convert("RGB")


def stack(imgs, bg=(30, 30, 30)):
    sheet = Image.new("RGB", (max(t.width for t in imgs), sum(t.height for t in imgs)), bg)
    y = 0
    for t in imgs:
        sheet.paste(t, (0, y))
        y += t.height
    return sheet


def save_png(img, path):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
    except (OSError, ValueError) as e:
        raise ToolError(f"파일을 쓸 수 없다: {path} ({e.__class__.__name__}: {e})")


def write_text(path, text):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
    except OSError as e:
        raise ToolError(f"파일을 쓸 수 없다: {path} ({e.__class__.__name__}: {e})")


def ranges(nums):
    nums, out = sorted(nums), []
    for n in nums:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    text = [f"f{a}" if a == b else f"f{a}-f{b}" for a, b in out]
    return ",".join(text[:8]) + (f" 외 {len(text) - 8}구간" if len(text) > 8 else "")


def pmap(fn, items, parallel):
    if not parallel:
        return [fn(x) for x in items]
    with ProcessPoolExecutor() as ex:
        return list(ex.map(fn, items, chunksize=max(1, len(items) // ((os.cpu_count() or 4) * 4))))


def is_big(F):
    w, h = size_of(F)
    return w * h > 500_000 and len(F) >= 64


def cell_means(a, n):
    h, w = a.shape
    return [[float(a[r * h // n:(r + 1) * h // n, c * w // n:(c + 1) * w // n].mean()) for c in range(n)] for r in range(n)]


def diff_one(job):
    pa, pb, i, grid = job
    xa, xb = rgba(pa), rgba(pb)
    ma, mb = ink_mask(xa), ink_mask(xb)
    ca, cb = composite(xa), composite(xb)
    d = np.abs(ca - cb).max(axis=2)
    u = ma | mb
    bga, bgb = background(xa), background(xb)
    r = {"frame": i, "bg_diff": float(np.abs(bga - bgb).max()) if bga is not None and bgb is not None else 0.0, "mean": float(d.mean()), "pct_over_32": float((d > 32).mean() * 100),
         "cmean": float(d[u].mean()) if u.any() else 0.0, "cpct": float((d[u] > 32).mean() * 100) if u.any() else 0.0,
         "changed": int(((d > 16) & u).sum()), "ink_a": float(ma.mean()), "ink_b": float(mb.mean()),
         "alpha_a": has_alpha(xa), "alpha_b": has_alpha(xb)}
    if grid:
        r["sat"] = cell_means(saturation(ca) - saturation(cb), grid)
        r["level"] = cell_means(ca.mean(axis=2) - cb.mean(axis=2), grid)
    return r


def frame_problems(FA, FB, na="A", nb="B"):
    if size_of(FA) != size_of(FB):
        raise ToolError(f"{na} 와 {nb} 의 프레임 크기가 다르다: {size_of(FA)} vs {size_of(FB)}")
    out = []
    if set(FB) - set(FA):
        out.append(f"{na} 에 없는 프레임 {ranges(set(FB) - set(FA))}")
    if set(FA) - set(FB):
        out.append(f"{nb} 에 없는 프레임 {ranges(set(FA) - set(FB))}")
    return out


def compare(A, B, grid=0, na="A", nb="B", common_only=False):
    FA, FB = frame_set(A), frame_set(B)
    problems = frame_problems(FA, FB, na, nb)
    if common_only:
        problems = []
    common = sorted(set(FA) & set(FB))
    rows = []
    if common:
        sampled = set(common[:: max(1, len(common) // GRID_SAMPLES)]) if grid else set()
        rows = pmap(diff_one, [(FA[i], FB[i], i, grid if i in sampled else 0) for i in common], is_big(FA))
    return FA, FB, rows, problems


def stat(rows, key):
    v = np.array([r[key] for r in rows])
    return {"avg": round(float(v.mean()), 3), "median": round(float(np.median(v)), 3), "max": round(float(v.max()), 3), "worst_frame": rows[int(v.argmax())]["frame"]}


def diff_summary(rows, top=6):
    s = {"frames": len(rows), "mean_abs_diff": stat(rows, "mean"), "pct_pixels_over_32": stat(rows, "pct_over_32"),
         "content_mean_abs_diff": stat(rows, "cmean"), "content_pct_over_32": stat(rows, "cpct"),
         "worst": [{"frame": r["frame"], "mean": round(r["mean"], 3), "content_mean": round(r["cmean"], 3), "content_pct_over_32": round(r["cpct"], 3)}
                   for r in sorted(rows, key=lambda r: -r["cpct"])[:top]]}
    for k in ("mean_abs_diff", "pct_pixels_over_32"):
        s[k] = {a: b for a, b in s[k].items() if a != "worst_frame"}
    return s


def diff_sheet(FA, FB, rows, path, top=6):
    w, tiles = 480, []
    for r in sorted(rows, key=lambda r: -r["cpct"])[:top]:
        i = r["frame"]
        ta, tb = thumb(FA[i], w), thumb(FB[i], w)
        d = np.clip(np.abs(composite(rgba(FA[i])) - composite(rgba(FB[i]))).max(axis=2) * 4, 0, 255).astype(np.uint8)
        hm = Image.fromarray(d, "L").resize(ta.size).convert("RGB")
        row = Image.new("RGB", (w * 3 + 20, ta.height + 24), (30, 30, 30))
        row.paste(ta, (0, 24)); row.paste(tb, (w + 10, 24)); row.paste(hm, (2 * w + 20, 24))
        ImageDraw.Draw(row).text((6, 5), f"frame {i}  content mean {r['cmean']:.2f}  content >32: {r['cpct']:.2f}%   [A | B | diff x4]", fill=(240, 240, 240))
        tiles.append(row)
    save_png(stack(tiles), path)


def pair_flags(rows):
    blank = [r["frame"] for r in rows if (r["ink_a"] < LIMITS["ink_min"]) != (r["ink_b"] < LIMITS["ink_min"])]
    alpha_diff = any(r["alpha_a"] != r["alpha_b"] for r in rows)
    bg_off = [r["frame"] for r in rows if r["bg_diff"] > LIMITS["bg_diff"]]
    return blank, alpha_diff, bg_off


def finite(*vals):
    return all(np.isfinite(v) for v in vals)


def check_players(A, B, sheet=None, common_only=False):
    FA, FB, rows, problems = compare(A, B, common_only=common_only)
    if problems or not rows:
        return Row("플레이어 차이", FAIL, "프레임 집합이 다르다: " + "; ".join(problems), "두 플레이어를 같은 프레임 범위로 다시 캡처한다"), {"problems": problems}
    s = diff_summary(rows)
    blank, alpha_diff, bg_off = pair_flags(rows)
    note = f" [공통 {len(rows)}/{max(len(FA), len(FB))}프레임만 비교(--common)]" if common_only and len(rows) < max(len(FA), len(FB)) else ""
    wp, wm = s["content_pct_over_32"], s["content_mean_abs_diff"]
    s["blank_one_side"], s["background_differs"] = blank, bg_off
    line = f"그림 영역 최악 f{wp['worst_frame']} 32 초과 {wp['max']}%·평균 {wm['max']}, 전체 평균 {s['mean_abs_diff']['avg']} /255 ({s['frames']}프레임)" + note
    if not finite(wp["max"], wm["max"]):
        st, fix = FAIL, "수치가 유한하지 않다. 프레임을 다시 캡처한다"
    elif blank:
        st, fix, line = FAIL, "한쪽 플레이어가 빈 화면을 그렸다. 그 플레이어가 지원하지 않는 기능이 있는지 본다", f"한쪽만 빈 프레임 {ranges(blank)}; " + line
    elif bg_off:
        st, fix, line = FAIL, "두 플레이어의 배경색이 다르다. 배경 설정(투명·불투명, 색)을 같게 한다", f"배경색이 다른 프레임 {ranges(bg_off)}; " + line
    elif wp["max"] > LIMITS["players_fail_pct32"]:
        st, fix = FAIL, "두 플레이어가 다르게 그린다. 글자별 애니메이터·텍스트 레이어·지원 안 되는 기능을 외곽선과 기본 도형으로 바꾼다"
    elif wp["max"] > LIMITS["players_warn_pct32"] or wm["max"] > LIMITS["players_warn_mean"]:
        st, fix = WARN, "차이가 큰 프레임을 시트로 열어 번짐·가장자리·안티앨리어싱 차이인지 확인한다"
    elif alpha_diff:
        st, fix = WARN, "한쪽만 알파가 있다. 같은 배경 설정으로 다시 캡처한다"
    else:
        st, fix = OK, ""
    if alpha_diff and st != OK:
        line += " (한쪽만 알파가 있다, 회색 128 위에서 비교했다)"
    if sheet:
        diff_sheet(FA, FB, rows, sheet)
        s["sheet"] = sheet
    return Row("플레이어 차이", st, line, fix), s


def region_label(r, c, n):
    return "가운데" if abs(r - (n - 1) / 2) <= 0.5 and abs(c - (n - 1) / 2) <= 0.5 else ("가장자리" if r in (0, n - 1) or c in (0, n - 1) else "중간")


def check_routes(A, B, grid=8, sheet=None, common_only=False):
    if grid < 3:
        raise ToolError("--grid 는 3 이상이어야 한다")
    FA, FB, rows, problems = compare(A, B, grid, common_only=common_only)
    w, h = size_of(FA)
    if grid > min(w, h):
        raise ToolError(f"--grid {grid} 가 프레임 {w}x{h} 보다 크다")
    if problems or not rows:
        return Row("경로 차이", FAIL, "프레임 집합이 다르다: " + "; ".join(problems), "두 경로를 같은 프레임 범위로 다시 렌더한다"), {"problems": problems}
    s = diff_summary(rows)
    blank, alpha_diff, bg_off = pair_flags(rows)
    note = f" [공통 {len(rows)}/{max(len(FA), len(FB))}프레임만 비교(--common)]" if common_only and len(rows) < max(len(FA), len(FB)) else ""
    out = {}
    for key in ("sat", "level"):
        mean = np.mean([r[key] for r in rows if key in r], axis=0)
        zones = {"가장자리": [], "중간": [], "가운데": []}
        for r in range(grid):
            for c in range(grid):
                zones[region_label(r, c, grid)].append(mean[r][c])
        out[key] = {"grid": [[round(float(v), 4) for v in row] for row in mean], **{z: round(float(np.mean(v)), 4) for z, v in zones.items() if v}}
    s.update(grid=grid, blank_one_side=blank, background_differs=bg_off, saturation_A_minus_B=out["sat"], level_A_minus_B=out["level"])
    m, gap = s["mean_abs_diff"]["avg"], out["sat"]["가장자리"]
    wp = s["content_pct_over_32"]
    line = (f"평균 {m} /255, 그림 영역 최악 f{wp['worst_frame']} 32 초과 {wp['max']}%, 채도 차이 가장자리 {gap:+.4f} 가운데 {out['sat']['가운데']:+.4f}, "
            f"밝기 차이 가장자리 {out['level']['가장자리']:+.3f} 가운데 {out['level']['가운데']:+.3f}") + note
    if not finite(m, gap, out["sat"]["가운데"]):
        st, fix = FAIL, "수치가 유한하지 않다. 프레임을 다시 렌더한다"
    elif blank:
        st, fix, line = FAIL, "한 경로가 빈 화면을 낸다. 그 출력기의 오류와 빠진 노드를 본다", f"한쪽만 빈 프레임 {ranges(blank)}; " + line
    elif bg_off:
        st, fix, line = FAIL, "두 경로의 배경색이 다르다. 배경 설정과 색 관리를 같게 한다", f"배경색이 다른 프레임 {ranges(bg_off)}; " + line
    elif wp["max"] > LIMITS["routes_fail_pct32"]:
        st, fix = FAIL, "한 프레임이라도 두 경로의 그림이 크게 다르다. 그 프레임을 시트로 열어 어느 출력기가 틀렸는지 본다"
    elif abs(gap) > LIMITS["routes_warn_gap"]:
        st, fix = WARN, "한 경로의 가장자리 채도가 다르다. 엔진 쪽 색 관리(sRGB, 흐린 배경의 알파 합성)와 인코딩 색 태그를 확인한다"
    elif m > LIMITS["routes_warn_mean"]:
        st, fix = WARN, "engineOnly 노드 때문인지 확인한다"
    elif alpha_diff:
        st, fix = WARN, "한쪽만 알파가 있다. 같은 배경 설정으로 다시 렌더한다"
    else:
        st, fix = OK, ""
    if alpha_diff and st != OK:
        line += " (한쪽만 알파가 있다, 회색 128 위에서 비교했다)"
    if sheet:
        diff_sheet(FA, FB, rows, sheet)
        s["sheet"] = sheet
    return Row("경로 차이", st, line, fix), s


def scan_chunk(items):
    ink, steps, prev = {}, [], None
    for i, f in items:
        a = rgba(f)
        m = ink_mask(a)
        ink[i] = float(m.mean())
        cur = composite(a)
        if prev is not None:
            d = np.abs(cur - prev[1]).max(axis=2)
            u = m | prev[2]
            steps.append((prev[0], i, float(d.mean()), float(d[u].mean()) if u.any() else 0.0))
        prev = (i, cur, m)
    return ink, steps


def scan(F):
    idx = sorted(F)
    n = max(1, min(len(idx) - 1, (os.cpu_count() or 4) * 2 if is_big(F) else 1))
    bounds = [round(k * (len(idx) - 1) / n) for k in range(n + 1)]
    jobs = [[(i, F[i]) for i in idx[bounds[k]:bounds[k + 1] + 1]] for k in range(n)]
    ink, steps = {}, []
    for k_ink, k_steps in pmap(scan_chunk, jobs, n > 1):
        ink.update(k_ink)
        steps += k_steps
    return {"idx": idx, "ink": ink, "steps": steps, "frames": F}


def check_loop(d, sc=None):
    sc = sc or scan(frame_set(d))
    idx, steps, F = sc["idx"], sc["steps"], sc["frames"]
    if len(idx) < 3:
        return Row("루프 이음새", FAIL, "프레임이 3개 미만이다", "전체 프레임을 캡처한다"), {}
    if idx != list(range(idx[0], idx[-1] + 1)):
        return (Row("루프 이음새", FAIL, f"빠진 프레임이 있다({ranges(set(range(idx[0], idx[-1] + 1)) - set(idx))})",
                    "render.mjs 를 --every 없이 다시 실행해 모든 프레임을 캡처한다"), {})
    a, b = rgba(F[idx[0]]), rgba(F[idx[-1]])
    d = np.abs(composite(a) - composite(b)).max(axis=2)
    u = ink_mask(a) | ink_mask(b)
    seam, cseam = float(d.mean()), float(d[u].mean()) if u.any() else 0.0
    full, cont = [s[2] for s in steps], [s[3] for s in steps]
    med, cmed = max(float(np.median(full)), STATIC_STEP), max(float(np.median(cont)), STATIC_STEP)
    ratio, cratio = seam / med, cseam / cmed
    s = {"frames": len(idx), "seam_diff": round(seam, 3), "median_step_diff": round(float(np.median(full)), 3), "max_step_diff": round(max(full), 3),
         "ratio": round(ratio, 2), "content_seam_diff": round(cseam, 3), "content_median_step_diff": round(float(np.median(cont)), 3),
         "content_ratio": round(cratio, 2), "seamless": cratio <= LIMITS["loop_ok"], "static_steps": sum(1 for v in full if v < STATIC_STEP)}
    if not finite(ratio, cratio):
        return Row("루프 이음새", FAIL, "수치가 유한하지 않다", "프레임을 다시 캡처한다"), s
    st = OK if cratio <= LIMITS["loop_ok"] else FAIL
    fix = "" if st == OK else "마지막 프레임이 처음 프레임으로 이어지지 않는다. 끝 포즈를 첫 포즈에 맞추고 루프 길이를 주기의 정수배로 한다"
    return Row("루프 이음새", st, f"이음새 {s['seam_diff']} / 중앙 변화 {s['median_step_diff']} = 비 {s['ratio']} (그림 영역 {s['content_ratio']})", fix), s


def load_lottie(path):
    p = Path(path)
    try:
        if p.suffix == ".lottie":
            with zipfile.ZipFile(p) as z:
                name = next(n for n in z.namelist() if n.startswith(("a/", "animations/")) and n.endswith(".json"))
                data = json.loads(z.read(name))
                manifest = json.loads(z.read("manifest.json")) if "manifest.json" in z.namelist() else {}
        else:
            data, manifest = json.loads(p.read_text()), {}
    except (OSError, ValueError, StopIteration, zipfile.BadZipFile) as e:
        raise ToolError(f"Lottie 를 읽을 수 없다: {path} ({e.__class__.__name__}: {e})")
    if not isinstance(data, dict):
        raise ToolError(f"Lottie 형식 오류: 최상위가 객체가 아니다 ({path})")
    for key in ("layers", "markers"):
        v = data.get(key, [])
        if not isinstance(v, list) or not all(isinstance(x, dict) for x in v):
            raise ToolError(f"Lottie 형식 오류: {key} 가 객체 배열이 아니다 ({path})")
    for key in ("fr", "ip", "op"):
        v = data.get(key, 0)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v):
            raise ToolError(f"Lottie 형식 오류: {key} 가 숫자가 아니다 ({path})")
    anims = manifest.get("animations") if isinstance(manifest, dict) else None
    loop = bool(anims and isinstance(anims, list) and isinstance(anims[0], dict) and anims[0].get("loop"))
    return data, loop


def lottie_issues(data):
    issues = []
    layers = data.get("layers") or []
    if not layers:
        issues.append("layers 가 비어 있다")
    if data.get("op", 0) <= data.get("ip", 0):
        issues.append("op <= ip 라 재생할 프레임이 없다")
    visible = [ly for ly in layers if not ly.get("hd")]
    if layers and not visible:
        issues.append("모든 레이어가 숨김(hd)이다")
    for ly in visible:
        if ly.get("ty") == 4 and not ly.get("shapes"):
            issues.append(f"셰이프 레이어 '{ly.get('nm', '?')}' 에 shapes 가 없다")
        if ly.get("op", 1) <= ly.get("ip", 0):
            issues.append(f"레이어 '{ly.get('nm', '?')}' 의 op <= ip 라 한 프레임도 보이지 않는다")
        if "ks" not in ly:
            issues.append(f"레이어 '{ly.get('nm', '?')}' 에 ks(transform)가 없다")
    return issues


def check_ink(d, lottie=None, sc=None, name="잉크"):
    sc = sc or scan(frame_set(d))
    idx = sc["idx"]
    ink = [sc["ink"][i] for i in idx]
    blank = [i for i, v in zip(idx, ink) if v < LIMITS["ink_min"]]
    lead = trail = 0
    while lead < len(idx) and idx[lead] in blank:
        lead += 1
    while trail < len(idx) - lead and idx[len(idx) - 1 - trail] in blank:
        trail += 1
    edge = set(idx[:lead]) | set(idx[len(idx) - trail:] if trail else [])
    bad = [i for i in blank if i not in edge]
    s = {"frames": len(idx), "blank_frames": blank, "blank_interior": bad, "min_ink": round(min(ink), 5), "max_ink": round(max(ink), 5)}
    if lottie:
        s["lottie_issues"] = lottie_issues(load_lottie(lottie)[0])
    if len(blank) == len(idx):
        why = "; ".join(s.get("lottie_issues", [])) or "플레이어가 오류 없이 빈 화면을 그렸다"
        return Row(name, FAIL, f"전 프레임이 비었다 ({why})", "스키마가 맞아도 구조가 틀리면 플레이어는 빈 화면을 내고 0으로 끝난다. 레이어·셰이프·op/ip 를 점검한다"), s
    if bad:
        return Row(name, FAIL, f"빈 프레임 {len(bad)}개: " + ranges(bad), "빈 프레임의 원인(키프레임 투명도 0, 매트, 레이어 op 범위)을 찾는다"), s
    if blank:
        return Row(name, WARN, f"처음·끝에 빈 프레임 {len(blank)}개 (의도한 등장·퇴장이면 무시)", "의도한 등장·퇴장이 아니면 빈 프레임의 원인을 찾는다"), s
    return Row(name, OK, f"빈 프레임 없음 (잉크 {s['min_ink'] * 100:.2f}~{s['max_ink'] * 100:.2f}%)", ""), s


def check_motion(d, first=None, last=None, fps=60.0, sc=None):
    sc = sc or scan(frame_set(d))
    steps = [s for s in sc["steps"] if (first is None or s[0] >= first) and (last is None or s[1] <= last)]
    if not steps:
        return Row("움직임", FAIL, "비교할 프레임이 2개 미만이다", "구간을 넓히거나 프레임을 더 캡처한다"), {}
    run = best = 0
    static_frames = 0
    for a, b, _, cs in steps:
        if cs < STATIC_STEP:
            run += b - a
            static_frames += b - a
            best = max(best, run)
        else:
            run = 0
    span = steps[-1][1] - steps[0][0]
    frac = static_frames / span
    cont = [s[3] for s in steps]
    s = {"frames": len(steps) + 1, "span_frames": span, "static_frames": static_frames, "static_fraction": round(frac, 3), "longest_static_run": best,
         "mean_step_diff": round(float(np.mean(cont)), 3), "max_step_diff": round(max(cont), 3)}
    if frac >= LIMITS["motion_fail_static"]:
        return Row("움직임", FAIL, f"멈춘 화면 {frac * 100:.0f}% ({static_frames}/{span}프레임)", "구간이 사실상 정지 상태다. idle 에 호흡·미세한 움직임을 넣거나 한 프레임으로 줄인다"), s
    if best > fps:
        return Row("움직임", WARN, f"{best}프레임({best / fps:.1f}초) 연속으로 멈춘다", "의도한 정지가 아니면 멈춤 구간에 움직임을 넣는다"), s
    return Row("움직임", OK, f"멈춘 프레임 {static_frames}/{span}, 최장 {best}프레임, 평균 변화 {s['mean_step_diff']}", ""), s


def pose_diff(F, a, b):
    xa, xb = rgba(F[a]), rgba(F[b])
    d = np.abs(composite(xa) - composite(xb)).max(axis=2)
    u = ink_mask(xa) | ink_mask(xb)
    return round(float(d[u].mean()) if u.any() else 0.0, 3)


def segment_step(F, a, b):
    nums = [i for i in range(a, b + 1) if i in F]
    if len(nums) < 2 or nums != list(range(nums[0], nums[-1] + 1)):
        return None
    return float(np.median([pose_diff(F, nums[k], nums[k + 1]) for k in range(len(nums) - 1)]))


def check_markers(lottie, d, loop_names=("idle", "loop")):
    data, _ = load_lottie(lottie)
    ip = data.get("ip", 0)
    try:
        marks = sorted(({"name": str(m["cm"]), "from": int(m["tm"] - ip), "to": int(m["tm"] + m["dr"] - ip)} for m in data.get("markers", [])), key=lambda m: m["from"])
    except (KeyError, TypeError, ValueError) as e:
        raise ToolError(f"Lottie 마커 형식 오류: cm, tm, dr 이 필요하다 ({e.__class__.__name__}: {e})")
    if not marks:
        return Row("마커 경계", SKIP, "마커가 없다", ""), {"markers": []}
    F = frame_set(d)
    pairs, missing = [], set()
    for k, m in enumerate(marks):
        wanted = []
        if m["from"] > 0:
            wanted.append((f"{m['name']} 진입", m["from"] - 1, m["from"], "entry"))
        if m["name"] in loop_names:
            wanted.append((f"{m['name']} 루프", m["to"] - 1, m["from"], "seam"))
            if m["to"] in F and m["from"] in F:
                wanted.append((f"{m['name']} 닫힘", m["from"], m["to"], "closing"))
        for name, a, b, kind in wanted:
            gone = {x for x in (a, b) if x not in F}
            if gone:
                missing |= gone
                continue
            pair = {"pair": name, "a": a, "b": b, "kind": kind, "diff": pose_diff(F, a, b)}
            if kind == "seam":
                step = segment_step(F, m["from"], m["to"] - 1)
                if step is not None:
                    pair["median_step"], pair["ratio"] = round(step, 3), round(pair["diff"] / max(step, STATIC_STEP), 2)
            pairs.append(pair)
    s = {"markers": marks, "pairs": pairs, "missing_frames": sorted(missing)}
    state = OK
    for p in pairs:
        if p["kind"] == "closing":
            continue
        if "ratio" in p:
            level = OK if p["ratio"] <= LIMITS["loop_ok"] else WARN if p["ratio"] <= LIMITS["loop_warn"] else FAIL
        else:
            level = OK if p["diff"] <= LIMITS["marker_ok"] else WARN if p["diff"] <= LIMITS["marker_warn"] else FAIL
        state = max(state, level, key=(OK, WARN, FAIL).index)
    line = f"마커 {len(marks)}개, " + ", ".join(f"{p['pair']} f{p['a']}↔f{p['b']} {p['diff']}" + (f"(비 {p['ratio']})" if "ratio" in p else "") for p in pairs)
    if state != OK:
        return Row("마커 경계", state, line, "경계 포즈가 튄다. 마커 경계의 끝 포즈와 시작 포즈를 맞춘다(루프 구간은 끝 직전 프레임이 시작 프레임으로 이어져야 한다)"), s
    if missing:
        return Row("마커 경계", WARN, f"검사하지 못한 경계 프레임 {ranges(missing)}; " + line, "마커 경계 프레임까지 캡처한다(render.mjs 를 --every 없이 실행)"), s
    return Row("마커 경계", OK, line, ""), s


def parse_themes(args):
    out = []
    for t in args:
        if "=" not in t:
            raise ToolError(f"테마는 이름=폴더 로 적는다: {t}")
        out.append(tuple(t.split("=", 1)))
    if len(out) < 2:
        raise ToolError("테마는 두 개 이상 필요하다(이름=폴더)")
    return out


def check_themes(themes, out=None, count=6, width=240):
    dirs = {n: frame_set(d) for n, d in themes}
    names = [n for n, _ in themes]
    base = dirs[names[0]]
    for n in names[1:]:
        if size_of(dirs[n]) != size_of(base):
            raise ToolError(f"테마 {names[0]} 와 {n} 의 프레임 크기가 다르다: {size_of(base)} vs {size_of(dirs[n])}")
    uneven = [f"{n} 에 없는 프레임 {ranges(set(base) ^ set(dirs[n]))}" for n in names[1:] if set(dirs[n]) != set(base)]
    if uneven:
        return Row("테마", FAIL, "프레임 집합이 다르다: " + "; ".join(uneven), "모든 테마를 같은 프레임 범위로 다시 캡처한다"), {"problems": uneven}
    common = sorted(base)
    pick = sorted({common[round(k * (len(common) - 1) / max(1, min(count, len(common)) - 1))] for k in range(min(count, len(common)))})
    pairs, same = [], []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            rows = pmap(diff_one, [(dirs[names[a]][i], dirs[names[b]][i], i, 0) for i in common], is_big(base))
            changed = max(r["changed"] for r in rows)
            pairs.append({"a": names[a], "b": names[b], "max_changed_pixels": changed, "frames_compared": len(common), "content_mean_diff": round(float(np.mean([r["cmean"] for r in rows])), 3)})
            if changed < LIMITS["themes_same_px"]:
                same.append((names[a], names[b]))
    s = {"themes": names, "frames": pick, "pairs": pairs}
    if out:
        tiles = []
        for n in names:
            ts = [thumb(dirs[n][i], width) for i in pick]
            row = Image.new("RGB", (len(ts) * (width + 6) + 90, ts[0].height + 4), (30, 30, 30))
            ImageDraw.Draw(row).text((6, 6), n, fill=(240, 240, 240))
            for k, t in enumerate(ts):
                row.paste(t, (90 + k * (width + 6), 2))
            tiles.append(row)
        save_png(stack(tiles), out)
        s["sheet"] = out
    if same:
        return Row("테마", FAIL, "같게 나온 테마: " + ", ".join(f"{a}={b}" for a, b in same), "테마가 적용되지 않았다. slots 이름과 테마 규칙(애니메이션 색은 키프레임)을 점검한다"), s
    return Row("테마", OK, f"{len(names)}개 테마, 쌍별 바뀐 화소(최대) " + ", ".join(f"{p['a']}/{p['b']} {p['max_changed_pixels']}" for p in pairs), ""), s


def make_sheet(d, out, count=12, every=None, cols=6, width=360):
    F = frame_set(d)
    idx = sorted(F)
    pick = idx[::every] if every else [idx[round(k * (len(idx) - 1) / max(1, min(count, len(idx)) - 1))] for k in range(min(count, len(idx)))]
    tiles = [thumb(F[i], width) for i in pick]
    cols = min(cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    tw, th = tiles[0].size
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 26) + 8), (30, 30, 30))
    dr = ImageDraw.Draw(sheet)
    for k, (i, t) in enumerate(zip(pick, tiles)):
        x, y = 8 + (k % cols) * (tw + 8), 8 + (k // cols) * (th + 26)
        sheet.paste(t, (x, y + 18))
        dr.text((x, y + 2), f"f{i}", fill=(230, 230, 230))
    save_png(sheet, out)
    return {"sheet": out, "frames": pick}


def run_report(a):
    rows, data = [], {}
    F = frame_set(a.dir)
    w, h = size_of(F)
    lottie, manifest_loop, fps = None, False, a.fps
    if a.lottie:
        lottie, manifest_loop = load_lottie(a.lottie)
        fps = fps or float(lottie.get("fr", 60))
    fps = fps or 60.0
    rows.append(Row("규격", OK, f"{w}x{h}, {len(F)}프레임 (f{min(F)}~f{max(F)}), {fps:g}fps", ""))

    def add(key, res):
        rows.append(res[0])
        data[key] = res[1]

    sc = scan(F)
    add("ink", check_ink(a.dir, a.lottie, sc))
    for key, folder, label in (("ink_lottieweb", a.lottie_web, "잉크(lottie-web)"), ("ink_engine", a.engine, "잉크(엔진)")):
        if folder:
            add(key, check_ink(folder, name=label))
    add("motion", check_motion(a.dir, fps=fps, sc=sc))
    if a.loop or manifest_loop:
        add("loop", check_loop(a.dir, sc))
    else:
        rows.append(Row("루프 이음새", SKIP, "루프 에셋이 아니다(--loop 나 dotLottie manifest 의 loop 로 지정)", ""))
    for key, folder, fn, label in (("players", a.lottie_web, check_players, "플레이어 차이"), ("routes", a.engine, check_routes, "경로 차이")):
        if folder:
            add(key, fn(a.dir, folder, common_only=a.common))
        else:
            rows.append(Row(label, SKIP, f"--{'lottie-web' if key == 'players' else 'engine'} 없음", ""))
    if a.lottie:
        add("markers", check_markers(a.lottie, a.dir))
    if a.theme:
        themes = parse_themes(a.theme)
        where = a.sheet_dir or (Path(a.out or a.json).parent if (a.out or a.json) else None)
        if where is None:
            raise ToolError("테마 시트를 쓸 폴더가 필요하다: --sheet-dir 이나 --out/--json 을 준다")
        for name, folder in themes:
            add(f"ink_theme_{name}", check_ink(folder, name=f"잉크(테마 {name})"))
        sheet = str(Path(where) / "sheet_themes.png")
        add("themes", check_themes(themes, out=sheet))
        rows[-1].line += f" (시트 {sheet})"
    return rows, data


def render_report(rows):
    lines = [f"{MARK[r.status]} {r.check}: {r.line}" for r in rows]
    todo = [f"- {r.check}: {r.fix}" for r in rows if r.status in (WARN, FAIL)]
    n = {s: sum(1 for r in rows if r.status == s) for s in (OK, WARN, FAIL)}
    lines.append(f"\n✓ {n[OK]}  △ {n[WARN]}  ✗ {n[FAIL]}")
    lines.append("\n고칠 것:\n" + ("\n".join(todo) if todo else "- 없음"))
    return "\n".join(lines)


def emit(row, data, as_json=None):
    print(f"{MARK[row.status]} {row.check}: {row.line}")
    if row.status in (WARN, FAIL):
        print(f"  고칠 것: {row.fix}")
    body = json.dumps(data, ensure_ascii=False, indent=2)
    if as_json:
        write_text(as_json, body)
    print(body)
    return 1 if row.status == FAIL else 0


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    def cmd(name, *args, flags=()):
        c = sp.add_parser(name)
        for x in args:
            c.add_argument(x)
        for f, kw in flags:
            c.add_argument(f, **kw)
        c.add_argument("--json")

    cmd("players", "A", "B", flags=[("--sheet", {}), ("--common", {"action": "store_true"})])
    cmd("routes", "A", "B", flags=[("--sheet", {}), ("--grid", {"type": int, "default": 8}), ("--common", {"action": "store_true"})])
    cmd("loop", "DIR")
    cmd("ink", "DIR", flags=[("--lottie", {})])
    cmd("motion", "DIR", flags=[("--first", {"type": int}), ("--last", {"type": int}), ("--fps", {"type": float, "default": 60.0})])
    cmd("markers", "DIR", flags=[("--lottie", {"required": True}), ("--loop", {"action": "append"})])
    cmd("themes", flags=[("--out", {}), ("THEME", {"nargs": "+"})])
    cmd("sheet", "DIR", flags=[("--out", {"required": True}), ("--count", {"type": int, "default": 12}), ("--every", {"type": int}),
                               ("--cols", {"type": int, "default": 6}), ("--width", {"type": int, "default": 360})])
    cmd("report", flags=[("--dir", {"required": True}), ("--lottie", {}), ("--lottie-web", {}), ("--engine", {}), ("--theme", {"action": "append"}),
                         ("--loop", {"action": "store_true"}), ("--common", {"action": "store_true"}), ("--fps", {"type": float}), ("--out", {}), ("--sheet-dir", {})])
    return p


def positive(**named):
    for name, v in named.items():
        if v is not None and not (np.isfinite(v) and v > 0):
            raise ToolError(f"--{name} 는 0 보다 큰 숫자여야 한다: {v}")


def run(a):
    positive(fps=getattr(a, "fps", None), count=getattr(a, "count", None), cols=getattr(a, "cols", None), width=getattr(a, "width", None))
    if a.cmd == "players":
        return emit(*check_players(a.A, a.B, a.sheet, a.common), a.json)
    if a.cmd == "routes":
        return emit(*check_routes(a.A, a.B, a.grid, a.sheet, a.common), a.json)
    if a.cmd == "loop":
        return emit(*check_loop(a.DIR), a.json)
    if a.cmd == "ink":
        return emit(*check_ink(a.DIR, a.lottie), a.json)
    if a.cmd == "motion":
        return emit(*check_motion(a.DIR, a.first, a.last, a.fps), a.json)
    if a.cmd == "markers":
        return emit(*check_markers(a.lottie, a.DIR, tuple(a.loop) if a.loop else ("idle", "loop")), a.json)
    if a.cmd == "themes":
        return emit(*check_themes(parse_themes(a.THEME), a.out), a.json)
    if a.cmd == "sheet":
        print(json.dumps(make_sheet(a.DIR, a.out, a.count, a.every, a.cols, a.width)))
        return 0
    rows, data = run_report(a)
    text = render_report(rows)
    print(text)
    if a.out:
        write_text(a.out, text + "\n")
    if a.json:
        write_text(a.json, json.dumps(data, ensure_ascii=False, indent=2))
    return 1 if any(r.status == FAIL for r in rows) else 0


def main():
    try:
        sys.exit(run(build_parser().parse_args()))
    except ToolError as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"오류: 예기치 못한 {e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
