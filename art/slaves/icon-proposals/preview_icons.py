"""Preview only: existing DoC slave button plus a hand-drawn weapon overlay.

Writes PNG proposals beside this script. Does not edit or install mod assets.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent
SOURCE = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/RFC Dawn of Civilization/Assets/Art/Units/slave/button_slave.dds")
S = 4

def draw_axe():
    # Draw at four times the native size to antialias the diagonal axe edges.
    layer = Image.new('RGBA', (64*S, 64*S))
    d = ImageDraw.Draw(layer)
    def line(points, color, width=1):
        d.line([(round(x*S),round(y*S)) for x,y in points],fill=color,width=round(width*S))
    def polygon(points,color):
        d.polygon([(round(x*S),round(y*S)) for x,y in points],fill=color)
    # Dark silhouette separates the weapon from the original chains/portrait.
    line([(11,61),(28,28)],(17,12,9,255),6)
    line([(11,61),(28,28)],(94,57,28,255),3.5)
    line([(10.4,60),(27.4,28)],(185,132,64,255),0.8)
    line([(12,60),(28.5,28)],(61,34,21,255),0.8)
    for i in range(5):
        y=49+i*2.1; x=28-(y-28)*17/33
        line([(x-1.6,y-0.7),(x+1.3,y+0.8)],(63,39,27,255),0.8)
    blade=[(24,30),(29,29),(31,31),(37,32),(38,36),(36,42),(32,46),(28,43),(24,39),(20,37)]
    polygon(blade,(22,15,10,255))
    # Warm, worn bronze with a hammered surface, drawn from a native mask.
    mask=Image.new('L',layer.size)
    md=ImageDraw.Draw(mask)
    inner=[(24.5,31),(28.5,30),(31,32),(36,33),(37,36),(35,41),(32,44.5),(28.5,42),(25,38),(22,36.5)]
    md.polygon([(int(x*S),int(y*S)) for x,y in inner],fill=255)
    pixels=layer.load();mp=mask.load()
    for y in range(28*S,46*S):
        for x in range(20*S,39*S):
            if mp[x,y]:
                texture=8*math.sin(x*0.53+y*0.77)+5*math.cos(x*1.31-y*0.37)
                light=22*(1-(y/S-30)/15)+texture
                pixels[x,y]=(int(145+light),int(99+light*.8),int(43+light*.5),255)
    line([(36.5,33),(37,36),(35,41),(32,44.5)],(238,205,133,255),1.2)
    line([(35.7,34),(35.5,37),(33.5,41)],(193,153,77,255),0.6)
    line([(25,31),(23.5,36),(27,39)],(78,48,22,255),1)
    polygon([(24,30),(27,31),(23,39),(20.5,37)],(95,66,36,255))
    line([(25,31),(21.5,37)],(224,182,98,255),0.7)
    for x,y in ((24,33),(22.6,36)):
        d.ellipse(((x-.7)*S,(y-.7)*S,(x+.7)*S,(y+.7)*S),fill=(238,208,137,255))
    shadow=Image.new('RGBA',layer.size,(0,0,0,0))
    alpha=layer.getchannel('A').filter(ImageFilter.GaussianBlur(1.1*S)).point(lambda v:int(v*.8))
    shadow.putalpha(alpha)
    shadow.alpha_composite(layer)
    # Keep the haft clear of the original button's lower rounded border.
    raised=Image.new('RGBA',layer.size)
    raised.alpha_composite(shadow,(0,-5*S))
    return raised.resize((64,64),Image.Resampling.LANCZOS)

def main():
    base=Image.open(SOURCE).convert('RGBA')
    armed=Image.alpha_composite(base,draw_axe())
    base.save(OUT/'slave.png')
    armed.save(OUT/'armed-slave-bronze.png')
    sheet=Image.new('RGB',(616,390),(27,26,25));d=ImageDraw.Draw(sheet)
    for i,(title,im) in enumerate((('Slave',base),('Armed slave (bronze)',armed))):
        x=22+i*304
        d.text((x,10),title,fill=(231,224,207))
        sheet.paste(im.resize((256,256),Image.Resampling.NEAREST),(x,34),im.resize((256,256),Image.Resampling.NEAREST))
        sheet.paste(im,(x+96,308),im)
    sheet.save(OUT/'comparison.png')
    print('Saved two 64x64 PNG proposals and comparison; mod files unchanged.')


if __name__ == "__main__":
    main()
