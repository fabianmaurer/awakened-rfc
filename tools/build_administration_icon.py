"""Pack the approved administration ledger into the existing MAP_CHAR glyph.

Run with .venv-art/Scripts/python.exe. Preserve other glyphs and font metadata.
"""
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "art/administration/sealed-ledger.png"
FONTS = ROOT / "Awakened RFC/Assets/res/Fonts"


def build(name, row, height):
    path = FONTS / name
    atlas = Image.open(path).convert("RGBA")
    cells, start = [], 0
    for x in range(atlas.width):
        if atlas.getpixel((x, row))[:3] == (255, 0, 255):
            if x > start:
                cells.append((start, x))
            start = x + 1
    left, right = cells[20]  # MAP_CHAR, used for administration.
    source = Image.open(SOURCE).convert("RGBA")
    source = source.crop(source.getchannel("A").getbbox())
    source.thumbnail((right - left, height), Image.Resampling.LANCZOS)
    glyph = Image.new("RGBA", (right - left, height))
    glyph.paste(source, ((glyph.width - source.width) // 2,
                         (height - source.height) // 2))
    # Delimiter rows and columns lie outside this rectangle.
    atlas.paste(glyph, (left, row))
    atlas.save(path)
    print("Updated " + str(path))


if __name__ == "__main__":
    build("GameFont.tga", 240, 20)
    build("GameFont_75.tga", 192, 16)
