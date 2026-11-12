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
    from PIL import Image, ImageSequence
except ImportError:
    print("SKIP: numpy and Pillow are required")
    sys.exit(0)

import asset_qa as qa

EXPECTED = json.loads((GOLDEN / "expected.json").read_text())
CHECKS = {
    "players": lambda d: qa.check_players(str(GOLDEN / d[0]), str(GOLDEN / d[1])),
    "routes": lambda d: qa.check_routes(str(GOLDEN / d[0]), str(GOLDEN / d[1])),
}


def dig(d, path):
    for k in path.split("."):
        d = d[k]
    return d


def write_frames(d, arrays, numbers=None):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    for k, a in zip(numbers if numbers is not None else range(len(arrays)), arrays):
        Image.fromarray(a, "RGBA").save(d / f"f{k:05d}.png")
    return d


def blank(w=64, h=64):
    return np.zeros((h, w, 4), np.uint8)


def square(x, w=64, h=64, color=(200, 40, 40, 255)):
    a = blank(w, h)
    a[20:40, x:x + 12] = color
    return a


def opaque(w=64, h=64, grey=40):
    a = np.full((h, w, 4), grey, np.uint8)
    a[..., 3] = 255
    return a


def pad(a, w=1920, h=1080):
    out = np.zeros((h, w, 4), np.uint8)
    out[:a.shape[0], :a.shape[1]] = a
    return out


def golden_frames(sub):
    return [np.asarray(Image.open(p).convert("RGBA")) for p in sorted((GOLDEN / sub).glob("f*.png"))]


