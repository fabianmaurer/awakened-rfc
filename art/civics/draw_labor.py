"""Draw five atmospheric object studies directly at the native 64px size."""
from pathlib import Path
from math import sin
from PIL import Image, ImageDraw
from dark_government import scene, weather

ROOT=Path(__file__).resolve().parents[2]
ART=Path(__file__).resolve().parent
DEST=ROOT/'RFC MP Plus/Assets/Art/Interface/Buttons/Civics/RFCMP'


def wood(d,box):
    x,y,r,b=box
    d.rectangle(box,fill='#61442c',outline='#281f20')
    for yy in range(y+2,b,4):
        d.line([(x+1,yy),(r-1,yy+1)],fill='#91704a')
        d.line([(x+2,yy+2),(r-3,yy+2)],fill='#49362a')


def wheat(d,x,y):
    d.line([(x,y),(x-2,y+25)],fill='#8e7243')
    for i in range(6):
        yy=y+i*3
        d.polygon([(x,yy+4),(x-5,yy),(x-3,yy-2),(x+1,yy+2)],fill='#c9a763')
        d.polygon([(x+1,yy+4),(x+5,yy),(x+4,yy-2),(x,yy+2)],fill='#9b7b43')
        d.point((x-3,yy),fill='#e5cb8a')
    d.line([(x,y-4),(x,y+2)],fill='#e6cd87')


def self_sufficiency():
    im=scene((19,20,21),[(24,24,48,(84,62,28))])
    d=ImageDraw.Draw(im)
    # Pantry shelf and a rough basket full of grain, with earthenware stores.
    d.polygon([(0,17),(29,5),(63,18),(63,50),(0,50)],fill='#302d28')
    for x in (5,56): d.line([(x,18),(x,52)],fill='#514a39',width=2)
    wood(d,(0,47,63,63))
    d.ellipse((40,25,59,49),fill='#7b4f35',outline='#211e21')
    d.rectangle((44,22,55,29),fill='#855c3c')
    d.ellipse((43,21,56,25),fill='#a58958',outline='#3b3029')
    d.arc((42,28,58,47),100,265,fill='#ba8c54',width=2)
    d.ellipse((6,31,42,54),fill='#25201c')
    for x,y in [(12,18),(22,10),(32,16)]: wheat(d,x,y)
    d.polygon([(7,34),(41,34),(36,54),(14,54)],fill='#8a6338',outline='#352820')
    d.arc((6,21,42,46),180,360,fill='#684d30',width=3)
    for yy in range(36,53,3):
        width=(yy-34)//4
        d.line([(8+width,yy),(40-width,yy)],fill='#c5a069')
    for x in range(12,39,5): d.line([(x,36),(x+2,51)],fill='#5f432a')
    d.ellipse((6,31,42,37),outline='#d0af73',width=2)
    d.ellipse((40,48,58,57),fill='#a7814e',outline='#4b3528')
    for x in (45,50,55): d.line([(x,49),(x-2,53)],fill='#e0bd7d')
    return weather(im)


def slavery():
    im=scene((14,20,28),[(21,25,42,(48,62,68)),(57,11,30,(69,34,15))])
    d=ImageDraw.Draw(im)
    # Heavy forged manacles on a damp stone slab, not an abstract chain logo.
    for y in range(9,64,13):
        d.line([(0,y),(63,y-3)],fill='#333e46')
        for x in range((y%3)*10,64,26): d.line([(x,y),(x+2,y+10)],fill='#101923')
    for box in [(9,16,34,42),(34,32,58,57)]:
        x,y,r,b=box
        d.ellipse((x+2,y+4,r+3,b+5),fill='#0b111b')
        d.ellipse(box,fill='#828a85',outline='#17202a',width=2)
        d.ellipse((x+6,y+5,r-5,b-5),fill='#1a2530',outline='#bdbaa3',width=1)
        d.arc((x+2,y+1,r-1,b-1),180,300,fill='#d4ceb4',width=2)
        d.arc((x+2,y+2,r-1,b-1),10,95,fill='#414c59',width=3)
        d.rectangle((r-7,y+7,r+1,y+17),fill='#4c5964',outline='#131d27')
        d.line([(r-6,y+8),(r,y+8)],fill='#aab2a6')
        d.rectangle((r-3,y+10,r-2,y+14),fill='#0e1722')
    for box in [(24,36,35,43),(28,40,38,49),(32,44,43,51)]:
        d.ellipse(box,outline='#171e27',width=4)
        d.ellipse(box,outline='#8b9697',width=2)
        d.arc(box,185,285,fill='#d2cbb5')
    for p in [(12,28),(18,39),(51,52),(46,35)]:
        d.point(p,fill='#a26a43')
    d.line([(1,58),(19,53),(30,58)],fill='#43545e')
    return weather(im)


