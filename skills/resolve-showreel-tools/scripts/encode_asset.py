#!/usr/bin/env python3
"""에셋 프레임 폴더(render.mjs --frames 출력, f00000.png …)를 납품 형식으로 인코딩하고 크기를 보고한다.

  encode_asset.py FRAMES_DIR --name out/x --fps 60 [--formats gif,webm,apng,mp4] [--gif-width 480] [--bg '#ffffff']

- 프레임 번호가 이어져 있어야 한다. 빠진 번호가 있으면 종료 코드 2 로 멈춘다(--every 로 캡처한 폴더는 인코딩하지 않는다).
- 알파는 모든 프레임에서 본다. 한 프레임이라도 투명하면 알파를 유지한다.
- gif: 폭을 --gif-width(기본 480)로 줄이고 프레임 간격을 10 ms 의 정수배로 맞춘다(60→50fps, 30→25fps, 24→20fps. 재생 시간은 그대로다).
  Chrome 은 10 ms 이하 지연을 100 ms 로 늘리고 지연은 10 ms 단위로 저장된다. 알파가 있으면 Pillow 로 만들고 프레임마다 배경으로 지운다(disposal 2).
  같은 프레임이 이어지면 하나로 합쳐 지연을 더한다. 길이는 프레임 수와 fps 로 맞는지 본다. 1비트 알파라 투명 배경 글자에는 쓰지 않는다.
- webm: VP9. 알파가 있으면 alpha_mode=1 태그가 붙고 ffprobe 는 화소 형식을 yuv420p 로 보고한다.
- apng: 무손실, 알파 유지. 큰 파일이다.
- mp4: H.264 yuv420p, 알파 없음이라 --bg 위에 RGB 로 합성한다. 홀수 크기는 --bg 색으로 짝수까지 채운다.
- webm·mp4 색: 색 행렬과 원색은 BT.709, 범위 tv, 밝기 곡선은 sRGB(iec61966-2-1)로 태그한다. 곡선을 BT.709 로 태그하면 Chrome 이 중간 밝기를 6.6/255 올린다.
종료 코드: 0 정상, 2 입력·인코딩 오류. ffmpeg 가 필요하다.
"""
import argparse
import json
import math
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageSequence

TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "iec61966-2-1", "-color_range", "tv"]
YUV = "scale=out_color_matrix=bt709:out_range=tv,setparams=colorspace=bt709:color_primaries=bt709:color_trc=iec61966-2-1:range=tv"
BASE = ["ffmpeg", "-y", "-nostdin", "-loglevel", "error"]
GIF_MAX_FPS = 50.0


def fail(msg):
    print(f"오류: {msg}", file=sys.stderr)
    sys.exit(2)


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        fail("ffmpeg 실패: " + " ".join(args) + "\n" + r.stderr[-2000:])