def cli(*args):
    r = subprocess.run([sys.executable, str(TOOLS / "asset_qa.py"), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)


class GoldenNumbers(unittest.TestCase):
    def test_numbers_match_spike_measurements(self):
        for name, c in EXPECTED["numeric"].items():
            with self.subTest(name):
                _, data = CHECKS[c["cmd"]](c["args"])
                self.assertAlmostEqual(dig(data, c["path"]), c["value"], delta=c["tol"])

    def test_spike_cases_calibration(self):
        text, build = (GOLDEN / "01-textlayer/dotlottie", GOLDEN / "01-builder/dotlottie")
        self.assertEqual(qa.check_players(str(text), str(GOLDEN / "01-textlayer/lottieweb"))[0].status, qa.FAIL)
        self.assertEqual(qa.check_players(str(build), str(GOLDEN / "01-builder/lottieweb"))[0].status, qa.OK)

    def test_routes_flags_edge_saturation_but_not_centre(self):
        row, data = qa.check_routes(str(GOLDEN / "04-pair/dotlottie"), str(GOLDEN / "04-pair/engine"))
        self.assertEqual(row.status, qa.WARN)
        self.assertIn("채도", row.fix)
        self.assertGreater(data["saturation_A_minus_B"]["가장자리"], 0.015)
        self.assertLess(abs(data["saturation_A_minus_B"]["가운데"]), 0.002)


class ContentAreaVerdicts(Tmp):
    def test_padding_onto_a_big_canvas_does_not_flip_a_failing_pair(self):
        for pl in ("dotlottie", "lottieweb"):
            write_frames(self.tmp / pl, [pad(a) for a in golden_frames(f"01-textlayer/{pl}")[:6]])
        self.assertEqual(qa.check_players(str(self.tmp / "dotlottie"), str(self.tmp / "lottieweb"))[0].status, qa.FAIL)

    def test_padding_idle_onto_1080p_still_moves(self):
        write_frames(self.tmp / "idle", [pad(a) for a in golden_frames("02-idle")[:30]], range(60, 90))
        self.assertEqual(qa.check_motion(str(self.tmp / "idle"))[0].status, qa.OK)

    def test_one_wrong_frame_in_480_fails_players(self):
        base = [square(2 + k % 40) for k in range(480)]
        bad = list(base)
        bad[200] = square(2, color=(10, 200, 10, 255))
        bad[200][:, :, :3] = 255 - bad[200][:, :, :3]
        write_frames(self.tmp / "a", base)
        write_frames(self.tmp / "b", bad)
        row, data = qa.check_players(str(self.tmp / "a"), str(self.tmp / "b"))
        self.assertEqual(row.status, qa.FAIL)
        self.assertIn("f200", row.line)

    def test_small_accent_change_is_still_a_theme(self):
        light = golden_frames("02-themes/light")
        accent = []
        for a in light:
            b = a.copy()
            ys, xs = np.nonzero(b[..., 3] > 200)
            b[ys[:12], xs[:12], :3] = 255 - b[ys[:12], xs[:12], :3]
            accent.append(b)
        write_frames(self.tmp / "light", light)
        write_frames(self.tmp / "accent", accent)
        write_frames(self.tmp / "same", light)
        self.assertEqual(qa.check_themes([("light", str(self.tmp / "light")), ("accent", str(self.tmp / "accent"))])[0].status, qa.OK)
        self.assertEqual(qa.check_themes([("light", str(self.tmp / "light")), ("same", str(self.tmp / "same"))])[0].status, qa.FAIL)


class FrameSetIntegrity(Tmp):
    def test_missing_frames_fail_with_numbers(self):
        write_frames(self.tmp / "a", [square(2 + k) for k in range(3)])
        write_frames(self.tmp / "b", [square(2)])
        for fn in (qa.check_players, qa.check_routes):
            row, _ = fn(str(self.tmp / "a"), str(self.tmp / "b"))
            self.assertEqual(row.status, qa.FAIL)
            self.assertIn("f1-f2", row.line)

    def test_common_flag_compares_the_overlap_and_says_so(self):
        write_frames(self.tmp / "a", [square(2 + k) for k in range(4)])
        write_frames(self.tmp / "b", [square(2), square(4)], [0, 2])
        write_frames(self.tmp / "c", [square(2 + k) for k in range(4)])
        row, _ = qa.check_players(str(self.tmp / "a"), str(self.tmp / "b"), common_only=True)
        self.assertIn("공통 2/4", row.line)
        self.assertEqual(qa.check_players(str(self.tmp / "a"), str(self.tmp / "c"))[0].status, qa.OK)

    def test_different_frame_sizes_exit_2(self):
        write_frames(self.tmp / "a", [blank(32, 32), blank(32, 1), blank(32, 32)])
        code, _, err = cli("ink", self.tmp / "a")
        self.assertEqual(code, 2)
        self.assertIn("크기", err)
        write_frames(self.tmp / "b", [square(2)])
        write_frames(self.tmp / "c", [square(2, 48, 48)])
        self.assertEqual(cli("players", self.tmp / "b", self.tmp / "c")[0], 2)

    def test_themes_with_no_common_frames_fail_not_nan(self):
        write_frames(self.tmp / "light", [square(2)], [0])
        write_frames(self.tmp / "dark", [square(4)], [1])
        row, _ = qa.check_themes([("light", str(self.tmp / "light")), ("dark", str(self.tmp / "dark"))], str(self.tmp / "s.png"))
        self.assertEqual(row.status, qa.FAIL)

    def test_themes_with_three_frames_keep_the_last_one(self):
        write_frames(self.tmp / "a", [square(2)] * 3)
        write_frames(self.tmp / "b", [square(2), square(2), square(30)])
        row, data = qa.check_themes([("a", str(self.tmp / "a")), ("b", str(self.tmp / "b"))])
        self.assertEqual(row.status, qa.OK)
        self.assertEqual(data["frames"], [0, 1, 2])

    def test_grid_larger_than_the_image_exits_2(self):
        write_frames(self.tmp / "a", [opaque(4, 4)])
        write_frames(self.tmp / "b", [opaque(4, 4, 50)])
        self.assertEqual(cli("routes", self.tmp / "a", self.tmp / "b")[0], 2)
        self.assertEqual(cli("routes", self.tmp / "a", self.tmp / "b", "--grid", 2)[0], 2)

    def test_theme_arguments_are_validated(self):
        write_frames(self.tmp / "a", [square(2)])
        self.assertEqual(cli("themes", f"light={self.tmp / 'a'}")[0], 2)
        self.assertEqual(cli("themes", f"light={self.tmp / 'a'}", str(self.tmp / "a"))[0], 2)

    def test_alpha_on_one_side_only_is_reported(self):
        write_frames(self.tmp / "a", [square(2 + k) for k in range(3)])
        write_frames(self.tmp / "b", [square(2 + k) for k in range(3)])
        for k in range(3):
            Image.fromarray(composite_grey(square(2 + k)), "RGBA").save(self.tmp / "b" / f"f{k:05d}.png")
        row, _ = qa.check_players(str(self.tmp / "a"), str(self.tmp / "b"))
        self.assertIn("알파", row.line)
        self.assertNotEqual(row.status, qa.OK)


def composite_grey(a):
    alpha = a[..., 3:4] / 255.0
    out = a.copy()
    out[..., :3] = (a[..., :3] * alpha + 128 * (1 - alpha)).astype(np.uint8)
    out[..., 3] = 255
    return out


class Ink(Tmp):
    def setUp(self):
        super().setUp()
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

    def test_one_transparent_pixel_does_not_make_a_white_frame_ink(self):
        a = np.full((32, 32, 4), 255, np.uint8)
        a[0, 0, 3] = 0
        write_frames(self.tmp / "white", [a] * 4)
        self.assertEqual(qa.check_ink(str(self.tmp / "white"))[0].status, qa.FAIL)

    def test_broken_lottie_rendered_empty_fails_with_cause(self):
        write_frames(self.tmp / "empty", [blank()] * 5)
        broken = self.tmp / "broken.json"
        broken.write_text(json.dumps({"v": "5.7.0", "fr": 60, "ip": 0, "op": 30, "w": 64, "h": 64, "layers": []}))
        row, data = qa.check_ink(str(self.tmp / "empty"), str(broken))
        self.assertEqual(row.status, qa.FAIL)
        self.assertIn("layers", row.line)
        self.assertEqual(len(data["blank_frames"]), 5)


class MotionAndLoop(Tmp):
    def test_idle_moves_and_frozen_copy_fails(self):
        self.assertEqual(qa.check_motion(str(GOLDEN / "02-idle"))[0].status, qa.OK)
        frozen = self.tmp / "frozen"
        frozen.mkdir()
        for i in range(60, 120):
            shutil.copy(GOLDEN / "02-idle/f00060.png", frozen / f"f{i:05d}.png")
        self.assertEqual(qa.check_motion(str(frozen))[0].status, qa.FAIL)

    def test_sparse_capture_uses_frame_numbers(self):
        write_frames(self.tmp / "s", [square(2), square(2), square(2), square(30)], [0, 60, 120, 180])
        row, data = qa.check_motion(str(self.tmp / "s"))
        self.assertEqual(row.status, qa.WARN)
        self.assertEqual(data["longest_static_run"], 120)

    def test_loop_seam_on_a_cycle_and_on_a_truncated_cycle(self):
        cycle = [square(int(26 + 24 * np.cos(2 * np.pi * k / 24))) for k in range(24)]
        write_frames(self.tmp / "full", cycle)
        write_frames(self.tmp / "cut", cycle[:18])
        self.assertEqual(qa.check_loop(str(self.tmp / "full"))[0].status, qa.OK)
        self.assertEqual(qa.check_loop(str(self.tmp / "cut"))[0].status, qa.FAIL)

    def test_loop_with_gaps_fails_and_names_the_fix(self):
        write_frames(self.tmp / "gap", [square(2 + k) for k in range(5)], [0, 8, 16, 24, 32])
        row, _ = qa.check_loop(str(self.tmp / "gap"))
        self.assertEqual(row.status, qa.FAIL)
        self.assertIn("--every", row.fix)
        self.assertNotIn("--frames all", row.fix)


class Markers(Tmp):
    def lottie(self, ip, marks):
        p = self.tmp / "m.json"
        p.write_text(json.dumps({"v": "5.7.0", "fr": 60, "ip": ip, "op": ip + 30, "w": 64, "h": 64, "layers": [], "markers": [{"cm": n, "tm": t, "dr": d} for n, t, d in marks]}))
        return p

    def test_marker_boundary_poses_match(self):
        row, data = qa.check_markers(str(GOLDEN / "02-markers/send-icon.json"), str(GOLDEN / "02-markers"))
        self.assertIn(row.status, (qa.OK, qa.WARN))
        diffs = {(p["a"], p["b"]): p["diff"] for p in data["pairs"]}
        self.assertEqual(diffs[(59, 60)], 0.0)
        self.assertEqual(diffs[(60, 180)], 0.0)

    def test_marker_jump_is_flagged(self):
        shutil.copytree(GOLDEN / "02-markers", self.tmp / "m")
        shutil.copy(GOLDEN / "02-themes/dark/f00060.png", self.tmp / "m/f00059.png")
        self.assertEqual(qa.check_markers(str(self.tmp / "m/send-icon.json"), str(self.tmp / "m"))[0].status, qa.FAIL)

    def test_missing_boundary_frames_warn_with_numbers(self):
        write_frames(self.tmp / "f", [square(2)] * 2, [9, 10])
        row, data = qa.check_markers(str(self.lottie(0, [("intro", 0, 10), ("idle", 10, 10), ("success", 20, 10)])), str(self.tmp / "f"))
        self.assertEqual(row.status, qa.WARN)
        self.assertIn("f19", row.line)
        self.assertIn(19, data["missing_frames"])

    def test_broken_loop_closing_pose_fails(self):
        write_frames(self.tmp / "l", [square(2 + 2 * k) for k in range(7)], range(7))
        row, _ = qa.check_markers(str(self.lottie(0, [("idle", 0, 6)])), str(self.tmp / "l"))
        self.assertEqual(row.status, qa.FAIL)

    def test_marker_times_subtract_the_lottie_in_point(self):
        write_frames(self.tmp / "ip", [square(2)] * 7, range(0, 7))
        row, data = qa.check_markers(str(self.lottie(60, [("intro", 60, 3), ("idle", 63, 3)])), str(self.tmp / "ip"))
        self.assertEqual({(p["a"], p["b"]) for p in data["pairs"]} >= {(2, 3), (5, 3)}, True)
        self.assertEqual(row.status, qa.OK)

    def test_themes_pairs_on_golden(self):
        names = ["light", "dark", "brand"]
        row, data = qa.check_themes([(n, str(GOLDEN / "02-themes" / n)) for n in names], str(self.tmp / "sheet.png"))
        self.assertEqual(row.status, qa.OK)
        self.assertEqual(len(data["pairs"]), 3)
        with Image.open(self.tmp / "sheet.png") as sheet:
            self.assertGreater(sheet.height, 3 * 100)


class Report(Tmp):
    def one_shot(self):
        write_frames(self.tmp / "once", [square(2 + 2 * k) for k in range(12)])
        return self.tmp / "once"

    def test_one_shot_asset_is_not_a_loop_failure(self):
        code, out, _ = cli("report", "--dir", self.one_shot())
        self.assertEqual(code, 0, out)
        self.assertIn("- 루프 이음새", out)

    def test_loop_flag_checks_the_seam(self):
        code, out, _ = cli("report", "--dir", self.one_shot(), "--loop")
        self.assertEqual(code, 1)
        self.assertIn("✗ 루프 이음새", out)

    def test_every_failing_row_is_in_the_fix_list(self):
        write_frames(self.tmp / "one", [square(2)])
        code, out, _ = cli("report", "--dir", self.tmp / "one")
        self.assertEqual(code, 1)
        todo = out.split("고칠 것:")[1]
        self.assertIn("움직임", todo)

    def test_blank_engine_folder_fails_the_report(self):
        write_frames(self.tmp / "engine", [blank()] * 12)
        code, out, _ = cli("report", "--dir", self.one_shot(), "--engine", self.tmp / "engine")
        self.assertEqual(code, 1)
        self.assertIn("✗ 잉크(엔진)", out)
        self.assertIn("✗ 경로 차이", out)

    def test_report_prints_one_line_per_check_and_a_fix_list(self):
        code, out, _ = cli("report", "--dir", GOLDEN / "01-textlayer/dotlottie", "--lottie-web", GOLDEN / "01-textlayer/lottieweb")
        self.assertEqual(code, 1)
        self.assertIn("✗ 플레이어 차이", out)
        self.assertIn("고칠 것:", out)

    def test_json_output_creates_its_folder(self):
        code, _, _ = cli("report", "--dir", self.one_shot(), "--json", self.tmp / "new/dir/r.json")
        self.assertEqual(code, 0)
        self.assertTrue((self.tmp / "new/dir/r.json").exists())
        self.assertEqual(cli("loop", self.one_shot(), "--json", self.tmp / "other/l.json")[0], 1)
        self.assertTrue((self.tmp / "other/l.json").exists())


class ToolErrors(Tmp):
    def test_missing_folder_exits_2(self):
        code, _, err = cli("ink", self.tmp / "nope")
        self.assertEqual(code, 2)
        self.assertEqual(len(err.strip().splitlines()), 1)

    def test_unreadable_frame_exits_2(self):
        (self.tmp / "bad").mkdir()
        (self.tmp / "bad/f00000.png").write_bytes(b"not a png")
        self.assertEqual(cli("ink", self.tmp / "bad")[0], 2)

    def test_bad_lottie_json_exits_2(self):
        write_frames(self.tmp / "f", [square(2)] * 3)
        bad = self.tmp / "bad.json"
        bad.write_text("{nope")
        self.assertEqual(cli("ink", self.tmp / "f", "--lottie", bad)[0], 2)
        bad.write_text('{"layers": "x"}')
        code, _, err = cli("ink", self.tmp / "f", "--lottie", bad)
        self.assertEqual(code, 2)
        self.assertIn("layers", err)
        self.assertEqual(cli("markers", self.tmp / "f", "--lottie", bad)[0], 2)

    def test_failing_verdict_exits_1(self):
        write_frames(self.tmp / "empty", [blank()] * 5)
        self.assertEqual(cli("ink", self.tmp / "empty")[0], 1)


ENC = shutil.which("ffmpeg") and shutil.which("ffprobe")


def probe(path, entries):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)["streams"][0]


