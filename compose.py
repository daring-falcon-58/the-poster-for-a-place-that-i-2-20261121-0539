# compose.py — VELMARA, Isle of the Glass Arch.
# A retro flat-illustration travel poster (1930s style) for a place that
# does not exist, code-rendered with PIL. Deterministic: fixed coordinates,
# no randomness, no network, no timestamps.
# Draw order: sky -> sun halo/disc -> clouds -> headlands -> sea -> beach
# -> the Glass Arch -> sailboat -> gulls -> name -> border.
# Only text in the image is the place name "VELMARA".

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

INK = (14, 52, 66)          # deep navy-teal: arch, border, gulls, name shadow
ARCH_BAND = (26, 74, 88)    # arch stone banding
HEADLAND = (20, 80, 94)     # distant headlands
SEA_TOP = (27, 127, 139)    # sea gradient top
SEA_BOT = (10, 69, 83)      # sea gradient bottom
SAND = (243, 221, 166)      # pale sand
WET_SAND = (227, 193, 132)  # wet-sand edge
SUN = (242, 98, 63)         # coral sun disc
GOLD = (246, 196, 83)       # gold: glint, rim light, halo
CREAM = (255, 243, 214)     # cream: name, clouds, sail

SKY_STOPS = [
    (0.00, (20, 78, 94)),
    (0.38, (46, 125, 132)),
    (0.62, (217, 154, 85)),
    (0.80, (242, 180, 92)),
    (1.00, (246, 196, 83)),
]
SKY_BOTTOM = 640
SEA_TOP_Y = 620
SEA_BOT_Y = 880

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient_colour(stops, frac):
    frac = max(0.0, min(1.0, frac))
    for i in range(len(stops) - 1):
        f0, c0 = stops[i]
        f1, c1 = stops[i + 1]
        if f0 <= frac <= f1:
            t = 0.0 if f1 == f0 else (frac - f0) / (f1 - f0)
            return lerp(c0, c1, t)
    return stops[-1][1]


def draw_sky(img):
    d = ImageDraw.Draw(img)
    for y in range(SKY_BOTTOM + 1):
        d.line([(0, y), (W, y)], fill=gradient_colour(SKY_STOPS, y / SKY_BOTTOM))


def draw_sun(img):
    # Gold halo: three translucent discs behind the sun, alpha-composited.
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for radius, alpha in ((215, 14), (170, 26), (130, 44)):
        hd.ellipse([512 - radius, 505 - radius, 512 + radius, 505 + radius],
                   fill=GOLD + (alpha,))
    img.alpha_composite(halo)
    d = ImageDraw.Draw(img)
    d.ellipse([512 - 92, 505 - 92, 512 + 92, 505 + 92], fill=SUN)
    d.ellipse([512 - 95, 505 - 95, 512 + 95, 505 + 95], outline=CREAM, width=3)


def draw_clouds(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    clusters = [
        (210, 300, 260, 34, 48),
        (820, 250, 300, 30, 55),
        (880, 335, 170, 24, 60),
        (150, 330, 160, 22, 42),
    ]
    for cx, cy, w, h, alpha in clusters:
        # Three overlapping ellipses per cluster: flat, soft, retro.
        d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                  fill=CREAM + (alpha,))
        d.ellipse([cx - w // 2 - 46, cy - h // 4, cx - w // 6, cy + h // 2],
                  fill=CREAM + (alpha,))
        d.ellipse([cx + w // 6, cy - h // 4, cx + w // 2 + 46, cy + h // 2],
                  fill=CREAM + (alpha,))
    img.alpha_composite(layer)


def draw_headlands(img):
    d = ImageDraw.Draw(img)
    d.polygon([(28, 640), (28, 612), (120, 588), (210, 596), (300, 640)],
              fill=HEADLAND)
    d.polygon([(996, 640), (996, 616), (910, 590), (830, 600), (760, 640)],
              fill=HEADLAND)


def draw_sea(img):
    d = ImageDraw.Draw(img)
    for y in range(SEA_TOP_Y, SEA_BOT_Y + 1):
        frac = (y - SEA_TOP_Y) / (SEA_BOT_Y - SEA_TOP_Y)
        d.line([(0, y), (W, y)], fill=lerp(SEA_TOP, SEA_BOT, frac))
    # Sun-glint: gold dashes down the centre, widening as they fall.
    glint = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glint)
    for i, y in enumerate(range(648, 851, 22)):
        half = 34 + i * 13
        alpha = max(26, 150 - i * 12)
        gd.rounded_rectangle([512 - half, y, 512 + half, y + 7], radius=3,
                             fill=GOLD + (alpha,))
    img.alpha_composite(glint)
    # White wave ticks, sparse so the sea stays calm.
    wave = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave)
    for x, y, w in ((180, 700, 46), (250, 780, 60), (830, 730, 52),
                    (760, 810, 64), (140, 830, 40)):
        wd.line([(x, y), (x + w, y)], fill=(255, 255, 255, 110), width=3)
    img.alpha_composite(wave)


def draw_beach(img):
    d = ImageDraw.Draw(img)
    # Crescent of pale sand, full-bleed to the bottom edge.
    d.polygon([(28, 1024), (28, 908), (180, 872), (380, 858), (512, 854),
               (644, 858), (844, 872), (996, 908), (996, 1024)], fill=SAND)
    # Wet-sand edge along the top of the crescent.
    d.line([(28, 908), (180, 872), (380, 858), (512, 854), (644, 858),
            (844, 872), (996, 908)], fill=WET_SAND, width=4)


