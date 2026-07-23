import math
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageSequence

BG_URL = (
    "https://cdn.jsdelivr.net/gh/ViratiAkiraNandhanReddy/"
    "pixel-art-readme-gifs@v1.0.0/gifs/hrzn/a1654aa1-c542-4269-b9f1-a9cc5634e112.gif"
)
OUT_PATH = "pixel-name-banner.gif"
TEXT = "FABIO CASAL"

FONT_CANDIDATES = [
    "C:/Windows/Fonts/consolab.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf",
]

c1 = (109, 40, 217)  # 6D28D9 purple
c2 = (14, 165, 233)  # 0EA5E9 blue

COLOR_PERIOD = 1800.0  # ms, full purple<->blue cycle
BLINK_PERIOD = 900.0  # ms, cursor blink cycle
OUT_DURATION = 60  # ms per output frame
SPRITE_SCALE = 2.5
PAD_X, PAD_Y = 20, 16


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def load_font():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, 44)
    return ImageFont.load_default()


def fetch_bg_frames():
    tmp_path = "_bg_download.gif"
    urllib.request.urlretrieve(BG_URL, tmp_path)
    bg = Image.open(tmp_path)
    frames = [f.convert("RGBA") for f in ImageSequence.Iterator(bg)]
    os.remove(tmp_path)
    return frames, bg.size


def main():
    bg_frames, (w, h) = fetch_bg_frames()
    n_bg = len(bg_frames)

    font = load_font()
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    spr_w, spr_h = tw + PAD_X * 2, th + PAD_Y * 2 + 6

    def make_sprite(t_ms):
        spr = Image.new("RGBA", (spr_w, spr_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(spr)
        wave = (math.sin((t_ms / COLOR_PERIOD) * 2 * math.pi) + 1) / 2
        col = lerp(c1, c2, wave)
        x = PAD_X - bbox[0]
        y = PAD_Y - bbox[1]
        d.text((x, y), TEXT, font=font, fill=col + (255,))

        if (t_ms % BLINK_PERIOD) < (BLINK_PERIOD / 2):
            cx = x + tw + 6
            d.rectangle([cx, y, cx + 8, y + th], fill=col + (255,))

        # scanline dim: darken every other row, only where alpha already > 0
        px = spr.load()
        for row in range(0, spr_h, 2):
            for col_x in range(spr_w):
                r, g, b, a = px[col_x, row]
                if a > 0:
                    px[col_x, row] = (r // 2, g // 2, b // 2, a)
        return spr

    sprite_big_size = (int(spr_w * SPRITE_SCALE), int(spr_h * SPRITE_SCALE))
    step = OUT_DURATION // 30  # bg gif runs at 30ms/frame
    pos_y = int(h * 0.22)  # top third

    out_frames = []
    for i in range(0, n_bg, step):
        t_ms = i * 30
        spr = make_sprite(t_ms).resize(sprite_big_size, Image.NEAREST)
        sw, sh = spr.size
        dest = ((w - sw) // 2, pos_y - sh // 2)
        frame = bg_frames[i].copy()
        frame.alpha_composite(spr, dest=dest)
        out_frames.append(frame.convert("RGB"))

    out_frames[0].save(
        OUT_PATH,
        save_all=True,
        append_images=out_frames[1:],
        duration=OUT_DURATION,
        loop=0,
        optimize=True,
    )
    print("saved", OUT_PATH)


if __name__ == "__main__":
    main()
