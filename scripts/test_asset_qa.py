#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "skills/resolve-showreel-tools/scripts"
GOLDEN = ROOT / "tests/asset/golden"
sys.path.insert(0, str(TOOLS))

try:
    import numpy as np
    from PIL import Image
except ImportError:
    print("SKIP: numpy and Pillow are required")
    sys.exit(0)

import asset_qa as qa

EXPECTED = json.loads((GOLDEN / "expected.json").read_text())
CHECKS = {
    "players": lambda d: qa.check_players(str(GOLDEN / d[0]), str(GOLDEN / d[1])),
    "routes": lambda d: qa.check_routes(str(GOLDEN / d[0]), str(GOLDEN / d[1])),
    "loop": lambda d: qa.check_loop(str(GOLDEN / d[0])),
}


def dig(d, path):
    for k in path.split("."):
        d = d[k]
    return d


def write_frames(d, arrays, start=0):
    d.mkdir(parents=True, exist_ok=True)
    for k, a in enumerate(arrays):
        Image.fromarray(a, "RGBA").save(d / f"f{start + k:05d}.png")


def blank(w=64, h=64):
    return np.zeros((h, w, 4), np.uint8)


def square(x, w=64, h=64):
    a = blank(w, h)
    a[20:40, x:x + 12] = (200, 40, 40, 255)
    return a


class GoldenNumbers(unittest.TestCase):
    def test_numbers_match_spike_measurements(self):
        for name, c in EXPECTED["numeric"].items():
            with self.subTest(name):
                _, data = CHECKS[c["cmd"]](c["args"])
                self.assertAlmostEqual(dig(data, c["path"]), c["value"], delta=c["tol"])

    def test_player_verdicts(self):
        self.assertEqual(qa.check_players(str(GOLDEN / "01-textlayer/dotlottie"), str(GOLDEN / "01-textlayer/lottieweb"))[0].status, qa.FAIL)
        self.assertEqual(qa.check_players(str(GOLDEN / "01-builder/dotlottie"), str(GOLDEN / "01-builder/lottieweb"))[0].status, qa.OK)

    def test_routes_flags_edge_saturation_but_not_centre(self):
        row, data = qa.check_routes(str(GOLDEN / "04-pair/dotlottie"), str(GOLDEN / "04-pair/engine"))
        self.assertEqual(row.status, qa.WARN)
        self.assertIn("채도", row.fix)
        self.assertGreater(data["saturation_A_minus_B"]["가장자리"], 0.015)
        self.assertLess(abs(data["saturation_A_minus_B"]["가운데"]), 0.002)


