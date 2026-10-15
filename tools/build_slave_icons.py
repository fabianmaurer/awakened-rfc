"""Draw 64px slave unit buttons using the approved captive and weapon overlays."""
from pathlib import Path
import re
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'art/slaves/icon-proposals'))
from preview_icons import draw_axe, SOURCE

DEST = ROOT / 'Awakened RFC/Assets/Art/Interface/Buttons/Units/SlaveUnits'
ART = ROOT / 'art/slaves'
S = 4
TIERS = ('SLAVE', 'ARMED_SLAVE', 'SLAVE_SWORDSMAN', 'SLAVE_MACEMAN',
         'SLAVE_MUSKETMAN', 'SLAVE_RIFLEMAN', 'SLAVE_INFANTRY', 'SLAVE_MODERN_INFANTRY')
LABELS = ('Slave', 'Bronze axe', 'Sword', 'Mace', 'Musket', 'Rifle', 'Infantry', 'Modern infantry')
RANKS = ('', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII')


def rank_icon(icon, rank):
    """Outlined gold Roman numeral, inset from the button's rounded border."""
    overlay = Image.new('RGBA', (64*S, 64*S))
    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype('timesbd.ttf', 18*S)
    except OSError:
        font = ImageFont.load_default(size=17*S)
    draw.text((56*S, 55*S), rank, font=font, anchor='rb',
              fill=(255, 230, 161, 255), stroke_width=S,
              stroke_fill=(15, 10, 6, 255))
    return Image.alpha_composite(icon, overlay.resize((64,64), Image.Resampling.LANCZOS))


def enlarge_overlay(image):
    """Increase visual weight without touching the rounded button border."""
    # Ignore the almost invisible shadow halo when fitting the artwork;
    # otherwise the halo makes the actual weapon shrink instead of grow.
    bounds=image.getchannel('A').point(lambda v:255 if v>40 else 0).getbbox()
    crop=image.crop(bounds)
    factor=min(1.24,40/crop.width,51/crop.height)
    size=(round(crop.width*factor),round(crop.height*factor))
    crop=crop.resize(size,Image.Resampling.LANCZOS)
    x=max(4,min(44-size[0],round((bounds[0]+bounds[2]-size[0])/2)))
    y=max(6,min(57-size[1],round((bounds[1]+bounds[3]-size[1])/2)))
    result=Image.new('RGBA',(64,64))
    result.alpha_composite(crop,(x,y))
    # Outline the visible weapon rather than its soft shadow. Draw at 4x
    # resolution so the roughly one-pixel contour stays smooth at native size.
    large=result.resize((64*S,64*S),Image.Resampling.LANCZOS)
    mask=large.getchannel('A').point(lambda v:255 if v>150 else 0)
    contour=mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(.35*S))
    outlined=Image.new('RGBA',large.size,(12,9,7,0))
    outlined.putalpha(contour)
    outlined.alpha_composite(large)
    return outlined.resize((64,64),Image.Resampling.LANCZOS)


