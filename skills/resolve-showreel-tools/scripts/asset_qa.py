#!/usr/bin/env python3
"""에셋 프레임 폴더 검수. 프레임은 render.mjs --frames 가 쓴 f00000.png … 이다. 시트는 반드시 Read 로 직접 열어 본다.

사용법
  asset_qa.py players A B [--sheet out.png]      두 플레이어(dotlottie / lottie-web) 렌더 차이
  asset_qa.py routes  A B [--grid 8] [--sheet out.png]   두 경로(Lottie / 엔진) 차이와 영역별 채도·밝기 차이(A-B)
  asset_qa.py loop    DIR                        마지막→처음 이음새와 프레임 간 중앙 변화의 비
  asset_qa.py ink     DIR                        빈 프레임, 빈 프레임만 나오는 깨진 Lottie
  asset_qa.py motion  DIR [--first N --last M] [--fps 60]   멈춘 구간
  asset_qa.py markers --lottie X.json|X.lottie DIR [--loop idle]   마커 경계 포즈 차이
  asset_qa.py themes  light=DIR dark=DIR … [--out sheet.png]   테마별 행 시트와 테마 간 차이
  asset_qa.py sheet   DIR --out sheet.png [--count 12 --cols 6 --width 360]
  asset_qa.py report  --dir DIR [--lottie X] [--lottie-web DIR] [--engine DIR] [--theme name=DIR …] [--fps 60] [--out qa/report.txt]

수치는 스파이크 harness/measure.py 와 같은 식이다(회색 128 위에 합성, 채널 최대 절대차의 평균, 0-255).
모든 하위 명령은 한 줄 판정(✓ △ ✗)과 JSON 상세를 출력하고 ✗ 이면 종료 코드 1 이다.
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
LIMITS = {
    "players_warn_mean": 1.0, "players_fail_pct32": 2.0, "players_warn_pct32": 0.5,
    "routes_warn_mean": 3.0, "routes_warn_gap": 0.01,
    "loop_ok": 1.5, "loop_warn": 3.0,
    "ink_min": 0.0005,
    "motion_fail_static": 0.95,
    "marker_ok": 1.0, "marker_warn": 3.0,
    "themes_same": 0.5,
}


@dataclass
class Row:
    check: str
    status: str
    line: str
    fix: str = ""


def frames_of(d):
    fs = sorted(Path(d).glob("f*.png")) or sorted(Path(d).glob("f*.jpeg"))
    if not fs:
        sys.exit(f"no frames in {d}")
    return {int(f.stem[1:]): f for f in fs}


def load(f, grey=128):
    a = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32)
    alpha = a[..., 3:4] / 255.0
    return a[..., :3] * alpha + grey * (1 - alpha)


def pose_diff(x, y):
    return float(np.abs(x - y).max(axis=2).mean())


def saturation(x):
    mx, mn = x.max(axis=2), x.min(axis=2)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)


def checker(w, h, s=16):
    y, x = np.mgrid[0:h, 0:w]
    base = np.where((((x // s) + (y // s)) % 2)[..., None] == 1, 205, 245).astype(np.uint8)
    return Image.fromarray(np.repeat(base, 3, axis=2), "RGB")


def thumb(f, width):
    im = Image.open(f).convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    bg = checker(*im.size).convert("RGBA")
    bg.alpha_composite(im)
    return bg.convert("RGB")


def stack(rows_img, bg=(30, 30, 30)):
    sheet = Image.new("RGB", (max(t.width for t in rows_img), sum(t.height for t in rows_img)), bg)
    y = 0
    for t in rows_img:
        sheet.paste(t, (0, y))
        y += t.height
    return sheet


def save_png(img, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def pmap(fn, items, parallel):
    if not parallel:
        return [fn(x) for x in items]
    with ProcessPoolExecutor() as ex:
        return list(ex.map(fn, items, chunksize=max(1, len(items) // ((os.cpu_count() or 4) * 4))))


def is_big(F):
    w, h = Image.open(next(iter(F.values()))).size
    return w * h > 500_000 and len(F) >= 64


def diff_one(job):
    pa, pb, i, grid = job
    x, y = load(pa), load(pb)
    if x.shape != y.shape:
        sys.exit(f"size mismatch at frame {i}: {x.shape} vs {y.shape}")
    d = np.abs(x - y).max(axis=2)
    r = {"frame": i, "mean": float(d.mean()), "pct_over_32": float((d > 32).mean() * 100)}
    if grid:
        r["sat"] = cell_means(saturation(x) - saturation(y), grid)
        r["level"] = cell_means(x.mean(axis=2) - y.mean(axis=2), grid)
    return r


GRID_SAMPLES = 24


def diff_rows(A, B, grid=0):
    common = sorted(set(A) & set(B))
    if not common:
        sys.exit("no common frames")
    sampled = set(common[:: max(1, len(common) // GRID_SAMPLES)]) if grid else set()
    rows = pmap(diff_one, [(A[i], B[i], i, grid if i in sampled else 0) for i in common], is_big(A))
    return common, rows


def cell_means(a, n):
    h, w = a.shape
    return [[float(a[r * h // n:(r + 1) * h // n, c * w // n:(c + 1) * w // n].mean()) for c in range(n)] for r in range(n)]


def diff_summary(rows, top=6):
    means = np.array([r["mean"] for r in rows])
    pcts = np.array([r["pct_over_32"] for r in rows])
    return {"frames": len(rows),
            "mean_abs_diff": {"avg": round(float(means.mean()), 3), "median": round(float(np.median(means)), 3), "max": round(float(means.max()), 3)},
            "pct_pixels_over_32": {"avg": round(float(pcts.mean()), 3), "max": round(float(pcts.max()), 3)},
            "worst": [{"frame": r["frame"], "mean": round(r["mean"], 3), "pct_over_32": round(r["pct_over_32"], 3)} for r in sorted(rows, key=lambda r: -r["mean"])[:top]]}


def diff_sheet(A, B, worst, path):
    w, tiles = 480, []
    for r in worst:
        i = r["frame"]
        ta, tb = thumb(A[i], w), thumb(B[i], w)
        d = np.clip(np.abs(load(A[i]) - load(B[i])).max(axis=2) * 4, 0, 255).astype(np.uint8)
        hm = Image.fromarray(d, "L").resize(ta.size).convert("RGB")
        row = Image.new("RGB", (w * 3 + 20, ta.height + 24), (30, 30, 30))
        row.paste(ta, (0, 24)); row.paste(tb, (w + 10, 24)); row.paste(hm, (2 * w + 20, 24))
        ImageDraw.Draw(row).text((6, 5), f"frame {i}  mean {r['mean']:.2f}  >32: {r['pct_over_32']:.2f}%   [A | B | diff x4]", fill=(240, 240, 240))
        tiles.append(row)
    save_png(stack(tiles), path)


def check_players(A, B, sheet=None, name="플레이어 차이"):
    FA, FB = frames_of(A), frames_of(B)
    _, rows = diff_rows(FA, FB)
    s = diff_summary(rows)
    m, p = s["mean_abs_diff"]["avg"], s["pct_pixels_over_32"]["avg"]
    if p > LIMITS["players_fail_pct32"]:
        st, fix = FAIL, "두 플레이어가 다르게 그린다. 글자별 애니메이터·텍스트 레이어·지원 안 되는 기능을 외곽선과 기본 도형으로 바꾼다"
    elif m > LIMITS["players_warn_mean"] or p > LIMITS["players_warn_pct32"]:
        st, fix = WARN, "차이가 큰 프레임을 시트로 열어 번짐·가장자리·안티앨리어싱 차이인지 확인한다"
    else:
        st, fix = OK, ""
    if sheet:
        diff_sheet(FA, FB, s["worst"], sheet)
        s["sheet"] = sheet
    return Row(name, st, f"평균 {m} /255, 32 초과 화소 {p}% ({s['frames']}프레임)", fix), s


def region_label(r, c, n):
    return "가운데" if abs(r - (n - 1) / 2) <= 0.5 and abs(c - (n - 1) / 2) <= 0.5 else ("가장자리" if r in (0, n - 1) or c in (0, n - 1) else "중간")


def check_routes(A, B, grid=8, sheet=None):
    FA, FB = frames_of(A), frames_of(B)
    _, rows = diff_rows(FA, FB, grid)
    s = diff_summary(rows)
    out = {}
    for key in ("sat", "level"):
        mean = np.mean([r[key] for r in rows if key in r], axis=0)
        zones = {"가장자리": [], "중간": [], "가운데": []}
        for r in range(grid):
            for c in range(grid):
                zones[region_label(r, c, grid)].append(mean[r][c])
        out[key] = {"grid": [[round(float(v), 4) for v in row] for row in mean],
                    **{z: round(float(np.mean(v)), 4) for z, v in zones.items() if v}}
    s.update(grid=grid, saturation_A_minus_B=out["sat"], level_A_minus_B=out["level"])
    m, gap = s["mean_abs_diff"]["avg"], out["sat"]["가장자리"]
    if abs(gap) > LIMITS["routes_warn_gap"] or m > LIMITS["routes_warn_mean"]:
        st, fix = WARN, "한 경로의 가장자리 채도가 다르다. 엔진 쪽 색 관리(sRGB, 흐린 배경의 알파 합성)와 인코딩 색 태그를 확인한다" if abs(gap) > LIMITS["routes_warn_gap"] else "engineOnly 노드 때문인지 확인한다"
    else:
        st, fix = OK, ""
    if sheet:
        diff_sheet(FA, FB, s["worst"], sheet)
        s["sheet"] = sheet
    line = f"평균 {m} /255, 채도 차이 가장자리 {gap:+.4f} 가운데 {out['sat']['가운데']:+.4f}, 밝기 차이 가장자리 {out['level']['가장자리']:+.3f} 가운데 {out['level']['가운데']:+.3f}"
    return Row("경로 차이", st, line, fix), s


def scan_chunk(job):
    items, prev_idx = job
    ink, steps, prev = {}, [], None
    for i, f in items:
        a = np.asarray(Image.open(f).convert("RGBA"))
        al = a[..., 3]
        if al.min() < 255:
            mask = al > 16
        else:
            sub = a[::16, ::16, :3].reshape(-1, 3).astype(np.int16)
            mask = np.abs(a[..., :3].astype(np.int16) - np.median(sub, axis=0)).max(axis=2) > 24
        ink[i] = float(mask.mean())
        alpha = a[..., 3:4].astype(np.float32) / 255.0
        cur = a[..., :3].astype(np.float32) * alpha + 128 * (1 - alpha)
        if prev is not None:
            steps.append(pose_diff(cur, prev))
        prev = cur
    return ink, steps


def scan(F):
    idx = sorted(F)
    n = max(1, min(len(idx) - 1, (os.cpu_count() or 4) * 2 if is_big(F) else 1))
    bounds = [round(k * (len(idx) - 1) / n) for k in range(n + 1)]
    jobs = [([(i, F[i]) for i in idx[bounds[k]:bounds[k + 1] + 1]], None) for k in range(n)] if len(idx) > 1 else [([(idx[0], F[idx[0]])], None)]
    res = pmap(scan_chunk, jobs, n > 1)
    ink, steps = {}, []
    for k_ink, k_steps in res:
        ink.update(k_ink)
        steps += k_steps
    return {"idx": idx, "ink": ink, "steps": steps, "frames": F}


def check_loop(d, sc=None):
    sc = sc or scan(frames_of(d))
    idx, steps, F = sc["idx"], sc["steps"], sc["frames"]
    if len(idx) < 3 or idx != list(range(idx[0], idx[-1] + 1)):
        return Row("루프 이음새", FAIL, "연속된 전체 프레임이 필요하다", "--frames all 로 다시 캡처한다"), {}
    seam = pose_diff(load(F[idx[0]]), load(F[idx[-1]]))
    med = max(float(np.median(steps)), STATIC_STEP)
    ratio = seam / med
    s = {"frames": len(idx), "seam_diff": round(seam, 3), "median_step_diff": round(float(np.median(steps)), 3), "max_step_diff": round(max(steps), 3),
         "ratio": round(ratio, 2), "seamless": ratio <= LIMITS["loop_ok"], "static_steps": sum(1 for v in steps if v < STATIC_STEP)}
    st = OK if ratio <= LIMITS["loop_ok"] else WARN if ratio <= LIMITS["loop_warn"] else FAIL
    fix = "" if st == OK else "마지막 프레임이 처음 프레임으로 이어지지 않는다. 끝 포즈를 첫 포즈에 맞추고 루프 길이를 주기의 정수배로 한다"
    return Row("루프 이음새", st, f"이음새 {s['seam_diff']} / 중앙 변화 {s['median_step_diff']} = 비 {s['ratio']}", fix), s


def lottie_issues(path):
    d = load_lottie(path)
    issues = []
    layers = d.get("layers") or []
    if not layers:
        issues.append("layers 가 비어 있다")
    if d.get("op", 0) <= d.get("ip", 0):
        issues.append("op <= ip 라 재생할 프레임이 없다")
    visible = [ly for ly in layers if not ly.get("hd")]
    if layers and not visible:
        issues.append("모든 레이어가 숨김(hd)이다")
    for ly in visible:
        if ly.get("ty") == 4 and not ly.get("shapes"):
            issues.append(f"셰이프 레이어 '{ly.get('nm', '?')}' 에 shapes 가 없다")
        if "ks" not in ly:
            issues.append(f"레이어 '{ly.get('nm', '?')}' 에 ks(transform)가 없다")
    return issues


def load_lottie(path):
    p = Path(path)
    if p.suffix == ".lottie":
        with zipfile.ZipFile(p) as z:
            name = next(n for n in z.namelist() if n.startswith(("a/", "animations/")) and n.endswith(".json"))
            return json.loads(z.read(name))
    return json.loads(p.read_text())


def check_ink(d, lottie=None, sc=None):
    sc = sc or scan(frames_of(d))
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
        s["lottie_issues"] = lottie_issues(lottie)
    if len(blank) == len(idx):
        why = "; ".join(s.get("lottie_issues", [])) or "플레이어가 오류 없이 빈 화면을 그렸다"
        return Row("잉크", FAIL, f"전 프레임이 비었다 ({why})", "스키마가 맞아도 구조가 틀리면 플레이어는 빈 화면을 내고 0으로 끝난다. 레이어·셰이프·op/ip 를 점검한다"), s
    if bad:
        return Row("잉크", FAIL, f"빈 프레임 {len(bad)}개: " + ", ".join(f"f{i}" for i in bad[:10]), "빈 프레임의 원인(키프레임 투명도 0, 매트, 레이어 op 범위)을 찾는다"), s
    if blank:
        return Row("잉크", WARN, f"처음·끝에 빈 프레임 {len(blank)}개 (의도한 등장·퇴장이면 무시)", ""), s
    return Row("잉크", OK, f"빈 프레임 없음 (잉크 {s['min_ink'] * 100:.2f}~{s['max_ink'] * 100:.2f}%)", ""), s


def check_motion(d, first=None, last=None, fps=60.0, sc=None):
    sc = sc or scan(frames_of(d))
    idx = sc["idx"]
    steps = [v for k, v in enumerate(sc["steps"]) if (first is None or idx[k] >= first) and (last is None or idx[k + 1] <= last)]
    if len(steps) < 1:
        return Row("움직임", FAIL, "프레임이 2개 미만이다", ""), {}
    n_frames = len(steps) + 1
    static = [v < STATIC_STEP for v in steps]
    run = best = 0
    for v in static:
        run = run + 1 if v else 0
        best = max(best, run)
    frac = sum(static) / len(static)
    s = {"frames": n_frames, "static_steps": sum(static), "static_fraction": round(frac, 3), "longest_static_run": best,
         "mean_step_diff": round(float(np.mean(steps)), 3), "max_step_diff": round(max(steps), 3)}
    if frac >= LIMITS["motion_fail_static"]:
        return Row("움직임", FAIL, f"멈춘 화면 {frac * 100:.0f}% ({s['static_steps']}/{len(steps)}스텝)", "구간이 사실상 정지 상태다. idle 에 호흡·미세한 움직임을 넣거나 한 프레임으로 줄인다"), s
    if best > fps:
        return Row("움직임", WARN, f"{best}프레임({best / fps:.1f}초) 연속으로 멈춘다", "의도한 정지가 아니면 멈춤 구간에 움직임을 넣는다"), s
    return Row("움직임", OK, f"멈춘 스텝 {s['static_steps']}/{len(steps)}, 최장 {best}프레임, 평균 변화 {s['mean_step_diff']}", ""), s


def check_markers(lottie, d, loop_names=("idle", "loop")):
    data = load_lottie(lottie)
    marks = sorted(({"name": m["cm"], "from": int(m["tm"]), "to": int(m["tm"] + m["dr"])} for m in data.get("markers") or []), key=lambda m: m["from"])
    if not marks:
        return Row("마커 경계", SKIP, "마커가 없다", ""), {"markers": []}
    F = frames_of(d)
    pairs = []
    for k, m in enumerate(marks):
        if k > 0 and m["from"] - 1 in F and m["from"] in F:
            pairs.append((f"{m['name']} 진입", m["from"] - 1, m["from"]))
        if m["name"] in loop_names and m["from"] in F and m["to"] in F:
            pairs.append((f"{m['name']} 루프", m["from"], m["to"]))
    out = [{"pair": n, "a": a, "b": b, "diff": round(pose_diff(load(F[a]), load(F[b])), 3)} for n, a, b in pairs]
    s = {"markers": marks, "pairs": out}
    worst = max((p["diff"] for p in out), default=0.0)
    st = OK if worst <= LIMITS["marker_ok"] else WARN if worst <= LIMITS["marker_warn"] else FAIL
    fix = "" if st == OK else "경계 포즈가 튄다. 마커 경계의 끝 포즈와 시작 포즈를 맞춘다"
    line = f"마커 {len(marks)}개, " + ", ".join(f"{p['pair']} f{p['a']}↔f{p['b']} {p['diff']}" for p in out)
    return Row("마커 경계", st if out else WARN, line if out else f"마커 {len(marks)}개의 경계 프레임이 폴더에 없다", fix if out else "마커 경계 프레임까지 캡처한다"), s


def check_themes(themes, out=None, count=6, width=240):
    dirs = {n: frames_of(d) for n, d in themes}
    names = [n for n, _ in themes]
    common = sorted(set.intersection(*[set(f) for f in dirs.values()]))
    pick = [common[round(k * (len(common) - 1) / max(1, count - 1))] for k in range(min(count, len(common)))]
    pairs, same = [], []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            v = float(np.mean([pose_diff(load(dirs[names[a]][i]), load(dirs[names[b]][i])) for i in pick]))
            pairs.append({"a": names[a], "b": names[b], "diff": round(v, 3)})
            if v < LIMITS["themes_same"]:
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
    return Row("테마", OK, f"{len(names)}개 테마, 쌍별 차이 " + ", ".join(f"{p['a']}/{p['b']} {p['diff']}" for p in pairs), ""), s


def make_sheet(d, out, count=12, every=None, cols=6, width=360):
    F = frames_of(d)
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
    fps = a.fps
    rows, data = [], {}
    F = frames_of(a.dir)
    w, h = Image.open(next(iter(F.values()))).size
    rows.append(Row("규격", OK, f"{w}x{h}, {len(F)}프레임 (f{min(F)}~f{max(F)}), {fps:g}fps", ""))

    def add(key, res):
        row, s = res
        rows.append(row)
        data[key] = s

    sc = scan(F)
    add("ink", check_ink(a.dir, a.lottie, sc))
    add("motion", check_motion(a.dir, fps=fps, sc=sc))
    add("loop", check_loop(a.dir, sc))
    if a.lottie_web:
        add("players", check_players(a.dir, a.lottie_web))
    else:
        rows.append(Row("플레이어 차이", SKIP, "--lottie-web 없음", ""))
    if a.engine:
        add("routes", check_routes(a.dir, a.engine))
    else:
        rows.append(Row("경로 차이", SKIP, "--engine 없음", ""))
    if a.lottie:
        add("markers", check_markers(a.lottie, a.dir))
    if a.theme:
        add("themes", check_themes([t.split("=", 1) for t in a.theme], out=str(Path(a.sheet_dir or Path(a.dir).parent) / "sheet_themes.png")))
    return rows, data


def render_report(rows):
    lines = [f"{MARK[r.status]} {r.check}: {r.line}" for r in rows]
    todo = [f"- {r.check}: {r.fix}" for r in rows if r.status in (WARN, FAIL) and r.fix]
    n = {s: sum(1 for r in rows if r.status == s) for s in (OK, WARN, FAIL)}
    lines.append(f"\n✓ {n[OK]}  △ {n[WARN]}  ✗ {n[FAIL]}")
    lines.append("\n고칠 것:\n" + ("\n".join(todo) if todo else "- 없음"))
    return "\n".join(lines)


def emit(row, data, as_json=None):
    print(f"{MARK[row.status]} {row.check}: {row.line}")
    if row.fix and row.status in (WARN, FAIL):
        print(f"  고칠 것: {row.fix}")
    body = json.dumps(data, ensure_ascii=False, indent=2)
    if as_json:
        Path(as_json).parent.mkdir(parents=True, exist_ok=True)
        Path(as_json).write_text(body)
    print(body)
    return 1 if row.status == FAIL else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    def cmd(name, *args, flags=()):
        c = sp.add_parser(name)
        for x in args:
            c.add_argument(x)
        for f, kw in flags:
            c.add_argument(f, **kw)
        c.add_argument("--json")
        return c

    cmd("players", "A", "B", flags=[("--sheet", {})])
    cmd("routes", "A", "B", flags=[("--sheet", {}), ("--grid", {"type": int, "default": 8})])
    cmd("loop", "DIR")
    cmd("ink", "DIR", flags=[("--lottie", {})])
    cmd("motion", "DIR", flags=[("--first", {"type": int}), ("--last", {"type": int}), ("--fps", {"type": float, "default": 60.0})])
    cmd("markers", "DIR", flags=[("--lottie", {"required": True}), ("--loop", {"action": "append"})])
    cmd("themes", flags=[("--out", {}), ("THEME", {"nargs": "+"})])
    cmd("sheet", "DIR", flags=[("--out", {"required": True}), ("--count", {"type": int, "default": 12}), ("--every", {"type": int}),
                               ("--cols", {"type": int, "default": 6}), ("--width", {"type": int, "default": 360})])
    cmd("report", flags=[("--dir", {"required": True}), ("--lottie", {}), ("--lottie-web", {}), ("--engine", {}), ("--theme", {"action": "append"}),
                         ("--fps", {"type": float, "default": 60.0}), ("--out", {}), ("--sheet-dir", {})])
    a = p.parse_args()

    if a.cmd == "players":
        sys.exit(emit(*check_players(a.A, a.B, a.sheet), a.json))
    if a.cmd == "routes":
        sys.exit(emit(*check_routes(a.A, a.B, a.grid, a.sheet), a.json))
    if a.cmd == "loop":
        sys.exit(emit(*check_loop(a.DIR), a.json))
    if a.cmd == "ink":
        sys.exit(emit(*check_ink(a.DIR, a.lottie), a.json))
    if a.cmd == "motion":
        sys.exit(emit(*check_motion(a.DIR, a.first, a.last, a.fps), a.json))
    if a.cmd == "markers":
        sys.exit(emit(*check_markers(a.lottie, a.DIR, tuple(a.loop) if a.loop else ("idle", "loop")), a.json))
    if a.cmd == "themes":
        sys.exit(emit(*check_themes([t.split("=", 1) for t in a.THEME], a.out), a.json))
    if a.cmd == "sheet":
        print(json.dumps(make_sheet(a.DIR, a.out, a.count, a.every, a.cols, a.width)))
        return
    rows, data = run_report(a)
    text = render_report(rows)
    print(text)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text + "\n")
    if a.json:
        Path(a.json).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(1 if any(r.status == FAIL for r in rows) else 0)


if __name__ == "__main__":
    main()
