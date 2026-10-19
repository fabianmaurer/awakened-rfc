"""Build dormant holy-city glyphs in religion-section slots 28-34.

Run with the existing .venv-art Python (Pillow). Original glyphs, alpha masks,
font delimiters and all existing symbol slots are preserved.
"""
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1] / "Awakened RFC/Assets/res/Fonts"


def build(name, width, height, religion_y, destination_y):
    path = ROOT / name
    atlas = Image.open(path).convert("RGBA")
    for religion in range(7):
        source_x = (2 * religion + 1) * width
        glyph = atlas.crop((source_x, religion_y,
                            source_x + width, religion_y + height))
        pixels = []
        for red, green, blue, alpha in [glyph.getpixel((x, y))
                                        for y in range(height) for x in range(width)]:
            # Magenta borders and cyan width markers are font metadata.
            if (red, green, blue) in ((255, 0, 255), (0, 255, 255)):
                pixels.append((red, green, blue, alpha))
            else:
                grey = 32 + (299 * red + 587 * green + 114 * blue) * 65 // 100000
                pixels.append((grey, grey, grey, alpha))
        glyph.putdata(pixels)
        # Seven religions and seven corporations occupy slots 0-27.
        atlas.paste(glyph, ((3 + religion) * width, destination_y))
    atlas.save(path)
    print("Updated " + str(path))


if __name__ == "__main__":
    build("GameFont.tga", 22, 21, 135, 156)
    build("GameFont_75.tga", 17, 17, 90, 107)
