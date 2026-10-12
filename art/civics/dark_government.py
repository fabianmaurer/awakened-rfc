"""Atmospheric government scenes, drawn at native 64px with Pillow."""
from math import hypot
from PIL import Image, ImageDraw
from draw_monarchy import render as throne


def scene(tint, lights):
    im = Image.new('RGBA', (64, 64))
    for y in range(64):
        for x in range(64):
            rgb = list(tint)
            for cx, cy, radius, color in lights:
                strength = max(0, 1 - hypot(x-cx, y-cy)/radius)**2
                rgb = [v + c*strength for v, c in zip(rgb, color)]
            grain = ((x*19+y*37+x*y*3) % 9)-4
            im.putpixel((x,y), tuple(max(0,min(255,int(v)+grain)) for v in rgb)+(255,))
    return im


def flame(d, x, y, scale=1):
    d.polygon([(x-3,y+3),(x-4,y-2),(x,y-10*scale),(x+1,y-3),(x+4,y),(x+2,y+4)], fill='#bf501e')
    d.polygon([(x-1,y+2),(x,y-5),(x+2,y),(x+1,y+3)], fill='#ffcf76')


def figure(d, x, y, robe, rim, hood=True):
    # Small cloaked human silhouette; head is deliberately kept readable.
    d.polygon([(x-3,y+5),(x+3,y+5),(x+7,y+20),(x-7,y+20)], fill=robe)
    d.line([(x-3,y+7),(x-5,y+18)], fill=rim)
    d.ellipse((x-4,y-3,x+4,y+6), fill=robe)
    if hood:
        d.ellipse((x-2,y,x+2,y+5), fill='#100e14')
        d.line([(x-3,y),(x-1,y-2),(x+2,y-1)], fill=rim)
    else:
        d.ellipse((x-2,y-1,x+2,y+4), fill=rim)


def weather(im):
    # Weathered pigments and a gentle vignette, without obscuring focal objects.
    for y in range(64):
        for x in range(64):
            r,g,b,a=im.getpixel((x,y))
            grain=((x*13+y*23+x*y*11)%7)-3
            edge=max(0,(hypot(x-31.5,y-30)/43-.55))*.48
            im.putpixel((x,y), tuple(max(0,min(255,int(v*(1-edge))+grain)) for v in (r,g,b))+(a,))
    return im


def tribal():
    im=scene((13,18,24),[(31,42,40,(123,61,18)),(17,12,30,(10,25,40))])
    d=ImageDraw.Draw(im)
    # Black pines, distant ridge, and a council gathered around an ember hearth.
    d.polygon([(0,27),(12,17),(20,24),(36,14),(54,23),(63,18),(63,46),(0,46)], fill='#181e25')
    for x,y in [(5,9),(57,4),(13,15),(49,13)]:
        d.polygon([(x,y),(x-6,y+25),(x+6,y+25)], fill='#0c151b')
        d.line([(x,y+9),(x,y+37)],fill='#11161c',width=2)
    d.polygon([(0,52),(25,45),(46,47),(64,54),(64,64),(0,64)],fill='#211b1b')
    figure(d,14,30,'#393234','#a57648')
    figure(d,49,29,'#292c30','#7c6549')
    figure(d,31,21,'#443b32','#c69961')
    # Antlered elder behind the fire, distinct from the two seated companions.
    for side in [-1,1]:
        d.line([(31+side*3,22),(31+side*7,16),(31+side*8,9)],fill='#b1a086')
        d.line([(31+side*7,16),(31+side*11,12)],fill='#b1a086')
    d.line([(12,27),(10,51)],fill='#997044',width=2)
    d.polygon([(12,20),(9,29),(14,28)],fill='#c3b59a')
    for box in [(21,49,27,53),(27,52,35,55),(37,49,44,53)]:
        d.ellipse(box,fill='#756452')
    d.line([(24,48),(39,51)],fill='#6a3925',width=3)
    flame(d,31,45,2)
    flame(d,37,46)
    for p in [(28,29),(37,34),(33,21)]: d.point(p,fill='#edb067')
    return weather(im)


def monarchy():
    im=scene((13,12,22),[(31,26,43,(58,28,17)),(9,40,28,(87,39,11)),(55,40,28,(87,39,11))])
    d=ImageDraw.Draw(im)
    # Vaulted hall and torn royal drapery behind the old throne illustration.
    d.line([(7,59),(7,23),(15,9),(31,2),(48,9),(57,23),(57,59)],fill='#65534b',width=2)
    for x in (12,50):
        d.polygon([(x,14),(x+3,12),(x+3,44),(x+1,40),(x,47)],fill='#4e1d29')
    old=throne()
    # Replace only the original backdrop, retaining the throne and stone dais.
    for y in range(4,59):
        for x in range(10,54):
            r,g,b,a=old.getpixel((x,y))
            if (r>65 and r>g*1.15) or (y>=51 and r>55):
                im.putpixel((x,y),(int(r*.86),int(g*.80),int(b*.82),255))
    d=ImageDraw.Draw(im)
    for x in (7,56):
        d.line([(x,42),(x,54)],fill='#78624b',width=2)
        flame(d,x,39)
    d.line([(26,58),(20,63)],fill='#342b30')
    return weather(im)


