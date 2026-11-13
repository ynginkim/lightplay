#!/usr/bin/env python3
"""납품 뒤 정리: 다시 안 쓸 작업 파일을 휴지통으로 옮긴다. 규칙은 references/qa.md 의 '납품 뒤 정리'.

사용법
  cleanup.py <프로젝트>                       목록과 크기만 보여 준다(기본, 아무것도 바꾸지 않는다)
  cleanup.py <프로젝트> --apply               '다시 안 쓸 것'을 휴지통으로 옮긴다
  cleanup.py <프로젝트> --apply --followup    '후속 작업용'도 함께 옮긴다
  cleanup.py <프로젝트> --apply --delete      휴지통 대신 바로 지운다(되돌릴 수 없다)
  [--trash-dir <폴더>]                        휴지통 위치(기본 ~/.Trash). 안에 lightplay-cleanup-<프로젝트>-<시각>/ 을 만들고 원래 경로 그대로 옮긴다

파일은 세 갈래 중 하나다. 어느 갈래인지는 아래 RULES 표가 정하고, 위에서부터 처음 맞는 줄이 이긴다.
  남긴다          납품본, 최종 믹스, 영상이 쓰는 음악, 최종 시트, 그 밖에 표가 건드리지 않는 모든 것. 목록에 나오지 않는다.
  후속 작업용     나레이션·음악만 고쳐 다시 마감할 때 쓰는 것(무음 렌더, 렌더 조각, 음악 스템, 녹음 원본). --followup 이 있어야 옮긴다.
  다시 안 쓸 것   초안, 점검 영상, 믹스 스템, 시험 믹스, 안 쓴 음악 테이크, 검수 스틸. --apply 가 옮긴다.

납품본(out/ 의 *_포스터.jpg 와 이름이 같은 파일)이 없으면 아무것도 하지 않는다(--force 로 무시).
"""
import argparse
import json
import os
import re
import shutil
import sys
import time
from collections import namedtuple
from pathlib import Path, PurePosixPath

MEDIA = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
AUDIO = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".aiff", ".aif"}
IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
POSTER = "_포스터.jpg"
MIX_STEMS = ("_premaster.wav", "_vo.wav", "_bed.wav")   # mix.py 가 <최종>.wav 옆에 쓰는 점검용 스템
PIECE_DIRS = (".pieces", ".parts")
TOP_DIRS = ("out", "audio", "qa")                         # 표가 다루는 폴더. 나머지(reel, assets, 문서, json)는 보지 않는다
LIST_LIMIT = 10                                           # 줄(label)마다 보여 주는 경로 수

KEEP, FOLLOWUP, DISCARD = "keep", "followup", "discard"
TITLE = {DISCARD: "다시 안 쓸 것", FOLLOWUP: "후속 작업용"}

# match(p, c): p 는 프로젝트 기준 상대 경로(PurePosixPath), c 는 Project
# unit(p): 목록에서 파일 대신 보여 줄 폴더(렌더 조각처럼 폴더째 한 줄로 읽히는 것). 옮길 때는 언제나 파일 단위다
Rule = namedtuple("Rule", "bucket label match unit", defaults=(None,))
Project = namedtuple("Project", "stems music_keep version_suffixes")


def under(p, *prefix):
    return p.parts[:len(prefix)] == prefix


def is_ext(p, exts):
    return p.suffix.lower() in exts


def in_dir(p, *folder):
    return p.parent.parts == folder


def top_dir(test):
    def unit(p):
        return next((d for d in reversed(p.parents) if test(d)), p)
    return unit


def is_piece_file(p):
    return under(p, "out") and any(part.endswith(PIECE_DIRS) for part in p.parts[1:-1])


def is_mix_stem(p):
    return in_dir(p, "audio") and p.name.endswith(MIX_STEMS)


def is_stem_file(p):
    return under(p, "audio", "music") and is_ext(p, AUDIO) and re.search(r"(?<![a-z])stems?(?![a-z])", p.name.lower())


def is_raw_recording(p):
    return under(p, "audio", "vo_raw") or under(p, "audio", "vo", "raw")