def weapon(kind):
    if kind == 'ARMED_SLAVE':
        return enlarge_overlay(draw_axe())
    layer = Image.new('RGBA', (64*S, 64*S))
    d = ImageDraw.Draw(layer)
    # Local coordinates run along the diagonal weapon, leaving the captive's
    # face and the button border visible. Positive v points toward the muzzle.
    def point(u, v):
        return ((20 + .89*u + .45*v)*S, (44 + .45*u - .89*v)*S)
    def poly(points, fill):
        d.polygon([point(u,v) for u,v in points], fill=fill)
    def line(points, fill, width=1):
        d.line([point(u,v) for u,v in points], fill=fill, width=round(width*S))
    def dot(u,v,r,fill):
        x,y=point(u,v)
        d.ellipse((x-r*S,y-r*S,x+r*S,y+r*S),fill=fill)
    dark=(19,15,12,255); steel=(139,151,151,255)
    light=(229,229,208,255); wood=(109,62,30,255); gold=(174,132,65,255)
    if kind == 'SLAVE_SWORDSMAN':
        poly([(-2,-13),(2,-13),(2,-1),(4,0),(3,25),(0,33),(-3,25),(-4,0),(-2,-1)],dark)
        poly([(-2.7,2),(2.7,2),(2.1,25),(0,31),(-2.1,25)],steel)
        poly([(-2.7,2),(0,2),(0,31),(-2.1,25)],light)
        line([(0,3),(0,25)],(93,107,113,255),.6)
        line([(-5,0),(5,0)],dark,3)
        line([(-5,0),(5,0)],gold,1.5)
        line([(0,-11),(0,-2)],wood,2.5)
        for v in (-9,-7,-5): line([(-1,v),(1,v+.5)],gold,.6)
        dot(0,-12,1.8,gold)
    elif kind == 'SLAVE_MACEMAN':
        line([(0,-13),(0,16)],dark,5)
        line([(0,-12),(0,15)],wood,2.8)
        line([(-.8,-11),(-.8,14)],(182,126,64,255),.7)
        line([(0,15),(-10,17),(-15,24)],dark,2.5)
        line([(0,15),(-10,17),(-15,24)],steel,1)
        for u,v in ((-3,15.7),(-7,16.5),(-11,18.5),(-13,21)):
            dot(u,v,.8,light)
        for du,dv in ((0,7),(0,-7),(7,0),(-7,0),(5,5),(-5,5),(5,-5),(-5,-5)):
            poly([(-15+du*.45,27+dv*.45),(-15+du,27+dv),(-15+du*.45-dv*.3,27+dv*.45+du*.3)],dark)
        dot(-15,27,4.8,dark)
        dot(-15,27,3.8,steel)
        dot(-16,28,2,(191,198,185,255))
        for u,v in ((-17,26),(-13,27),(-15,30)):dot(u,v,.7,dark)
        for v in (-10,-7,-4):line([(-1.4,v),(1.4,v)],dark,.7)
    else:
        # A true side profile: broad butt at the lower left, muzzle at the
        # upper right. Positive u is the underside, so trigger, pistol grip
        # and magazine consistently hang below the barrel, never above it.
        modern = kind == 'SLAVE_MODERN_INFANTRY'
        infantry = kind == 'SLAVE_INFANTRY'
        musket = kind == 'SLAVE_MUSKETMAN'
        end = 30 if musket else (28 if kind == 'SLAVE_RIFLEMAN' else (26 if infantry else 23))
        def point(u, v):
            return ((20 + .77*u + .64*v)*S, (42 + .64*u - .77*v)*S)
        # Wide wooden shoulder stock, with a visibly flat butt plate.
        stock=[(-2,-17),(4,-17),(5,-10),(2,-6),(2,3),(-2,3),(-2,-7),(-3,-10)]
        poly(stock,dark)
        poly([(-1,-16),(3,-16),(4,-10),(1,-6),(1,2),(-1,2),(-1,-8),(-2,-10)],wood)
        line([(-.8,-15),(-1.5,-10),(-.3,-7)],(203,149,81,255),1)
        line([(-2,-17),(4,-17)],(102,111,111,255),1.5)
        # Barrel sits above the wood; dark outline and a silver top edge.
        line([(-1,-1),(-1,end)],dark,4)
        line([(-1.4,1),(-1.4,end)],steel,2)
        line([(-2,2),(-2,end-1)],light,.7)
        if musket:
            # Full wooden fore-end and brass barrel bands/flintlock.
            line([(1,1),(1,19)],wood,3.6)
            line([(0,2),(0,18)],(185,127,61,255),.8)
            for v in (6,14,19):line([(-2.2,v),(2.4,v)],gold,1.2)
            poly([(1,-3),(3,-3),(3,2),(1,2)],gold)
            line([(2,0),(4,3),(3,5)],steel,1.3)
        else:
            poly([(-3,-4),(2,-4),(2,9),(-3,9)],dark)
            poly([(-2,-3),(1,-3),(1,8),(-2,8)],(90,103,104,255))
            line([(-2,-2),(-2,8)],(193,199,187,255),.8)
            if not modern:
                line([(1,3),(4,2)],steel,1.6)
                dot(4,2,1.2,dark)
                line([(1,9),(1,18 if infantry else 15)],wood,4)
                line([(0,10),(0,17 if infantry else 14)],(181,128,69,255),.8)
                line([(-2,14),(3,14)],dark,1)
        # Trigger guard below the action, distinct from the stock.
        line([(2,-5),(5,-5),(5,-1),(2,-1)],dark,1.2)
        line([(2.3,-4.4),(4.2,-4.4),(4.2,-1.5)],steel,.7)
        if infantry:
            # Springfield's short underside magazine / floor plate.
            poly([(2,0),(4,0),(4,5),(2,5)],dark)
            line([(3,1),(3,4)],steel,.8)
        if modern:
            # AK-style wood foregrip, separate pistol grip, curved magazine.
            line([(1,10),(1,16)],dark,5)
            line([(1,11),(1,15)],wood,3.3)
            line([(0,11),(0,15)],(198,139,68,255),.7)
            poly([(2,-4),(5,-5),(8,-9),(5,-11),(3,-7)],dark)
            line([(4,-6),(6,-9)],wood,2)
            poly([(2,2),(7,1),(10,3),(12,7),(11,10),(8,8),(7,5),(2,5)],dark)
            poly([(3,2.6),(6,2),(9,4),(10.5,7.5),(10,8),(8.5,6.5),(7.5,4),(3,4)],steel)
            line([(6,2.5),(8.5,4.5),(10,7)],(184,189,171,255),.6)
            line([(-2,end-3),(-4,end-3)],dark,2)
        line([(-2,end),(.2,end)],dark,1.2)
    shadow = Image.new('RGBA',layer.size)
    shadow.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(S*.8)).point(lambda v:int(v*.85)))
    shadow.alpha_composite(layer)
    return enlarge_overlay(shadow.resize((64,64),Image.Resampling.LANCZOS))


