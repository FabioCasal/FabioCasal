from PIL import Image, ImageDraw, ImageFont
import math

TEXT = "FABIO CASAL"
SMALL_W, SMALL_H = 160, 24
SCALE = 6
W, H = SMALL_W * SCALE, SMALL_H * SCALE
N_FRAMES = 24

font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf", 16)

# color cycle palette (purple -> blue, matching the wave banner theme)
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

c1 = (109, 40, 217)   # 6D28D9 purple
c2 = (14, 165, 233)   # 0EA5E9 blue
bg = (13, 17, 23)     # 0D1117 github dark

frames = []
for i in range(N_FRAMES):
    small = Image.new("RGB", (SMALL_W, SMALL_H), bg)
    d = ImageDraw.Draw(small)
    bbox = d.textbbox((0,0), TEXT, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (SMALL_W - tw)//2 - bbox[0]
    y = (SMALL_H - th)//2 - bbox[1]

    t = i / N_FRAMES
    wave = (math.sin(t * 2*math.pi) + 1) / 2
    col = lerp(c1, c2, wave)

    # scanline flicker: dim every other row slightly for retro CRT feel
    d.text((x, y), TEXT, font=font, fill=col)

    big = small.resize((W, H), Image.NEAREST)

    # add scanlines on the upscaled image
    bd = ImageDraw.Draw(big)
    for row in range(0, H, SCALE*2):
        bd.line([(0,row),(W,row)], fill=(0,0,0), width=1)

    # blinking cursor block at the end every other frame cycle
    if (i // 4) % 2 == 0:
        cursor_x = x*SCALE + tw*SCALE + SCALE
        bd.rectangle([cursor_x, y*SCALE, cursor_x+SCALE, y*SCALE+th*SCALE], fill=col)

    frames.append(big)

frames[0].save(
    "pixel-name-banner.gif",
    save_all=True,
    append_images=frames[1:],
    duration=90,
    loop=0,
    optimize=True,
)
print("done")