def encode(src, name, *extra):
    return subprocess.run([sys.executable, str(TOOLS / "encode_asset.py"), str(src), "--name", str(name), "--fps", "60", *extra], capture_output=True, text=True)


@unittest.skipUnless(ENC, "ffmpeg and ffprobe are required")
class Encode(Tmp):
    def decode_alpha(self, path):
        subprocess.run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-c:v", "libvpx-vp9", "-i", str(path), "-pix_fmt", "rgba", str(self.tmp / "dec_%02d.png")], check=True)
        return [int(np.asarray(Image.open(f))[..., 3].min()) for f in sorted(self.tmp.glob("dec_*.png"))]

    def test_webm_and_mp4_color_tags_and_alpha(self):
        out = self.tmp / "x"
        r = encode(GOLDEN / "02-idle", out, "--formats", "gif,webm,mp4,apng")
        self.assertEqual(r.returncode, 0, r.stderr)
        for ext in ("webm", "mp4"):
            s = probe(f"{out}.{ext}", "stream=color_space,color_primaries,color_transfer,color_range")
            self.assertEqual((s["color_space"], s["color_primaries"], s["color_transfer"], s["color_range"]), ("bt709", "bt709", "iec61966-2-1", "tv"), ext)
        self.assertEqual(probe(f"{out}.webm", "stream_tags=alpha_mode")["tags"]["alpha_mode"], "1")
        self.assertLess(min(self.decode_alpha(f"{out}.webm")), 8)
        with Image.open(f"{out}.gif") as gif:
            self.assertLessEqual(gif.width, 480)
            self.assertGreaterEqual(gif.info["duration"], 20)
        with Image.open(f"{out}.apng") as apng:
            self.assertEqual(apng.n_frames, 60)

    def test_alpha_in_later_frames_is_kept(self):
        write_frames(self.tmp / "mixed", [opaque(32, 32), square(2, 32, 32), square(4, 32, 32)])
        r = encode(self.tmp / "mixed", self.tmp / "m", "--formats", "webm")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(min(self.decode_alpha(self.tmp / "m.webm")), 8)

    def test_gapped_folder_is_refused(self):
        write_frames(self.tmp / "gap", [square(2)] * 4, [0, 1, 3, 4])
        r = encode(self.tmp / "gap", self.tmp / "g")
        self.assertEqual(r.returncode, 2)
        self.assertIn("이어지지", r.stderr)
        self.assertFalse((self.tmp / "g.webm").exists())

    def test_odd_sizes_make_an_mp4(self):
        for w, h in ((35, 33), (255, 255), (375, 667)):
            write_frames(self.tmp / f"o{w}", [opaque(w, h), opaque(w, h, 80)])
            r = encode(self.tmp / f"o{w}", self.tmp / f"o{w}x", "--formats", "mp4")
            self.assertEqual(r.returncode, 0, r.stderr)
            s = probe(self.tmp / f"o{w}x.mp4", "stream=width,height")
            self.assertEqual((s["width"] % 2, s["height"] % 2), (0, 0))

    def test_transparent_gif_clears_previous_frames(self):
        write_frames(self.tmp / "t", [opaque(32, 32), square(2, 32, 32), square(4, 32, 32)])
        r = encode(self.tmp / "t", self.tmp / "t", "--formats", "gif")
        self.assertEqual(r.returncode, 0, r.stderr)
        subprocess.run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-i", str(self.tmp / "t.gif"), "-pix_fmt", "rgba", str(self.tmp / "gd_%02d.png")], check=True)
        shares = [float((np.asarray(Image.open(f))[..., 3] == 0).mean()) for f in sorted(self.tmp.glob("gd_*.png"))]
        self.assertGreater(shares[-1], 0.5)

    def test_gif_caps_the_frame_rate(self):
        write_frames(self.tmp / "r", [square(2 + k) for k in range(30)])
        r = encode(self.tmp / "r", self.tmp / "r", "--formats", "gif")
        self.assertEqual(r.returncode, 0, r.stderr)
        with Image.open(self.tmp / "r.gif") as gif:
            self.assertLessEqual(gif.n_frames, 26)
            self.assertGreaterEqual(gif.info["duration"], 20)

    def test_chrome_safe_mp4_background_is_composited_in_rgb(self):
        write_frames(self.tmp / "g", [np.full((64, 64, 4), (128, 128, 128, 255), np.uint8)] * 2)
        r = encode(self.tmp / "g", self.tmp / "g", "--formats", "mp4")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(probe(self.tmp / "g.mp4", "stream=color_transfer")["color_transfer"], "iec61966-2-1")