def draw_arch(img):
    # The Glass Arch: mask-built so sky and sun show through the opening.
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    # Outer silhouette: semicircle + two pillars down to the water.
    md.pieslice([512 - 210, 470 - 210, 512 + 210, 470 + 210], 180, 360, fill=255)
    md.rectangle([512 - 210, 470, 512 - 140, 640], fill=255)
    md.rectangle([512 + 140, 470, 512 + 210, 640], fill=255)
    # Opening: smaller semicircle + rectangle, knocked out in black.
    md.pieslice([512 - 140, 470 - 140, 512 + 140, 470 + 140], 180, 360, fill=0)
    md.rectangle([512 - 140, 470, 512 + 140, 640], fill=0)
    stone = Image.new("RGBA", (W, H), INK + (255,))
    img.paste(stone, (0, 0), mask)
    d = ImageDraw.Draw(img)
    # Stone banding across both pillars.
    for y in (520, 570, 615):
        d.line([(512 - 210, y), (512 - 140, y)], fill=ARCH_BAND, width=3)
        d.line([(512 + 140, y), (512 + 210, y)], fill=ARCH_BAND, width=3)
    # Gold rim light: inner top arc + inner pillar edges.
    d.arc([512 - 140, 470 - 140, 512 + 140, 470 + 140], 180, 360,
          fill=GOLD, width=4)
    d.line([(512 - 140, 470), (512 - 140, 640)], fill=GOLD, width=3)
    d.line([(512 + 140, 470), (512 + 140, 640)], fill=GOLD, width=3)
    # Faint pillar reflections in the water below.
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    rd.rectangle([512 - 210, 640, 512 - 140, 700], fill=INK + (70,))
    rd.rectangle([512 + 140, 640, 512 + 210, 700], fill=INK + (70,))
    img.alpha_composite(refl)


def draw_boat(img):
    d = ImageDraw.Draw(img)
    # One small sailboat on the lagoon, right of the arch, waterline (770, 716).
    d.polygon([(770, 658), (770, 710), (804, 710)], fill=CREAM)   # mainsail
    d.polygon([(766, 668), (766, 710), (740, 710)], fill=(255, 255, 255))  # jib
    d.line([(770, 654), (770, 712)], fill=INK, width=3)           # mast
    d.polygon([(732, 712), (810, 712), (800, 726), (742, 726)], fill=INK)  # hull
    d.line([(736, 732), (806, 732)], fill=(255, 255, 255, 160), width=2)


def draw_gulls(img):
    d = ImageDraw.Draw(img)
    for x, y, s in ((250, 300, 16), (300, 268, 12), (700, 282, 15),
                    (760, 322, 12), (648, 246, 11)):
        d.line([(x - s, y - 5), (x, y + 3), (x + s, y - 5)], fill=INK, width=3)


def draw_name(img):
    d = ImageDraw.Draw(img)
    name = "VELMARA"
    # Auto-fit: shrink from 170 px until the letterspaced width fits 900 px.
    size = 170
    while size > 40:
        font = ImageFont.truetype(SERIF_BOLD, size)
        spacing = max(6, size // 9)
        width = sum(d.textlength(ch, font=font) for ch in name) + spacing * (len(name) - 1)
        if width <= 900:
            break
        size -= 6
    font = ImageFont.truetype(SERIF_BOLD, size)
    spacing = max(6, size // 9)
    # Draw letter by letter so the letterspacing is exact.
    widths = [d.textlength(ch, font=font) for ch in name]
    total = sum(widths) + spacing * (len(name) - 1)
    x = (W - total) / 2
    y = 66
    # Navy shadow first, offset down 5 px, then the cream face.
    xs = x
    for ch, w in zip(name, widths):
        d.text((xs, y + 5), ch, font=font, fill=INK)
        xs += w + spacing
    xs = x
    for ch, w in zip(name, widths):
        d.text((xs, y), ch, font=font, fill=CREAM)
        xs += w + spacing
    # Thin cream rule under the name + a small diamond centred on it.
    baseline = y + size
    rule_y = baseline + 22
    half = total * 0.32
    d.line([(512 - half, rule_y), (512 + half, rule_y)], fill=CREAM, width=3)
    d.polygon([(512, rule_y - 9), (512 + 9, rule_y), (512, rule_y + 9),
               (512 - 9, rule_y)], fill=CREAM)


def draw_border(img):
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, 1004, 1004], outline=INK, width=6)
    d.rectangle([32, 32, 992, 992], outline=INK, width=2)


def render():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw_sky(img)
    draw_sun(img)
    draw_clouds(img)
    draw_headlands(img)
    draw_sea(img)
    draw_beach(img)
    draw_arch(img)
    draw_boat(img)
    draw_gulls(img)
    draw_name(img)
    draw_border(img)
    return img.convert("RGB")


def main():
    poster = render()
    poster.save("poster.png", optimize=True)
    import os
    print(f"poster.png: {poster.size[0]}x{poster.size[1]}, "
          f"{os.path.getsize('poster.png')} bytes")


if __name__ == "__main__":
    main()
