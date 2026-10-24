#!/usr/bin/env python3
"""제작 전 환경 점검. 무엇이 있고 무엇이 없는지, 없으면 어떻게 설치하는지 한 번에 보여 준다.

사용법: preflight.py [--voice ibCGc01503OQd2R6i1n1] [--json]
결과의 '쓸 수 있는 경로'를 콘셉트에 반영한다(예: 나레이션 불가 → 음악·화면만으로 전하는 콘셉트, Music 불가 → 합성 음악).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = Path.home() / ".claude" / "skills"
REPO = "https://github.com/revfactory/skills"


def find_op55():
    if os.environ.get("OP55_SCRIPTS"):
        cands = [Path(os.environ["OP55_SCRIPTS"]).expanduser()]
    else:
        roots = [HERE.parent.parent]
        for d in [Path.cwd(), *Path.cwd().parents]:
            roots += [d / ".claude/skills", d / ".agents/skills"]
        roots += [Path.home() / ".claude/skills", Path.home() / ".agents/skills"]
        cands = [root / "resolve-op55-tools/scripts" for root in roots]
    return next((c.resolve() for c in cands if c.parent.name != "op55" and c.resolve().parent.name != "op55"
                 and all((c / name).is_file()
                 for name in ("render.mjs", "verify.py", "setup.mjs"))), None)


def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 127, str(e)


def op55_version(scripts):
    version_pattern = r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"
    try:
        text = (scripts.parent / "SKILL.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        text = ""
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if frontmatter:
        metadata = re.search(r"(?m)^metadata:[ \t]*\r?\n((?:[ \t]+[^\n]*(?:\n|$)|\r?\n)*)", frontmatter[1])
        if metadata:
            lines = [line for line in metadata[1].splitlines() if line.strip() and not line.lstrip().startswith("#")]
            indent = min((len(line) - len(line.lstrip()) for line in lines), default=0)
            for line in lines:
                name, _, value = line.strip().partition(":")
                value = value.strip().strip("\"'")
                if len(line) - len(line.lstrip()) == indent and name == "version" and re.fullmatch(version_pattern, value):
                    return value
    code, output = run(["node", str(scripts / "render.mjs"), "--version"])
    version = re.fullmatch(r"op55 (" + version_pattern + r")", output)
    return version[1] if code == 0 and version else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="ibCGc01503OQd2R6i1n1")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows, fix, caps = [], [], {}

    def row(name, ok, info, how=None):
        rows.append(("✓" if ok else "✗", name, info))
        if not ok and how:
            fix.append(f"{name}: {how}")

    # 필수 도구
    code, out = run(["node", "--version"])
    row("node", code == 0, out.splitlines()[0] if code == 0 else "없음", "https://nodejs.org 에서 LTS 설치 또는 brew install node")
    code, out = run(["ffmpeg", "-hide_banner", "-filters"])
    has_ff = code == 0
    flt = {f: (f" {f} " in out) for f in ("loudnorm", "ebur128", "tmix", "freezedetect", "signalstats")}
    row("ffmpeg", has_ff and all(flt.values()), "필터 " + ", ".join(k for k, v in flt.items() if v) if has_ff else "없음", "brew install ffmpeg")
    chrome = Path("/Applications/Google Chrome.app").exists() or bool(shutil.which("google-chrome")) or bool(os.environ.get("REEL_CHROME_PATH"))
    row("Chrome", chrome, "시스템 Chrome 사용" if chrome else "없음", "Google Chrome 설치 또는 REEL_CHROME_PATH=<chromium 실행 파일>")
    pw = (HERE / "node_modules" / "playwright-core").exists()
    row("playwright-core", pw, "설치됨" if pw else "없음", f"cd {HERE} && npm install (new_project.py 가 자동으로 한다)")
    try:
        import numpy  # noqa
        import PIL  # noqa
        row("python numpy·Pillow", True, f"python {sys.version.split()[0]}")
    except ImportError as e:
        row("python numpy·Pillow", False, str(e), f"{sys.executable} -m pip install numpy pillow")
    fonts = [p for d in (Path.home() / "Library/Fonts", Path("/Library/Fonts")) if d.exists() for p in d.glob("Pretendard*")]
    row("한글 폰트(Pretendard)", True, "로컬 있음" if fonts else "없음 → new_project.py 가 내려받음")
    swift = bool(shutil.which("swiftc"))
    row("누끼(swiftc, macOS)", swift, "가능" if swift else "불가 — 인물 누끼 없이 진행", "xcode-select --install")
    op55 = find_op55()
    version = op55_version(op55) if op55 else None
    banks = op55 is not None and run(["node", str(op55 / "setup.mjs"), "--check"])[0] == 0
    row("BGM 스킬(op55)", op55 is not None and banks,
        f"{op55} (op55 {version or '버전 미확인'}, 사운드뱅크 {'있음' if banks else '없음'})" if op55 else "없음 또는 지원하지 않는 옛 설치본",
        "npx skills@1.7.4 add ynginkim/op55로 설치. 옛 op55 사본은 npx skills@1.7.4 remove op55로 제거(전역이면 -g)" if op55 is None else f"node {op55}/setup.mjs")
    caps["music"] = str(op55) if op55 else None
    caps["op55_version"] = version

    # 이미지 생성
    code, out = run(["codex", "login", "status"])
    codex_ok = code == 0
    row("codex CLI 로그인", codex_ok, out.splitlines()[0][:60] if out else "없음",
        "npm i -g @openai/codex && codex login (ChatGPT 계정)")
    for sk in ("codex-image", "photoreal", "codex-cli"):
        row(f"스킬 {sk}", (SKILLS / sk / "SKILL.md").exists(), "설치됨" if (SKILLS / sk / "SKILL.md").exists() else "없음",
            f"git clone {REPO}.git ~/src/revfactory-skills && ln -s ~/src/revfactory-skills/{sk} ~/.claude/skills/{sk}")
    caps["image_gen"] = codex_ok and (SKILLS / "codex-image").exists()

    # ElevenLabs
    sys.path.insert(0, str(HERE))
    import eleven
    key = eleven.api_key()
    caps["music_api"] = None if key else False
    if not key:
        row("ElevenLabs API 키", False, "없음", "아래 'ElevenLabs 키 발급' 참고")
        caps["narration"] = False
    else:
        try:
            json.loads(eleven.request("GET", "/v1/models", retries=1))
            row("ElevenLabs API 키", True, "유효")
            try:
                v = json.loads(eleven.request("GET", f"/v1/voices/{a.voice}", retries=1))
                row("점검 보이스(--voice)", True, v.get("name", a.voice)[:50])
                caps["narration"] = True
            except eleven.ElevenError as e:
                row("점검 보이스(--voice)", False, str(e)[:80], "Free 플랜이면 라이브러리 보이스가 막힌다 → 유료 플랜 또는 eleven.py voices 로 다른 보이스")
                caps["narration"] = "other_voice"
            try:
                s = json.loads(eleven.request("GET", "/v1/user/subscription", retries=1))
                left = (s.get("character_limit") or 0) - (s.get("character_count") or 0)
                row("요금제·크레딧", True, f"{s.get('tier')} · 남은 크레딧 {left:,}")
                caps["music_api"] = False if s.get("tier") == "free" else None
            except eleven.ElevenError:
                row("요금제·크레딧", True, "확인 불가 — Music 사용을 선택한 경우에만 생성 시도")
                caps["music_api"] = None
        except eleven.ElevenError as e:
            row("ElevenLabs API 키", False, str(e).splitlines()[0][:80], "키 권한·유효성 확인")
            caps["narration"] = False

    if a.json:
        print(json.dumps({"rows": rows, "fix": fix, "caps": caps}, ensure_ascii=False, indent=1))
        return
    for ok, name, info in rows:
        print(f"{ok} {name:24s} {info}")
    print("\n쓸 수 있는 경로:")
    print(f"  렌더링        {'가능' if all(r[0] == '✓' for r in rows[:4]) else '설치 필요'}")
    print(f"  이미지 생성    {'codex-image (+photoreal)' if caps.get('image_gen') else '불가 → 타이포·그래픽·사용자 제공 사진으로 구성'}")
    n = caps.get("narration")
    print(f"  나레이션      {'ElevenLabs (점검 보이스 사용 가능)' if n is True else '다른 보이스 필요' if n == 'other_voice' else '불가 → 음악·자막 버전'}")
    m = caps.get("music_api")
    print(f"  음악 기본     {'op55 문서·뱅크 확인(O=' + caps['music'] + ')' if caps.get('music') else 'op55 경로 요청 또는 설치 안내'}")
    print(f"  음악 API      {'BYOK 키 없음 또는 Free 플랜, 설정 안내 또는 다른 경로 선택' if m is False else 'BYOK 키 있음, Music 권한·크레딧 미확인. 선택한 경우에만 사용'}")
    print("  음악 fallback 내장 synth_music.py 사용(ffmpeg·numpy 필요), 앞선 두 경로가 실패하거나 사용 불가할 때")
    if fix:
        print("\n고칠 것:")
        for f in fix:
            print("  - " + f)
    if not key:
        print("\nElevenLabs 키 발급:\n" + eleven.KEY_HELP)


if __name__ == "__main__":
    main()