def serfdom():
    im=scene((18,22,24),[(20,28,50,(77,64,37))])
    d=ImageDraw.Draw(im)
    # Foreground harvest tools; fields and a distant manor establish the context.
    d.polygon([(0,31),(25,25),(46,28),(63,22),(63,63),(0,63)],fill='#554f34')
    d.rectangle((39,15,57,28),fill='#464846')
    d.polygon([(36,16),(46,7),(60,16)],fill='#282c33')
    d.rectangle((45,19,49,27),fill='#171d22')
    for y in (33,40,48,57):
        d.line([(0,y),(42,y-10)],fill='#8b7847',width=2)
        d.line([(2,y+3),(43,y-7)],fill='#30352a')
    # Worn iron sickle with a dark wooden handle, leaning across a wheat sheaf.
    for x,y in [(14,23),(23,18),(29,27)]: wheat(d,x,y)
    d.line([(9,48),(33,43)],fill='#b7955c',width=3)
    d.line([(10,50),(34,45)],fill='#58432c')
    d.line([(29,57),(42,39)],fill='#302621',width=7)
    d.line([(28,56),(41,38)],fill='#8e5f36',width=4)
    d.line([(28,55),(40,39)],fill='#c39255')
    d.arc((28,17,57,44),195,470,fill='#242932',width=8)
    d.arc((28,17,57,44),195,470,fill='#8b9391',width=5)
    d.arc((28,17,57,44),205,380,fill='#d0c9ad',width=1)
    d.polygon([(29,26),(30,20),(34,18),(33,25)],fill='#bcc0ac')
    return weather(im)


def planned_economy():
    im=scene((16,20,28),[(36,20,44,(63,39,34))])
    d=ImageDraw.Draw(im)
    # Industrial skyline behind a large, visibly folded crimson standard.
    for x,h in [(1,43),(13,36),(49,41),(59,30)]:
        d.rectangle((x,h,x+5,63),fill='#30343b')
        d.rectangle((x-1,h,x+6,h+2),fill='#4c4b48')
    d.polygon([(16,52),(25,44),(34,52),(45,44),(57,52),(57,63),(16,63)],fill='#252b33')
    for x in (20,31,43,52): d.rectangle((x,55,x+2,58),fill='#94704a')
    d.line([(9,7),(9,61)],fill='#a39278',width=2)
    d.polygon([(11,10),(27,5),(43,11),(61,7),(58,38),(45,43),(28,37),(11,43)],fill='#9b313d',outline='#2d1c27')
    # Cloth folds are continuous curves rather than a flat red rectangle.
    for x in range(12,60):
        for y in range(12,36):
            if im.getpixel((x,y))[:3] == (155,49,61):
                fold=sin((x-12)*.23)*19+sin(y*.17+x*.08)*5
                im.putpixel((x,y),(int(143+fold),int(43+fold*.35),int(54+fold*.32),255))
    d.line([(12,11),(27,7),(43,13),(59,9)],fill='#cf7762')
    d.line([(13,41),(28,35),(45,41),(57,37)],fill='#642332',width=2)
    # Gold sickle, blade taper, and hammer with its own readable head.
    d.arc((26,14,47,34),270,545,fill='#5e3a29',width=6)
    d.arc((26,13,47,33),270,545,fill='#dab76b',width=4)
    d.arc((26,13,47,33),275,355,fill='#f4d794')
    d.line([(29,31),(44,16)],fill='#7d542d',width=5)
    d.line([(29,30),(43,16)],fill='#dbb768',width=3)
    d.polygon([(30,15),(35,11),(44,19),(40,23)],fill='#e1bd72',outline='#75472e')
    d.line([(31,15),(35,12),(42,18)],fill='#f2d699')
    return weather(im)