def disc(k, n=60, w=128, h=128, r=20):
    y, x = np.mgrid[0:h, 0:w]
    cx, cy = w / 2 + r * np.cos(2 * np.pi * k / n), h / 2 + r * np.sin(2 * np.pi * k / n)
    a = blank(w, h)
    a[(x - cx) ** 2 + (y - cy) ** 2 <= 49] = (200, 40, 40, 255)
    return a


class RoutesBackgroundsThemes(Tmp):
    def test_one_wrong_engine_frame_in_480_fails_routes(self):
        base = [square(2 + k % 40) for k in range(480)]
        bad = list(base)
        bad[200] = square(2, color=(10, 200, 10, 255))
        write_frames(self.tmp / "a", base)
        write_frames(self.tmp / "b", bad)
        row, _ = qa.check_routes(str(self.tmp / "a"), str(self.tmp / "b"))
        self.assertEqual(row.status, qa.FAIL)
        self.assertIn("f200", row.line)

    def test_textlayer_pair_fails_routes_and_peacock_pair_stays_a_warning(self):
        self.assertEqual(qa.check_routes(str(GOLDEN / "01-textlayer/dotlottie"), str(GOLDEN / "01-textlayer/lottieweb"))[0].status, qa.FAIL)
        self.assertEqual(qa.check_routes(str(GOLDEN / "04-pair/dotlottie"), str(GOLDEN / "04-pair/engine"))[0].status, qa.WARN)

    def test_same_shape_on_white_and_black_fails(self):
        def on(grey):
            a = opaque(64, 64, grey)
            a[20:40, 20:40, :3] = (200, 40, 40)
            return a
        write_frames(self.tmp / "w", [on(255)] * 3)
        write_frames(self.tmp / "k", [on(0)] * 3)
        for fn in (qa.check_players, qa.check_routes):
            row, _ = fn(str(self.tmp / "w"), str(self.tmp / "k"))
            self.assertEqual(row.status, qa.FAIL)
            self.assertIn("배경", row.line)

    def test_theme_difference_on_one_of_121_frames_counts(self):
        frames = [square(2 + k % 30) for k in range(121)]
        other = [f.copy() for f in frames]
        other[1][20:36, 20:36] = (10, 10, 200, 255)
        write_frames(self.tmp / "light", frames)
        write_frames(self.tmp / "dark", other)
        row, data = qa.check_themes([("light", str(self.tmp / "light")), ("dark", str(self.tmp / "dark"))])
        self.assertEqual(row.status, qa.OK)
        self.assertEqual(data["pairs"][0]["frames_compared"], 121)

    def test_report_runs_ink_on_every_theme_folder(self):
        write_frames(self.tmp / "once", [square(2 + 2 * k) for k in range(6)])
        write_frames(self.tmp / "light", [square(2 + 2 * k) for k in range(6)])
        write_frames(self.tmp / "dark", [blank()] * 6)
        code, out, _ = cli("report", "--dir", self.tmp / "once", "--theme", f"light={self.tmp / 'light'}", "--theme", f"dark={self.tmp / 'dark'}", "--sheet-dir", self.tmp / "sheets")
        self.assertEqual(code, 1)
        self.assertIn("✗ 잉크(테마 dark)", out)

    def test_theme_sheet_needs_a_folder_and_its_path_is_printed(self):
        write_frames(self.tmp / "once", [square(2 + 2 * k) for k in range(6)])
        write_frames(self.tmp / "light", [square(2 + 2 * k) for k in range(6)])
        write_frames(self.tmp / "dark", [square(2 + 2 * k, color=(10, 10, 200, 255)) for k in range(6)])
        args = ["report", "--dir", self.tmp / "once", "--theme", f"light={self.tmp / 'light'}", "--theme", f"dark={self.tmp / 'dark'}"]
        self.assertEqual(cli(*args)[0], 2)
        code, out, _ = cli(*args, "--out", self.tmp / "qa/report.txt")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.tmp / "qa/sheet_themes.png").exists())
        self.assertIn("sheet_themes.png", out)


