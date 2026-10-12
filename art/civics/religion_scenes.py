"""Ceremonial religion portraits and a native-pixel burning scripture scene."""
from PIL import Image, ImageDraw
from math import sin
from dark_government import scene, weather
from reuse_government import portrait


def ceremonial(name):
    im=portrait(name)
    # Keep gilding and candlelit highlights richer than the military portraits.
    for y in range(64):
        for x in range(64):
            r,g,b,a=im.getpixel((x,y))
            if r>95 and g>65 and r>b*1.3:
                im.putpixel((x,y),(min(255,int(r*1.12)),min(255,int(g*1.08)),b,a))
    return im


def state_religion():
    return ceremonial('State_Religion')


def god_state():
    im=scene((17,14,27),[(31,15,48,(85,55,35))])
    d=ImageDraw.Draw(im)
    # Golden sanctuary occupying the whole scene, crimson state banners and a
    # processional stair: institutional sacred power rather than another priest.
    d.ellipse((20,1,45,26),fill='#685133',outline='#a5874b')
    d.ellipse((24,5,41,22),fill='#b69652',outline='#ead59b')
    for x in (5,54):
        d.rectangle((x,11,x+4,54),fill='#80654c')
        d.polygon([(x-2,12),(x+2,5),(x+6,12)],fill='#cfac63')
    d.polygon([(15,34),(15,22),(23,22),(23,16),(31,11),(40,17),(40,22),(48,22),(48,35)],fill='#aa874d',outline='#48352f')
    d.polygon([(12,25),(31,9),(51,25)],fill='#73533c',outline='#332733')
    d.polygon([(17,23),(31,12),(46,23)],fill='#d6b56c')
    d.polygon([(23,22),(31,16),(39,22)],fill='#82663c')
    d.line([(16,24),(48,24)],fill='#f0dca1',width=2)
    d.rectangle((16,26,47,46),fill='#3c292f')
    for x in (16,24,38,46):
        d.rectangle((x,27,x+3,46),fill='#aa8e54')
        d.line([(x,28),(x,45)],fill='#e0c989')
        d.line([(x+3,28),(x+3,45)],fill='#6c5138')
        d.rectangle((x-1,26,x+4,28),fill='#dbbd77')
        d.rectangle((x-1,45,x+4,47),fill='#c7a668')
    d.polygon([(29,45),(29,34),(32,30),(35,34),(35,45)],fill='#d6ae62')
    d.line([(32,34),(32,44)],fill='#f2d996')
    for x in (8,50):
        d.polygon([(x,19),(x+6,19),(x+6,43),(x+3,39),(x,44)],fill='#8e2939',outline='#411e2b')
        d.line([(x+1,20),(x+1,40)],fill='#c95a53')
        d.line([(x+3,24),(x+3,33)],fill='#d6b775')
        d.line([(x+1,27),(x+5,27)],fill='#d6b775')
    for y in range(48,63,3):
        spread=(y-48)//2
        d.rectangle((12-spread,y,51+spread,y+2),fill='#8d7552')
        d.line([(13-spread,y),(50+spread,y)],fill='#d4b981')
    d.polygon([(28,48),(36,48),(42,63),(22,63)],fill='#692533')
    d.line([(28,49),(22,62)],fill='#af734c')
    d.line([(36,49),(42,62)],fill='#af734c')
    return weather(im)


