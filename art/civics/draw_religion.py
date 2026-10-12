"""Export native-pixel religious scenes and preserved ceremonial portraits."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
ART=Path(__file__).resolve().parent
DEST=ROOT/'RFC MP Plus/Assets/Art/Interface/Buttons/Civics/RFCMP'


from religion_scenes import ancestor_cult, state_religion, god_state, tolerance, state_atheism

ICONS=[('Ancestor_Cult','Ancestor Cult',ancestor_cult),('State_Religion','State Religion',state_religion),
       ('God_State','Holy State',god_state),('Tolerance','Tolerance',tolerance),
       ('State_Atheism','State Atheism',state_atheism)]


def main():
    with Image.open(ROOT/'RFC MP Plus/Assets/Art/Interface/Buttons/civics_civilizations_religions_atlas.dds') as atlas:
        alpha=atlas.convert('RGBA').crop((0,0,64,64)).getchannel('A')
    preview=Image.new('RGB',(960,225),(23,26,32)); d=ImageDraw.Draw(preview)
    for row,(name,label,draw) in enumerate(ICONS):
        icon=draw(); icon.putalpha(alpha)
        icon.save(ART/(name.lower().replace('_','-')+'-pixel.png'))
        icon.save(DEST/(name+'.dds'),pixel_format='DXT3')
        with Image.open(DEST/(name+'.dds')) as compressed: rgba=compressed.convert('RGBA')
        tile=rgba.resize((180,180),Image.Resampling.NEAREST)
        preview.paste(tile,(row*192+6,7),tile)
        d.text((row*192+96,198),label,fill=(230,225,208),anchor='mt')
        for filename,size,x,y in [('preview.png',96,528,row*140+10),
                                  ('symbolic-civics-preview.png',180,774,row*216+30)]:
            path=ART/filename
            if path.exists():
                with Image.open(path) as old: sheet=old.convert('RGB')
                ImageDraw.Draw(sheet).rectangle((x,y,x+size-1,y+size-1),fill=(23,26,32))
                tile=rgba.resize((size,size),Image.Resampling.NEAREST)
                sheet.paste(tile,(x,y),tile); sheet.save(path)
    preview.save(ART/'religion-pixel-preview.png')
    print('Created five new atmospheric 64px DXT3 Religion icons.')


if __name__=='__main__': main()
