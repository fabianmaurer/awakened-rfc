"""Convert generated civic artwork to Civ4's original 64px DXT3 DDS format.

Run using a Python environment with Pillow installed:
    python art/civics/prepare_icons.py art/civics/sources.local.json

The local source manifest maps civic types to generated PNG paths. The original
full-resolution images stay in the image generator's output directory.
"""

import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    root = Path(__file__).resolve().parents[2]
    metadata = json.loads((root / "art/civics/generation.json").read_text())
    sources = json.loads(Path(sys.argv[1]).read_text())
    destination = root / "Awakened RFC/Assets/Art/Interface/Buttons/Civics/RFCMP"
    destination.mkdir(parents=True, exist_ok=True)
    with Image.open(root / "Awakened RFC/Assets/Art/Interface/Buttons/civics_civilizations_religions_atlas.dds") as atlas:
        corner_mask = atlas.convert("RGBA").crop((0, 0, 64, 64)).getchannel("A")
    preview = Image.new("RGB", (640, 700), (22, 27, 38))
    draw = ImageDraw.Draw(preview)
    for index, entry in enumerate(metadata["icons"]):
        with Image.open(sources[entry["type"]]) as original:
            icon = original.convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
        icon.putalpha(corner_mask)
        icon.save(destination / entry["filename"], pixel_format="DXT3")
        x = (index // 5) * 128 + 32
        y = (index % 5) * 140 + 10
        enlarged = icon.resize((96, 96), Image.Resampling.NEAREST)
        preview.paste(enlarged, (x - 16, y), enlarged)
        label = entry["filename"].replace(".dds", "").replace("_", " ")
        words = label.split()
        if len(label) > 19:
            label = " ".join(words[:-1]) + "\n" + words[-1]
        draw.multiline_text((x + 32, y + 102), label, fill="white", anchor="ma", align="center")
    preview.save(root / "art/civics/preview.png")

    path = root / "Awakened RFC/Assets/XML/GameInfo/CIV4CivicInfos.xml"
    xml = path.read_text(encoding="utf-8")
    for entry in metadata["icons"]:
        pattern = r"(<Type>" + re.escape(entry["type"]) + r"</Type>.*?<Button>)[^<]*(</Button>)"
        button = "Art/Interface/Buttons/Civics/RFCMP/" + entry["filename"]
        xml, count = re.subn(pattern, lambda match: match[1] + button + match[2], xml, flags=re.S)
        if count != 1:
            raise ValueError("Expected exactly one civic: " + entry["type"])
    path.write_text(xml, encoding="utf-8")
    print("Prepared 25 civic icons and updated their XML button paths.")


if __name__ == "__main__":
    main()