RULES = [
    Rule(KEEP, "납품본", lambda p, c: in_dir(p, "out") and p.name.startswith(c.stems)),
    Rule(KEEP, "영상이 쓰는 음악", lambda p, c: p.as_posix() in c.music_keep),
    Rule(KEEP, "버전 보존 음악", lambda p, c: in_dir(p, "audio", "music") and is_ext(p, AUDIO) and p.stem.endswith(c.version_suffixes)),
    Rule(KEEP, "최종 시트", lambda p, c: under(p, "qa") and p.match("final_sheet*.png")),
    Rule(FOLLOWUP, "무음 렌더", lambda p, c: in_dir(p, "out") and p.match("video*.mp4")),
    Rule(FOLLOWUP, "렌더 조각", lambda p, c: is_piece_file(p), top_dir(lambda d: d.name.endswith(PIECE_DIRS))),
    Rule(FOLLOWUP, "음악 스템", lambda p, c: under(p, "audio", "music", "dbg", "stems") or is_stem_file(p),
         top_dir(lambda d: d.as_posix() == "audio/music/dbg/stems")),
    Rule(FOLLOWUP, "녹음 원본", lambda p, c: is_raw_recording(p),
         top_dir(lambda d: d.as_posix() in ("audio/vo_raw", "audio/vo/raw"))),
    Rule(DISCARD, "out 초안·점검 영상", lambda p, c: under(p, "out") and is_ext(p, MEDIA)),
    Rule(DISCARD, "audio 믹스 스템(mix.py 가 매번 새로 씀)", lambda p, c: is_mix_stem(p)),
    Rule(DISCARD, "audio/music 시험 믹스(verify)", lambda p, c: under(p, "audio", "music", "verify") and is_ext(p, AUDIO)),
    Rule(KEEP, "음악 참조가 없는 프로젝트의 음악(뭐가 안 쓰이는지 알 수 없다)",
         lambda p, c: not c.music_keep and under(p, "audio", "music") and is_ext(p, AUDIO)),
    Rule(DISCARD, "audio/music 안 쓴 테이크", lambda p, c: under(p, "audio", "music") and is_ext(p, AUDIO)),
    Rule(DISCARD, "qa 스틸·시트·클립", lambda p, c: under(p, "qa") and is_ext(p, MEDIA | AUDIO | IMAGE)),
    Rule(DISCARD, "x264 2패스 임시 파일(*.mbtree)", lambda p, c: p.suffix == ".mbtree"),
    Rule(KEEP, "그대로 둔다(최종 믹스 audio/mix*.wav, reel, assets, audio/vo·sfx, 문서, json 등)", lambda p, c: True),
]

Item = namedtuple("Item", "rule rel size")


