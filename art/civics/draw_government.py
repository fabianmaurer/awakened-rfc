"""Export five atmospheric government scenes as native 64px game buttons."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ART = Path(__file__).resolve().parent
DEST = ROOT / "Awakened RFC/Assets/Art/Interface/Buttons/Civics/RFCMP"


def main():
    # Export only Government; Legitimacy has its own portrait exporter.
    from dark_government import tribal, monarchy, republic, dictatorship, democracy
    from reuse_government import portrait
    with Image.open(ROOT / "Awakened RFC/Assets/Art/Interface/Buttons/civics_civilizations_religions_atlas.dds") as atlas:
        alpha = atlas.convert("RGBA").crop((0, 0, 64, 64)).getchannel("A")
    icons = [("Tribal_System", tribal()), ("Monarchy", monarchy()),
             ("Republic", portrait("Republic")), ("Dictatorship", portrait("Dictatorship")),
             ("Democracy", democracy())]
    preview = Image.new("RGB", (960, 225), (23, 26, 32))
    draw = ImageDraw.Draw(preview)
    for index, (name, icon) in enumerate(icons):
        icon.putalpha(alpha)
        # Keep the illustrated edge dark; Civ4 supplies its own selection frame.
        icon.save(ART / (name.lower().replace("_", "-") + "-pixel.png"))
        icon.save(DEST / (name + ".dds"), pixel_format="DXT3")
        with Image.open(DEST / (name + ".dds")) as game:
            enlarged = game.convert("RGBA").resize((180, 180), Image.Resampling.NEAREST)
            preview.paste(enlarged, (index * 192 + 6, 7), enlarged)
            if name == "Monarchy":
                game.resize((384, 384), Image.Resampling.NEAREST).save(ART / "monarchy-pixel-preview.local.png")
        draw.text((index * 192 + 96, 198), name.replace("_", " "), fill=(230, 225, 208), anchor="mt")
    preview.save(ART / "government-pixel-preview.png")
    # Refresh the government column in the existing full civic contact sheet.
    if (ART / "preview.png").exists():
        with Image.open(ART / "preview.png") as original:
            sheet = original.convert("RGB")
        for index, (name, _) in enumerate(icons):
            with Image.open(DEST / (name + ".dds")) as game:
                thumb = game.convert("RGBA").resize((96, 96), Image.Resampling.NEAREST)
                ImageDraw.Draw(sheet).rectangle((16, index * 140 + 10, 111, index * 140 + 105), fill=(22, 27, 38))
                sheet.paste(thumb, (16, index * 140 + 10), thumb)
        sheet.save(ART / "preview.png")
    if (ART / "symbolic-civics-preview.png").exists():
        with Image.open(ART / "symbolic-civics-preview.png") as original:
            sheet = original.convert("RGB")
        for index, (name, _) in enumerate(icons):
            with Image.open(DEST / (name + ".dds")) as game:
                thumb = game.convert("RGBA").resize((180, 180), Image.Resampling.NEAREST)
                ImageDraw.Draw(sheet).rectangle((6, index * 216 + 30, 185, index * 216 + 209), fill=(23, 26, 32))
                sheet.paste(thumb, (6, index * 216 + 30), thumb)
        sheet.save(ART / "symbolic-civics-preview.png")
    print("Created five atmospheric 64 x 64 DXT3 government icons with original rounded alpha.")


if __name__ == "__main__":
    main()
