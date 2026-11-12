#!/usr/bin/env python3
"""Rebuild the golden frame subsets from the Lottie render spike, then run make_expected.py.

  python3 tests/asset/golden/build_golden.py --spike <repo>/spikes/lottie-render
"""
import argparse
import shutil
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
RESAMPLER = "PIL.Image.LANCZOS"
SUBSETS = [
    {"dest": f"01-{name}/{player}", "src": f"assets/01-hangul-loader/frames/lottie-{name}/{player}", "frames": list(range(0, 120, 8))}
    for name in ("builder", "textlayer") for player in ("dotlottie", "lottieweb")
] + [
    {"dest": "02-idle", "src": "assets/02-svg-icon/frames/idle_dotlottie", "frames": list(range(60, 120))},
    {"dest": "02-markers", "src": "assets/02-svg-icon/frames/dotlottie", "frames": [59, 60, 180], "extra": ["assets/02-svg-icon/out/send-icon.json"]},
] + [
    {"dest": f"02-themes/{t}", "src": f"assets/02-svg-icon/frames/theme_{t}_dotlottie", "frames": [60, 120, 180]} for t in ("light", "dark", "brand")
] + [
    {"dest": f"04-pair/{p}", "src": f"assets/04-folk-peacock/frames/{p}", "frames": [240], "resize": [480, 270]} for p in ("dotlottie", "engine")
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spike", required=True)
    a = ap.parse_args()
    spike = Path(a.spike)
    for s in SUBSETS:
        dest = HERE / s["dest"]
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True)
        for i in s["frames"]:
            src = spike / s["src"] / f"f{i:05d}.png"
            if s.get("resize"):
                with Image.open(src) as im:
                    im.convert("RGB").resize(tuple(s["resize"]), Image.LANCZOS).save(dest / src.name, optimize=True)
            else:
                shutil.copy(src, dest / src.name)
        for extra in s.get("extra", []):
            shutil.copy(spike / extra, dest / Path(extra).name)


if __name__ == "__main__":
    main()