def main():
    DEST.mkdir(parents=True,exist_ok=True)
    source = ART / 'slave-icon-source.png'
    if not source.exists():
        Image.open(SOURCE).convert('RGBA').save(source)
    base = Image.open(source).convert('RGBA')
    sheet = Image.new('RGB',(800,456),(27,26,25))
    draw = ImageDraw.Draw(sheet)
    for i,tier in enumerate(TIERS):
        icon = base.copy() if tier == 'SLAVE' else Image.alpha_composite(base,weapon(tier))
        if RANKS[i]:
            icon = rank_icon(icon, RANKS[i])
        icon.save(ART / (tier.lower()+'-icon.png'))
        icon.save(DEST / (tier+'.dds'),pixel_format='DXT3')
        x,y=(i%4)*200,(i//4)*228
        large=icon.resize((160,160),Image.Resampling.NEAREST)
        sheet.paste(large,(x+20,y+8),large)
        sheet.paste(icon,(x+68,y+173),icon)
        draw.text((x+8,y+213),LABELS[i],fill=(231,224,207))
    sheet.save(ART/'unit-icons.png')
    path=ROOT/'Awakened RFC/Assets/XML/Art/CIV4ArtDefines_Unit.xml'
    text=path.read_text(encoding='utf-8')
    def patch(match):
        block=match.group()
        for tier in TIERS:
            if re.search(r'<Type>ART_DEF_UNIT_'+tier+r'_[AB]</Type>',block):
                button='Art/Interface/Buttons/Units/SlaveUnits/'+tier+'.dds'
                return re.sub(r'<Button>.*?</Button>','<Button>'+button+'</Button>',block,flags=re.S)
        return block
    path.write_text(re.sub(r'<UnitArtInfo>.*?</UnitArtInfo>',patch,text,flags=re.S),encoding='utf-8')
    print('Created eight 64x64 DXT3 slave icons and updated both art variants.')


if __name__ == '__main__':
    main()
