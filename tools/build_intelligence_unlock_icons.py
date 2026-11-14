"""Draw the shared intelligence tech-unlock button family. Run with .venv-art."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'Awakened RFC/Assets/Art/Interface/Buttons/Intelligence'
S = 4
GOLD = '#e7c779'
INK = '#142438'
PALE = '#f0e4bb'
NAMES = ('Technology', 'Military', 'Political', 'Economic', 'Cooperation', 'Dynastic')


def icon(kind):
    image = Image.new('RGBA', (64*S, 64*S))
    d = ImageDraw.Draw(image)

    def line(points, fill=PALE, width=3):
        d.line([(x*S, y*S) for x, y in points], fill=fill, width=width*S, joint='curve')

    def polygon(points, fill=PALE):
        d.polygon([(x*S, y*S) for x, y in points], fill=fill)

    def ellipse(box, fill, outline=None, width=1):
        d.ellipse(tuple(v*S for v in box), fill=fill, outline=outline, width=width*S)

    d.rounded_rectangle((2*S, 2*S, 62*S, 62*S), radius=9*S, fill=INK, outline=GOLD, width=2*S)
    d.rounded_rectangle((6*S, 6*S, 58*S, 58*S), radius=6*S, outline='#53677a', width=S)

    if kind == 'Technology':
        polygon([(14, 17), (29, 20), (32, 23), (35, 20), (50, 17), (50, 39), (35, 42), (32, 45), (29, 42), (14, 39)])
        line([(32, 23), (32, 42)], INK, 2)
        for y in (25, 31):
            line([(19, y), (27, y+2)], INK, 1)
            line([(37, y+2), (45, y)], INK, 1)
    elif kind == 'Military':
        for flip in (False, True):
            pts = [(18, 39), (39, 15), (45, 12), (43, 19), (22, 43)]
            polygon([(64-x if flip else x, y) for x, y in pts])
            pts = [(15, 36), (25, 45)]
            line([(64-x if flip else x, y) for x, y in pts], GOLD, 3)
    elif kind == 'Political':
        polygon([(13, 23), (32, 12), (51, 23)], GOLD)
        for x in (19, 30, 41):
            d.rectangle((x*S, 26*S, (x+4)*S, 39*S), fill=PALE)
        line([(14, 42), (50, 42)], GOLD, 4)
    elif kind == 'Economic':
        line([(14, 14), (14, 41), (51, 41)], '#53677a', 2)
        line([(17, 35), (25, 26), (32, 31), (45, 16), (50, 20)], GOLD, 4)
        for x, y in ((17, 35), (25, 26), (32, 31), (45, 16), (50, 20)):
            ellipse((x-2, y-2, x+2, y+2), PALE)
    elif kind == 'Cooperation':
        ellipse((12, 19, 35, 39), None, PALE, 4)
        ellipse((29, 19, 52, 39), None, GOLD, 4)
    elif kind == 'Dynastic':
        polygon([(14, 19), (24, 27), (32, 13), (40, 27), (50, 19), (46, 40), (18, 40)], GOLD)
        line([(19, 36), (45, 36)], INK, 2)
        for x, y in ((14, 17), (32, 12), (50, 17)):
            ellipse((x-2, y-2, x+2, y+2), PALE)

    # The same eye badge on every focus identifies intelligence at small sizes.
    d.rounded_rectangle((20*S, 46*S, 44*S, 59*S), radius=5*S, fill=INK, outline=GOLD, width=S)
    polygon([(23, 52), (27, 49), (37, 49), (41, 52), (37, 55), (27, 55)], GOLD)
    ellipse((29, 49, 35, 55), INK)
    ellipse((31, 50, 33, 52), PALE)
    return image.resize((64, 64), Image.Resampling.LANCZOS)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    preview = Image.new('RGB', (6*80, 80), '#292d35')
    for i, name in enumerate(NAMES):
        result = icon(name)
        result.save(DEST / ('Unlock' + name + '.dds'), pixel_format='DXT3')
        disabled = ImageOps.colorize(result.convert('L'), '#111a25', '#83909c').convert('RGBA')
        disabled.putalpha(result.getchannel('A'))
        disabled.save(DEST / ('Unlock' + name + 'Disabled.dds'), pixel_format='DXT3')
        preview.paste(result, (i*80+8, 8), result)
    output = ROOT / 'art/intelligence-unlocks.png'
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.with_suffix('.tmp.png')
    preview.save(staging)
    staging.replace(output)
    print('Generated six intelligence unlock buttons; preview:', output)


if __name__ == '__main__':
    main()
