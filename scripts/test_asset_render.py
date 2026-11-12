#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1] / "skills/resolve-showreel-tools"
RENDER = SKILL / "scripts/render.mjs"
DOTLOTTIE = SKILL / "scripts/node_modules/@lottiefiles/dotlottie-web/dist"
SOLID = ('{"v":"5.7.0","fr":10,"ip":0,"op":5,"w":32,"h":32,"layers":[{"ty":1,"sw":32,"sh":32,"sc":"#ff0000",'
         '"ks":{"o":{"a":0,"k":100},"p":{"a":0,"k":[16,16,0]},"a":{"a":0,"k":[16,16,0]},"s":{"a":0,"k":[100,100,100]},'
         '"r":{"a":0,"k":0}},"ip":0,"op":5,"st":0}]}')

PAGE = """<!doctype html><html><body style="margin:0;background:transparent">
<div id="b" style="position:absolute;top:8px;width:16px;height:16px;background:#d33"></div>
<script>
const X = %s;
window.__meta = {duration: 0.5, fps: 10, width: 64, height: 64, scenes: [{id: 's'}], fonts: ['none']};
window.__seek = t => { document.getElementById('b').style.left = X(t) + 'px'; };
window.__ready = true;
</script></body></html>"""


def png_alpha_min(path):
    data = Path(path).read_bytes()
    pos, idat, width, height, ctype = 8, b"", 0, 0, 0
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            width, height, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 8 and ctype == 6, "expected 8-bit RGBA"
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    raw, stride, prev, alphas = zlib.decompress(idat), width * 4, bytearray(width * 4), []
    for y in range(height):
        row = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        ft = raw[y * (stride + 1)]
        for i in range(stride):
            a = row[i - 4] if i >= 4 else 0
            b = prev[i]
            c = prev[i - 4] if i >= 4 else 0
            if ft == 1: row[i] = (row[i] + a) & 255
            elif ft == 2: row[i] = (row[i] + b) & 255
            elif ft == 3: row[i] = (row[i] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[i] = (row[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        alphas.extend(row[3::4])
        prev = row
    return min(alphas)


class AssetRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("node") or not (RENDER.parent / "node_modules/playwright-core").exists():
            raise unittest.SkipTest("node or playwright-core is missing")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.page("steady", "t => t * 100")
        cls.page("random", "t => Math.random() * 100")
        cls.page("query", "t => t * 100", "new URLSearchParams(location.search).get('src') === '/a.lottie' ? true : 'error'")
        probe = cls.render("steady", "probe", "--every", "5")
        if probe.returncode == 1 and "브라우저를 띄우지 못했다" in probe.stderr:
            raise unittest.SkipTest("Chrome is missing")
        assert probe.returncode == 0, probe.stderr
        cls.player_ready = DOTLOTTIE.exists()
        if cls.player_ready:
            shutil.copytree(DOTLOTTIE, cls.root / "lib/dotlottie-web")
            shutil.copytree(SKILL / "assets/player", cls.root / "player")
            (cls.root / "out").mkdir()
            (cls.root / "out/solid.json").write_text(SOLID, encoding="utf-8")

    @classmethod
    def page(cls, name, expr, ready="true"):
        (cls.root / name).mkdir()
        (cls.root / name / "index.html").write_text(PAGE % expr, encoding="utf-8")
        if ready != "true":
            f = cls.root / name / "index.html"
            f.write_text(f.read_text(encoding="utf-8").replace("window.__ready = true;", f"window.__ready = {ready};"), encoding="utf-8")

    @classmethod
    def render(cls, name, out, *extra):
        return subprocess.run(["node", str(RENDER), "--dir", str(cls.root / name), "--root", str(cls.root),
                               "--frames", str(cls.root / out), *extra], capture_output=True, text=True, timeout=120)

    def player(self, cfg, out):
        if not self.player_ready:
            self.skipTest("dotlottie-web is not installed")
        page = self.root / out
        shutil.copytree(self.root / "player", page)
        f = page / "index.html"
        f.write_text(f.read_text(encoding="utf-8").replace("window.PLAYER_CFG || {}", cfg), encoding="utf-8")
        return subprocess.run(["node", str(RENDER), "--dir", str(page), "--root", str(self.root),
                               "--frames", str(self.root / (out + "-f"))], capture_output=True, text=True, timeout=120)

    def frame_files(self, out):
        return sorted(p.name for p in (self.root / out).glob("f*.png"))

    def test_alpha_frames_keep_transparency(self):
        r = self.render("steady", "alpha", "--alpha")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.frame_files("alpha")), 5)
        self.assertLess(png_alpha_min(self.root / "alpha/f00000.png"), 255)

    def test_alpha_flag_never_consumes_the_next_token(self):
        r = self.render("steady", "alpha-tok", "--alpha", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(png_alpha_min(self.root / "alpha-tok/f00000.png"), 255)

    def test_deterministic_page_passes_repeat(self):
        r = self.render("steady", "rep-ok", "--repeat", "2")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_repeat_is_stable_with_many_workers(self):
        for i in range(8):
            r = self.render("steady", f"rep-w{i}", "--repeat", "2", "--workers", "6")
            self.assertEqual(r.returncode, 0, f"run {i}: {r.stderr}")

    def test_random_page_fails_repeat_with_frame_numbers(self):
        r = self.render("random", "rep-bad", "--repeat", "2")
        self.assertEqual(r.returncode, 3, r.stderr)
        m = re.search(r"비결정 프레임 (\d+)개.*: ([\d, ]+)", r.stderr)
        self.assertIsNotNone(m, r.stderr)
        listed = [int(x) for x in m.group(2).split(",")]
        self.assertEqual(len(listed), int(m.group(1)))
        self.assertTrue(set(listed) <= {0, 1, 2, 3, 4})

    def test_invalid_numeric_flags_exit_1_without_frames(self):
        for i, flags in enumerate((["--repeat"], ["--repeat", "abc"], ["--repeat", "0"], ["--every", "1.5"], ["--workers", "0"])):
            r = self.render("steady", f"bad{i}", *flags)
            self.assertEqual(r.returncode, 1, f"{flags}: {r.stderr}")
            self.assertEqual(self.frame_files(f"bad{i}"), [], flags)

    def test_frames_dir_drops_stale_frames(self):
        self.assertEqual(self.render("steady", "stale").returncode, 0)
        self.assertEqual(len(self.frame_files("stale")), 5)
        (self.root / "stale/keep.txt").write_text("x")
        self.assertEqual(self.render("steady", "stale", "--to", "0.2").returncode, 0)
        self.assertEqual(self.frame_files("stale"), ["f00000.png", "f00001.png"])
        self.assertTrue((self.root / "stale/keep.txt").exists())

    def test_page_query_keeps_render_flag_separate(self):
        r = subprocess.run(["node", str(RENDER), "--dir", str(self.root / "query"), "--root", str(self.root),
                            "--page", "index.html?src=/a.lottie", "--frames", str(self.root / "query-f")],
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_player_renders_solid_json(self):
        r = self.player("{ src: '/out/solid.json' }", "pl-ok")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.frame_files("pl-ok-f")), 5)

    def test_player_unknown_theme_exits_2(self):
        r = self.player("{ src: '/out/solid.json', theme: 'missing' }", "pl-theme")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("setTheme failed: missing", r.stderr)

    def test_player_unregistered_font_exits_2(self):
        (self.root / "fonts").mkdir(exist_ok=True)
        (self.root / "fonts/fonts.json").write_text(
            '[{"id":"Nope-400","family":"Nope","weight":400,"file":"nope.ttf"}]', encoding="utf-8")
        self.addCleanup(shutil.rmtree, self.root / "fonts")
        r = self.player("{ src: '/out/solid.json' }", "pl-font")
        self.assertEqual(r.returncode, 2, r.stderr)


if __name__ == "__main__":
    unittest.main()
