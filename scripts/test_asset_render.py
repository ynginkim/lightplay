#!/usr/bin/env python3
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

sys.dont_write_bytecode = True
RENDER = Path(__file__).resolve().parents[1] / "skills/resolve-showreel-tools/scripts/render.mjs"

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
        if cls.render("steady", "probe", "--every", "5").returncode == 1:
            raise unittest.SkipTest("Chrome is missing")

    @classmethod
    def page(cls, name, expr):
        (cls.root / name).mkdir()
        (cls.root / name / "index.html").write_text(PAGE % expr, encoding="utf-8")

    @classmethod
    def render(cls, name, out, *extra):
        return subprocess.run(["node", str(RENDER), "--dir", str(cls.root / name), "--root", str(cls.root),
                               "--frames", str(cls.root / out), *extra], capture_output=True, text=True, timeout=120)

    def test_alpha_frames_keep_transparency(self):
        r = self.render("steady", "alpha", "--alpha")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(list((self.root / "alpha").glob("f*.png"))), 5)
        self.assertLess(png_alpha_min(self.root / "alpha/f00000.png"), 255)

    def test_deterministic_page_passes_repeat(self):
        r = self.render("steady", "rep-ok", "--repeat", "2")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_random_page_fails_repeat_with_frame_numbers(self):
        r = self.render("random", "rep-bad", "--repeat", "2")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertRegex(r.stderr, r"비결정 프레임 \d+개")


if __name__ == "__main__":
    unittest.main()
