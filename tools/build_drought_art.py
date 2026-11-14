"""Prepare Civ4 floodplain DDS variants from the checked-in generated dry texture.

Run with .venv-art/Scripts/python.exe. Reuses the installed game's original
texture and alpha through the existing Assets reader; never changes river art.
"""
from pathlib import Path
import io
from PIL import Image
from build_slave_art import Assets, MOD


def main():
    source = Image.open(io.BytesIO(Assets().read(
        'base:Art/Terrain/Features/Floodplain/FloodPlain_baseALL.dds'))).convert('RGBA')
    dry = Image.open(MOD.parent / 'art/drought/FloodPlain_SevereDrought.png').convert('RGBA')
    dry = dry.resize(source.size, Image.Resampling.LANCZOS)
    dry.putalpha(source.getchannel('A'))
    folder = MOD / 'Assets/Art/Terrain/Features/Floodplain'
    folder.mkdir(parents=True, exist_ok=True)
    for name, image in (
            ('FloodPlain_Drought.dds', Image.blend(source, dry, .60)),
            ('FloodPlain_SevereDrought.dds', dry)):
        image.save(folder / name, pixel_format='DXT5')
        print(folder / name)


if __name__ == '__main__':
    main()
