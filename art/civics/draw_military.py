"""Export five atmospheric Military scenes from preserved 64px first-set art.

Run: .venv-art/Scripts/python.exe art/civics/draw_military.py
No image generation is used. Only Military game textures are written.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from reuse_government import portrait

ROOT=Path(__file__).resolve().parents[2]
ART=Path(__file__).resolve().parent
DEST=ROOT/'Awakened RFC/Assets/Art/Interface/Buttons/Civics/RFCMP'
ICONS=[('Warrior_Society','Warrior Society'),('Militia','Militia'),
       ('Knighthood','Knighthood'),('Professional_Army','Professional Army'),
       ('Conscription','Conscription')]


def main():
    with Image.open(ROOT/'Awakened RFC/Assets/Art/Interface/Buttons/civics_civilizations_religions_atlas.dds') as atlas:
        alpha=atlas.convert('RGBA').crop((0,0,64,64)).getchannel('A')
    preview=Image.new('RGB',(960,225),(23,26,32))
    d=ImageDraw.Draw(preview)
    for row,(name,label) in enumerate(ICONS):
        icon=portrait(name); icon.putalpha(alpha)
        icon.save(ART/(name.lower().replace('_','-')+'-pixel.png'))
        icon.save(DEST/(name+'.dds'),pixel_format='DXT3')
        with Image.open(DEST/(name+'.dds')) as compressed:
            rgba=compressed.convert('RGBA')
        tile=rgba.resize((180,180),Image.Resampling.NEAREST)
        preview.paste(tile,(row*192+6,7),tile)
        d.text((row*192+96,198),label,fill=(230,225,208),anchor='mt')
        for filename,size,x,y in [('preview.png',96,400,row*140+10),
                                  ('symbolic-civics-preview.png',180,582,row*216+30)]:
            path=ART/filename
            if path.exists():
                with Image.open(path) as old: sheet=old.convert('RGB')
                bg=(22,27,38) if size==96 else (23,26,32)
                ImageDraw.Draw(sheet).rectangle((x,y,x+size-1,y+size-1),fill=bg)
                tile=rgba.resize((size,size),Image.Resampling.NEAREST)
                sheet.paste(tile,(x,y),tile); sheet.save(path)
    preview.save(ART/'military-pixel-preview.png')
    print('Created five atmospheric 64px DXT3 Military icons.')


if __name__=='__main__': main()
