#!/usr/bin/env python3
"""에셋 프레임 폴더(render.mjs --frames 출력, f00000.png …)를 납품 형식으로 인코딩하고 크기를 보고한다.

  encode_asset.py FRAMES_DIR --name out/x --fps 60 [--formats gif,webm,apng,mp4] [--gif-width 480] [--bg '#ffffff']

- gif: 파일마다 팔레트. 알파가 있으면 1비트 투명(투명 배경 글자에는 쓰지 않는다). 폭은 --gif-width(기본 480)로 줄인다.
- webm: VP9, 알파가 있으면 yuva420p. BT.709 색 변환과 태그(colorspace, primaries, transfer, range=tv).
- apng: 무손실, 알파 유지. 큰 파일이다.
- mp4: H.264 yuv420p, 알파 없음이라 --bg 위에 합성. BT.709 색 변환과 태그.
ffmpeg 가 필요하다.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

BT709_TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
BT709_SCALE = "scale=out_color_matrix=bt709:out_range=tv,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv"
BASE = ["ffmpeg", "-y", "-nostdin", "-loglevel", "error"]


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg failed: " + " ".join(args) + "\n" + r.stderr[-2000:])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("DIR")
    p.add_argument("--name", required=True, help="출력 경로 접두사, 예: out/x")
    p.add_argument("--fps", type=float, required=True)
    p.add_argument("--formats", default="gif,webm,apng,mp4")
    p.add_argument("--gif-width", type=int, default=480)
    p.add_argument("--bg", default="#ffffff")
    a = p.parse_args()
    d = Path(a.DIR)
    frames = sorted(d.glob("f*.png"))
    if not frames:
        sys.exit(f"no PNG frames in {d}")
    with Image.open(frames[0]) as src:
        im = src.convert("RGBA")
    w, h = im.size
    has_alpha = im.getextrema()[3][0] < 255
    inp = ["-framerate", str(a.fps), "-start_number", str(int(frames[0].stem[1:])), "-i", str(d / "f%05d.png")]
    Path(a.name).parent.mkdir(parents=True, exist_ok=True)
    out = []
    for fmt in a.formats.split(","):
        f = f"{a.name}.{fmt}"
        if fmt == "gif":
            pg = "palettegen=reserve_transparent=1:stats_mode=diff" if has_alpha else "palettegen=stats_mode=diff"
            pu = "paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" + (":alpha_threshold=128" if has_alpha else "")
            vf = f"scale='min({a.gif_width},iw)':-2:flags=lanczos,split[a][b];[a]{pg}[p];[b][p]{pu}"
            run([*BASE, *inp, "-vf", vf, "-loop", "0", f])
        elif fmt == "webm":
            pix = "yuva420p" if has_alpha else "yuv420p"
            run([*BASE, *inp, "-vf", f"{BT709_SCALE},format={pix}", "-c:v", "libvpx-vp9", "-pix_fmt", pix, "-b:v", "0", "-crf", "32",
                 "-row-mt", "1", *BT709_TAGS, f])
        elif fmt == "apng":
            run([*BASE, *inp, "-plays", "0", "-f", "apng", f])
        elif fmt == "mp4":
            bg = a.bg.lstrip("#")
            flat = [*inp, "-f", "lavfi", "-i", f"color=c=0x{bg}:s={w}x{h}:r={a.fps}", "-filter_complex",
                    f"[1:v][0:v]overlay=shortest=1:format=auto,{BT709_SCALE},format=yuv420p"]
            run([*BASE, *flat, "-c:v", "libx264", "-crf", "18", "-preset", "medium", *BT709_TAGS, "-movflags", "+faststart", f])
        else:
            sys.exit(f"unknown format {fmt}")
        out.append(f)
    print(json.dumps({"frames_dir": str(d), "alpha": has_alpha,
                      "outputs": [{"file": f, "kb": round(Path(f).stat().st_size / 1024, 1)} for f in out]}, indent=2))


if __name__ == "__main__":
    main()