class MarkerSemantics(Tmp):
    def lottie(self, ip, op, marks):
        p = self.tmp / "m.json"
        p.write_text(json.dumps({"v": "5.7.0", "fr": 60, "ip": ip, "op": op, "w": 128, "h": 128, "layers": [], "markers": [{"cm": n, "tm": t, "dr": d} for n, t, d in marks]}))
        return p

    def test_a_normal_circular_idle_loop_passes(self):
        write_frames(self.tmp / "c", [disc(k) for k in range(60)])
        row, data = qa.check_markers(str(self.lottie(0, 60, [("idle", 0, 60)])), str(self.tmp / "c"))
        self.assertEqual(row.status, qa.OK, row.line)
        self.assertIn("ratio", data["pairs"][0])

    def test_last_marker_ending_at_op_needs_no_frame_op(self):
        write_frames(self.tmp / "c", [disc(k, 30) for k in range(30)])
        row, data = qa.check_markers(str(self.lottie(0, 30, [("idle", 0, 30)])), str(self.tmp / "c"))
        self.assertEqual(row.status, qa.OK, row.line)
        self.assertEqual(data["missing_frames"], [])

    def test_first_marker_after_frame_zero_checks_its_entry(self):
        write_frames(self.tmp / "e", [square(2), square(3), square(50), square(51), square(52)])
        row, data = qa.check_markers(str(self.lottie(0, 5, [("success", 2, 3)])), str(self.tmp / "e"))
        self.assertNotEqual(row.status, qa.OK)
        self.assertEqual([(p["a"], p["b"]) for p in data["pairs"]], [(1, 2)])