def referenced_music(root):
    keep = set()
    docs = [f for pattern in ("script*.json", "timeline*.json", "versions/*/script*.json", "versions/*/timeline*.json")
            for f in root.glob(pattern)]
    for doc in sorted(docs):
        try:
            data = json.loads(doc.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.exit(f"{doc.relative_to(root)} 을 읽지 못했다({e}). 어떤 음악을 쓰는지 알 수 없어 정리하지 않는다.")
        music = data.get("music") if isinstance(data, dict) else None
        name = music.get("file") if isinstance(music, dict) else None
        if isinstance(name, str) and name:
            for base in (root, doc.parent):
                try:
                    keep.add(Path(os.path.normpath(base / name)).relative_to(root).as_posix())
                except ValueError:
                    pass
    return keep


def load_project(root):
    out = root / "out"
    stems = tuple(sorted(f.name[:-len(POSTER)] for f in out.glob(f"*{POSTER}"))) if out.is_dir() else ()
    versions = root / "versions"
    names = sorted(d.name for d in versions.iterdir() if d.is_dir()) if versions.is_dir() else []
    return Project(stems, referenced_music(root), tuple(f"_{n}" for n in names))


def scan(root, project):
    items = []
    for top in TOP_DIRS:
        for base, dirs, files in os.walk(root / top):
            dirs.sort()
            for name in sorted(files):
                f = Path(base, name)
                if f.is_symlink():
                    continue
                rel = PurePosixPath(f.relative_to(root).as_posix())
                rule = next(r for r in RULES if r.match(rel, project))
                if rule.bucket != KEEP:
                    items.append(Item(rule, rel, f.stat().st_size))
    return items


def human(n):
    return f"{n / 1073741824:7.2f}GB" if n >= 1073741824 else f"{n / 1048576:7.1f}MB"


def show(items, stems):
    for bucket, hint in ((DISCARD, "--apply 가 옮긴다"), (FOLLOWUP, "--apply --followup 이 옮긴다")):
        group = [i for i in items if i.rule.bucket == bucket]
        if not group:
            continue
        print(f"{TITLE[bucket]} · {human(sum(i.size for i in group)).strip()} · {len(group)}개 ({hint})")
        for rule in RULES:
            mine = [i for i in group if i.rule is rule]
            if not mine:
                continue
            print(f"  {rule.label} · {len(mine)}개 · {human(sum(i.size for i in mine)).strip()}")
            units = {}
            for i in mine:
                units.setdefault(rule.unit(i.rel) if rule.unit else i.rel, []).append(i)
            shown = list(units.items())
            for u, files in shown[:LIST_LIMIT]:
                print(f"      {u}" + (f"/  ({len(files)}개)" if u != files[0].rel else ""))
            if len(shown) > LIST_LIMIT:
                print(f"      … 외 {sum(len(files) for _, files in shown[LIST_LIMIT:])}개")
    if not items:
        print("옮길 것이 없다.")
    print(f"남기는 납품본: {', '.join(stems) or '(없음)'}")


def main():
    ap = argparse.ArgumentParser(description="납품 뒤 정리. 기본은 목록만 보여 준다.")
    ap.add_argument("project")
    ap.add_argument("--apply", action="store_true", help="'다시 안 쓸 것'을 휴지통으로 옮긴다")
    ap.add_argument("--followup", action="store_true", help="--apply 와 함께: '후속 작업용'도 옮긴다")
    ap.add_argument("--delete", action="store_true", help="--apply 와 함께: 휴지통 대신 바로 지운다")
    ap.add_argument("--trash-dir", help="휴지통 위치(기본 ~/.Trash)")
    ap.add_argument("--force", action="store_true", help="납품본이 없어도 진행한다")
    a = ap.parse_args()
    if (a.followup or a.delete) and not a.apply:
        ap.error("--followup, --delete 는 --apply 와 같이 쓴다")
    if a.delete and a.trash_dir:
        ap.error("--delete 는 휴지통을 쓰지 않으니 --trash-dir 와 같이 쓸 수 없다")
    root = Path(a.project).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"프로젝트 폴더가 아니다: {root}")

    project = load_project(root)
    if not project.stems and not a.force:
        sys.exit("납품본(out/*_포스터.jpg)이 없다. 납품 전이면 정리하지 않는다(--force 로 무시).")
    items = scan(root, project)
    show(items, project.stems)
    if not a.apply:
        print("목록만 보였다. 옮기려면 --apply (후속 작업용까지는 --apply --followup, 바로 지우려면 --delete 를 더한다)")
        return

    chosen = [i for i in items if i.rule.bucket == DISCARD or (a.followup and i.rule.bucket == FOLLOWUP)]
    left = [] if a.followup else [i for i in items if i.rule.bucket == FOLLOWUP]
    total = human(sum(i.size for i in chosen)).strip()
    dest = None
    if chosen and not a.delete:
        trash = Path(a.trash_dir).expanduser() if a.trash_dir else Path.home() / ".Trash"
        dest = trash / f"lightplay-cleanup-{root.name}-{time.strftime('%Y%m%d-%H%M%S')}"
        try:
            dest.mkdir(parents=True)
        except OSError as e:
            sys.exit(f"휴지통을 쓸 수 없다({e}). --trash-dir 로 다른 폴더를 주거나 --delete 를 쓴다.")
    moved = 0
    for i in chosen:
        src = root / i.rel
        try:
            if dest:
                target = dest / i.rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(target))
            else:
                src.unlink()
        except OSError as e:
            sys.exit(f"{i.rel} 을 처리하지 못했다({e}). {moved}개를 처리했다. 같은 명령을 다시 돌리면 나머지를 이어서 한다.")
        moved += 1
    dirs = {root / d for i in chosen for d in i.rel.parents if len(d.parts) >= 2}
    for d in sorted(dirs, key=lambda d: len(d.parts), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    if chosen:
        print(f"{'휴지통으로 옮겼다 → ' + str(dest) if dest else '지웠다'} · {total} · {moved}개")
    elif items:
        print("옮긴 것이 없다.")
    if left:
        print(f"남겼다: 후속 작업용 {len(left)}개 · {human(sum(i.size for i in left)).strip()} (같이 옮기려면 --followup)")


if __name__ == "__main__":
    main()
