#!/usr/bin/env python3
"""Regenerate expected.json from the golden frame subsets.

  python3 tests/asset/golden/make_expected.py --measure <spike>/harness/measure.py
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from build_golden import RESAMPLER, SUBSETS

HERE = Path(__file__).resolve().parent
GRID = 8

NUMERIC = [
    ("players_01_textlayer", "players", ["01-textlayer/dotlottie", "01-textlayer/lottieweb"], "mean_abs_diff.avg", 0.05, 2.37),
    ("players_01_builder", "players", ["01-builder/dotlottie", "01-builder/lottieweb"], "mean_abs_diff.avg", 0.02, 0.145),
    ("routes_04_mean", "routes", ["04-pair/dotlottie", "04-pair/engine"], "mean_abs_diff.avg", 0.05, 2.45),
    ("routes_04_edge_saturation", "routes", ["04-pair/dotlottie", "04-pair/engine"], "saturation_A_minus_B.가장자리", 0.003, 0.021),
    ("routes_04_centre_saturation", "routes", ["04-pair/dotlottie", "04-pair/engine"], "saturation_A_minus_B.가운데", 0.002, 0.001),
]


def measure(script, args):
    r = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def grey_composite(path):
    a = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
    al = a[..., 3:4] / 255.0
    return a[..., :3] * al + 128 * (1 - al)


def saturation(x):
    mx, mn = x.max(axis=2), x.min(axis=2)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)


def saturation_zone(a_dir, b_dir, zone):
    d = saturation(grey_composite(next(Path(a_dir).glob("f*.png")))) - saturation(grey_composite(next(Path(b_dir).glob("f*.png"))))
    h, w = d.shape
    cells = np.array([[d[r * h // GRID:(r + 1) * h // GRID, c * w // GRID:(c + 1) * w // GRID].mean() for c in range(GRID)] for r in range(GRID)])
    ring = np.ones((GRID, GRID), bool)
    ring[1:-1, 1:-1] = False
    centre = np.zeros((GRID, GRID), bool)
    centre[GRID // 2 - 1:GRID // 2 + 1, GRID // 2 - 1:GRID // 2 + 1] = True
    return float(cells[ring if zone == "가장자리" else centre].mean())


def dig(d, path):
    for k in path.split("."):
        d = d[k]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure", required=True)
    a = ap.parse_args()
    numeric = {}
    for name, cmd, dirs, path, tol, spike in NUMERIC:
        paths = [str(HERE / d) for d in dirs]
        if name.startswith("routes_04_") and "saturation" in name:
            value = saturation_zone(*paths, path.split(".")[1])
            how = "numpy HSV saturation (A-B) on an 8x8 grid after compositing on grey 128, one frame"
        elif cmd == "loop":
            value = dig(measure(a.measure, ["loop", *paths]), path)
            how = "measure.py loop"
        else:
            value = dig(measure(a.measure, ["diff", *paths, "--top", "1"]), path)
            how = "measure.py diff"
        numeric[name] = {"cmd": cmd, "args": dirs, "path": path, "value": round(value, 4), "tol": tol, "spike_full": spike, "how": how}
    sources = [{k: v for k, v in s.items()} for s in SUBSETS]
    out = {
        "method": "value = spike harness/measure.py on exactly the committed subset (see how). spike_full = published number on the full folder. Tests assert value within tol.",
        "rebuild": "python3 tests/asset/golden/build_golden.py --spike <repo>/spikes/lottie-render, then make_expected.py --measure <spike>/harness/measure.py",
        "resampler": RESAMPLER,
        "sources": sources,
        "numeric": numeric,
    }
    (HERE / "expected.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(numeric, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