class InputValidation(Tmp):
    def test_bad_numbers_exit_2(self):
        write_frames(self.tmp / "f", [square(2), square(5), square(9)])
        for bad in ("0", "-1", "nan", "inf"):
            self.assertEqual(cli("motion", self.tmp / "f", "--fps", bad)[0], 2, bad)
            self.assertEqual(cli("report", "--dir", self.tmp / "f", "--fps", bad)[0], 2, bad)
        for flag in ("--count", "--cols", "--width"):
            self.assertEqual(cli("sheet", self.tmp / "f", "--out", self.tmp / "s.png", flag, "0")[0], 2, flag)

    def test_non_numeric_lottie_fields_exit_2(self):
        write_frames(self.tmp / "f", [square(2)] * 3)
        for field in ("fr", "ip", "op"):
            bad = self.tmp / f"{field}.json"
            bad.write_text(json.dumps({"layers": [], "markers": [], field: "x"}))
            code, _, err = cli("ink", self.tmp / "f", "--lottie", bad)
            self.assertEqual(code, 2, field)
            self.assertIn(field, err)

    def test_output_paths_that_cannot_be_written_exit_2(self):
        write_frames(self.tmp / "f", [square(2), square(5), square(9)])
        (self.tmp / "dir").mkdir()
        self.assertEqual(cli("motion", self.tmp / "f", "--json", self.tmp / "dir")[0], 2)
        self.assertEqual(cli("report", "--dir", self.tmp / "f", "--out", self.tmp / "dir")[0], 2)
        self.assertEqual(cli("sheet", self.tmp / "f", "--out", self.tmp / "dir")[0], 2)

    def test_report_usage_lists_its_flags(self):
        line = next(l for l in qa.__doc__.splitlines() if l.strip().startswith("asset_qa.py report"))
        for flag in ("--sheet-dir", "--json", "--loop", "--common"):
            self.assertIn(flag, line)


