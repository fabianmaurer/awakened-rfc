"""Draw a symbolic Monarchy button directly at 64 x 64 pixels.

Run with .venv-art/Scripts/python.exe art/civics/draw_monarchy.py.
No image generation service or high-resolution source is used.
"""
from math import sqrt
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ART = Path(__file__).resolve().parent
DEST = ROOT / "Awakened RFC/Assets/Art/Interface/Buttons/Civics/RFCMP/Monarchy.dds"


def render():
    im = Image.new("RGBA", (64, 64))
    pixels = im.load()
    for y in range(64):
        for x in range(64):
            light = max(0, 1 - sqrt(((x - 30) / 37.0) ** 2 + ((y - 24) / 46.0) ** 2))
            grain = ((x * 17 + y * 31 + x * y * 7) % 9) - 4
            pixels[x, y] = (int(15 + 28 * light) + grain,
                            int(11 + 15 * light) + grain,
                            int(14 + 13 * light) + grain, 255)
    d = ImageDraw.Draw(im)
    dark = (52, 28, 13)
    gold = (185, 126, 44)
    shine = (247, 215, 132)
    shade = (105, 63, 25)
    # Ground shadow and stone dais.
    d.ellipse((9, 52, 55, 59), fill=(10, 8, 9))
    d.polygon([(17, 51), (46, 51), (53, 58), (10, 58)], fill=(85, 69, 56))
    d.line([(17, 51), (46, 51), (53, 58)], fill=(148, 120, 83))
    d.line([(11, 58), (53, 58)], fill=(43, 34, 29))
    d.line([(14, 56), (49, 56)], fill=(114, 94, 72))
    # Tall, gold-framed back, with a crown silhouette built into its crest.
    d.polygon([(19, 38), (19, 17), (23, 12), (40, 12), (44, 17), (44, 38)], fill=dark)
    d.polygon([(21, 36), (21, 18), (25, 14), (38, 14), (42, 18), (42, 36)], fill=gold)
    d.line([(20, 35), (20, 18), (24, 13), (39, 13)], fill=shine)
    d.line([(43, 18), (43, 36)], fill=shade)
    d.polygon([(24, 13), (22, 6), (28, 10), (31, 4), (35, 10), (41, 6), (39, 13)], fill=dark)
    d.polygon([(25, 12), (24, 8), (28, 11), (31, 6), (35, 11), (39, 8), (38, 12)], fill=gold)
    d.line([(25, 12), (38, 12)], fill=shine)
    for x, y in [(23, 6), (31, 4), (40, 6)]:
        d.point((x, y), fill=shine)
    d.rectangle((30, 10, 32, 12), fill=(108, 17, 25))
    d.point((30, 10), fill=(239, 109, 81))
    # Burgundy upholstery: each pixel gets shading and a woven texture.
    mask = Image.new("1", (64, 64))
    ImageDraw.Draw(mask).polygon([(24, 19), (27, 16), (36, 16), (39, 19), (39, 36), (24, 36)], fill=1)
    for y in range(16, 37):
        for x in range(24, 40):
            if mask.getpixel((x, y)):
                light = max(0, 1 - abs(x - 29) / 12.0)
                grain = ((x * 7 + y * 11) % 7) - 3
                pixels[x, y] = (int(67 + 66 * light) + grain,
                                int(13 + 12 * light), int(22 + 12 * light), 255)
    d.line([(24, 35), (24, 19), (27, 16), (36, 16)], fill=(226, 174, 79))
    d.line([(39, 19), (39, 36)], fill=(90, 48, 21))
    # Small diamond stitching and upholstered buttons.
    for cy in (22, 29):
        d.line([(25, cy), (31, cy - 4), (38, cy)], fill=(93, 21, 28))
        d.line([(25, cy), (31, cy + 4), (38, cy)], fill=(93, 21, 28))
        d.point((31, cy), fill=(238, 176, 87))
        d.point((32, cy + 1), fill=(46, 10, 17))
    # Feet and gold-carved arm supports.
    for x in (17, 43):
        d.polygon([(x, 38), (x + 5, 38), (x + 3, 54), (x - 1, 54)], fill=dark)
        d.line([(x + 1, 40), (x + 1, 52)], fill=gold, width=2)
        d.line([(x, 53), (x + 3, 53)], fill=shine)
    d.polygon([(15, 33), (21, 32), (24, 37), (18, 40), (14, 38)], fill=dark)
    d.polygon([(40, 37), (43, 32), (49, 33), (50, 38), (45, 40)], fill=dark)
    d.polygon([(15, 33), (20, 33), (23, 36), (17, 38), (15, 37)], fill=gold)
    d.polygon([(41, 36), (44, 33), (48, 33), (48, 37), (45, 38)], fill=gold)
    d.line([(15, 33), (20, 33), (22, 35)], fill=shine)
    d.line([(42, 35), (44, 33), (48, 33)], fill=shine)
    d.ellipse((14, 29, 19, 34), fill=shade, outline=gold)
    d.ellipse((44, 29, 49, 34), fill=shade, outline=gold)
    d.point((15, 30), fill=shine)
    d.point((45, 30), fill=shine)
    # Seat in perspective and the thick, ornamented front rail.
    d.polygon([(24, 35), (39, 35), (44, 41), (20, 41)], fill=(56, 12, 21))
    d.polygon([(25, 36), (38, 36), (42, 40), (22, 40)], fill=(152, 32, 43))
    d.line([(25, 36), (38, 36)], fill=(203, 65, 64))
    d.rectangle((20, 41, 44, 44), fill=shade)
    d.line([(20, 41), (44, 41)], fill=shine)
    d.line([(21, 43), (43, 43)], fill=gold)
    for x in (25, 31, 37):
        d.point((x, 43), fill=shine)
    # Original Civ4 buttons have rounded alpha corners, without a gold frame.
    with Image.open(ROOT / "Awakened RFC/Assets/Art/Interface/Buttons/civics_civilizations_religions_atlas.dds") as atlas:
        im.putalpha(atlas.convert("RGBA").crop((0, 0, 64, 64)).getchannel("A"))
    return im


if __name__ == "__main__":
    icon = render()
    icon.save(ART / "monarchy-pixel.png")
    icon.save(DEST, pixel_format="DXT3")
    # Preview the actual compressed game asset, not just the uncompressed source.
    with Image.open(DEST) as dds:
        dds.resize((384, 384), Image.Resampling.NEAREST).save(ART / "monarchy-pixel-preview.local.png")
    print("Created Monarchy.dds: 64 x 64, DXT3, original corner alpha.")