def ancestor_cult():
    im=scene((12,20,23),[(25,37,42,(96,56,27)),(45,17,40,(23,40,41))])
    d=ImageDraw.Draw(im)
    for x in (3,58):
        d.line([(x+3,0),(x,40),(x-5,62)],fill='#33332d',width=5)
        d.line([(x,18),(x+10,8)],fill='#414237',width=2)
    d.polygon([(0,50),(24,42),(45,46),(63,51),(63,63),(0,63)],fill='#292823')
    # Tall carved wooden ancestor mask with deep eye sockets and ochre paint.
    mask=Image.new('1',(64,64)); md=ImageDraw.Draw(mask)
    shape=[(21,9),(34,6),(44,13),(45,33),(38,45),(25,46),(17,34),(16,17)]
    md.polygon(shape,fill=1)
    for y in range(6,47):
        for x in range(16,46):
            if mask.getpixel((x,y)):
                shade=sin(x*.58+sin(y*.18))*9+max(0,1-abs(x-24)/22)*23
                im.putpixel((x,y),(int(95+shade),int(58+shade*.65),int(33+shade*.35),255))
    d=ImageDraw.Draw(im)
    d.line([(18,31),(18,18),(23,11),(33,8)],fill='#c39861')
    d.polygon([(20,20),(27,19),(28,24),(23,27),(20,24)],fill='#231d1c',outline='#a0794b')
    d.polygon([(33,20),(40,18),(41,23),(36,26),(32,24)],fill='#211d20',outline='#a0794b')
    d.line([(21,21),(26,20)],fill='#d1a36b')
    d.line([(34,21),(39,19)],fill='#bc935b')
    d.polygon([(30,17),(26,31),(32,32),(34,28)],fill='#bd9258',outline='#664128')
    d.line([(28,30),(32,30)],fill='#ebc184')
    d.polygon([(25,35),(36,33),(34,39),(28,40)],fill='#241d1d')
    for x in (28,31,34): d.line([(x,35),(x,37)],fill='#bfa472')
    for x,y in [(22,29),(38,28)]:
        d.line([(x,y),(x-1,y+7)],fill='#a84932',width=2)
    d.line([(24,13),(31,11),(37,13)],fill='#d0b07b')
    # Feathers, cord, beads, offerings and an incense bowl establish a ritual.
    d.line([(19,16),(10,12),(12,28)],fill='#b6a57b')
    d.polygon([(10,13),(7,23),(10,32),(13,22)],fill='#a49878')
    d.line([(10,15),(10,28)],fill='#ddd0a1')
    d.line([(39,13),(50,11),(49,25)],fill='#92704b')
    d.polygon([(50,12),(46,20),(49,29),(53,20)],fill='#786856')
    for x,y in [(22,42),(26,44),(30,45),(35,43),(39,40)]: d.ellipse((x,y,x+2,y+2),fill='#cbb17d')
    d.ellipse((21,48,43,57),fill='#583b2a',outline='#bb8b54')
    d.ellipse((23,49,41,53),fill='#272525')
    for x in (27,32,36): d.point((x,51),fill='#f0a459')
    d.line([(32,49),(29,43),(32,39),(34,34),(32,30)],fill='#928c7b')
    d.line([(35,46),(37,41),(35,38)],fill='#6b756c')
    for x,y in [(11,42),(49,41)]:
        d.rectangle((x,y,x+2,y+10),fill='#bdad86')
        d.polygon([(x+1,y-6),(x-1,y),(x+3,y)],fill='#f6c784')
    d.ellipse((6,53,18,58),fill='#9e764a',outline='#46382a')
    d.line([(9,54),(15,54)],fill='#d1a96b')
    d.ellipse((46,51,56,58),fill='#583b32',outline='#997151')
    return weather(im)


def tolerance():
    im=scene((15,21,29),[(32,32,48,(36,43,45))])
    d=ImageDraw.Draw(im)
    # Four equally sized compartments: equal standing under the state, without
    # implying religious agreement. No central or dominant religious symbol.
    d.line([(32,6),(32,57)],fill='#5c655f')
    d.line([(6,32),(57,32)],fill='#5c655f')
    d.line([(31,7),(31,56)],fill='#1c2931')
    d.line([(7,31),(56,31)],fill='#1c2931')
    # Christianity: a sculpted upright cross, upper left.
    d.rectangle((15,8,20,27),fill='#b7a679',outline='#4e483c')
    d.rectangle((10,13,25,18),fill='#b7a679',outline='#4e483c')
    d.line([(16,9),(16,25)],fill='#e5d5a5')
    d.line([(11,14),(24,14)],fill='#e5d5a5')
    # Islam: a crescent, upper right; the cutout follows the background exactly.
    moon=im.copy()
    d.ellipse((38,8,56,27),fill='#b7a679',outline='#ded1a0')
    for y in range(7,27):
        for x in range(44,59):
            if ((x-51)/8.0)**2+((y-15)/9.0)**2<=1:
                im.putpixel((x,y),moon.getpixel((x,y)))
    d=ImageDraw.Draw(im)
    # Judaism: interlaced Star of David, lower left.
    d.line([(17,36),(7,53),(27,53),(17,36)],fill='#4b4b40',width=4)
    d.line([(17,57),(7,40),(27,40),(17,57)],fill='#4b4b40',width=4)
    d.line([(17,36),(7,53),(27,53),(17,36)],fill='#c9b78a',width=2)
    d.line([(17,57),(7,40),(27,40),(17,57)],fill='#c9b78a',width=2)
    # Buddhism: eight-spoked Dharma wheel, lower right.
    d.ellipse((37,37,57,57),outline='#4b4b40',width=4)
    d.ellipse((38,38,56,56),outline='#c9b78a',width=2)
    for x,y in [(47,38),(53,41),(56,47),(53,53),(47,56),(41,53),(38,47),(41,41)]:
        d.line([(47,47),(x,y)],fill='#c9b78a',width=2)
    d.ellipse((44,44,50,50),fill='#e2cfa0',outline='#6f6951')
    return weather(im)