def packets(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def alpha_min(path):
    with Image.open(path) as im:
        return im.convert("RGBA").getchannel("A").getextrema()[0]


def gif_timing(fps):
    cs = max(2, math.ceil(100 / min(fps, GIF_MAX_FPS) - 1e-9))
    return cs, 100 / cs


def gif_total_ms(path):
    with Image.open(path) as im:
        return sum(f.info.get("duration", 0) for f in ImageSequence.Iterator(im))


def gif_alpha(frames, fps, width, out):
    cs, gfps = gif_timing(fps)
    pick = [frames[min(int(k * fps / gfps), len(frames) - 1)] for k in range(max(1, round(len(frames) * gfps / fps)))]
    ims = []
    for f in pick:
        with Image.open(f) as src:
            im = src.convert("RGBA")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        p = im.convert("RGB").quantize(colors=255)
        p.paste(255, im.getchannel("A").point(lambda v: 255 if v < 128 else 0))
        pal = p.getpalette()[:765]
        p.putpalette(pal + [0, 0, 0] * (256 - len(pal) // 3))
        ims.append(p)
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=cs * 10, loop=0, disposal=2, transparency=255, optimize=False)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("DIR")
    p.add_argument("--name", required=True, help="출력 경로 접두사, 예: out/x")
    p.add_argument("--fps", type=float, required=True)
    p.add_argument("--formats", default="gif,webm,apng,mp4")
    p.add_argument("--gif-width", type=int, default=480)
    p.add_argument("--bg", default="#ffffff")
    a = p.parse_args()
    if not (math.isfinite(a.fps) and a.fps > 0):
        fail(f"--fps 는 0 보다 큰 숫자여야 한다: {a.fps}")
    if a.gif_width < 1:
        fail(f"--gif-width 는 1 이상이어야 한다: {a.gif_width}")
    d = Path(a.DIR)
    if not d.is_dir():
        fail(f"폴더가 없다: {d}")
    frames = sorted(f for f in d.glob("f*.png") if f.stem[1:].isdigit())
    if not frames:
        fail(f"PNG 프레임이 없다: {d}")
    nums = [int(f.stem[1:]) for f in frames]
    gone = sorted(set(range(nums[0], nums[-1] + 1)) - set(nums))
    if gone:
        fail(f"프레임 번호가 이어지지 않는다(빠진 번호 {gone[:8]}{'…' if len(gone) > 8 else ''}). render.mjs 를 --every 없이 다시 실행한다")
    with Image.open(frames[0]) as im:
        w, h = im.size
    with ThreadPoolExecutor() as ex:
        has_alpha = min(ex.map(alpha_min, frames)) < 255
    inp = ["-framerate", str(a.fps), "-start_number", str(nums[0]), "-i", str(d / "f%05d.png")]
    Path(a.name).parent.mkdir(parents=True, exist_ok=True)
    out = []
    for fmt in a.formats.split(","):
        f = f"{a.name}.{fmt}"
        if fmt == "gif" and has_alpha:
            gif_alpha(frames, a.fps, a.gif_width, f)
        elif fmt == "gif":
            vf = f"fps={gif_timing(a.fps)[1]},scale='min({a.gif_width},iw)':-2:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
            run([*BASE, *inp, "-vf", vf, "-loop", "0", f])
        elif fmt == "webm":
            pix = "yuva420p" if has_alpha else "yuv420p"
            run([*BASE, *inp, "-vf", f"{YUV},format={pix}", "-c:v", "libvpx-vp9", "-pix_fmt", pix, "-b:v", "0", "-crf", "32", "-row-mt", "1", *TAGS, f])
        elif fmt == "apng":
            run([*BASE, *inp, "-plays", "0", "-f", "apng", f])
        elif fmt == "mp4":
            bg = a.bg.lstrip("#")
            graph = (f"[1:v]format=rgba[bg];[0:v]format=rgba[fg];[bg][fg]overlay=shortest=1:format=rgb,"
                     f"pad=ceil(iw/2)*2:ceil(ih/2)*2:color=0x{bg},{YUV},format=yuv420p")
            run([*BASE, *inp, "-f", "lavfi", "-i", f"color=c=0x{bg}:s={w}x{h}:r={a.fps}", "-filter_complex", graph,
                 "-c:v", "libx264", "-crf", "18", "-preset", "medium", *TAGS, "-movflags", "+faststart", f])
        else:
            fail(f"알 수 없는 형식: {fmt}")
        if fmt == "gif":
            want, got = len(frames) / a.fps * 1000, gif_total_ms(f)
            if abs(got - want) > max(0.02 * want, 2 * gif_timing(a.fps)[0] * 10):
                fail(f"{f} 의 재생 시간이 맞지 않는다: {want:.0f} ms 여야 하는데 {got} ms")
        elif packets(f) != len(frames):
            fail(f"{f} 의 프레임 수가 맞지 않는다: 입력 {len(frames)}개, 출력 {packets(f)}개")
        out.append(f)
    print(json.dumps({"frames_dir": str(d), "frames": len(frames), "alpha": has_alpha,
                      "outputs": [{"file": f, "kb": round(Path(f).stat().st_size / 1024, 1)} for f in out]}, indent=2))


if __name__ == "__main__":
    main()
