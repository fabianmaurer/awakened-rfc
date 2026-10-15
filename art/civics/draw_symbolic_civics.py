"""Draw the remaining 20 Civ4 civic buttons directly on a 64px pixel canvas.

Run after draw_government.py, using the Pillow environment .venv-art.
All shapes and shading are deterministic; no generated image service is used.
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


def background(base, glow):
    im = Image.new('RGBA', (64, 64))
    for y in range(64):
        for x in range(64):
            light = max(0, 1 - math.sqrt(((x-29)/39.0)**2 + ((y-26)/44.0)**2))
            grain = (x*17 + y*31 + x*y*7) % 7 - 3
            im.putpixel((x,y), tuple(max(0,int(b+g*light)+grain) for b,g in zip(base,glow))+(255,))
    return im

ROOT = Path(__file__).resolve().parents[2]
ART = Path(__file__).resolve().parent
DEST = ROOT / "Awakened RFC/Assets/Art/Interface/Buttons/Civics/RFCMP"
GOLD = (206, 158, 65)
LIGHT = (251, 223, 140)
IRON = (147, 160, 161)
DARK = (30, 35, 40)
IVORY = (227, 217, 174)


def canvas(kind="gold"):
    palettes = {
        "gold": ((21, 14, 17), (34, 23, 15)),
        "green": ((12, 22, 15), (31, 35, 22)),
        "steel": ((13, 19, 26), (35, 35, 40)),
        "red": ((26, 10, 15), (48, 19, 21)),
        "blue": ((10, 23, 28), (25, 36, 39)),
        "purple": ((22, 13, 29), (34, 28, 44)),
    }
    return background(*palettes[kind])


def metal(d, box, color=IRON, highlight=(226, 229, 208)):
    x, y, r, b = box
    d.rounded_rectangle(box, radius=2, fill=color, outline=DARK)
    d.line([(x + 1, b - 2), (x + 1, y + 1), (r - 2, y + 1)], fill=highlight)
    d.line([(r - 1, y + 2), (r - 1, b - 1), (x + 2, b - 1)], fill=(77, 78, 68))


def paper(d, box):
    x, y, r, b = box
    d.rectangle((x + 2, y + 2, r + 2, b + 2), fill=(14, 20, 23))
    d.rectangle(box, fill=IVORY, outline=(99, 86, 59))
    d.line([(x + 1, b - 1), (x + 1, y + 1), (r - 1, y + 1)], fill=(251, 242, 208))


def sword(d, x, y):
    d.polygon([(x, y), (x - 3, y + 7), (x - 3, y + 28), (x + 3, y + 28), (x + 3, y + 7)], fill=IRON, outline=DARK)
    d.line([(x, y + 3), (x, y + 27)], fill=(240, 236, 204))
    metal(d, (x - 8, y + 27, x + 8, y + 31), GOLD, LIGHT)
    d.rectangle((x - 2, y + 31, x + 2, y + 42), fill=(99, 53, 29), outline=(37, 25, 23))
    for yy in range(y + 33, y + 41, 3):
        d.line([(x - 1, yy), (x + 1, yy)], fill=(182, 117, 52))
    d.ellipse((x - 3, y + 40, x + 3, y + 45), fill=GOLD, outline=(92, 65, 31))


def wheat(d, x, y, height=26):
    d.line([(x, y + height), (x, y)], fill=(180, 146, 63))
    for yy in range(y + 4, y + height - 3, 5):
        d.polygon([(x, yy + 3), (x - 6, yy - 3), (x - 6, yy), (x - 2, yy + 4)], fill=(222, 185, 78))
        d.polygon([(x, yy + 3), (x + 6, yy - 3), (x + 6, yy), (x + 2, yy + 4)], fill=(181, 138, 47))
    d.line([(x, y), (x, y + 5)], fill=LIGHT)


def helmet(d, x, y, size=20):
    w = size
    d.pieslice((x, y, x + w, y + w), 180, 360, fill=IRON, outline=DARK)
    d.arc((x + 2, y + 2, x + w - 2, y + w - 2), 195, 270, fill=(236, 233, 201), width=2)
    metal(d, (x - 2, y + w // 2 - 1, x + w + 2, y + w // 2 + 3))


def despotism():
    im = canvas("purple"); d = ImageDraw.Draw(im)
    # A single oversized scepter, with a jeweled orb and pointed finial.
    d.ellipse((15, 51, 50, 57), fill=(13, 10, 18))
    metal(d, (29, 25, 35, 53), GOLD, LIGHT)
    for y in (31, 37, 43, 49):
        d.line([(30, y), (34, y)], fill=(110, 69, 31))
    d.ellipse((21, 12, 43, 32), fill=(148, 97, 37), outline=(47, 27, 20))
    d.ellipse((23, 13, 40, 28), fill=GOLD)
    d.arc((24, 14, 40, 28), 180, 280, fill=LIGHT, width=2)
    d.line([(23, 22), (41, 22)], fill=(122, 73, 28), width=2)
    d.line([(31, 13), (31, 30)], fill=(126, 73, 27))
    d.polygon([(27, 11), (32, 4), (37, 11), (32, 16)], fill=GOLD, outline=(102, 61, 29))
    d.polygon([(28, 11), (32, 6), (32, 14)], fill=LIGHT)
    d.ellipse((29, 19, 35, 25), fill=(114, 24, 43), outline=LIGHT)
    metal(d, (26, 52, 38, 57), GOLD, LIGHT)
    return im


def theocratic_legitimacy():
    im = canvas("purple"); d = ImageDraw.Draw(im)
    # Ceremonial mitre resting on a closed sacred book.
    d.polygon([(12, 46), (44, 43), (53, 48), (21, 53)], fill=(162, 51, 49), outline=(45, 18, 26))
    d.polygon([(21, 53), (53, 48), (53, 53), (21, 58)], fill=IVORY)
    d.line([(20, 58), (53, 53)], fill=GOLD, width=2)
    d.polygon([(18, 44), (19, 22), (30, 6), (41, 17), (45, 40), (36, 46)], fill=(130, 102, 63), outline=(38, 25, 24))
    d.polygon([(20, 41), (21, 23), (30, 8), (33, 21), (35, 43)], fill=IVORY)
    d.polygon([(33, 21), (30, 8), (39, 19), (42, 39), (36, 43)], fill=(191, 164, 107))
    d.line([(30, 12), (30, 39)], fill=GOLD, width=3)
    d.line([(23, 28), (38, 28)], fill=GOLD, width=3)
    d.rectangle((20, 39, 42, 43), fill=GOLD)
    d.line([(21, 39), (41, 39)], fill=LIGHT)
    d.ellipse((28, 25, 32, 29), fill=(96, 31, 52), outline=LIGHT)
    return im


def plutocracy():
    im = canvas(); d = ImageDraw.Draw(im)
    # Three gold coin towers, increasing in height.
    d.ellipse((7, 49, 57, 58), fill=(15, 11, 11))
    for x, top in [(9, 37), (25, 23), (41, 10)]:
        for y in range(50, top - 1, -4):
            d.rectangle((x, y, x + 13, y + 4), fill=(166, 105, 31), outline=(73, 44, 20))
            d.line([(x + 1, y + 2), (x + 12, y + 2)], fill=(233, 181, 72))
        d.ellipse((x, top - 3, x + 13, top + 3), fill=GOLD, outline=LIGHT)
        d.ellipse((x + 4, top - 1, x + 9, top + 1), outline=(131, 82, 28))
    return im


def nationalism():
    im = canvas("blue"); d = ImageDraw.Draw(im)
    # Abstract national standard, with no real-world flag or ideology.
    d.line([(17, 8), (17, 56)], fill=(67, 44, 25), width=4)
    d.line([(16, 8), (16, 55)], fill=LIGHT)
    d.ellipse((14, 5, 20, 11), fill=GOLD, outline=(91, 63, 29))
    d.polygon([(19, 12), (33, 8), (44, 12), (56, 10), (52, 23), (54, 34), (42, 36), (31, 32), (19, 36)], fill=(167, 43, 44), outline=(69, 26, 29))
    d.polygon([(20, 13), (33, 10), (43, 14), (53, 12), (51, 17), (42, 19), (32, 15), (20, 18)], fill=(218, 81, 54))
    d.line([(20, 26), (32, 22), (43, 26), (52, 24)], fill=GOLD, width=3)
    d.line([(33, 10), (31, 32)], fill=(122, 34, 39))
    d.rectangle((11, 56, 24, 58), fill=(99, 79, 49))
    return im


def rule_of_law():
    im = canvas("blue"); d = ImageDraw.Draw(im)
    paper(d, (13, 37, 51, 56))
    for y in (43, 47, 51):
        d.line([(20, y), (44, y)], fill=(149, 135, 96))
    metal(d, (29, 15, 33, 48), GOLD, LIGHT)
    d.ellipse((27, 9, 35, 17), fill=GOLD, outline=LIGHT)
    d.line([(10, 20), (52, 20)], fill=GOLD, width=3)
    d.line([(11, 19), (51, 19)], fill=LIGHT)
    for x in (14, 48):
        d.line([(x, 20), (x - 7, 33)], fill=GOLD)
        d.line([(x, 20), (x + 7, 33)], fill=GOLD)
        d.pieslice((x - 8, 27, x + 8, 39), 0, 180, fill=GOLD, outline=(97, 67, 30))
        d.line([(x - 8, 33), (x + 8, 33)], fill=LIGHT)
    metal(d, (23, 49, 39, 52), GOLD, LIGHT)
    return im


def self_sufficiency():
    im = canvas("green"); d = ImageDraw.Draw(im)
    wheat(d, 20, 8, 31); wheat(d, 31, 5, 32); wheat(d, 43, 11, 27)
    d.polygon([(11, 32), (53, 32), (47, 54), (17, 54)], fill=(128, 84, 37), outline=(45, 36, 23))
    for y in (36, 41, 46, 51):
        d.line([(15, y), (49, y)], fill=(194, 143, 67), width=2)
    for x in range(19, 48, 6):
        d.line([(x, 34), (x - 2, 52)], fill=(71, 49, 28))
    metal(d, (11, 31, 53, 35), (179, 127, 58), (232, 189, 110))
    d.ellipse((25, 27, 47, 39), fill=(212, 165, 85), outline=(119, 75, 30))
    for x in (30, 36, 42):
        d.line([(x, 29), (x - 2, 34)], fill=(143, 100, 47))
    return im


def slavery():
    im = canvas("steel"); d = ImageDraw.Draw(im)
    # Empty iron shackles: no people needed to express bondage.
    for box in [(8, 14, 28, 39), (36, 24, 57, 49)]:
        d.ellipse(box, outline=DARK, width=7)
        d.ellipse((box[0]+1, box[1]+1, box[2]-1, box[3]-1), outline=IRON, width=4)
        d.arc((box[0]+2, box[1]+2, box[2]-2, box[3]-2), 170, 280, fill=(225, 225, 198), width=2)
    for box in [(22, 33, 32, 41), (27, 37, 38, 45), (33, 40, 43, 48)]:
        d.ellipse(box, outline=(35, 40, 46), width=4)
        d.ellipse(box, outline=(152, 164, 164), width=2)
    metal(d, (10, 34, 19, 41)); metal(d, (46, 45, 55, 52))
    d.point((14, 37), fill=(25, 30, 36)); d.point((50, 48), fill=(25, 30, 36))
    return im


def serfdom():
    im = canvas("green"); d = ImageDraw.Draw(im)
    # Grain and a harvesting sickle beneath a distant manor roof.
    d.polygon([(8, 22), (8, 15), (17, 8), (27, 15), (27, 22)], fill=(84, 85, 62))
    d.line([(7, 15), (17, 7), (28, 15)], fill=(142, 126, 80), width=2)
    d.rectangle((15, 15, 19, 22), fill=(37, 43, 33))
    wheat(d, 21, 24, 31); wheat(d, 32, 17, 35)
    d.arc((25, 8, 57, 43), 250, 90, fill=(35, 39, 36), width=7)
    d.arc((25, 8, 57, 43), 255, 90, fill=IRON, width=4)
    d.arc((27, 10, 55, 41), 260, 35, fill=(228, 225, 188), width=1)
    d.line([(41, 41), (34, 57)], fill=(58, 39, 23), width=7)
    d.line([(40, 42), (33, 55)], fill=(186, 122, 52), width=4)
    return im


def planned_economy():
    im = canvas("red"); d = ImageDraw.Draw(im)
    # Hammer and sickle, with deliberately broad silhouettes at native size.
    d.arc((12, 8, 54, 50), 270, 110, fill=(82, 40, 19), width=9)
    d.arc((12, 8, 54, 50), 275, 110, fill=GOLD, width=6)
    d.arc((14, 10, 52, 48), 285, 65, fill=LIGHT, width=2)
    d.polygon([(23, 42), (29, 46), (16, 58), (10, 53)], fill=GOLD, outline=(109, 70, 29))
    d.line([(13, 53), (25, 43)], fill=LIGHT)
    d.polygon([(19, 22), (24, 18), (50, 49), (44, 54)], fill=GOLD, outline=(110, 65, 24))
    d.line([(23, 22), (47, 49)], fill=LIGHT, width=2)
    d.polygon([(10, 21), (25, 8), (33, 17), (17, 30)], fill=GOLD, outline=(95, 53, 26))
    d.line([(11, 21), (25, 9), (31, 16)], fill=LIGHT, width=2)
    return im


def corporate_economy():
    im = canvas("blue"); d = ImageDraw.Draw(im)
    # A market stall: goods and exchange rather than a wealthy portrait.
    d.rectangle((12, 22, 51, 48), fill=(53, 42, 30), outline=(20, 27, 26))
    for x in (13, 49):
        metal(d, (x, 18, x + 3, 54), (169, 118, 58), (219, 167, 93))
    d.polygon([(13, 11), (49, 11), (56, 24), (7, 24)], fill=(198, 180, 132), outline=(46, 42, 32))
    for x in (12, 26, 40):
        d.polygon([(x + 3, 12), (x + 9, 12), (x + 11, 24), (x, 24)], fill=(145, 40, 40))
    d.rectangle((8, 24, 55, 27), fill=(217, 195, 137))
    for x in (10, 24, 38):
        d.rectangle((x, 24, x + 6, 27), fill=(166, 47, 43))
    for x in (19, 25, 31):
        d.ellipse((x, 35, x + 6, 41), fill=(165, 105, 39), outline=(211, 161, 62))
    d.rectangle((38, 32, 45, 41), fill=(75, 124, 89), outline=(33, 65, 53))
    metal(d, (11, 43, 53, 48), (153, 104, 50), (227, 177, 99))
    d.rectangle((17, 49, 47, 54), fill=(85, 63, 35))
    return im


def warrior_society():
    im = canvas("green"); d = ImageDraw.Draw(im)
    d.line([(10, 9), (51, 56)], fill=(145, 108, 59), width=3)
    d.polygon([(7, 5), (17, 11), (10, 18)], fill=IRON, outline=DARK)
    d.ellipse((15, 16, 49, 52), fill=(113, 66, 32), outline=(45, 32, 23))
    for x in (21, 27, 33, 39, 45):
        d.line([(x, 21), (x, 47)], fill=(166, 113, 54))
    d.ellipse((15, 16, 49, 52), outline=(173, 155, 105), width=3)
    d.ellipse((26, 28, 38, 40), fill=IRON, outline=DARK)
    d.arc((28, 29, 37, 38), 170, 290, fill=(231, 225, 185), width=2)
    return im


def militia():
    im = canvas("steel"); d = ImageDraw.Draw(im)
    # Crenellated town wall and a bow for local defense.
    d.rectangle((8, 29, 51, 53), fill=(128, 129, 112), outline=DARK)
    for x in range(8, 51, 10):
        d.rectangle((x, 22, x + 5, 31), fill=(164, 162, 135), outline=(65, 70, 69))
    for y in (34, 42, 50):
        d.line([(9, y), (50, y)], fill=(72, 80, 80))
        for x in range(12 + (y % 3) * 3, 51, 11):
            d.line([(x, y - 7), (x, y)], fill=(78, 83, 80))
    d.rounded_rectangle((22, 35, 35, 54), radius=6, fill=(29, 35, 38))
    d.arc((34, 6, 59, 54), 265, 95, fill=(209, 166, 91), width=3)
    d.line([(46, 7), (46, 53)], fill=(224, 216, 166))
    d.line([(33, 30), (58, 30)], fill=(169, 130, 68))
    d.polygon([(58, 27), (62, 30), (58, 33)], fill=IRON)
    return im


def knighthood():
    im = canvas("blue"); d = ImageDraw.Draw(im)
    # Horseshoe and lance distinguish the mounted military order.
    d.line([(46, 10), (46, 56)], fill=(176, 135, 68), width=3)
    d.polygon([(46, 4), (42, 14), (49, 14)], fill=IRON, outline=DARK)
    d.polygon([(47, 16), (60, 19), (47, 27)], fill=(161, 43, 48))
    d.arc((9, 12, 48, 54), 140, 400, fill=(41, 44, 48), width=10)
    d.arc((10, 13, 47, 53), 140, 400, fill=IRON, width=7)
    d.arc((12, 15, 45, 51), 150, 300, fill=(237, 230, 188), width=2)
    for x, y in [(15, 36), (14, 26), (20, 19), (30, 17), (39, 23), (41, 33)]:
        d.rectangle((x, y, x + 1, y + 2), fill=(48, 59, 66))
    return im


def professional_army():
    im = canvas("steel"); d = ImageDraw.Draw(im)
    sword(d, 15, 6); sword(d, 49, 6)
    # Regiment helmet with a strong visor and neck guard.
    d.polygon([(22, 28), (22, 16), (29, 9), (39, 12), (44, 24), (41, 44), (28, 48), (20, 40)], fill=(89, 106, 119), outline=DARK)
    d.polygon([(23, 25), (24, 17), (30, 11), (35, 14), (35, 27)], fill=(176, 185, 176))
    d.line([(24, 18), (30, 12), (35, 14)], fill=(243, 235, 194))
    metal(d, (21, 27, 43, 36))
    d.line([(24, 31), (39, 31)], fill=(29, 38, 47), width=2)
    d.polygon([(25, 37), (39, 37), (38, 43), (29, 46)], fill=(148, 159, 160))
    d.line([(32, 38), (32, 44)], fill=(64, 82, 100))
    d.line([(26, 49), (39, 49)], fill=GOLD, width=3)
    return im


def conscription():
    im = canvas("steel"); d = ImageDraw.Draw(im)
    paper(d, (14, 7, 48, 49))
    for y in (15, 22, 29):
        d.rectangle((20, y, 23, y + 3), outline=(120, 106, 77))
        d.line([(27, y + 1), (41, y + 1)], fill=(151, 135, 96))
    d.ellipse((32, 35, 42, 45), fill=(154, 43, 45), outline=(109, 34, 37))
    # Repeated helmets signify mass recruitment, distinct from a single professional.
    helmet(d, 7, 41, 15); helmet(d, 25, 44, 15); helmet(d, 43, 41, 15)
    return im


def ancestor_cult():
    im = canvas("purple"); d = ImageDraw.Draw(im)
    d.polygon([(22, 45), (22, 13), (27, 7), (39, 7), (44, 13), (44, 45)], fill=(141, 138, 122), outline=(48, 46, 48))
    d.line([(23, 43), (23, 14), (28, 8), (39, 8)], fill=(210, 197, 158))
    d.rectangle((28, 15, 38, 38), fill=(100, 100, 93))
    d.ellipse((30, 18, 36, 24), outline=(199, 185, 146))
    d.line([(33, 24), (33, 34)], fill=(199, 185, 146))
    d.line([(29, 28), (37, 28)], fill=(199, 185, 146))
    metal(d, (18, 45, 48, 50), (112, 107, 94), (180, 163, 132))
    for x in (11, 51):
        d.rectangle((x, 40, x + 3, 53), fill=IVORY)
        d.polygon([(x - 1, 39), (x + 1, 32), (x + 4, 39)], fill=(247, 176, 66))
        d.point((x + 1, 36), fill=(255, 239, 158))
    d.arc((27, 45, 39, 57), 0, 180, fill=(157, 114, 54), width=3)
    return im


def state_religion():
    im = canvas("blue"); d = ImageDraw.Draw(im)
    # A sacred book with a radiant sun, without privileging one game's religion.
    for angle in range(0, 360, 30):
        a = math.radians(angle)
        d.line([(32 + int(9 * math.cos(a)), 18 + int(9 * math.sin(a))),
                (32 + int(15 * math.cos(a)), 18 + int(15 * math.sin(a)))], fill=GOLD, width=2)
    d.ellipse((26, 12, 38, 24), fill=GOLD, outline=LIGHT)
    d.polygon([(9, 34), (26, 30), (32, 34), (38, 30), (55, 34), (55, 54), (38, 51), (32, 55), (26, 51), (9, 54)], fill=(127, 67, 34), outline=(35, 29, 25))
    d.polygon([(11, 34), (26, 32), (31, 35), (31, 51), (26, 48), (11, 51)], fill=IVORY)
    d.polygon([(33, 35), (38, 32), (53, 34), (53, 51), (38, 48), (33, 51)], fill=(204, 193, 146))
    for y in (39, 43, 47):
        d.line([(15, y), (26, y - 1)], fill=(148, 132, 90))
        d.line([(38, y - 1), (49, y)], fill=(134, 119, 84))
    d.line([(32, 35), (32, 53)], fill=(82, 53, 29))
    return im


def god_state():
    im = canvas("purple"); d = ImageDraw.Draw(im)
    # Monumental sanctuary under a crown: religious and political authority.
    d.rectangle((15, 28, 49, 51), fill=(148, 134, 108), outline=(51, 45, 46))
    d.polygon([(10, 30), (32, 17), (54, 30)], fill=(209, 188, 139), outline=(68, 56, 47))
    d.line([(11, 30), (53, 30)], fill=LIGHT)
    for x in (18, 41):
        d.rectangle((x, 31, x + 5, 49), fill=(217, 198, 151))
        d.line([(x + 4, 32), (x + 4, 49)], fill=(97, 88, 78))
    d.rounded_rectangle((27, 34, 37, 51), radius=5, fill=(43, 33, 43))
    metal(d, (11, 51, 53, 55), (150, 128, 90), IVORY)
    d.polygon([(22, 17), (19, 6), (26, 11), (32, 4), (38, 11), (45, 6), (42, 17)], fill=GOLD, outline=(109, 67, 29))
    d.line([(23, 16), (41, 16)], fill=LIGHT, width=2)
    d.rectangle((30, 12, 33, 14), fill=(133, 38, 44))
    return im


def tolerance():
    im = canvas("green"); d = ImageDraw.Draw(im)
    # Three equal rings, different colors, interlinked without a dominant emblem.
    boxes = [(9, 12, 35, 38), (29, 12, 55, 38), (19, 29, 45, 55)]
    colors = [(222, 176, 76), (131, 175, 195), (153, 188, 120)]
    for box, color in zip(boxes, colors):
        d.ellipse(box, outline=(22, 33, 30), width=7)
        d.ellipse((box[0]+1, box[1]+1, box[2]-1, box[3]-1), outline=color, width=4)
        d.arc((box[0]+2, box[1]+2, box[2]-2, box[3]-2), 190, 285, fill=IVORY, width=1)
    d.arc((10, 13, 34, 37), 5, 70, fill=colors[0], width=4)
    return im


def state_atheism():
    im = canvas("blue"); d = ImageDraw.Draw(im)
    # Atom above a secular reference book, for scientific institutions.
    d.polygon([(13, 44), (46, 41), (54, 46), (21, 50)], fill=(80, 116, 132), outline=(27, 43, 49))
    d.polygon([(21, 50), (54, 46), (54, 52), (21, 57)], fill=IVORY)
    d.line([(20, 57), (54, 52)], fill=(79, 137, 163), width=2)
    center = (32, 25)
    for rotation in (0, math.pi / 3, -math.pi / 3):
        pts = []
        for index in range(73):
            a = index * math.tau / 72
            x, y = 23 * math.cos(a), 8 * math.sin(a)
            pts.append((round(center[0] + x * math.cos(rotation) - y * math.sin(rotation)),
                        round(center[1] + x * math.sin(rotation) + y * math.cos(rotation))))
        d.line(pts, fill=(145, 200, 210), width=2)
    d.ellipse((28, 21, 36, 29), fill=GOLD, outline=LIGHT)
    for box in [(9, 22, 13, 26), (42, 7, 46, 11), (39, 40, 43, 44)]:
        d.ellipse(box, fill=(242, 223, 160))
    return im


DRAWINGS = {
    "Despotism": despotism, "Theocratic_Legitimacy": theocratic_legitimacy,
    "Plutocracy": plutocracy, "Nationalism": nationalism, "Rule_Of_Law": rule_of_law,
    "Self_Sufficiency": self_sufficiency, "Slavery": slavery, "Serfdom": serfdom,
    "Planned_Economy": planned_economy, "Corporate_Economy": corporate_economy,
    "Warrior_Society": warrior_society, "Militia": militia, "Knighthood": knighthood,
    "Professional_Army": professional_army, "Conscription": conscription,
    "Ancestor_Cult": ancestor_cult, "State_Religion": state_religion,
    "God_State": god_state, "Tolerance": tolerance, "State_Atheism": state_atheism,
}


def main():
    from draw_legitimacy import main as draw_legitimacy
    from draw_labor import main as draw_labor
    from draw_military import main as draw_military
    from draw_religion import main as draw_religion
    draw_legitimacy()
    draw_labor()
    draw_military()
    draw_religion()
    with Image.open(ROOT / "Awakened RFC/Assets/Art/Interface/Buttons/civics_civilizations_religions_atlas.dds") as atlas:
        alpha = atlas.convert("RGBA").crop((0, 0, 64, 64)).getchannel("A")
    for name, drawing in DRAWINGS.items():
        if name in ('Despotism', 'Theocratic_Legitimacy', 'Plutocracy', 'Nationalism', 'Rule_Of_Law'):
            continue
        if name in ('Self_Sufficiency', 'Slavery', 'Serfdom', 'Planned_Economy', 'Corporate_Economy'):
            continue
        if name in ('Warrior_Society', 'Militia', 'Knighthood', 'Professional_Army', 'Conscription'):
            continue
        if name in ('Ancestor_Cult', 'State_Religion', 'God_State', 'Tolerance', 'State_Atheism'):
            continue
        icon = drawing()
        icon.putalpha(alpha)
        icon.save(ART / (name.lower().replace("_", "-") + "-pixel.png"))
        icon.save(DEST / (name + ".dds"), pixel_format="DXT3")
    # Show all 25 compressed game assets, in the same five-column arrangement.
    metadata = json.loads((ART / "generation.json").read_text(encoding="utf-8"))
    sheet = Image.new("RGB", (960, 1120), (23, 26, 32))
    d = ImageDraw.Draw(sheet)
    for col, heading in enumerate(("Government", "Legitimacy", "Labor", "Military", "Religion")):
        d.text((col * 192 + 96, 8), heading, fill=(243, 225, 185), anchor="mt")
    labels = {"Corporate_Economy": "Market Economy", "God_State": "Holy State", "Theocratic_Legitimacy": "Theocracy"}
    # Also keep the existing compact contact sheet up to date.
    compact = Image.new("RGB", (640, 700), (22, 27, 38))
    cd = ImageDraw.Draw(compact)
    for index, entry in enumerate(metadata["icons"]):
        name = Path(entry["filename"]).stem
        col, row = index // 5, index % 5
        with Image.open(DEST / entry["filename"]) as game:
            rgba = game.convert("RGBA")
            large = rgba.resize((180, 180), Image.Resampling.NEAREST)
            small = rgba.resize((96, 96), Image.Resampling.NEAREST)
        sheet.paste(large, (col * 192 + 6, row * 216 + 30), large)
        label = labels.get(name, name.replace("_", " "))
        d.text((col * 192 + 96, row * 216 + 220), label, fill=(230, 225, 208), anchor="mt")
        compact.paste(small, (col * 128 + 16, row * 140 + 10), small)
        if len(label) > 19:
            words = label.split(); label = " ".join(words[:-1]) + "\n" + words[-1]
        cd.multiline_text((col * 128 + 64, row * 140 + 112), label, fill="white", anchor="ma", align="center")
    sheet.save(ART / "symbolic-civics-preview.png")
    compact.save(ART / "preview.png")
    print("Refreshed Legitimacy, Labor, Military, Religion and both full previews.")


if __name__ == "__main__":
    main()