def republic():
    im=scene((13,19,28),[(29,22,42,(39,50,62)),(47,39,23,(73,39,18))])
    d=ImageDraw.Draw(im)
    # Monumental senate with an illuminated chamber and council silhouettes.
    d.polygon([(4,24),(31,7),(60,24)],fill='#777974',outline='#252a31')
    d.polygon([(10,22),(31,11),(53,22)],fill='#a6a08b')
    d.polygon([(18,21),(31,14),(44,21)],fill='#464e55')
    d.rectangle((10,25,54,49),fill='#161820')
    d.ellipse((22,26,41,45),fill='#59402c')
    for x in (10,22,40,52):
        d.rectangle((x-2,25,x+3,28),fill='#96968b')
        d.rectangle((x-1,29,x+2,48),fill='#626d73')
        d.line([(x-1,29),(x-1,47)],fill='#b9b5a0')
        d.rectangle((x-2,48,x+3,50),fill='#8e948c')
    d.rectangle((7,51,57,53),fill='#65696b')
    d.rectangle((3,54,61,57),fill='#454c55')
    for x,y in [(27,36),(36,35),(18,48),(45,48)]:
        figure(d,x,y,'#24222a','#8a8172')
    d.line([(28,46),(38,46)],fill='#b99562',width=2)
    flame(d,48,38)
    return weather(im)


def dictatorship():
    im=scene((20,13,22),[(37,24,44,(58,23,23))])
    d=ImageDraw.Draw(im)
    # Wind-whipped crimson banner behind a shadowed armored overlord.
    d.line([(12,6),(12,59)],fill='#867363',width=2)
    d.polygon([(13,9),(29,6),(42,12),(60,8),(56,34),(43,39),(29,31),(14,34)],fill='#702733')
    d.polygon([(14,10),(28,8),(31,29),(16,32)],fill='#9d3c3d')
    d.polygon([(43,14),(58,10),(54,31),(44,36)],fill='#491d2c')
    d.line([(15,10),(28,8),(42,14),(57,10)],fill='#b46955')
    # A helmeted ruler, oversized shoulders and a heavy black cloak.
    d.polygon([(20,34),(31,29),(44,34),(58,63),(8,63)],fill='#171a24')
    d.polygon([(18,35),(28,31),(29,41),(13,45)],fill='#626269')
    d.polygon([(35,31),(45,35),(51,45),(35,41)],fill='#393e4c')
    d.line([(19,35),(27,32)],fill='#b3a18c',width=2)
    d.polygon([(24,19),(31,14),(39,19),(38,30),(32,35),(25,29)],fill='#5b626b',outline='#12151d')
    d.polygon([(25,20),(30,17),(30,30),(26,27)],fill='#9c9a8c')
    d.line([(25,24),(37,24)],fill='#13151d',width=2)
    d.line([(31,18),(32,32)],fill='#b4ac99')
    d.line([(35,43),(49,60)],fill='#5a2630',width=4)
    d.line([(21,46),(17,61)],fill='#45454e')
    return weather(im)


def democracy():
    im=scene((12,22,29),[(29,29,40,(43,50,44)),(8,28,20,(65,37,15))])
    d=ImageDraw.Draw(im)
    # A public vote in a torchlit square: varied citizens, foreground hand and ballot.
    d.polygon([(0,23),(11,12),(19,23),(27,15),(42,22),(55,12),(64,22),(64,49),(0,49)],fill='#26313a')
    for x,y in [(10,28),(23,26),(38,28),(53,25)]:
        figure(d,x,y,'#303035','#88806b')
    flame(d,5,26)
    d.polygon([(15,43),(43,38),(57,47),(28,53)],fill='#8b6845',outline='#181b22')
    d.polygon([(15,43),(28,53),(28,64),(15,57)],fill='#403a35')
    d.polygon([(28,53),(57,47),(57,61),(28,64)],fill='#65503c')
    d.line([(25,45),(45,42)],fill='#161921',width=3)
    d.line([(28,54),(55,49)],fill='#aa8960')
    # Human hand extending from a blue sleeve rather than an isolated symbol.
    d.polygon([(62,7),(47,16),(50,27),(63,20)],fill='#3c5668')
    d.line([(49,17),(53,23)],fill='#8b9c9d',width=2)
    d.polygon([(47,17),(41,17),(34,24),(34,29),(38,31),(43,25),(50,24)],fill='#b89c7b',outline='#51433d')
    d.polygon([(25,25),(40,27),(37,44),(23,42)],fill='#d5c9a4',outline='#706854')
    d.line([(28,33),(31,37),(36,30)],fill='#3e5553',width=2)
    d.line([(38,25),(42,21),(47,21)],fill='#e1c49a',width=2)
    d.rectangle((40,55,44,60),fill='#a18c5a')
    d.point((42,57),fill='#272b2c')
    return weather(im)
