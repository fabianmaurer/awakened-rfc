"""Reuse the first set's readable human portraits with subdued, darker pigments.

The 64px source PNGs are preserved in references/ so rebuilding is independent
of Git history and the original image generator's machine-local output.
"""
from pathlib import Path
from PIL import Image


def portrait(name):
    with Image.open(Path(__file__).resolve().parent / 'references' / (name+'.png')) as source:
        im = source.convert('RGBA')
    for y in range(64):
        for x in range(64):
            r,g,b,a = im.getpixel((x,y))
            # Desaturate the original bright gold/red, retain the face's highlights,
            # and let the corners recede into a cold, shadowed background.
            gray = .30*r + .59*g + .11*b
            edge = min(1, ((x-31.5)**2+(y-30)**2)/1700)
            light = .90-.20*edge
            rgb = [r*.78+gray*.22, g*.78+gray*.22, b*.78+gray*.22]
            im.putpixel((x,y), (int(rgb[0]*light*.94), int(rgb[1]*light*.96),
                               min(255,int(rgb[2]*light+5*edge)), a))
    return im