def corporate_economy():
    im=scene((16,22,26),[(32,31,47,(65,53,34))])
    d=ImageDraw.Draw(im)
    # An abundant market stall: striped cloth, carved counter, goods and coins.
    d.polygon([(0,20),(11,8),(23,19),(38,12),(55,20),(64,12),(64,63),(0,63)],fill='#293238')
    for x in (10,53): wood(d,(x,22,x+3,59))
    d.polygon([(7,17),(46,12),(60,28),(4,32)],fill='#63303b',outline='#171f28')
    for x in (11,24,37):
        d.polygon([(x,17-(x//12)),(x+6,16-(x//12)),(x+12,29-(x//18)),(x+3,30-(x//18))],fill='#b7a17c')
    d.line([(6,32),(58,28)],fill='#d0b38b')
    for x in range(6,58,8): d.arc((x,27,x+8,35),0,180,fill='#7a3941',width=3)
    wood(d,(8,43,55,59))
    d.line([(8,43),(55,43)],fill='#c6a66d',width=2)
    d.rectangle((12,48,51,55),outline='#342c25')
    d.ellipse((12,35,28,44),fill='#997040',outline='#352a24')
    for x in (17,22): d.line([(x,37),(x-2,40)],fill='#d1b17b')
    d.ellipse((34,35,46,44),fill='#4a6650',outline='#273632')
    d.ellipse((44,33,53,43),fill='#793936',outline='#32292a')
    d.line([(39,36),(39,33)],fill='#829069')
    for x,y in [(25,46),(30,46),(28,49)]:
        d.ellipse((x,y,x+5,y+2),fill='#d6b15e',outline='#85603a')
    d.polygon([(14,60),(14,53),(21,50),(26,54),(26,61)],fill='#725c3d',outline='#302b26')
    d.line([(17,53),(23,53)],fill='#b59e72')
    return weather(im)


ICONS=[('Self_Sufficiency','Self Sufficiency',self_sufficiency),('Slavery','Slavery',slavery),
       ('Serfdom','Serfdom',serfdom),('Planned_Economy','Planned Economy',planned_economy),
       ('Corporate_Economy','Market Economy',corporate_economy)]


def main():
    with Image.open(ROOT/'RFC MP Plus/Assets/Art/Interface/Buttons/civics_civilizations_religions_atlas.dds') as atlas:
        alpha=atlas.convert('RGBA').crop((0,0,64,64)).getchannel('A')
    preview=Image.new('RGB',(960,225),(23,26,32))
    d=ImageDraw.Draw(preview)
    for row,(name,label,draw) in enumerate(ICONS):
        icon=draw(); icon.putalpha(alpha)
        icon.save(ART/(name.lower().replace('_','-')+'-pixel.png'))
        icon.save(DEST/(name+'.dds'),pixel_format='DXT3')
        with Image.open(DEST/(name+'.dds')) as compressed: rgba=compressed.convert('RGBA')
        tile=rgba.resize((180,180),Image.Resampling.NEAREST)
        preview.paste(tile,(row*192+6,7),tile)
        d.text((row*192+96,198),label,fill=(230,225,208),anchor='mt')
        for filename,size,x,y in [('preview.png',96,272,row*140+10),
                                  ('symbolic-civics-preview.png',180,390,row*216+30)]:
            path=ART/filename
            if path.exists():
                with Image.open(path) as old: sheet=old.convert('RGB')
                ImageDraw.Draw(sheet).rectangle((x,y,x+size-1,y+size-1),fill=(23,26,32))
                tile=rgba.resize((size,size),Image.Resampling.NEAREST)
                sheet.paste(tile,(x,y),tile); sheet.save(path)
    preview.save(ART/'labor-pixel-preview.png')
    print('Created five atmospheric 64px DXT3 Labor icons.')


if __name__=='__main__': main()