def state_atheism():
    im=scene((15,16,24),[(32,31,48,(119,50,12))])
    d=ImageDraw.Draw(im)
    # Iron grate, ash and a thick leather-bound holy book being consumed by fire.
    d.polygon([(0,48),(19,42),(43,43),(64,49),(64,64),(0,64)],fill='#242029')
    for x in range(6,62,9):
        d.line([(x,46),(x-7,63)],fill='#4d4850',width=2)
    d.line([(2,52),(62,52)],fill='#716259')
    d.line([(0,59),(62,59)],fill='#514954')
    # Long, irregular flames behind the book; no tidy standalone fire symbol.
    d.polygon([(10,48),(8,32),(15,38),(13,23),(20,29),(24,8),(28,20),
               (34,5),(36,23),(42,16),(41,32),(50,19),(48,36),(57,30),
               (54,47),(45,54),(22,55)],fill='#a03823')
    d.polygon([(13,46),(13,37),(21,40),(21,28),(26,18),(29,29),(33,15),
               (37,35),(44,28),(44,40),(51,34),(49,48),(29,53)],fill='#e47825')
    d.polygon([(20,45),(24,35),(27,38),(30,27),(35,40),(40,34),(44,44),
               (36,51),(26,50)],fill='#f6c664')
    # Red-black cover, raised spine, layered charred pages, conspicuous gold cross.
    d.polygon([(13,38),(39,29),(53,42),(27,54)],fill='#1d151f',outline='#10121c')
    d.polygon([(14,41),(39,32),(51,43),(27,54)],fill='#9c8665',outline='#382c2b')
    for dy in (0,2,4):
        d.line([(16,43+dy),(27,52+dy),(50,42+dy)],fill='#c5ae80')
    d.polygon([(12,37),(38,28),(52,40),(26,51)],fill='#66312c',outline='#271c24')
    d.line([(13,37),(26,49)],fill='#a66b42',width=2)
    d.line([(15,38),(37,30),(49,40),(27,49),(15,38)],fill='#b58b4d')
    d.line([(30,34),(36,43)],fill='#e4c779',width=3)
    d.line([(26,39),(39,34)],fill='#e4c779',width=3)
    # Curling burnt corner and foreground flames visibly eating the cover.
    d.polygon([(41,34),(52,40),(42,44),(45,39)],fill='#222027')
    d.line([(43,36),(49,40)],fill='#c95c27')
    d.polygon([(9,54),(9,42),(14,47),(18,36),(21,46),(26,40),(24,53),
               (19,59)],fill='#bf4e22')
    d.polygon([(13,54),(16,46),(18,51),(21,47),(20,56)],fill='#ffd381')
    d.polygon([(42,52),(43,43),(48,47),(50,35),(53,44),(57,40),(56,53)],fill='#d56a26')
    d.polygon([(47,52),(50,43),(52,50),(54,47),(54,54)],fill='#f9c36c')
    for p in [(19,15),(39,11),(48,26),(8,25),(30,3),(57,18)]:
        d.point(p,fill='#eea95c')
    return weather(im)