@unittest.skipUnless(ENC, "ffmpeg and ffprobe are required")
class GifRound3(Tmp):
    def gif_ms(self, path):
        with Image.open(path) as im:
            return sum(f.info["duration"] for f in ImageSequence.Iterator(im))

    def test_held_frames_do_not_abort_the_default_formats(self):
        write_frames(self.tmp / "held", [square(2)] * 6 + [square(2 + k) for k in range(6)] + [square(9)] * 4)
        r = encode(self.tmp / "held", self.tmp / "h")
        self.assertEqual(r.returncode, 0, r.stderr)
        for ext in ("gif", "webm", "apng", "mp4"):
            self.assertTrue((self.tmp / f"h.{ext}").exists(), ext)
        self.assertAlmostEqual(self.gif_ms(self.tmp / "h.gif"), 16 / 60 * 1000, delta=60)

    def test_alpha_gif_plays_for_the_right_time(self):
        for fps, n in ((30, 120), (24, 96), (60, 240)):
            write_frames(self.tmp / f"d{fps}", [square(2 + k % 40) for k in range(n)])
            r = encode(self.tmp / f"d{fps}", self.tmp / f"d{fps}", "--formats", "gif", "--fps", str(fps))
            self.assertEqual(r.returncode, 0, r.stderr)
            want = n / fps * 1000
            self.assertLessEqual(abs(self.gif_ms(self.tmp / f"d{fps}.gif") - want) / want, 0.01, fps)

    def test_opaque_gif_plays_for_the_right_time(self):
        write_frames(self.tmp / "o", [opaque(48, 48, 20 + 2 * k) for k in range(60)])
        r = encode(self.tmp / "o", self.tmp / "o", "--formats", "gif", "--fps", "30")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLessEqual(abs(self.gif_ms(self.tmp / "o.gif") - 2000) / 2000, 0.02)

    def test_bad_fps_exits_2(self):
        write_frames(self.tmp / "f", [square(2)] * 2)
        for bad in ("0", "-5", "nan"):
            self.assertEqual(encode(self.tmp / "f", self.tmp / "x", "--fps", bad).returncode, 2, bad)


if __name__ == "__main__":
    unittest.main()
