"""Compensate for the in-game flag's horizontal squeeze and export legacy DDS."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art'
DEST = ROOT / 'Awakened RFC/Assets/Art/Interface/TeamColor'
NAMES = ('Arabia', 'Abbasid', 'Fatimid', 'Umayyad', 'Papal')


def main():
    previews = []
    for name in NAMES:
        source = ART / 'caliphate' / (name + '-source.png')
        if name == 'Papal':
            source = ART / 'papal/banner-source.png'
        # In-game feedback confirmed horizontal squeezing, not stretching.
        # Widen the artwork relative to its height without cropping any of it.
        emblem = Image.open(source).convert('RGB').resize((128, 96), Image.Resampling.LANCZOS)
        texture = Image.new('RGB', (128, 128))
        texture.paste(emblem.crop((0, 0, 128, 1)).resize((128, 16)), (0, 0))
        texture.paste(emblem, (0, 16))
        texture.paste(emblem.crop((0, 95, 128, 96)).resize((128, 16)), (0, 112))
        texture = texture.convert('RGBA')
        texture.putalpha(0)  # Civ4 team-color mask: zero retains RGB artwork.
        path = DEST / ('FlagDECAL_' + name + '.dds')
        texture.save(path, pixel_format='DXT3')
        # Approximate the reported horizontal squeeze for the local preview.
        preview = Image.open(path).convert('RGB').resize((96, 128), Image.Resampling.LANCZOS)
        previews.append(preview)
        print(name + ': 128x128 DXT3, complete artwork fitted to 128x96')

    sheet = Image.new('RGB', (384, 152), '#e7dfcf')
    draw = ImageDraw.Draw(sheet)
    for i, name in enumerate(NAMES[:4]):
        sheet.paste(previews[i], (96 * i, 24))
        draw.text((96 * i + 6, 5), name, fill='black')
    sheet.save(ART / 'caliphate/banner-preview.png')
    previews[4].save(ART / 'papal/banner-preview.png')


if __name__ == '__main__':
    main()
