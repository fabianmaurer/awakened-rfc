"""Convert the generated civic variant artwork into Civ4's 64px DXT3 buttons."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/civic-variants'
DEST = ROOT / 'Awakened RFC/Assets/Art/Interface/Buttons/civics/RFCMP'
NAMES = ('Pharaonic_Kingship', 'Divine_Kingship', 'Bushido')


def main():
    preview = Image.new('RGB', (64 * len(NAMES), 64), '#101a22')
    for i, name in enumerate(NAMES):
        icon = Image.open(SOURCE / (name + '.png')).convert('RGBA')
        icon = icon.resize((64, 64), Image.Resampling.LANCZOS)
        icon.save(DEST / (name + '.dds'), pixel_format='DXT3')
        preview.paste(icon, (64 * i, 0))
    preview.save(SOURCE / 'preview.png')
    print('Created three 64x64 DXT3 civic variant buttons.')


if __name__ == '__main__':
    main()