class Ink(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.frames = self.tmp / "idle"
        shutil.copytree(GOLDEN / "02-idle", self.frames)

    def test_clean_idle_has_ink(self):
        self.assertEqual(qa.check_ink(str(self.frames))[0].status, qa.OK)

    def test_injected_blank_frame_fails_and_names_the_frame(self):
        Image.fromarray(blank(256, 256), "RGBA").save(self.frames / "f00090.png")
        row, data = qa.check_ink(str(self.frames))
        self.assertEqual(row.status, qa.FAIL)
        self.assertEqual(data["blank_interior"], [90])
        self.assertIn("f90", row.line)

    def test_leading_blank_frame_is_a_warning(self):
        Image.fromarray(blank(256, 256), "RGBA").save(self.frames / "f00060.png")
        self.assertEqual(qa.check_ink(str(self.frames))[0].status, qa.WARN)

    def test_broken_lottie_rendered_empty_fails_with_cause(self):
        empty = self.tmp / "empty"
        write_frames(empty, [blank()] * 5)
        broken = self.tmp / "broken.json"
        broken.write_text(json.dumps({"v": "5.7.0", "fr": 60, "ip": 0, "op": 30, "w": 64, "h": 64, "layers": []}))
        row, data = qa.check_ink(str(empty), str(broken))
        self.assertEqual(row.status, qa.FAIL)
        self.assertIn("layers", row.line)
        self.assertEqual(len(data["blank_frames"]), 5)

    def test_cli_exits_nonzero_on_blank_frames(self):
        empty = self.tmp / "empty"
        write_frames(empty, [blank()] * 5)
        r = subprocess.run([sys.executable, str(TOOLS / "asset_qa.py"), "ink", str(empty)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("✗", r.stdout)


class MotionAndLoop(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_idle_moves_and_frozen_copy_fails(self):
        self.assertEqual(qa.check_motion(str(GOLDEN / "02-idle"))[0].status, qa.OK)
        frozen = self.tmp / "frozen"
        frozen.mkdir()
        for i in range(60, 120):
            shutil.copy(GOLDEN / "02-idle/f00060.png", frozen / f"f{i:05d}.png")
        self.assertEqual(qa.check_motion(str(frozen))[0].status, qa.FAIL)

    def test_loop_seam_on_a_cycle_and_on_a_truncated_cycle(self):
        cycle = [square(int(26 + 24 * np.cos(2 * np.pi * k / 24))) for k in range(24)]
        write_frames(self.tmp / "full", cycle)
        write_frames(self.tmp / "cut", cycle[:18])
        self.assertEqual(qa.check_loop(str(self.tmp / "full"))[0].status, qa.OK)
        self.assertEqual(qa.check_loop(str(self.tmp / "cut"))[0].status, qa.FAIL)

    def test_golden_loop_is_seamless(self):
        self.assertEqual(qa.check_loop(str(GOLDEN / "04-loop"))[0].status, qa.OK)


class MarkersAndThemes(unittest.TestCase):
    def test_marker_boundary_poses_match(self):
        row, data = qa.check_markers(str(GOLDEN / "02-markers/send-icon.json"), str(GOLDEN / "02-markers"))
        self.assertEqual(row.status, qa.OK)
        diffs = {(p["a"], p["b"]): p["diff"] for p in data["pairs"]}
        self.assertEqual(diffs[(59, 60)], 0.0)
        self.assertEqual(diffs[(60, 180)], 0.0)

    def test_marker_jump_is_flagged(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        shutil.copytree(GOLDEN / "02-markers", tmp / "m")
        shutil.copy(GOLDEN / "02-themes/dark/f00060.png", tmp / "m/f00059.png")
        self.assertEqual(qa.check_markers(str(tmp / "m/send-icon.json"), str(tmp / "m"))[0].status, qa.FAIL)

    def test_themes_differ_and_a_missing_theme_is_caught(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        names = ["light", "dark", "brand"]
        row, data = qa.check_themes([(n, str(GOLDEN / "02-themes" / n)) for n in names], str(tmp / "sheet.png"))
        self.assertEqual(row.status, qa.OK)
        self.assertEqual(len(data["pairs"]), 3)
        with Image.open(tmp / "sheet.png") as sheet:
            self.assertGreater(sheet.height, 3 * 100)
        row, _ = qa.check_themes([("light", str(GOLDEN / "02-themes/light")), ("dark", str(GOLDEN / "02-themes/light"))])
        self.assertEqual(row.status, qa.FAIL)


class ReportAndEncode(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_report_prints_one_line_per_check_and_a_fix_list(self):
        r = subprocess.run([sys.executable, str(TOOLS / "asset_qa.py"), "report", "--dir", str(GOLDEN / "01-textlayer/dotlottie"),
                            "--lottie-web", str(GOLDEN / "01-textlayer/lottieweb")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("✗ 플레이어 차이", r.stdout)
        self.assertIn("고칠 것:", r.stdout)

    def test_webm_and_mp4_carry_bt709_tags(self):
        out = self.tmp / "x"
        r = subprocess.run([sys.executable, str(TOOLS / "encode_asset.py"), str(GOLDEN / "02-idle"), "--name", str(out), "--fps", "60",
                            "--formats", "gif,webm,mp4"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for ext in ("webm", "mp4"):
            p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=color_space,color_primaries,color_transfer,color_range",
                                "-of", "json", f"{out}.{ext}"], capture_output=True, text=True, check=True)
            s = json.loads(p.stdout)["streams"][0]
            self.assertEqual((s["color_space"], s["color_primaries"], s["color_transfer"], s["color_range"]), ("bt709", "bt709", "bt709", "tv"), ext)
        with Image.open(f"{out}.gif") as gif:
            self.assertLessEqual(gif.width, 480)


if __name__ == "__main__":
    unittest.main()
