#!/usr/bin/env python3
"""사용자가 한 파일로 녹음한 나레이션 → 줄별 클립 audio/vo/<id>.mp3 + <id>.align.json + report.json. narrate.py 대신 쓴다.

사용법
  vo_split.py <녹음> --script <project>/script.json [--stt <받아쓰기.json>] [--out audio/vo]
              [--spans n06=31.2-34.2,n17=67.5-70.3] [--timeline timeline.json] [--lang ko|en] [--dry-run]

녹음 규칙: 한 파일에 줄 순서대로 읽고, 틀리면 그 줄을 처음부터 다시 읽는다. 다시 읽은 줄은 마지막 테이크를 쓰고
앞 테이크·군말·헛시작은 버린다(버린 구간은 "쓰지 않은 구간"으로 출력). 녹음 원본은 읽기만 한다.

줄 찾기
  --stt 있음  받아쓰기(eleven.py stt <녹음> --json out.json, 크레딧을 쓰므로 한 번 받아 저장)의 단어 시각에
              script.json 줄(tts 가 있으면 tts, 없으면 text)을 순서대로 맞춘다. 가장 정확하다. align.json 은 단어 시각이다.
  --stt 없음  소리 크기로 말 덩어리를 찾고, macOS say 로 만든 기준 낭독(언어별 음성 3개, 임시 폴더)과 MFCC+DTW 거리를
              비교해 줄 번호를 붙인다(20~30초). 쉼 길이는 믿지 않는다. 쉼표 자리에서 갈라진 덩어리는 한 줄로 묶고,
              같은 줄로 본 테이크끼리는 서로 같은 문장으로 들려야 한다(DTW 거리). 녹음 문장이 원고와 같은지는 확인하지 못한다.
              align.json 은 글자를 말한 시간에 고르게 편 추정이라 report.json 에 "align": "estimated" 로 적고,
              그 줄의 cues 는 대략의 시각이다. 줄 사이를 0.3초보다 좁게 읽었거나 0.25초보다 짧은 줄은 자동으로 못 나눈다(--spans).
  --spans     자동으로 못 맞춘 줄을 원본 시각으로 고친다(n06=시작-끝). 앞뒤 가장자리는 소리 크기로 다듬는다.

가장자리: 소음 바닥(10퍼센트 지점)+12dB 를 넘는 소리를 말로 보고 60ms 보다 짧은 소리는 버린다. 말 앞 0.12초·뒤 0.22초를
남기되 이웃 테이크·소리 덩어리 안으로는 넘지 않는다.

--timeline: scenes 의 start/end 가 숫자로 풀린 timeline.json 을 주면 숫자 "at" 이 있는 줄마다 시작·끝·앞 줄과의 틈
(0.25초 이상)·장면 끝 0.25초 전까지 여유를 표로 보이고, 모자라면 ✗ 로 표시한다.
✗(줄 못 찾음 포함)가 하나라도 있으면 종료 코드 1. 줄 길이를 고를 때 이 표를 쓴다.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
import tempfile
import warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

SR = 48000
HOP = 0.01
PAD_IN, PAD_OUT = 0.12, 0.22
GAP_LINE = 0.25
THETA_STT = 0.5
THETA_AUDIO = 0.3
COVER = 0.3
PRIOR, PRIOR_TOL = 2.0, 0.3
FULL_SLACK = 0.12
RETAKE_DIST = 14.5
MIN_EDGE_RUN = 0.25
GROUP_RUNS, GROUP_GAP = 4, 1.2
SAY_PREFERRED = ["Eddy", "Reed", "Flo", "Shelley", "Grandma", "Daniel", "Samantha", "Yuna"]


@dataclass
class Take:
    line: int
    method: str
    score: float
    s: float
    e: float
    words: list = field(default_factory=list)
    on: float = 0.0
    off: float = 0.0
    c0: float = 0.0
    c1: float = 0.0


def die(msg):
    sys.exit(f"✗ {msg}")


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        die(f"{path} 를 읽지 못했다: {e}")


def norm(s):
    return "".join(c for c in s.lower() if c.isalnum())


def pcm(path, sr):
    try:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
    except FileNotFoundError:
        die("ffmpeg 가 없다")
    except subprocess.CalledProcessError as e:
        die(f"{path} 를 읽지 못했다: {e.stderr.decode(errors='replace').strip()}")
    return np.frombuffer(raw, np.float32)


class Sound:
    def __init__(self, path):
        self.path = Path(path)
        x = pcm(self.path, SR)
        hop = int(SR * HOP)
        n = len(x) // hop
        if n < 10:
            die(f"{path} 가 비어 있거나 너무 짧다")
        self.dur = len(x) / SR
        self.db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1)) + 1e-9)
        self.floor = float(np.percentile(self.db, 10))
        self.mask = self.db > self.floor + 12

    def runs(self, gap, minlen=0.0):
        d = np.diff(np.concatenate([[0], self.mask.astype(np.int8), [0]]))
        out = []
        for a, b in zip(np.where(d == 1)[0] * HOP, np.where(d == -1)[0] * HOP):
            if b - a < 0.06:
                continue
            if out and a - out[-1][1] <= gap + 1e-9:
                out[-1][1] = b
            else:
                out.append([a, b])
        return [r for r in out if r[1] - r[0] >= minlen]


def chain(npos, nlines, cands):
    ending = defaultdict(list)
    for c in cands:
        ending[c[1]].append(c)
    g = np.zeros((npos + 1, nlines + 1))
    how = {}
    for p in range(npos + 1):
        for k in range(1, nlines + 1):
            g[p, k], how[p, k] = g[p, k - 1], "k"
            if p and g[p - 1, k] > g[p, k]:
                g[p, k], how[p, k] = g[p - 1, k], "p"
            for c in ending[p]:
                if c[2] == k - 1 and g[c[0], k - 1] + c[3] > g[p, k]:
                    g[p, k], how[p, k] = g[c[0], k - 1] + c[3], c
    out, p, k = [], npos, nlines
    while p and k:
        h = how[p, k]
        if h == "k":
            k -= 1
        elif h == "p":
            p -= 1
        else:
            out.append(h)
            p, k = h[0], k - 1
    anchors = list(out)
    for k in range(nlines):
        lo = max((c[1] for c in anchors if c[2] < k), default=0)
        hi = min((c[0] for c in anchors if c[2] > k), default=npos)
        for c in sorted((c for c in cands if c[2] == k and lo <= c[0] and c[1] <= hi), key=lambda c: -c[3]):
            if all(c[1] <= d[0] or d[1] <= c[0] for d in out):
                out.append(c)
    return sorted(out)


def stt_takes(words, lines, blocked):
    toks = [w for w in words if w.get("type", "word") == "word" and norm(w["text"])]
    nt = [norm(w["text"]) for w in toks]
    cum = np.concatenate([[0], np.cumsum([len(t) for t in nt])])
    cands = []
    for k, l in enumerate(lines):
        if l["id"] in blocked["ids"]:
            continue
        targets = list({norm(l.get("tts") or l["text"]), norm(l["text"])} - {""})
        lo, hi = min(map(len, targets)), max(map(len, targets))
        for T in targets:
            sm = difflib.SequenceMatcher(None, autojunk=False)
            sm.set_seq2(T)
            for a in range(len(toks)):
                for b in range(a, len(toks)):
                    n = cum[b + 1] - cum[a]
                    if n > 1.6 * hi + 2:
                        break
                    if n < 0.4 * lo or blocked["hit"](toks[a]["start"], toks[b]["end"]):
                        continue
                    sm.set_seq1("".join(nt[a:b + 1]))
                    if sm.real_quick_ratio() < THETA_STT or sm.quick_ratio() < THETA_STT:
                        continue
                    r = sm.ratio()
                    if r >= THETA_STT:
                        cands.append((a, b + 1, k, r - THETA_STT, r))
    best = {}
    for c in chain(len(toks), len(lines), cands):
        best[c[0], c[1], c[2]] = max(best.get((c[0], c[1], c[2]), 0), c[4])
    takes = [Take(k, "stt", r, toks[a]["start"], toks[b - 1]["end"], [[w["text"], w["start"], w["end"]] for w in toks[a:b]])
             for (a, b, k), r in best.items()]
    used = np.zeros(len(toks), bool)
    for a, b, _ in best:
        used[a:b] = True
    junk, i = [], 0
    while i < len(toks):
        j = i
        while j < len(toks) and not used[j]:
            j += 1
        if j > i:
            junk.append((toks[i]["start"], toks[j - 1]["end"], "받아쓴 말: " + " ".join(w["text"] for w in toks[i:j])))
        i = max(j, i + 1)
    return takes, junk


def say_voices(lang, want=3):
    try:
        out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        die("say 가 없다(macOS 전용) → --stt 로 받아쓰기를 주거나 --spans 로 줄 위치를 직접 지정한다")
    have = []
    for ln in out.splitlines():
        m = re.match(r"(.+?)\s{2,}([a-z]{2,3})_[A-Z]{2}\s", ln)
        if m and m.group(2) == lang:
            have.append(m.group(1))
    if not have:
        die(f"say 에 '{lang}' 음성이 없다(say -v '?') → --stt 로 받아쓰기를 주거나 --spans 로 줄 위치를 직접 지정한다")
    base = lambda v: v.split(" (")[0]
    have = list({base(v): v for v in reversed(have)}.values())
    have.sort(key=lambda v: SAY_PREFERRED.index(base(v)) if base(v) in SAY_PREFERRED else len(SAY_PREFERRED))
    return have[:want]


MR, MH, MN, MM, MC = 16000, 320, 512, 26, 13


def _mel_tables():
    mel = lambda hz: 2595 * np.log10(1 + hz / 700)
    pts = 700 * (10 ** (np.linspace(mel(100), mel(6000), MM + 2) / 2595) - 1)
    bins = np.floor((MN + 1) * pts / MR).astype(int)
    fb = np.zeros((MM, MN // 2 + 1))
    for m in range(1, MM + 1):
        a, b, c = bins[m - 1], bins[m], bins[m + 1]
        fb[m - 1, a:b] = (np.arange(a, b) - a) / max(b - a, 1)
        fb[m - 1, b:c] = (c - np.arange(b, c)) / max(c - b, 1)
    dct = np.cos(np.pi / MM * (np.arange(MM)[None, :] + 0.5) * np.arange(MC)[:, None])
    return fb, dct


FB, DCT = _mel_tables()


def mfcc(x, zscore=True):
    x = x.astype(np.float64)
    x = np.append(x[0], x[1:] - 0.97 * x[:-1])
    fr = np.lib.stride_tricks.sliding_window_view(x, MN)[::MH] * np.hanning(MN)
    mf = (np.log((np.abs(np.fft.rfft(fr, MN)) ** 2) @ FB.T + 1e-10) @ DCT.T)[:, 1:]
    mf = mf - mf.mean(0)
    return mf / (mf.std(0) + 1e-6) if zscore else mf


def dtw(A, B):
    D = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    prev = np.full(D.shape[1] + 1, np.inf)
    prev[0] = 0
    for i in range(D.shape[0]):
        tmp = D[i] + np.minimum(prev[1:], prev[:-1])
        cs = np.cumsum(D[i])
        prev = np.concatenate([[np.inf], cs + np.minimum.accumulate(tmp - cs)])
    return prev[-1] / sum(D.shape)


def reference(lines, lang):
    voices = say_voices(lang)
    print(f"기준 낭독 음성: {', '.join(voices)}")
    with tempfile.TemporaryDirectory() as tmp:
        def one(job):
            v, k = job
            f = Path(tmp) / f"{voices.index(v)}_{k}.aiff"
            subprocess.run(["say", "-v", v, "-o", str(f), "--", lines[k].get("tts") or lines[k]["text"]], check=True)
            x = pcm(f, MR)
            db = 20 * np.log10(np.sqrt((x[:len(x) // 160 * 160].reshape(-1, 160) ** 2).mean(1)) + 1e-9)
            on = np.where(db > db.max() - 35)[0]
            x = x[on[0] * 160:(on[-1] + 1) * 160] if len(on) else x
            return mfcc(x), len(x) / MR
        jobs = [(v, k) for v in voices for k in range(len(lines))]
        try:
            with ThreadPoolExecutor(4) as ex:
                res = list(ex.map(one, jobs))
        except subprocess.CalledProcessError as e:
            die(f"say 로 기준 낭독을 만들지 못했다({e.cmd[2]}) → --stt 로 받아쓰기를 주거나 --spans 로 줄 위치를 직접 지정한다")
    return [[res[vi * len(lines) + k] for k in range(len(lines))] for vi in range(len(voices))]


def alike(Ds):
    out = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for X in Ds:
            for _ in range(2):
                for ax in (1, 0):
                    if np.isfinite(X).any(1 - ax).sum() > 1:
                        X = (X - np.nanmean(X, ax, keepdims=True)) / (np.nanstd(X, ax, keepdims=True) + 1e-9)
            out.append(-X)
        return np.nanmean(out, axis=0)


def audio_takes(snd, lines, lang, blocked):
    utt = snd.runs(0.30, 0.12)
    groups = []
    for i in range(len(utt)):
        for j in range(i, min(i + GROUP_RUNS, len(utt))):
            if j > i and utt[j][0] - utt[j - 1][1] > GROUP_GAP:
                break
            if all(r[1] - r[0] >= MIN_EDGE_RUN for r in (utt[i], utt[j])):
                groups.append((i, j + 1))
    x16 = pcm(snd.path, MR)
    gx = [mfcc(x16[int(utt[i][0] * MR):int(utt[j - 1][1] * MR)]) for i, j in groups]
    gd = [utt[j - 1][1] - utt[i][0] for i, j in groups]
    ref = reference(lines, lang)
    Ds = []
    for R in ref:
        D = np.full((len(groups), len(lines)), np.nan)
        for g, (A, d) in enumerate(zip(gx, gd)):
            for k, (B, rd) in enumerate(R):
                if lines[k]["id"] not in blocked["ids"] and 0.4 <= d / rd <= 2.6:
                    D[g, k] = dtw(A, B)
        Ds.append(D)

    def solve(Z):
        cands = [(i, j, k, Z[g, k] - THETA_AUDIO + COVER * gd[g], Z[g, k], g) for g, (i, j) in enumerate(groups) for k in range(len(lines))
                 if Z[g, k] > THETA_AUDIO and not blocked["hit"](utt[i][0], utt[j - 1][1])]
        return chain(len(utt), len(lines), cands)

    Z, gd, rd = alike(Ds), np.array(gd), np.mean([[r[1] for r in R] for R in ref], axis=0)
    best = solve(Z)
    if best:
        rho = np.median([gd[c[5]] / rd[c[2]] for c in best])
        Z = Z - PRIOR * np.maximum(0, np.abs(np.log(gd[:, None] / rd[None, :] / rho)) - PRIOR_TOL)
        best = solve(Z)
    takes = [Take(k, "audio", float(z), utt[i][0], utt[j - 1][1]) for i, j, k, _, z, _ in best]
    same = []
    for k in {t.line for t in takes}:
        ts = [t for t in takes if t.line == k]
        top = max(ts, key=lambda t: t.score)
        ft = {id(t): mfcc(x16[int(t.s * MR):int(t.e * MR)], zscore=False) for t in ts}
        same += [t for t in ts if t is top or dtw(ft[id(top)], ft[id(t)]) <= RETAKE_DIST]
    junk = [(a, b, "") for a, b in utt if not any(t.s <= a and b <= t.e for t in same)]
    return same, junk


def refine(takes, snd):
    fine = snd.runs(0.15)
    order = sorted(takes, key=lambda t: t.s)
    for i, t in enumerate(order):
        lo = max(order[i - 1].e + 0.08 if i else 0.0, t.s - 0.35)
        hi = min(order[i + 1].s - 0.08 if i + 1 < len(order) else snd.dur, t.e + 0.6)
        r_on = next((r for r in fine if r[1] >= t.s - 0.05 and r[0] <= t.e - 0.05), None)
        r_off = next((r for r in reversed(fine) if r[0] <= t.e + 0.05 and r[1] >= t.s + 0.05), None)
        t.on = max(r_on[0], lo) if r_on else t.s
        t.off = min(r_off[1], hi) if r_off else t.e
        if t.off <= t.on:
            t.on, t.off = t.s, t.e
        before = max((r[1] for r in fine if r[1] <= (r_on or [t.s])[0]), default=0.0)
        after = min((r[0] for r in fine if r[0] >= (r_off[1] if r_off else t.e)), default=snd.dur)
        t.c0 = max(lo, t.on - PAD_IN, before + 0.02 if before else 0.0)
        t.c1 = min(hi, t.off + PAD_OUT, after - 0.02)


def cut(snd, t, mp3):
    dur = t.c1 - t.c0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t.c0:.3f}", "-t", f"{dur:.3f}", "-i", str(snd.path),
                    "-af", f"afade=t=in:st=0:d=0.02,afade=t=out:st={max(0, dur - 0.08):.3f}:d=0.08",
                    "-ar", "48000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "192k", str(mp3)], check=True)


def heard_times(text, t):
    mine = [c.lower() for c in text if c.isalnum()]
    heard = []
    for w, a, b in t.words:
        cs = [c for c in w.lower() if c.isalnum()]
        b = max(b, a + 0.05)
        heard += [(c, a + (b - a) * j / len(cs), a + (b - a) * (j + 1) / len(cs)) for j, c in enumerate(cs)]
    t0, t1 = [None] * len(mine), [None] * len(mine)
    for blk in difflib.SequenceMatcher(None, mine, [h[0] for h in heard], autojunk=False).get_matching_blocks():
        for d in range(blk.size):
            t0[blk.a + d], t1[blk.a + d] = heard[blk.b + d][1], heard[blk.b + d][2]
    return t0, t1, (heard[0][1] if heard else t.s), (heard[-1][2] if heard else t.e)


def spread_times(text, parts):
    segs = [n for n in (sum(c.isalnum() for c in s) for s in re.split(r"(?<=[,;:…])", text)) if n]
    groups = list(zip(segs, [[p] for p in parts])) if len(segs) == len(parts) else [(sum(segs), parts)]
    t0, t1 = [], []
    for n, iv in groups:
        tot = sum(b - a for a, b in iv)

        def at(f):
            f *= tot
            for a, b in iv:
                if f <= b - a:
                    return a + f
                f -= b - a
            return iv[-1][1]
        t0 += [at(j / n) for j in range(n)]
        t1 += [at((j + 1) / n) for j in range(n)]
    return t0, t1


def align_json(text, t0, t1, first, last, c0):
    t0, t1 = list(t0), list(t1)
    i, prev = 0, first
    while i < len(t0):
        if t0[i] is not None:
            prev, i = t1[i], i + 1
            continue
        j = i
        while j < len(t0) and t0[j] is None:
            j += 1
        nxt = t0[j] if j < len(t0) else last
        for m in range(i, j):
            t0[m] = prev + (nxt - prev) * (m - i) / (j - i)
            t1[m] = prev + (nxt - prev) * (m - i + 1) / (j - i)
        i = j
    al = {"characters": [], "character_start_times_seconds": [], "character_end_times_seconds": []}
    k, end = 0, first
    for c in text:
        if c.isalnum():
            s, e = t0[k], t1[k]
            k, end = k + 1, e
        else:
            s = e = end
            if c.isspace() and k < len(t0):
                e = max(s, t0[k])
        al["characters"].append(c)
        al["character_start_times_seconds"].append(round(max(0.0, s - c0), 3))
        al["character_end_times_seconds"].append(round(max(0.0, e - c0), 3))
    return al


def write_clip(snd, l, t, out):
    cut(snd, t, out / f"{l['id']}.mp3")
    text = l.get("tts") or l["text"]
    if t.words:
        t0, t1, first, last = heard_times(text, t)
    else:
        parts = [[max(a, t.on), min(b, t.off)] for a, b in snd.runs(0.25) if b > t.on and a < t.off] or [[t.on, t.off]]
        (t0, t1), first, last = spread_times(text, parts), t.on, t.off
    (out / f"{l['id']}.align.json").write_text(json.dumps(align_json(text, t0, t1, first, last, t.c0), ensure_ascii=False))
    r = {"file": f"{l['id']}.mp3", "source": snd.path.name, "method": t.method, "src_start": round(t.c0, 3), "src_end": round(t.c1, 3),
         "dur": round(t.c1 - t.c0, 3), "speech_start": round(t.on - t.c0, 3), "speech_end": round(t.off - t.c0, 3),
         "score": round(t.score, 3), "align": "stt" if t.words else "estimated"}
    if t.words:
        r["stt"] = " ".join(w[0] for w in t.words)
    return r


def pick(lines, takes, junk):
    by = defaultdict(list)
    for t in takes:
        by[t.line].append(t)
    chosen, unused = {}, list(junk)
    for k, ts in by.items():
        ts.sort(key=lambda t: t.s)
        best = max(t.score for t in ts)
        full = [t for t in ts if t.method != "stt" or t.score >= best - FULL_SLACK]
        chosen[k] = (full[-1], full)
        unused += [(t.s, t.e, f"{lines[k]['id']} {full.index(t) + 1}번째 테이크" if t in full else f"{lines[k]['id']} 덜 닮은 테이크(sim {t.score:.2f})")
                   for t in ts if t is not full[-1]]
    return chosen, sorted(unused)


def report(lines, chosen, snd, out, dry, timeline, unused):
    scenes = [x for x in (timeline or {}).get("scenes", []) if isinstance(x.get("start"), (int, float)) and isinstance(x.get("end"), (int, float))]
    if timeline and not scenes:
        die("timeline.json 의 scenes 에 숫자 start/end 가 없다 → timeline.py 를 먼저 실행한다")
    rep = {}
    if not dry:
        out.mkdir(parents=True, exist_ok=True)
        rep = json.loads((out / "report.json").read_text()) if (out / "report.json").exists() else {}
    head = f"{'id':6s} {'테이크':5s} {'원본 말 구간':13s} {'말':>5s} {'근거':9s}"
    print(head + (f" {'시작':>6s} {'끝':>6s} {'앞 틈':>5s} {'여유':>6s}" if timeline else "") + "  원고")
    bad, prev, total = 0, None, 0.0
    for k, l in enumerate(lines):
        if k not in chosen:
            bad += 1
            print(f"{l['id']:6s} ✗ 못 찾음  {l['text']}")
            continue
        t, ts = chosen[k]
        n, sp = ts.index(t) + 1, t.off - t.on
        total += sp
        basis = {"stt": f"sim {t.score:.2f}", "audio": f"z {t.score:.1f}", "manual": "수동"}[t.method]
        row = f"{l['id']:6s} {n}/{len(ts):<3d} {t.on:6.2f}-{t.off:6.2f} {sp:5.2f} {basis:9s}"
        marks = []
        if (t.method == "stt" and t.score < 0.8) or (t.method == "audio" and t.score < THETA_AUDIO + 0.7):
            marks.append("△ 원고와 덜 닮음 → 들어 볼 것")
        at = l.get("at")
        if timeline:
            if isinstance(at, (int, float)) and not isinstance(at, bool):
                start, end = float(at), float(at) + sp
                sc = next((s for s in scenes if s["start"] <= start < s["end"]), None)
                gap = start - prev if prev is not None else start
                room = sc["end"] - GAP_LINE - end if sc else None
                row += f" {start:6.2f} {end:6.2f} {gap:5.2f} " + (f"{room:+6.2f}" if sc else "  장면밖")
                if gap < GAP_LINE:
                    marks.append("✗ 앞 줄과 붙음")
                if sc is None:
                    marks.append("✗ 장면 밖")
                elif room < 0:
                    marks.append("✗ 장면 넘침")
                prev = end
            else:
                row += f" {'':6s} {'':6s} {'':5s} {'':6s}"
        bad += sum(m.startswith("✗") for m in marks)
        print(f"{row}  {l['text'][:22]}" + "".join(f"  {m}" for m in marks))
        if not dry:
            rep[l["id"]] = write_clip(snd, l, t, out)
            if len(ts) > 1:
                rep[l["id"]]["retakes"] = [[round(x.s, 3), round(x.e, 3)] for x in ts if x is not t]
    if not dry:
        (out / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(f"\n말 합계 {total:.1f}s · 줄 {len(chosen)}/{len(lines)}")
    if unused:
        print("쓰지 않은 구간(원본 초)")
        for s, e, why in unused:
            print(f"  {s:6.2f}-{e:6.2f}  {why or '말소리, 어느 줄에도 안 맞음'}")
    if any(t.method == "audio" for t, _ in chosen.values()):
        print("받아쓰기 없이 줄을 맞췄다. 줄 번호는 기준 낭독과 닮은 정도로 정했고 문장 내용이 원고와 같은지는 확인하지 못했다 → 사람이 들어 볼 것")
    print("--dry-run: 클립을 쓰지 않았다" if dry else f"→ {out}")
    return bad


def parse_spans(arg, ids):
    out = {}
    for item in filter(None, (arg or "").split(",")):
        m = re.fullmatch(r"\s*(\w+)\s*=\s*([\d.]+)\s*-\s*([\d.]+)\s*", item)
        if not m or m.group(1) not in ids or float(m.group(2)) >= float(m.group(3)):
            die(f"--spans 형식이 아니다: '{item}' (예: n06=31.2-34.2, id 는 script.json 에 있어야 한다)")
        out[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--script", required=True)
    ap.add_argument("--stt")
    ap.add_argument("--out")
    ap.add_argument("--spans")
    ap.add_argument("--timeline")
    ap.add_argument("--lang", help="기준 낭독 언어(ko, en …). 없으면 원고 글자로 정한다")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    sp = Path(a.script).resolve()
    lines = read_json(sp).get("lines")
    if not lines:
        die("script.json 에 lines 가 없다")
    ids = [l["id"] for l in lines]
    if len(ids) != len(set(ids)):
        die("줄 id 가 중복됐다")
    for l in lines:
        if not norm(l.get("tts") or l.get("text", "")):
            die(f"{l['id']}: 텍스트에 글자가 없다")
    out = Path(a.out) if a.out else sp.parent / "audio" / "vo"
    rec = Path(a.recording).resolve()
    if rec.parent == out.resolve() and rec.stem in ids:
        die("녹음 파일이 클립 이름과 겹친다")
    spans = parse_spans(a.spans, ids)
    if not rec.is_file():
        die(f"녹음 파일이 없다: {rec}")
    snd = Sound(rec)
    print(f"녹음 {snd.dur:.1f}s · 소음 바닥 {snd.floor:.1f} dBFS, 말 문턱 {snd.floor + 12:.1f} dBFS")

    blocked = {"ids": set(spans), "hit": lambda s, e: any(s < y and x < e for x, y in spans.values())}
    if len(spans) == len(lines):
        takes, junk = [], []
    elif a.stt:
        stt = read_json(a.stt)
        takes, junk = stt_takes(stt["words"] if isinstance(stt, dict) else stt, lines, blocked)
    else:
        text = "".join(l["text"] for l in lines)
        lang = a.lang or ("ko" if sum("가" <= c <= "힣" for c in text) > 0.3 * sum(c.isalnum() for c in text) else "en")
        takes, junk = audio_takes(snd, lines, lang, blocked)
    for lid, (s, e) in spans.items():
        takes.append(Take(ids.index(lid), "manual", 0.0, s, e))
    refine(takes, snd)
    chosen, unused = pick(lines, takes, junk)

    timeline = read_json(a.timeline) if a.timeline else None
    bad = report(lines, chosen, snd, out, a.dry_run, timeline, unused)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
