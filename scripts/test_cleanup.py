#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata
import unittest

sys.dont_write_bytecode = True
CLEANUP = Path(__file__).resolve().parents[1] / "skills/resolve-showreel-tools/scripts/cleanup.py"

KEEP, FOLLOWUP, DISCARD = "keep", "followup", "discard"

# 가짜 프로젝트의 파일마다, 정리가 어느 갈래로 다뤄야 하는지(요구사항). 파일 내용은 경로 문자열이다.
FIXTURE = {
    "out/demo_60s.mp4": KEEP,
    "out/demo_60s_공유용.mp4": KEEP,
    "out/demo_60s_포스터.jpg": KEEP,
    "out/demo_60s.srt": KEEP,
    "out/demo_60s_readme.mp4": KEEP,
    "out/draft_render.log": KEEP,
    "audio/mix.wav": KEEP,
    "audio/mix_60s_en.wav": KEEP,
    "audio/mix_60s_ko.wav": KEEP,
    "audio/vo/n01.wav": KEEP,
    "audio/vo_en/n01.wav": KEEP,
    "audio/sfx/hit.wav": KEEP,
    "audio/music/music.wav": KEEP,            # script.json 이 가리킨다
    "audio/music/for_timeline.wav": KEEP,     # timeline_ko.json 만 가리킨다
    "audio/music/alt.wav": KEEP,              # versions/alt/script.json 이 가리킨다
    "audio/music/music_54s.wav": KEEP,        # versions/54s/ 가 있으니 그 판의 음악이다
    "audio/music/score.mjs": KEEP,
    "audio/music/analysis.json": KEEP,
    "audio/music/verify/hits_waveform.png": KEEP,
    "qa/final_sheet_01.png": KEEP,
    "qa/qa_en/final_sheet_02.png": KEEP,
    "qa/critique_01.md": KEEP,
    "reel/scene.js": KEEP,
    "assets/photo.png": KEEP,
    "제작노트.md": KEEP,
    "script.json": KEEP,
    "timeline_ko.json": KEEP,
    "versions/54s/script.json": KEEP,
    "versions/alt/script.json": KEEP,

    "out/video_en.mp4": FOLLOWUP,
    "out/video_en.pieces/p1.mp4": FOLLOWUP,
    "out/video_en.pieces/concat.txt": FOLLOWUP,
    "out/video_ko.parts/p1.mp4": FOLLOWUP,
    "audio/music/dbg/stems/stem_kick.wav": FOLLOWUP,
    "audio/music/dbg/stems/stem_pad.wav": FOLLOWUP,
    "audio/music/take_stem.wav": FOLLOWUP,
    "audio/vo_raw/ko.m4a": FOLLOWUP,
    "audio/vo/raw/en.m4a": FOLLOWUP,

    "out/draft1.mp4": DISCARD,
    "out/chk_s02.mp4": DISCARD,
    "audio/mix_premaster.wav": DISCARD,
    "audio/mix_vo.wav": DISCARD,
    "audio/mix_bed.wav": DISCARD,
    "audio/mix_60s_en_premaster.wav": DISCARD,
    "audio/mix_60s_en_vo.wav": DISCARD,
    "audio/mix_60s_en_bed.wav": DISCARD,
    "audio/music/verify/mix_test.wav": DISCARD,
    "audio/music/verify/mix_en/mix_test_bed.wav": DISCARD,
    "audio/music/take2.wav": DISCARD,
    "audio/music/music_55s.wav": DISCARD,
    "audio/music/dbg/full.wav": DISCARD,
    "qa/sheet_a.png": DISCARD,
    "qa/clip.mp4": DISCARD,
    "qa/final_audio.mp3": DISCARD,
    "qa/vo/mix_test.wav": DISCARD,
    "qa/readme/x264_en-0.log.mbtree": DISCARD,
}
DOCS = {
    "script.json": {"music": {"file": "audio/music/music.wav"}},
    "timeline_ko.json": {"music": {"file": "audio/music/for_timeline.wav"}},
    "versions/54s/script.json": {"music": {"file": "audio/music/music.wav"}},
    "versions/alt/script.json": {"music": {"file": "audio/music/alt.wav"}},
}


def paths(*buckets):
    return {p for p, b in FIXTURE.items() if b in buckets}


class CleanupTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.project = self.root / "demo"
        self.trash = self.root / "trash"
        self.home = self.root / "home"
        self.home.mkdir()
        for rel in FIXTURE:
            self.write(rel, json.dumps(DOCS[rel]) if rel in DOCS else rel)

    def write(self, rel, text):
        f = self.project / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")

    def cli(self, *args):
        env = {**os.environ, "HOME": str(self.home)}
        return subprocess.run([sys.executable, "-B", str(CLEANUP), str(self.project), *args],
                              capture_output=True, text=True, env=env, timeout=60)

    def files(self, base):
        return {unicodedata.normalize("NFC", f.relative_to(base).as_posix())
                for f in base.rglob("*") if f.is_file()}

    def trashed(self):
        dests = list(self.trash.iterdir())
        self.assertEqual(len(dests), 1, dests)
        self.assertTrue(dests[0].name.startswith("lightplay-cleanup-demo-"), dests[0].name)
        return dests[0]

    def test_listing_changes_nothing_and_names_only_the_two_buckets(self):
        before = self.files(self.project)
        r = self.cli()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.files(self.project), before)
        self.assertFalse(self.trash.exists())
        self.assertFalse(any(self.home.iterdir()))
        shown = r.stdout.split()
        for p in paths(KEEP):
            self.assertNotIn(p, shown)
        for p in paths(FOLLOWUP, DISCARD):
            self.assertTrue(any(p == t or (t.endswith("/") and p.startswith(t)) for t in shown), p)
        self.assertLess(r.stdout.index("다시 안 쓸 것"), r.stdout.index("후속 작업용"))

    def test_apply_moves_only_discard_to_trash_keeping_relative_paths(self):
        r = self.cli("--apply", "--trash-dir", str(self.trash))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dest = self.trashed()
        self.assertEqual(self.files(dest), paths(DISCARD))
        self.assertEqual(self.files(self.project), paths(KEEP, FOLLOWUP))
        for p in paths(DISCARD):
            self.assertEqual((dest / p).read_text(encoding="utf-8"), p)

    def test_followup_moves_the_second_bucket_and_leaves_no_empty_folders(self):
        r = self.cli("--apply", "--followup", "--trash-dir", str(self.trash))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.files(self.trashed()), paths(DISCARD, FOLLOWUP))
        self.assertEqual(self.files(self.project), paths(KEEP))
        for gone in ("out/video_en.pieces", "out/video_ko.parts", "audio/music/dbg", "audio/vo_raw", "audio/vo/raw", "qa/vo"):
            self.assertFalse((self.project / gone).exists(), gone)

    def test_delete_removes_without_a_trash_folder(self):
        r = self.cli("--apply", "--delete")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.files(self.project), paths(KEEP, FOLLOWUP))
        self.assertFalse(any(self.home.iterdir()))
        r = self.cli("--apply", "--followup", "--delete")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.files(self.project), paths(KEEP))

    def test_default_trash_is_home_dot_trash(self):
        r = self.cli("--apply")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dests = list((self.home / ".Trash").iterdir())
        self.assertEqual(len(dests), 1)
        self.assertEqual(self.files(dests[0]), paths(DISCARD))

    def test_second_run_finds_nothing_to_move(self):
        self.assertEqual(self.cli("--apply", "--followup", "--trash-dir", str(self.trash)).returncode, 0)
        r = self.cli("--apply", "--followup", "--trash-dir", str(self.trash))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("옮길 것이 없다", r.stdout)
        self.trashed()

    def test_no_deliverable_refuses_until_forced(self):
        (self.project / "out/demo_60s_포스터.jpg").unlink()
        before = self.files(self.project)
        for args in ((), ("--apply", "--trash-dir", str(self.trash))):
            r = self.cli(*args)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("납품본", r.stderr)
        self.assertEqual(self.files(self.project), before)
        r = self.cli("--apply", "--force", "--trash-dir", str(self.trash))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.project / "out/draft1.mp4").exists())

    def test_followup_and_delete_need_apply_and_delete_has_no_trash_folder(self):
        before = self.files(self.project)
        for args in (("--followup",), ("--delete",), ("--apply", "--delete", "--trash-dir", str(self.trash))):
            self.assertEqual(self.cli(*args).returncode, 2, args)
        self.assertEqual(self.files(self.project), before)

    def test_unreadable_script_stops_before_anything_moves(self):
        self.write("script.json", "{")
        before = self.files(self.project)
        r = self.cli("--apply", "--trash-dir", str(self.trash))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("script.json", r.stderr)
        self.assertEqual(self.files(self.project), before)

    def test_unusable_trash_moves_nothing(self):
        (self.root / "not_a_folder").write_text("file")
        before = self.files(self.project)
        r = self.cli("--apply", "--trash-dir", str(self.root / "not_a_folder"))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.files(self.project), before)

    def test_music_is_kept_when_nothing_says_which_music_is_used(self):
        for doc in DOCS:
            (self.project / doc).unlink()
        r = self.cli("--apply", "--followup", "--trash-dir", str(self.trash))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        unjudged = {"audio/music/music.wav", "audio/music/for_timeline.wav", "audio/music/alt.wav", "audio/music/music_54s.wav",
                    "audio/music/take2.wav", "audio/music/music_55s.wav", "audio/music/dbg/full.wav"}
        left = self.files(self.project)
        self.assertLessEqual(unjudged, left)
        self.assertFalse({"audio/music/verify/mix_test.wav", "audio/music/dbg/stems/stem_kick.wav", "audio/music/take_stem.wav"} & left)

    def test_long_lists_are_capped_but_totals_stay_complete(self):
        for n in range(200):
            self.write(f"qa/still_{n:03}.png", "x")
        r = self.cli()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(f"{len(paths(DISCARD)) + 200}개", r.stdout)
        self.assertLess(len(r.stdout.splitlines()), 60)
        self.assertIn("…", r.stdout)


if __name__ == "__main__":
    unittest.main()
